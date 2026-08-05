import os
import sys
import json
import subprocess
import time
import urllib.request
import datetime
import threading

try:
    import cloud_saves
except ImportError:
    cloud_saves = None

# ==========================================
# Flycast Updater - Launcher v2.1 (GUI & CLI)
# Desenvolvido por DaniboySan & Geminix
# ==========================================

VERSION = "2.1"
CONFIG_FILE = "config.json"
REPO_UPDATER = "dsantanna/flycast_updater"

# ==========================================
# FUNÇÕES NUCLEARES (USADAS PELA GUI E CLI)
# ==========================================
def carregar_configuracao():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
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
    except Exception:
        pass

def aplicar_auto_atualizacao(url_download, install_path, modo_gui=False, app_gui=None):
    exe_atual = sys.executable
    dir_atual = os.path.dirname(exe_atual)
    exe_novo = os.path.join(dir_atual, "FlycastUpdater_novo.exe")
    script_bat = os.path.join(dir_atual, "atualiza_updater.bat")
    
    if modo_gui and app_gui:
        app_gui.after(0, app_gui.label_status.configure, {"text": "Baixando nova versão do Atualizador...", "text_color": "orange"})
    
    try:
        urllib.request.urlretrieve(url_download, exe_novo)
        nome_exe = os.path.basename(exe_atual)
        conteudo_bat = f"""@echo off\ntimeout /t 2 /nobreak > NUL\ndel "{nome_exe}"\nren "FlycastUpdater_novo.exe" "{nome_exe}"\nstart "" "{nome_exe}"\n(goto) 2>nul & del "%~f0"\n"""
        with open(script_bat, "w") as f:
            f.write(conteudo_bat)
            
        subprocess.Popen(script_bat, shell=True)
        sys.exit(0)
    except Exception:
        if os.path.exists(exe_novo):
            os.remove(exe_novo)

def verificar_atualizacao_updater(install_path, modo_gui=False, app_gui=None):
    api_url = f"https://api.github.com/repos/{REPO_UPDATER}/releases/latest"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            dados = json.loads(response.read().decode())
            
        versao_remota = dados.get("tag_name", "").replace("v", "")
        if versao_remota and versao_remota > VERSION:
            for asset in dados.get("assets", []):
                if asset["name"].endswith(".exe"):
                    aplicar_auto_atualizacao(asset["browser_download_url"], install_path, modo_gui, app_gui)
                    return True
    except Exception:
        pass
    return False

# ==========================================
# MODO INTERFACE GRÁFICA (GUI)
# ==========================================
class ConsoleRedirector:
    def __init__(self, app):
        self.app = app

    def write(self, message):
        texto = message.strip()
        if not texto: return
        
        if "[*] Progresso:" in texto:
            try:
                pct_str = texto.split("%")[0].split(" ")[-1]
                pct_float = float(pct_str) / 100.0
                tamanhos = texto.split("(")[1].replace(")", "")
                
                self.app.after(0, self.app.progressbar.set, pct_float)
                self.app.after(0, self.app.label_status.configure, {
                    "text": f"🦔 Velocidade Sônica! Baixando... {pct_str}% ({tamanhos})",
                    "text_color": "cyan"
                })
            except Exception: pass
        elif "[!]" in texto or "Aviso de BIOS" in texto:
            # Alerta claro para falta de BIOS ou avisos importantes
            self.app.after(0, self.app.label_status.configure, {
                "text": f"⚠️ {texto}",
                "text_color": "#FF8C00" # Laranja de alerta
            })
        elif "Backup" in texto or "sincronização" in texto.lower() or "[✓]" in texto:
            # Feedback claro sobre operações de backup local ou nuvem
            self.app.after(0, self.app.label_status.configure, {
                "text": f"💾 {texto}",
                "text_color": "#00FF7F" # Verde esmeralda para sucesso/backup
            })
        else:
            self.app.after(0, self.app.label_status.configure, {"text": texto, "text_color": "cyan"})
            
    def flush(self): pass

