"""
Flycast Auto-Updater Script
---------------------------
Versão: 1.3 (Cloud Saves)
Autor: Daniel de Souza Sant'Anna (com auxílio do Gemini)
"""

import os
import sys            
import json           
import urllib.request 
from urllib.error import HTTPError, URLError
import zipfile        
import subprocess     
import shutil         
import tempfile       
import datetime       

try:
    import cloud_saves
except ImportError:
    cloud_saves = None

# --- VARIÁVEIS GLOBAIS E DIRETÓRIOS ---
SCRIPT_VERSION = "1.3"
INSTALL_DIR = os.getcwd()
SHOULD_CREATE_SHORTCUT = False 
SHOULD_CREATE_STARTUP = False
CLOUD_PROVIDER = None
CLOUD_PATH = None

args_lower = [arg.lower() for arg in sys.argv]

if '-silent' in args_lower:
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

if any(h in args_lower for h in ['-help', '--help', '-h', 'help']):
    sys.exit(0)

for param in ['-path', '-caminho']:
    if param in args_lower:
        idx = args_lower.index(param)
        if len(sys.argv) > idx + 1:
            INSTALL_DIR = os.path.abspath(sys.argv[idx + 1])
            break

if not os.path.exists(INSTALL_DIR):
    os.makedirs(INSTALL_DIR)

LOG_FILE = os.path.join(INSTALL_DIR, "flycast_updater.log")

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [v{SCRIPT_VERSION}] {message}\n")
    except Exception as e:
        print(f"Aviso: Falha ao escrever no log: {e}")

if getattr(sys, 'frozen', False):
    current_script_path = sys.executable
else:
    current_script_path = os.path.abspath(__file__)

dest_script_path = os.path.join(INSTALL_DIR, os.path.basename(current_script_path))

if current_script_path != dest_script_path:
    try:
        shutil.copy2(current_script_path, dest_script_path)
    except Exception:
        pass

VERSION_FILE = os.path.join(INSTALL_DIR, "version.txt")
CONFIG_FILE = os.path.join(INSTALL_DIR, "branch_config.txt")

S3_BUCKETS = [
    "https://flycast-builds.s3.fr-par.scw.cloud",
    "https://flycast-builds.s3.amazonaws.com"
]

def get_user_preference():
    return 'master' # Controlado pelo Launcher via Monkeypatching

def create_desktop_shortcut(branch_choice):
    try:
        python_exe = sys.executable
        flycast_exe = os.path.join(INSTALL_DIR, "flycast.exe")
        vbs_content = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sDesktop = oWS.SpecialFolders("Desktop")
