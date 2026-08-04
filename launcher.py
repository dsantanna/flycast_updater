import os
import sys
import json
import subprocess

# ==========================================
# Flycast Updater - Launcher v1.1
# Desenvolvido por DaniboySan & Geminix
# ==========================================

VERSION = "1.1"
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

def salvar_configuracao(branch, create_shortcut, install_path):
    """Salva as preferências no arquivo config.json."""
    config_data = {
        "branch": branch,
        "create_shortcut": create_shortcut,
        "install_path": install_path
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        print("[✓] Preferências salvas com sucesso em config.json!")
    except Exception as e:
        print(f"[Erro] Falha ao salvar configuração: {e}")

def menu_interativo():
    """Exibe o menu para o usuário escolher as opções na primeira execução."""
    print("\n--- Configuração Inicial ---")
    
    # 1. Escolha da Branch
    print("Qual versão do Flycast você deseja instalar/atualizar?")
    print("1 - Master (Estável - Oficial)")
    print("2 - Dev (Builds Diárias - Atualizações constantes)")
    escolha_branch = input("Digite o número (1 ou 2): ").strip()
    branch = "dev" if escolha_branch == "2" else "master"
    
    # 2. Criar atalho?
    escolha_atalho = input("Deseja criar um atalho na Área de Trabalho? (S/N): ").strip().upper()
    create_shortcut = True if escolha_atalho == "S" else False

    # 3. Caminho personalizado (Opcional, pressione Enter para padrão)
    print("\n[Opcional] Digite o caminho de instalação (ou pressione ENTER para a pasta atual):")
    install_path = input("Caminho: ").strip()
    if not install_path:
        install_path = os.getcwd()

    return branch, create_shortcut, install_path

def main():
    exibir_cabecalho()
    
    args = sys.argv[1:]
    
    # Menu de Ajuda
    if "-help" in args or "-h" in args or "--help" in args:
        print("Uso: FlycastUpdater [argumentos]")
        print("Argumentos:")
        print("  -dev          Força a versão de desenvolvimento")
        print("  -master       Força a versão estável")
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
        branch, create_shortcut, install_path = menu_interativo()
        salvar_configuracao(branch, create_shortcut, install_path)
        config = carregar_configuracao()

    # Captura caminho e atalho
    install_path = config.get("install_path", os.getcwd())
    if "-path" in args:
        idx = args.index("-path")
        if len(args) > idx + 1:
            install_path = os.path.abspath(args[idx + 1])

    create_shortcut = config.get("create_shortcut", False)

    print("\n🚀 Iniciando a atualização com os seguintes parâmetros:")
    print(f" - Branch: {branch}")
    print(f" - Destino: {install_path}")
    print(f" - Criar Atalho: {'Sim' if create_shortcut else 'Não'}\n")

    # ==============================================================
    # CONEXÃO COM O MOTOR DE ATUALIZAÇÃO (update_flycast.py)
    # ==============================================================
    import update_flycast
    
    # Configuramos as variáveis globais do motor original de forma limpa
    update_flycast.INSTALL_DIR = install_path
    update_flycast.SHOULD_CREATE_SHORTCUT = create_shortcut
    
    # Recriamos a lista de argumentos falsa para simular que o launcher
    # chamou o script original passando os parâmetros corretos direto na linha de comando.
    # Isso impede que o update_flycast.py abra o menu interativo antigo!
    args_simulados = [f"-{branch}", "-path", install_path]
    update_flycast.args_lower = [arg.lower() for arg in args_simulados]
    
    # Atualiza variáveis de caminho internas do motor
    update_flycast.VERSION_FILE = os.path.join(install_path, "version.txt")
    update_flycast.CONFIG_FILE = os.path.join(install_path, "branch_config.txt")
    update_flycast.LOG_FILE = os.path.join(install_path, "flycast_updater.log")

    # Dispara a lógica principal do motor de download
    update_flycast.main()
    # ==============================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Operação cancelada pelo usuário.")
        sys.exit(1)