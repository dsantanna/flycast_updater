import os
import sys
import json
import time
import subprocess
import urllib.request
import threading
import tkinter.messagebox as mb

VERSION = "6.3.1"
REPO_UPDATER = "dsantanna/flycast_updater"

# ==========================================
# LÓGICA DO MODO TERMINAL / LEGADO
# ==========================================
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


# ==========================================
# LÓGICA DO MODO GUI (Big Blue)
# ==========================================
def checar_atualizacao_bg(app):
    """Busca atualizações em segundo plano sem travar a interface"""
    def rotina():
        api_url = f"https://api.github.com/repos/{REPO_UPDATER}/releases/latest"
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                dados = json.loads(response.read().decode())
            
            versao_remota = dados.get("tag_name", "").replace("v", "")
            if versao_remota and versao_remota > VERSION:
                for asset in dados.get("assets", []):
                    if asset["name"].endswith(".exe"):
                        download_url = asset["browser_download_url"]
                        # Encontrou versão nova! Desenha o botão magicamente na tela.
                        app.after(0, lambda u=download_url, v=versao_remota: exibir_botao_atualizacao(app, u, v))
                        break
        except Exception:
            pass # Se estiver sem internet ou o GitHub bloquear, falha silenciosamente
    threading.Thread(target=rotina, daemon=True).start()

def exibir_botao_atualizacao(app, url, versao):
    """Configura e exibe o botão dourado no cabeçalho"""
    if not hasattr(app, 'btn_update_app'): return
    
    app.btn_update_app.configure(command=lambda: iniciar_atualizacao_app(app, url, versao))
    app.btn_update_app.pack(side="left", padx=(0, 5), before=app.btn_bigpicture_top)
    
    try:
        from launcher import ToolTip
        app.btn_update_app._tooltip = ToolTip(app.btn_update_app, f"Nova versão v{versao} disponível!")
    except Exception: pass

def iniciar_atualizacao_app(app, url, versao):
    """Baixa e aplica a atualização do aplicativo com interface de progresso"""
    resposta = mb.askyesno("Atualização Disponível", f"A nova versão v{versao} do Flycast Updater está disponível!\n\nDeseja baixar e reiniciar o aplicativo agora?", parent=app)
    if not resposta: return

    app.btn_update_app.configure(text="⏳ Baixando...", state="disabled")
    
    if hasattr(app, 'progressbar') and hasattr(app, 'label_status'):
        app.progressbar.set(0)
        app.label_status.configure(text=f"Baixando nova versão v{versao}...", text_color="#FFD700")
        app.progressbar.pack(pady=(2, 0))
        app.label_status.pack(pady=(2, 5))

    def download_e_atualizar():
        exe_atual = sys.executable
        dir_atual = os.path.dirname(exe_atual)
        exe_novo = os.path.join(dir_atual, "FlycastUpdater_novo.exe")
        script_bat = os.path.join(dir_atual, "atualiza_updater.bat")

        try:
            urllib.request.urlretrieve(url, exe_novo)

            app.after(0, lambda: mb.showinfo("Download Concluído", "A atualização foi baixada com sucesso!\n\nO aplicativo será reiniciado automaticamente em instantes para aplicar a nova versão.", parent=app))

            if os.name == 'nt':
                nome_exe = os.path.basename(exe_atual)
                conteudo_bat = f"""@echo off\ncd /d "{dir_atual}"\n:wait\ntimeout /t 1 /nobreak > NUL\ndel "{nome_exe}"\nif exist "{nome_exe}" goto wait\nren "FlycastUpdater_novo.exe" "{nome_exe}"\nstart "" "{nome_exe}"\n(goto) 2>nul & del "%~f0"\n"""
                with open(script_bat, "w", encoding="utf-8") as f:
                    f.write(conteudo_bat)

                # Executa o .bat de forma 100% invisível (0x08000000 = CREATE_NO_WINDOW)
                subprocess.Popen(script_bat, shell=True, cwd=dir_atual, creationflags=0x08000000)
            
            app.after(1000, app.destroy)
            time.sleep(1)
            os._exit(0)

        except Exception as e:
            if os.path.exists(exe_novo): os.remove(exe_novo)
            app.after(0, lambda: mb.showerror("Erro de Download", f"Ocorreu um erro ao baixar a atualização:\n{e}", parent=app))
            app.after(0, lambda: app.btn_update_app.configure(text="🌟 Atualizar Big Blue", state="normal"))
            if hasattr(app, 'label_status'):
                app.after(0, lambda: app.label_status.configure(text="Erro ao atualizar.", text_color="red"))

    threading.Thread(target=download_e_atualizar, daemon=True).start()