import os, sys, json, subprocess, time, urllib.request, urllib.parse, datetime, threading, configparser, zipfile, shutil, re
import tkinter as tk 
import tkinter.messagebox as mb
import webbrowser
import bigpicture 
import radio_flycast
from idiomas import TRANSLATIONS
from game_launcher import GameLibraryManager

try: import cloud_saves
except ImportError: cloud_saves = None

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError: HAS_PIL = False

try:
    import pygame
    HAS_PYGAME = True
except ImportError: HAS_PYGAME = False

# ==========================================
# Flycast Updater - Launcher v6.0 (Big Blue)
# Desenvolvido por DaniboySan & Geminix
# ==========================================

VERSION = "6.0"
CONFIG_FILE = "config.json"
REPO_UPDATER = "dsantanna/flycast_updater"

PERFIS_CONTROLES = {
    "Xbox (360 / One / Series)": {"arquivo": "XInput Controller.cfg", "conteudo": "[emulator]\nmapping_name = XInput Controller\n\n[dreamcast]\nbtn_a = 0\nbtn_b = 1\nbtn_x = 2\nbtn_y = 3\nbtn_start = 7\nbtn_dpad1_up = 11\nbtn_dpad1_down = 12\nbtn_dpad1_left = 13\nbtn_dpad1_right = 14\naxis_x = 0\naxis_y = 1\naxis_trigger_left = 4\naxis_trigger_right = 5\n"},
    "PlayStation (PS4 / PS5)": {"arquivo": "PS4 Controller.cfg", "conteudo": "[emulator]\nmapping_name = PS4 Controller\n\n[dreamcast]\nbtn_a = 1\nbtn_b = 2\nbtn_x = 0\nbtn_y = 3\nbtn_start = 9\nbtn_dpad1_up = 11\nbtn_dpad1_down = 12\nbtn_dpad1_left = 13\nbtn_dpad1_right = 14\naxis_x = 0\naxis_y = 1\naxis_trigger_left = 4\naxis_trigger_right = 5\n"},
    "8BitDo (Pro 2 / Ultimate / SN30)": {"arquivo": "8BitDo Controller.cfg", "conteudo": "[emulator]\nmapping_name = 8BitDo Controller\n\n[dreamcast]\nbtn_a = 1\nbtn_b = 0\nbtn_x = 3\nbtn_y = 2\nbtn_start = 11\nbtn_dpad1_up = 15\nbtn_dpad1_down = 16\nbtn_dpad1_left = 17\nbtn_dpad1_right = 18\naxis_x = 0\naxis_y = 1\naxis_trigger_left = 4\naxis_trigger_right = 5\n"}
}

THEMES = {
    "Padrão DARK": {"primary": "#4169E1", "hover": "#1E90FF", "text": "white"},
    "Sonic The Hedgehog": {"primary": "#0055FF", "hover": "#0033AA", "text": "white"},
    "Crazy Taxi": {"primary": "#FFAC1C", "hover": "#CC8A16", "text": "black"},
    "Shenmue": {"primary": "#5D9B9B", "hover": "#4A7C7C", "text": "white"},
    "Marvel vs Capcom 2": {"primary": "#FF007F", "hover": "#CC0066", "text": "white"}
}

def carregar_configuracao():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: pass
    return {}

def salvar_configuracao(dados):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception: pass

def obter_token_retroachievements(usuario, senha):
    url = f"https://retroachievements.org/dorequest.php?r=login&u={urllib.parse.quote(usuario)}&p={urllib.parse.quote(senha)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
        with urllib.request.urlopen(req, timeout=5) as response:
            resposta = json.loads(response.read().decode('utf-8'))
            if resposta.get("Success"): return resposta.get("Token")
    except Exception: pass
    return None

def obter_gpus_windows():
    if os.name != 'nt': return []
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion | ConvertTo-Json"'
        result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)
        if result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, dict): data = [data]
            return [{"nome": g.get("Name", "Desconhecida"), "driver": g.get("DriverVersion", "Desconhecido")} for g in data if g.get("Name")]
    except Exception: pass
    return []

def obter_monitores_windows():
    if os.name != 'nt': return [{"nome": "Monitor Padrão", "left": 0, "top": 0}]
    import ctypes
    monitores = []
    try:
        user32 = ctypes.windll.user32
        class RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
        def _callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            r = lprcMonitor.contents
            idx = len(monitores) + 1
            nome = f"Monitor {idx} ({r.right - r.left}x{r.bottom - r.top})"
            if r.left == 0 and r.top == 0: nome += " [Principal]"
            monitores.append({"nome": nome, "left": r.left, "top": r.top})
            return 1
        MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(RECT), ctypes.c_void_p)
        user32.EnumDisplayMonitors(0, None, MonitorEnumProc(_callback), 0)
    except Exception:
        monitores.append({"nome": "Monitor Padrão", "left": 0, "top": 0})
    return monitores

def atualizar_emu_cfg(install_path, roms_path=None, ra_enabled=None, ra_user=None, ra_pass=None, ra_hardcore=None, 
                      vmu_individual=None, fetch_boxart=None, vga_cable=None, discord_presence=None,
                      show_osd_vmu=None, vmu_sound=None, bios_path=None, vmu_path=None, state_path=None, save_path=None,
                      vid_api=None, vid_res=None, vid_full=None, vid_int=None, vid_lin=None, vid_vsync=None,
                      streamer_mode=None, cheat_enable=None, window_left=None, window_top=None, widescreen_hack=None, use_hle=None):
    caminhos_possiveis = [os.path.join(install_path, "emu.cfg"), os.path.join(install_path, "data", "emu.cfg")]
    cfg_path = next((p for p in caminhos_possiveis if os.path.exists(p)), os.path.join(install_path, "emu.cfg"))

    config = configparser.RawConfigParser(strict=False)
    config.optionxform = str 
    if os.path.exists(cfg_path):
        try: config.read(cfg_path, encoding='utf-8')
        except Exception: return False

    for section in ['achievements', 'config', 'audio', 'window']:
        if not config.has_section(section): config.add_section(section)

    if ra_enabled is not None: config.set('achievements', 'Enabled', 'yes' if ra_enabled else 'no')
    if ra_hardcore is not None: config.set('achievements', 'HardcoreMode', 'yes' if ra_hardcore else 'no')
    if ra_user is not None: config.set('achievements', 'UserName', ra_user)
    if ra_pass is not None: config.set('achievements', 'Token', ra_pass)

    if roms_path is not None: 
        if isinstance(roms_path, list):
            caminhos_formatados = ";".join([p.replace("/", "\\") for p in roms_path])
            config.set('config', 'Dreamcast.ContentPath', caminhos_formatados)
        else:
            config.set('config', 'Dreamcast.ContentPath', roms_path.replace("/", "\\"))

    if vmu_individual is not None: config.set('config', 'PerGameVmu', 'yes' if vmu_individual else 'no')
    if fetch_boxart is not None:
        config.set('config', 'FetchBoxart', 'yes' if fetch_boxart else 'no')
        config.set('config', 'BoxartDisplayMode', 'yes' if fetch_boxart else 'no')
    if vga_cable is not None: config.set('config', 'Dreamcast.Cable', '0' if vga_cable else '3') 
    if discord_presence is not None: config.set('config', 'DiscordPresence', 'yes' if discord_presence else 'no')
    if show_osd_vmu is not None: 
        config.set('config', 'ShowOsdVmu', 'yes' if show_osd_vmu else 'no')
        config.set('config', 'rend.FloatVMUs', 'yes' if show_osd_vmu else 'no')
    if streamer_mode is not None: config.set('config', 'OsdMessages', 'no' if streamer_mode else 'yes')
    if cheat_enable is not None: config.set('config', 'Cheat', 'yes' if cheat_enable else 'no')
    if use_hle is not None: config.set('config', 'UseReios', 'yes' if use_hle else 'no')

    def _set_or_remove(sec, k, val):
        if val: config.set(sec, k, val.replace("/", "\\"))
        elif config.has_option(sec, k): config.remove_option(sec, k)

    if bios_path is not None: 
        if bios_path: os.makedirs(bios_path, exist_ok=True)
        _set_or_remove('config', 'Dreamcast.BiosPath', bios_path)
    if vmu_path is not None: 
        if vmu_path: os.makedirs(vmu_path, exist_ok=True)
        _set_or_remove('config', 'Dreamcast.VmuPath', vmu_path)
    if state_path is not None: 
        if state_path: os.makedirs(state_path, exist_ok=True)
        _set_or_remove('config', 'Dreamcast.SavestatePath', state_path)
    if save_path is not None: 
        if save_path: os.makedirs(save_path, exist_ok=True)
        _set_or_remove('config', 'Dreamcast.SavePath', save_path)

    if vid_api is not None:
        api_map = {"OpenGL": "0", "DirectX 9": "1", "DirectX 11": "2", "Vulkan": "4"}
        config.set('config', 'pvr.rend', api_map.get(vid_api, "4"))
    if vid_res is not None: config.set('config', 'rend.Resolution', vid_res)
    if vid_int is not None: config.set('config', 'rend.IntegerScale', 'yes' if vid_int else 'no')
    if vid_lin is not None: config.set('config', 'rend.LinearInterpolation', 'yes' if vid_lin else 'no')
    if vid_vsync is not None: config.set('config', 'rend.vsync', 'yes' if vid_vsync else 'no')
    if vid_full is not None: config.set('window', 'fullscreen', 'yes' if vid_full else 'no')
    if vmu_sound is not None: config.set('audio', 'VmuSound', 'yes' if vmu_sound else 'no')
    if widescreen_hack is not None: config.set('config', 'WidescreenGameHacks', 'yes' if widescreen_hack else 'no')

    if window_left is not None: config.set('window', 'left', str(window_left))
    if window_top is not None: config.set('window', 'top', str(window_top))

    try:
        os.makedirs(os.path.dirname(os.path.abspath(cfg_path)), exist_ok=True)
        with open(cfg_path, 'w', encoding='utf-8') as f: config.write(f, space_around_delimiters=True)
        return True
    except Exception: return False

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
        if self.tooltip_window or not self.text: return
        try:
            if self.widget.cget("state") == "disabled" and "Rollback" not in self.text and "não detectado" not in self.text: return 
        except Exception: pass
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        label = tk.Label(tw, text=self.text, justify='left', background="#2b2b2b", foreground="#ffffff", relief='solid', borderwidth=1, font=("Segoe UI", 9, "normal"), padx=8, pady=4)
        label.pack(ipadx=1)
        
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class ConsoleRedirector:
    def __init__(self, app): self.app = app
    def write(self, message):
        texto = message.strip()
        if not texto: return
        self.app.log(f"[MOTOR] {texto}", bypass_console=True)
        if "[*] Progresso:" in texto:
            try:
                pct_str = texto.split("%")[0].split(" ")[-1]
                tamanhos = texto.split("(")[1].replace(")", "")
                self.app.after(0, self.app.progressbar.set, float(pct_str) / 100.0)
                self.app.after(0, self.app.label_status.configure, {"text": f"🦔 Velocidade Sônica! Baixando... {pct_str}% ({tamanhos})", "text_color": "cyan"})
            except Exception: pass
        elif "[!]" in texto or "Aviso de BIOS" in texto: self.app.after(0, self.app.label_status.configure, {"text": f"⚠️ {texto}", "text_color": "#FF8C00"})
        elif "Backup" in texto or "Sincronizando" in texto or "[✓]" in texto or "Rollback" in texto or "[+]" in texto: self.app.after(0, self.app.label_status.configure, {"text": f"💾 {texto}", "text_color": "#00FF7F"})
        elif "Erro" in texto or "[-]" in texto: self.app.after(0, self.app.label_status.configure, {"text": f"❌ {texto}", "text_color": "#FF4C4C"})
        else: self.app.after(0, self.app.label_status.configure, {"text": texto, "text_color": "cyan"})
    def flush(self): pass

