import os, sys, json, subprocess, time, urllib.request, urllib.parse, datetime, threading, configparser, zipfile, shutil, re
import tkinter as tk 
import tkinter.messagebox as mb
import webbrowser 
from idiomas import TRANSLATIONS

try: import cloud_saves
except ImportError: cloud_saves = None

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError: HAS_PIL = False

# ==========================================
# Flycast Updater - Launcher v5.1 (Official API)
# Desenvolvido por DaniboySan & Geminix
# ==========================================

VERSION = "5.1"
CONFIG_FILE = "config.json"
REPO_UPDATER = "dsantanna/flycast_updater"

PERFIS_CONTROLES = {
    "Xbox (360 / One / Series)": {"arquivo": "XInput Controller.cfg", "conteudo": "[emulator]\nmapping_name = XInput Controller\n\n[dreamcast]\nbtn_a = 0\nbtn_b = 1\nbtn_x = 2\nbtn_y = 3\nbtn_start = 7\nbtn_dpad1_up = 11\nbtn_dpad1_down = 12\nbtn_dpad1_left = 13\nbtn_dpad1_right = 14\naxis_x = 0\naxis_y = 1\naxis_trigger_left = 4\naxis_trigger_right = 5\n"},
    "PlayStation (PS4 / PS5)": {"arquivo": "PS4 Controller.cfg", "conteudo": "[emulator]\nmapping_name = PS4 Controller\n\n[dreamcast]\nbtn_a = 1\nbtn_b = 2\nbtn_x = 0\nbtn_y = 3\nbtn_start = 9\nbtn_dpad1_up = 11\nbtn_dpad1_down = 12\nbtn_dpad1_left = 13\nbtn_dpad1_right = 14\naxis_x = 0\naxis_y = 1\naxis_trigger_left = 4\naxis_trigger_right = 5\n"},
    "8BitDo (Pro 2 / Ultimate / SN30)": {"arquivo": "8BitDo Controller.cfg", "conteudo": "[emulator]\nmapping_name = 8BitDo Controller\n\n[dreamcast]\nbtn_a = 1\nbtn_b = 0\nbtn_x = 3\nbtn_y = 2\nbtn_start = 11\nbtn_dpad1_up = 15\nbtn_dpad1_down = 16\nbtn_dpad1_left = 17\nbtn_dpad1_right = 18\naxis_x = 0\naxis_y = 1\naxis_trigger_left = 4\naxis_trigger_right = 5\n"}
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

def atualizar_emu_cfg(install_path, roms_path=None, ra_enabled=None, ra_user=None, ra_pass=None, ra_hardcore=None, 
                      vmu_individual=None, fetch_boxart=None, vga_cable=None, discord_presence=None,
                      show_osd_vmu=None, vmu_sound=None, bios_path=None, vmu_path=None, state_path=None, save_path=None,
                      vid_api=None, vid_res=None, vid_full=None, vid_int=None, vid_lin=None, vid_vsync=None,
                      streamer_mode=None, cheat_enable=None):
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
    if show_osd_vmu is not None: config.set('config', 'ShowOsdVmu', 'yes' if show_osd_vmu else 'no')
    if streamer_mode is not None: config.set('config', 'OsdMessages', 'no' if streamer_mode else 'yes')
    if cheat_enable is not None: config.set('config', 'Cheat', 'yes' if cheat_enable else 'no')

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
    def update_text(self, new_text): self.text = new_text
    def show_tooltip(self, event=None):
        try:
            if self.widget.cget("state") == "disabled" and "Rollback" not in self.text and "não detectado" not in self.text: return 
        except Exception: pass
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
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
            
            self.title(f"🌀 Flycast Updater - v{VERSION}")
            self.geometry("800x980") 
            self.minsize(800, 600)
            self.resizable(True, True) 

            try: self.state('zoomed')
            except Exception: self.attributes('-zoomed', True)
            
            self.token_ra_salvo = "" 
            self.bios_prompt_done = False
            self.fabricante_gpu = None
            self.rom_paths_list = []
            self.ra_labels = {} 

            self.frame_header = ctk.CTkFrame(self, fg_color="transparent")
            self.frame_header.pack(fill="x", padx=20, pady=(15, 0))
            self.label_titulo = ctk.CTkLabel(self.frame_header, text="Flycast Updater", font=ctk.CTkFont(size=24, weight="bold"))
            self.label_titulo.pack(side="top")
            self.label_sub = ctk.CTkLabel(self.frame_header, text=self._("title_sub"), text_color="gray")
            self.label_sub.pack(side="top", pady=(0, 10))

            self.frame_top_right = ctk.CTkFrame(self.frame_header, fg_color="transparent")
            self.frame_top_right.place(relx=1.0, rely=0.0, anchor="ne")
            self.lang_map = {
                "Português (BR)": "pt",
                "English (US)": "en",
                "Español (ES)": "es",
                "Français (FR)": "fr",
                "Deutsch (DE)": "de",
                "Italiano (IT)": "it",
                "日本語 (JA)": "ja",
                "简体中文 (ZH)": "zh",
                "Русский (RU)": "ru",
                "العربية (AR)": "ar",
                "हिन्दी (HI)": "hi",
                "한국어 (KO)": "ko",
                "Polski (PL)": "pl",
                "Nederlands (NL)": "nl",
                "Türkçe (TR)": "tr",
                "Svenska (SV)": "sv",
                "Bahasa Indonesia (ID)": "id",
                "ภาษาไทย (TH)": "th",
                "Tiếng Việt (VI)": "vi",
                "Ελληνικά (EL)": "el"
            }
            self.rev_lang_map = {v: k for k, v in self.lang_map.items()}

            self.combo_lang = ctk.CTkComboBox(self.frame_top_right, values=list(self.lang_map.keys()), width=95, height=28, command=self.mudar_idioma)
            self.combo_lang.pack(side="left", padx=5)
            self.combo_lang.set(self.rev_lang_map.get(self.lang, "PT-BR"))
            self.btn_help = ctk.CTkButton(self.frame_top_right, text=self._("btn_help"), width=70, height=28, fg_color="#444", hover_color="#666", command=self.abrir_janela_ajuda)
            self.btn_help.pack(side="left")

            self.tabview = ctk.CTkTabview(self, width=620, height=680)
            self.tabview.pack(pady=5, padx=15, fill="both", expand=True)
            self.tab_atualizador = self.tabview.add(self._("tab_cloud", default="🚀 Atualização"))
            self.tab_jogos = self.tabview.add(self._("tab_games", default="🕹️ Jogos")) 
            self.tab_config = self.tabview.add(self._("tab_emu", default="⚙️ Emulador"))
            self.tab_qol = self.tabview.add(self._("tab_qol", default="🌟 QoL"))
            self.tab_video = self.tabview.add(self._("tab_vid", default="🖥️ Vídeo"))
            self.tab_controles = self.tabview.add(self._("tab_ctrl", default="🎮 Controles"))
            self.tab_saves = self.tabview.add(self._("tab_saves", default="🔄 Saves"))
            self.tab_logs = self.tabview.add(self._("tab_logs", default="📝 Logs"))

            self.construir_aba_nuvem()
            self.construir_aba_jogos()   
            self.construir_aba_emulador()
            self.construir_aba_qol()
            self.construir_aba_video()
            self.construir_aba_controles()
            self.construir_aba_saves()
            self.construir_aba_logs()

            caminho_inicial = os.path.normpath(self.config_atual.get("install_path", os.getcwd()))
            self.entry_path.configure(state="normal")
            self.entry_path.delete(0, 'end')
            self.entry_path.insert(0, caminho_inicial)
            self.entry_path.configure(state="readonly")
            
            self.carregar_dados_atuais_emu_cfg()

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
            
            self.lbl_rodape = ctk.CTkLabel(self, text="Desenvolvido por DaniboySan & Geminix", text_color="#1E90FF", cursor="hand2", font=ctk.CTkFont(size=11, underline=True))
            self.lbl_rodape.pack(side="bottom", pady=(0, 5))
            self.lbl_rodape.bind("<Button-1>", lambda e: webbrowser.open(f"https://github.com/{REPO_UPDATER}"))

            self.log(f"🚀 Flycast Updater v{VERSION} iniciado.")
            self.atualizar_status_diretorio(self.entry_path.get())
            self.after(200, self.verificar_primeiro_acesso)
            self.after(800, self.carregar_gpus) 
            self.after(1000, self.escanear_jogos) 

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
            self.switch_desktop.configure(text=self._("sw_desk"))
            self.switch_startup.configure(text=self._("sw_start"))
            self.switch_nogui.configure(text=self._("sw_nogui"))
            self.btn_reconfig.configure(text=self._("btn_reconfig"))
            self.label_games_title.configure(text=self._("lbl_games_title"))
            self.label_games_desc.configure(text=self._("lbl_games_desc"))
            self.switch_cheats.configure(text=self._("sw_cheats"))
            self.btn_scan_games.configure(text=self._("btn_scan_games"))
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
            self.frame_branches.columnconfigure(0, weight=1)
            self.frame_branches.columnconfigure(1, weight=1)

            self.rb_dev = ctk.CTkRadioButton(self.frame_branches, text="Branch Dev", font=ctk.CTkFont(weight="bold"), variable=self.branch_var, value="dev", command=self.ao_trocar_branch)
            self.rb_dev.grid(row=0, column=0, sticky="w", padx=(0, 10))
            self.lbl_dev_desc = ctk.CTkLabel(self.frame_branches, text=self._("rb_dev_desc"), text_color="gray", font=ctk.CTkFont(size=11), justify="left")
            self.lbl_dev_desc.grid(row=1, column=0, sticky="nw", padx=(28, 0))

            self.rb_master = ctk.CTkRadioButton(self.frame_branches, text="Branch Master", font=ctk.CTkFont(weight="bold"), variable=self.branch_var, value="master", command=self.ao_trocar_branch)
            self.rb_master.grid(row=0, column=1, sticky="w", padx=(0, 10))
            self.lbl_master_desc = ctk.CTkLabel(self.frame_branches, text=self._("rb_master_desc"), text_color="gray", font=ctk.CTkFont(size=11), justify="left")
            self.lbl_master_desc.grid(row=1, column=1, sticky="nw", padx=(28, 0)) 

            self.switch_desktop = ctk.CTkSwitch(self.tab_atualizador, text=self._("sw_desk"))
            self.switch_desktop.pack(anchor="w", padx=10, pady=(15, 5))
            if self.config_atual.get("create_shortcut", False): self.switch_desktop.select()

            self.switch_startup = ctk.CTkSwitch(self.tab_atualizador, text=self._("sw_start"))
            self.switch_startup.pack(anchor="w", padx=10, pady=5)
            if self.config_atual.get("create_startup", False): self.switch_startup.select()

            self.switch_nogui = ctk.CTkSwitch(self.tab_atualizador, text=self._("sw_nogui"))
            self.switch_nogui.pack(anchor="w", padx=10, pady=5)
            if self.config_atual.get("nogui", False): self.switch_nogui.select()

            self.btn_reconfig = ctk.CTkButton(self.tab_atualizador, text=self._("btn_reconfig"), width=220, height=28, fg_color="#333", hover_color="#555", command=lambda: self.tabview.set(self._("tab_emu")))
            self.btn_reconfig.pack(anchor="w", padx=10, pady=(15, 5))

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

        def ao_trocar_streamer(self):
            if getattr(self, "switch_streamer", ctk.BooleanVar(value=False)).get() == 1:
                self.switch_osd_vmu.deselect()
                self.switch_vmu_sound.deselect()
                self.log("🎥 Modo Streamer ativado: OSD e sons desativados.")

        def ao_trocar_cheats(self):
            if self.switch_cheats.get() == 1:
                mb.showwarning("RetroAchievements", self._("msg_cheats_ra"), parent=self)

        def construir_aba_jogos(self):
            self.label_games_title = ctk.CTkLabel(self.tab_jogos, text=self._("lbl_games_title"), font=ctk.CTkFont(size=16, weight="bold"))
            self.label_games_title.pack(anchor="w", padx=10, pady=(10, 2))
            self.label_games_desc = ctk.CTkLabel(self.tab_jogos, text=self._("lbl_games_desc"), text_color="gray", justify="left")
            self.label_games_desc.pack(anchor="w", padx=10, pady=(0, 10))
            
            self.frame_games_top = ctk.CTkFrame(self.tab_jogos, fg_color="transparent")
            self.frame_games_top.pack(fill="x", padx=10, pady=5)
            self.switch_cheats = ctk.CTkSwitch(self.frame_games_top, text=self._("sw_cheats"), command=self.ao_trocar_cheats)
            self.switch_cheats.pack(side="left")
            self.btn_scan_games = ctk.CTkButton(self.frame_games_top, text=self._("btn_scan_games"), width=150, command=self.escanear_jogos)
            self.btn_scan_games.pack(side="right")
            
            self.frame_grid_games = ctk.CTkScrollableFrame(self.tab_jogos, width=580, height=450, corner_radius=10)
            self.frame_grid_games.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        def baixar_capa_libretro(self, nome_jogo, boxart_dir, capa_lbl):
            nome_busca = nome_jogo.replace("_", " ")
            url_repo = f"https://raw.githubusercontent.com/libretro/libretro-thumbnails/master/Sega%20-%20Dreamcast/Named_Boxarts/{urllib.parse.quote(nome_busca)}.png"
            destino = os.path.join(boxart_dir, f"{nome_jogo}.png")
            try:
                os.makedirs(boxart_dir, exist_ok=True)
                req = urllib.request.Request(url_repo, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as response, open(destino, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                if HAS_PIL and os.path.exists(destino):
                    pil_img = Image.open(destino).resize((150, 150), Image.Resampling.LANCZOS)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(150, 150))
                    self.after(0, lambda: capa_lbl.configure(image=ctk_img, text=""))
                    self.log(f"🖼️ Auto-Scraper: Capa baixada com sucesso!")
            except Exception:
                nome_limpo2 = re.sub(r'\(.*?\)|\[.*?\]', '', nome_busca).strip()
                if nome_limpo2 and nome_limpo2 != nome_busca:
                    url2 = f"https://raw.githubusercontent.com/libretro/libretro-thumbnails/master/Sega%20-%20Dreamcast/Named_Boxarts/{urllib.parse.quote(nome_limpo2)}.png"
                    try:
                        req = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=3) as response, open(destino, 'wb') as out_file:
                            shutil.copyfileobj(response, out_file)
                        if HAS_PIL and os.path.exists(destino):
                            pil_img = Image.open(destino).resize((150, 150), Image.Resampling.LANCZOS)
                            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(150, 150))
                            self.after(0, lambda: capa_lbl.configure(image=ctk_img, text=""))
                    except Exception: self.after(0, lambda: capa_lbl.configure(text="🎮\nFLYCAST"))
                else: self.after(0, lambda: capa_lbl.configure(text="🎮\nFLYCAST"))

        def sincronizar_retroachievements(self):
            usuario = self.entry_ra_user.get().strip()
            api_key = self.config_atual.get("ra_api_key", "").strip()
            is_hardcore = getattr(self, "switch_hardcore", ctk.BooleanVar(value=False)).get() == 1
            tag_modo = " (Hardcore)" if is_hardcore else ""

            # NOVO NOME: RAlocal.db
            db_path = os.path.join(self.entry_path.get(), "RAlocal.db")
            ra_db = {}
            if os.path.exists(db_path):
                try:
                    with open(db_path, "r", encoding="utf-8") as f: ra_db = json.load(f)
                except Exception: pass

            user_db = ra_db.setdefault(usuario, {})

            if not usuario or not api_key:
                self.log("⚠️ RA Sync: Web API Key não configurada. Lendo apenas cache local 'RAlocal.db'.")
                for base_name, (lbl, nome_exib) in self.ra_labels.items():
                    data = user_db.get(nome_exib)
                    if data:
                        pts = data.get('score_hc', '0') if is_hardcore else data.get('score', '0')
                        tot = data.get('total_score', '0')
                        texto = f"🏆 {pts}/{tot} pts{tag_modo}"
                        cor = "gray" if pts == "0" else "#00FF7F"
                    else:
                        texto = f"🏆 Não Iniciado{tag_modo}"
                        cor = "gray"
                    try: self.after(0, lambda l=lbl, t=texto, c=cor: l.configure(text=t, text_color=c))
                    except Exception: pass
                return

            self.log(f"🌐 RA Sync: Conectando à API Oficial do RetroAchievements para '{usuario}'...")
            try:
                url = f"https://retroachievements.org/API/API_GetUserRecentlyPlayedGames.php?z={urllib.parse.quote(usuario)}&y={api_key}&u={urllib.parse.quote(usuario)}&c=50"
                req = urllib.request.Request(url, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    json_data = json.loads(response.read().decode('utf-8'))
                
                self.log(f"✔️ RA Sync: Dados recebidos com sucesso. Atualizando banco de dados completo...")
                atualizou_algo = False
                
                for game in json_data:
                    title = game.get("Title", "")
                    if not title: continue
                    
                    # Salva TUDO no RAlocal.db de forma estruturada e correta
                    achieved = str(game.get("NumAchieved", "0"))
                    achieved_hc = str(game.get("NumAchievedHardcore", "0"))
                    total_ach = str(game.get("NumPossibleAchievements", "0"))
                    
                    score = str(game.get("ScoreAchieved", "0"))
                    score_hc = str(game.get("ScoreAchievedHardcore", "0"))
                    total_score = str(game.get("PossibleScore", "0"))

                    novo_dado = {
                        "achieved": achieved,
                        "achieved_hc": achieved_hc,
                        "total_achievements": total_ach,
                        "score": score,
                        "score_hc": score_hc,
                        "total_score": total_score
                    }
                    
                    if user_db.get(title) != novo_dado:
                        user_db[title] = novo_dado
                        atualizou_algo = True
                        pts_exib = score_hc if is_hardcore else score
                        self.log(f"🎯 RA Sync: Atualizado '{title}': {pts_exib}/{total_score} pts!")

                if atualizou_algo:
                    with open(db_path, "w", encoding="utf-8") as f: json.dump(ra_db, f, indent=4)
                    self.log(f"💾 RA Sync: Banco local 'RAlocal.db' atualizado.")
                else:
                    self.log(f"⚡ RA Sync: Nenhuma alteração nas pontuações.")

                for base_name, (lbl, nome_exib) in self.ra_labels.items():
                    data = user_db.get(nome_exib)
                    if data:
                        pts = data.get('score_hc', '0') if is_hardcore else data.get('score', '0')
                        tot = data.get('total_score', '0')
                        texto = f"🏆 {pts}/{tot} pts{tag_modo}"
                        cor = "gray" if pts == "0" else "#00FF7F"
                    else:
                        texto = f"🏆 Não Iniciado{tag_modo}"
                        cor = "gray"
                    try: self.after(0, lambda l=lbl, t=texto, c=cor: l.configure(text=t, text_color=c))
                    except Exception: pass

            except Exception as e:
                self.log(f"❌ RA Sync [Erro na API Oficial]: {e}")
                self.log(f"♻️ RA Sync: Utilizando dados salvos no cache local 'RAlocal.db'...")
                for base_name, (lbl, nome_exib) in self.ra_labels.items():
                    data = user_db.get(nome_exib)
                    if data:
                        pts = data.get('score_hc', '0') if is_hardcore else data.get('score', '0')
                        tot = data.get('total_score', '0')
                        texto = f"🏆 {pts}/{tot} pts{tag_modo}"
                        cor = "gray" if pts == "0" else "#00FF7F"
                    else:
                        texto = f"🏆 Não Iniciado{tag_modo}"
                        cor = "gray"
                    try: self.after(0, lambda l=lbl, t=texto, c=cor: l.configure(text=t, text_color=c))
                    except Exception: pass

        def monitorar_jogo(self, proc, nome_limpo):
            inicio = time.time()
            proc.wait() 
            fim = time.time()
            jogado_segundos = int(fim - inicio)
            if jogado_segundos > 10:
                playtime_db = self.config_atual.setdefault("playtime", {})
                total_jogado = playtime_db.get(nome_limpo, 0)
                total_jogado += jogado_segundos
                self.config_atual["playtime"][nome_limpo] = total_jogado
                self.salvar_estado_atual()
                self.log(f"⏱️ Playtime Tracker: Tempo atualizado para '{nome_limpo}': +{jogado_segundos}s")
                self.after(0, self.escanear_jogos)

        def lancar_jogo(self, rom_path, base_name=None):
            install_path = self.entry_path.get()
            flycast_exe = os.path.join(install_path, "flycast.exe")
            if not os.path.exists(flycast_exe):
                mb.showerror("Erro", "O emulador Flycast não foi encontrado.", parent=self)
                return
            usar_cheats = self.switch_cheats.get() == 1
            atualizar_emu_cfg(install_path, cheat_enable=usar_cheats)
            self.log(f"🚀 Iniciando jogo: {os.path.basename(rom_path)}")
            try:
                proc = subprocess.Popen([flycast_exe, rom_path], cwd=install_path)
                nome_track = base_name if base_name else os.path.splitext(os.path.basename(rom_path))[0]
                threading.Thread(target=self.monitorar_jogo, args=(proc, nome_track), daemon=True).start()
            except Exception as e:
                mb.showerror("Erro Crítico", f"Falha ao abrir jogo: {e}", parent=self)

        def selecionar_disco(self, base_name, arquivos):
            if len(arquivos) == 1:
                self.lancar_jogo(arquivos[0], base_name)
                return
            top = ctk.CTkToplevel(self)
            top.title(self._("lbl_select_disc"))
            top.geometry("400x300")
            top.attributes("-topmost", True)
            top.grab_set()
            lbl = ctk.CTkLabel(top, text=self._("lbl_choose_disc"), font=ctk.CTkFont(weight="bold"))
            lbl.pack(pady=15)
            frame = ctk.CTkScrollableFrame(top, fg_color="transparent")
            frame.pack(fill="both", expand=True, padx=20, pady=5)
            for arq in sorted(arquivos):
                nome_arq = os.path.basename(arq)
                btn = ctk.CTkButton(frame, text=nome_arq, command=lambda a=arq: [top.destroy(), self.lancar_jogo(a, base_name)])
                btn.pack(pady=5, fill="x")

        def mostrar_info_jogo(self, base_name, nome_exibicao, db_info):
            top = ctk.CTkToplevel(self)
            top.title(self._("lbl_info_title"))
            top.geometry("550x450")
            top.attributes("-topmost", True)
            lbl_nome = ctk.CTkLabel(top, text=nome_exibicao, font=ctk.CTkFont(size=20, weight="bold"))
            lbl_nome.pack(pady=(20, 5), padx=20, anchor="w")
            data_lancamento = db_info.get("release_date", "") if db_info else ""
            overview = db_info.get("overview", "") if db_info else ""
            if not data_lancamento: data_lancamento = self._("lbl_unknown")
            if not overview: overview = self._("msg_no_overview")
            lbl_data = ctk.CTkLabel(top, text=f"{self._('lbl_release')} {data_lancamento}", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
            lbl_data.pack(padx=20, anchor="w")
            txt_desc = ctk.CTkTextbox(top, wrap="word", font=("Segoe UI", 13))
            txt_desc.pack(fill="both", expand=True, padx=20, pady=20)
            txt_desc.insert("1.0", overview)
            txt_desc.configure(state="disabled")

        def escanear_jogos(self):
            for widget in self.frame_grid_games.winfo_children(): widget.destroy()
            self.ra_labels = {} 
            install_path = self.entry_path.get()
            boxart_dir = os.path.join(install_path, "data", "boxart")

            if not self.rom_paths_list:
                lbl = ctk.CTkLabel(self.frame_grid_games, text=self._("msg_no_games", default="Nenhuma pasta configurada."), font=ctk.CTkFont(size=14, slant="italic"), text_color="gray")
                lbl.pack(pady=40)
                return

            extensoes_suportadas = ('.cdi', '.gdi', '.chd', '.cue')
            jogos_fisicos = []
            for path_atual in self.rom_paths_list:
                if not os.path.exists(path_atual): continue
                try:
                    for f in os.listdir(path_atual):
                        if f.lower().endswith(extensoes_suportadas):
                            caminho_arquivo = os.path.join(path_atual, f)
                            if os.path.getsize(caminho_arquivo) > 1024 * 1024: 
                                jogos_fisicos.append((f, path_atual))
                except Exception: pass

            if not jogos_fisicos:
                lbl = ctk.CTkLabel(self.frame_grid_games, text=self._("msg_no_games", default="Nenhum jogo encontrado."), font=ctk.CTkFont(size=14, slant="italic"), text_color="gray")
                lbl.pack(pady=40)
                return

            jogos_agrupados = {}
            padrao_disco = re.compile(r'(?i)\s*[\(\[-]?\s*disc\s*[0-9a-z]+\s*[\)\]]?')
            for jogo, r_path in jogos_fisicos:
                nome_limpo = os.path.splitext(jogo)[0]
                base_name = padrao_disco.sub('', nome_limpo).strip()
                if base_name not in jogos_agrupados: jogos_agrupados[base_name] = []
                jogos_agrupados[base_name].append(os.path.join(r_path, jogo))

            db_path = os.path.join(boxart_dir, "flycast-gamedb.json")
            game_db = {}
            if os.path.exists(db_path):
                try:
                    with open(db_path, "r", encoding="utf-8") as f:
                        for item in json.load(f):
                            if item.get("file_name"):
                                game_db[item["file_name"]] = {"boxart_path": item.get("boxart_path", ""), "name": item.get("name", ""), "overview": item.get("overview", ""), "release_date": item.get("release_date", "")}
                except Exception: pass
            
            screen_width = self.winfo_screenwidth()
            max_cols = max(3, (screen_width - 80) // 190)
            row, col = 0, 0
            playtime_db = self.config_atual.get("playtime", {})
            
            # NOVO: Leitura do banco RAlocal.db com a arquitetura expandida
            usuario = self.entry_ra_user.get().strip()
            db_ra_path = os.path.join(install_path, "RAlocal.db")
            ra_db = {}
            if os.path.exists(db_ra_path):
                try:
                    with open(db_ra_path, "r", encoding="utf-8") as f: ra_db = json.load(f)
                except Exception: pass
            user_db = ra_db.get(usuario, {})
            is_hardcore = getattr(self, "switch_hardcore", ctk.BooleanVar(value=False)).get() == 1
            tag_modo = " (Hardcore)" if is_hardcore else ""

            for base_name in sorted(jogos_agrupados.keys()):
                arquivos_jogo = jogos_agrupados[base_name]
                jogo_ref = os.path.basename(arquivos_jogo[0])
                roms_path_ref = os.path.dirname(arquivos_jogo[0])
                nome_limpo_ref = os.path.splitext(jogo_ref)[0]
                nome_exibicao = base_name
                
                card = ctk.CTkFrame(self.frame_grid_games, width=170, height=275, corner_radius=12, fg_color="#2b2b2b")
                card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
                card.grid_propagate(False) 

                capa_lbl = None
                img_carregada = False
                db_info = game_db.get(jogo_ref)

                if HAS_PIL:
                    caminhos_img = []
                    if db_info and db_info.get("name"): nome_exibicao = db_info["name"]
                    if db_info and db_info.get("boxart_path"): caminhos_img.append(os.path.join(boxart_dir, db_info["boxart_path"]))
                    caminhos_img.extend([os.path.join(boxart_dir, f"{jogo_ref}.png"), os.path.join(boxart_dir, f"{jogo_ref}.jpg"), os.path.join(boxart_dir, f"{nome_limpo_ref}.png"), os.path.join(boxart_dir, f"{nome_limpo_ref}.jpg"), os.path.join(roms_path_ref, f"{nome_limpo_ref}.png"), os.path.join(roms_path_ref, f"{nome_limpo_ref}.jpg")])
                    for img_p in caminhos_img:
                        if os.path.exists(img_p):
                            try:
                                pil_img = Image.open(img_p).resize((150, 150), Image.Resampling.LANCZOS)
                                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(150, 150))
                                capa_lbl = ctk.CTkLabel(card, image=ctk_img, text="")
                                img_carregada = True
                                break
                            except Exception: pass

                if not img_carregada:
                    texto_dl = self._("lbl_downloading_cover", default="🎮\n(Baixando...)") if HAS_PIL else "🎮\nFLYCAST"
                    capa_lbl = ctk.CTkLabel(card, text=texto_dl, width=150, height=150, fg_color="#1a1a1a", corner_radius=8, font=ctk.CTkFont(size=14, weight="bold"))
                    if HAS_PIL: threading.Thread(target=self.baixar_capa_libretro, args=(base_name, boxart_dir, capa_lbl), daemon=True).start()

                capa_lbl.pack(pady=(10, 5), padx=10)
                capa_lbl.bind("<Double-Button-1>", lambda e, b=base_name, a=arquivos_jogo: self.selecionar_disco(b, a))

                nome_exibicao_curto = nome_exibicao[:18] + "..." if len(nome_exibicao) > 18 else nome_exibicao
                lbl_nome = ctk.CTkLabel(card, text=nome_exibicao_curto, font=ctk.CTkFont(size=12, weight="bold"))
                lbl_nome.pack(pady=(0, 2))
                ToolTip(lbl_nome, nome_exibicao)

                # NOVO: Formatação que exibe PONTOS (Score) ao invés de Achievements
                data_ra = user_db.get(nome_exibicao)
                if data_ra:
                    pts = data_ra.get('score_hc', '0') if is_hardcore else data_ra.get('score', '0')
                    tot = data_ra.get('total_score', '0')
                    texto_inicial_ra = f"🏆 {pts}/{tot} pts{tag_modo}"
                    cor_ra = "gray" if pts == "0" else "#00FF7F"
                else:
                    texto_inicial_ra = f"🏆 Buscando..."
                    cor_ra = "#FFD700"

                lbl_ra = ctk.CTkLabel(card, text=texto_inicial_ra, font=ctk.CTkFont(size=10), text_color=cor_ra)
                lbl_ra.pack(pady=(0, 2))
                self.ra_labels[base_name] = (lbl_ra, nome_exibicao)

                total_segundos = playtime_db.get(base_name, 0)
                horas, minutos = total_segundos // 3600, (total_segundos % 3600) // 60
                if horas > 0: str_tempo = f"{horas}h {minutos}m"
                elif minutos > 0: str_tempo = f"{minutos}m"
                else: str_tempo = self._("playtime_new", default="Novo") if total_segundos == 0 else self._("playtime_less_1m", default="< 1m")

                lbl_tempo = ctk.CTkLabel(card, text=f"⏱️ {str_tempo}", font=ctk.CTkFont(size=10), text_color="gray")
                lbl_tempo.pack(pady=(0, 2))

                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(pady=(2, 10))
                btn_play = ctk.CTkButton(btn_frame, text="▶️ Jogar", width=85, height=26, fg_color="#4169E1", hover_color="#1E90FF", command=lambda b=base_name, a=arquivos_jogo: self.selecionar_disco(b, a))
                btn_play.pack(side="left", padx=(0, 5))
                btn_info = ctk.CTkButton(btn_frame, text="ℹ️", width=26, height=26, fg_color="#555555", hover_color="#777777", command=lambda b=base_name, n=nome_exibicao, d=db_info: self.mostrar_info_jogo(b, n, d))
                btn_info.pack(side="left")

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            if self.ra_labels: threading.Thread(target=self.sincronizar_retroachievements, daemon=True).start()
        
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
                    self.escanear_jogos()

        def remover_diretorio_roms(self, path):
            if path in self.rom_paths_list:
                self.rom_paths_list.remove(path)
                self.atualizar_lista_ui_roms()
                self.log(f"🗑️ Pasta removida: {path}")
                self.escanear_jogos()

        def construir_aba_emulador(self):
            self.label_roms_title = ctk.CTkLabel(self.tab_config, text=self._("lbl_roms"), font=ctk.CTkFont(weight="bold"))
            self.label_roms_title.pack(anchor="w", padx=10, pady=(5, 2))

            self.frame_roms_list = ctk.CTkScrollableFrame(self.tab_config, height=70, fg_color="#1a1a1a")
            self.frame_roms_list.pack(fill="x", padx=10, pady=(0, 5))
            
            self.btn_add_rom = ctk.CTkButton(self.tab_config, text=self._("btn_add_path"), width=150, fg_color="#228B22", hover_color="#006400", command=self.adicionar_diretorio_roms)
            self.btn_add_rom.pack(anchor="w", padx=10, pady=(0, 10))

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
            self.lbl_save_path.grid(row=3, column=0, sticky="w", padx=(10, 5), pady=(2, 10))
            self.entry_save_path = ctk.CTkEntry(self.frame_custom_paths, state="readonly", height=24)
            self.entry_save_path.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 10))
            self.btn_save_path = ctk.CTkButton(self.frame_custom_paths, text=self._("btn_browse"), width=50, height=24, command=lambda: self.escolher_dir_custom_path(self.entry_save_path))
            self.btn_save_path.grid(row=3, column=2, padx=(5, 10), pady=(2, 10))

            self.frame_divisor = ctk.CTkFrame(self.tab_config, height=2, fg_color="#444")
            self.frame_divisor.pack(fill="x", padx=10, pady=(5, 5))

            self.label_ra_title = ctk.CTkLabel(self.tab_config, text=self._("lbl_ra"), font=ctk.CTkFont(weight="bold"))
            self.label_ra_title.pack(anchor="w", padx=10, pady=(5, 2))

            self.switch_ra = ctk.CTkSwitch(self.tab_config, text=self._("sw_ra"))
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

            self.switch_hardcore = ctk.CTkSwitch(self.tab_config, text=self._("sw_hard"))
            self.switch_hardcore.pack(anchor="w", padx=10, pady=(5, 2))
            
            self.lbl_hc_desc = ctk.CTkLabel(self.tab_config, text=self._("lbl_hc_desc"), text_color="gray", font=ctk.CTkFont(size=11), justify="left")
            self.lbl_hc_desc.pack(anchor="w", padx=45, pady=(0, 5))

            self.frame_divisor2 = ctk.CTkFrame(self.tab_config, height=2, fg_color="#444")
            self.frame_divisor2.pack(fill="x", padx=10, pady=(5, 5))

            self.btn_salvar_config_emu = ctk.CTkButton(self.tab_config, text=self._("btn_save_emu"), width=280, height=35, font=ctk.CTkFont(weight="bold"), command=self.salvar_configuracoes_emulador)
            self.btn_salvar_config_emu.pack(anchor="center", pady=(10, 10))

        def construir_aba_qol(self):
            self.label_qol_title = ctk.CTkLabel(self.tab_qol, text=self._("lbl_qol"), font=ctk.CTkFont(size=16, weight="bold"))
            self.label_qol_title.pack(anchor="w", padx=10, pady=(15, 5))

            self.frame_qol = ctk.CTkFrame(self.tab_qol, fg_color="transparent")
            self.frame_qol.pack(fill="x", padx=10)
            self.frame_qol.columnconfigure(0, weight=1)
            self.frame_qol.columnconfigure(1, weight=1)

            self.switch_vmu = ctk.CTkSwitch(self.frame_qol, text=self._("sw_vmu"))
            self.switch_vmu.grid(row=0, column=0, sticky="w", pady=10)
            self.switch_boxart = ctk.CTkSwitch(self.frame_qol, text=self._("sw_box"))
            self.switch_boxart.grid(row=0, column=1, sticky="w", pady=10)
            self.switch_vga = ctk.CTkSwitch(self.frame_qol, text=self._("sw_vga"))
            self.switch_vga.grid(row=1, column=0, sticky="w", pady=10)
            self.switch_discord = ctk.CTkSwitch(self.frame_qol, text=self._("sw_disc"))
            self.switch_discord.grid(row=1, column=1, sticky="w", pady=10)
            self.switch_osd_vmu = ctk.CTkSwitch(self.frame_qol, text=self._("sw_osd"))
            self.switch_osd_vmu.grid(row=2, column=0, sticky="w", pady=10)
            self.switch_vmu_sound = ctk.CTkSwitch(self.frame_qol, text=self._("sw_vmu_snd"))
            self.switch_vmu_sound.grid(row=2, column=1, sticky="w", pady=10)

            self.frame_divisor3 = ctk.CTkFrame(self.tab_qol, height=2, fg_color="#444")
            self.frame_divisor3.pack(fill="x", padx=10, pady=(15, 10))

            self.switch_streamer = ctk.CTkSwitch(self.tab_qol, text=self._("sw_streamer"), command=self.ao_trocar_streamer)
            self.switch_streamer.pack(anchor="w", padx=10, pady=5)
            
            if self.config_atual.get("streamer_mode", False):
                self.switch_streamer.select()

            self.frame_divisor4 = ctk.CTkFrame(self.tab_qol, height=2, fg_color="#444")
            self.frame_divisor4.pack(fill="x", padx=10, pady=(15, 15))

            self.btn_salvar_config_qol = ctk.CTkButton(self.tab_qol, text=self._("btn_save_emu"), width=280, height=35, font=ctk.CTkFont(weight="bold"), command=self.salvar_configuracoes_emulador)
            self.btn_salvar_config_qol.pack(anchor="center", pady=(10, 10))

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

            self.rb_opengl = ctk.CTkRadioButton(self.frame_api_rb, text="OpenGL", variable=self.api_var, value="OpenGL")
            self.rb_opengl.pack(side="left", padx=(0, 15))
            
            self.rb_vulkan = ctk.CTkRadioButton(self.frame_api_rb, text="Vulkan", variable=self.api_var, value="Vulkan")
            self.rb_vulkan.pack(side="left", padx=(0, 15))
            
            self.rb_dx9 = ctk.CTkRadioButton(self.frame_api_rb, text="DirectX 9", variable=self.api_var, value="DirectX 9")
            self.rb_dx9.pack(side="left", padx=(0, 15))
            
            self.rb_dx11 = ctk.CTkRadioButton(self.frame_api_rb, text="DirectX 11", variable=self.api_var, value="DirectX 11")
            self.rb_dx11.pack(side="left", padx=(0, 15))

            self.lbl_res = ctk.CTkLabel(self.frame_video_options, text=self._("lbl_res"))
            self.lbl_res.grid(row=2, column=0, sticky="w", pady=5, padx=(0, 10))
            self.combo_res = ctk.CTkComboBox(self.frame_video_options, values=[
                "640x480 (Nativo)", "960x720 (1.5x)", "1280x960 (2x)", 
                "1440x1080 (3x)", "1920x1440 (4x)", "2880x2160 (6x)"
            ], state="readonly", width=180)
            self.combo_res.grid(row=2, column=1, sticky="w", pady=5)
            self.combo_res.set("640x480 (Nativo)")

            self.switch_fullscreen = ctk.CTkSwitch(self.frame_video_options, text=self._("sw_full"))
            self.switch_fullscreen.grid(row=3, column=0, columnspan=2, sticky="w", pady=(15, 5))
            self.switch_integer = ctk.CTkSwitch(self.frame_video_options, text=self._("sw_int"))
            self.switch_integer.grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
            self.switch_linear = ctk.CTkSwitch(self.frame_video_options, text=self._("sw_lin"))
            self.switch_linear.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
            self.switch_vsync = ctk.CTkSwitch(self.frame_video_options, text=self._("sw_vsync"))
            self.switch_vsync.grid(row=6, column=0, columnspan=2, sticky="w", pady=5)

            self.btn_salvar_video = ctk.CTkButton(self.tab_video, text=self._("btn_save_vid"), width=280, height=35, font=ctk.CTkFont(weight="bold"), command=self.salvar_configuracoes_video)
            self.btn_salvar_video.pack(pady=(15, 5))

            self.frame_divisor_vid = ctk.CTkFrame(self.tab_video, height=2, fg_color="#444")
            self.frame_divisor_vid.pack(fill="x", padx=10, pady=(5, 5))

            self.label_hw_title = ctk.CTkLabel(self.tab_video, text=self._("lbl_hw_title"), font=ctk.CTkFont(size=14, weight="bold"))
            self.label_hw_title.pack(anchor="w", padx=10, pady=(5, 2))

            self.frame_hw = ctk.CTkFrame(self.tab_video, fg_color="#2b2b2b")
            self.frame_hw.pack(fill="x", padx=10, pady=2, ipadx=5, ipady=5)
            
            self.lbl_hw_info = ctk.CTkLabel(self.frame_hw, text=self._("lbl_hw_search"), justify="left")
            self.lbl_hw_info.pack(anchor="w", padx=10, pady=5)
            
            self.btn_driver = ctk.CTkButton(self.frame_hw, text=self._("btn_driver"), width=200, height=28, fg_color="#4169E1", hover_color="#1E90FF", command=self.abrir_site_driver, state="disabled")
            self.btn_driver.pack(anchor="w", padx=10, pady=(0, 5))

        def construir_aba_controles(self):
            self.label_ctrl_title = ctk.CTkLabel(self.tab_controles, text=self._("lbl_ctrl_title"), font=ctk.CTkFont(size=16, weight="bold"))
            self.label_ctrl_title.pack(anchor="w", padx=10, pady=(15, 5))

            self.label_ctrl_desc = ctk.CTkLabel(self.tab_controles, text=self._("lbl_ctrl_desc"), text_color="gray", justify="left")
            self.label_ctrl_desc.pack(anchor="w", padx=10, pady=(0, 15))

            self.frame_ctrl = ctk.CTkFrame(self.tab_controles, fg_color="transparent")
            self.frame_ctrl.pack(fill="x", padx=10, pady=5)

            self.combo_ctrl = ctk.CTkComboBox(self.frame_ctrl, values=list(PERFIS_CONTROLES.keys()), width=350, state="readonly")
            self.combo_ctrl.pack(side="left", fill="x", expand=True, padx=(0, 10))
            if list(PERFIS_CONTROLES.keys()):
                self.combo_ctrl.set(list(PERFIS_CONTROLES.keys())[0])

            self.btn_injetar_ctrl = ctk.CTkButton(self.tab_controles, text=self._("btn_inject"), width=280, height=35, font=ctk.CTkFont(weight="bold"), fg_color="#8B008B", hover_color="#A52A2A", command=self.injetar_controle)
            self.btn_injetar_ctrl.pack(pady=(20, 10))

        def injetar_controle(self):
            controle_selecionado = self.combo_ctrl.get()
            perfil = PERFIS_CONTROLES.get(controle_selecionado)
            if not perfil: return

            install_path = self.entry_path.get()
            if not install_path or not os.path.exists(install_path):
                mb.showerror("Erro", self._("msg_error"), parent=self)
                return

            mappings_dir = os.path.join(install_path, "mappings")
            os.makedirs(mappings_dir, exist_ok=True)
            
            arquivo_destino = os.path.join(mappings_dir, perfil["arquivo"])
            try:
                with open(arquivo_destino, "w", encoding="utf-8") as f:
                    f.write(perfil["conteudo"])
                self.log(f"🎮 Injeção: '{perfil['arquivo']}' injetado em mappings/ com sucesso.")
                mb.showinfo("Sucesso", self._("msg_inject_success"), parent=self)
            except Exception as e:
                self.log(f"❌ Erro ao injetar o controle: {e}")
                mb.showerror("Erro", f"Erro: {e}", parent=self)

        def construir_aba_saves(self):
            self.label_cloud = ctk.CTkLabel(self.tab_saves, text=self._("lbl_cloud"), font=ctk.CTkFont(weight="bold", size=14))
            self.label_cloud.pack(anchor="w", padx=10, pady=(15, 2))
            
            self.cloud_var = ctk.StringVar(value="nenhum")
            self.frame_cloud = ctk.CTkFrame(self.tab_saves, fg_color="transparent")
            self.frame_cloud.pack(fill="x", padx=10, pady=(0, 5))

            has_gdrive = self.verificar_caminho_nuvem("Google Drive")
            has_onedrive = self.verificar_caminho_nuvem("OneDrive")

            self.rb_cloud_none = ctk.CTkRadioButton(self.frame_cloud, text=self._("rb_none"), font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="nenhum")
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

            self.switch_mappings = ctk.CTkSwitch(self.tab_saves, text=self._("sw_map"))
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
            self.label_saves_desc.pack(anchor="w", padx=10, pady=(0, 10))

            self.frame_saves_list = ctk.CTkFrame(self.tab_saves, fg_color="transparent")
            self.frame_saves_list.pack(fill="x", padx=10, pady=5)

            self.btn_buscar_saves = ctk.CTkButton(self.frame_saves_list, text=self._("btn_search_saves"), width=140, command=self.buscar_backups_saves)
            self.btn_buscar_saves.pack(side="left", padx=(0, 10))

            self.combo_backups = ctk.CTkComboBox(self.frame_saves_list, values=[self._("combo_saves_def")], width=350, state="readonly")
            self.combo_backups.pack(side="left", fill="x", expand=True)
            self.combo_backups.set(self._("combo_saves_def"))

            self.btn_restaurar_save = ctk.CTkButton(self.tab_saves, text=self._("btn_extract"), width=280, height=35, font=ctk.CTkFont(weight="bold"), fg_color="#228B22", hover_color="#006400", command=self.restaurar_backup_selecionado)
            self.btn_restaurar_save.pack(pady=(20, 10))
            self.btn_restaurar_save.configure(state="disabled")
            self.arquivos_backup_encontrados = {}

        def resolver_bios_mal_posicionada(self, path):
            if getattr(self, 'bios_prompt_done', False): return
            self.bios_prompt_done = True
            resposta_mover = mb.askyesno("BIOS", "Os arquivos da BIOS foram encontrados na pasta raiz do emulador.\nO padrão é armazená-los na pasta 'data'. Mover automaticamente?", parent=self)
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
                resposta_config = mb.askyesno("BIOS", "Deseja registrar essa pasta raiz nas opções do emulador para resolver o aviso?", parent=self)
                if resposta_config:
                    if atualizar_emu_cfg(install_path=path, bios_path=path):
                        self.atualizar_status_diretorio(path)

        def limpar_backups_antigos(self):
            limite_str = self.config_atual.get("backup_limit", "5")
            if limite_str in ["Ilimitado", "Unlimited", "Illimité", "Unbegrenzt", "无限制", "無制限", "Неограничено", "غير محدود", "असीमित"]: return
            try: limite = int(limite_str)
            except ValueError: return
            cloud_prov = self.config_atual.get("cloud_provider", "nenhum")
            if not cloud_prov or cloud_prov == "nenhum": return
            
            caminho_base = None
            if cloud_prov == "gdrive" and cloud_saves: caminho_base = cloud_saves.get_gdrive_path()
            elif cloud_prov == "onedrive" and cloud_saves: caminho_base = cloud_saves.get_onedrive_path()
            if not caminho_base or not os.path.exists(caminho_base): return

            caminho_nuvem = os.path.join(caminho_base, "Flycast_Saves_Backup")
            if not os.path.exists(caminho_nuvem): return
            arquivos_zip = [f for f in os.listdir(caminho_nuvem) if f.lower().endswith(".zip") and f != "flycast_backup.zip"]
            if len(arquivos_zip) <= limite: return

            arquivos_zip.sort(key=lambda x: os.path.getmtime(os.path.join(caminho_nuvem, x)))
            for i in range(len(arquivos_zip) - limite):
                try: os.remove(os.path.join(caminho_nuvem, arquivos_zip[i]))
                except Exception: pass

        def buscar_backups_saves(self):
            cloud_prov = self.cloud_var.get()
            if cloud_prov == "nenhum": return
            caminho_base = None
            if cloud_prov == "gdrive" and cloud_saves: caminho_base = cloud_saves.get_gdrive_path()
            elif cloud_prov == "onedrive" and cloud_saves: caminho_base = cloud_saves.get_onedrive_path()
            if not caminho_base or not os.path.exists(caminho_base): return

            caminho_nuvem = os.path.join(caminho_base, "Flycast_Saves_Backup")
            if not os.path.exists(caminho_nuvem):
                self.combo_backups.configure(values=[self._("log_not_found")])
                self.combo_backups.set(self._("log_not_found"))
                self.btn_restaurar_save.configure(state="disabled")
                return

            try:
                self.limpar_backups_antigos() 
                arquivos_zip = [f for f in os.listdir(caminho_nuvem) if f.lower().endswith(".zip") and f != "flycast_backup.zip"]
                if not arquivos_zip:
                    self.combo_backups.configure(values=[self._("log_not_found")])
                    self.combo_backups.set(self._("log_not_found"))
                    self.btn_restaurar_save.configure(state="disabled")
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
            except Exception: pass

        def restaurar_backup_selecionado(self):
            selecionado = self.combo_backups.get()
            caminho_zip = self.arquivos_backup_encontrados.get(selecionado)
            if not caminho_zip or not os.path.exists(caminho_zip): return
            install_path = self.entry_path.get()
            if not install_path or not os.path.exists(install_path): return
            
            if not mb.askyesno("Confirmar", f"Extrair arquivos de:\n{selecionado}\n\nContinuar?", parent=self): return
            
            custom_vmu = ""
            custom_save = ""
            cfg_path = os.path.join(install_path, "emu.cfg")
            if not os.path.exists(cfg_path): cfg_path = os.path.join(install_path, "data", "emu.cfg")
                
            if os.path.exists(cfg_path):
                try:
                    c = configparser.RawConfigParser(strict=False)
                    c.read(cfg_path, encoding='utf-8')
                    if c.has_section('config'):
                        custom_vmu = c.get('config', 'Dreamcast.VmuPath', fallback='')
                        custom_save = c.get('config', 'Dreamcast.SavePath', fallback='')
                except Exception: pass

            if custom_vmu and not os.path.isabs(custom_vmu): custom_vmu = os.path.join(install_path, custom_vmu)
            if custom_save and not os.path.isabs(custom_save): custom_save = os.path.join(install_path, custom_save)
                
            try:
                with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                    for file_info in zip_ref.infolist():
                        if file_info.filename.endswith('/'): continue
                        basename = os.path.basename(file_info.filename)
                        if file_info.filename.startswith('mappings/') or basename.endswith('.cfg'):
                            dest_dir = os.path.join(install_path, "mappings")
                        else:
                            if basename.startswith('vmu') and custom_vmu: dest_dir = custom_vmu
                            elif custom_save: dest_dir = custom_save
                            else: dest_dir = os.path.join(install_path, "data")
                        os.makedirs(dest_dir, exist_ok=True)
                        with zip_ref.open(file_info.filename) as source, open(os.path.join(dest_dir, basename), "wb") as target:
                            shutil.copyfileobj(source, target)
                mb.showinfo("Sucesso", self._("msg_success"), parent=self)
            except Exception as e:
                mb.showerror("Erro", f"Erro na extração: {e}", parent=self)

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
            mb.showinfo("Copiado", self._("msg_success"), parent=self)

        def limpar_logs(self):
            log_path = os.path.join(self.entry_path.get(), "flycast_updater.log")
            if os.path.exists(log_path):
                try:
                    os.remove(log_path)
                    self.carregar_logs()
                    self.log("🗑️ Log limpo pelo usuário.")
                except Exception: pass

        def salvar_estado_atual(self):
            self.config_atual["branch"] = self.branch_var.get()
            self.config_atual["create_shortcut"] = self.switch_desktop.get() == 1
            self.config_atual["create_startup"] = self.switch_startup.get() == 1
            self.config_atual["install_path"] = self.entry_path.get()
            self.config_atual["cloud_provider"] = self.cloud_var.get() if self.cloud_var.get() != "nenhum" else None
            self.config_atual["nogui"] = self.switch_nogui.get() == 1
            self.config_atual["language"] = self.lang
            self.config_atual["backup_mappings"] = self.switch_mappings.get() == 1
            self.config_atual["backup_limit"] = self.combo_limit.get()
            self.config_atual["streamer_mode"] = getattr(self, "switch_streamer", ctk.BooleanVar(value=False)).get() == 1
            salvar_configuracao(self.config_atual)

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
                resposta = mb.askyesno("Bem-vindo", "Deseja ajuda para configurar rapidamente a pasta de ROMs e o RetroAchievements agora?", parent=self)
                if resposta:
                    self.tabview.set(self._("tab_emu"))
                    self.config_atual["setup_completed"] = True
                else:
                    self.config_atual["setup_declined"] = True
                self.salvar_estado_atual()
            elif completo:
                self.tabview.set(self._("tab_games"))
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
            
            self.definir_entry_custom(self.entry_bios_path, def_bios)
            self.definir_entry_custom(self.entry_vmu_path, def_vmu)
            self.definir_entry_custom(self.entry_state_path, def_state)
            self.definir_entry_custom(self.entry_save_path, def_save)
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
                            
                            if bios_p or vmu_p or state_p or save_p:
                                self.switch_custom_paths.select()
                                self.toggle_custom_paths()
                                if bios_p: self.definir_entry_custom(self.entry_bios_path, bios_p)
                                if vmu_p: self.definir_entry_custom(self.entry_vmu_path, vmu_p)
                                if state_p: self.definir_entry_custom(self.entry_state_path, state_p)
                                if save_p: self.definir_entry_custom(self.entry_save_path, save_p)

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

                        if config.has_section('window'):
                            if config.get('window', 'fullscreen', fallback='no').lower() == 'yes': self.switch_fullscreen.select()
                        break
                    except Exception: pass

        def salvar_configuracoes_emulador(self):
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
                    self.btn_salvar_config_emu.configure(text="⏳ Autenticando...")
                    if hasattr(self, 'btn_salvar_config_qol'):
                        self.btn_salvar_config_qol.configure(text="⏳ Autenticando...")
                    self.update() 
                    token_api = obter_token_retroachievements(ra_user, ra_pass_input)
                    if token_api:
                        ra_token_final = token_api
                        self.token_ra_salvo = token_api
                    else:
                        mb.showerror("Login", self._("msg_error"), parent=self)
                        self.btn_salvar_config_emu.configure(text=self._("btn_save_emu"))
                        if hasattr(self, 'btn_salvar_config_qol'):
                            self.btn_salvar_config_qol.configure(text=self._("btn_save_emu"))
                        return 
            else:
                ra_token_final = ra_pass_input

            sucesso = atualizar_emu_cfg(
                install_path=install_path, roms_path=self.rom_paths_list,
                ra_enabled=ra_on, ra_user=ra_user, ra_pass=ra_token_final, ra_hardcore=ra_hard,
                vmu_individual=qol_vmu, fetch_boxart=qol_boxart, vga_cable=qol_vga,
                discord_presence=qol_discord, show_osd_vmu=qol_osd_vmu, vmu_sound=qol_vmu_sound,
                bios_path=bios_p, vmu_path=vmu_p, state_path=state_p, save_path=save_p,
                streamer_mode=is_streamer
            )

            self.config_atual["setup_completed"] = True
            self.config_atual["ra_api_key"] = getattr(self, "entry_ra_api", tk.Entry()).get().strip() if hasattr(self, "entry_ra_api") else ""
            self.salvar_estado_atual()
            
            self.btn_salvar_config_emu.configure(text=self._("btn_save_emu"))
            if hasattr(self, 'btn_salvar_config_qol'):
                self.btn_salvar_config_qol.configure(text=self._("btn_save_emu"))

            if sucesso: mb.showinfo("Sucesso", self._("msg_success"), parent=self)
            else: mb.showerror("Erro", self._("msg_error"), parent=self)

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

            sucesso = atualizar_emu_cfg(install_path=install_path, vid_api=api, vid_res=res_val, vid_full=full, vid_int=integer, vid_lin=linear, vid_vsync=vsync)
            self.salvar_estado_atual()
            if sucesso: mb.showinfo("Sucesso", self._("msg_success"), parent=self)
            else: mb.showerror("Erro", self._("msg_error"), parent=self)

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
                    self.lbl_emulador_status.configure(text=self._("emu_status_offline"), text_color="#FFD700")
                    self.btn_atualizar.configure(text=f"🚀 {self._('btn_update_act')}")
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

        def abrir_janela_ajuda(self):
            win_ajuda = ctk.CTkToplevel(self)
            win_ajuda.title("Sobre / About")
            win_ajuda.geometry("550x550")
            win_ajuda.attributes("-topmost", True)
            texto_ajuda = f"🌀 FLYCAST UPDATER - v{VERSION}\n\n• Branch Master: Lançamentos estáveis / Stable releases.\n• Branch Dev: Lançamentos diários / Daily builds.\n\n🖧 USO PELO TERMINAL (CLI) / COMMAND LINE:\n-nogui, -dev, -master, -rollback, -silent, -reset\n"
            lbl_texto = ctk.CTkLabel(win_ajuda, text=texto_ajuda, justify="left", font=ctk.CTkFont(size=12))
            lbl_texto.pack(padx=20, pady=20, fill="both", expand=True)

        def abrir_ajuda_api_key(self):
            win_api = ctk.CTkToplevel(self)
            win_api.title("Como obter a Web API Key?")
            win_api.geometry("500x320")
            win_api.attributes("-topmost", True)
            
            texto = (
                "Para exibir seus pontos na interface, o sistema precisa da sua Web API Key.\n\n"
                "Passo a Passo:\n"
                "1. Clique no botão abaixo para abrir o site do RetroAchievements.\n"
                "2. Faça o seu login normalmente (caso não esteja logado).\n"
                "3. Na página que se abrir, acesse a aba 'Aplicações' no menu esquerdo.\n"
                "4. Copie o código longo listado em 'Web API Key'.\n"
                "5. Cole no campo do Flycast Updater e clique em Salvar."
            )
            
            lbl_texto = ctk.CTkLabel(win_api, text=texto, justify="left", font=ctk.CTkFont(size=13), wraplength=460)
            lbl_texto.pack(padx=20, pady=(20, 10), fill="both", expand=True)
            
            # O link abaixo já manda o usuário direto para o painel de configurações (Control Panel)
            btn_link = ctk.CTkButton(win_api, text="🌐 Abrir RetroAchievements", width=200, height=35, fg_color="#228B22", hover_color="#006400", font=ctk.CTkFont(weight="bold"), command=lambda: webbrowser.open("https://retroachievements.org/controlpanel.php"))
            btn_link.pack(pady=(0, 20))

        def preparar_motor(self, acao):
            texto_atual = self.btn_atualizar.cget("text")
            self.btn_atualizar.configure(state="disabled")
            self.btn_rollback.configure(state="disabled")
            
            if acao == "atualizar": 
                if self._("btn_play") in texto_atual: self.btn_atualizar.configure(text=self._("btn_starting"))
                else: self.btn_atualizar.configure(text=self._("btn_processing"))
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
                if getattr(sys, 'frozen', False) and acao != "rollback":
                    if verificar_atualizacao_updater(install_path, modo_gui=True, app_gui=self): return 

                branch_escolhida = self.branch_var.get()
                criar_desktop = self.switch_desktop.get() == 1
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
                update_flycast.SHOULD_CREATE_SHORTCUT = criar_desktop
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