import os
import locale
import subprocess
from datetime import datetime

LOG_FILE = "flycast_updater.log"

def registrar_log(mensagem):
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"{data_hora} - [v1.0-linux] - {mensagem}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linha)

def detectar_idioma():
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith("pt"):
            return "pt"
    except Exception:
        pass
    return "en"

def criar_atalho_desktop(idioma):
    desktop_dir = os.path.expanduser("~/Desktop")
    if not os.path.exists(desktop_dir):
        desktop_dir = os.path.expanduser("~/Área de Trabalho")
    
    if not os.path.exists(desktop_dir):
        os.makedirs(desktop_dir, exist_ok=True)

    desktop_path = os.path.join(desktop_dir, "flycast_updater.desktop")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exec_path = os.path.join(script_dir, "update_flycast_linux.py")
    icon_path = os.path.join(script_dir, "flycast_updater.png")

    conteudo_desktop = f"""[Desktop Entry]
Type=Application
Name=Flycast Auto-Updater
Comment=Flycast Emulator Auto-Updater for Linux
Exec=python3 "{exec_path}"
Icon={icon_path if os.path.exists(icon_path) else ""}
Terminal=true
Categories=Game;Emulator;
"""
    try:
        with open(desktop_path, "w", encoding="utf-8") as f:
            f.write(conteudo_desktop)
        # Torna o atalho confiável/executável no Ubuntu
        os.chmod(desktop_path, 0o755)
        msg = "Atalho na Área de Trabalho criado com sucesso." if idioma == "pt" else "Desktop shortcut created successfully."
        print(msg)
        registrar_log(msg)
    except Exception as e:
        err_msg = f"Erro ao criar atalho: {e}"
        print(err_msg)
        registrar_log(err_msg)

if __name__ == "__main__":
    idioma = detectar_idioma()
    if idioma == "pt":
        print("=== Flycast Auto-Updater (Linux Ubuntu) ===")
        resp = input("Deseja criar um atalho na Área de Trabalho? (s/n): ").strip().lower()
        criar = resp in ['s', 'sim', 'y', 'yes']
    else:
        print("=== Flycast Auto-Updater (Linux Ubuntu) ===")
        resp = input("Do you want to create a Desktop shortcut? (y/n): ").strip().lower()
        criar = resp in ['y', 'yes', 's', 'sim']

    registrar_log("Inicializador executado no Linux.")
    if criar:
        criar_atalho_desktop(idioma)

    import update_flycast_linux
    update_flycast_linux.executar(idioma)