def iniciar_gui():
    import customtkinter as ctk
    from customtkinter import filedialog
    
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("blue") 

    class FlycastUpdaterApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.config_atual = carregar_configuracao()
            self.lang = self.config_atual.get("language", "pt")

            if HAS_PYGAME:
                try: pygame.mixer.init()
                except Exception: pass
                self.bgm_playing = False

            self.title(f"🌀 Flycast Updater - v{VERSION} (Big Blue)")
            self.geometry("800x980") 
            self.minsize(800, 600)
            self.resizable(True, True) 

            def forcar_maximizacao():
                try: self.state('zoomed')
                except Exception: self.attributes('-zoomed', True)
            self.after(100, forcar_maximizacao)
            self.after(1200, self.iniciar_radio)
            
            self.token_ra_salvo = "" 
            self.bios_prompt_done = False
            self.fabricante_gpu = None
            self.rom_paths_list = []

            self.frame_header = ctk.CTkFrame(self, fg_color="transparent")
            self.frame_header.pack(fill="x", padx=20, pady=(15, 0))
            self.label_titulo = ctk.CTkLabel(self.frame_header, text="Flycast Updater", font=ctk.CTkFont(size=24, weight="bold"))
            self.label_titulo.pack(side="top")
            self.label_sub = ctk.CTkLabel(self.frame_header, text=self._("title_sub"), text_color="gray")
            self.label_sub.pack(side="top", pady=(0, 10))

            self.frame_top_right = ctk.CTkFrame(self.frame_header, fg_color="transparent")
            self.frame_top_right.place(relx=1.0, rely=0.0, anchor="ne")
            self.lang_map = {
                "Português (BR)": "pt", "English (US)": "en", "Español (ES)": "es", "Français (FR)": "fr","Deutsch (DE)": "de","Italiano (IT)": "it", "日本語 (JA)": "ja", "简体中文 (ZH)": "zh", "Русский (RU)": "ru", "العربية (AR)": "ar"
            }
            self.rev_lang_map = {v: k for k, v in self.lang_map.items()}

            self.btn_bigpicture_top = ctk.CTkButton(
                self.frame_top_right, 
                text="📺 Big Picture", 
                width=100, 
                height=28, 
                fg_color="#FF4500", 
                hover_color="#FF6347", 
                font=ctk.CTkFont(weight="bold"),
                command=self.abrir_big_picture
            )
            self.btn_bigpicture_top.pack(side="left", padx=5)
            self.btn_bigpicture_top._tooltip = ToolTip(self.btn_bigpicture_top, "Abrir Interface de TV em Tela Cheia")

            self.combo_lang = ctk.CTkComboBox(self.frame_top_right, values=list(self.lang_map.keys()), width=95, height=28, command=self.mudar_idioma)
            self.combo_lang.pack(side="left", padx=5)
            self.combo_lang.set(self.rev_lang_map.get(self.lang, "PT-BR"))
            self.btn_help = ctk.CTkButton(self.frame_top_right, text=self._("btn_help"), width=70, height=28, fg_color="#444", hover_color="#666", command=self.abrir_janela_ajuda)
            self.btn_help.pack(side="left")

            self.tabview = ctk.CTkTabview(self, width=620, height=680)
            self.tabview.pack(pady=5, padx=15, fill="both", expand=True)
            self.tab_jogos = self.tabview.add(self._("tab_games", default="🕹️ Launcher")) 
            self.tab_atualizador = self.tabview.add(self._("tab_cloud", default="🚀 BIOS e Emu"))
            self.tab_config = self.tabview.add(self._("tab_emu", default="⚙️ Configurações"))
            self.tab_qol = self.tabview.add(self._("tab_qol", default="🌟 QoL"))
            self.tab_video = self.tabview.add(self._("tab_vid", default="🖥️ Vídeo"))
            self.tab_devices = self.tabview.add("🎮 Controles e VMU") # <-- NOME NOVO AQUI
            self.tab_saves = self.tabview.add(self._("tab_saves", default="🔄 Saves"))
            self.tab_logs = self.tabview.add(self._("tab_logs", default="📝 Logs"))
            
            # --- CONEXÃO COM O MOTOR MODULAR ---
            self.game_manager = GameLibraryManager(self)
            
            import saves
            self.save_manager = saves.SaveManager(self)
            
            import qol
            self.qol_manager = qol.QoLManager(self)
            
            import devices
            self.devices_manager = devices.DevicesManager(self)
            
            import discord_rpc
            self.discord = discord_rpc.DiscordManager(self)
            self.after(3000, self.discord.conectar) 
            
            self.construir_aba_nuvem()
            self.construir_aba_jogos()   
            self.construir_aba_emulador()
            self.construir_aba_qol()
            self.construir_aba_video()
            self.construir_aba_dispositivos()
            self.construir_aba_saves()
            self.construir_aba_logs()

            caminho_inicial = os.path.normpath(self.config_atual.get("install_path", os.getcwd()))
            self.entry_path.configure(state="normal")
            self.entry_path.delete(0, 'end')
            self.entry_path.insert(0, caminho_inicial)
            self.entry_path.configure(state="readonly")

            self.progressbar = ctk.CTkProgressBar(self, width=580)
            self.progressbar.set(0)
            self.label_status = ctk.CTkLabel(self, text="...", text_color="cyan")
            self.lbl_emulador_status = ctk.CTkLabel(self, text=self._("emu_status_checking", default="Verificando..."), font=ctk.CTkFont(size=14, weight="bold"))
            self.lbl_emulador_status.pack(pady=(2, 5))

            self.frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
            self.frame_botoes.pack(pady=(0, 10))
            self.btn_atualizar = ctk.CTkButton(self.frame_botoes, text=self._("btn_verify", default="VERIFICANDO..."), width=220, height=38, font=ctk.CTkFont(weight="bold"), command=lambda: self.preparar_motor("atualizar"))
            self.btn_atualizar.grid(row=0, column=0, padx=10)
            self.btn_rollback = ctk.CTkButton(self.frame_botoes, text=self._("btn_rollback", default="REVERTER"), width=180, height=38, fg_color="#8B0000", hover_color="#A52A2A", font=ctk.CTkFont(weight="bold"), command=lambda: self.preparar_motor("rollback"))
            self.btn_rollback.grid(row=0, column=1, padx=10)

            self.frame_player = ctk.CTkFrame(self.frame_botoes, fg_color="#1a1a1a", corner_radius=8)
            self.frame_player.grid(row=0, column=2, padx=(20, 0), sticky="e")
            
            self.lbl_now_playing = ctk.CTkLabel(self.frame_player, text="🎵 Rádio Parada", font=ctk.CTkFont(size=11), width=160, anchor="center")
            self.lbl_now_playing.pack(side="top", padx=10, pady=(2, 0))

            self.frame_player_controls = ctk.CTkFrame(self.frame_player, fg_color="transparent")
            self.frame_player_controls.pack(side="top", pady=(0, 2))

            self.btn_radio_prev = ctk.CTkButton(self.frame_player_controls, text="⏮", width=30, height=20, fg_color="transparent", hover_color="#333", command=self.radio_prev)
            self.btn_radio_prev.pack(side="left", padx=2)

            self.btn_radio_play = ctk.CTkButton(self.frame_player_controls, text="▶", width=30, height=20, fg_color="transparent", hover_color="#333", command=self.radio_play_pause)
            self.btn_radio_play.pack(side="left", padx=2)

            self.btn_radio_stop = ctk.CTkButton(self.frame_player_controls, text="⏹", width=30, height=20, fg_color="transparent", hover_color="#333", command=self.radio_stop)
            self.btn_radio_stop.pack(side="left", padx=2)

            self.btn_radio_next = ctk.CTkButton(self.frame_player_controls, text="⏭", width=30, height=20, fg_color="transparent", hover_color="#333", command=self.radio_next)
            self.btn_radio_next.pack(side="left", padx=2)

            # --- FRAME DO SEMÁFORO DE BACKUP ---
            self.frame_backup_status = ctk.CTkFrame(self.frame_botoes, fg_color="#1a1a1a", corner_radius=8)
            self.frame_backup_status.grid(row=0, column=3, padx=(20, 0), sticky="e")
            
            self.lbl_backup_status = ctk.CTkLabel(self.frame_backup_status, text="☁️ Backup: 🔴", font=ctk.CTkFont(size=11, weight="bold"))
            self.lbl_backup_status.pack(side="top", padx=10, pady=(2, 0))
            
            self.lbl_backup_date = ctk.CTkLabel(self.frame_backup_status, text="--/--/---- - --:--", font=ctk.CTkFont(size=10), text_color="gray")
            self.lbl_backup_date.pack(side="bottom", padx=10, pady=(0, 2))
            
            self.lbl_rodape = ctk.CTkLabel(self, text="Desenvolvido por DaniboySan & Geminix", text_color="#1E90FF", cursor="hand2", font=ctk.CTkFont(size=11, underline=True))
            self.lbl_rodape.pack(side="bottom", pady=(0, 5))
            self.lbl_rodape.bind("<Button-1>", lambda e: webbrowser.open(f"https://github.com/{REPO_UPDATER}"))

            self.carregar_dados_atuais_emu_cfg()

            self.log(f"🚀 Flycast Updater v{VERSION} iniciado.")
            self.atualizar_status_diretorio(self.entry_path.get())
            self.after(200, self.verificar_primeiro_acesso)
            self.after(800, self.carregar_gpus) 
            self.after(1000, self.game_manager.escanear_jogos) 
            self.after(1100, self.aplicar_tema)

            import sfx_manager
            self.sfx = sfx_manager.SFXManager(self.entry_path.get())
            self.after(1500, lambda: self.sfx.apply_hover_to_all_widgets(self))
            self.after(1600, self.checar_status_backup)

        def iniciar_radio(self):
            if not HAS_PYGAME: return
            if self.config_atual.get("radio_on", False):
                if not hasattr(self, 'radio'):
                    self.radio = radio_flycast.RadioFlycast()
                self.radio.carregar_playlist(self.entry_path.get())
                self.radio.play()
                self.bgm_playing = True
                self.log("📻 Rádio Ambiente (Modulada) iniciada.")
                self.atualizar_interface_radio()

        def checar_status_backup(self):
            self.log("🔍 Auto-Diagnóstico: Inspecionando o cofre de saves na nuvem...")
            cloud_prov = self.config_atual.get("cloud_provider", "nenhum")
            
            # Regra 1: Nuvem Desligada
            if not cloud_prov or cloud_prov == "nenhum":
                self.lbl_backup_status.configure(text="☁️ Backup: 🔴 Desativado", text_color="#FF4C4C")
                self.lbl_backup_date.configure(text="Nenhuma nuvem selecionada")
                self.log("⚠️ Defesa Aberta: A nuvem está desativada. Seus saves estão vulneráveis!")
                return

            caminho_base = None
            if cloud_prov == "gdrive" and cloud_saves: caminho_base = cloud_saves.get_gdrive_path()
            elif cloud_prov == "onedrive" and cloud_saves: caminho_base = cloud_saves.get_onedrive_path()

            # Regra 2: Erro de Diretório
            if not caminho_base or not os.path.exists(caminho_base):
                self.lbl_backup_status.configure(text="☁️ Backup: 🔴 Erro", text_color="#FF4C4C")
                self.lbl_backup_date.configure(text="Pasta da nuvem inalcançável")
                self.log(f"❌ Falha de Conexão: A pasta do provedor '{cloud_prov}' não foi localizada no sistema.")
                return

            caminho_nuvem = os.path.join(caminho_base, "Flycast_Saves_Backup")
            
            # Regra 3: Cofre Vazio
            if not os.path.exists(caminho_nuvem):
                self.lbl_backup_status.configure(text="☁️ Backup: 🔴 Vazio", text_color="#FF4C4C")
                self.lbl_backup_date.configure(text="Nenhum arquivo encontrado")
                self.log("⚠️ Alerta: A pasta na nuvem existe, mas o cofre de backups está completamente vazio.")
                return

            try:
                arquivos_zip = [f for f in os.listdir(caminho_nuvem) if f.lower().endswith(".zip") and f != "flycast_backup.zip"]
                if not arquivos_zip:
                    self.lbl_backup_status.configure(text="☁️ Backup: 🔴 Vazio", text_color="#FF4C4C")
                    self.lbl_backup_date.configure(text="Nenhum backup realizado")
                    self.log("⚠️ Alerta: Nenhum arquivo .zip de save foi encontrado no cofre.")
                    return

                # Localiza o arquivo mais recente pela data de modificação do Windows
                caminho_completo = max([os.path.join(caminho_nuvem, f) for f in arquivos_zip], key=os.path.getmtime)
                mtime = os.path.getmtime(caminho_completo)
                data_formatada = datetime.datetime.fromtimestamp(mtime).strftime('%d/%m/%Y-%H:%M')
                
                # O Juiz apita a regra do tempo:
                agora = time.time()
                idade_segundos = agora - mtime
                horas_idade = idade_segundos / 3600

                if horas_idade <= 24: 
                    # Sinal Verde: Backup com menos de 24 horas
                    self.lbl_backup_status.configure(text="☁️ Backup: 🟢 Em dia", text_color="#00FF7F")
                    self.log(f"✅ Zaga Sólida! Último backup validado na nuvem. Idade: {int(horas_idade)} hora(s).")
                else: 
                    # Sinal Amarelo: Backup com mais de 24 horas
                    self.lbl_backup_status.configure(text="☁️ Backup: 🟡 Antigo", text_color="#FFD700")
                    self.log(f"⚠️ Atenção: Seu último backup tem {int(horas_idade // 24)} dias de idade. Jogue uma partida para ativar o Auto-Sync!")

                self.lbl_backup_date.configure(text=data_formatada)

            except Exception as e:
                self.log(f"❌ Erro ao ler status da nuvem: {e}")

        def toggle_radio(self):
            if self.switch_radio.get() == 1:
                install_path = self.entry_path.get()
                media_dir = os.path.join(install_path, "media")
                
                if not os.path.exists(media_dir):
                    try:
                        os.makedirs(media_dir, exist_ok=True)
                        self.mostrar_toast("Rádio Ambiente", "A pasta 'media' foi criada! Copie suas músicas para lá.", "success")
                    except Exception: pass
                
                self.config_atual["radio_on"] = True
                if not hasattr(self, 'radio'):
                    self.radio = radio_flycast.RadioFlycast()
                self.iniciar_radio()
            else:
                self.config_atual["radio_on"] = False
                self.radio_stop()
            self.salvar_estado_atual()

        def radio_play_pause(self):
            if not HAS_PYGAME: return
            
            if self.switch_radio.get() == 0:
                self.switch_radio.select()
                self.toggle_radio()
                return

            if getattr(self, 'bgm_playing', False):
                if not getattr(self, 'is_paused', False):
                    if hasattr(self, 'radio'): self.radio.pause()
                    self.is_paused = True
                    if hasattr(self, 'btn_radio_play'): self.btn_radio_play.configure(text="▶")
                    if hasattr(self, 'lbl_now_playing'): self.lbl_now_playing.configure(text="🎵 Rádio Pausada")
                    self.log("📻 Rádio: Pausada.")
                else:
                    if hasattr(self, 'radio'): self.radio.play()
                    self.is_paused = False
                    if hasattr(self, 'btn_radio_play'): self.btn_radio_play.configure(text="⏸")
                    self.atualizar_interface_radio()
                    self.log("📻 Rádio: Retomada.")
            else:
                if not hasattr(self, 'radio'):
                    self.radio = radio_flycast.RadioFlycast()
                    self.radio.carregar_playlist(self.entry_path.get())
                self.radio.play()
                self.bgm_playing = True
                self.is_paused = False
                if hasattr(self, 'btn_radio_play'): self.btn_radio_play.configure(text="⏸")
                self.atualizar_interface_radio()

        def radio_stop(self):
            if not HAS_PYGAME: return
            try:
                if hasattr(self, 'radio'): self.radio.stop()
                self.bgm_playing = False
                self.is_paused = False
                
                if self.switch_radio.get() == 1:
                    self.switch_radio.deselect()
                    self.config_atual["radio_on"] = False
                    self.salvar_estado_atual()
                    
                if hasattr(self, 'btn_radio_play'): self.btn_radio_play.configure(text="▶")
                if hasattr(self, 'lbl_now_playing'): self.lbl_now_playing.configure(text="🎵 Rádio Parada")
                self.log("📻 Rádio: Parada.")
            except: pass

        def radio_next(self):
            if hasattr(self, 'radio'):
                self.radio.next_track()
                self.atualizar_interface_radio()
                self.log("📻 Rádio: Próxima faixa.")

        def radio_prev(self):
            if hasattr(self, 'radio'):
                self.radio.prev_track()
                self.atualizar_interface_radio()
                self.log("📻 Rádio: Faixa anterior.")

        def atualizar_interface_radio(self):
            if hasattr(self, 'radio') and hasattr(self, 'lbl_now_playing'):
                titulo = self.radio.obter_titulo_atual()
                nome_curto = titulo[:22] + "..." if len(titulo) > 22 else titulo
                self.lbl_now_playing.configure(text=f"🎵 {nome_curto}")
                if hasattr(self.lbl_now_playing, '_tooltip'): self.lbl_now_playing._tooltip.update_text(titulo)
                else: self.lbl_now_playing._tooltip = ToolTip(self.lbl_now_playing, titulo)

        def abrir_pasta_media(self):
            install_path = self.entry_path.get()
            if not install_path: return
            media_dir = os.path.join(install_path, "media")
            os.makedirs(media_dir, exist_ok=True)
            try:
                os.startfile(media_dir)
                self.log("📁 Explorador de Arquivos aberto na pasta 'media'.")
            except Exception as e:
                self.log(f"❌ Erro ao abrir pasta media: {e}")

        def abrir_pasta_sfx(self):
            install_path = self.entry_path.get()
            if not install_path: return
            sfx_dir = os.path.join(install_path, "media", "sfx")
            os.makedirs(sfx_dir, exist_ok=True)
            try:
                os.startfile(sfx_dir)
                self.log("📁 Explorador aberto na pasta de efeitos sonoros (media/sfx). Personalize seus arquivos .wav aqui!")
            except Exception as e:
                self.log(f"❌ Erro ao abrir pasta sfx: {e}")

        def log(self, mensagem, bypass_console=False):
            try:
                path = self.entry_path.get()
                if path and os.path.exists(path):
                    log_file = os.path.join(path, "flycast_updater.log")
                    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    prefixo = "" if bypass_console else "[LAUNCHER] "
                    with open(log_file, "a", encoding="utf-8") as f: f.write(f"[{agora}] {prefixo}{mensagem}\n")
                    if hasattr(self, 'textbox_logs') and self.textbox_logs.winfo_exists():
                        self.textbox_logs.configure(state="normal")
                        self.textbox_logs.insert(tk.END, f"[{agora}] {prefixo}{mensagem}\n")
                        self.textbox_logs.see(tk.END)
                        self.textbox_logs.configure(state="disabled")
            except Exception: pass

        def mostrar_toast(self, titulo, mensagem, tipo="info", duracao=3000):
            """Chama a notificação flutuante e atrela o SFX adequado."""
            try:
                import toast
                toast.ToastNotification(self, titulo, mensagem, tipo, duracao)
                
                if hasattr(self, 'sfx'):
                    if tipo == "success": self.sfx.play("success")
                    elif tipo in ["error", "warning"]: self.sfx.play("error")
            except Exception as e:
                self.log(f"⚠️ Erro ao exibir Toast: {e}")

        def _(self, key, **kwargs):
            default_text = kwargs.pop("default", key)
            fallback = TRANSLATIONS.get("pt", {}).get(key, default_text)
            texto = TRANSLATIONS.get(self.lang, TRANSLATIONS["pt"]).get(key, fallback)
            if kwargs:
                try: return texto.format(**kwargs)
                except Exception: pass
            return texto

        def mudar_idioma(self, escolha):
            novo_lang = self.lang_map.get(escolha, "pt")
            if novo_lang != self.lang:
                self.log(f"🌐 Idioma alterado: {escolha}")
                self.lang = novo_lang
                self.config_atual["language"] = novo_lang
                self.salvar_estado_atual()
                self.atualizar_textos_ui()

        def atualizar_textos_ui(self):
            self.label_sub.configure(text=self._("title_sub"))
            self.btn_help.configure(text=self._("btn_help"))
            self.label_path.configure(text=self._("lbl_path"))
            self.btn_path.configure(text=self._("btn_browse"))
            self.label_branch.configure(text=self._("lbl_branch"))
            self.lbl_dev_desc.configure(text=self._("rb_dev_desc"))
            self.lbl_master_desc.configure(text=self._("rb_master_desc"))
            self.switch_startup.configure(text=self._("sw_start"))
            self.label_games_title.configure(text=self._("lbl_games_title"))
            self.label_games_desc.configure(text=self._("lbl_games_desc"))
            self.switch_cheats.configure(text=self._("sw_cheats"))
            if hasattr(self, 'btn_scan_games'): self.btn_scan_games.configure(text=self._("btn_scan_games"))
            self.label_roms_title.configure(text=self._("lbl_roms"))
            self.btn_add_rom.configure(text=self._("btn_add_path"))
            self.switch_custom_paths.configure(text=self._("sw_custom_paths"))
            self.lbl_bios_path.configure(text=self._("lbl_bios_path"))
            self.btn_bios_path.configure(text=self._("btn_browse"))
            self.lbl_vmu_path.configure(text=self._("lbl_vmu_path"))
            self.btn_vmu_path.configure(text=self._("btn_browse"))
            self.lbl_state_path.configure(text=self._("lbl_state_path"))
            self.btn_state_path.configure(text=self._("btn_browse"))
            self.lbl_save_path.configure(text=self._("lbl_save_path"))
            self.btn_save_path.configure(text=self._("btn_browse"))
            self.label_ra_title.configure(text=self._("lbl_ra"))
            self.switch_ra.configure(text=self._("sw_ra"))
            self.lbl_ra_user.configure(text=self._("lbl_user"))
            self.lbl_ra_pass.configure(text=self._("lbl_pass"))
            self.lbl_ra_api.configure(text=self._("lbl_ra_api"))
            self.switch_hardcore.configure(text=self._("sw_hard"))
            self.lbl_hc_desc.configure(text=self._("lbl_hc_desc"))
            self.btn_salvar_config_emu.configure(text=self._("btn_save_emu"))
            self.label_qol_title.configure(text=self._("lbl_qol"))
            self.switch_vmu.configure(text=self._("sw_vmu"))
            self.switch_boxart.configure(text=self._("sw_box"))
            self.switch_vga.configure(text=self._("sw_vga"))
            self.switch_discord.configure(text=self._("sw_disc"))
            self.switch_osd_vmu.configure(text=self._("sw_osd"))
            self.switch_vmu_sound.configure(text=self._("sw_vmu_snd"))
            self.switch_streamer.configure(text=self._("sw_streamer"))
            if hasattr(self, 'btn_salvar_config_qol'): self.btn_salvar_config_qol.configure(text=self._("btn_save_emu"))
            self.label_video_title.configure(text=self._("lbl_vid_title"))
            self.label_video_aviso.configure(text=self._("lbl_vid_warn"))
            self.lbl_api.configure(text=self._("lbl_api"))
            self.lbl_res.configure(text=self._("lbl_res"))
            self.switch_fullscreen.configure(text=self._("sw_full"))
            self.switch_integer.configure(text=self._("sw_int"))
            self.switch_linear.configure(text=self._("sw_lin"))
            self.switch_vsync.configure(text=self._("sw_vsync"))
            self.btn_salvar_video.configure(text=self._("btn_save_vid"))
            self.label_hw_title.configure(text=self._("lbl_hw_title"))
            self.btn_driver.configure(text=self._("btn_driver"))
            self.label_ctrl_title.configure(text=self._("lbl_ctrl_title"))
            self.label_ctrl_desc.configure(text=self._("lbl_ctrl_desc"))
            self.btn_injetar_ctrl.configure(text=self._("btn_inject"))
            self.label_cloud.configure(text=self._("lbl_cloud"))
            self.switch_mappings.configure(text=self._("sw_map"))
            self.lbl_limit.configure(text=self._("lbl_backup_limit"))
            self.label_saves_title.configure(text=self._("lbl_saves_title"))
            self.label_saves_desc.configure(text=self._("lbl_saves_desc"))
            self.btn_buscar_saves.configure(text=self._("btn_search_saves"))
            self.btn_restaurar_save.configure(text=self._("btn_extract"))
            self.label_logs_title.configure(text=self._("lbl_logs_title"))
            self.btn_refresh_log.configure(text=self._("btn_log_refresh"))
            self.btn_copy_log.configure(text=self._("btn_log_copy"))
            self.btn_clear_log.configure(text=self._("btn_log_clear"))

        def construir_aba_nuvem(self):
            self.frame_path_title = ctk.CTkFrame(self.tab_atualizador, fg_color="transparent")
            self.frame_path_title.pack(fill="x", padx=10, pady=(10, 2))
            self.label_path = ctk.CTkLabel(self.frame_path_title, text=self._("lbl_path"), font=ctk.CTkFont(weight="bold"))
            self.label_path.pack(side="left")
            self.lbl_bios = ctk.CTkLabel(self.frame_path_title, text="BIOS: ...", font=ctk.CTkFont(size=12, weight="bold"))
            self.lbl_bios.pack(side="right")

            self.frame_path = ctk.CTkFrame(self.tab_atualizador, fg_color="transparent")
            self.frame_path.pack(fill="x", padx=10, pady=(0, 10))
            self.frame_path.columnconfigure(0, weight=1) 

            self.entry_path = ctk.CTkEntry(self.frame_path)
            self.entry_path.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            self.entry_path.configure(state="readonly") 

            self.btn_path = ctk.CTkButton(self.frame_path, text=self._("btn_browse"), width=80, command=self.escolher_diretorio)
            self.btn_path.grid(row=0, column=1)

            self.label_branch = ctk.CTkLabel(self.tab_atualizador, text=self._("lbl_branch"), font=ctk.CTkFont(weight="bold"))
            self.label_branch.pack(anchor="w", padx=10, pady=(5, 2))

            self.branch_var = ctk.StringVar(value=self.config_atual.get("branch", "dev").lower())
            self.frame_branches = ctk.CTkFrame(self.tab_atualizador, fg_color="transparent")
            self.frame_branches.pack(fill="x", padx=10, pady=(0, 10))

            self.rb_dev = ctk.CTkRadioButton(self.frame_branches, text="Branch Dev", font=ctk.CTkFont(weight="bold"), variable=self.branch_var, value="dev", command=self.ao_trocar_branch)
            self.rb_dev.grid(row=0, column=0, sticky="w", padx=(0, 50))
            self.lbl_dev_desc = ctk.CTkLabel(self.frame_branches, text=self._("rb_dev_desc"), text_color="gray", font=ctk.CTkFont(size=11), justify="left")
            self.lbl_dev_desc.grid(row=1, column=0, sticky="nw", padx=(28, 50))

            self.rb_master = ctk.CTkRadioButton(self.frame_branches, text="Branch Master", font=ctk.CTkFont(weight="bold"), variable=self.branch_var, value="master", command=self.ao_trocar_branch)
            self.rb_master.grid(row=0, column=1, sticky="w", padx=(0, 10))
            self.lbl_master_desc = ctk.CTkLabel(self.frame_branches, text=self._("rb_master_desc"), text_color="gray", font=ctk.CTkFont(size=11), justify="left")
            self.lbl_master_desc.grid(row=1, column=1, sticky="nw", padx=(28, 0)) 

            self.btn_desktop_shortcut = ctk.CTkButton(self.tab_atualizador, text="🖥️ Criar Atalho no Desktop", width=220, height=28, command=self.abrir_janela_atalho)
            self.btn_desktop_shortcut.pack(anchor="w", padx=10, pady=(15, 5))

            # Auto-save injetado no Switch!
            self.switch_startup = ctk.CTkSwitch(self.tab_atualizador, text=self._("sw_start"), command=self.salvar_estado_atual)
            self.switch_startup.pack(anchor="w", padx=10, pady=5)
            if self.config_atual.get("create_startup", False): self.switch_startup.select()
            # --- DREAMCAST ---
            self.lbl_dc_title = ctk.CTkLabel(self.tab_atualizador, text="🕹️ Dreamcast", font=ctk.CTkFont(size=14, weight="bold"))
            self.lbl_dc_title.pack(anchor="w", padx=10, pady=(15, 2))

            self.switch_hle = ctk.CTkSwitch(self.tab_atualizador, text="Ativar BIOS HLE", command=self.ao_trocar_hle)
            self.switch_hle.pack(anchor="w", padx=20, pady=(5, 2))
            
            texto_hle = (
                "💡 High-Level Emulation (HLE)\n"
                "Simula o sistema nativo do console em software, ignorando o uso da BIOS original\n"
                "(dc_boot.bin). Alguns jogos independentes e homebrews recentes (como o clássico\n"
                "RPG Pier Solar) SÓ funcionam se esta opção estiver ATIVADA."
            )
            self.lbl_hle_desc = ctk.CTkLabel(self.tab_atualizador, text=texto_hle, text_color="gray", font=ctk.CTkFont(size=11), justify="left")
            self.lbl_hle_desc.pack(anchor="w", padx=55, pady=(0, 15))

            # --- OUTROS SISTEMAS (ARCADE) ---
            self.frame_divisor_arcade = ctk.CTkFrame(self.tab_atualizador, height=2, fg_color="#444")
            self.frame_divisor_arcade.pack(fill="x", padx=10, pady=(5, 10))

            self.lbl_arcade_title = ctk.CTkLabel(self.tab_atualizador, text="👾 Outros Sistemas (Arcade)", font=ctk.CTkFont(size=14, weight="bold"))
            self.lbl_arcade_title.pack(anchor="w", padx=10, pady=(5, 10))

            self.frame_arcade_switches = ctk.CTkFrame(self.tab_atualizador, fg_color="transparent")
            self.frame_arcade_switches.pack(fill="x", padx=20)

            self.switch_naomi = ctk.CTkSwitch(self.frame_arcade_switches, text="BIOS Naomi", command=lambda: self.toggle_bios_arcade("Naomi", "naomi.zip", self.switch_naomi))
            self.switch_naomi.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=5)

            self.switch_naomi2 = ctk.CTkSwitch(self.frame_arcade_switches, text="BIOS Naomi 2", command=lambda: self.toggle_bios_arcade("Naomi 2", "naomi2.zip", self.switch_naomi2))
            self.switch_naomi2.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=5)

            self.switch_atomiswave = ctk.CTkSwitch(self.frame_arcade_switches, text="BIOS Atomiswave", command=lambda: self.toggle_bios_arcade("Atomiswave", "awbios.zip", self.switch_atomiswave))
            self.switch_atomiswave.grid(row=0, column=2, sticky="w", pady=5)
            # --------------------------------------------------

        def abrir_janela_atalho(self):
            win_atalho = ctk.CTkToplevel(self)
            win_atalho.title("Atalho no Desktop")
            win_atalho.geometry("450x380")
            win_atalho.attributes("-topmost", True)
            win_atalho.grab_set()

            lbl_title = ctk.CTkLabel(win_atalho, text="Configurações do Atalho", font=ctk.CTkFont(size=16, weight="bold"))
            lbl_title.pack(pady=(15, 10))

            var_nogui = ctk.BooleanVar(value=self.config_atual.get("nogui", False))
            chk_nogui = ctk.CTkCheckBox(win_atalho, text="Desabilitar Gráficos (-nogui) ao abrir", variable=var_nogui)
            chk_nogui.pack(anchor="w", padx=20, pady=5)

            lbl_nome = ctk.CTkLabel(win_atalho, text="Nome do Atalho:", font=ctk.CTkFont(weight="bold"))
            lbl_nome.pack(anchor="w", padx=20, pady=(15, 5))

            var_nome = ctk.StringVar(value="Flycast")
            frame_nomes = ctk.CTkFrame(win_atalho, fg_color="transparent")
            frame_nomes.pack(fill="x", padx=20)

            def update_entry_state():
                if var_nome.get() == "Outro":
                    entry_custom_nome.configure(state="normal")
                    entry_custom_nome.focus()
                else:
                    entry_custom_nome.configure(state="disabled")

            rb_flycast = ctk.CTkRadioButton(frame_nomes, text="Flycast", variable=var_nome, value="Flycast", command=update_entry_state)
            rb_flycast.grid(row=0, column=0, sticky="w", pady=5)
            
            branch_atual = self.branch_var.get().capitalize()
            rb_branch = ctk.CTkRadioButton(frame_nomes, text=f"Flycast-{branch_atual}", variable=var_nome, value=f"Flycast-{branch_atual}", command=update_entry_state)
            rb_branch.grid(row=0, column=1, sticky="w", pady=5, padx=15)

            rb_dreamcast = ctk.CTkRadioButton(frame_nomes, text="Dreamcast", variable=var_nome, value="Dreamcast", command=update_entry_state)
            rb_dreamcast.grid(row=1, column=0, sticky="w", pady=5)

            rb_outro = ctk.CTkRadioButton(frame_nomes, text="Outro", variable=var_nome, value="Outro", command=update_entry_state)
            rb_outro.grid(row=1, column=1, sticky="w", pady=5, padx=15)

            entry_custom_nome = ctk.CTkEntry(win_atalho, placeholder_text="Digite o nome customizado...", state="disabled")
            entry_custom_nome.pack(fill="x", padx=20, pady=(10, 15))

            def confirmar_criacao():
                nome_escolhido = var_nome.get()
                if nome_escolhido == "Outro":
                    nome_final = entry_custom_nome.get().strip()
                    if not nome_final:
                        mb.showerror("Erro", "Digite um nome para o atalho.", parent=win_atalho)
                        return
                else:
                    nome_final = nome_escolhido

                usar_nogui = var_nogui.get()
                self.config_atual["nogui"] = usar_nogui
                self.salvar_estado_atual()

                self.criar_atalho_desktop_customizado(nome_final, usar_nogui)
                mb.showinfo("Sucesso", f"Atalho '{nome_final}' criado com sucesso na sua Área de Trabalho!", parent=win_atalho)
                win_atalho.destroy()

            btn_criar = ctk.CTkButton(win_atalho, text="✔️ Criar Atalho Agora", font=ctk.CTkFont(weight="bold"), height=35, command=confirmar_criacao)
            btn_criar.pack(pady=(10, 20))

        def criar_atalho_desktop_customizado(self, nome_atalho, usar_nogui):
            try:
                exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
                trabalho_dir = os.path.dirname(exe_path)
                args = " -nogui" if usar_nogui else ""
                
                ps_script = f'''
                $WshShell = New-Object -ComObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut("$([Environment]::GetFolderPath('Desktop'))\\{nome_atalho}.lnk")
                $Shortcut.TargetPath = "{exe_path}"
                $Shortcut.Arguments = "{args}"
                $Shortcut.WorkingDirectory = "{trabalho_dir}"
                $Shortcut.Description = "Flycast Updater - Big Blue"
                $Shortcut.Save()
                '''
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.run(['powershell', '-NoProfile', '-Command', ps_script], startupinfo=startupinfo, capture_output=True)
                self.log(f"🖥️ Atalho '{nome_atalho}' criado na Área de Trabalho (nogui={usar_nogui}).")
            except Exception as e:
                self.log(f"❌ Erro ao criar atalho na Área de Trabalho: {e}")

        def definir_entry_custom(self, entry_widget, texto):
            entry_widget.configure(state="normal")
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, texto)
            entry_widget.configure(state="readonly")

        def escolher_dir_custom_path(self, entry_widget):
            dir_escolhido = ctk.filedialog.askdirectory()
            if dir_escolhido:
                self.definir_entry_custom(entry_widget, os.path.normpath(dir_escolhido))

        def toggle_custom_paths(self):
            if self.switch_custom_paths.get() == 1: self.frame_custom_paths.pack(fill="x", padx=10, pady=(5, 5))
            else: self.frame_custom_paths.pack_forget()
            self.salvar_estado_atual() # Salva a escolha silenciosamente

        def abrir_big_picture(self):
            # Salva a referência da janela para podermos minimizá-la depois!
            self.janela_bp = bigpicture.ModoBigPicture(self, self.game_manager)

        def construir_aba_jogos(self):
            self.label_games_title = ctk.CTkLabel(self.tab_jogos, text=self._("lbl_games_title"), font=ctk.CTkFont(size=16, weight="bold"))
            self.label_games_title.pack(anchor="w", padx=10, pady=(10, 2))
            self.label_games_desc = ctk.CTkLabel(self.tab_jogos, text=self._("lbl_games_desc"), text_color="gray", justify="left")
            self.label_games_desc.pack(anchor="w", padx=10, pady=(0, 5))

            self.frame_dashboard = ctk.CTkFrame(self.tab_jogos, fg_color="#1a1a1a", corner_radius=10)
            self.frame_dashboard.pack(fill="x", padx=10, pady=(0, 5))
            self.frame_dashboard.columnconfigure(0, weight=1)
            self.frame_dashboard.columnconfigure(1, weight=1)

            self.lbl_dash_tempo = ctk.CTkLabel(self.frame_dashboard, text="⏱️ Tempo Total: 0h 0m", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1E90FF")
            self.lbl_dash_tempo.grid(row=0, column=0, pady=10, padx=10, sticky="w")

            self.lbl_dash_ra = ctk.CTkLabel(self.frame_dashboard, text="🏆 Total RA: 0 pts", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00FF7F")
            self.lbl_dash_ra.grid(row=0, column=1, pady=10, padx=10, sticky="e")

            self.frame_games_top = ctk.CTkFrame(self.tab_jogos, fg_color="transparent")
            self.frame_games_top.pack(fill="x", padx=10, pady=0)

            self.switch_cheats = ctk.CTkSwitch(self.frame_games_top, text=self._("sw_cheats"), command=self.qol_manager.ao_trocar_cheats)
            self.switch_cheats.pack(side="left")

            self.btn_filter_fav = ctk.CTkButton(self.frame_games_top, text="⭐", width=30, fg_color="transparent", border_width=1, text_color="gray", command=self.game_manager.toggle_filtro_favoritos)
            self.btn_filter_fav.pack(side="left", padx=(15, 0))

            self.btn_roleta = ctk.CTkButton(self.frame_games_top, text="🎲", width=30, fg_color="transparent", border_width=1, text_color="#FFAC1C", hover_color="#CC8A16", command=self.game_manager.sortear_jogo)
            self.btn_roleta.pack(side="left", padx=(10, 0))
            self.btn_roleta._tooltip = ToolTip(self.btn_roleta, "Estou com Sorte (Roleta)")

            # --- BOTÃO DOS ATALHOS STEAM ---
            self.btn_steam = ctk.CTkButton(self.frame_games_top, text="☁️ Steam", width=60, fg_color="transparent", border_width=1, text_color="#1E90FF", hover_color="#4169E1", command=self.game_manager.exportar_para_steam)
            self.btn_steam.pack(side="left", padx=(10, 0))
            self.btn_steam._tooltip = ToolTip(self.btn_steam, "Exportar Jogos para a Biblioteca Steam")

            # --- BOTÃO DOS ATALHOS DESKTOP ---
            self.btn_desktop = ctk.CTkButton(self.frame_games_top, text="🖥️ Desktop", width=70, fg_color="transparent", border_width=1, text_color="#00FF7F", hover_color="#2E8B57", command=self.game_manager.exportar_para_desktop)
            self.btn_desktop.pack(side="left", padx=(10, 0))
            self.btn_desktop._tooltip = ToolTip(self.btn_desktop, "Criar atalhos na Área de Trabalho")

            self.btn_scan_games = ctk.CTkButton(self.frame_games_top, text=self._("btn_scan_games"), width=120, command=self.game_manager.escanear_jogos)
            self.btn_scan_games.pack(side="right", padx=(10, 0))

            self.entry_busca_jogos = ctk.CTkEntry(self.frame_games_top, placeholder_text="🔍 Buscar jogo...", width=160)
            self.entry_busca_jogos.pack(side="right")
            self.entry_busca_jogos.bind("<KeyRelease>", lambda e: self.game_manager.escanear_jogos())

            self.frame_grid_games = ctk.CTkScrollableFrame(self.tab_jogos, width=580, height=330, corner_radius=10)
            self.frame_grid_games.pack(fill="both", expand=True, padx=10, pady=(5, 5))

        def atualizar_lista_ui_roms(self):
            for widget in self.frame_roms_list.winfo_children(): widget.destroy()
            for p in self.rom_paths_list:
                f = ctk.CTkFrame(self.frame_roms_list, fg_color="transparent")
                f.pack(fill="x", pady=2)
                lbl = ctk.CTkLabel(f, text=p, anchor="w", font=ctk.CTkFont(size=11))
                lbl.pack(side="left", fill="x", expand=True)
                ToolTip(lbl, p)
                btn = ctk.CTkButton(f, text="X", width=25, height=20, fg_color="#8B0000", hover_color="#A52A2A", command=lambda path=p: self.remover_diretorio_roms(path))
                btn.pack(side="right")

        def adicionar_diretorio_roms(self):
            dir_escolhido = ctk.filedialog.askdirectory()
            if dir_escolhido:
                dir_escolhido = os.path.normpath(dir_escolhido)
                if dir_escolhido not in self.rom_paths_list:
                    self.rom_paths_list.append(dir_escolhido)
                    self.atualizar_lista_ui_roms()
                    self.log(f"📁 Pasta adicionada: {dir_escolhido}")
                    self.game_manager.escanear_jogos()

        def remover_diretorio_roms(self, path):
            if path in self.rom_paths_list:
                self.rom_paths_list.remove(path)
                self.atualizar_lista_ui_roms()
                self.log(f"🗑️ Pasta removida: {path}")
                self.game_manager.escanear_jogos()

        def construir_aba_emulador(self):
            self.label_roms_title = ctk.CTkLabel(self.tab_config, text=self._("lbl_roms"), font=ctk.CTkFont(weight="bold"))
            self.label_roms_title.pack(anchor="w", padx=10, pady=(5, 2))

            self.frame_roms_list = ctk.CTkScrollableFrame(self.tab_config, height=70, fg_color="#1a1a1a")
            self.frame_roms_list.pack(fill="x", padx=10, pady=(0, 5))
            
            self.btn_add_rom = ctk.CTkButton(self.tab_config, text=self._("btn_add_path"), width=150, fg_color="#228B22", hover_color="#006400", command=self.adicionar_diretorio_roms)
            self.btn_add_rom.pack(anchor="w", padx=10, pady=(0, 10))

            # Auto-save injetado!
            self.switch_custom_paths = ctk.CTkSwitch(self.tab_config, text=self._("sw_custom_paths"), command=self.toggle_custom_paths)
            self.switch_custom_paths.pack(anchor="w", padx=10, pady=(5, 5))

            self.container_custom_paths = ctk.CTkFrame(self.tab_config, fg_color="transparent", height=0)
            self.container_custom_paths.pack(fill="x", padx=0, pady=0)

            self.frame_custom_paths = ctk.CTkFrame(self.container_custom_paths, fg_color="#2b2b2b", corner_radius=6)
            self.frame_custom_paths.columnconfigure(1, weight=1)

            self.lbl_bios_path = ctk.CTkLabel(self.frame_custom_paths, text=self._("lbl_bios_path"))
            self.lbl_bios_path.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=(5, 2))
            self.entry_bios_path = ctk.CTkEntry(self.frame_custom_paths, state="readonly", height=24)
            self.entry_bios_path.grid(row=0, column=1, sticky="ew", padx=5, pady=(5, 2))
            self.btn_bios_path = ctk.CTkButton(self.frame_custom_paths, text=self._("btn_browse"), width=50, height=24, command=lambda: self.escolher_dir_custom_path(self.entry_bios_path))
            self.btn_bios_path.grid(row=0, column=2, padx=(5, 10), pady=(5, 2))

            self.lbl_vmu_path = ctk.CTkLabel(self.frame_custom_paths, text=self._("lbl_vmu_path"))
            self.lbl_vmu_path.grid(row=1, column=0, sticky="w", padx=(10, 5), pady=2)
            self.entry_vmu_path = ctk.CTkEntry(self.frame_custom_paths, state="readonly", height=24)
            self.entry_vmu_path.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
            self.btn_vmu_path = ctk.CTkButton(self.frame_custom_paths, text=self._("btn_browse"), width=50, height=24, command=lambda: self.escolher_dir_custom_path(self.entry_vmu_path))
            self.btn_vmu_path.grid(row=1, column=2, padx=(5, 10), pady=2)

            self.lbl_state_path = ctk.CTkLabel(self.frame_custom_paths, text=self._("lbl_state_path"))
            self.lbl_state_path.grid(row=2, column=0, sticky="w", padx=(10, 5), pady=2)
            self.entry_state_path = ctk.CTkEntry(self.frame_custom_paths, state="readonly", height=24)
            self.entry_state_path.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
            self.btn_state_path = ctk.CTkButton(self.frame_custom_paths, text=self._("btn_browse"), width=50, height=24, command=lambda: self.escolher_dir_custom_path(self.entry_state_path))
            self.btn_state_path.grid(row=2, column=2, padx=(5, 10), pady=2)

            self.lbl_save_path = ctk.CTkLabel(self.frame_custom_paths, text=self._("lbl_save_path"))
            self.lbl_save_path.grid(row=3, column=0, sticky="w", padx=(10, 5), pady=2)
            self.entry_save_path = ctk.CTkEntry(self.frame_custom_paths, state="readonly", height=24)
            self.entry_save_path.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
            self.btn_save_path = ctk.CTkButton(self.frame_custom_paths, text=self._("btn_browse"), width=50, height=24, command=lambda: self.escolher_dir_custom_path(self.entry_save_path))
            self.btn_save_path.grid(row=3, column=2, padx=(5, 10), pady=2)

            self.lbl_manual_path = ctk.CTkLabel(self.frame_custom_paths, text="Manuais")
            self.lbl_manual_path.grid(row=4, column=0, sticky="w", padx=(10, 5), pady=2)
            self.entry_manual_path = ctk.CTkEntry(self.frame_custom_paths, state="readonly", height=24)
            self.entry_manual_path.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
            self.btn_manual_path = ctk.CTkButton(self.frame_custom_paths, text=self._("btn_browse"), width=50, height=24, command=lambda: self.escolher_dir_custom_path(self.entry_manual_path))
            self.btn_manual_path.grid(row=4, column=2, padx=(5, 10), pady=2)

            self.lbl_cheat_path = ctk.CTkLabel(self.frame_custom_paths, text="Trapaças (Cheats)")
            self.lbl_cheat_path.grid(row=5, column=0, sticky="w", padx=(10, 5), pady=(2, 10))
            self.entry_cheat_path = ctk.CTkEntry(self.frame_custom_paths, state="readonly", height=24)
            self.entry_cheat_path.grid(row=5, column=1, sticky="ew", padx=5, pady=(2, 10))
            self.btn_cheat_path = ctk.CTkButton(self.frame_custom_paths, text=self._("btn_browse"), width=50, height=24, command=lambda: self.escolher_dir_custom_path(self.entry_cheat_path))
            self.btn_cheat_path.grid(row=5, column=2, padx=(5, 10), pady=(2, 10))

            self.frame_divisor = ctk.CTkFrame(self.tab_config, height=2, fg_color="#444")
            self.frame_divisor.pack(fill="x", padx=10, pady=(5, 5))

            self.label_ra_title = ctk.CTkLabel(self.tab_config, text=self._("lbl_ra"), font=ctk.CTkFont(weight="bold"))
            self.label_ra_title.pack(anchor="w", padx=10, pady=(5, 2))

            # Auto-save injetado nos Switches RA!
            self.switch_ra = ctk.CTkSwitch(self.tab_config, text=self._("sw_ra"), command=lambda: self.salvar_configuracoes_emulador(silencioso=True))
            self.switch_ra.pack(anchor="w", padx=10, pady=5)

            self.frame_ra_cred = ctk.CTkFrame(self.tab_config, fg_color="transparent")
            self.frame_ra_cred.pack(fill="x", padx=10, pady=2)
            self.frame_ra_cred.columnconfigure(1, weight=1)

            self.lbl_ra_user = ctk.CTkLabel(self.frame_ra_cred, text=self._("lbl_user"))
            self.lbl_ra_user.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=2)
            self.entry_ra_user = ctk.CTkEntry(self.frame_ra_cred, height=26)
            self.entry_ra_user.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)

            self.lbl_ra_pass = ctk.CTkLabel(self.frame_ra_cred, text=self._("lbl_pass"))
            self.lbl_ra_pass.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=2)
            
            self.entry_ra_pass = ctk.CTkEntry(self.frame_ra_cred, show="*", height=26)
            self.entry_ra_pass.grid(row=1, column=1, sticky="ew", pady=2)

            self.lbl_ra_api = ctk.CTkLabel(self.frame_ra_cred, text=self._("lbl_ra_api"))
            self.lbl_ra_api.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=2)
            self.entry_ra_api = ctk.CTkEntry(self.frame_ra_cred, show="*", height=26)
            self.entry_ra_api.grid(row=2, column=1, sticky="ew", pady=2)
            self.btn_ajuda_api = ctk.CTkButton(self.frame_ra_cred, text="?", width=30, height=26, fg_color="#4169E1", hover_color="#1E90FF", command=self.abrir_ajuda_api_key)
            self.btn_ajuda_api.grid(row=2, column=2, padx=(5, 0), pady=2)
            
            self.btn_toggle_senha = ctk.CTkButton(self.frame_ra_cred, text="👁", width=30, height=26, fg_color="transparent", border_width=1, text_color="gray", hover_color="#444", command=self.toggle_senha_visibility)
            self.btn_toggle_senha.grid(row=1, column=2, padx=(5, 0), pady=2)

            # Auto-save injetado!
            self.switch_hardcore = ctk.CTkSwitch(self.tab_config, text=self._("sw_hard"), command=lambda: self.salvar_configuracoes_emulador(silencioso=True))
            self.switch_hardcore.pack(anchor="w", padx=10, pady=(5, 2))
            
            self.lbl_hc_desc = ctk.CTkLabel(self.tab_config, text=self._("lbl_hc_desc"), text_color="gray", font=ctk.CTkFont(size=11), justify="left")
            self.lbl_hc_desc.pack(anchor="w", padx=45, pady=(0, 5))

            self.frame_divisor2 = ctk.CTkFrame(self.tab_config, height=2, fg_color="#444")
            self.frame_divisor2.pack(fill="x", padx=10, pady=(5, 5))

            # Este botão continua aqui porque a aba de RA tem digitação de Senha e User
            self.btn_salvar_config_emu = ctk.CTkButton(self.tab_config, text=self._("btn_save_emu"), width=280, height=35, font=ctk.CTkFont(weight="bold"), command=lambda: self.salvar_configuracoes_emulador(silencioso=False))
            self.btn_salvar_config_emu.pack(anchor="center", pady=(10, 10))

        def construir_aba_qol(self):
            self.label_qol_title = ctk.CTkLabel(self.tab_qol, text=self._("lbl_qol"), font=ctk.CTkFont(size=16, weight="bold"))
            self.label_qol_title.pack(anchor="w", padx=10, pady=(15, 5))

            self.lbl_tema = ctk.CTkLabel(self.tab_qol, text="🎨 Tema Visual:", font=ctk.CTkFont(weight="bold"))
            self.lbl_tema.pack(anchor="w", padx=10, pady=(5, 0))

            self.combo_tema = ctk.CTkComboBox(self.tab_qol, values=list(THEMES.keys()), state="readonly", command=self.aplicar_tema)
            self.combo_tema.pack(anchor="w", padx=10, pady=(0, 10))
            self.combo_tema.set(self.config_atual.get("tema", "Padrão DARK"))

            self.frame_qol = ctk.CTkFrame(self.tab_qol, fg_color="transparent")
            self.frame_qol.pack(fill="x", padx=10)
            self.frame_qol.columnconfigure(0, weight=1)
            self.frame_qol.columnconfigure(1, weight=1)

            # --- SWITCHES REMANESCENTES DE QOL ---
            self.switch_boxart = ctk.CTkSwitch(self.frame_qol, text=self._("sw_box"), command=lambda: self.salvar_configuracoes_emulador(silencioso=True))
            self.switch_boxart.grid(row=0, column=0, sticky="w", pady=10)
            self.switch_vga = ctk.CTkSwitch(self.frame_qol, text=self._("sw_vga"), command=lambda: self.salvar_configuracoes_emulador(silencioso=True))
            self.switch_vga.grid(row=0, column=1, sticky="w", pady=10)
            self.switch_discord = ctk.CTkSwitch(self.frame_qol, text=self._("sw_disc"), command=lambda: self.salvar_configuracoes_emulador(silencioso=True))
            self.switch_discord.grid(row=1, column=0, sticky="w", pady=10)

            # --- O NOVO QUADRO DE ÁUDIO E SFX (ZONA AZUL) ---
            self.frame_audio_qol = ctk.CTkFrame(self.frame_qol, fg_color="transparent")
            self.frame_audio_qol.grid(row=2, column=0, columnspan=2, sticky="w", pady=10)

            self.switch_radio = ctk.CTkSwitch(self.frame_audio_qol, text="🎵 Rádio Ambiente (BGM)", command=self.toggle_radio)
            self.switch_radio.grid(row=0, column=0, sticky="w", pady=5)

            self.btn_open_media = ctk.CTkButton(self.frame_audio_qol, text="📁", width=28, height=24, fg_color="#555555", hover_color="#777777", command=self.abrir_pasta_media)
            self.btn_open_media.grid(row=0, column=1, padx=(10, 0), pady=5)
            self.btn_open_media._tooltip = ToolTip(self.btn_open_media, "Abrir pasta de Músicas")

            if self.config_atual.get("radio_on", False): self.switch_radio.select()

            # Muta os efeitos
            self.switch_sfx = ctk.CTkSwitch(self.frame_audio_qol, text="🔇 Desativar Efeitos de Som (SFX) do Updater", command=self.salvar_estado_atual)
            self.switch_sfx.grid(row=1, column=0, columnspan=2, sticky="w", pady=10)
            if self.config_atual.get("disable_sfx", False): self.switch_sfx.select()

            # Personaliza os efeitos
            self.btn_custom_sfx = ctk.CTkButton(self.frame_audio_qol, text="🎧 Personalizar Efeitos Sonoros", height=28, font=ctk.CTkFont(weight="bold"), fg_color="#8B008B", hover_color="#A52A2A", command=self.abrir_pasta_sfx)
            self.btn_custom_sfx.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 10))

            # --- MODO STREAMER ---
            self.frame_divisor3 = ctk.CTkFrame(self.tab_qol, height=2, fg_color="#444")
            self.frame_divisor3.pack(fill="x", padx=10, pady=(15, 10))

            self.switch_streamer = ctk.CTkSwitch(self.tab_qol, text=self._("sw_streamer"), command=self.qol_manager.ao_trocar_streamer)
            self.switch_streamer.pack(anchor="w", padx=10, pady=5)
            texto_streamer = (
                "🎥 Sua Live no Nível Profissional!\n"
                "🛡️ Anti-Leak: Blinda a interface escondendo caminhos de pastas e usuário (Zero vazamentos!).\n"
                "📺 Tela Limpa: Desativa OSDs e bipes do VMU no emulador para uma gameplay puramente cinemática.\n"
                "🟢 Arsenal OBS: Gera dados em tempo real (Jogo, Tempo, Pontos RA) na pasta 'StreamData' e\n"
                "invoca o incrível Widget Chroma Key verde direto para a sua transmissão!"
            )
            self.lbl_streamer_desc = ctk.CTkLabel(self.tab_qol, text=texto_streamer, text_color="gray", font=ctk.CTkFont(size=12), justify="left")
            self.lbl_streamer_desc.pack(anchor="w", padx=45, pady=(0, 10))
            
            if self.config_atual.get("streamer_mode", False):
                self.switch_streamer.select()
                self.after(200, self.qol_manager.ao_trocar_streamer)

        def construir_aba_video(self):
            self.label_video_title = ctk.CTkLabel(self.tab_video, text=self._("lbl_vid_title"), font=ctk.CTkFont(size=16, weight="bold"))
            self.label_video_title.pack(anchor="w", padx=10, pady=(15, 5))

            self.label_video_aviso = ctk.CTkLabel(self.tab_video, text=self._("lbl_vid_warn"), text_color="#FFD700", justify="left")
            self.label_video_aviso.pack(anchor="w", padx=10, pady=(0, 15))

            self.frame_video_options = ctk.CTkFrame(self.tab_video, fg_color="transparent")
            self.frame_video_options.pack(fill="x", padx=10)

            self.api_var = ctk.StringVar(value="DirectX 11")

            self.lbl_api = ctk.CTkLabel(self.frame_video_options, text=self._("lbl_api"), font=ctk.CTkFont(weight="bold"))
            self.lbl_api.grid(row=0, column=0, sticky="w", pady=(5, 0), padx=(0, 10))

            self.frame_api_rb = ctk.CTkFrame(self.frame_video_options, fg_color="transparent")
            self.frame_api_rb.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 15))

            # --- MÁGICA: Auto-Save em todos os Widgets de Vídeo ---
            self.rb_opengl = ctk.CTkRadioButton(self.frame_api_rb, text="OpenGL", variable=self.api_var, value="OpenGL", command=self.salvar_configuracoes_video)
            self.rb_opengl.pack(side="left", padx=(0, 15))
            self.rb_vulkan = ctk.CTkRadioButton(self.frame_api_rb, text="Vulkan", variable=self.api_var, value="Vulkan", command=self.salvar_configuracoes_video)
            self.rb_vulkan.pack(side="left", padx=(0, 15))
            self.rb_dx9 = ctk.CTkRadioButton(self.frame_api_rb, text="DirectX 9", variable=self.api_var, value="DirectX 9", command=self.salvar_configuracoes_video)
            self.rb_dx9.pack(side="left", padx=(0, 15))
            self.rb_dx11 = ctk.CTkRadioButton(self.frame_api_rb, text="DirectX 11", variable=self.api_var, value="DirectX 11", command=self.salvar_configuracoes_video)
            self.rb_dx11.pack(side="left", padx=(0, 15))

            self.lbl_res = ctk.CTkLabel(self.frame_video_options, text=self._("lbl_res"))
            self.lbl_res.grid(row=2, column=0, sticky="w", pady=5, padx=(0, 10))
            self.combo_res = ctk.CTkComboBox(self.frame_video_options, values=[
                "640x480 (Nativo)", "960x720 (1.5x)", "1280x960 (2x)", 
                "1440x1080 (3x)", "1920x1440 (4x)", "2880x2160 (6x)"
            ], state="readonly", width=180, command=self.salvar_configuracoes_video)
            self.combo_res.grid(row=2, column=1, sticky="w", pady=5)
            self.combo_res.set("640x480 (Nativo)")

            self.lista_monitores = obter_monitores_windows()
            nomes_monitores = [m["nome"] for m in self.lista_monitores]
            
            self.lbl_monitor = ctk.CTkLabel(self.frame_video_options, text="📺 Iniciar no:")
            self.lbl_monitor.grid(row=3, column=0, sticky="w", pady=5, padx=(0, 10))
            self.combo_monitor = ctk.CTkComboBox(self.frame_video_options, values=nomes_monitores, state="readonly", width=180, command=self.salvar_configuracoes_video)
            self.combo_monitor.grid(row=3, column=1, sticky="w", pady=5)
            if nomes_monitores: self.combo_monitor.set(nomes_monitores[0])

            self.switch_fullscreen = ctk.CTkSwitch(self.frame_video_options, text=self._("sw_full"), command=self.salvar_configuracoes_video)
            self.switch_fullscreen.grid(row=4, column=0, columnspan=2, sticky="w", pady=(15, 5))
            self.switch_integer = ctk.CTkSwitch(self.frame_video_options, text=self._("sw_int"), command=self.salvar_configuracoes_video)
            self.switch_integer.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
            self.switch_linear = ctk.CTkSwitch(self.frame_video_options, text=self._("sw_lin"), command=self.salvar_configuracoes_video)
            self.switch_linear.grid(row=6, column=0, columnspan=2, sticky="w", pady=5)
            self.switch_vsync = ctk.CTkSwitch(self.frame_video_options, text=self._("sw_vsync"), command=self.salvar_configuracoes_video)
            self.switch_vsync.grid(row=7, column=0, columnspan=2, sticky="w", pady=5)
            self.switch_widescreen = ctk.CTkSwitch(self.frame_video_options, text="📺 Forçar Widescreen (Hacks 16:9)", command=self.salvar_configuracoes_video)
            self.switch_widescreen.grid(row=8, column=0, columnspan=2, sticky="w", pady=5)

            # Botão Salvar REMOVIDO DA ABA VÍDEO!

            self.frame_divisor_vid = ctk.CTkFrame(self.tab_video, height=2, fg_color="#444")
            self.frame_divisor_vid.pack(fill="x", padx=10, pady=(15, 5))

            self.label_hw_title = ctk.CTkLabel(self.tab_video, text=self._("lbl_hw_title"), font=ctk.CTkFont(size=14, weight="bold"))
            self.label_hw_title.pack(anchor="w", padx=10, pady=(5, 2))

            self.frame_hw = ctk.CTkFrame(self.tab_video, fg_color="#2b2b2b")
            self.frame_hw.pack(fill="x", padx=10, pady=2, ipadx=5, ipady=5)
            
            self.lbl_hw_info = ctk.CTkLabel(self.frame_hw, text=self._("lbl_hw_search"), justify="left")
            self.lbl_hw_info.pack(anchor="w", padx=10, pady=5)
            
            self.btn_driver = ctk.CTkButton(self.frame_hw, text=self._("btn_driver"), width=200, height=28, fg_color="#4169E1", hover_color="#1E90FF", command=self.abrir_site_driver, state="disabled")
            self.btn_driver.pack(anchor="w", padx=10, pady=(0, 5))

        def atualizar_lista_fisicos(self):
            # Limpa o frame para não sobrepor se o usuário recarregar a tela
            for widget in getattr(self, 'frame_fisicos_list', ctk.CTkFrame(self)).winfo_children():
                widget.destroy()
            
            dispositivos = self.devices_manager.obter_dispositivos_fisicos()
            self.combos_fisicos = {}
            
            if not dispositivos:
                lbl = ctk.CTkLabel(self.frame_fisicos_list, text="Nenhum dispositivo físico (Teclado, Mouse, Gamepad) detectado.\nAbra um jogo no Flycast pelo menos uma vez para que ele registre seus periféricos no emu.cfg.", text_color="gray", justify="left")
                lbl.pack(pady=20, padx=10, anchor="w")
                return
                
            for i, (key, val) in enumerate(dispositivos.items()):
                # Formata o nome técnico (maple_sdl_joystick_0 -> Sdl Joystick 0)
                nome_formatado = key.replace('maple_', '').replace('_', ' ').title()
                
                # Identifica ícones intuitivos
                icone = "🎮" if "joystick" in key.lower() or "xinput" in key.lower() else "⌨️" if "keyboard" in key.lower() else "🖱️" if "mouse" in key.lower() else "🔌"

                f = ctk.CTkFrame(self.frame_fisicos_list, fg_color="transparent")
                f.pack(fill="x", pady=2)
                
                lbl_icon = ctk.CTkLabel(f, text=icone, width=25)
                lbl_icon.pack(side="left", padx=(10, 0))
                
                lbl = ctk.CTkLabel(f, text=nome_formatado, width=220, anchor="w", font=ctk.CTkFont(weight="bold"))
                lbl.pack(side="left", padx=5)
                
                cb = ctk.CTkComboBox(f, values=["Porta A", "Porta B", "Porta C", "Porta D", "Nenhum"], width=100, state="readonly", command=self.devices_manager.salvar_dispositivos)
                cb.pack(side="right", padx=10)
                
                porta_nome = self.devices_manager.mapa_portas_fisicas.get(val, "Nenhum")
                cb.set(porta_nome)
                
                self.combos_fisicos[key] = cb

        def atualizar_ui_slots(self, porta, valor):
            sem_slots = ["Controle Marcas", "Teclado", "Mouse", "Nenhum", "Controle Densha de Go", "Controle de música Pop'n", "Controle de Pesca", "Controlador DreamParaPara"]
            um_slot = ["Controle de Alavanca Dupla", "Controle de Corrida"]
            
            cb_s1 = self.combos_devices.get(f"{porta}_s1")
            cb_s2 = self.combos_devices.get(f"{porta}_s2")
            btn_color = getattr(self, 'btn_color_pickers', {}).get(porta)
            
            if not cb_s1 or not cb_s2: return
            
            # Reseta tudo para o padrão livre
            cb_s1.configure(state="readonly")
            cb_s2.grid()
            cb_s2.configure(state="readonly")
            if btn_color: btn_color.grid_remove()
            
            if valor in sem_slots:
                cb_s1.set("Nenhum")
                cb_s1.configure(state="disabled")
                cb_s2.set("Nenhum")
                cb_s2.configure(state="disabled")
            elif valor in um_slot:
                cb_s2.set("Nenhum")
                cb_s2.configure(state="disabled")
            elif valor == "Pistola de Luz":
                cb_s2.grid_remove() # Some com o Slot 2
                if btn_color: btn_color.grid() # Mostra a Mira!

        def ao_trocar_controle_main(self, porta, valor):
            # Atualiza o visual da interface e depois grava o arquivo
            self.atualizar_ui_slots(porta, valor)
            if hasattr(self, 'devices_manager'):
                self.devices_manager.salvar_dispositivos()

        def escolher_cor_mira(self, porta):
            from tkinter import colorchooser
            cor = colorchooser.askcolor(title=f"Cor da Mira - Porta {porta}")
            if cor[1]: # Retorna a cor Hex (Ex: '#ff0000')
                r, g, b = int(cor[1][1:3], 16), int(cor[1][3:5], 16), int(cor[1][5:7], 16)
                argb = (255 << 24) | (r << 16) | (g << 8) | b # O Flycast lê a cor em ARGB (32 bits)
                self.cores_mira[porta] = str(argb)
                self.btn_color_pickers[porta].configure(fg_color=cor[1])
                if hasattr(self, 'devices_manager'):
                    self.devices_manager.salvar_dispositivos()

        def construir_aba_dispositivos(self):
            # 1. A MÁGICA DO AUTOFIT: A aba toda vira uma página rolável!
            self.scroll_devices = ctk.CTkScrollableFrame(self.tab_devices, fg_color="transparent")
            self.scroll_devices.pack(fill="both", expand=True)

            # --- 1. INJEÇÃO DE PERFIS DE CONTROLE (NOVO TOPO) ---
            self.label_ctrl_title = ctk.CTkLabel(self.scroll_devices, text=self._("lbl_ctrl_title", default="Injeção de Perfis de Controle"), font=ctk.CTkFont(size=16, weight="bold"))
            self.label_ctrl_title.pack(anchor="w", padx=10, pady=(10, 5))

            self.label_ctrl_desc = ctk.CTkLabel(self.scroll_devices, text=self._("lbl_ctrl_desc", default="Selecione o modelo abaixo e injete na pasta mappings."), text_color="gray", justify="left")
            self.label_ctrl_desc.pack(anchor="w", padx=10, pady=(0, 10))

            self.frame_ctrl = ctk.CTkFrame(self.scroll_devices, fg_color="transparent")
            self.frame_ctrl.pack(fill="x", padx=10, pady=(0, 15))

            self.combo_ctrl = ctk.CTkComboBox(self.frame_ctrl, values=list(PERFIS_CONTROLES.keys()), width=350, state="readonly")
            self.combo_ctrl.pack(side="left", fill="x", expand=True, padx=(0, 10))
            if list(PERFIS_CONTROLES.keys()):
                self.combo_ctrl.set(list(PERFIS_CONTROLES.keys())[0])

            self.btn_injetar_ctrl = ctk.CTkButton(self.frame_ctrl, text=self._("btn_inject", default="Injetar Perfil de Controle"), width=200, height=30, font=ctk.CTkFont(weight="bold"), fg_color="#8B008B", hover_color="#A52A2A", command=self.injetar_controle)
            self.btn_injetar_ctrl.pack(side="right")

            self.frame_divisor_ctrl = ctk.CTkFrame(self.scroll_devices, height=2, fg_color="#444")
            self.frame_divisor_ctrl.pack(fill="x", padx=10, pady=(5, 15))

            # --- 2. DISPOSITIVOS FÍSICOS REAIS (MEIO) ---
            self.label_fisicos_title = ctk.CTkLabel(self.scroll_devices, text="🎮 Dispositivos Físicos Reais", font=ctk.CTkFont(size=16, weight="bold"))
            self.label_fisicos_title.pack(anchor="w", padx=10, pady=(0, 5))

            self.frame_fisicos_list = ctk.CTkFrame(self.scroll_devices, fg_color="#1a1a1a", corner_radius=10)
            self.frame_fisicos_list.pack(fill="x", padx=10, pady=(0, 15))
            self.combos_fisicos = {}

            # --- 3. DISPOSITIVOS VIRTUAIS DO DREAMCAST (EMBAIXO) ---
            self.label_devices_title = ctk.CTkLabel(self.scroll_devices, text="🖥️ Portas Virtuais do Dreamcast", font=ctk.CTkFont(size=16, weight="bold"))
            self.label_devices_title.pack(anchor="w", padx=10, pady=(5, 5))
            
            self.frame_devices_grid = ctk.CTkFrame(self.scroll_devices, fg_color="#1a1a1a", corner_radius=10)
            self.frame_devices_grid.pack(fill="x", padx=10, pady=5)

            self.combos_devices = {}
            portas = ["A", "B", "C", "D"]

            opcoes_controles = list(self.devices_manager.mapa_controles.keys())
            opcoes_acessorios = list(self.devices_manager.mapa_acessorios.keys())

            ctk.CTkLabel(self.frame_devices_grid, text="Porta", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10)
            ctk.CTkLabel(self.frame_devices_grid, text="Controle Principal", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=10)
            ctk.CTkLabel(self.frame_devices_grid, text="Slot 1 (VMU)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=10)
            ctk.CTkLabel(self.frame_devices_grid, text="Slot 2 (Extra)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=10)

            self.btn_color_pickers = {}
            self.cores_mira = {"A": "0", "B": "0", "C": "0", "D": "0"}

            for i, p in enumerate(portas):
                lbl = ctk.CTkLabel(self.frame_devices_grid, text=f"Porta {p}", font=ctk.CTkFont(weight="bold"))
                lbl.grid(row=i+1, column=0, padx=10, pady=10, sticky="e")

                cb_main = ctk.CTkComboBox(self.frame_devices_grid, values=opcoes_controles, width=190, state="readonly", command=lambda val, p=p: self.ao_trocar_controle_main(p, val))
                cb_main.grid(row=i+1, column=1, padx=5, pady=10)
                cb_main.set("Nenhum")
                self.combos_devices[f"{p}_main"] = cb_main

                cb_s1 = ctk.CTkComboBox(self.frame_devices_grid, values=opcoes_acessorios, width=140, state="readonly", command=self.devices_manager.salvar_dispositivos)
                cb_s1.grid(row=i+1, column=2, padx=5, pady=10)
                cb_s1.set("Nenhum")
                self.combos_devices[f"{p}_s1"] = cb_s1

                cb_s2 = ctk.CTkComboBox(self.frame_devices_grid, values=opcoes_acessorios, width=140, state="readonly", command=self.devices_manager.salvar_dispositivos)
                cb_s2.grid(row=i+1, column=3, padx=5, pady=10)
                cb_s2.set("Nenhum")
                self.combos_devices[f"{p}_s2"] = cb_s2

                btn_color = ctk.CTkButton(self.frame_devices_grid, text="🎯 Cor da Mira", width=140, fg_color="#333333", text_color="white", command=lambda p=p: self.escolher_cor_mira(p))
                btn_color.grid(row=i+1, column=3, padx=5, pady=10)
                btn_color.grid_remove()
                self.btn_color_pickers[p] = btn_color

            texto_dica = (
                "💡 Recomendações de Hardware:\n"
                "• Setup Padrão: 'Controle Sega' e 'Sega VMU' no Slot 1 da Porta A.\n"
                "• Vibração: Conecte o 'Pacote de Vibração' no Slot 2 da Porta A para Force Feedback.\n"
                "• Arcades: Jogos como Marvel vs Capcom ficam excelentes com 'Controle de Arcade/Ascii'."
            )
            self.lbl_devices_dica = ctk.CTkLabel(self.scroll_devices, text=texto_dica, text_color="gray", justify="left", font=ctk.CTkFont(size=12))
            self.lbl_devices_dica.pack(anchor="w", padx=15, pady=(15, 0))

            self.frame_divisor_vmu = ctk.CTkFrame(self.scroll_devices, height=2, fg_color="#444")
            self.frame_divisor_vmu.pack(fill="x", padx=10, pady=(15, 10))

            self.label_vmu_configs = ctk.CTkLabel(self.scroll_devices, text="Configurações de Visor do VMU", font=ctk.CTkFont(size=14, weight="bold"))
            self.label_vmu_configs.pack(anchor="w", padx=10, pady=(0, 10))

            self.frame_vmu_switches = ctk.CTkFrame(self.scroll_devices, fg_color="transparent")
            self.frame_vmu_switches.pack(fill="x", padx=20, pady=(0, 20))

            self.switch_vmu = ctk.CTkSwitch(self.frame_vmu_switches, text=self._("sw_vmu"), command=lambda: self.salvar_configuracoes_emulador(silencioso=True))
            self.switch_vmu.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=10)

            self.switch_osd_vmu = ctk.CTkSwitch(self.frame_vmu_switches, text=self._("sw_osd"), command=lambda: self.salvar_configuracoes_emulador(silencioso=True))
            self.switch_osd_vmu.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=10)

            self.switch_vmu_sound = ctk.CTkSwitch(self.frame_vmu_switches, text=self._("sw_vmu_snd"), command=lambda: self.salvar_configuracoes_emulador(silencioso=True))
            self.switch_vmu_sound.grid(row=1, column=0, sticky="w", pady=10)

        def injetar_controle(self):
            controle_selecionado = self.combo_ctrl.get()
            perfil = PERFIS_CONTROLES.get(controle_selecionado)
            if not perfil: return

            install_path = self.entry_path.get()
            if not install_path or not os.path.exists(install_path):
                mb.showerror("Erro", self._("msg_error"), parent=self)
                return

            mappings_dir = os.path.join(install_path, "data", "mappings")
            os.makedirs(mappings_dir, exist_ok=True)
            
            arquivo_destino = os.path.join(mappings_dir, perfil["arquivo"])
            try:
                with open(arquivo_destino, "w", encoding="utf-8") as f:
                    f.write(perfil["conteudo"])
                self.log(f"🎮 Injeção: '{perfil['arquivo']}' injetado em data/mappings/ com sucesso.")
                self.mostrar_toast("Controle Injetado", "O perfil de controle foi aplicado com sucesso e está pronto para uso!", "success")
            except Exception as e:
                self.log(f"❌ Erro ao injetar o controle: {e}")
                self.mostrar_toast("Falha na Injeção", f"Não foi possível aplicar o controle: {e}", "error")

        def construir_aba_saves(self):
            self.label_cloud = ctk.CTkLabel(self.tab_saves, text=self._("lbl_cloud"), font=ctk.CTkFont(weight="bold", size=14))
            self.label_cloud.pack(anchor="w", padx=10, pady=(15, 2))
            
            self.cloud_var = ctk.StringVar(value="nenhum")
            self.frame_cloud = ctk.CTkFrame(self.tab_saves, fg_color="transparent")
            self.frame_cloud.pack(fill="x", padx=10, pady=(0, 5))

            has_gdrive = self.save_manager.verificar_caminho_nuvem("Google Drive")
            has_onedrive = self.save_manager.verificar_caminho_nuvem("OneDrive")

            # --- MÁGICA: Auto-Save nas Nuvens e Checkboxes ---
            self.rb_cloud_none = ctk.CTkRadioButton(self.frame_cloud, text=self._("rb_none"), font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="nenhum", command=self.salvar_estado_atual)
            self.rb_cloud_none.pack(side="left", padx=(0, 15))

            self.rb_cloud_gdrive = ctk.CTkRadioButton(self.frame_cloud, text="Google Drive", font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="gdrive", command=self.salvar_estado_atual)
            self.rb_cloud_gdrive.pack(side="left", padx=(0, 15))
            if not has_gdrive: self.rb_cloud_gdrive.configure(state="disabled")

            self.rb_cloud_onedrive = ctk.CTkRadioButton(self.frame_cloud, text="OneDrive", font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="onedrive", command=self.salvar_estado_atual)
            self.rb_cloud_onedrive.pack(side="left", padx=(0, 15))
            if not has_onedrive: self.rb_cloud_onedrive.configure(state="disabled")

            nuvem_salva = self.config_atual.get("cloud_provider", "nenhum")
            if nuvem_salva == "gdrive" and has_gdrive: self.cloud_var.set("gdrive")
            elif nuvem_salva == "onedrive" and has_onedrive: self.cloud_var.set("onedrive")
            else: self.cloud_var.set("nenhum")

            self.switch_mappings = ctk.CTkSwitch(self.tab_saves, text=self._("sw_map"), command=self.salvar_estado_atual)
            self.switch_mappings.pack(anchor="w", padx=10, pady=(5, 10))
            if self.config_atual.get("backup_mappings", False): self.switch_mappings.select()

            self.frame_limit = ctk.CTkFrame(self.tab_saves, fg_color="transparent")
            self.frame_limit.pack(fill="x", padx=10, pady=(0, 10))
            self.lbl_limit = ctk.CTkLabel(self.frame_limit, text=self._("lbl_backup_limit"))
            self.lbl_limit.pack(side="left")
            
            self.combo_limit = ctk.CTkComboBox(self.frame_limit, values=["1", "3", "5", "10", "15", self._("limit_unlimited")], width=100, state="readonly", command=lambda x: self.salvar_estado_atual())
            self.combo_limit.pack(side="left", padx=10)
            
            val_salvo = self.config_atual.get("backup_limit", "5")
            if val_salvo in ["Ilimitado", "Unlimited", "Illimité", "Unbegrenzt", "无限制", "無制限", "Неограничено", "غير محدود", "असीमित"]:
                self.combo_limit.set(self._("limit_unlimited"))
            elif val_salvo in ["1", "3", "5", "10", "15"]:
                self.combo_limit.set(val_salvo)
            else:
                self.combo_limit.set("5")

            self.frame_divisor = ctk.CTkFrame(self.tab_saves, height=2, fg_color="#444")
            self.frame_divisor.pack(fill="x", padx=10, pady=(5, 10))

            self.label_saves_title = ctk.CTkLabel(self.tab_saves, text=self._("lbl_saves_title"), font=ctk.CTkFont(size=14, weight="bold"))
            self.label_saves_title.pack(anchor="w", padx=10, pady=(5, 5))
            
            self.label_saves_desc = ctk.CTkLabel(self.tab_saves, text=self._("lbl_saves_desc"), text_color="gray", justify="left")
            self.label_saves_desc.pack(anchor="w", padx=10, pady=(0, 5))

            self.frame_saves_list = ctk.CTkFrame(self.tab_saves, fg_color="transparent")
            self.frame_saves_list.pack(fill="x", padx=10, pady=5)

            self.btn_buscar_saves = ctk.CTkButton(self.frame_saves_list, text=self._("btn_search_saves"), width=140, command=self.save_manager.buscar_backups_saves)
            self.btn_buscar_saves.pack(side="left", padx=(0, 10))

            self.combo_backups = ctk.CTkComboBox(self.frame_saves_list, values=[self._("combo_saves_def")], width=350, state="readonly")
            self.combo_backups.pack(side="left", fill="x", expand=True)
            self.combo_backups.set(self._("combo_saves_def"))

            self.btn_restaurar_save = ctk.CTkButton(self.tab_saves, text=self._("btn_extract"), width=280, height=35, font=ctk.CTkFont(weight="bold"), fg_color="#228B22", hover_color="#006400", command=self.save_manager.restaurar_backup_selecionado)
            self.btn_restaurar_save.pack(pady=(10, 10))
            self.btn_restaurar_save.configure(state="disabled")
            self.arquivos_backup_encontrados = {}

            self.frame_divisor_cfg = ctk.CTkFrame(self.tab_saves, height=2, fg_color="#444")
            self.frame_divisor_cfg.pack(fill="x", padx=10, pady=(15, 10))

            self.lbl_cfg_bkp_title = ctk.CTkLabel(self.tab_saves, text=self._("lbl_cfg_bkp_title", default="Backup de Arquivos de Configuração"), font=ctk.CTkFont(size=14, weight="bold"))
            self.lbl_cfg_bkp_title.pack(anchor="w", padx=10, pady=(5, 5))

            self.frame_switches_cfg = ctk.CTkFrame(self.tab_saves, fg_color="transparent")
            self.frame_switches_cfg.pack(fill="x", padx=10, pady=0)

            self.sw_bkp_emu = ctk.CTkSwitch(self.frame_switches_cfg, text=self._("sw_bkp_emu", default="Emulador (emu.cfg)"), command=self.salvar_estado_atual)
            self.sw_bkp_emu.grid(row=0, column=0, sticky="w", padx=(0, 15), pady=5)
            if self.config_atual.get("backup_cfg_emu", True): self.sw_bkp_emu.select()

            self.sw_bkp_upd = ctk.CTkSwitch(self.frame_switches_cfg, text=self._("sw_bkp_upd", default="Updater (config.json)"), command=self.salvar_estado_atual)
            self.sw_bkp_upd.grid(row=0, column=1, sticky="w", padx=(0, 15), pady=5)
            if self.config_atual.get("backup_cfg_upd", True): self.sw_bkp_upd.select()

            self.sw_bkp_ra = ctk.CTkSwitch(self.frame_switches_cfg, text=self._("sw_bkp_ra", default="Banco RA (RAlocal.db)"), command=self.salvar_estado_atual)
            self.sw_bkp_ra.grid(row=0, column=2, sticky="w", pady=5)
            if self.config_atual.get("backup_cfg_ra", True): self.sw_bkp_ra.select()

            self.btn_do_bkp_cfg = ctk.CTkButton(self.tab_saves, text=self._("btn_do_bkp_cfg", default="💾 Fazer Backup de Configurações Agora"), width=280, height=30, command=self.save_manager.realizar_backup_configs)
            self.btn_do_bkp_cfg.pack(pady=(10, 15))

            self.frame_cfg_list = ctk.CTkFrame(self.tab_saves, fg_color="transparent")
            self.frame_cfg_list.pack(fill="x", padx=10, pady=5)

            self.btn_buscar_cfg = ctk.CTkButton(self.frame_cfg_list, text=self._("btn_search_cfg", default="🔄 Buscar Configs"), width=140, command=self.save_manager.buscar_backups_configs)
            self.btn_buscar_cfg.pack(side="left", padx=(0, 10))

            self.combo_backups_cfg = ctk.CTkComboBox(self.frame_cfg_list, values=[self._("combo_cfg_def", default="Clique em Buscar Configs...")], width=350, state="readonly")
            self.combo_backups_cfg.pack(side="left", fill="x", expand=True)
            self.combo_backups_cfg.set(self._("combo_cfg_def", default="Clique em Buscar Configs..."))

            self.btn_restaurar_cfg = ctk.CTkButton(self.tab_saves, text=self._("btn_extract_cfg", default="📥 Restaurar Configurações"), width=280, height=35, font=ctk.CTkFont(weight="bold"), fg_color="#1E90FF", hover_color="#4169E1", command=self.save_manager.restaurar_backup_configs)
            self.btn_restaurar_cfg.pack(pady=(10, 10))
            self.btn_restaurar_cfg.configure(state="disabled")
            self.arquivos_cfg_encontrados = {}

        def resolver_bios_mal_posicionada(self, path):
            if getattr(self, 'bios_prompt_done', False): return
            self.bios_prompt_done = True
            resposta_mover = mb.askyesno(self._("msg_bios_move_title"), self._("msg_bios_move_desc"), parent=self)
            if resposta_mover:
                pasta_data = os.path.join(path, "data")
                os.makedirs(pasta_data, exist_ok=True)
                try:
                    shutil.move(os.path.join(path, "dc_boot.bin"), os.path.join(pasta_data, "dc_boot.bin"))
                    shutil.move(os.path.join(path, "dc_flash.bin"), os.path.join(pasta_data, "dc_flash.bin"))
                    mb.showinfo("Sucesso", self._("msg_success"), parent=self)
                    self.atualizar_status_diretorio(path)
                except Exception: pass
            else:
                resposta_config = mb.askyesno("BIOS", self._("msg_bios_register_desc"), parent=self)
                if resposta_config:
                    if atualizar_emu_cfg(install_path=path, bios_path=path):
                        self.atualizar_status_diretorio(path)

        def construir_aba_logs(self):
            self.label_logs_title = ctk.CTkLabel(self.tab_logs, text=self._("lbl_logs_title"), font=ctk.CTkFont(size=16, weight="bold"))
            self.label_logs_title.pack(anchor="w", padx=10, pady=(10, 0))

            self.frame_logs_botoes = ctk.CTkFrame(self.tab_logs, fg_color="transparent")
            self.frame_logs_botoes.pack(fill="x", padx=10, pady=5)

            self.btn_refresh_log = ctk.CTkButton(self.frame_logs_botoes, text=self._("btn_log_refresh"), width=100, command=self.carregar_logs)
            self.btn_refresh_log.pack(side="left", padx=5)

            self.btn_copy_log = ctk.CTkButton(self.frame_logs_botoes, text=self._("btn_log_copy"), width=100, command=self.copiar_logs)
            self.btn_copy_log.pack(side="left", padx=5)

            self.btn_clear_log = ctk.CTkButton(self.frame_logs_botoes, text=self._("btn_log_clear"), width=100, fg_color="#8B0000", hover_color="#A52A2A", command=self.limpar_logs)
            self.btn_clear_log.pack(side="left", padx=5)

            self.textbox_logs = ctk.CTkTextbox(self.tab_logs, width=540, height=450, state="disabled")
            self.textbox_logs.pack(padx=10, pady=5, fill="both", expand=True)

        def carregar_gpus(self):
            def rotina():
                gpus = obter_gpus_windows()
                if not gpus:
                    self.lbl_hw_info.configure(text=self._("msg_no_gpu"))
                    return
                texto = self._("msg_gpu_done")
                fabricante_detectado = None
                
                for i, gpu in enumerate(gpus):
                    nome = gpu['nome']
                    driver = gpu['driver']
                    texto += f"🎮 GPU {i+1}: {nome}\n⚙️ Driver: {driver}"
                    if i < len(gpus) - 1: texto += "\n\n ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ \n\n"
                    else: texto += "\n"
                        
                    if not fabricante_detectado:
                        nome_lower = nome.lower()
                        if "nvidia" in nome_lower: fabricante_detectado = "nvidia"
                        elif "amd" in nome_lower or "radeon" in nome_lower: fabricante_detectado = "amd"
                        elif "intel" in nome_lower: fabricante_detectado = "intel"
                
                self.fabricante_gpu = fabricante_detectado
                self.lbl_hw_info.configure(text=texto)
                if fabricante_detectado: self.btn_driver.configure(state="normal")
            threading.Thread(target=rotina, daemon=True).start()

        def abrir_site_driver(self):
            urls = {"nvidia": "https://www.nvidia.com/pt-br/geforce/drivers/", "amd": "https://www.amd.com/pt/support/download/drivers.html", "intel": "https://www.intel.com.br/content/www/br/pt/download-center/home.html"}
            if hasattr(self, 'fabricante_gpu') and self.fabricante_gpu in urls:
                webbrowser.open(urls[self.fabricante_gpu])
                mb.showinfo("Atualização de Driver", self._("msg_driver_suggest"), parent=self)

        def carregar_logs(self):
            log_path = os.path.join(self.entry_path.get(), "flycast_updater.log")
            self.textbox_logs.configure(state="normal")
            self.textbox_logs.delete("1.0", tk.END)
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8") as f: self.textbox_logs.insert(tk.END, f.read())
                    self.textbox_logs.see(tk.END)
                except Exception: pass
            else:
                self.textbox_logs.insert(tk.END, self._("log_not_found"))
            self.textbox_logs.configure(state="disabled")

        def copiar_logs(self):
            self.clipboard_clear()
            self.clipboard_append(self.textbox_logs.get("1.0", tk.END))
            self.mostrar_toast("Copiado!", "Os logs foram copiados para a área de transferência.", "success")

        def limpar_logs(self):
            log_path = os.path.join(self.entry_path.get(), "flycast_updater.log")
            if os.path.exists(log_path):
                try:
                    os.remove(log_path)
                    self.carregar_logs()
                    self.log("🗑️ Log limpo pelo usuário.")
                    self.mostrar_toast("Logs Limpos", "O histórico foi apagado com sucesso.", "info")
                except Exception: pass

        def salvar_estado_atual(self):
            self.config_atual["branch"] = self.branch_var.get()
            self.config_atual["create_startup"] = self.switch_startup.get() == 1
            self.config_atual["install_path"] = self.entry_path.get()
            self.config_atual["cloud_provider"] = self.cloud_var.get() if self.cloud_var.get() != "nenhum" else None
            self.config_atual["language"] = self.lang
            self.config_atual["backup_mappings"] = self.switch_mappings.get() == 1
            self.config_atual["backup_limit"] = self.combo_limit.get()
            self.config_atual["streamer_mode"] = getattr(self, "switch_streamer", ctk.BooleanVar(value=False)).get() == 1

            if hasattr(self, 'entry_manual_path'):
                self.config_atual["custom_manual_path"] = self.entry_manual_path.get() if self.switch_custom_paths.get() == 1 else ""
            if hasattr(self, 'entry_cheat_path'): # NOVO
                self.config_atual["custom_cheat_path"] = self.entry_cheat_path.get() if self.switch_custom_paths.get() == 1 else ""
            if hasattr(self, 'combo_tema'):
                self.config_atual["tema"] = self.combo_tema.get()
            if hasattr(self, 'sw_bkp_emu'):
                self.config_atual["backup_cfg_emu"] = self.sw_bkp_emu.get() == 1
                self.config_atual["backup_cfg_upd"] = self.sw_bkp_upd.get() == 1
                self.config_atual["backup_cfg_ra"] = self.sw_bkp_ra.get() == 1
            if hasattr(self, 'switch_sfx'):
                self.config_atual["disable_sfx"] = self.switch_sfx.get() == 1
                if hasattr(self, 'sfx'):
                    self.sfx.enabled = not self.config_atual["disable_sfx"] and HAS_PYGAME
                
            salvar_configuracao(self.config_atual)
            self.checar_status_backup()    
            salvar_configuracao(self.config_atual)
            self.checar_status_backup()

        def aplicar_tema(self, nome_tema=None):
            if not nome_tema: nome_tema = self.config_atual.get("tema", "Padrão DARK")
            tema = THEMES.get(nome_tema, THEMES["Padrão DARK"])
            primaria = tema["primary"]
            hover = tema["hover"]
            texto = tema["text"]

            botoes_excecao = [getattr(self, 'btn_rollback', None), getattr(self, 'btn_reconfig', None), getattr(self, 'btn_clear_log', None), getattr(self, 'btn_filter_fav', None), getattr(self, 'btn_toggle_senha', None)]

            try:
                self.tabview.configure(segmented_button_selected_color=primaria, segmented_button_selected_hover_color=hover)
                self.progressbar.configure(progress_color=primaria)
                self.lbl_rodape.configure(text_color=primaria)
                self.btn_atualizar.configure(fg_color=primaria, hover_color=hover, text_color=texto)
            except Exception: pass

            def colorir_widgets(pai):
                for widget in pai.winfo_children():
                    if isinstance(widget, ctk.CTkButton) and widget not in botoes_excecao:
                        txt = widget.cget("text")
                        if txt not in ["X", "⭐", "ℹ️", "✔️ Salvo!", "?"]:
                            try: widget.configure(fg_color=primaria, hover_color=hover, text_color=texto)
                            except Exception: pass
                    elif isinstance(widget, ctk.CTkSwitch):
                        try: widget.configure(progress_color=primaria)
                        except Exception: pass
                    colorir_widgets(widget)

            colorir_widgets(self)
            
            self.config_atual["tema"] = nome_tema
            if hasattr(self, 'combo_tema'): self.combo_tema.set(nome_tema)
            self.log(f"🎨 Tema Visual carregado/alterado: {nome_tema}")
            self.salvar_estado_atual()
            
            if hasattr(self, 'game_manager'):
                self.game_manager.escanear_jogos()

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
                self.log("🚀 Primeiro acesso detectado. Exibindo assistente de configuração.")
                resposta = mb.askyesno(self._("msg_welcome_title"), self._("msg_welcome_desc"), parent=self)
                if resposta:
                    self.tabview.set(self._("tab_emu", default="⚙️ Configurações"))
                    self.config_atual["setup_completed"] = True
                else:
                    self.config_atual["setup_declined"] = True
                self.salvar_estado_atual()
            elif completo:
                self.tabview.set(self._("tab_games", default="🕹️ Launcher"))
            self.carregar_logs()

        def procurar_e_instalar_bios(self, install_path, custom_bios_path):
            self.log("🔍 Usuário abriu seletor de arquivos de BIOS.")
            arquivo = ctk.filedialog.askopenfilename(title="Select BIOS (.bin) or ZIP (.zip)", filetypes=[("BIOS / ZIP", "*.bin *.zip"), ("All files", "*.*")])
            if not arquivo: return
                
            target_dir = custom_bios_path if custom_bios_path else os.path.join(install_path, "data")
            os.makedirs(target_dir, exist_ok=True)
            self.log(f"📂 Diretório alvo da BIOS: {target_dir}")
            
            if arquivo.lower().endswith(".zip"):
                try:
                    with zipfile.ZipFile(arquivo, 'r') as zip_ref:
                        encontrou = False
                        for file_info in zip_ref.infolist():
                            basename = os.path.basename(file_info.filename).lower()
                            if basename in ['dc_boot.bin', 'dc_flash.bin']:
                                source = zip_ref.open(file_info.filename)
                                target = open(os.path.join(target_dir, basename), "wb")
                                with source, target:
                                    shutil.copyfileobj(source, target)
                                encontrou = True
                        if encontrou: mb.showinfo("Sucesso", self._("msg_bios_zip_success"), parent=self)
                        else: mb.showwarning("Aviso", "O ZIP não continha dc_boot.bin ou dc_flash.bin.", parent=self)
                except Exception as e:
                    mb.showerror("Erro", f"Erro: {e}", parent=self)
            elif arquivo.lower().endswith(".bin"):
                orig_basename = os.path.basename(arquivo).lower()
                target_basename = orig_basename
                if "boot" in orig_basename and "dc_boot.bin" not in orig_basename: target_basename = "dc_boot.bin"
                elif "flash" in orig_basename and "dc_flash.bin" not in orig_basename: target_basename = "dc_flash.bin"
                
                try:
                    shutil.copy(arquivo, os.path.join(target_dir, target_basename))
                    has_boot = os.path.exists(os.path.join(target_dir, "dc_boot.bin")) or os.path.exists(os.path.join(target_dir, "DC_BOOT.BIN"))
                    has_flash = os.path.exists(os.path.join(target_dir, "dc_flash.bin")) or os.path.exists(os.path.join(target_dir, "DC_FLASH.BIN"))
                    missing_other = None
                    if not has_boot: missing_other = "dc_boot.bin"
                    elif not has_flash: missing_other = "dc_flash.bin"
                    
                    if missing_other:
                        resp = mb.askyesno(self._("title_bios_partial"), self._("msg_bios_partial").format(missing=missing_other), parent=self)
                        if resp: self.procurar_e_instalar_bios(install_path, custom_bios_path)
                    else:
                        mb.showinfo("Sucesso", self._("msg_bios_bin_success"), parent=self)
                except Exception as e:
                    mb.showerror("Erro", f"Erro: {e}", parent=self)
            self.atualizar_status_diretorio(install_path)

        def tratar_bios_ausente(self, path, custom_bios_path, has_boot, has_flash):
            if getattr(self, 'bios_prompt_done', False): return
            self.bios_prompt_done = True
            missing = []
            if not has_boot: missing.append("dc_boot.bin")
            if not has_flash: missing.append("dc_flash.bin")
            if not missing: return
            
            msg = self._("msg_bios_missing").format(files="\n- ".join(missing))
            resposta = mb.askyesno(self._("title_bios_missing"), msg, parent=self)
            if resposta: self.procurar_e_instalar_bios(path, custom_bios_path)

        def carregar_dados_atuais_emu_cfg(self):
            install_path = os.path.normpath(self.entry_path.get())
            def_bios = os.path.join(install_path, "bios")
            def_vmu = os.path.join(install_path, "vmu")
            def_state = os.path.join(install_path, "save_state")
            def_save = os.path.join(install_path, "saves")
            def_manual = os.path.join(install_path, "manuals")
            def_cheat = os.path.join(install_path, "data", "cheats")
            
            self.definir_entry_custom(self.entry_bios_path, def_bios)
            self.definir_entry_custom(self.entry_vmu_path, def_vmu)
            self.definir_entry_custom(self.entry_state_path, def_state)
            self.definir_entry_custom(self.entry_save_path, def_save)
            self.definir_entry_custom(self.entry_manual_path, def_manual)
            self.definir_entry_custom(self.entry_cheat_path, def_cheat)

            self.switch_custom_paths.deselect()
            self.toggle_custom_paths()

            caminhos = [os.path.join(install_path, "emu.cfg"), os.path.join(install_path, "data", "emu.cfg")]
            for p in caminhos:
                if os.path.exists(p):
                    try:
                        config = configparser.RawConfigParser(strict=False)
                        config.optionxform = str
                        config.read(p, encoding='utf-8')
                        
                        if config.has_section('config'):
                            if config.has_option('config', 'Dreamcast.ContentPath'):
                                caminhos_brutos = config.get('config', 'Dreamcast.ContentPath')
                                self.rom_paths_list = [cp.strip() for cp in caminhos_brutos.split(";") if cp.strip()]
                                self.atualizar_lista_ui_roms()
                                
                            bios_p = config.get('config', 'Dreamcast.BiosPath', fallback='')
                            vmu_p = config.get('config', 'Dreamcast.VmuPath', fallback='')
                            state_p = config.get('config', 'Dreamcast.SavestatePath', fallback='')
                            save_p = config.get('config', 'Dreamcast.SavePath', fallback='')
                            
                            custom_manual = self.config_atual.get("custom_manual_path", "")
                            custom_cheat = self.config_atual.get("custom_cheat_path", "")
                            
                            if bios_p or vmu_p or state_p or save_p or custom_manual or custom_cheat:
                                self.switch_custom_paths.select()
                                self.toggle_custom_paths()
                                if bios_p: self.definir_entry_custom(self.entry_bios_path, bios_p)
                                if vmu_p: self.definir_entry_custom(self.entry_vmu_path, vmu_p)
                                if state_p: self.definir_entry_custom(self.entry_state_path, state_p)
                                if save_p: self.definir_entry_custom(self.entry_save_path, save_p)
                                if custom_manual: self.definir_entry_custom(self.entry_manual_path, custom_manual)
                                if custom_cheat: self.definir_entry_custom(self.entry_cheat_path, custom_cheat)

                            if config.get('config', 'PerGameVmu', fallback='no').lower() == 'yes': self.switch_vmu.select()
                            if config.get('config', 'FetchBoxart', fallback='no').lower() == 'yes': self.switch_boxart.select()
                            if config.get('config', 'Dreamcast.Cable', fallback='3') == '0': self.switch_vga.select()
                            if config.get('config', 'DiscordPresence', fallback='no').lower() == 'yes': self.switch_discord.select()
                            if config.get('config', 'ShowOsdVmu', fallback='no').lower() == 'yes' or config.get('config', 'rend.FloatVMUs', fallback='no').lower() == 'yes': 
                                self.switch_osd_vmu.select()
                            if config.get('config', 'UseReios', fallback='no').lower() == 'yes': 
                                if hasattr(self, 'switch_hle'): self.switch_hle.select()
                            
                        if config.has_section('achievements'):
                            if config.get('achievements', 'Enabled', fallback='no').lower() == 'yes': self.switch_ra.select()
                            if config.get('achievements', 'HardcoreMode', fallback='no').lower() == 'yes': self.switch_hardcore.select()
                            if config.has_option('achievements', 'UserName'):
                                self.entry_ra_user.insert(0, config.get('achievements', 'UserName'))
                            if config.has_option('achievements', 'Token'):
                                self.token_ra_salvo = config.get('achievements', 'Token')
                                self.entry_ra_pass.insert(0, self.token_ra_salvo)
                            
                            api_key = self.config_atual.get("ra_api_key", "")
                            self.entry_ra_api.delete(0, 'end')
                            self.entry_ra_api.insert(0, api_key)

                        if config.has_section('audio'):
                            if config.get('audio', 'VmuSound', fallback='no').lower() == 'yes': self.switch_vmu_sound.select()
                            
                        if config.has_section('config'):
                            if config.has_option('config', 'pvr.rend'):
                                api_rev_map = {"0": "OpenGL", "1": "DirectX 9", "2": "DirectX 11", "4": "Vulkan"}
                                self.api_var.set(api_rev_map.get(config.get('config', 'pvr.rend'), "DirectX 11"))
                            if config.has_option('config', 'rend.Resolution'):
                                res_map = {"480": "640x480 (Nativo)", "720": "960x720 (1.5x)", "960": "1280x960 (2x)", "1080": "1440x1080 (3x)", "1440": "1920x1440 (4x)", "2160": "2880x2160 (6x)"}
                                self.combo_res.set(res_map.get(config.get('config', 'rend.Resolution'), "640x480 (Nativo)"))
                            if config.get('config', 'rend.IntegerScale', fallback='no').lower() == 'yes': self.switch_integer.select()
                            if config.get('config', 'rend.LinearInterpolation', fallback='no').lower() == 'yes': self.switch_linear.select()
                            if config.get('config', 'rend.vsync', fallback='no').lower() == 'yes': self.switch_vsync.select()
                            if config.get('config', 'WidescreenGameHacks', fallback='no').lower() == 'yes': self.switch_widescreen.select()

                        if config.has_section('window'):
                            if config.get('window', 'fullscreen', fallback='no').lower() == 'yes': self.switch_fullscreen.select()
                            
                            try:
                                win_left = int(float(config.get('window', 'left', fallback='0')))
                                win_top = int(float(config.get('window', 'top', fallback='0')))
                                if hasattr(self, 'lista_monitores'):
                                    for m in self.lista_monitores:
                                        if abs(m['left'] - win_left) <= 50 and abs(m['top'] - win_top) <= 50:
                                            self.combo_monitor.set(m['nome'])
                                            break
                            except Exception: pass
                        break
                    except Exception: pass

            # --- CORREÇÃO: AGORA ELE CARREGA FORA DA BARREIRA! ---
            if hasattr(self, 'devices_manager'):
                self.devices_manager.carregar_dispositivos()
                
        def salvar_configuracoes_emulador(self, silencioso=True):
            install_path = self.entry_path.get()
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

            hle_bios = self.switch_hle.get() == 1 if hasattr(self, 'switch_hle') else False
            is_streamer = getattr(self, "switch_streamer", ctk.BooleanVar(value=False)).get() == 1
            use_custom = self.switch_custom_paths.get() == 1
            bios_p = self.entry_bios_path.get() if use_custom else ""
            vmu_p = self.entry_vmu_path.get() if use_custom else ""
            state_p = self.entry_state_path.get() if use_custom else ""
            save_p = self.entry_save_path.get() if use_custom else ""

            ra_token_final = ""
            if ra_on and ra_user and ra_pass_input:
                if getattr(self, 'token_ra_salvo', '') == ra_pass_input:
                    ra_token_final = self.token_ra_salvo
                else:
                    if not silencioso:
                        self.btn_salvar_config_emu.configure(text="⏳ Autenticando...")
                        self.update() 
                    token_api = obter_token_retroachievements(ra_user, ra_pass_input)
                    if token_api:
                        ra_token_final = token_api
                        self.token_ra_salvo = token_api
                    else:
                        if not silencioso:
                            self.mostrar_toast("Erro de Login", "Não foi possível autenticar no RetroAchievements.", "error")
                            self.btn_salvar_config_emu.configure(text=self._("btn_save_emu"))
                        return 
            else:
                ra_token_final = ra_pass_input

            sucesso = atualizar_emu_cfg(
                install_path=install_path, roms_path=self.rom_paths_list,
                ra_enabled=ra_on, ra_user=ra_user, ra_pass=ra_token_final, ra_hardcore=ra_hard,
                vmu_individual=qol_vmu, fetch_boxart=qol_boxart, vga_cable=qol_vga,
                discord_presence=qol_discord, show_osd_vmu=qol_osd_vmu, vmu_sound=qol_vmu_sound,
                bios_path=bios_p, vmu_path=vmu_p, state_path=state_p, save_path=save_p,
                streamer_mode=is_streamer, use_hle=hle_bios
            )

            self.config_atual["setup_completed"] = True
            self.config_atual["ra_api_key"] = getattr(self, "entry_ra_api", tk.Entry()).get().strip() if hasattr(self, "entry_ra_api") else ""
            self.salvar_estado_atual()
            
            if not silencioso:
                self.btn_salvar_config_emu.configure(text=self._("btn_save_emu"))
                if sucesso: 
                    self.mostrar_toast("Salvo!", "Suas configurações foram aplicadas com sucesso.", "success")
                else: 
                    self.mostrar_toast("Erro", "Não foi possível salvar o emu.cfg.", "error")
        
        def salvar_configuracoes_video(self, *args):
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
            wide_hack = self.switch_widescreen.get() == 1
            
            monitor_str = self.combo_monitor.get()
            monitor_selecionado = next((m for m in self.lista_monitores if m['nome'] == monitor_str), None)
            win_left, win_top = None, None
            if monitor_selecionado:
                win_left = monitor_selecionado['left']
                win_top = monitor_selecionado['top']

            sucesso = atualizar_emu_cfg(
                install_path=install_path, vid_api=api, vid_res=res_val, 
                vid_full=full, vid_int=integer, vid_lin=linear, vid_vsync=vsync,
                window_left=win_left, window_top=win_top, widescreen_hack=wide_hack
            )
            self.salvar_estado_atual()
            if sucesso: self.log("🖥️ Vídeo: Configurações injetadas no emu.cfg silenciosamente.")
            else: self.log("❌ Vídeo: Erro ao auto-salvar configurações.")

        def ao_trocar_branch(self):
            self.salvar_estado_atual()
            self.atualizar_status_diretorio(self.entry_path.get())

        def ao_trocar_hle(self):
            self.salvar_estado_atual()
            self.salvar_configuracoes_emulador(silencioso=True)
            estado = "ATIVADA" if self.switch_hle.get() == 1 else "DESATIVADA"
            self.log(f"⚙️ BIOS HLE foi {estado}.")

        def toggle_bios_arcade(self, sistema, arquivo_esperado, switch_widget):
            install_path = self.entry_path.get()
            use_custom = self.switch_custom_paths.get() == 1 if hasattr(self, 'switch_custom_paths') else False
            custom_bios_path = self.entry_bios_path.get() if use_custom else ""
            target_dir = custom_bios_path if custom_bios_path else os.path.join(install_path, "data")
            os.makedirs(target_dir, exist_ok=True)
            
            caminho_final = os.path.join(target_dir, arquivo_esperado)

            if switch_widget.get() == 1:
                resposta = mb.askyesno("Instalar BIOS", f"Deseja procurar e instalar a BIOS do sistema {sistema} agora?", parent=self)
                if resposta:
                    arquivo = ctk.filedialog.askopenfilename(title=f"Selecione a BIOS do {sistema} (.zip ou avulso)", filetypes=[("BIOS / ZIP", "*.zip *.bin *.rom *.ic27"), ("All files", "*.*")])
                    if arquivo:
                        try:
                            if arquivo.lower().endswith(".zip"):
                                shutil.copy2(arquivo, caminho_final)
                            else:
                                # Empacota o arquivo avulso num ZIP com o nome correto para o Flycast reconhecer!
                                with zipfile.ZipFile(caminho_final, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                    zipf.write(arquivo, os.path.basename(arquivo))
                            mb.showinfo("Sucesso", f"A BIOS do {sistema} foi instalada com sucesso em:\n{caminho_final}", parent=self)
                            self.log(f"🗄️ BIOS {sistema} instalada em: {caminho_final}")
                        except Exception as e:
                            mb.showerror("Erro", f"Falha ao instalar a BIOS: {e}", parent=self)
                            switch_widget.deselect()
                    else:
                        switch_widget.deselect()
                else:
                    switch_widget.deselect()
            else:
                if os.path.exists(caminho_final):
                    resposta = mb.askyesno("Remover BIOS", f"Deseja excluir a BIOS do {sistema} do emulador?", parent=self)
                    if resposta:
                        try:
                            os.remove(caminho_final)
                            mb.showinfo("Removido", f"A BIOS do {sistema} foi removida.", parent=self)
                            self.log(f"🗑️ BIOS {sistema} removida.")
                        except Exception as e:
                            mb.showerror("Erro", f"Falha ao remover a BIOS: {e}", parent=self)
                            switch_widget.select()
                    else:
                        switch_widget.select()


        def verificar_versao_em_background(self, path, branch):
            def rotina():
                self.lbl_emulador_status.configure(text=self._("emu_status_checking"), text_color="cyan")
                self.btn_atualizar.configure(text=self._("btn_verify"))
                version_file = os.path.join(path, "version.txt")
                local_version = ""
                if os.path.exists(version_file):
                    with open(version_file, "r") as f:
                        local_version = f.read().strip()
                if not local_version:
                    self.lbl_emulador_status.configure(text=self._("emu_status_outdated"), text_color="#FFD700")
                    self.btn_atualizar.configure(text=f"🚀 {self._('btn_update_act')}")
                    return

                remote_version = None
                agora = time.time()
                
                ultimo_check = self.config_atual.get("last_github_check_time", 0)
                versao_cache = self.config_atual.get("last_github_version", "")
                branch_cache = self.config_atual.get("last_github_branch", "")
                
                if versao_cache and branch_cache == branch and (agora - ultimo_check) < 1800:
                    remote_version = versao_cache
                    self.log(f"⚡ GitHub API: Usando versão em cache ({remote_version}) para economizar requisições.")
                else:
                    try:
                        headers_api = {'User-Agent': f'FlycastUpdater/{VERSION}'}
                        
                        token = self.config_atual.get("github_token", "")
                        if token:
                            headers_api['Authorization'] = f'token {token}'

                        if branch == 'master':
                            api_url = "https://api.github.com/repos/flyinghead/flycast/releases/latest"
                            req = urllib.request.Request(api_url, headers=headers_api)
                            with urllib.request.urlopen(req, timeout=5) as response:
                                release = json.loads(response.read().decode('utf-8'))
                                remote_version = release.get("tag_name")
                        else:
                            api_url = "https://api.github.com/repos/flyinghead/flycast/commits?sha=dev&per_page=1"
                            req = urllib.request.Request(api_url, headers=headers_api)
                            with urllib.request.urlopen(req, timeout=5) as response:
                                commits = json.loads(response.read().decode('utf-8'))
                                if commits: remote_version = commits[0]["sha"]
                                
                        if remote_version:
                            self.config_atual["last_github_check_time"] = agora
                            self.config_atual["last_github_version"] = remote_version
                            self.config_atual["last_github_branch"] = branch
                            self.salvar_estado_atual()
                            
                    except Exception as e:
                        erro_msg = str(e)
                        self.log(f"❌ Erro ao consultar API do GitHub: {erro_msg}")
                        
                        if "403" in erro_msg:
                            texto_erro = "API em Espera (403)"
                        else:
                            texto_erro = self._("emu_status_offline")
                            
                        self.lbl_emulador_status.configure(text=texto_erro, text_color="#FFD700")
                        
                        if os.path.exists(os.path.join(path, "flycast.exe")):
                            self.btn_atualizar.configure(text=f"🚀 {self._('btn_play')}")
                        else:
                            self.btn_atualizar.configure(text=f"🚀 {self._('btn_install_act')}")
                        return

                if remote_version and (local_version == remote_version or local_version.startswith(remote_version)):
                    self.lbl_emulador_status.configure(text=self._("emu_status_updated"), text_color="#00FF7F")
                    self.btn_atualizar.configure(text=f"🚀 {self._('btn_play')}")
                else:
                    self.lbl_emulador_status.configure(text=self._("emu_status_outdated"), text_color="#FFD700")
                    self.btn_atualizar.configure(text=f"🚀 {self._('btn_update_act')}")

            threading.Thread(target=rotina, daemon=True).start()

        def atualizar_status_diretorio(self, path):
            if not path or not os.path.exists(path):
                self.lbl_bios.configure(text=self._("bios_error"), text_color="#FF4C4C")
                self.lbl_emulador_status.configure(text=self._("emu_status_error"), text_color="#FF4C4C")
                self.btn_rollback.configure(state="disabled")
                self.btn_atualizar.configure(text=f"🚀 {self._('btn_install_act')}")
                return

            # --- ESTRUTURA DE PASTAS AUTOMÁTICA (UX) ---
            try:
                os.makedirs(os.path.join(path, "media", "sfx"), exist_ok=True)
                os.makedirs(os.path.join(path, "media", "snaps"), exist_ok=True)
                os.makedirs(os.path.join(path, "media", "music"), exist_ok=True)
            except Exception: pass
                
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
                            if not custom_bios_path: custom_bios_path = None
                        break
                    except: pass

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
                self.lbl_bios.configure(text=self._("bios_ok"), text_color="#00FF7F")
            elif custom_bios_path and boot_custom and flash_custom:
                self.lbl_bios.configure(text=self._("bios_custom"), text_color="#00FF7F")
            elif boot_root and flash_root:
                self.lbl_bios.configure(text=self._("bios_wrong"), text_color="#FFD700")
                self.after(500, lambda: self.resolver_bios_mal_posicionada(path))
            else:
                self.lbl_bios.configure(text=self._("bios_missing"), text_color="#FF4C4C")
                has_boot = boot_data or (custom_bios_path and boot_custom)
                has_flash = flash_data or (custom_bios_path and flash_custom)
                self.after(500, lambda p=path, cb=custom_bios_path, hb=has_boot, hf=has_flash: self.tratar_bios_ausente(p, cb, hb, hf))

            flycast_exe = os.path.join(path, "flycast.exe")
            if os.path.exists(flycast_exe):
                self.btn_atualizar.configure(text=self._("btn_verify"))
                self.verificar_versao_em_background(path, self.branch_var.get())
            else:
                self.lbl_emulador_status.configure(text=self._("emu_status_missing"), text_color="#FF4C4C")
                self.btn_atualizar.configure(text=f"🚀 {self._('btn_install_act')}")

            backup_path = os.path.join(path, "flycast_backup.zip")
            if os.path.exists(backup_path): self.btn_rollback.configure(state="normal")
            else: self.btn_rollback.configure(state="disabled")

            if hasattr(self, 'switch_naomi'):
                target_dir = custom_bios_path if custom_bios_path and os.path.isabs(custom_bios_path) else (os.path.join(path, custom_bios_path) if custom_bios_path else os.path.join(path, "data"))
                
                if os.path.exists(os.path.join(target_dir, "naomi.zip")): self.switch_naomi.select()
                else: self.switch_naomi.deselect()
                
                if os.path.exists(os.path.join(target_dir, "naomi2.zip")): self.switch_naomi2.select()
                else: self.switch_naomi2.deselect()
                
                if os.path.exists(os.path.join(target_dir, "awbios.zip")): self.switch_atomiswave.select()
                else: self.switch_atomiswave.deselect()

        def escolher_diretorio(self):
            dir_escolhido = ctk.filedialog.askdirectory()
            if dir_escolhido:
                dir_escolhido = os.path.normpath(dir_escolhido)
                self.entry_path.configure(state="normal")
                self.entry_path.delete(0, 'end')
                self.entry_path.insert(0, dir_escolhido)
                self.entry_path.configure(state="readonly")
                self.bios_prompt_done = False 
                self.atualizar_status_diretorio(dir_escolhido)
                self.carregar_dados_atuais_emu_cfg()

        def criar_atalho_desktop_limpo(self):
            try:
                exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
                trabalho_dir = os.path.dirname(exe_path)
                
                # Script nativo do Windows (WScript.Shell) executado via PowerShell para criar o atalho sem argumentos indesejados
                ps_script = f'''
                $WshShell = New-Object -ComObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut("$([Environment]::GetFolderPath('Desktop'))\\Flycast Updater.lnk")
                $Shortcut.TargetPath = "{exe_path}"
                $Shortcut.WorkingDirectory = "{trabalho_dir}"
                $Shortcut.Description = "Flycast Updater - Big Blue"
                $Shortcut.Save()
                '''
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.run(['powershell', '-NoProfile', '-Command', ps_script], startupinfo=startupinfo, capture_output=True)
                self.log("🖥️ Atalho limpo criado na Área de Trabalho com sucesso (sem -nogui).")
            except Exception as e:
                self.log(f"❌ Erro ao criar atalho na Área de Trabalho: {e}")

        def abrir_janela_ajuda(self):
            win_ajuda = ctk.CTkToplevel(self)
            win_ajuda.title(self._("msg_about_title"))
            win_ajuda.geometry("550x550")
            win_ajuda.attributes("-topmost", True)
            texto_ajuda = self._("msg_about_desc", version=VERSION)
            lbl_texto = ctk.CTkLabel(win_ajuda, text=texto_ajuda, justify="left", font=ctk.CTkFont(size=12))
            lbl_texto.pack(padx=20, pady=20, fill="both", expand=True)

        def abrir_ajuda_api_key(self):
            win_api = ctk.CTkToplevel(self)
            win_api.title(self._("msg_api_title"))
            win_api.geometry("500x320")
            win_api.attributes("-topmost", True)
            texto = self._("msg_api_desc")
            lbl_texto = ctk.CTkLabel(win_api, text=texto, justify="left", font=ctk.CTkFont(size=13), wraplength=460)
            lbl_texto.pack(padx=20, pady=(20, 10), fill="both", expand=True)
            btn_link = ctk.CTkButton(win_api, text=self._("btn_api_link"), width=200, height=35, fg_color="#228B22", hover_color="#006400", font=ctk.CTkFont(weight="bold"), command=lambda: webbrowser.open("https://retroachievements.org/controlpanel.php"))
            btn_link.pack(pady=(0, 20))

        def preparar_motor(self, acao):
            texto_atual = self.btn_atualizar.cget("text")
            self.btn_atualizar.configure(state="disabled")
            self.btn_rollback.configure(state="disabled")
            
            if acao == "atualizar": 
                if self._("btn_play") in texto_atual: 
                    self.btn_atualizar.configure(text=self._("btn_starting"))
                    acao = "jogar"  # Altera a ação interna para Fast Boot
                else: 
                    self.btn_atualizar.configure(text=self._("btn_processing"))
            else: 
                self.btn_rollback.configure(text=self._("btn_reverting"))

            self.progressbar.pack(pady=(2, 0))
            self.label_status.pack(pady=(2, 5))
            threading.Thread(target=self.rodar_motor, args=(acao,), daemon=True).start()

        def rodar_motor(self, acao):
            terminal_original = sys.stdout
            sys.stdout = ConsoleRedirector(self)
            try:
                install_path = self.entry_path.get()

                # --- NOVO: FAST BOOT OFFLINE ---
                if acao == "jogar":
                    flycast_exe = os.path.join(install_path, "flycast.exe")
                    if os.path.exists(flycast_exe):
                        self.log("🚀 Iniciando Flycast diretamente (Fast Boot)...")
                        usar_cheats = self.switch_cheats.get() == 1 if hasattr(self, 'switch_cheats') else False
                        atualizar_emu_cfg(install_path, cheat_enable=usar_cheats)
                        
                        self.withdraw()
                        subprocess.Popen([flycast_exe], cwd=install_path)
                        self.after(2000, self.destroy)
                    return
                # ---------------------------------

                if getattr(sys, 'frozen', False) and acao != "rollback":
                    if verificar_atualizacao_updater(install_path, modo_gui=True, app_gui=self): return 

                branch_escolhida = self.branch_var.get()
                criar_startup = self.switch_startup.get() == 1
                
                cloud_escolhida = self.cloud_var.get()
                cloud_prov, cloud_path = None, None
                
                if cloud_escolhida == "gdrive" and cloud_saves:
                    cloud_prov, cloud_path = "gdrive", cloud_saves.get_gdrive_path()
                elif cloud_escolhida == "onedrive" and cloud_saves:
                    cloud_prov, cloud_path = "onedrive", cloud_saves.get_onedrive_path()

                self.salvar_estado_atual()

                import update_flycast
                update_flycast.SCRIPT_VERSION = f"{VERSION} (GUI)"
                update_flycast.args_lower = ['-rollback'] if acao == "rollback" else []
                update_flycast.INSTALL_DIR = install_path
                update_flycast.SHOULD_CREATE_SHORTCUT = False
                update_flycast.SHOULD_CREATE_STARTUP = criar_startup
                update_flycast.CLOUD_PROVIDER = cloud_prov
                update_flycast.CLOUD_PATH = cloud_path
                update_flycast.VERSION_FILE = os.path.join(install_path, "version.txt")
                update_flycast.LOG_FILE = os.path.join(install_path, "flycast_updater.log")
                update_flycast.get_user_preference = lambda: branch_escolhida
                update_flycast.BACKUP_MAPPINGS = self.switch_mappings.get() == 1
                
                update_flycast.main()
                self.limpar_backups_antigos()
                self.after(2000, self.destroy)
            except SystemExit:
                self.limpar_backups_antigos()
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
    salvar_configuracao({
        "branch": branch_choice, "create_shortcut": create_desktop, "create_startup": create_startup,
        "install_path": install_path, "cloud_provider": cloud_prov, "cloud_path": cloud_path, "setup_completed": True
    })
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

    update_flycast.BACKUP_MAPPINGS = config.get("backup_mappings", False)

    update_flycast.main()

if __name__ == "__main__":
    # --- INTERCEPTADOR STEAM (SMART LAUNCHER) ---
    if getattr(sys, 'frozen', False):
        exe_name = os.path.basename(sys.executable)
        if "[Flycast]" in exe_name:
            map_file = os.path.join(os.path.dirname(sys.executable), "steam_mapping.json")
            if os.path.exists(map_file):
                try:
                    with open(map_file, "r", encoding="utf-8") as f:
                        mapping = json.load(f)
                    if exe_name in mapping:
                        fly_exe = mapping[exe_name]["flycast"]
                        rom_path = mapping[exe_name]["rom"]
                        
                        # Injeta o jogo e bloqueia o processo até o emulador fechar (para manter a Steam engatilhada e o Overlay vivo)
                        subprocess.run([fly_exe, rom_path], cwd=os.path.dirname(fly_exe))
                except Exception: pass
            sys.exit(0) # Fecha silenciosamente após o jogo terminar
    # --------------------------------------------

    args_lower = [arg.lower() for arg in sys.argv[1:]]
    gatilhos_cli = ['-nogui', '-silent', '-rollback', '-backup', '-dev', '-master', '-help', '-h', '--help', '-reset', '-gdrive', '-onedrive']
    
    config = carregar_configuracao()
    if config.get("nogui", False) and "-nogui" not in args_lower and "-reset" not in args_lower:
        args_lower.append("-nogui")

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