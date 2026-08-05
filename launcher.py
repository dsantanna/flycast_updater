import os
import sys
import json
import subprocess
import time
import urllib.request
from urllib.error import URLError
import datetime

# Importa o nosso novo módulo de saves
try:
    import cloud_saves
except ImportError:
    cloud_saves = None

# ==========================================
# Flycast Updater - Launcher v1.2 (Cloud Saves)
# Desenvolvido por DaniboySan & Geminix
# ==========================================

VERSION = "1.2"
CONFIG_FILE = "config.json"

def exibir_cabecalho():
    print("=" * 50)
    print(f"🌀 Flycast Updater - v{VERSION}")
    print("=" * 50)

def carregar_configuracao():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[!] Arquivo de configuração corrompido. Criando um novo...")
        except Exception as e:
            print(f"[Erro] Falha ao ler configuração: {e}")
    return {}

def salvar_configuracao(branch, create_shortcut, create_startup, install_path, cloud_prov, cloud_path):
    config_data = {
        "branch": branch,
        "create_shortcut": create_shortcut,
        "create_startup": create_startup,
        "install_path": install_path,
        "cloud_provider": cloud_prov,
        "cloud_path": cloud_path
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        print("[✓] Preferências salvas com sucesso em config.json!")
    except Exception as e:
        print(f"[Erro] Falha ao salvar configuração: {e}")

REPO_UPDATER = "dsantanna/flycast_updater"

def gravar_log(mensagem, install_path):
    log_file = os.path.join(install_path, "flycast_updater.log")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [v{VERSION}] {mensagem}\n")
    except:
        pass

def verificar_atualizacao_updater(install_path):
    msg_inicio = "Verificando se há atualizações para o próprio Flycast Updater..."
    print(f"[*] {msg_inicio}")
    gravar_log(msg_inicio, install_path)
    
    api_url = f"https://api.github.com/repos/{REPO_UPDATER}/releases/latest"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            dados = json.loads(response.read().decode())
            
        versao_remota = dados.get("tag_name", "").replace("v", "")
        
        if versao_remota and versao_remota > VERSION:
            msg_nova = f"Nova versão do Updater encontrada: v{versao_remota}. Iniciando auto-atualização."
            print(f"\n[!] {msg_nova}")
            gravar_log(msg_nova, install_path)
            for asset in dados.get("assets", []):
                if asset["name"].endswith(".exe"):
                    aplicar_auto_atualizacao(asset["browser_download_url"], install_path)
                    return 
                    
        msg_ok = "O Flycast Updater já está na versão mais recente."
        print(f"[✓] {msg_ok}\n")
        gravar_log(msg_ok, install_path)
        
    except Exception as e:
        msg_erro = f"Aviso: Não foi possível checar atualização do Updater: {e}"
        print(f"[-] {msg_erro}\n")
        gravar_log(msg_erro, install_path)

def aplicar_auto_atualizacao(url_download, install_path):
    msg_down = "Baixando a nova versão do atualizador. Aguarde..."
    print(f"[*] {msg_down}")
    gravar_log(msg_down, install_path)
    
    exe_atual = sys.executable
    dir_atual = os.path.dirname(exe_atual)
    exe_novo = os.path.join(dir_atual, "FlycastUpdater_novo.exe")
    script_bat = os.path.join(dir_atual, "atualiza_updater.bat")
    
    try:
        urllib.request.urlretrieve(url_download, exe_novo)
        nome_exe = os.path.basename(exe_atual)
        conteudo_bat = f"""@echo off\ntimeout /t 2 /nobreak > NUL\ndel "{nome_exe}"\nren "FlycastUpdater_novo.exe" "{nome_exe}"\nstart "" "{nome_exe}"\ndel "%~f0"\n"""
        with open(script_bat, "w") as f:
            f.write(conteudo_bat)
            
        msg_sucesso = "Download concluído! Reiniciando para aplicar..."
        print(f"[✓] {msg_sucesso}")
        gravar_log(msg_sucesso, install_path)
        
        subprocess.Popen(script_bat, shell=True)
        sys.exit(0)
    except Exception as e:
        print(f"[-] Erro ao atualizar o script: {e}\n")
        if os.path.exists(exe_novo):
            os.remove(exe_novo)

def menu_interativo():
    print("\n--- Configuração Inicial ---")
    print("Qual versão do Flycast você deseja instalar/atualizar?")
    print("1 - Master (Estável - Oficial)\n2 - Dev (Builds Diárias - Atualizações constantes)")
    branch = "dev" if input("Digite o número (1 ou 2): ").strip() == "2" else "master"
    
    create_shortcut = input("Deseja criar um atalho na Área de Trabalho? (S/N): ").strip().upper() == "S"
    
    print("\nDeseja que o atualizador rode em Modo Silencioso (em segundo plano)")
    print("toda vez que você ligar o computador (pasta de Inicialização do Windows)?")
    create_startup = input("Executar ao iniciar o PC? (S/N): ").strip().upper() == "S"

    install_path = input("\n[Opcional] Digite o caminho de instalação (ou pressione ENTER para a pasta atual):\nCaminho: ").strip()
    if not install_path:
        install_path = os.getcwd()

    cloud_prov, cloud_path = None, None
    if cloud_saves:
        cloud_prov, cloud_path = cloud_saves.configurar_nuvem_interativo()

    return branch, create_shortcut, create_startup, install_path, cloud_prov, cloud_path

def main():
    args = sys.argv[1:]
    if "-silent" in args:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        
    exibir_cabecalho()
            
    if "-help" in args or "-h" in args or "--help" in args:
        print("Uso: FlycastUpdater [argumentos]")
        print("  -dev          Força a versão de desenvolvimento")
        print("  -master       Força a versão estável")
        print("  -rollback     Restaura o último backup funcional do emulador")
        print("  -silent       Executa em segundo plano sem exibir o terminal")
        print("  -backup       Apenas realiza o backup dos saves na nuvem e encerra")
        print("  -gdrive       Força/Ativa o uso do Google Drive para saves")
        print("  -onedrive     Força/Ativa o uso do OneDrive para saves")
        print("  -path <dir>   Define o diretório de instalação")
        print("  -reset        Ignora o config.json e refaz a configuração")
        sys.exit(0)

    forcar_menu = "-reset" in args
    config = {} if forcar_menu else carregar_configuracao()

    cloud_prov = config.get("cloud_provider")
    cloud_path = config.get("cloud_path")

    # Override de Nuvem via CLI
    if "-gdrive" in args and cloud_saves:
        cloud_path = cloud_saves.get_gdrive_path()
        if cloud_path:
            cloud_prov = "gdrive"
            print("[*] Google Drive forçado via linha de comando.")
    elif "-onedrive" in args and cloud_saves:
        cloud_path = cloud_saves.get_onedrive_path()
        if cloud_path and os.path.exists(cloud_path):
            cloud_prov = "onedrive"
            print("[*] OneDrive forçado via linha de comando.")

    if "-dev" in args:
        branch = "dev"
    elif "-master" in args:
        branch = "master"
    elif config and "branch" in config:
        branch = config["branch"]
    else:
        branch, create_shortcut, create_startup, install_path, cloud_prov, cloud_path = menu_interativo()
        salvar_configuracao(branch, create_shortcut, create_startup, install_path, cloud_prov, cloud_path)
        config = carregar_configuracao()

    install_path = config.get("install_path", os.getcwd())
    if "-path" in args:
        idx = args.index("-path")
        if len(args) > idx + 1:
            install_path = os.path.abspath(args[idx + 1])

    create_shortcut = config.get("create_shortcut", False)
    create_startup = config.get("create_startup", False)

    # Salva sempre que houver alteração forçada
    if ("-gdrive" in args or "-onedrive" in args) and cloud_prov:
        salvar_configuracao(branch, create_shortcut, create_startup, install_path, cloud_prov, cloud_path)

    if "-rollback" not in args and "-backup" not in args:
        print("\n🚀 Iniciando a atualização com os seguintes parâmetros:")
        print(f" - Branch: {branch} | Destino: {install_path}")
        print(f" - Nuvem Ativa: {cloud_prov.capitalize() if cloud_prov else 'Nenhuma'}\n")

    gravar_log(f"Parâmetros -> Branch: {branch.upper()} | Nuvem: {cloud_prov}", install_path)

    if getattr(sys, 'frozen', False) and "-rollback" not in args and "-backup" not in args:
        verificar_atualizacao_updater(install_path)

    import update_flycast
    update_flycast.SCRIPT_VERSION = VERSION
    update_flycast.args_lower = [arg.lower() for arg in sys.argv]
    update_flycast.INSTALL_DIR = install_path
    update_flycast.SHOULD_CREATE_SHORTCUT = create_shortcut
    update_flycast.SHOULD_CREATE_STARTUP = create_startup
    update_flycast.VERSION_FILE = os.path.join(install_path, "version.txt")
    update_flycast.LOG_FILE = os.path.join(install_path, "flycast_updater.log")
    
    # Injetando as variáveis de nuvem no Motor
    update_flycast.CLOUD_PROVIDER = cloud_prov
    update_flycast.CLOUD_PATH = cloud_path

    update_flycast.get_user_preference = lambda: branch
    update_flycast.main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Operação cancelada pelo usuário.")
        sys.exit(1)