import os
import sys
import json
import subprocess
import time
import urllib.request
import urllib.parse
import datetime
import threading
import configparser
import zipfile
import shutil
import tkinter as tk 
import tkinter.messagebox as mb
import webbrowser 

try:
    import cloud_saves
except ImportError:
    cloud_saves = None

# ==========================================
# Flycast Updater - Launcher v3.0 (Emerald Coast Edition)
# Desenvolvido por DaniboySan & Geminix
# ==========================================

VERSION = "3.0"
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

def salvar_configuracao(branch, create_shortcut, create_startup, install_path, cloud_prov, cloud_path, setup_completed=False, setup_declined=False):
    config_data = {
        "branch": branch,
        "create_shortcut": create_shortcut,
        "create_startup": create_startup,
        "install_path": install_path,
        "cloud_provider": cloud_prov,
        "cloud_path": cloud_path,
        "setup_completed": setup_completed,
        "setup_declined": setup_declined
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    except Exception:
        pass

def obter_token_retroachievements(usuario, senha):
    url = f"https://retroachievements.org/dorequest.php?r=login&u={urllib.parse.quote(usuario)}&p={urllib.parse.quote(senha)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'FlycastUpdater/3.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            resposta = json.loads(response.read().decode('utf-8'))
            if resposta.get("Success"):
                return resposta.get("Token")
    except Exception as e:
        print(f"Erro ao buscar token RA: {e}")
    return None

def atualizar_emu_cfg(install_path, roms_path=None, ra_enabled=None, ra_user=None, ra_pass=None, ra_hardcore=None, 
                      vmu_individual=None, fetch_boxart=None, vga_cable=None, discord_presence=None,
                      show_osd_vmu=None, vmu_sound=None, bios_path=None,
                      vid_api=None, vid_res=None, vid_full=None, vid_int=None, vid_lin=None, vid_vsync=None):
    """
    Lê e atualiza o arquivo emu.cfg do Flycast utilizando o padrão correto de seções (INI).
    """
    caminhos_possiveis = [
        os.path.join(install_path, "emu.cfg"),
        os.path.join(install_path, "data", "emu.cfg")
    ]
    
    cfg_path = None
    for p in caminhos_possiveis:
        if os.path.exists(p):
            cfg_path = p
            break
            
    if not cfg_path:
        cfg_path = os.path.join(install_path, "emu.cfg")

    config = configparser.RawConfigParser(strict=False)
    config.optionxform = str 
    
    if os.path.exists(cfg_path):
        try:
            config.read(cfg_path, encoding='utf-8')
        except Exception as e:
            print(f"Erro ao ler emu.cfg: {e}")
            return False

    if not config.has_section('achievements'):
        config.add_section('achievements')
    if not config.has_section('config'):
        config.add_section('config')
    if not config.has_section('audio'):
        config.add_section('audio')
    if not config.has_section('window'):
        config.add_section('window')

    # RetroAchievements
    if ra_enabled is not None:
        config.set('achievements', 'Enabled', 'yes' if ra_enabled else 'no')
    if ra_hardcore is not None:
        config.set('achievements', 'HardcoreMode', 'yes' if ra_hardcore else 'no')
    if ra_user is not None:
        config.set('achievements', 'UserName', ra_user)
    if ra_pass is not None:
        config.set('achievements', 'Token', ra_pass)

    # Config e QoL
    if roms_path:
        config.set('config', 'Dreamcast.ContentPath', roms_path.replace("/", "\\"))
    if vmu_individual is not None:
        config.set('config', 'PerGameVmu', 'yes' if vmu_individual else 'no')
    if fetch_boxart is not None:
        config.set('config', 'FetchBoxart', 'yes' if fetch_boxart else 'no')
        config.set('config', 'BoxartDisplayMode', 'yes' if fetch_boxart else 'no')
    if vga_cable is not None:
        config.set('config', 'Dreamcast.Cable', '0' if vga_cable else '3') 
    if discord_presence is not None:
        config.set('config', 'DiscordPresence', 'yes' if discord_presence else 'no')
    if show_osd_vmu is not None:
        config.set('config', 'ShowOsdVmu', 'yes' if show_osd_vmu else 'no')
    if bios_path is not None:
        config.set('config', 'Dreamcast.BiosPath', bios_path.replace("/", "\\"))

    # Configurações de Vídeo (Mapeamento Exato do Flycast)
    if vid_api is not None:
        api_map = {"OpenGL": "0", "DirectX 9": "1", "DirectX 11": "2", "Vulkan": "4"}
        config.set('config', 'pvr.rend', api_map.get(vid_api, "2"))
    if vid_res is not None:
        config.set('config', 'rend.Resolution', vid_res)
    if vid_int is not None:
        config.set('config', 'rend.IntegerScale', 'yes' if vid_int else 'no')
    if vid_lin is not None:
        config.set('config', 'rend.LinearInterpolation', 'yes' if vid_lin else 'no')
    if vid_vsync is not None:
        config.set('config', 'rend.vsync', 'yes' if vid_vsync else 'no')

    # Tela Cheia (Seção Window)
    if vid_full is not None:
        config.set('window', 'fullscreen', 'yes' if vid_full else 'no')

    # Audio
    if vmu_sound is not None:
        config.set('audio', 'VmuSound', 'yes' if vmu_sound else 'no')

    try:
        os.makedirs(os.path.dirname(os.path.abspath(cfg_path)), exist_ok=True)
        with open(cfg_path, 'w', encoding='utf-8') as f:
            config.write(f, space_around_delimiters=True)
        return True
    except Exception as e:
        print(f"Erro ao salvar emu.cfg: {e}")
        return False

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
        try:
            if self.widget.cget("state") == "disabled" and "Rollback" not in self.text and "não detectado" not in self.text:
                return 
        except Exception:
            pass
            
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
            self.title(f"🌀 Flycast Updater - v{VERSION} (Emerald Coast)")
            self.geometry("620x920") 
            self.resizable(False, False)
            self.config_atual = carregar_configuracao()
            self.token_ra_salvo = "" 
            self.bios_prompt_done = False

            # --- CABEÇALHO ---
            self.frame_header = ctk.CTkFrame(self, fg_color="transparent")
            self.frame_header.pack(fill="x", padx=20, pady=(15, 0))
            
            self.label_titulo = ctk.CTkLabel(self.frame_header, text="Flycast Updater", font=ctk.CTkFont(size=24, weight="bold"))
            self.label_titulo.pack(side="top")
            
            self.label_sub = ctk.CTkLabel(self.frame_header, text="Gerenciador de Atualizações, Nuvem e Configurações", text_color="gray")
            self.label_sub.pack(side="top", pady=(0, 10))

            self.btn_help = ctk.CTkButton(self.frame_header, text="❔ Ajuda", width=70, height=28, fg_color="#444", hover_color="#666", command=self.abrir_janela_ajuda)
            self.btn_help.place(relx=1.0, rely=0.0, anchor="ne")
            ToolTip(self.btn_help, "Clique aqui para ler o manual completo de uso.")

            # --- SISTEMA DE ABAS (v3.0 Emerald Coast) ---
            self.tabview = ctk.CTkTabview(self, width=580, height=660)
            self.tabview.pack(pady=5, padx=20, fill="both", expand=True)
            
            self.tab_atualizador = self.tabview.add("🚀 Nuvem")
            self.tab_config = self.tabview.add("⚙️ Emulador")
            self.tab_video = self.tabview.add("🖥️ Vídeo")
            self.tab_saves = self.tabview.add("🔄 Saves")

            # ==========================================
            # ABA 1: ATUALIZADOR & NUVEM
            # ==========================================
            self.frame_path_title = ctk.CTkFrame(self.tab_atualizador, fg_color="transparent")
            self.frame_path_title.pack(fill="x", padx=10, pady=(10, 2))
            
            self.label_path = ctk.CTkLabel(self.frame_path_title, text="Local de Instalação do Emulador:", font=ctk.CTkFont(weight="bold"))
            self.label_path.pack(side="left")
            
            self.lbl_bios = ctk.CTkLabel(self.frame_path_title, text="BIOS: Aguardando...", font=ctk.CTkFont(size=12, weight="bold"))
            self.lbl_bios.pack(side="right")
            ToolTip(self.lbl_bios, "Verifica os arquivos dc_boot.bin e dc_flash.bin.\nEles são obrigatórios para rodar o emulador.")

            self.frame_path = ctk.CTkFrame(self.tab_atualizador, fg_color="transparent")
            self.frame_path.pack(fill="x", padx=10, pady=(0, 10))
            self.frame_path.columnconfigure(0, weight=1)

            self.entry_path = ctk.CTkEntry(self.frame_path)
            self.entry_path.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            self.entry_path.insert(0, self.config_atual.get("install_path", os.getcwd()))
            self.entry_path.configure(state="readonly") 
            ToolTip(self.entry_path, "Este é o local onde o Flycast está (ou será) instalado.")

            self.btn_path = ctk.CTkButton(self.frame_path, text="Procurar...", width=80, command=self.escolher_diretorio)
            self.btn_path.grid(row=0, column=1)

            self.label_branch = ctk.CTkLabel(self.tab_atualizador, text="Versão do Emulador:", font=ctk.CTkFont(weight="bold"))
            self.label_branch.pack(anchor="w", padx=10, pady=(5, 2))

            self.branch_var = ctk.StringVar(value=self.config_atual.get("branch", "dev").lower())

            self.frame_branches = ctk.CTkFrame(self.tab_atualizador, fg_color="transparent")
            self.frame_branches.pack(fill="x", padx=10, pady=(0, 10))
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

            self.label_cloud = ctk.CTkLabel(self.tab_atualizador, text="Sincronização de Saves na Nuvem:", font=ctk.CTkFont(weight="bold"))
            self.label_cloud.pack(anchor="w", padx=10, pady=(5, 2))
            
            self.cloud_var = ctk.StringVar(value="nenhum")
            self.frame_cloud = ctk.CTkFrame(self.tab_atualizador, fg_color="transparent")
            self.frame_cloud.pack(fill="x", padx=10, pady=(0, 10))

            has_gdrive = self.verificar_caminho_nuvem("Google Drive")
            has_onedrive = self.verificar_caminho_nuvem("OneDrive")

            self.rb_cloud_none = ctk.CTkRadioButton(self.frame_cloud, text="Nenhum", font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="nenhum")
            self.rb_cloud_none.pack(side="left", padx=(0, 15))

            self.rb_cloud_gdrive = ctk.CTkRadioButton(self.frame_cloud, text="Google Drive", font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="gdrive")
            self.rb_cloud_gdrive.pack(side="left", padx=(0, 15))
            if not has_gdrive: self.rb_cloud_gdrive.configure(state="disabled")

            self.rb_cloud_onedrive = ctk.CTkRadioButton(self.frame_cloud, text="OneDrive", font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="onedrive")
            self.rb_cloud_onedrive.pack(side="left", padx=(0, 15))
            if not has_onedrive: self.rb_cloud_onedrive.configure(state="disabled")

            nuvem_salva = self.config_atual.get("cloud_provider", "nenhum")
            if nuvem_salva == "gdrive" and has_gdrive: self.cloud_var.set("gdrive")
            elif nuvem_salva == "onedrive" and has_onedrive: self.cloud_var.set("onedrive")
            else: self.cloud_var.set("nenhum")

            self.switch_desktop = ctk.CTkSwitch(self.tab_atualizador, text="Criar Atalho no Desktop")
            self.switch_desktop.pack(anchor="w", padx=10, pady=5)
            if self.config_atual.get("create_shortcut", False): self.switch_desktop.select()

            self.switch_startup = ctk.CTkSwitch(self.tab_atualizador, text="Iniciar com o Windows (Modo Silencioso)")
            self.switch_startup.pack(anchor="w", padx=10, pady=5)
            if self.config_atual.get("create_startup", False): self.switch_startup.select()

            self.btn_reconfig = ctk.CTkButton(self.tab_atualizador, text="⚙️ Reconfigurar Emulador e ROMs", width=220, height=28, fg_color="#333", hover_color="#555", command=lambda: self.tabview.set("⚙️ Emulador"))
            self.btn_reconfig.pack(anchor="w", padx=10, pady=(5, 5))
            ToolTip(self.btn_reconfig, "Abre a aba para alterar pastas de ROMs e credenciais do RetroAchievements.")

            # ==========================================
            # ABA 2: CONFIGURAR EMULADOR
            # ==========================================
            self.label_roms_title = ctk.CTkLabel(self.tab_config, text="Pasta de Jogos (ROMs / ISOs / GDI):", font=ctk.CTkFont(weight="bold"))
            self.label_roms_title.pack(anchor="w", padx=10, pady=(15, 5))

            self.frame_roms = ctk.CTkFrame(self.tab_config, fg_color="transparent")
            self.frame_roms.pack(fill="x", padx=10, pady=(0, 10))
            self.frame_roms.columnconfigure(0, weight=1)

            self.entry_roms = ctk.CTkEntry(self.frame_roms)
            self.entry_roms.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            self.entry_roms.configure(state="readonly")
            
            self.btn_roms = ctk.CTkButton(self.frame_roms, text="Procurar...", width=80, command=self.escolher_diretorio_roms)
            self.btn_roms.grid(row=0, column=1)

            self.label_ra_title = ctk.CTkLabel(self.tab_config, text="RetroAchievements & Conquistas:", font=ctk.CTkFont(weight="bold"))
            self.label_ra_title.pack(anchor="w", padx=10, pady=(5, 5))

            self.switch_ra = ctk.CTkSwitch(self.tab_config, text="Ativar RetroAchievements no Emulador")
            self.switch_ra.pack(anchor="w", padx=10, pady=5)

            self.frame_ra_cred = ctk.CTkFrame(self.tab_config, fg_color="transparent")
            self.frame_ra_cred.pack(fill="x", padx=10, pady=2)
            self.frame_ra_cred.columnconfigure(1, weight=1)

            self.lbl_ra_user = ctk.CTkLabel(self.frame_ra_cred, text="Usuário:")
            self.lbl_ra_user.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=2)
            self.entry_ra_user = ctk.CTkEntry(self.frame_ra_cred, placeholder_text="Seu nick no site")
            self.entry_ra_user.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)

            self.lbl_ra_pass = ctk.CTkLabel(self.frame_ra_cred, text="Senha / Token:")
            self.lbl_ra_pass.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=2)
            
            self.entry_ra_pass = ctk.CTkEntry(self.frame_ra_cred, show="*", placeholder_text="Sua senha ou Web API Key")
            self.entry_ra_pass.grid(row=1, column=1, sticky="ew", pady=2)
            
            self.btn_toggle_senha = ctk.CTkButton(self.frame_ra_cred, text="👁", width=30, fg_color="transparent", border_width=1, text_color="gray", hover_color="#444", command=self.toggle_senha_visibility)
            self.btn_toggle_senha.grid(row=1, column=2, padx=(5, 0), pady=2)

            self.switch_hardcore = ctk.CTkSwitch(self.tab_config, text="Modo Hardcore (Desativa Save States e Trapaças)")
            self.switch_hardcore.pack(anchor="w", padx=10, pady=(5, 5))

            self.label_qol_title = ctk.CTkLabel(self.tab_config, text="Melhorias e Qualidade de Vida (QoL):", font=ctk.CTkFont(weight="bold"))
            self.label_qol_title.pack(anchor="w", padx=10, pady=(10, 5))

            self.frame_qol = ctk.CTkFrame(self.tab_config, fg_color="transparent")
            self.frame_qol.pack(fill="x", padx=10)
            self.frame_qol.columnconfigure(0, weight=1)
            self.frame_qol.columnconfigure(1, weight=1)

            self.switch_vmu = ctk.CTkSwitch(self.frame_qol, text="VMU Individual por Jogo")
            self.switch_vmu.grid(row=0, column=0, sticky="w", pady=5)

            self.switch_boxart = ctk.CTkSwitch(self.frame_qol, text="Baixar Capas Automático")
            self.switch_boxart.grid(row=0, column=1, sticky="w", pady=5)

            self.switch_vga = ctk.CTkSwitch(self.frame_qol, text="Otimizar Gráficos (VGA)")
            self.switch_vga.grid(row=1, column=0, sticky="w", pady=5)

            self.switch_discord = ctk.CTkSwitch(self.frame_qol, text="Status no Discord")
            self.switch_discord.grid(row=1, column=1, sticky="w", pady=5)

            self.switch_osd_vmu = ctk.CTkSwitch(self.frame_qol, text="Mostrar VMU na Tela")
            self.switch_osd_vmu.grid(row=2, column=0, sticky="w", pady=5)

            self.switch_vmu_sound = ctk.CTkSwitch(self.frame_qol, text="Ativar Sons do VMU")
            self.switch_vmu_sound.grid(row=2, column=1, sticky="w", pady=5)

            self.btn_salvar_config_emu = ctk.CTkButton(self.tab_config, text="💾 Salvar Configurações do Emulador", width=280, height=35, font=ctk.CTkFont(weight="bold"), command=self.salvar_configuracoes_emulador)
            self.btn_salvar_config_emu.pack(anchor="center", pady=(15, 10))

            # ==========================================
            # ABA 3: VÍDEO & GRÁFICOS
            # ==========================================
            self.label_video_title = ctk.CTkLabel(self.tab_video, text="Configurações de Vídeo (Básicas)", font=ctk.CTkFont(size=16, weight="bold"))
            self.label_video_title.pack(anchor="w", padx=10, pady=(15, 5))

            self.label_video_aviso = ctk.CTkLabel(self.tab_video, text="⚠️ Aviso: Estas são configurações básicas do emulador.\nSe você quiser modificar opções avançadas ou se encontrar\nproblemas de performance, verifique o menu de vídeo dentro do próprio Flycast.", text_color="#FFD700", justify="left")
            self.label_video_aviso.pack(anchor="w", padx=10, pady=(0, 15))

            self.frame_video_options = ctk.CTkFrame(self.tab_video, fg_color="transparent")
            self.frame_video_options.pack(fill="x", padx=10)

            self.api_var = ctk.StringVar(value="DirectX 11")

            self.lbl_api = ctk.CTkLabel(self.frame_video_options, text="Gráficos API:", font=ctk.CTkFont(weight="bold"))
            self.lbl_api.grid(row=0, column=0, sticky="w", pady=(5, 0), padx=(0, 10))

            self.frame_api_rb = ctk.CTkFrame(self.frame_video_options, fg_color="transparent")
            self.frame_api_rb.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 15))

            self.rb_opengl = ctk.CTkRadioButton(self.frame_api_rb, text="OpenGL", variable=self.api_var, value="OpenGL")
            self.rb_opengl.pack(side="left", padx=(0, 15))
            ToolTip(self.rb_opengl, "API clássica e madura. Muito compatível, mas pode consumir mais CPU. Ideal para PCs antigos.")

            self.rb_vulkan = ctk.CTkRadioButton(self.frame_api_rb, text="Vulkan", variable=self.api_var, value="Vulkan")
            self.rb_vulkan.pack(side="left", padx=(0, 15))
            ToolTip(self.rb_vulkan, "API moderna. Altíssimo desempenho e baixo uso de CPU. Recomendada para placas de vídeo recentes.")

            self.rb_dx9 = ctk.CTkRadioButton(self.frame_api_rb, text="DirectX 9", variable=self.api_var, value="DirectX 9")
            self.rb_dx9.pack(side="left", padx=(0, 15))
            ToolTip(self.rb_dx9, "Legado do Windows. Útil apenas se o PC for extremamente antigo e não suportar bem o OpenGL.")

            self.rb_dx11 = ctk.CTkRadioButton(self.frame_api_rb, text="DirectX 11", variable=self.api_var, value="DirectX 11")
            self.rb_dx11.pack(side="left", padx=(0, 15))
            ToolTip(self.rb_dx11, "Ótima alternativa ao Vulkan no Windows. Excelente estabilidade e performance.")

            self.lbl_res = ctk.CTkLabel(self.frame_video_options, text="Resolução Interna:")
            self.lbl_res.grid(row=2, column=0, sticky="w", pady=5, padx=(0, 10))
            self.combo_res = ctk.CTkComboBox(self.frame_video_options, values=[
                "640x480 (Nativo)", 
                "960x720 (1.5x)", 
                "1280x960 (2x)", 
                "1440x1080 (3x)", 
                "1920x1440 (4x)", 
                "2880x2160 (6x)"
            ], state="readonly", width=180)
            self.combo_res.grid(row=2, column=1, sticky="w", pady=5)
            self.combo_res.set("640x480 (Nativo)")

            self.switch_fullscreen = ctk.CTkSwitch(self.frame_video_options, text="Tela Cheia")
            self.switch_fullscreen.grid(row=3, column=0, columnspan=2, sticky="w", pady=(15, 5))

            self.switch_integer = ctk.CTkSwitch(self.frame_video_options, text="Escala Inteira")
            self.switch_integer.grid(row=4, column=0, columnspan=2, sticky="w", pady=5)

            self.switch_linear = ctk.CTkSwitch(self.frame_video_options, text="Interpolação Linear")
            self.switch_linear.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)

            self.switch_vsync = ctk.CTkSwitch(self.frame_video_options, text="Sincronização Vertical (V-Sync)")
            self.switch_vsync.grid(row=6, column=0, columnspan=2, sticky="w", pady=5)

            self.btn_salvar_video = ctk.CTkButton(self.tab_video, text="💾 Salvar Configurações de Vídeo", width=280, height=35, font=ctk.CTkFont(weight="bold"), command=self.salvar_configuracoes_video)
            self.btn_salvar_video.pack(pady=(30, 10))

            # ==========================================
            # ABA 4: RESTAURAR SAVES
            # ==========================================
            self.label_saves_title = ctk.CTkLabel(self.tab_saves, text="Restaurar Backups da Nuvem", font=ctk.CTkFont(size=16, weight="bold"))
            self.label_saves_title.pack(anchor="w", padx=10, pady=(15, 5))
            
            self.label_saves_desc = ctk.CTkLabel(self.tab_saves, text="Selecione um arquivo .zip de backup de saves do seu Google Drive ou OneDrive\npara extrair de volta na pasta do emulador.", text_color="gray", justify="left")
            self.label_saves_desc.pack(anchor="w", padx=10, pady=(0, 15))

            self.frame_saves_list = ctk.CTkFrame(self.tab_saves, fg_color="transparent")
            self.frame_saves_list.pack(fill="x", padx=10, pady=5)

            self.btn_buscar_saves = ctk.CTkButton(self.frame_saves_list, text="🔄 Buscar Backups", width=140, command=self.buscar_backups_saves)
            self.btn_buscar_saves.pack(side="left", padx=(0, 10))

            self.combo_backups = ctk.CTkComboBox(self.frame_saves_list, values=["Nenhum backup carregado..."], width=350, state="readonly")
            self.combo_backups.pack(side="left", fill="x", expand=True)
            self.combo_backups.set("Clique em Buscar Backups...")

            self.btn_restaurar_save = ctk.CTkButton(self.tab_saves, text="📥 Extrair e Restaurar Saves", width=280, height=35, font=ctk.CTkFont(weight="bold"), fg_color="#228B22", hover_color="#006400", command=self.restaurar_backup_selecionado)
            self.btn_restaurar_save.pack(pady=(20, 10))
            self.btn_restaurar_save.configure(state="disabled")
            
            self.arquivos_backup_encontrados = {}

            self.carregar_dados_atuais_emu_cfg()

            # --- PROGRESSO E STATUS GERAL ---
            self.progressbar = ctk.CTkProgressBar(self, width=540)
            self.progressbar.set(0)
            self.label_status = ctk.CTkLabel(self, text="Aguardando...", text_color="cyan")

            # --- SEMÁFORO DO EMULADOR ---
            self.lbl_emulador_status = ctk.CTkLabel(self, text="Emulador: Aguardando...", font=ctk.CTkFont(size=14, weight="bold"))
            self.lbl_emulador_status.pack(pady=(2, 5))

            # --- BOTÕES DE AÇÃO PRINCIPAL ---
            self.frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
            self.frame_botoes.pack(pady=(0, 10))

            self.btn_atualizar = ctk.CTkButton(self.frame_botoes, text="🚀 VERIFICANDO...", width=220, height=38, font=ctk.CTkFont(weight="bold"), command=lambda: self.preparar_motor("atualizar"))
            self.btn_atualizar.grid(row=0, column=0, padx=10)

            self.btn_rollback = ctk.CTkButton(self.frame_botoes, text="↩️ REVERTER", width=180, height=38, fg_color="#8B0000", hover_color="#A52A2A", font=ctk.CTkFont(weight="bold"), command=lambda: self.preparar_motor("rollback"))
            self.btn_rollback.grid(row=0, column=1, padx=10)
            
            self.tt_rollback = ToolTip(self.btn_rollback, "") 

            # --- RODAPÉ COM LINK ---
            self.lbl_rodape = ctk.CTkLabel(self, text="Desenvolvido por DaniboySan & Geminix • github.com/dsantanna", text_color="#1E90FF", cursor="hand2", font=ctk.CTkFont(size=11, underline=True))
            self.lbl_rodape.pack(side="bottom", pady=(0, 5))
            self.lbl_rodape.bind("<Button-1>", lambda e: webbrowser.open(f"https://github.com/{REPO_UPDATER}"))

            self.atualizar_status_diretorio(self.entry_path.get())
            
            self.after(200, self.verificar_primeiro_acesso)

        def toggle_senha_visibility(self):
            if self.entry_ra_pass.cget("show") == "*":
                self.entry_ra_pass.configure(show="")
                self.btn_toggle_senha.configure(text="🙈") 
            else:
                self.entry_ra_pass.configure(show="*")
                self.btn_toggle_senha.configure(text="👁")

        def verificar_primeiro_acesso(self):
            completo = self.config_atual.get("setup_completed", False)
            recusado = self.config_atual.get("setup_declined", False)
            
            if not completo and not recusado:
                resposta = mb.askyesno(
                    "Flycast Updater - v3.0 (Emerald Coast)",
                    "Bem-vindo à v3.0 (Emerald Coast Edition)!\n\n"
                    "Deseja ajuda para configurar rapidamente a pasta de ROMs e o RetroAchievements agora?",
                    parent=self
                )
                if resposta:
                    self.tabview.set("⚙️ Emulador")
                    self.config_atual["setup_completed"] = True
                else:
                    self.config_atual["setup_declined"] = True
                
                salvar_configuracao(
                    self.branch_var.get(),
                    self.switch_desktop.get() == 1,
                    self.switch_startup.get() == 1,
                    self.entry_path.get(),
                    self.cloud_var.get() if self.cloud_var.get() != "nenhum" else None,
                    None,
                    setup_completed=self.config_atual.get("setup_completed", False),
                    setup_declined=self.config_atual.get("setup_declined", False)
                )

        def resolver_bios_mal_posicionada(self, path):
            if getattr(self, 'bios_prompt_done', False):
                return
            self.bios_prompt_done = True
            
            resposta_mover = mb.askyesno(
                "BIOS em Local Incorreto",
                "Os arquivos da BIOS foram encontrados na pasta raiz do emulador.\n\n"
                "O padrão do Flycast é armazená-los na pasta 'data'. Deseja que eu mova os arquivos para a pasta correta automaticamente para você?",
                parent=self
            )
            
            if resposta_mover:
                pasta_data = os.path.join(path, "data")
                os.makedirs(pasta_data, exist_ok=True)
                try:
                    shutil.move(os.path.join(path, "dc_boot.bin"), os.path.join(pasta_data, "dc_boot.bin"))
                    shutil.move(os.path.join(path, "dc_flash.bin"), os.path.join(pasta_data, "dc_flash.bin"))
                    mb.showinfo("Sucesso", "Arquivos de BIOS movidos para a pasta 'data' com sucesso!", parent=self)
                    self.atualizar_status_diretorio(path)
                except Exception as e:
                    mb.showerror("Erro", f"Não foi possível mover os arquivos: {e}", parent=self)
            else:
                resposta_config = mb.askyesno(
                    "Configurar Caminho Personalizado",
                    "Já que os arquivos serão mantidos na pasta raiz, deseja registrar essa pasta nas opções do emulador (Paths Personalizados -> Pastas da BIOS)?\n\nIsso resolverá o aviso definitivamente.",
                    parent=self
                )
                if resposta_config:
                    sucesso = atualizar_emu_cfg(install_path=path, bios_path=path)
                    if sucesso:
                        mb.showinfo("Sucesso", "O caminho personalizado da BIOS foi salvo nas configurações do emulador!", parent=self)
                        self.atualizar_status_diretorio(path)
                    else:
                        mb.showerror("Erro", "Não foi possível salvar a configuração no arquivo emu.cfg.", parent=self)

        def buscar_backups_saves(self):
            cloud_prov = self.cloud_var.get()
            if cloud_prov == "nenhum":
                mb.showwarning("Aviso", "Selecione um provedor de nuvem (Google Drive ou OneDrive) na primeira aba.", parent=self)
                return

            caminho_base = None
            if cloud_prov == "gdrive" and cloud_saves:
                caminho_base = cloud_saves.get_gdrive_path()
            elif cloud_prov == "onedrive" and cloud_saves:
                caminho_base = cloud_saves.get_onedrive_path()

            if not caminho_base or not os.path.exists(caminho_base):
                mb.showerror("Erro", "A pasta principal do provedor não foi encontrada no seu sistema.", parent=self)
                return

            caminho_nuvem = os.path.join(caminho_base, "Flycast_Saves_Backup")
            
            if not os.path.exists(caminho_nuvem):
                self.combo_backups.configure(values=["Nenhum backup encontrado..."])
                self.combo_backups.set("Nenhum backup encontrado...")
                self.btn_restaurar_save.configure(state="disabled")
                mb.showinfo("Busca Concluída", "A pasta 'Flycast_Saves_Backup' ainda não existe na sua nuvem.", parent=self)
                return

            try:
                arquivos_zip = []
                for f in os.listdir(caminho_nuvem):
                    if f.lower().endswith(".zip") and f != "flycast_backup.zip":
                        arquivos_zip.append(f)
                
                if not arquivos_zip:
                    self.combo_backups.configure(values=["Nenhum backup encontrado..."])
                    self.combo_backups.set("Nenhum backup encontrado...")
                    self.btn_restaurar_save.configure(state="disabled")
                    mb.showinfo("Busca Concluída", "Nenhum arquivo de backup (.zip) encontrado na pasta Flycast_Saves_Backup.", parent=self)
                    return

                arquivos_zip.sort(key=lambda x: os.path.getmtime(os.path.join(caminho_nuvem, x)), reverse=True)

                self.arquivos_backup_encontrados = {}
                nomes_exibicao = []
                for f in arquivos_zip:
                    caminho_completo = os.path.join(caminho_nuvem, f)
                    data_mod = datetime.datetime.fromtimestamp(os.path.getmtime(caminho_completo)).strftime('%d/%m/%Y %H:%M')
                    nome_exib = f"{f}  [{data_mod}]"
                    nomes_exibicao.append(nome_exib)
                    self.arquivos_backup_encontrados[nome_exib] = caminho_completo

                self.combo_backups.configure(values=nomes_exibicao)
                self.combo_backups.set(nomes_exibicao[0])
                self.btn_restaurar_save.configure(state="normal")

            except Exception as e:
                mb.showerror("Erro", f"Falha ao buscar backups: {e}", parent=self)

        def restaurar_backup_selecionado(self):
            selecionado = self.combo_backups.get()
            caminho_zip = self.arquivos_backup_encontrados.get(selecionado)

            if not caminho_zip or not os.path.exists(caminho_zip):
                mb.showerror("Erro", "Arquivo de backup inválido ou não selecionado.", parent=self)
                return

            install_path = self.entry_path.get()
            if not install_path or not os.path.exists(install_path):
                mb.showerror("Erro", "Diretório do emulador inválido.", parent=self)
                return
            
            resposta = mb.askyesno("Confirmar Restauração", f"Deseja extrair os arquivos de:\n{selecionado}\n\nEles substituirão os saves atuais no seu emulador. Continuar?", parent=self)
            if not resposta:
                return
                
            try:
                with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                    zip_ref.extractall(install_path)
                mb.showinfo("Sucesso", "Saves restaurados com sucesso para a pasta do emulador!", parent=self)
            except Exception as e:
                mb.showerror("Erro", f"Falha ao extrair o backup: {e}", parent=self)

        def carregar_dados_atuais_emu_cfg(self):
            install_path = self.entry_path.get()
            caminhos = [os.path.join(install_path, "emu.cfg"), os.path.join(install_path, "data", "emu.cfg")]
            for p in caminhos:
                if os.path.exists(p):
                    try:
                        config = configparser.RawConfigParser(strict=False)
                        config.optionxform = str
                        config.read(p, encoding='utf-8')
                        
                        # --- DADOS ABA EMULADOR ---
                        if config.has_section('config'):
                            if config.has_option('config', 'Dreamcast.ContentPath'):
                                self.entry_roms.configure(state="normal")
                                self.entry_roms.delete(0, 'end')
                                self.entry_roms.insert(0, config.get('config', 'Dreamcast.ContentPath').replace("/", "\\"))
                                self.entry_roms.configure(state="readonly")
                                
                            if config.get('config', 'PerGameVmu', fallback='no').lower() == 'yes': self.switch_vmu.select()
                            if config.get('config', 'FetchBoxart', fallback='no').lower() == 'yes': self.switch_boxart.select()
                            if config.get('config', 'Dreamcast.Cable', fallback='3') == '0': self.switch_vga.select()
                            if config.get('config', 'DiscordPresence', fallback='no').lower() == 'yes': self.switch_discord.select()
                            if config.get('config', 'ShowOsdVmu', fallback='no').lower() == 'yes': self.switch_osd_vmu.select()
                            
                        if config.has_section('achievements'):
                            if config.get('achievements', 'Enabled', fallback='no').lower() == 'yes': self.switch_ra.select()
                            if config.get('achievements', 'HardcoreMode', fallback='no').lower() == 'yes': self.switch_hardcore.select()
                            if config.has_option('achievements', 'UserName'):
                                self.entry_ra_user.insert(0, config.get('achievements', 'UserName'))
                            if config.has_option('achievements', 'Token'):
                                token_lido = config.get('achievements', 'Token')
                                self.entry_ra_pass.insert(0, token_lido)
                                self.token_ra_salvo = token_lido 

                        if config.has_section('audio'):
                            if config.get('audio', 'VmuSound', fallback='no').lower() == 'yes': self.switch_vmu_sound.select()
                            
                        if config.has_section('config'):
                            if config.has_option('config', 'pvr.rend'):
                                val = config.get('config', 'pvr.rend')
                                api_rev_map = {"0": "OpenGL", "1": "DirectX 9", "2": "DirectX 11", "4": "Vulkan"}
                                self.api_var.set(api_rev_map.get(val, "DirectX 11"))
                                
                            if config.has_option('config', 'rend.Resolution'):
                                val = config.get('config', 'rend.Resolution')
                                res_map = {
                                    "480": "640x480 (Nativo)", 
                                    "720": "960x720 (1.5x)", 
                                    "960": "1280x960 (2x)", 
                                    "1080": "1440x1080 (3x)", 
                                    "1440": "1920x1440 (4x)", 
                                    "2160": "2880x2160 (6x)"
                                }
                                self.combo_res.set(res_map.get(val, "640x480 (Nativo)"))

                            if config.get('config', 'rend.IntegerScale', fallback='no').lower() == 'yes': self.switch_integer.select()
                            if config.get('config', 'rend.LinearInterpolation', fallback='no').lower() == 'yes': self.switch_linear.select()
                            if config.get('config', 'rend.vsync', fallback='no').lower() == 'yes': self.switch_vsync.select()

                        if config.has_section('window'):
                            if config.get('window', 'fullscreen', fallback='no').lower() == 'yes': self.switch_fullscreen.select()

                        break
                    except Exception:
                        pass

        def escolher_diretorio_roms(self):
            dir_escolhido = ctk.filedialog.askdirectory(title="Selecione a pasta de Jogos (ROMs)")
            if dir_escolhido:
                self.entry_roms.configure(state="normal")
                self.entry_roms.delete(0, 'end')
                self.entry_roms.insert(0, dir_escolhido)
                self.entry_roms.configure(state="readonly")

        def salvar_configuracoes_emulador(self):
            install_path = self.entry_path.get()
            roms_path = self.entry_roms.get()
            ra_on = self.switch_ra.get() == 1
            ra_user = self.entry_ra_user.get().strip()
            ra_pass_input = self.entry_ra_pass.get().strip()
            ra_hard = self.switch_hardcore.get() == 1
            
            qol_vmu = self.switch_vmu.get() == 1
            qol_boxart = self.switch_boxart.get() == 1
            qol_vga = self.switch_vga.get() == 1
            qol_discord = self.switch_discord.get() == 1
            qol_osd_vmu = self.switch_osd_vmu.get() == 1
            qol_vmu_sound = self.switch_vmu_sound.get() == 1

            ra_token_final = ""
            if ra_on and ra_user and ra_pass_input:
                if getattr(self, 'token_ra_salvo', '') == ra_pass_input:
                    ra_token_final = self.token_ra_salvo
                else:
                    self.btn_salvar_config_emu.configure(text="⏳ Autenticando na Nuvem...")
                    self.update() 
                    
                    token_api = obter_token_retroachievements(ra_user, ra_pass_input)
                    if token_api:
                        ra_token_final = token_api
                        self.token_ra_salvo = token_api
                    else:
                        mb.showerror("Falha no Login", "Usuário ou senha do RetroAchievements incorretos.\nVerifique suas credenciais.", parent=self)
                        self.btn_salvar_config_emu.configure(text="💾 Salvar Configurações do Emulador")
                        return 
            else:
                ra_token_final = ra_pass_input

            sucesso = atualizar_emu_cfg(
                install_path=install_path,
                roms_path=roms_path if roms_path else None,
                ra_enabled=ra_on,
                ra_user=ra_user,
                ra_pass=ra_token_final,
                ra_hardcore=ra_hard,
                vmu_individual=qol_vmu,
                fetch_boxart=qol_boxart,
                vga_cable=qol_vga,
                discord_presence=qol_discord,
                show_osd_vmu=qol_osd_vmu,
                vmu_sound=qol_vmu_sound
            )

            self.config_atual["setup_completed"] = True
            salvar_configuracao(
                self.branch_var.get(),
                self.switch_desktop.get() == 1,
                self.switch_startup.get() == 1,
                install_path,
                self.cloud_var.get() if self.cloud_var.get() != "nenhum" else None,
                None,
                setup_completed=True,
                setup_declined=self.config_atual.get("setup_declined", False)
            )

            self.btn_salvar_config_emu.configure(text="💾 Salvar Configurações do Emulador")

            if sucesso:
                mb.showinfo("Sucesso", "Configurações gerais salvas com sucesso!", parent=self)
            else:
                mb.showerror("Erro", "Não foi possível gravar no arquivo emu.cfg. Verifique as permissões da pasta.", parent=self)

        def salvar_configuracoes_video(self):
            install_path = self.entry_path.get()
            
            api = self.api_var.get()
            
            res_str = self.combo_res.get()
            res_val = "480"
            if "720" in res_str: res_val = "720"
            elif "960" in res_str: res_val = "960"
            elif "1080" in res_str: res_val = "1080"
            elif "1440" in res_str: res_val = "1440"
            elif "2160" in res_str: res_val = "2160"

            full = self.switch_fullscreen.get() == 1
            integer = self.switch_integer.get() == 1
            linear = self.switch_linear.get() == 1
            vsync = self.switch_vsync.get() == 1

            sucesso = atualizar_emu_cfg(
                install_path=install_path,
                vid_api=api,
                vid_res=res_val,
                vid_full=full,
                vid_int=integer,
                vid_lin=linear,
                vid_vsync=vsync
            )

            if sucesso:
                mb.showinfo("Sucesso", "Configurações de vídeo salvas com sucesso no emu.cfg!", parent=self)
            else:
                mb.showerror("Erro", "Não foi possível gravar as configurações de vídeo no arquivo emu.cfg.", parent=self)

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
                
            custom_bios_path = None
            caminhos_cfg = [os.path.join(path, "emu.cfg"), os.path.join(path, "data", "emu.cfg")]
            for p in caminhos_cfg:
                if os.path.exists(p):
                    try:
                        config = configparser.RawConfigParser(strict=False)
                        config.optionxform = str
                        config.read(p, encoding='utf-8')
                        if config.has_option('config', 'Dreamcast.BiosPath'):
                            custom_bios_path = config.get('config', 'Dreamcast.BiosPath').strip()
                            if not custom_bios_path:
                                custom_bios_path = None
                        break
                    except:
                        pass

            boot_data = os.path.exists(os.path.join(path, "data", "dc_boot.bin"))
            flash_data = os.path.exists(os.path.join(path, "data", "dc_flash.bin"))
            boot_root = os.path.exists(os.path.join(path, "dc_boot.bin"))
            flash_root = os.path.exists(os.path.join(path, "dc_flash.bin"))
            
            boot_custom = False
            flash_custom = False
            if custom_bios_path:
                if not os.path.isabs(custom_bios_path):
                    custom_bios_path = os.path.join(path, custom_bios_path)
                if os.path.exists(custom_bios_path):
                    boot_custom = os.path.exists(os.path.join(custom_bios_path, "dc_boot.bin"))
                    flash_custom = os.path.exists(os.path.join(custom_bios_path, "dc_flash.bin"))

            if boot_data and flash_data:
                self.lbl_bios.configure(text="BIOS: 🟢 Arquivos OK", text_color="#00FF7F")
            elif custom_bios_path and boot_custom and flash_custom:
                self.lbl_bios.configure(text="BIOS: 🟢 Arquivos OK (Custom Path)", text_color="#00FF7F")
            elif boot_root and flash_root:
                self.lbl_bios.configure(text="BIOS: 🟡 Local incorreto", text_color="#FFD700")
                self.after(500, lambda: self.resolver_bios_mal_posicionada(path))
            else:
                self.lbl_bios.configure(text="BIOS: 🔴 Arquivos Ausentes", text_color="#FF4C4C")

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
                self.tt_rollback.update_text("Restaura o emulador para a versão do último backup.")
            else:
                self.btn_rollback.configure(state="disabled")
                self.tt_rollback.update_text("🔴 Nenhum backup (flycast_backup.zip) encontrado.")

        def escolher_diretorio(self):
            dir_escolhido = ctk.filedialog.askdirectory(initialdir=self.entry_path.get(), title="Selecione a pasta do Flycast")
            if dir_escolhido:
                self.entry_path.configure(state="normal")
                self.entry_path.delete(0, 'end')
                self.entry_path.insert(0, dir_escolhido)
                self.entry_path.configure(state="readonly")
                self.bios_prompt_done = False 
                self.atualizar_status_diretorio(dir_escolhido)

        def abrir_janela_ajuda(self):
            win_ajuda = ctk.CTkToplevel(self)
            win_ajuda.title("Manual do Flycast Updater")
            win_ajuda.geometry("550x550")
            win_ajuda.attributes("-topmost", True)
            
            texto_ajuda = (
                "🌀 MANUAL DO FLYCAST UPDATER\n\n"
                "Este aplicativo mantém o seu emulador Flycast sempre atualizado com as\n"
                "versões mais recentes do GitHub e sincroniza seus jogos na nuvem.\n\n"
                "🖥️ COMO USAR AS VERSÕES:\n"
                "• Branch Master: Versão oficial de lançamento (estável).\n"
                "• Branch Dev: Versão de desenvolvimento (atualizada diariamente).\n\n"
                "💾 CLOUD SAVES & CONFIGURAÇÕES (v3.0):\n"
                "• Escolha o Google Drive ou OneDrive para backup automático.\n"
                "• Na aba 'Configurar Emulador', defina sua pasta de ROMs e ajuste\n"
                "  suas credenciais do RetroAchievements com Modo Hardcore.\n\n"
                "🌴 SOBRE A VERSÃO 3.0 (Emerald Coast Edition):\n"
                "Homenagem à clássica primeira fase de Sonic Adventure! Esta versão\n"
                "torna o utilitário um gerenciador completo do ecossistema Flycast.\n\n"
                "🖧 USO PELO TERMINAL (PowerShell/CMD):\n"
                "Parâmetros: -nogui, -dev, -master, -rollback, -silent, -reset"
            )
            
            lbl_texto = ctk.CTkLabel(win_ajuda, text=texto_ajuda, justify="left", font=ctk.CTkFont(size=12))
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

            self.progressbar.pack(pady=(2, 0))
            self.label_status.pack(pady=(2, 5))
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

                salvar_configuracao(branch_escolhida, criar_desktop, criar_startup, install_path, cloud_prov, cloud_path, 
                                    setup_completed=self.config_atual.get("setup_completed", False),
                                    setup_declined=self.config_atual.get("setup_declined", False))

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
                
                # Fechamento automático garantido após o sucesso da tarefa principal
                self.after(2000, self.destroy)
            except SystemExit:
                self.after(2000, self.destroy)
            except Exception as e:
                self.after(0, self.label_status.configure, {"text": f"Erro crítico: {e}", "text_color": "red"})
            finally:
                sys.stdout = terminal_original
                self.after(0, self.btn_atualizar.configure, {"state": "normal"})
                self.after(0, self.atualizar_status_diretorio, self.entry_path.get())

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
                print("[-] Aviso: Google Drive não encontrado no seu PC.")
        elif c == '2':
            path = cloud_saves.get_onedrive_path()
            if path and os.path.exists(path):
                cloud_prov, cloud_path = 'onedrive', path
            else:
                print("[-] Aviso: OneDrive não encontrado no seu PC.")

    install_path = os.getcwd()
    salvar_configuracao(branch_choice, create_desktop, create_startup, install_path, cloud_prov, cloud_path, setup_completed=True)
    print("\n[+] Preferências salvas com sucesso!\n")
    
    return {
        "branch": branch_choice,
        "create_shortcut": create_desktop,
        "create_startup": create_startup,
        "install_path": install_path,
        "cloud_provider": cloud_prov,
        "cloud_path": cloud_path,
        "setup_completed": True
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
        print("  -nogui        Executa em modo texto")
        print("  -dev          Força a versão de desenvolvimento")
        print("  -master       Força a versão estável")
        print("  -rollback     Restaura o último backup funcional")
        print("  -silent       Executa em segundo plano")
        print("  -backup       Apenas realiza o backup na nuvem")
        print("  -reset        Refaz a configuração inicial")
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