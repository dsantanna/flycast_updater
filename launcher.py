import os
import sys
import json
import subprocess
import time
import urllib.request
from urllib.error import URLError
import datetime

# ==========================================
# Flycast Updater - Launcher v1.2
# Desenvolvido por DaniboySan & Geminix
# ==========================================

VERSION = "1.2"
CONFIG_FILE = "config.json"

def exibir_cabecalho():
    print("=" * 50)
    print(f"🌀 Flycast Updater - v{VERSION}")
    print("=" * 50)

def carregar_configuracao():
    """Carrega as preferências salvas do arquivo config.json."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[!] Arquivo de configuração corrompido. Criando um novo...")
        except Exception as e:
            print(f"[Erro] Falha ao ler configuração: {e}")
    return {}

def salvar_configuracao(branch, create_shortcut, create_startup, install_path):
    """Salva as preferências no arquivo config.json."""
    config_data = {
        "branch": branch,
        "create_shortcut": create_shortcut,
        "create_startup": create_startup,
        "install_path": install_path
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        print("[✓] Preferências salvas com sucesso em config.json!")
    except Exception as e:
        print(f"[Erro] Falha ao salvar configuração: {e}")

# Substitua com o seu repositório exato caso esteja diferente
REPO_UPDATER = "dsantanna/flycast_updater"

def gravar_log(mensagem, install_path):
    """Grava os eventos do Launcher no mesmo arquivo de log do motor."""
    log_file = os.path.join(install_path, "flycast_updater.log")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [v{VERSION}] {mensagem}\n")
    except:
        pass

def verificar_atualizacao_updater(install_path):
    """Verifica se há uma nova versão do FlycastUpdater lançada no GitHub."""
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
    """Baixa o novo .exe e cria um script .bat para substituí-lo."""
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
        conteudo_bat = f"""@echo off