def iniciar_gui():
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("blue") 

    class FlycastUpdaterApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title(f"🌀 Flycast Updater - v{VERSION}")
            self.geometry("550x550")
            self.resizable(False, False)
            self.config_atual = carregar_configuracao()

            self.label_titulo = ctk.CTkLabel(self, text="Flycast Auto-Updater", font=ctk.CTkFont(size=24, weight="bold"))
            self.label_titulo.pack(pady=(20, 5))
            self.label_sub = ctk.CTkLabel(self, text="Gerenciador de Atualizações e Cloud Saves", text_color="gray")
            self.label_sub.pack(pady=(0, 20))

            self.frame_opcoes = ctk.CTkFrame(self)
            self.frame_opcoes.pack(pady=10, padx=40, fill="both", expand=True)

            self.label_branch = ctk.CTkLabel(self.frame_opcoes, text="Versão do Emulador:", font=ctk.CTkFont(weight="bold"))
            self.label_branch.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
            self.combo_branch = ctk.CTkComboBox(self.frame_opcoes, values=["Master", "Dev"])
            self.combo_branch.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="e")
            self.combo_branch.set(self.config_atual.get("branch", "dev").capitalize())

            self.label_cloud = ctk.CTkLabel(self.frame_opcoes, text="Backup na Nuvem:", font=ctk.CTkFont(weight="bold"))
            self.label_cloud.grid(row=1, column=0, padx=20, pady=10, sticky="w")
            self.combo_cloud = ctk.CTkComboBox(self.frame_opcoes, values=["Nenhum", "Google Drive", "OneDrive"])
            self.combo_cloud.grid(row=1, column=1, padx=20, pady=10, sticky="e")
            nuvem_salva = self.config_atual.get("cloud_provider", "nenhum")
            if nuvem_salva == "gdrive": self.combo_cloud.set("Google Drive")
            elif nuvem_salva == "onedrive": self.combo_cloud.set("OneDrive")
            else: self.combo_cloud.set("Nenhum")

            self.switch_desktop = ctk.CTkSwitch(self.frame_opcoes, text="Criar Atalho no Desktop")
            self.switch_desktop.grid(row=2, column=0, columnspan=2, padx=20, pady=15, sticky="w")
            if self.config_atual.get("create_shortcut", False): self.switch_desktop.select()

            self.switch_startup = ctk.CTkSwitch(self.frame_opcoes, text="Iniciar com o Windows (Silencioso)")
            self.switch_startup.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="w")
            if self.config_atual.get("create_startup", False): self.switch_startup.select()

            self.progressbar = ctk.CTkProgressBar(self, width=400)
            self.progressbar.set(0)
            self.label_status = ctk.CTkLabel(self, text="Aguardando...", text_color="cyan")

            self.btn_atualizar = ctk.CTkButton(self, text="🚀 ATUALIZAR FLYCAST", height=40, font=ctk.CTkFont(weight="bold"), command=self.disparar_atualizacao)
            self.btn_atualizar.pack(pady=20)

        def disparar_atualizacao(self):
            self.btn_atualizar.configure(state="disabled", text="PROCESSANDO...")
            self.progressbar.pack(pady=(10, 0))
            self.label_status.pack(pady=(5, 10))
            threading.Thread(target=self.rodar_motor, daemon=True).start()

        def rodar_motor(self):
            terminal_original = sys.stdout
            sys.stdout = ConsoleRedirector(self)
            try:
                install_path = self.config_atual.get("install_path", os.getcwd())
                
                if getattr(sys, 'frozen', False):
                    atualizou = verificar_atualizacao_updater(install_path, modo_gui=True, app_gui=self)
                    if atualizou: return 

                branch_escolhida = self.combo_branch.get().lower()
                criar_desktop = self.switch_desktop.get() == 1
                criar_startup = self.switch_startup.get() == 1
                
                nuvem_escolhida = self.combo_cloud.get()
                cloud_prov, cloud_path = None, None
                if nuvem_escolhida == "Google Drive" and cloud_saves:
                    cloud_prov, cloud_path = "gdrive", cloud_saves.get_gdrive_path()
                elif nuvem_escolhida == "OneDrive" and cloud_saves:
                    cloud_prov, cloud_path = "onedrive", cloud_saves.get_onedrive_path()

                salvar_configuracao(branch_escolhida, criar_desktop, criar_startup, install_path, cloud_prov, cloud_path)

                import update_flycast
                update_flycast.SCRIPT_VERSION = f"{VERSION} (GUI)"
                update_flycast.INSTALL_DIR = install_path
                update_flycast.SHOULD_CREATE_SHORTCUT = criar_desktop
                update_flycast.SHOULD_CREATE_STARTUP = criar_startup
                update_flycast.CLOUD_PROVIDER = cloud_prov
                update_flycast.CLOUD_PATH = cloud_path
                update_flycast.VERSION_FILE = os.path.join(install_path, "version.txt")
                update_flycast.LOG_FILE = os.path.join(install_path, "flycast_updater.log")
                update_flycast.get_user_preference = lambda: branch_escolhida
                
                update_flycast.main()
            except Exception as e:
                self.after(0, self.label_status.configure, {"text": f"Erro crítico: {e}", "text_color": "red"})
            finally:
                sys.stdout = terminal_original
                self.after(0, self.btn_atualizar.configure, {"state": "normal", "text": "PRONTO!"})
                # Fecha a interface gráfica automaticamente após 2 segundos para dar tempo de ler o status final
                self.after(2000, self.destroy)

    app = FlycastUpdaterApp()
    app.mainloop()

# ==========================================
# MODO TERMINAL (CLI)
# ==========================================
def iniciar_cli(args):
    print(f"=" * 50)
    print(f"🌀 Flycast Updater - v{VERSION} (CLI Mode)")
    print(f"=" * 50)

    if "-silent" in args:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    config = carregar_configuracao()
    install_path = config.get("install_path", os.getcwd())
    
    if getattr(sys, 'frozen', False) and "-rollback" not in args and "-backup" not in args:
        verificar_atualizacao_updater(install_path)

    import update_flycast
    update_flycast.SCRIPT_VERSION = f"{VERSION} (CLI)"
    update_flycast.args_lower = args
    update_flycast.INSTALL_DIR = install_path
    update_flycast.SHOULD_CREATE_SHORTCUT = config.get("create_shortcut", False)
    update_flycast.SHOULD_CREATE_STARTUP = config.get("create_startup", False)
    update_flycast.CLOUD_PROVIDER = config.get("cloud_provider")
    update_flycast.CLOUD_PATH = config.get("cloud_path")
    update_flycast.VERSION_FILE = os.path.join(install_path, "version.txt")
    update_flycast.LOG_FILE = os.path.join(install_path, "flycast_updater.log")
    
    branch = config.get("branch", "dev")
    if "-master" in args: branch = "master"
    if "-dev" in args: branch = "dev"
    update_flycast.get_user_preference = lambda: branch

    update_flycast.main()

# ==========================================
# PONTO DE ENTRADA PRINCIPAL
# ==========================================
if __name__ == "__main__":
    args_lower = [arg.lower() for arg in sys.argv[1:]]
    gatilhos_cli = ['-nogui', '-silent', '-rollback', '-backup', '-dev', '-master', '-help', '-h']
    
    if any(g in args_lower for g in gatilhos_cli):
        iniciar_cli(args_lower)
    else:
        iniciar_gui()