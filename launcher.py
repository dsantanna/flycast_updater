import os
import sys
import json
import subprocess
import time
import urllib.request
import datetime
import threading
import tkinter as tk 
import webbrowser 

try:
    import cloud_saves
except ImportError:
    cloud_saves = None

# ==========================================
# Flycast Updater - Launcher v2.0 (GUI & CLI)
# Desenvolvido por DaniboySan & Geminix
# ==========================================

VERSION = "2.0"
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
# CLASSE DE TOOLTIPS FLUTUANTES
# ==========================================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def update_text(self, new_text):
        self.text = new_text

    def show_tooltip(self, event=None):
        if self.widget.cget("state") == "disabled" and "Rollback" not in self.text and "não detectado" not in self.text:
            return 
            
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#2b2b2b", foreground="#ffffff", relief='solid', borderwidth=1,
                         font=("Segoe UI", 9, "normal"), padx=8, pady=4)
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

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
            self.app.after(0, self.app.label_status.configure, {"text": f"⚠️ {texto}", "text_color": "#FF8C00"})
        elif "Backup" in texto or "Sincronizando" in texto or "[✓]" in texto or "Rollback" in texto or "[+]" in texto:
            self.app.after(0, self.app.label_status.configure, {"text": f"💾 {texto}", "text_color": "#00FF7F"})
        elif "Erro" in texto or "[-]" in texto:
             self.app.after(0, self.app.label_status.configure, {"text": f"❌ {texto}", "text_color": "#FF4C4C"})
        else:
            self.app.after(0, self.app.label_status.configure, {"text": texto, "text_color": "cyan"})
            
    def flush(self): pass