Set oLink = oWS.CreateShortcut(sDesktop & "\\Flycast ({branch_choice.capitalize()}).lnk")
oLink.TargetPath = "{python_exe}"
oLink.Arguments = Chr(34) & "{dest_script_path}" & Chr(34) & " -{branch_choice} -path " & Chr(34) & "{INSTALL_DIR}" & Chr(34)
oLink.WorkingDirectory = "{INSTALL_DIR}"
oLink.IconLocation = "{flycast_exe}, 0"
oLink.Save
"""
        vbs_path = os.path.join(tempfile.gettempdir(), "create_flycast_shortcut.vbs")
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_content)
        subprocess.run(['cscript.exe', '//Nologo', vbs_path], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(vbs_path): os.remove(vbs_path)
        print(f"\n[+] Atalho 'Flycast' criado com sucesso!")
    except Exception as e:
        pass

def get_stable_release():
    print("Consultando a API do GitHub pela última Release Estável (Master)...")
    api_url = "https://api.github.com/repos/flyinghead/flycast/releases/latest"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            release = json.loads(response.read().decode('utf-8'))
    except Exception: return None, None
    remote_version = release.get("tag_name")
    for asset in release.get("assets", []):
        name = asset["name"].lower()
        if ("win" in name or "windows" in name) and ("debug" not in name) and name.endswith(".zip"):
            return asset["browser_download_url"], remote_version
    return None, None

def get_dev_release():
    print("Buscando histórico de código da branch 'DEV'...")
    api_url = "https://api.github.com/repos/flyinghead/flycast/commits?sha=dev&per_page=15"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            commits = json.loads(response.read().decode('utf-8'))
            commit_hashes = [commit["sha"] for commit in commits]
    except Exception: return None, None
    for commit in commit_hashes:
        for bucket in S3_BUCKETS:
            url = f"{bucket}/win/heads/dev-{commit}/flycast.zip"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
                urllib.request.urlopen(req)
                return url, commit
            except (HTTPError, URLError):
                continue
    return None, None

def launch_emulator():
    exe_path = os.path.join(INSTALL_DIR, "flycast.exe")
    if os.path.exists(exe_path):
        print("Iniciando o Flycast...")
        log_event("Execução finalizada. Inicializando emulador.")
        subprocess.Popen([exe_path], cwd=INSTALL_DIR)

def verificar_bios_local(install_dir):
    arquivos_bios = ["dc_boot.bin", "dc_flash.bin"]
    arquivos_faltantes = []
    for arquivo in arquivos_bios:
        caminho_raiz = os.path.join(install_dir, arquivo)
        caminho_data = os.path.join(install_dir, "data", arquivo)
        if not (os.path.exists(caminho_raiz) or os.path.exists(caminho_data)):
            arquivos_faltantes.append(arquivo)
    if arquivos_faltantes:
        print(f"\n[!] Aviso de BIOS: Arquivos não detectados ({', '.join(arquivos_faltantes)}).")
    else:
        print(f"\n[✓] Verificação de BIOS: OK.")

def create_startup_shortcut(branch_choice):
    try:
        python_exe = sys.executable
        vbs_content = f"""
            Set oWS = WScript.CreateObject("WScript.Shell")
            sStartup = oWS.SpecialFolders("Startup")
            Set oLink = oWS.CreateShortcut(sStartup & "\\FlycastUpdater_Silent.lnk")
            oLink.TargetPath = "{python_exe}"
            oLink.Arguments = Chr(34) & "{dest_script_path}" & Chr(34) & " -{branch_choice} -silent -path " & Chr(34) & "{INSTALL_DIR}" & Chr(34)
            oLink.WorkingDirectory = "{INSTALL_DIR}"
            oLink.WindowStyle = 7 
            oLink.Save
        """
        vbs_path = os.path.join(tempfile.gettempdir(), "create_startup_shortcut.vbs")
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_content)
        subprocess.run(['cscript.exe', '//Nologo', vbs_path], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(vbs_path): os.remove(vbs_path)
    except Exception:
        pass

def criar_backup(install_dir):
    backup_path = os.path.join(install_dir, "flycast_backup.zip")
    print("\n[*] Criando backup de segurança da versão atual...")
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(install_dir):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if file not in ["flycast_backup.zip", "flycast_update.zip", "flycast_updater.log"] and ext not in ['.chd', '.gdi', '.cdi', '.iso']:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, install_dir)
                        zipf.write(file_path, arcname)
        log_event("Backup criado com sucesso.")
    except Exception:
        pass

def restaurar_backup():
    backup_path = os.path.join(INSTALL_DIR, "flycast_backup.zip")
    if not os.path.exists(backup_path):
        print(f"\n[-] Nenhum arquivo de backup encontrado.")
        return
    print(f"\n[*] Iniciando Rollback: Restaurando versão anterior...")
    try:
        with zipfile.ZipFile(backup_path, 'r') as zip_ref:
            zip_ref.extractall(INSTALL_DIR)
        print("[+] Rollback concluído!")
        log_event("Rollback executado com sucesso.")
    except Exception as e:
        print(f"[-] Erro crítico durante rollback: {e}")

def acionar_backup_nuvem():
    """Gatilho para acionar a rotina de Cloud Saves se estiver configurada."""
    if cloud_saves and CLOUD_PROVIDER and CLOUD_PATH:
        print(f"\n[*] Iniciando sincronização de saves com {CLOUD_PROVIDER.capitalize()}...")
        sucesso, mensagem = cloud_saves.realizar_backup(INSTALL_DIR, CLOUD_PROVIDER, CLOUD_PATH)
        if sucesso:
            print(f"[✓] {mensagem}")
            log_event(mensagem)
        else:
            print(f"[-] {mensagem}")
            log_event(f"Aviso no Cloud Save: {mensagem}")

def main():
    log_event("--- Script iniciado ---")
    
    if '-rollback' in args_lower:
        restaurar_backup()
        return

    # Se o usuário acionou APENAS o backup manual
    if '-backup' in args_lower:
        if cloud_saves and CLOUD_PROVIDER:
            acionar_backup_nuvem()
        else:
            print("[-] Nenhuma nuvem configurada para backup.")
        return

    branch_choice = get_user_preference()
    
    download_url, remote_version = get_stable_release() if branch_choice == 'master' else get_dev_release()
        
    if not download_url:
        print(f"Erro: Não foi possível localizar os arquivos para {branch_choice.upper()}.")
        return

    print(f"Pacote localizado! (Commit: {remote_version[:10]})")
    local_version = ""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            local_version = f.read().strip()

    if local_version == remote_version:
        print(f"O Flycast ({branch_choice.upper()}) já está atualizado!")
        if SHOULD_CREATE_SHORTCUT: create_desktop_shortcut(branch_choice)
        if SHOULD_CREATE_STARTUP: create_startup_shortcut(branch_choice)
        
        acionar_backup_nuvem() # Faz backup dos saves mesmo se o emu não precisou atualizar
        launch_emulator()
        return

    print(f"Nova versão detectada. Iniciando download...")
    download_path = os.path.join(INSTALL_DIR, "flycast_update.zip")
    
    try:
        req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(download_path, 'wb') as out_file:
            tamanho_total = response.getheader('Content-Length')
            if tamanho_total is None:
                out_file.write(response.read())
            else:
                tamanho_total = int(tamanho_total)
                tamanho_baixado = 0
                print("") 
                while True:
                    bloco = response.read(8192)
                    if not bloco: break
                    tamanho_baixado += len(bloco)
                    out_file.write(bloco)
                    porcentagem = int(tamanho_baixado * 100 / tamanho_total)
                    preenchido = int(40 * tamanho_baixado // tamanho_total)
                    sys.stdout.write(f'\r[*] Progresso: |{"█" * preenchido + "-" * (40 - preenchido)}| {porcentagem}%')
                    sys.stdout.flush()
                print("\n")
    except Exception as e:
        print(f"\nErro no download: {e}")
        return

    print("Extraindo arquivos e substituindo a versão antiga...")
    criar_backup(INSTALL_DIR)
    try:
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(INSTALL_DIR)
    except Exception as e:
        print(f"Erro na extração: {e}")
    finally:
        if os.path.exists(download_path): os.remove(download_path)

    with open(VERSION_FILE, "w") as f: f.write(remote_version)
    verificar_bios_local(INSTALL_DIR)

    print(f"Sucesso! Flycast atualizado.")
    if SHOULD_CREATE_SHORTCUT: create_desktop_shortcut(branch_choice)
    if SHOULD_CREATE_STARTUP: create_startup_shortcut(branch_choice)
    
    acionar_backup_nuvem() # Faz o backup dos saves após atualizar
    launch_emulator()

if __name__ == "__main__":
    main()