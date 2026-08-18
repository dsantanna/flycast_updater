import os
import sys
import json
import time
import subprocess
import urllib.request
import tkinter.messagebox as mb

VERSION = "6.2"
REPO_UPDATER = "dsantanna/flycast_updater"

def aplicar_auto_atualizacao(url_download, install_path, modo_gui=False, app_gui=None):
    exe_atual = sys.executable
    dir_atual = os.path.dirname(exe_atual)
    exe_novo = os.path.join(dir_atual, "FlycastUpdater_novo.exe")
    script_bat = os.path.join(dir_atual, "atualiza_updater.bat")
    if modo_gui and app_gui: app_gui.after(0, app_gui.label_status.configure, {"text": "Baixando nova versão do Atualizador...", "text_color": "orange"})
    try:
        urllib.request.urlretrieve(url_download, exe_novo)
        nome_exe = os.path.basename(exe_atual)
        conteudo_bat = f"""@echo off\ncd /d "{dir_atual}"\n:wait\ntimeout /t 1 /nobreak > NUL\ndel "{nome_exe}"\nif exist "{nome_exe}" goto wait\nren "FlycastUpdater_novo.exe" "{nome_exe}"\nstart "" "{nome_exe}"\n(goto) 2>nul & del "%~f0"\n"""
        with open(script_bat, "w", encoding="utf-8") as f: f.write(conteudo_bat)
        subprocess.Popen(script_bat, shell=True, cwd=dir_atual)
        if modo_gui and app_gui: app_gui.after(0, app_gui.destroy)
        time.sleep(0.5)
        os._exit(0)
    except Exception:
        if os.path.exists(exe_novo): os.remove(exe_novo)

def verificar_atualizacao_updater(install_path, modo_gui=False, app_gui=None):
    api_url = f"https://api.github.com/repos/{REPO_UPDATER}/releases/latest"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            dados = json.loads(response.read().decode())
        versao_remota = dados.get("tag_name", "").replace("v", "")
        if versao_remota and versao_remota > VERSION:
            if modo_gui and app_gui:
                mb.showinfo("Flycast Updater", app_gui._("msg_updater_update"), parent=app_gui)
            for asset in dados.get("assets", []):
                if asset["name"].endswith(".exe"):
                    aplicar_auto_atualizacao(asset["browser_download_url"], install_path, modo_gui, app_gui)
                    return True
    except Exception: pass
    return False