def iniciar_gui():
    import customtkinter as ctk
    from customtkinter import filedialog
    
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("blue") 

    class FlycastUpdaterApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title(f"🌀 Flycast Updater - v{VERSION}")
            self.geometry("620x780") 
            self.resizable(False, False)
            self.config_atual = carregar_configuracao()

            # --- CABEÇALHO ---
            self.frame_header = ctk.CTkFrame(self, fg_color="transparent")
            self.frame_header.pack(fill="x", padx=20, pady=(15, 0))
            
            self.label_titulo = ctk.CTkLabel(self.frame_header, text="Flycast Updater", font=ctk.CTkFont(size=24, weight="bold"))
            self.label_titulo.pack(side="top")
            
            self.label_sub = ctk.CTkLabel(self.frame_header, text="Gerenciador de Atualizações e Cloud Saves", text_color="gray")
            self.label_sub.pack(side="top", pady=(0, 10))

            self.btn_help = ctk.CTkButton(self.frame_header, text="❔ Ajuda", width=70, height=28, fg_color="#444", hover_color="#666", command=self.abrir_janela_ajuda)
            self.btn_help.place(relx=1.0, rely=0.0, anchor="ne")
            ToolTip(self.btn_help, "Clique aqui para ler o manual completo de uso.")

            # --- FRAME PRINCIPAL ---
            self.frame_opcoes = ctk.CTkFrame(self)
            self.frame_opcoes.pack(pady=10, padx=20, fill="both", expand=True)
            self.frame_opcoes.columnconfigure(0, weight=1)
            self.frame_opcoes.columnconfigure(1, weight=1)

            # 1. ESCOLHA DE DIRETÓRIO E BIOS
            self.frame_path_title = ctk.CTkFrame(self.frame_opcoes, fg_color="transparent")
            self.frame_path_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="ew")
            
            self.label_path = ctk.CTkLabel(self.frame_path_title, text="Local de Instalação do Emulador:", font=ctk.CTkFont(weight="bold"))
            self.label_path.pack(side="left")
            
            self.lbl_bios = ctk.CTkLabel(self.frame_path_title, text="BIOS: Aguardando...", font=ctk.CTkFont(size=12, weight="bold"))
            self.lbl_bios.pack(side="right")
            ToolTip(self.lbl_bios, "Verifica os arquivos dc_boot.bin e dc_flash.bin.\nEles são obrigatórios para rodar o emulador.")

            self.frame_path = ctk.CTkFrame(self.frame_opcoes, fg_color="transparent")
            self.frame_path.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="ew")
            self.frame_path.columnconfigure(0, weight=1)

            self.entry_path = ctk.CTkEntry(self.frame_path)
            self.entry_path.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            self.entry_path.insert(0, self.config_atual.get("install_path", os.getcwd()))
            self.entry_path.configure(state="readonly") 
            ToolTip(self.entry_path, "Este é o local onde o Flycast está (ou será) instalado.")

            self.btn_path = ctk.CTkButton(self.frame_path, text="Procurar...", width=80, command=self.escolher_diretorio)
            self.btn_path.grid(row=0, column=1)

            # 2. ESCOLHA DE BRANCH 
            self.label_branch = ctk.CTkLabel(self.frame_opcoes, text="Versão do Emulador:", font=ctk.CTkFont(weight="bold"))
            self.label_branch.grid(row=2, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")

            self.branch_var = ctk.StringVar(value=self.config_atual.get("branch", "dev").lower())

            self.frame_branches = ctk.CTkFrame(self.frame_opcoes, fg_color="transparent")
            self.frame_branches.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="ew")
            self.frame_branches.columnconfigure(0, weight=1)
            self.frame_branches.columnconfigure(1, weight=1)

            self.rb_master = ctk.CTkRadioButton(self.frame_branches, text="Branch Master", font=ctk.CTkFont(weight="bold"), variable=self.branch_var, value="master", command=self.ao_trocar_branch)
            self.rb_master.grid(row=0, column=0, sticky="w", padx=(0, 10))
            self.lbl_master_desc = ctk.CTkLabel(self.frame_branches, text="Lançamentos oficiais e\nestáveis do emulador.", text_color="gray", font=ctk.CTkFont(size=11), justify="left")
            self.lbl_master_desc.grid(row=1, column=0, sticky="nw", padx=(28, 0)) 
            ToolTip(self.rb_master, "Estável. Atualiza apenas quando há lançamentos fechados.")

            self.rb_dev = ctk.CTkRadioButton(self.frame_branches, text="Branch Dev", font=ctk.CTkFont(weight="bold"), variable=self.branch_var, value="dev", command=self.ao_trocar_branch)
            self.rb_dev.grid(row=0, column=1, sticky="w", padx=(0, 10))
            self.lbl_dev_desc = ctk.CTkLabel(self.frame_branches, text="Builds diárias da nuvem.\nNovos recursos e correções.", text_color="gray", font=ctk.CTkFont(size=11), justify="left")
            self.lbl_dev_desc.grid(row=1, column=1, sticky="nw", padx=(28, 0))
            ToolTip(self.rb_dev, "Baixa as modificações diárias do criador (Flyinghead).")

            # 3. BACKUP NA NUVEM
            self.label_cloud = ctk.CTkLabel(self.frame_opcoes, text="Sincronização de Saves na Nuvem:", font=ctk.CTkFont(weight="bold"))
            self.label_cloud.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")
            
            self.cloud_var = ctk.StringVar(value="nenhum")
            self.frame_cloud = ctk.CTkFrame(self.frame_opcoes, fg_color="transparent")
            self.frame_cloud.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="ew")

            has_gdrive = self.verificar_caminho_nuvem("Google Drive")
            has_onedrive = self.verificar_caminho_nuvem("OneDrive")

            self.rb_cloud_none = ctk.CTkRadioButton(self.frame_cloud, text="Nenhum", font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="nenhum")
            self.rb_cloud_none.pack(side="left", padx=(0, 15))
            ToolTip(self.rb_cloud_none, "Sincronização desativada.")

            self.rb_cloud_gdrive = ctk.CTkRadioButton(self.frame_cloud, text="Google Drive", font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="gdrive")
            self.rb_cloud_gdrive.pack(side="left", padx=(0, 15))
            if not has_gdrive:
                self.rb_cloud_gdrive.configure(state="disabled")
                ToolTip(self.rb_cloud_gdrive, "🔴 Google Drive não detectado no seu PC.\nBaixe e instale o aplicativo oficial para ativar.")
            else:
                ToolTip(self.rb_cloud_gdrive, "Faz o backup automático e passivo no seu Google Drive.")

            self.rb_cloud_onedrive = ctk.CTkRadioButton(self.frame_cloud, text="OneDrive", font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="onedrive")
            self.rb_cloud_onedrive.pack(side="left", padx=(0, 15))
            if not has_onedrive:
                self.rb_cloud_onedrive.configure(state="disabled")
                ToolTip(self.rb_cloud_onedrive, "🔴 OneDrive não detectado no seu PC.\nBaixe e instale o aplicativo oficial para ativar.")
            else:
                ToolTip(self.rb_cloud_onedrive, "Faz o backup automático e passivo no seu OneDrive.")

            nuvem_salva = self.config_atual.get("cloud_provider", "nenhum")
            if nuvem_salva == "gdrive" and has_gdrive: self.cloud_var.set("gdrive")
            elif nuvem_salva == "onedrive" and has_onedrive: self.cloud_var.set("onedrive")
            else: self.cloud_var.set("nenhum")

            # 4. SWITCHES (ATALHOS)
            self.switch_desktop = ctk.CTkSwitch(self.frame_opcoes, text="Criar Atalho no Desktop")
            self.switch_desktop.grid(row=6, column=0, columnspan=2, padx=20, pady=10, sticky="w")
            ToolTip(self.switch_desktop, "Cria um atalho na sua Área de Trabalho para iniciar o emulador por aqui.")
            if self.config_atual.get("create_shortcut", False): self.switch_desktop.select()

            self.switch_startup = ctk.CTkSwitch(self.frame_opcoes, text="Iniciar com o Windows (Modo Silencioso)")
            self.switch_startup.grid(row=7, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="w")
            ToolTip(self.switch_startup, "Garante que o Flycast seja atualizado sozinho ao ligar o PC.")
            if self.config_atual.get("create_startup", False): self.switch_startup.select()

            # --- PROGRESSO E STATUS ---
            self.progressbar = ctk.CTkProgressBar(self, width=400)
            self.progressbar.set(0)
            self.label_status = ctk.CTkLabel(self, text="Aguardando...", text_color="cyan")

            # --- NOVO SEMÁFORO DO EMULADOR ---
            self.lbl_emulador_status = ctk.CTkLabel(self, text="Emulador: Aguardando...", font=ctk.CTkFont(size=14, weight="bold"))
            self.lbl_emulador_status.pack(pady=(5, 10))

            # --- BOTÕES DE AÇÃO ---
            self.frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
            self.frame_botoes.pack(pady=(0, 10))

            self.btn_atualizar = ctk.CTkButton(self.frame_botoes, text="🚀 VERIFICANDO...", width=180, height=40, font=ctk.CTkFont(weight="bold"), command=lambda: self.preparar_motor("atualizar"))
            self.btn_atualizar.grid(row=0, column=0, padx=10)

            self.btn_rollback = ctk.CTkButton(self.frame_botoes, text="↩️ REVERTER", width=180, height=40, fg_color="#8B0000", hover_color="#A52A2A", font=ctk.CTkFont(weight="bold"), command=lambda: self.preparar_motor("rollback"))
            self.btn_rollback.grid(row=0, column=1, padx=10)
            
            self.tt_rollback = ToolTip(self.btn_rollback, "") 

            # --- RODAPÉ COM LINK ---
            self.lbl_rodape = ctk.CTkLabel(self, text="Desenvolvido por DaniboySan & Geminix • github.com/dsantanna", text_color="#1E90FF", cursor="hand2", font=ctk.CTkFont(size=11, underline=True))
            self.lbl_rodape.pack(side="bottom", pady=(0, 15))
            self.lbl_rodape.bind("<Button-1>", lambda e: webbrowser.open(f"https://github.com/{REPO_UPDATER}"))

            # Aciona as verificações iniciais 
            self.atualizar_status_diretorio(self.entry_path.get())

        def ao_trocar_branch(self):
            self.atualizar_status_diretorio(self.entry_path.get())

        def verificar_caminho_nuvem(self, escolha):
            if not cloud_saves: return False
            caminho = None
            if escolha == "Google Drive": caminho = cloud_saves.get_gdrive_path()
            elif escolha == "OneDrive": caminho = cloud_saves.get_onedrive_path()
            return caminho is not None and os.path.exists(caminho)

        def verificar_versao_em_background(self, path, branch):
            def rotina():
                self.lbl_emulador_status.configure(text="Emulador: 🔵 Verificando versão na nuvem...", text_color="cyan")
                self.btn_atualizar.configure(text="🚀 VERIFICANDO...")
                
                version_file = os.path.join(path, "version.txt")
                local_version = ""
                
                if os.path.exists(version_file):
                    with open(version_file, "r") as f:
                        local_version = f.read().strip()
                
                if not local_version:
                    self.lbl_emulador_status.configure(text="Emulador: 🟡 Desatualizado (Versão Local Desconhecida)", text_color="#FFD700")
                    self.btn_atualizar.configure(text="🚀 ATUALIZAR")
                    return

                remote_version = None
                try:
                    if branch == 'master':
                        api_url = "https://api.github.com/repos/flyinghead/flycast/releases/latest"
                        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=3) as response:
                            release = json.loads(response.read().decode('utf-8'))
                            remote_version = release.get("tag_name")
                    else:
                        api_url = "https://api.github.com/repos/flyinghead/flycast/commits?sha=dev&per_page=1"
                        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=3) as response:
                            commits = json.loads(response.read().decode('utf-8'))
                            if commits: remote_version = commits[0]["sha"]
                except Exception:
                    self.lbl_emulador_status.configure(text="Emulador: 🟡 Falha ao checar nuvem (Verifique a internet)", text_color="#FFD700")
                    self.btn_atualizar.configure(text="🚀 ATUALIZAR")
                    return

                if remote_version and (local_version == remote_version or local_version.startswith(remote_version)):
                    self.lbl_emulador_status.configure(text="Emulador: 🟢 Atualizado (Pronto para Jogar)", text_color="#00FF7F")
                    self.btn_atualizar.configure(text="🚀 JOGAR")
                else:
                    self.lbl_emulador_status.configure(text="Emulador: 🟡 Desatualizado (Nova versão disponível)", text_color="#FFD700")
                    self.btn_atualizar.configure(text="🚀 ATUALIZAR")

            threading.Thread(target=rotina, daemon=True).start()

        def atualizar_status_diretorio(self, path):
            if not path or not os.path.exists(path):
                self.lbl_bios.configure(text="BIOS: 🔴 Diretório Inválido", text_color="#FF4C4C")
                self.lbl_emulador_status.configure(text="Emulador: 🔴 Diretório Inválido", text_color="#FF4C4C")
                self.btn_rollback.configure(state="disabled")
                self.tt_rollback.update_text("Nenhum diretório válido foi selecionado.")
                self.btn_atualizar.configure(text="🚀 INSTALAR")
                return
                
            boot_data = os.path.exists(os.path.join(path, "data", "dc_boot.bin"))
            flash_data = os.path.exists(os.path.join(path, "data", "dc_flash.bin"))
            boot_root = os.path.exists(os.path.join(path, "dc_boot.bin"))
            flash_root = os.path.exists(os.path.join(path, "dc_flash.bin"))
            
            if boot_data and flash_data: self.lbl_bios.configure(text="BIOS: 🟢 Arquivos OK", text_color="#00FF7F")
            elif boot_root and flash_root: self.lbl_bios.configure(text="BIOS: 🟡 Local incorreto", text_color="#FFD700")
            else: self.lbl_bios.configure(text="BIOS: 🔴 Arquivos Ausentes", text_color="#FF4C4C")

            flycast_exe = os.path.join(path, "flycast.exe")
            if os.path.exists(flycast_exe):
                self.btn_atualizar.configure(text="🚀 VERIFICANDO...")
                self.verificar_versao_em_background(path, self.branch_var.get())
            else:
                self.lbl_emulador_status.configure(text="Emulador: 🔴 Ausente (Aguardando Instalação)", text_color="#FF4C4C")
                self.btn_atualizar.configure(text="🚀 INSTALAR")

            backup_path = os.path.join(path, "flycast_backup.zip")
            if os.path.exists(backup_path):
                self.btn_rollback.configure(state="normal")
                self.tt_rollback.update_text("Utilize APENAS se a nova versão apresentar problemas.\nRestaura o emulador para a versão do último backup.")
            else:
                self.btn_rollback.configure(state="disabled")
                self.tt_rollback.update_text("🔴 Botão inibido: Nenhum backup (flycast_backup.zip) foi\nencontrado neste diretório para fazer a reversão.")

        def escolher_diretorio(self):
            dir_escolhido = ctk.filedialog.askdirectory(initialdir=self.entry_path.get(), title="Selecione a pasta do Flycast")
            if dir_escolhido:
                self.entry_path.configure(state="normal")
                self.entry_path.delete(0, 'end')
                self.entry_path.insert(0, dir_escolhido)
                self.entry_path.configure(state="readonly")
                self.atualizar_status_diretorio(dir_escolhido)

        def abrir_janela_ajuda(self):
            win_ajuda = ctk.CTkToplevel(self)
            win_ajuda.title("Manual do Flycast Updater")
            win_ajuda.geometry("550x480")
            win_ajuda.attributes("-topmost", True)
            
            texto_ajuda = (
                "🌀 MANUAL DO FLYCAST UPDATER\n\n"
                "Este aplicativo mantém o seu emulador Flycast sempre atualizado com as\n"
                "versões mais recentes do GitHub e sincroniza seus jogos na nuvem.\n\n"
                "🖥️ COMO USAR AS VERSÕES:\n"
                "• Branch Master: É a versão oficial de lançamento. É muito estável, mas\n"
                "  demora para receber as novidades e correções do emulador.\n"
                "• Branch Dev: É a versão de desenvolvimento. Atualizada quase diariamente\n"
                "  para você ter as melhorias mais recentes instantaneamente.\n\n"
                "💾 CLOUD SAVES (Backup na Nuvem):\n"
                "Escolha o Google Drive ou OneDrive (o ícone ficará cinza se não estiverem\n"
                "instalados no seu Windows). O atualizador fará o backup automático\n"
                "do seu progresso prevenindo que você perca seus saves.\n\n"
                "🖧 USO PELO TERMINAL (PowerShell/CMD):\n"
                "Para usuários avançados, rode o executável com os parâmetros:\n"
                "  -nogui        : Roda no terminal de texto sem abrir janela visual.\n"
                "  -dev / -master: Força a baixar uma versão específica diretamente.\n"
                "  -rollback     : Desfaz a última atualização se o emulador quebrar.\n"
                "  -silent       : Roda invisível no fundo (Ideal para usar no Startup).\n"
                "  -reset        : Apaga suas configurações atuais guardadas."
            )
            
            lbl_texto = ctk.CTkLabel(win_ajuda, text=texto_ajuda, justify="left", font=ctk.CTkFont(size=13))
            lbl_texto.pack(padx=20, pady=20, fill="both", expand=True)

        def preparar_motor(self, acao):
            texto_atual = self.btn_atualizar.cget("text")
            
            self.btn_atualizar.configure(state="disabled")
            self.btn_rollback.configure(state="disabled")
            
            if acao == "atualizar": 
                if "JOGAR" in texto_atual:
                    self.btn_atualizar.configure(text="INICIANDO...")
                else:
                    self.btn_atualizar.configure(text="PROCESSANDO...")
            else: 
                self.btn_rollback.configure(text="REVERTENDO...")

            self.progressbar.pack(pady=(5, 0))
            self.label_status.pack(pady=(5, 10))
            threading.Thread(target=self.rodar_motor, args=(acao,), daemon=True).start()

        def rodar_motor(self, acao):
            terminal_original = sys.stdout
            sys.stdout = ConsoleRedirector(self)
            try:
                install_path = self.entry_path.get()
                
                if getattr(sys, 'frozen', False) and acao != "rollback":
                    atualizou = verificar_atualizacao_updater(install_path, modo_gui=True, app_gui=self)
                    if atualizou: return 

                branch_escolhida = self.branch_var.get()
                criar_desktop = self.switch_desktop.get() == 1
                criar_startup = self.switch_startup.get() == 1
                
                cloud_escolhida = self.cloud_var.get()
                cloud_prov, cloud_path = None, None
                
                if cloud_escolhida == "gdrive" and cloud_saves:
                    cloud_prov, cloud_path = "gdrive", cloud_saves.get_gdrive_path()
                elif cloud_escolhida == "onedrive" and cloud_saves:
                    cloud_prov, cloud_path = "onedrive", cloud_saves.get_onedrive_path()

                salvar_configuracao(branch_escolhida, criar_desktop, criar_startup, install_path, cloud_prov, cloud_path)

                import update_flycast
                update_flycast.SCRIPT_VERSION = f"{VERSION} (GUI)"
                
                if acao == "rollback": update_flycast.args_lower = ['-rollback']
                else: update_flycast.args_lower = []
                    
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
                self.after(0, self.btn_atualizar.configure, {"state": "normal"})
                self.after(0, self.atualizar_status_diretorio, self.entry_path.get())
                self.after(4000, self.destroy) 

    app = FlycastUpdaterApp()
    app.mainloop()

