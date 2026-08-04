"""
Flycast Auto-Updater Script
---------------------------
Versão: 1.0
Autor: Daniel de Souza Sant'Anna (com auxílio do Gemini)

Este script automatiza o download e a atualização do emulador Flycast.
Inclui a capacidade de auto-copiar, gerar atalhos automatizados na Área de 
Trabalho e manter um log incremental de auditoria das execuções e atualizações.
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

# --- VARIÁVEIS GLOBAIS E DIRETÓRIOS ---
SCRIPT_VERSION = "1.0"
INSTALL_DIR = os.getcwd()
SHOULD_CREATE_SHORTCUT = False 

args_lower = [arg.lower() for arg in sys.argv]

# --- MENU DE AJUDA ---
if any(h in args_lower for h in ['-help', '--help', '-h', 'help']):
    print("\n=== Ajuda do Atualizador do Flycast ===")
    print("Uso: python update_flycast.py [argumentos]\n")
    print("Argumentos opcionais:")
    print("  -help, --help, -h  Exibe este menu de ajuda e encerra o script.")
    print("  -dev               Força a configuração e o download da versão DEV (Build diária).")
    print("  -master            Força a configuração e o download da versão MASTER (Estável).")
    print("  -path, -caminho    <diretorio>")
    print("                     Define um diretório de instalação personalizado.")
    print("                     Exemplo: python update_flycast.py -path \"D:\\Emuladores\\Flycast\"\n")
    print("Comportamento padrão:")
    print("Se executado sem argumentos, o script usará as configurações salvas")
    print("(ou perguntará na primeira vez) e instalará no diretório atual (corrente).")
    print("=======================================\n")
    sys.exit(0)

for param in ['-path', '-caminho']:
    if param in args_lower:
        idx = args_lower.index(param)
        if len(sys.argv) > idx + 1:
            INSTALL_DIR = os.path.abspath(sys.argv[idx + 1])
            break

if not os.path.exists(INSTALL_DIR):
    os.makedirs(INSTALL_DIR)

# --- SISTEMA DE LOG ---
LOG_FILE = os.path.join(INSTALL_DIR, "flycast_updater.log")

def log_event(message):
    """Grava eventos de forma incremental no arquivo de log com data, hora e versão do script."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [v{SCRIPT_VERSION}] {message}\n")
    except Exception as e:
        print(f"Aviso: Falha ao escrever no arquivo de log. Detalhes: {e}")

# --- AUTO-CÓPIA (Compatível com PyInstaller) ---
if getattr(sys, 'frozen', False):
    current_script_path = sys.executable
else:
    current_script_path = os.path.abspath(__file__)

dest_script_path = os.path.join(INSTALL_DIR, os.path.basename(current_script_path))

if current_script_path != dest_script_path:
    try:
        shutil.copy2(current_script_path, dest_script_path)
    except Exception as e:
        print(f"Aviso: Não foi possível copiar o script para o destino. Detalhes: {e}")

VERSION_FILE = os.path.join(INSTALL_DIR, "version.txt")
CONFIG_FILE = os.path.join(INSTALL_DIR, "branch_config.txt")

S3_BUCKETS = [
    "https://flycast-builds.s3.fr-par.scw.cloud",
    "https://flycast-builds.s3.amazonaws.com"
]

def get_user_preference():
    global SHOULD_CREATE_SHORTCUT
    
    if '-dev' in args_lower:
        print("Parâmetro '-dev' detectado. Alterando configuração para versão DEV...")
        with open(CONFIG_FILE, "w") as f:
            f.write('dev')
        log_event("Opção do usuário (via parâmetro): Branch alterada para DEV.")
        return 'dev'
    elif '-master' in args_lower:
        print("Parâmetro '-master' detectado. Alterando configuração para versão MASTER...")
        with open(CONFIG_FILE, "w") as f:
            f.write('master')
        log_event("Opção do usuário (via parâmetro): Branch alterada para MASTER.")
        return 'master'
        
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            choice = f.read().strip().lower()
            if choice in ['master', 'dev']:
                return choice

    print("\n=== Configuração Inicial do Flycast Updater ===")
    print(f"Diretório alvo: {INSTALL_DIR}")
    if current_script_path != dest_script_path:
        print(f"(O script updater fará uma cópia de si mesmo para este diretório)")
    print("\nQual versão do emulador você deseja baixar e manter atualizada?")
    print("[1] Master (Versão Estável / Principal Oficial)")
    print("[2] Dev    (Versão de Desenvolvimento / Diária da Nuvem)")
    
    while True:
        resp = input("Digite 1 ou 2 e aperte Enter: ").strip()
        if resp == '1':
            choice = 'master'
            break
        elif resp == '2':
            choice = 'dev'
            break
        else:
            print("Opção inválida. Digite 1 para Master ou 2 para Dev.")
            
    with open(CONFIG_FILE, "w") as f:
        f.write(choice)
        
    log_event(f"Configuração inicial concluída. Branch escolhida: {choice.upper()}.")
        
    print("\nDeseja criar um atalho na Área de Trabalho para este atualizador?")
    print("Ele usará os parâmetros corretos automaticamente e terá o ícone oficial do emulador.")
    while True:
        resp_shortcut = input("Criar atalho? (S/N): ").strip().upper()
        if resp_shortcut == 'S':
            SHOULD_CREATE_SHORTCUT = True
            log_event("Opção do usuário: Criação de atalho na Área de Trabalho solicitada.")
            break
        elif resp_shortcut == 'N':
            log_event("Opção do usuário: Criação de atalho recusada.")
            break
        else:
            print("Por favor, digite 'S' para Sim ou 'N' para Não.")
            
    return choice

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
        
        if os.path.exists(vbs_path):
            os.remove(vbs_path)
            
        print(f"\n[+] Atalho 'Flycast ({branch_choice.capitalize()})' criado com sucesso na Área de Trabalho!")
        log_event(f"Atalho da Área de Trabalho gerado com sucesso (Branch: {branch_choice.upper()}).")
    except Exception as e:
        print(f"\n[-] Aviso: Não foi possível gerar o atalho. Erro: {e}")
        log_event(f"Erro ao gerar atalho: {e}")

