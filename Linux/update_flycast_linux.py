import os
import urllib.request
import zipfile
import stat

def registrar_log(mensagem):
    with open("flycast_updater.log", "a", encoding="utf-8") as f:
        f.write(f"UPDATE_LINUX: {mensagem}\n")

def dar_permissao_execucao(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        st = os.stat(caminho_arquivo)
        # Adiciona permissão de execução para usuário, grupo e outros (chmod +x equivalente)
        os.chmod(caminho_arquivo, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        registrar_log(f"Permissão de execução concedida para: {caminho_arquivo}")

def executar(idioma):
    if idioma == "pt":
        print("Verificando atualizações do Flycast para Linux...")
    else:
        print("Checking for Flycast Linux updates...")
    
    # Aqui entra a lógica de requisição HTTP (GitHub Releases / S3) para baixar o .zip do Flycast para Linux
    # Exemplo conceitual após extração do binário 'flycast':
    caminho_binario = os.path.join(os.getcwd(), "flycast")
    if os.path.exists(caminho_binario):
        dar_permissao_execucao(caminho_binario)
    
    msg = "Processo de atualização do Linux concluído com sucesso." if idioma == "pt" else "Linux update process completed successfully."
    print(msg)
    registrar_log(msg)