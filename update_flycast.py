"""
Flycast Auto-Updater Script - MOTOR
---------------------------
Versão: 2.0 (Versão Gold Master)
Autor: Daniel de Souza Sant'Anna & Geminix
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

# --- VARIÁVEIS GLOBAIS INJETADAS PELO LAUNCHER ---
SCRIPT_VERSION = "2.0"
INSTALL_DIR = os.getcwd()
SHOULD_CREATE_SHORTCUT = False 
SHOULD_CREATE_STARTUP = False
CLOUD_PROVIDER = None
CLOUD_PATH = None
VERSION_FILE = ""
LOG_FILE = ""
args_lower = []

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [v{SCRIPT_VERSION}] {message}\n")
    except Exception:
        pass

def get_dest_script_path():
    if getattr(sys, 'frozen', False):
        current_script_path = sys.executable
    else:
        current_script_path = os.path.abspath(sys.argv[0])

    dest_script_path = os.path.join(INSTALL_DIR, os.path.basename(current_script_path))

    if os.path.abspath(current_script_path) != os.path.abspath(dest_script_path):
        try:
            shutil.copy2(current_script_path, dest_script_path)
            log_event(f"Atualizador copiado para o diretório de destino: {dest_script_path}")
        except Exception as e:
            log_event(f"Aviso: Não foi possível copiar o executável: {e}")
            
    return dest_script_path

S3_BUCKETS = [
    "https://flycast-builds.s3.fr-par.scw.cloud",
    "https://flycast-builds.s3.amazonaws.com"
]

def get_user_preference():
    return 'master' 

def create_desktop_shortcut(branch_choice, dest_script_path):
    try:
        flycast_exe = os.path.join(INSTALL_DIR, "flycast.exe")
        
        if getattr(sys, 'frozen', False):
            target = dest_script_path
            args_vbs = f'"-{branch_choice} -path " & Chr(34) & "{INSTALL_DIR}" & Chr(34)'
        else:
            target = sys.executable
            args_vbs = f'Chr(34) & "{dest_script_path}" & Chr(34) & " -{branch_choice} -path " & Chr(34) & "{INSTALL_DIR}" & Chr(34)'
            
        vbs_content = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sDesktop = oWS.SpecialFolders("Desktop")
Set oLink = oWS.CreateShortcut(sDesktop & "\\Flycast ({branch_choice.capitalize()}).lnk")
oLink.TargetPath = "{target}"
oLink.Arguments = {args_vbs}
oLink.WorkingDirectory = "{INSTALL_DIR}"
oLink.IconLocation = "{flycast_exe}, 0"
oLink.Save
"""
        vbs_path = os.path.join(tempfile.gettempdir(), "create_flycast_shortcut.vbs")
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_content)
        subprocess.run(['cscript.exe', '//Nologo', vbs_path], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(vbs_path): os.remove(vbs_path)
        print(f"\n[+] Atalho 'Flycast' apontado para a instalação com sucesso!")
    except Exception:
        pass

def create_startup_shortcut(branch_choice, dest_script_path):
    try:
        if getattr(sys, 'frozen', False):
            target = dest_script_path
            args_vbs = f'"-{branch_choice} -silent -path " & Chr(34) & "{INSTALL_DIR}" & Chr(34)'
        else:
            target = sys.executable
            args_vbs = f'Chr(34) & "{dest_script_path}" & Chr(34) & " -{branch_choice} -silent -path " & Chr(34) & "{INSTALL_DIR}" & Chr(34)'
            
        vbs_content = f"""
            Set oWS = WScript.CreateObject("WScript.Shell")
            sStartup = oWS.SpecialFolders("Startup")
            Set oLink = oWS.CreateShortcut(sStartup & "\\FlycastUpdater_Silent.lnk")
            oLink.TargetPath = "{target}"
            oLink.Arguments = {args_vbs}
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

def get_stable_release():
    msg = "Consultando a API do GitHub pela última Release Estável (Master)..."
    print(msg)
    log_event(msg)
    api_url = "https://api.github.com/repos/flyinghead/flycast/releases/latest"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            release = json.loads(response.read().decode('utf-8'))
    except Exception as e: 
        log_event(f"Erro ao consultar API da Master: {e}")
        return None, None
    remote_version = release.get("tag_name")
    for asset in release.get("assets", []):
        name = asset["name"].lower()
        if ("win" in name or "windows" in name) and ("debug" not in name) and name.endswith(".zip"):
            log_event(f"Pacote Master localizado: {remote_version}")
            return asset["browser_download_url"], remote_version
    return None, None

def get_dev_release():
    msg = "Buscando histórico de código da branch 'DEV'..."
    print(msg)
    log_event(msg)
    api_url = "https://api.github.com/repos/flyinghead/flycast/commits?sha=dev&per_page=15"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            commits = json.loads(response.read().decode('utf-8'))
            commit_hashes = [commit["sha"] for commit in commits]
    except Exception as e: 
        log_event(f"Erro ao consultar API da Dev: {e}")
        return None, None
    for commit in commit_hashes:
        for bucket in S3_BUCKETS:
            url = f"{bucket}/win/heads/dev-{commit}/flycast.zip"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
                urllib.request.urlopen(req)
                log_event(f"Pacote Dev localizado no commit: {commit[:10]}")
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
        log_event(f"Aviso de BIOS: Arquivos não detectados ({', '.join(arquivos_faltantes)}).")
    else:
        print(f"\n[✓] Verificação de BIOS: OK.")
        log_event("Verificação de BIOS: OK.")

def criar_backup(install_dir):
    backup_path = os.path.join(install_dir, "flycast_backup.zip")
    flycast_exe = os.path.join(install_dir, "flycast.exe")
    
    print("\n[*] Criando backup de segurança do emulador (flycast.exe)...")
    try:
        # Só cria o backup se o executável do emulador realmente existir
        if os.path.exists(flycast_exe):
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Grava APENAS o flycast.exe, com o nome limpo na raiz do ZIP
                zipf.write(flycast_exe, "flycast.exe")
            log_event("Backup do emulador (flycast.exe) criado com sucesso.")
        else:
            print("[-] flycast.exe não encontrado. Backup ignorado.")
    except Exception as e:
        print(f"[-] Erro ao criar backup: {e}")

def restaurar_backup():
    backup_path = os.path.join(INSTALL_DIR, "flycast_backup.zip")
    if not os.path.exists(backup_path):
        print(f"\n[-] Nenhum arquivo de backup encontrado.")
        return
        
    print(f"\n[*] Iniciando Rollback: Restaurando apenas o executável do emulador...")
    try:
        with zipfile.ZipFile(backup_path, 'r') as zip_ref:
            # Verifica se o flycast.exe está dentro do ZIP antes de extrair
            if "flycast.exe" in zip_ref.namelist():
                zip_ref.extract("flycast.exe", INSTALL_DIR)
                print("[+] Rollback concluído! Versão do emulador restaurada.")
                log_event("Rollback do flycast.exe executado com sucesso.")
            else:
                print("[-] O arquivo de backup é inválido (não contém flycast.exe).")
                log_event("Erro: Arquivo flycast.exe ausente no backup.")
    except Exception as e:
        print(f"[-] Erro crítico durante rollback: {e}")

def acionar_backup_nuvem():
    if cloud_saves and CLOUD_PROVIDER and CLOUD_PATH:
        print(f"\n[*] Verificando Saves para sincronização ({CLOUD_PROVIDER.capitalize()})...")
        log_event(f"Iniciando rotina de Sincronização em Nuvem ({CLOUD_PROVIDER.capitalize()}).")
        
        sucesso, mensagem = cloud_saves.realizar_backup(INSTALL_DIR, CLOUD_PROVIDER, CLOUD_PATH)
        
        if sucesso:
            if any(palavra in mensagem.lower() for palavra in ["nenhum", "nada", "atualizado", "não encontrados"]):
                print(f"[✓] Sincronização: {mensagem}")
                log_event(f"Cloud Save (Status): Arquivos verificados. Nada novo para enviar ({mensagem}).")
            else:
                print(f"[✓] Sincronização Concluída: {mensagem}")
                log_event(f"Cloud Save (Sucesso): Arquivos enviados/sincronizados -> {mensagem}.")
        else:
            print(f"[-] Erro de Sincronização: {mensagem}")
            log_event(f"Cloud Save (Falha/Aviso): {mensagem}")

def main():
    log_event("--- Script de Atualização Iniciado ---")
    dest_script_path = get_dest_script_path()
    
    if '-rollback' in args_lower:
        restaurar_backup()
        return

    if '-backup' in args_lower:
        if cloud_saves and CLOUD_PROVIDER:
            acionar_backup_nuvem()
        else:
            print("[-] Nenhuma nuvem configurada para backup.")
            log_event("Backup abortado: Nenhuma nuvem configurada.")
        return

    branch_choice = get_user_preference()
    log_event(f"Iniciando rotina de verificação para a branch: {branch_choice.upper()}")
    download_url, remote_version = get_stable_release() if branch_choice == 'master' else get_dev_release()
        
    if not download_url:
        print(f"Erro: Não foi possível localizar os arquivos para {branch_choice.upper()}.")
        log_event(f"Erro Crítico: Download URL não localizada para {branch_choice.upper()}.")
        return

    print(f"Pacote localizado! (Commit: {remote_version[:10]})")
    local_version = ""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            local_version = f.read().strip()

    if local_version == remote_version:
        print(f"O Flycast ({branch_choice.upper()}) já está atualizado!")
        log_event(f"Validação: A versão instalada ({local_version[:10]}) já é a mais recente.")
        if SHOULD_CREATE_SHORTCUT: create_desktop_shortcut(branch_choice, dest_script_path)
        if SHOULD_CREATE_STARTUP: create_startup_shortcut(branch_choice, dest_script_path)
        acionar_backup_nuvem() 
        launch_emulator()
        return

    print(f"Nova versão detectada. Iniciando download...")
    log_event(f"Nova versão detectada ({remote_version[:10]}). Iniciando o download do arquivo ZIP...")
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
                    tamanho_barra = 40
                    preenchido = int(tamanho_barra * tamanho_baixado // tamanho_total)
                    
                    if preenchido == tamanho_barra:
                        barra = '█' * tamanho_barra
                    else:
                        barra = '█' * preenchido + '🦔' + '-' * (tamanho_barra - preenchido - 1)
                    
                    mb_baixado = tamanho_baixado / (1024 * 1024)
                    mb_total = tamanho_total / (1024 * 1024)
                    
                    sys.stdout.write(f'\r[*] Progresso: |{barra}| {porcentagem}% ({mb_baixado:.1f}MB / {mb_total:.1f}MB)')
                    sys.stdout.flush()
                print("\n")
        log_event("Download do pacote de atualização concluído com sucesso.")
    except Exception as e:
        print(f"\nErro no download: {e}")
        log_event(f"Erro Crítico durante o download: {e}")
        return

    print("Extraindo arquivos e substituindo a versão antiga...")
    log_event("Iniciando rotina de extração de arquivos...")
    criar_backup(INSTALL_DIR)
    try:
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(INSTALL_DIR)
        log_event("Extração concluída e arquivos substituídos.")
    except Exception as e:
        print(f"Erro na extração: {e}")
        log_event(f"Erro Crítico durante a extração: {e}")
    finally:
        if os.path.exists(download_path): os.remove(download_path)

    with open(VERSION_FILE, "w") as f: f.write(remote_version)
    log_event("Arquivo version.txt atualizado.")
    
    verificar_bios_local(INSTALL_DIR)

    print(f"Sucesso! Flycast atualizado.")
    log_event(f"Ciclo de Atualização concluído com sucesso. Emulador pronto.")
    
    if SHOULD_CREATE_SHORTCUT: create_desktop_shortcut(branch_choice, dest_script_path)
    if SHOULD_CREATE_STARTUP: create_startup_shortcut(branch_choice, dest_script_path)
    
    acionar_backup_nuvem()
    launch_emulator()

if __name__ == "__main__":
    main()