def get_stable_release():
    print("Consultando a API do GitHub pela última Release Estável (Master)...")
    api_url = "https://api.github.com/repos/flyinghead/flycast/releases/latest"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            release = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Erro ao acessar API do GitHub: {e}")
        return None, None

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
    except Exception as e:
        print(f"Erro ao consultar a API de commits: {e}")
        return None, None

    print("Sondando servidores S3 pela última build diária para Windows...")
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
        log_event("Execução do script finalizada. Inicializando o emulador.")
        subprocess.Popen([exe_path], cwd=INSTALL_DIR)
    else:
        msg = f"Aviso: Executável não encontrado em: {exe_path}"
        print(f"\n{msg}")
        log_event(msg)

def main():
    log_event("--- Script iniciado ---")
    branch_choice = get_user_preference()
    
    download_url = None
    remote_version = None
    
    if branch_choice == 'master':
        download_url, remote_version = get_stable_release()
    else:
        download_url, remote_version = get_dev_release()
        
    if not download_url:
        msg_erro = f"Erro: Não foi possível localizar os arquivos para a versão {branch_choice.upper()}."
        print(msg_erro)
        log_event(msg_erro)
        return

    print(f"Pacote válido localizado! (Versão/Commit: {remote_version[:10]})")

    local_version = ""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            local_version = f.read().strip()

    if local_version == remote_version:
        print(f"O Flycast ({branch_choice.upper()}) já está atualizado na última versão disponível!")
        log_event(f"Verificação concluída. A branch {branch_choice.upper()} já estava atualizada (ID: {remote_version[:10]}).")
        
        if SHOULD_CREATE_SHORTCUT:
            create_desktop_shortcut(branch_choice)
            
        launch_emulator()
        return

    print(f"Nova versão detectada. Iniciando o download de:\n{download_url}")
    log_event(f"Nova versão detectada para a branch {branch_choice.upper()}. Iniciando download do pacote {remote_version[:10]}.")
    download_path = os.path.join(INSTALL_DIR, "flycast_update.zip")
    
    try:
        req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(download_path, 'wb') as out_file:
            
            # Descobre o tamanho total do arquivo
            tamanho_total = response.getheader('Content-Length')
            
            if tamanho_total is None:
                # Se o servidor não informar o tamanho, baixa do jeito antigo
                out_file.write(response.read())
            else:
                tamanho_total = int(tamanho_total)
                tamanho_baixado = 0
                tamanho_bloco = 8192 # Baixa de 8 em 8 KB
                
                print("") # Pula uma linha para a barra ficar isolada
                while True:
                    bloco = response.read(tamanho_bloco)
                    if not bloco:
                        break
                    tamanho_baixado += len(bloco)
                    out_file.write(bloco)
                    
                    # Calcula o progresso
                    porcentagem = int(tamanho_baixado * 100 / tamanho_total)
                    tamanho_barra = 40
                    preenchido = int(tamanho_barra * tamanho_baixado // tamanho_total)
                    barra = '█' * preenchido + '-' * (tamanho_barra - preenchido)
                    
                    # Converte para MB para exibição
                    mb_baixado = tamanho_baixado / (1024 * 1024)
                    mb_total = tamanho_total / (1024 * 1024)
                    
                    # O '\r' faz o cursor voltar ao início da linha, sobrescrevendo a anterior
                    sys.stdout.write(f'\r[*] Progresso: |{barra}| {porcentagem}% ({mb_baixado:.1f} MB / {mb_total:.1f} MB)')
                    sys.stdout.flush()
                
                print("\n") # Pula uma linha ao terminar para não grudar no próximo texto

    except Exception as e:
        msg_erro = f"Erro durante o download: {e}"
        print(f"\n{msg_erro}")
        log_event(msg_erro)
        return

    print("Download concluído. Extraindo arquivos e substituindo a versão antiga...")
    try:
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(INSTALL_DIR)
    except Exception as e:
        msg_erro = f"Erro na extração: {e}"
        print(msg_erro)
        log_event(msg_erro)
    finally:
        if os.path.exists(download_path):
            os.remove(download_path)

    with open(VERSION_FILE, "w") as f:
        f.write(remote_version)

    print(f"Sucesso! O Flycast ({branch_choice.upper()}) foi atualizado corretamente.")
    log_event(f"Atualização concluída com sucesso. Flycast atualizado para a versão {remote_version[:10]}.")
    
    if SHOULD_CREATE_SHORTCUT:
        create_desktop_shortcut(branch_choice)
        
    launch_emulator()

if __name__ == "__main__":
    main()