# ==========================================
# MODO TERMINAL (CLI)
# ==========================================
def configurar_interativamente():
    print("\n[?] Nenhuma configuração encontrada (ou -reset ativado).")
    print("-" * 50)
    
    while True:
        b = input("[1] Qual versão do Flycast deseja? [M]aster (Estável) ou [D]ev (Diária): ").strip().lower()
        if b in ['m', 'd', 'master', 'dev']:
            branch_choice = 'master' if b.startswith('m') else 'dev'
            break
    
    desk = input("[2] Criar atalho na Área de Trabalho? [S/N]: ").strip().lower()
    create_desktop = desk == 's'
    
    start = input("[3] Iniciar junto com o Windows (Modo Silencioso)? [S/N]: ").strip().lower()
    create_startup = start == 's'

    cloud_prov = None
    cloud_path = None
    if cloud_saves:
        print("\n[4] Backup na Nuvem (Cloud Saves)")
        print("  0 = Nenhum")
        print("  1 = Google Drive")
        print("  2 = OneDrive")
        c = input("-> Escolha o provedor [0/1/2]: ").strip()
        
        if c == '1':
            path = cloud_saves.get_gdrive_path()
            if path and os.path.exists(path):
                cloud_prov, cloud_path = 'gdrive', path
            else:
                print("[-] Aviso: Google Drive não encontrado no seu PC. Opção ignorada.")
        elif c == '2':
            path = cloud_saves.get_onedrive_path()
            if path and os.path.exists(path):
                cloud_prov, cloud_path = 'onedrive', path
            else:
                print("[-] Aviso: OneDrive não encontrado no seu PC. Opção ignorada.")

    install_path = os.getcwd()
    salvar_configuracao(branch_choice, create_desktop, create_startup, install_path, cloud_prov, cloud_path)
    print("\n[+] Preferências salvas com sucesso!\n")
    
    return {
        "branch": branch_choice,
        "create_shortcut": create_desktop,
        "create_startup": create_startup,
        "install_path": install_path,
        "cloud_provider": cloud_prov,
        "cloud_path": cloud_path
    }