timeout /t 2 /nobreak > NUL
del "{nome_exe}"
ren "FlycastUpdater_novo.exe" "{nome_exe}"
start "" "{nome_exe}"
del "%~f0"
"""
        with open(script_bat, "w") as f:
            f.write(conteudo_bat)
            
        msg_sucesso = "Download do novo Updater concluído! Reiniciando para aplicar..."
        print(f"[✓] {msg_sucesso}")
        gravar_log(msg_sucesso, install_path)
        
        subprocess.Popen(script_bat, shell=True)
        sys.exit(0)
        
    except Exception as e:
        msg_erro_down = f"Erro ao tentar atualizar o script: {e}"
        print(f"[-] {msg_erro_down}\n")
        gravar_log(msg_erro_down, install_path)
        if os.path.exists(exe_novo):
            os.remove(exe_novo)

def menu_interativo():
    """Exibe o menu para o usuário escolher as opções na primeira execução."""
    print("\n--- Configuração Inicial ---")
    
    # 1. Escolha da Branch
    print("Qual versão do Flycast você deseja instalar/atualizar?")
    print("1 - Master (Estável - Oficial)")
    print("2 - Dev (Builds Diárias - Atualizações constantes)")
    escolha_branch = input("Digite o número (1 ou 2): ").strip()
    branch = "dev" if escolha_branch == "2" else "master"
    
    # 2. Criar atalho na Área de Trabalho?
    escolha_atalho = input("Deseja criar um atalho na Área de Trabalho? (S/N): ").strip().upper()
    create_shortcut = True if escolha_atalho == "S" else False
    
    # 3. Criar atalho Silencioso na Inicialização? (NOVO v1.2)
    print("\nDeseja que o atualizador rode em Modo Silencioso (em segundo plano)")
    print("toda vez que você ligar o computador (pasta de Inicialização do Windows)?")
    escolha_startup = input("Executar ao iniciar o PC? (S/N): ").strip().upper()
    create_startup = True if escolha_startup == "S" else False

    # 4. Caminho personalizado (Opcional, pressione Enter para padrão)
    print("\n[Opcional] Digite o caminho de instalação (ou pressione ENTER para a pasta atual):")
    install_path = input("Caminho: ").strip()
    if not install_path:
        install_path = os.getcwd()

    return branch, create_shortcut, create_startup, install_path

def main():
    args = sys.argv[1:]
    
    # --- MODO SILENCIOSO DO LAUNCHER ---
    # Se rodar com -silent, emudece o terminal do próprio launcher também
    if "-silent" in args:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        
    exibir_cabecalho()
            
    # Menu de Ajuda (Atualizado para v1.2)
    if "-help" in args or "-h" in args or "--help" in args:
        print("Uso: FlycastUpdater [argumentos]")
        print("Argumentos:")
        print("  -dev          Força a versão de desenvolvimento")
        print("  -master       Força a versão estável")
        print("  -rollback     Restaura o último backup funcional do emulador (v1.2)")
        print("  -silent       Executa o atualizador em segundo plano sem exibir o terminal (v1.2)")
        print("  -path <dir>   Define o diretório de instalação")
        print("  -reset        Ignora o config.json e refaz a configuração")
        sys.exit(0)

    # Verifica se o usuário quer resetar as configurações
    forcar_menu = "-reset" in args

    config = {}
    if not forcar_menu:
        config = carregar_configuracao()

    # Define as variáveis com base no CLI, no Config.json ou no Menu Interativo
    if "-dev" in args:
        branch = "dev"
    elif "-master" in args:
        branch = "master"
    elif config and "branch" in config:
        branch = config["branch"]
        print(f"[*] Carregado do config.json -> Branch: {branch.capitalize()}")
    else:
        branch, create_shortcut, create_startup, install_path = menu_interativo()
        salvar_configuracao(branch, create_shortcut, create_startup, install_path)
        config = carregar_configuracao()

    # Captura caminho e atalhos
    install_path = config.get("install_path", os.getcwd())
    if "-path" in args:
        idx = args.index("-path")
        if len(args) > idx + 1:
            install_path = os.path.abspath(args[idx + 1])

    create_shortcut = config.get("create_shortcut", False)
    create_startup = config.get("create_startup", False)

    # Só exibe se não for rollback e não for silencioso
    if "-rollback" not in args:
        print("\n🚀 Iniciando a atualização com os seguintes parâmetros:")
        print(f" - Branch: {branch}")
        print(f" - Destino: {install_path}")
        print(f" - Criar Atalho (Desktop): {'Sim' if create_shortcut else 'Não'}")
        print(f" - Criar Atalho (Silent/Startup): {'Sim' if create_startup else 'Não'}\n")

    # Gravando as escolhas vitais do usuário no arquivo de log
    gravar_log(f"Parâmetros definidos -> Branch: {branch.upper()} | Destino: {install_path} | Atalho Desktop: {create_shortcut} | Atalho Startup: {create_startup}", install_path)

    # Auto-Update do Launcher (Se não for rollback)
    if getattr(sys, 'frozen', False) and "-rollback" not in args:
        verificar_atualizacao_updater(install_path)

    # ==============================================================
    # CONEXÃO COM O MOTOR DE ATUALIZAÇÃO (update_flycast.py)
    # ==============================================================
    import update_flycast
    
    # Sincronizamos a versão do motor com o launcher
    update_flycast.SCRIPT_VERSION = VERSION
    
    # Repassa os argumentos extras do launcher para o motor não se perder
    update_flycast.args_lower = [arg.lower() for arg in sys.argv]
    
    # Configura as variáveis globais de caminho e atalhos no motor
    update_flycast.INSTALL_DIR = install_path
    update_flycast.SHOULD_CREATE_SHORTCUT = create_shortcut
    update_flycast.SHOULD_CREATE_STARTUP = create_startup
    update_flycast.VERSION_FILE = os.path.join(install_path, "version.txt")
    update_flycast.LOG_FILE = os.path.join(install_path, "flycast_updater.log")

    # Monkeypatching dinâmico para pular a configuração original do motor
    update_flycast.get_user_preference = lambda: branch

    # Dispara a lógica principal do motor de download
    update_flycast.main()
    # ==============================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Operação cancelada pelo usuário.")
        sys.exit(1)
