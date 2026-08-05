import os
import sys
import glob
import zipfile
import datetime
import shutil

# ==========================================
# Módulo de Backup de Saves em Nuvem
# Flycast Updater - v1.2
# ==========================================

def get_onedrive_path():
    """Verifica passivamente se o OneDrive está ativo através de Variáveis de Ambiente do Windows."""
    # O Windows 10/11 por padrão cria a variável %OneDrive% quando o app está logado
    return os.environ.get('OneDrive')

def get_gdrive_path():
    """Verifica passivamente caminhos comuns de montagem do Google Drive no Windows."""
    # O Google Drive geralmente monta um disco virtual ou usa pastas locais padrões
    caminhos_comuns = [
        r"G:\Meu Drive",
        r"G:\My Drive",
        os.path.join(os.environ.get('USERPROFILE', ''), 'Google Drive'),
        os.path.join(os.environ.get('USERPROFILE', ''), 'My Drive')
    ]
    for caminho in caminhos_comuns:
        if os.path.exists(caminho):
            return caminho
    return None

def detectar_nuvens_disponiveis():
    """Retorna um dicionário com os provedores detectados passivamente."""
    nuvens = {}
    
    onedrive = get_onedrive_path()
    if onedrive and os.path.exists(onedrive):
        nuvens['onedrive'] = onedrive
        
    gdrive = get_gdrive_path()
    if gdrive:
        nuvens['gdrive'] = gdrive
        
    return nuvens

def realizar_backup(install_dir, provedor, caminho_nuvem):
    """Compacta os arquivos de save do Flycast e envia para a nuvem."""
    if not caminho_nuvem or not os.path.exists(caminho_nuvem):
        return False, "Caminho da nuvem inacessível ou desconectado."

    pasta_data = os.path.join(install_dir, "data")
    if not os.path.exists(pasta_data):
        return False, "Pasta 'data' do Flycast não encontrada. Nenhum save para fazer backup."

    # Busca arquivos de VMU do Dreamcast e Saves de Arcade (SRAM)
    saves_vmu = glob.glob(os.path.join(pasta_data, "vmu_save_*.bin"))
    saves_sram = glob.glob(os.path.join(pasta_data, "*.srm"))
    todos_saves = saves_vmu + saves_sram

    if not todos_saves:
        return False, "Nenhum arquivo de save (.bin ou .srm) encontrado na pasta 'data'."

    # Cria a pasta de destino na Nuvem (Ex: OneDrive\Flycast_Saves_Backup)
    pasta_backup_nuvem = os.path.join(caminho_nuvem, "Flycast_Saves_Backup")
    if not os.path.exists(pasta_backup_nuvem):
        try:
            os.makedirs(pasta_backup_nuvem)
        except Exception as e:
            return False, f"Falha ao criar pasta na nuvem: {e}"

    # Gera o nome do arquivo ZIP com a data e hora atual
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    nome_zip = f"Saves_Flycast_{timestamp}.zip"
    caminho_zip = os.path.join(pasta_backup_nuvem, nome_zip)

    # Compacta os saves
    try:
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for save_file in todos_saves:
                nome_arquivo = os.path.basename(save_file)
                zipf.write(save_file, nome_arquivo)
        
        # Mantém apenas os 5 backups mais recentes para não lotar a nuvem
        limpar_backups_antigos(pasta_backup_nuvem)
        
        return True, f"Backup concluído com sucesso em: {provedor.capitalize()} ({nome_zip})"
    except Exception as e:
        return False, f"Erro ao compactar saves: {e}"

def limpar_backups_antigos(pasta_backup_nuvem, limite=5):
    """Apaga os backups mais antigos, mantendo apenas o número estipulado pelo limite."""
    backups = glob.glob(os.path.join(pasta_backup_nuvem, "Saves_Flycast_*.zip"))
    if len(backups) > limite:
        # Ordena os arquivos pela data de modificação (mais antigos primeiro)
        backups.sort(key=os.path.getmtime)
        arquivos_para_apagar = len(backups) - limite
        for i in range(arquivos_para_apagar):
            try:
                os.remove(backups[i])
            except:
                pass

def configurar_nuvem_interativo():
    """Interface de configuração para a primeira execução do Launcher."""
    nuvens = detectar_nuvens_disponiveis()
    
    if not nuvens:
        return None, None
        
    print("\n--- ☁️  Backup em Nuvem dos Saves ---")
    print("O sistema detectou que você possui serviços de nuvem ativos.")
    print("Deseja fazer o backup automático dos seus saves de jogos?")
    
    opcoes = []
    if 'onedrive' in nuvens:
        opcoes.append('onedrive')
    if 'gdrive' in nuvens:
        opcoes.append('gdrive')

    for idx, opcao in enumerate(opcoes, 1):
        if opcao == 'onedrive':
            print(f"[{idx}] Sim, usar o Microsoft OneDrive")
        elif opcao == 'gdrive':
            print(f"[{idx}] Sim, usar o Google Drive")
            
    print(f"[{len(opcoes) + 1}] Não fazer backup em nuvem")

    while True:
        try:
            escolha = int(input("Digite o número da opção desejada: "))
            if 1 <= escolha <= len(opcoes):
                provedor = opcoes[escolha - 1]
                caminho = nuvens[provedor]
                print(f"[✓] Backup ativado via {provedor.capitalize()}!")
                return provedor, caminho
            elif escolha == len(opcoes) + 1:
                print("[-] Backup em nuvem ignorado.")
                return None, None
            else:
                print("Opção inválida.")
        except ValueError:
            print("Digite um número válido.")

if __name__ == "__main__":
    # Teste rápido se o script for rodado sozinho
    print("Testando detecção passiva de nuvens...")
    detectadas = detectar_nuvens_disponiveis()
    print(f"Resultado: {detectadas}")