def iniciar_cli(args):
    try:
        import ctypes
        ctypes.windll.kernel32.AttachConsole(-1)
        sys.stdout = open('CONOUT$', 'w', encoding='utf-8')
        sys.stderr = open('CONOUT$', 'w', encoding='utf-8')
    except Exception:
        pass

    print(f"=" * 50)
    print(f"🌀 Flycast Updater - v{VERSION} (CLI Mode)")
    print(f"=" * 50)

    if "-help" in args or "-h" in args or "--help" in args:
        print("Uso: FlycastUpdater.exe [argumentos]")
        print("  -nogui        Executa em modo texto (Terminal Clássico)")
        print("  -dev          Força a versão de desenvolvimento")
        print("  -master       Força a versão estável")
        print("  -rollback     Restaura o último backup funcional do emulador")
        print("  -silent       Executa em segundo plano sem exibir o terminal")
        print("  -backup       Apenas realiza o backup dos saves na nuvem")
        print("  -gdrive       Força/Ativa o uso do Google Drive para saves")
        print("  -onedrive     Força/Ativa o uso do OneDrive para saves")
        print("  -reset        Ignora o config.json e refaz a configuração inicial")
        sys.exit(0)

    if "-silent" in args:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    config = carregar_configuracao()
    
    flags_auto = ["-silent", "-backup", "-rollback", "-dev", "-master"]
    bypass_questions = any(f in args for f in flags_auto)
    
    if "-reset" in args or (not config and not bypass_questions):
        config = configurar_interativamente()
        
    install_path = config.get("install_path", os.getcwd())
    
    if getattr(sys, 'frozen', False) and "-rollback" not in args and "-backup" not in args:
        verificar_atualizacao_updater(install_path)

    if "-gdrive" in args and cloud_saves:
        path = cloud_saves.get_gdrive_path()
        if path and os.path.exists(path):
            config["cloud_provider"], config["cloud_path"] = "gdrive", path
        else:
            print("[-] Aviso: Google Drive não encontrado. Backup ignorado.")
    elif "-onedrive" in args and cloud_saves:
        path = cloud_saves.get_onedrive_path()
        if path and os.path.exists(path):
            config["cloud_provider"], config["cloud_path"] = "onedrive", path
        else:
            print("[-] Aviso: OneDrive não encontrado. Backup ignorado.")

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

if __name__ == "__main__":
    args_lower = [arg.lower() for arg in sys.argv[1:]]
    gatilhos_cli = ['-nogui', '-silent', '-rollback', '-backup', '-dev', '-master', '-help', '-h', '--help', '-reset', '-gdrive', '-onedrive']
    
    if any(g in args_lower for g in gatilhos_cli):
        iniciar_cli(args_lower)
    else:
        if os.name == 'nt':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            
            process_ids = (ctypes.c_uint * 2)()
            num_procs = kernel32.GetConsoleProcessList(process_ids, 2)
            
            if num_procs <= 1:
                hwnd = kernel32.GetConsoleWindow()
                if hwnd:
                    user32.ShowWindow(hwnd, 0)
                    
        iniciar_gui()