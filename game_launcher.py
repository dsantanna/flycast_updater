import sys, os, json, time, subprocess, threading, urllib.request, urllib.parse, datetime, re, shutil
import tkinter as tk
import tkinter.messagebox as mb
import customtkinter as ctk
import dc_gamesdb
import concurrent.futures

try:
    import pygame
    HAS_PYGAME = True
except ImportError: HAS_PYGAME = False

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

import configparser

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

class GameLibraryManager:
    def __init__(self, app_instance):
        self.app = app_instance
        self.ra_labels = {}
        self.show_favorites_only = False 
        self.garantir_arquivos_essenciais()

    # ==========================================
    # NOVO MOTOR DE BUSCA INTELIGENTE (RA)
    # ==========================================
    def buscar_dados_ra(self, user_db, nome_jogo, arquivos):
        import re
        def simplificar(texto):
            return re.sub(r'[^a-z0-9]', '', str(texto).lower())

        s_nome_jogo = simplificar(nome_jogo)
        
        # 1. Busca Exata com Case-Insensitive (Ignora "SoulCalibur" vs "Soulcalibur")
        for key, data in user_db.items():
            if simplificar(key) == s_nome_jogo:
                return data
                
        # 2. Busca Agressiva via arquivos ROM (Multi-Disco/Região)
        for rom_path in arquivos:
            s_rom = simplificar(os.path.splitext(os.path.basename(rom_path))[0])
            for key, data in user_db.items():
                s_key = simplificar(key)
                if len(s_key) > 3 and (s_key in s_rom or s_rom in s_key):
                    return data
                    
        return None
    # ==========================================
        
    def toggle_filtro_favoritos(self):
        self.show_favorites_only = not self.show_favorites_only
        cor = "#FFD700" if self.show_favorites_only else "gray"
        self.app.btn_filter_fav.configure(text_color=cor, border_color=cor)
        self.escanear_jogos()

    def toggle_favorito(self, nome_jogo, btn_widget):
        install_path = self.app.entry_path.get()
        db_ra_path = os.path.join(install_path, "RAlocal.db")
        ra_db = {}
        if os.path.exists(db_ra_path):
            try:
                with open(db_ra_path, "r", encoding="utf-8") as f: ra_db = json.load(f)
            except Exception: pass
        
        favs = ra_db.setdefault("_Favorites_", [])
        if nome_jogo in favs:
            favs.remove(nome_jogo)
            btn_widget.configure(text_color="gray")
        else:
            favs.append(nome_jogo)
            btn_widget.configure(text_color="#FFD700")
            
        try:
            with open(db_ra_path, "w", encoding="utf-8") as f: json.dump(ra_db, f, indent=4)
        except Exception: pass

    def salvar_notas_jogo(self, nome_jogo, text_widget, btn_widget):
        nota = text_widget.get("1.0", "end-1c")
        install_path = self.app.entry_path.get()
        db_ra_path = os.path.join(install_path, "RAlocal.db")
        ra_db = {}
        if os.path.exists(db_ra_path):
            try:
                with open(db_ra_path, "r", encoding="utf-8") as f: ra_db = json.load(f)
            except Exception: pass
        
        notas_db = ra_db.setdefault("_UserNotes_", {})
        notas_db[nome_jogo] = nota
        try:
            with open(db_ra_path, "w", encoding="utf-8") as f: json.dump(ra_db, f, indent=4)
        except Exception: pass
        
        btn_widget.configure(text="✔️ Salvo!", fg_color="#228B22")
        self.app.after(2000, lambda: btn_widget.configure(text="💾 Salvar Notas", fg_color="#1E90FF"))

    def baixar_capa_libretro(self, nome_jogo, boxart_dir, capa_lbl, no_cover_path=""):
        nome_busca = nome_jogo.replace("_", " ")
        url_repo = f"https://raw.githubusercontent.com/libretro/libretro-thumbnails/master/Sega%20-%20Dreamcast/Named_Boxarts/{urllib.parse.quote(nome_busca)}.png"
        destino = os.path.join(boxart_dir, f"{nome_jogo}.png")
        
        # Função auxiliar para aplicar a capa do Sonic se tudo der errado
        def aplicar_fallback():
            if HAS_PIL and os.path.exists(no_cover_path):
                try:
                    pil_img = Image.open(no_cover_path).resize((150, 150), Image.Resampling.LANCZOS)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(150, 150))
                    self.app.after(0, lambda: capa_lbl.configure(image=ctk_img, text="") if capa_lbl.winfo_exists() else None)
                except: pass
            else:
                self.app.after(0, lambda: capa_lbl.configure(text="🎮\nFLYCAST") if capa_lbl.winfo_exists() else None)

        try:
            os.makedirs(boxart_dir, exist_ok=True)
            req = urllib.request.Request(url_repo, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response, open(destino, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            if HAS_PIL and os.path.exists(destino):
                pil_img = Image.open(destino).resize((150, 150), Image.Resampling.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(150, 150))
                self.app.after(0, lambda: capa_lbl.configure(image=ctk_img, text="") if capa_lbl.winfo_exists() else None)
                self.app.log(f"🖼️ Auto-Scraper: Capa baixada com sucesso!")
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
                        self.app.after(0, lambda: capa_lbl.configure(image=ctk_img, text="") if capa_lbl.winfo_exists() else None)
                except Exception: 
                    aplicar_fallback()
            else: 
                aplicar_fallback()

    def sincronizar_retroachievements(self):
        from launcher import VERSION
        usuario = self.app.entry_ra_user.get().strip()
        api_key = self.app.config_atual.get("ra_api_key", "").strip()
        is_hardcore = getattr(self.app, "switch_hardcore", ctk.BooleanVar(value=False)).get() == 1
        tag_modo = " (Hardcore)" if is_hardcore else ""

        db_path = os.path.join(self.app.entry_path.get(), "RAlocal.db")
        ra_db = {}
        if os.path.exists(db_path):
            try:
                with open(db_path, "r", encoding="utf-8") as f: ra_db = json.load(f)
            except Exception: pass

        user_db = ra_db.setdefault(usuario, {})

        if not usuario or not api_key:
            self.app.log("⚠️ RA Sync: Web API Key não configurada. Lendo apenas cache local 'RAlocal.db'.")
            for base_name, (lbl, nome_exib) in self.ra_labels.items():
                arquivos = getattr(self, 'jogos_agrupados_cache', {}).get(nome_exib, [])
                data = self.buscar_dados_ra(user_db, nome_exib, arquivos)
                if data:
                    pts = data.get('score_hc', '0') if is_hardcore else data.get('score', '0')
                    tot = data.get('total_score', '0')
                    ach = int(data.get('achieved_hc', '0')) if is_hardcore else int(data.get('achieved', '0'))
                    tot_ach = int(data.get('total_achievements', '0'))
                    
                    if ach == tot_ach and tot_ach > 0:
                        texto = f"🌀 PLATINA{tag_modo}"
                        cor = "#00BFFF"
                    else:
                        texto = f"🏆 {pts}/{tot} pts{tag_modo}"
                        cor = "gray" if pts == "0" else "#00FF7F"
                else:
                    texto = f"🏆 Não Iniciado{tag_modo}"
                    cor = "gray"
                try: self.app.after(0, lambda l=lbl, t=texto, c=cor: l.configure(text=t, text_color=c) if l.winfo_exists() else None)
                except Exception: pass
            return

        self.app.log(f"🌐 RA Sync: Conectando à API Oficial do RetroAchievements para '{usuario}'...")
        try:
            url = f"https://retroachievements.org/API/API_GetUserRecentlyPlayedGames.php?z={urllib.parse.quote(usuario)}&y={api_key}&u={urllib.parse.quote(usuario)}&c=50"
            req = urllib.request.Request(url, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
            with urllib.request.urlopen(req, timeout=10) as response:
                json_data = json.loads(response.read().decode('utf-8'))
            
            self.app.log(f"✔️ RA Sync: Dados recebidos com sucesso. Atualizando banco de dados completo...")
            atualizou_algo = False
            
            for game in json_data:
                title = game.get("Title", "")
                if not title: continue
                
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
                    self.app.log(f"🎯 RA Sync: Atualizado '{title}': {pts_exib}/{total_score} pts!")

            if atualizou_algo:
                with open(db_path, "w", encoding="utf-8") as f: json.dump(ra_db, f, indent=4)
                self.app.log(f"💾 RA Sync: Banco local 'RAlocal.db' atualizado.")
            else:
                self.app.log(f"⚡ RA Sync: Nenhuma alteração nas pontuações.")

            for base_name, (lbl, nome_exib) in self.ra_labels.items():
                arquivos = getattr(self, 'jogos_agrupados_cache', {}).get(nome_exib, [])
                data = self.buscar_dados_ra(user_db, nome_exib, arquivos)
                if data:
                    pts = data.get('score_hc', '0') if is_hardcore else data.get('score', '0')
                    tot = data.get('total_score', '0')
                    ach = int(data.get('achieved_hc', '0')) if is_hardcore else int(data.get('achieved', '0'))
                    tot_ach = int(data.get('total_achievements', '0'))
                    
                    if ach == tot_ach and tot_ach > 0:
                        texto = f"🌀 PLATINA{tag_modo}"
                        cor = "#00BFFF"
                    else:
                        texto = f"🏆 {pts}/{tot} pts{tag_modo}"
                        cor = "gray" if pts == "0" else "#00FF7F"
                else:
                    texto = f"🏆 Não Iniciado{tag_modo}"
                    cor = "gray"
                try: self.app.after(0, lambda l=lbl, t=texto, c=cor: l.configure(text=t, text_color=c) if l.winfo_exists() else None)
                except Exception: pass

        except Exception as e:
            self.app.log(f"❌ RA Sync [Erro na API Oficial]: {e}")
            self.app.log(f"♻️ RA Sync: Utilizando dados salvos no cache local 'RAlocal.db'...")
            for base_name, (lbl, nome_exib) in self.ra_labels.items():
                arquivos = getattr(self, 'jogos_agrupados_cache', {}).get(nome_exib, [])
                data = self.buscar_dados_ra(user_db, nome_exib, arquivos)
                if data:
                    pts = data.get('score_hc', '0') if is_hardcore else data.get('score', '0')
                    tot = data.get('total_score', '0')
                    ach = int(data.get('achieved_hc', '0')) if is_hardcore else int(data.get('achieved', '0'))
                    tot_ach = int(data.get('total_achievements', '0'))
                    
                    if ach == tot_ach and tot_ach > 0:
                        texto = f"🌀 PLATINA{tag_modo}"
                        cor = "#00BFFF"
                    else:
                        texto = f"🏆 {pts}/{tot} pts{tag_modo}"
                        cor = "gray" if pts == "0" else "#00FF7F"
                else:
                    texto = f"🏆 Não Iniciado{tag_modo}"
                    cor = "gray"
                try: self.app.after(0, lambda l=lbl, t=texto, c=cor: l.configure(text=t, text_color=c) if l.winfo_exists() else None)
                except Exception: pass

    def buscar_empresa_ra(self, base_name, lbl_empresa):
        from launcher import VERSION
        usuario = self.app.entry_ra_user.get().strip()
        api_key = self.app.config_atual.get("ra_api_key", "").strip()
        
        install_path = self.app.entry_path.get()
        db_ra_path = os.path.join(install_path, "RAlocal.db")
        ra_db = {}
        if os.path.exists(db_ra_path):
            try:
                with open(db_ra_path, "r", encoding="utf-8") as f: ra_db = json.load(f)
            except Exception: pass
        
        info_db = ra_db.setdefault("_GameInfo_", {})
        if base_name in info_db:
            self.app.after(0, lambda: lbl_empresa.configure(text=f"Empresa: {info_db[base_name]}"))
            return
            
        if not usuario or not api_key: return 
        
        try:
            game_id = None
            nome_busca = base_name.lower().replace(" (usa)", "").replace(" (europe)", "").replace(" (japan)", "").strip()
            
            for console_id in [32, 27]:
                if game_id: break
                url_list = f"https://retroachievements.org/API/API_GetGameList.php?z={urllib.parse.quote(usuario)}&y={api_key}&i={console_id}"
                req = urllib.request.Request(url_list, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    lista = json.loads(response.read().decode('utf-8'))
                
                for game in lista:
                    if nome_busca in game.get("Title", "").lower() or game.get("Title", "").lower() in nome_busca:
                        game_id = game.get("ID")
                        break
            
            if game_id:
                url_game = f"https://retroachievements.org/API/API_GetGame.php?z={urllib.parse.quote(usuario)}&y={api_key}&i={game_id}"
                req2 = urllib.request.Request(url_game, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
                with urllib.request.urlopen(req2, timeout=5) as response2:
                    dados_jogo = json.loads(response2.read().decode('utf-8'))
                    empresa = dados_jogo.get("Developer", dados_jogo.get("Publisher", ""))
                    if empresa:
                        info_db[base_name] = empresa
                        with open(db_ra_path, "w", encoding="utf-8") as f: json.dump(ra_db, f, indent=4)
                        self.app.after(0, lambda: lbl_empresa.configure(text=f"Empresa: {empresa}"))
        except Exception: pass

    def monitorar_jogo(self, proc, nome_jogo):
        inicio = time.time()
        proc.wait() 
        fim = time.time()
        jogado_segundos = int(fim - inicio)

        self.app.after(0, self.app.deiconify)
        self.app.after(1000, getattr(self.app, 'iniciar_radio', lambda: None))

        if hasattr(self.app, 'widget_chroma') and self.app.widget_chroma.winfo_exists():
            self.app.after(0, self.app.widget_chroma.destroy)

        if jogado_segundos > 10:
            install_path = self.app.entry_path.get()
            db_ra_path = os.path.join(install_path, "RAlocal.db")
            ra_db = {}
            if os.path.exists(db_ra_path):
                try:
                    with open(db_ra_path, "r", encoding="utf-8") as f: ra_db = json.load(f)
                except Exception: pass
            
            playtime_db = ra_db.setdefault("_Playtime_", {})
            playtime_antigo = self.app.config_atual.get("playtime", {})
            
            if playtime_antigo:
                for k, v in playtime_antigo.items():
                    if k not in playtime_db: playtime_db[k] = v
                self.app.config_atual["playtime"] = {} 
                self.app.salvar_estado_atual()

            playtime_db[nome_jogo] = playtime_db.get(nome_jogo, 0) + jogado_segundos
            
            try:
                with open(db_ra_path, "w", encoding="utf-8") as f: json.dump(ra_db, f, indent=4)
            except Exception: pass
            
            self.app.log(f"⏱️ Playtime Tracker: Tempo atualizado para '{nome_jogo}': +{jogado_segundos}s")
            self.app.after(0, self.escanear_jogos)

    def selecionar_disco(self, nome_jogo, arquivos, from_bp=False):
        if len(arquivos) <= 1:
            rom_alvo = arquivos[0] if arquivos else ""
            self.lancar_jogo(rom_alvo, nome_jogo, from_bp=from_bp)
            return

        win_disco = ctk.CTkToplevel(self.app)
        win_disco.title("Selecionar Disco")
        win_disco.geometry("400x280")
        win_disco.attributes("-topmost", True)
        win_disco.grab_set()

        ctk.CTkLabel(win_disco, text="Este jogo possui múltiplos discos ou versões.\nEscolha qual iniciar:", font=ctk.CTkFont(weight="bold", size=13), justify="center").pack(pady=(15, 10))
        
        escolha_var = ctk.StringVar(value=arquivos[0])
        self.idx_selecionado = 0
        botoes_rom = arquivos

        for r in arquivos:
            basename = os.path.basename(r)
            ctk.CTkRadioButton(win_disco, text=basename, variable=escolha_var, value=r).pack(anchor="w", padx=30, pady=5)

        def confirmar_disco():
            rom_escolhida = escolha_var.get()
            win_disco.destroy()
            self.lancar_jogo(rom_escolhida, nome_jogo, from_bp=from_bp)

        ctk.CTkButton(win_disco, text="✔️ OK (Botão A)", command=confirmar_disco, width=120, height=32, font=ctk.CTkFont(weight="bold")).pack(pady=15)

        # --- MÁGICA: Pop-up controlável pelo Gamepad ---
        def gamepad_poll():
            if not win_disco.winfo_exists(): return
            try:
                import pygame
                for event in pygame.event.get():
                    if event.type == pygame.JOYHATMOTION:
                        if event.value[1] == 1: # D-Pad Cima
                            self.idx_selecionado = max(0, self.idx_selecionado - 1)
                            escolha_var.set(botoes_rom[self.idx_selecionado])
                        elif event.value[1] == -1: # D-Pad Baixo
                            self.idx_selecionado = min(len(botoes_rom)-1, self.idx_selecionado + 1)
                            escolha_var.set(botoes_rom[self.idx_selecionado])
                    elif event.type == pygame.JOYBUTTONDOWN:
                        if event.button in [0, 1, 7, 9]: # A / Cross / Start / Options
                            confirmar_disco()
                            return
                        elif event.button in [2, 6, 8]: # Voltar / Circle / Share
                            win_disco.destroy()
                            if hasattr(self.app, 'janela_bp'): self.app.janela_bp.jogo_em_execucao = False
                            return
            except: pass
            win_disco.after(50, gamepad_poll)

        if from_bp:
            win_disco.after(50, gamepad_poll)

    def lancar_jogo(self, rom_path, nome_jogo=None, is_netplay=False, from_bp=False):
        if not rom_path or not os.path.exists(rom_path):
            self.app.mostrar_toast("Erro ao Lançar", "O arquivo de ROM selecionado não foi localizado no disco.", "error")
            if hasattr(self.app, 'janela_bp'): self.app.janela_bp.jogo_em_execucao = False
            return

        install_path = self.app.entry_path.get()
        flycast_exe = os.path.join(install_path, "flycast.exe")
        
        if not os.path.exists(flycast_exe):
            self.app.mostrar_toast("Emulador Ausente", "O executável 'flycast.exe' não foi encontrado. Atualize na aba BIOS e Emu.", "error")
            if hasattr(self.app, 'janela_bp'): self.app.janela_bp.jogo_em_execucao = False
            return

        usar_cheats = self.switch_cheats.get() == 1 if hasattr(self, 'switch_cheats') else False
        is_hardcore = self.app.switch_hardcore.get() == 1 if hasattr(self.app, 'switch_hardcore') else False

        # --- A JOGADA DE MESTRE: Importar só no momento de uso (Zero Circular Import) ---
        from launcher import atualizar_emu_cfg

        # --- FORÇA FULLSCREEN SE VIER DO BIG PICTURE ---
        if from_bp:
            atualizar_emu_cfg(install_path, cheat_enable=usar_cheats, ra_hardcore=is_hardcore, vid_full=True)
        else:
            atualizar_emu_cfg(install_path, cheat_enable=usar_cheats, ra_hardcore=is_hardcore)
        
        try:
            import configparser
            caminhos_cfg = [os.path.join(install_path, "emu.cfg"), os.path.join(install_path, "data", "emu.cfg")]
            for cfg_net in caminhos_cfg:
                if os.path.exists(cfg_net):
                    c_net = configparser.RawConfigParser(strict=False)
                    c_net.optionxform = str
                    c_net.read(cfg_net, encoding='utf-8')
                    if not c_net.has_section('network'): c_net.add_section('network')
                    
                    if not is_netplay:
                        c_net.set('network', 'Enable', 'no')
                        c_net.set('network', 'ActAsServer', 'no')
                        c_net.set('network', 'GGPO', 'no')
                        
                    with open(cfg_net, 'w', encoding='utf-8') as f: 
                        c_net.write(f, space_around_delimiters=True)
        except Exception as e:
            self.app.log(f"⚠️ Aviso Netplay Firewall: {e}")
        
        self.app.log(f"🚀 Iniciando jogo: {os.path.basename(rom_path)}")

        args_lancamento = [flycast_exe, rom_path]

        def executar_processo():
            try:
                # 1. Pausa a Rádio do App e do Big Picture
                if hasattr(self.app, 'bgm_playing') and self.app.bgm_playing:
                    if not getattr(self.app, 'is_paused', False):
                        self.app.radio_play_pause()
                if hasattr(self.app, 'janela_bp') and self.app.janela_bp and self.app.janela_bp.winfo_exists():
                    self.app.janela_bp.radio.pause()

                # 2. Esconde o Big Picture e o Launcher Principal para manter a imersão
                if hasattr(self.app, 'janela_bp') and self.app.janela_bp and self.app.janela_bp.winfo_exists():
                    self.app.janela_bp.withdraw()
                self.app.after(0, self.app.withdraw)
                
                inicio = time.time()
                
                # 3. TOCA O SOM ÉPICO E LANÇA O JOGO
                if hasattr(self.app, 'sfx'): self.app.sfx.play("start")

                # --- O OVERLAY INICIA AQUI! ---
                if hasattr(self.app, 'ra_manager'):
                    self.app.ra_manager.iniciar_rastreio_em_gameplay(nome_jogo)
                # --------------------------------------

                processo = subprocess.Popen(args_lancamento, cwd=install_path)
                processo.wait() # <--- Fica aqui até o cara fechar o emulador

                # --- O OVERLAY TERMINA AQUI! ---
                if hasattr(self.app, 'ra_manager'):
                    self.app.ra_manager.parar_rastreio()
                # ----------------------------------------

                # Avisa o Discord que a gameplay começou!
                if hasattr(self.app, 'discord'): self.app.discord.atualizar_jogo(nome_jogo)

                processo = subprocess.Popen(args_lancamento, cwd=install_path)
                processo.wait()

                if hasattr(self.app, 'discord'): self.app.discord.atualizar_menu()
                
                fim = time.time()
                duracao_segundos = int(fim - inicio)
                if duracao_segundos > 30:
                    minutos = duracao_segundos // 60
                    self.app.log(f"⏱️ Partida encerrada. Tempo jogado: {minutos} minuto(s).")
                    self.atualizar_tempo_jogo_db(rom_path, minutos)

                # --- GATILHO DO AUTO-CLOUD SYNC ---
                if hasattr(self.app, 'save_manager'):
                    self.app.save_manager.auto_sync_saves()
                    
            except Exception as e:
                self.app.log(f"❌ Erro ao rodar o emulador: {e}")
            finally:
                # 4. Restaura o modo de vídeo original do usuário ANTES de reexibir as janelas
                if from_bp:
                    full_original = self.app.switch_fullscreen.get() == 1 if hasattr(self.app, 'switch_fullscreen') else False
                    atualizar_emu_cfg(install_path, vid_full=full_original)

                # 5. Acorda o Big Picture (ou o Launcher) do modo de hibernação
                if hasattr(self.app, 'janela_bp') and self.app.janela_bp and self.app.janela_bp.winfo_exists():
                    self.app.janela_bp.deiconify()
                    self.app.janela_bp.focus_force()
                    
                    # --- O PARRY FINAL NO GHOST INPUT ---
                    try:
                        import pygame
                        pygame.event.clear()
                    except: pass
                    # 1.5 segundos de bloqueio TOTAL de botões na interface!
                    self.app.janela_bp.tempo_desbloqueio = time.time() + 1.5
                    # ----------------------------------------------

                    self.app.janela_bp.jogo_em_execucao = False
                    self.app.janela_bp.radio.play()
                        
                self.app.after(0, self.escanear_jogos)

        import threading
        threading.Thread(target=executar_processo, daemon=True).start()

    def mostrar_info_jogo(self, nome_jogo, db_info):
        top = ctk.CTkToplevel(self.app)
        top.title(self.app._("lbl_info_title"))
        top.geometry("680x660")
        top.attributes("-topmost", True)

        install_path = self.app.entry_path.get()
        boxart_dir = os.path.join(install_path, "data", "boxart")

        frame_header_top = ctk.CTkFrame(top, fg_color="transparent")
        frame_header_top.pack(fill="x", padx=20, pady=(20, 10))

        frame_capa = ctk.CTkFrame(frame_header_top, fg_color="transparent")
        frame_capa.pack(side="left", padx=(0, 15))

        if HAS_PIL:
            caminhos_img = []
            if db_info and db_info.get("boxart_path"):
                caminhos_img.append(os.path.join(boxart_dir, db_info["boxart_path"]))
            caminhos_img.extend([
                os.path.join(boxart_dir, f"{nome_jogo}.png"), os.path.join(boxart_dir, f"{nome_jogo}.jpg")
            ])
            
            capa_encontrada = False
            for img_p in caminhos_img:
                if os.path.exists(img_p):
                    try:
                        pil_img = Image.open(img_p).resize((100, 100), Image.Resampling.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(100, 100))
                        lbl_capa = ctk.CTkLabel(frame_capa, image=ctk_img, text="")
                        lbl_capa.pack()
                        capa_encontrada = True
                        break
                    except Exception: pass
            
            # --- MÁGICA: FALLBACK PARA A JANELA DE INFO ---
                no_cover_path = os.path.join(boxart_dir, "no_cover.jpg")
                if os.path.exists(no_cover_path):
                    try:
                        pil_img = Image.open(no_cover_path).resize((100, 100), Image.Resampling.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(100, 100))
                        lbl_capa_placeholder = ctk.CTkLabel(frame_capa, image=ctk_img, text="")
                        lbl_capa_placeholder.pack()
                        capa_encontrada = True
                    except: pass
                    
            if not capa_encontrada:
                # --- MÁGICA: FALLBACK BLINDADO PARA A JANELA DE INFO ---
                fallback_dest = os.path.join(boxart_dir, "no_cover.jpg")
                fallback_src1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "no_cover.jpg")
                fallback_src2 = os.path.join(os.getcwd(), "no_cover.jpg")
                
                no_cover_path = fallback_dest
                if not os.path.exists(no_cover_path):
                    if os.path.exists(fallback_src1): no_cover_path = fallback_src1
                    elif os.path.exists(fallback_src2): no_cover_path = fallback_src2
                
                if os.path.exists(no_cover_path):
                    try:
                        pil_img = Image.open(no_cover_path).resize((100, 100), Image.Resampling.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(100, 100))
                        lbl_capa_placeholder = ctk.CTkLabel(frame_capa, image=ctk_img, text="")
                        lbl_capa_placeholder.pack()
                        capa_encontrada = True
                    except: pass
                    
                if not capa_encontrada:
                    lbl_capa_placeholder = ctk.CTkLabel(frame_capa, text="🎮", width=100, height=100, fg_color="#1a1a1a", corner_radius=8, font=ctk.CTkFont(size=30))
                    lbl_capa_placeholder.pack()

        frame_titulo_data = ctk.CTkFrame(frame_header_top, fg_color="transparent")
        frame_titulo_data.pack(side="left", fill="both", expand=True)

        lbl_nome = ctk.CTkLabel(frame_titulo_data, text=nome_jogo, font=ctk.CTkFont(size=20, weight="bold"), anchor="w", justify="left")
        lbl_nome.pack(fill="x", pady=(5, 2))

        data_bruta = db_info.get("release_date", "") if db_info else ""
        if data_bruta and len(data_bruta) == 10 and data_bruta.count("-") == 2:
            partes = data_bruta.split("-")
            data_formatada = f"{partes[2]}/{partes[1]}/{partes[0]}"
        else:
            data_formatada = data_bruta if data_bruta else self.app._("lbl_unknown")

        lbl_data = ctk.CTkLabel(frame_titulo_data, text=f"{self.app._('lbl_release')} {data_formatada}", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray", anchor="w")
        lbl_data.pack(fill="x")
        
        lbl_empresa = ctk.CTkLabel(frame_titulo_data, text=f"Empresa: {self.app._('lbl_unknown')}", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray", anchor="w")
        lbl_empresa.pack(fill="x")
        threading.Thread(target=self.buscar_empresa_ra, args=(nome_jogo, lbl_empresa), daemon=True).start()

        frame_stats = ctk.CTkFrame(frame_header_top, fg_color="#1a1a1a", corner_radius=8)
        frame_stats.pack(side="right", anchor="center", padx=(10, 0), ipadx=10, ipady=8)

        lbl_stats_title = ctk.CTkLabel(frame_stats, text="RetroAchievements", font=ctk.CTkFont(size=10, weight="bold"), text_color="gray")
        lbl_stats_title.pack(anchor="center", pady=(0, 5))

        usuario = self.app.entry_ra_user.get().strip()
        db_ra_path = os.path.join(install_path, "RAlocal.db")
        ra_db = {}
        if os.path.exists(db_ra_path):
            try:
                with open(db_ra_path, "r", encoding="utf-8") as f: ra_db = json.load(f)
            except Exception: pass
        
        user_db = ra_db.get(usuario, {})
        is_hardcore = getattr(self.app, "switch_hardcore", ctk.BooleanVar(value=False)).get() == 1
        tag_modo = " (HC)" if is_hardcore else ""
        
        arquivos_jogo = getattr(self, 'jogos_agrupados_cache', {}).get(nome_jogo, [])
        data_ra = self.buscar_dados_ra(user_db, nome_jogo, arquivos_jogo)
        
        if data_ra:
            pts = data_ra.get('score_hc', '0') if is_hardcore else data_ra.get('score', '0')
            tot = data_ra.get('total_score', '0')
            ach = int(data_ra.get('achieved_hc', '0')) if is_hardcore else int(data_ra.get('achieved', '0'))
            tot_ach = int(data_ra.get('total_achievements', '0'))
            
            if ach == tot_ach and tot_ach > 0:
                str_ra = f"🌀 PLATINA{tag_modo}"
                cor_ra = "#00BFFF"
            else:
                str_ra = f"🏆 {pts}/{tot} pts{tag_modo}"
                cor_ra = "gray" if pts == "0" else "#00FF7F"
        else:
            str_ra = "🏆 0/0 pts"
            cor_ra = "gray"

        playtime_db = ra_db.get("_Playtime_", {})
        total_segundos = playtime_db.get(nome_jogo, 0)
        
        horas, minutos = total_segundos // 3600, (total_segundos % 3600) // 60
        if horas > 0: str_tempo = f"⏱️ {horas}h {minutos}m"
        elif minutos > 0: str_tempo = f"⏱️ {minutos}m"
        else: str_tempo = f"⏱️ {self.app._('playtime_new', default='Novo')}"

        lbl_stat_ra = ctk.CTkLabel(frame_stats, text=str_ra, font=ctk.CTkFont(size=13, weight="bold"), text_color=cor_ra)
        lbl_stat_ra.pack(anchor="center", pady=(0, 5))

        lbl_stat_tempo = ctk.CTkLabel(frame_stats, text=str_tempo, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1E90FF")
        lbl_stat_tempo.pack(anchor="center", pady=(0, 0))

        # --- BOTÃO DA GALERIA DE CONQUISTAS ---
        btn_ver_conquistas = ctk.CTkButton(frame_stats, text="Ver Conquistas", height=24, font=ctk.CTkFont(weight="bold"), fg_color="#8B008B", hover_color="#9400D3", command=lambda: self.exibir_janela_conquistas(nome_jogo))
        btn_ver_conquistas.pack(pady=(10, 0))

        # --- BOTÃO DO GESTOR DE NETPLAY ---
        import netplay
        btn_netplay = ctk.CTkButton(frame_stats, text="🌐 Multiplayer (Netplay)", height=24, font=ctk.CTkFont(weight="bold"), fg_color="#FF4500", hover_color="#FF6347", command=lambda: netplay.NetplayManager(top, nome_jogo, rom_path, install_path, self))
        btn_netplay.pack(pady=(10, 0))
        # ----------------------------------------

        arquivos = self.jogos_agrupados_cache.get(nome_jogo, [])
        rom_path = arquivos[0] if arquivos else ""
        meta = dc_gamesdb.buscar_metadados(nome_jogo, rom_path, install_path, self.app.lang)
        
        if meta["score"]:
            str_score = dc_gamesdb.gerar_estrelas(meta["score"])
            lbl_score = ctk.CTkLabel(frame_stats, text=f"Nota: {str_score}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFD700")
            lbl_score.pack(anchor="center", pady=(5, 0))
            
        if meta["manufacturer"]:
            lbl_manuf = ctk.CTkLabel(frame_stats, text=f"🏢 Produtora: {meta['manufacturer']}", font=ctk.CTkFont(size=12))
            lbl_manuf.pack(anchor="center")
            
        if meta["player"] or meta["rating"]:
            txt_extra = []
            if meta["player"]: txt_extra.append(f"👥 {meta['player']}")
            if meta["rating"]: txt_extra.append(f"🔞 {meta['rating']}")
            lbl_extra = ctk.CTkLabel(frame_stats, text=" | ".join(txt_extra), font=ctk.CTkFont(size=11), text_color="gray")
            lbl_extra.pack(anchor="center")

        sinopse_texto = meta["story"]

        tabview_info = ctk.CTkTabview(top, height=360)
        tabview_info.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        tab_geral = tabview_info.add("Geral & Saves")
        tab_notas = tabview_info.add("📝 Diário de Bordo")

        txt_desc = ctk.CTkTextbox(tab_geral, wrap="word", font=("Segoe UI", 13), height=90)
        txt_desc.pack(fill="x", padx=5, pady=(5, 10))
        txt_desc.insert("1.0", sinopse_texto)
        txt_desc.configure(state="disabled")
        
        manual_path_found = None
        custom_manual = self.app.config_atual.get("custom_manual_path", "")
        manual_dir = custom_manual if custom_manual and os.path.exists(custom_manual) else os.path.join(install_path, "manuals")

        nome_limpo = re.sub(r'\(.*?\)|\[.*?\]', '', nome_jogo).strip()
        nome_jogo_lower = nome_jogo.lower()

        if os.path.exists(manual_dir):
            nome_limpo_lower = nome_limpo.lower()
            for f in os.listdir(manual_dir):
                if f.lower().endswith(".pdf"):
                    f_lower = f.lower()
                    if nome_jogo_lower in f_lower or nome_limpo_lower in f_lower:
                        manual_path_found = os.path.join(manual_dir, f)
                        break

        tema_atual = self.app.config_atual.get("tema", "Padrão DARK")
        try:
            from launcher import THEMES
            cor_primaria = THEMES.get(tema_atual, THEMES["Padrão DARK"])["primary"]
            cor_hover = THEMES.get(tema_atual, THEMES["Padrão DARK"])["hover"]
        except ImportError:
            cor_primaria, cor_hover = "#4169E1", "#1E90FF"

        if manual_path_found:
            def abrir_manual(m=manual_path_found):
                top.attributes("-topmost", False) 
                top.iconify() 
                try: os.startfile(m) 
                except Exception: pass

            btn_manual = ctk.CTkButton(tab_geral, text="📖 Ler Manual Original", font=ctk.CTkFont(weight="bold"), fg_color=cor_primaria, hover_color=cor_hover, command=abrir_manual)
            btn_manual.pack(fill="x", padx=5, pady=(0, 10))
        else:
            def buscar_manual_web():
                import webbrowser
                query = urllib.parse.quote(f'Dreamcast "{nome_limpo}" manual filetype:pdf')
                url = f"https://www.google.com/search?q={query}"
                webbrowser.open(url)

            btn_manual = ctk.CTkButton(tab_geral, text="🔍 Buscar Manual na Web", font=ctk.CTkFont(weight="bold"), fg_color="#555555", hover_color="#777777", command=buscar_manual_web)
            btn_manual.pack(fill="x", padx=5, pady=(0, 10))

        lbl_galeria = ctk.CTkLabel(tab_geral, text="📸 Galeria de Save States", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_galeria.pack(padx=5, anchor="w")

        scroll_galeria = ctk.CTkScrollableFrame(tab_geral, orientation="horizontal", height=150, fg_color="#1a1a1a", corner_radius=10)
        scroll_galeria.pack(fill="both", expand=True, padx=5, pady=(5, 5))

        custom_state = self.app.entry_state_path.get()
        state_dir = custom_state if custom_state else os.path.join(install_path, "data")
        
        encontrou_saves = False
        
        if os.path.exists(state_dir):
            arquivos = os.listdir(state_dir)
            nome_limpo_busca = re.sub(r'\(.*?\)|\[.*?\]', '', nome_jogo).strip()

            imagens_state = [f for f in arquivos if f.startswith(nome_limpo_busca) and f.lower().endswith(('.png', '.jpg')) and 'state' in f.lower()]
            
            for img_file in sorted(imagens_state, key=lambda x: os.path.getmtime(os.path.join(state_dir, x)), reverse=True):
                caminho_img = os.path.join(state_dir, img_file)
                try:
                    state_file = os.path.splitext(img_file)[0]
                    caminho_state = os.path.join(state_dir, state_file)
                    tamanho_kb = os.path.getsize(caminho_state) // 1024 if os.path.exists(caminho_state) else 0
                    
                    data_mod = datetime.datetime.fromtimestamp(os.path.getmtime(caminho_img)).strftime('%d/%m/%Y %H:%M')
                    
                    frame_card = ctk.CTkFrame(scroll_galeria, fg_color="#2b2b2b", corner_radius=8)
                    frame_card.pack(side="left", padx=10, pady=10)
                    
                    if HAS_PIL:
                        pil_img = Image.open(caminho_img).resize((140, 105), Image.Resampling.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(140, 105))
                        lbl_img = ctk.CTkLabel(frame_card, image=ctk_img, text="")
                        lbl_img.pack(padx=5, pady=5)
                    
                    lbl_info = ctk.CTkLabel(frame_card, text=f"🕒 {data_mod}\n💾 {tamanho_kb} KB", font=ctk.CTkFont(size=11), text_color="gray")
                    lbl_info.pack(pady=(0, 5))
                    
                    encontrou_saves = True
                except Exception: pass
        
        if not encontrou_saves:
            lbl_vazio = ctk.CTkLabel(scroll_galeria, text="Nenhuma captura de Save State encontrada para este jogo.", text_color="gray", font=ctk.CTkFont(slant="italic"))
            lbl_vazio.pack(expand=True, pady=40)

        notas_db = ra_db.get("_UserNotes_", {})
        texto_nota = notas_db.get(nome_jogo, "")

        txt_notas = ctk.CTkTextbox(tab_notas, wrap="word", font=("Segoe UI", 14))
        txt_notas.pack(fill="both", expand=True, padx=5, pady=(5, 10))
        txt_notas.insert("1.0", texto_nota)
        tema_atual = self.app.config_atual.get("tema", "Padrão DARK")
        from launcher import THEMES
        cor_primaria = THEMES.get(tema_atual, THEMES["Padrão DARK"])["primary"]
        cor_hover = THEMES.get(tema_atual, THEMES["Padrão DARK"])["hover"]
        cor_texto = THEMES.get(tema_atual, THEMES["Padrão DARK"])["text"]

        btn_salvar_notas = ctk.CTkButton(tab_notas, text="💾 Salvar Notas", font=ctk.CTkFont(weight="bold"), fg_color=cor_primaria, hover_color=cor_hover, text_color=cor_texto)
        btn_salvar_notas.configure(command=lambda: self.salvar_notas_jogo(nome_jogo, txt_notas, btn_salvar_notas))
        btn_salvar_notas.pack(pady=(0, 5))

    def exibir_janela_conquistas(self, nome_jogo):
        from launcher import VERSION
        usuario = self.app.entry_ra_user.get().strip()
        api_key = self.app.config_atual.get("ra_api_key", "").strip()

        if not usuario or not api_key:
            mb.showwarning("RetroAchievements", "Configure seu Usuário e Web API Key na aba Emulador para acessar a Galeria!", parent=self.app)
            return

        win_ra = ctk.CTkToplevel(self.app)
        win_ra.title(f"🏆 Galeria de Conquistas: {nome_jogo}")
        win_ra.geometry("780x680")
        win_ra.attributes("-topmost", True)
        win_ra.grab_set() # Prende o foco na janela
        
        lbl_status = ctk.CTkLabel(win_ra, text="⏳ Sincronizando com os servidores do RetroAchievements...", font=ctk.CTkFont(size=16))
        lbl_status.pack(expand=True)

        def rotina_carregamento():
            import re
            def simplificar(texto):
                return re.sub(r'[^a-z0-9]', '', str(texto).lower())

            game_id = None
            s_jogo = simplificar(nome_jogo)
            
            # Tenta descobrir o ID do Jogo cruzando dados dos jogos recentes
            try:
                url_rec = f"https://retroachievements.org/API/API_GetUserRecentlyPlayedGames.php?z={urllib.parse.quote(usuario)}&y={api_key}&u={urllib.parse.quote(usuario)}&c=50"
                req = urllib.request.Request(url_rec, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    recentes = json.loads(response.read().decode('utf-8'))
                    for g in recentes:
                        if simplificar(g.get("Title", "")) in s_jogo or s_jogo in simplificar(g.get("Title", "")):
                            game_id = g.get("GameID")
                            break
            except: pass

            # Se não jogou recentemente, varre o catálogo inteiro do Dreamcast (23) e Arcade (27)
            if not game_id:
                for console_id in [23, 27]:
                    if game_id: break
                    try:
                        url_list = f"https://retroachievements.org/API/API_GetGameList.php?z={urllib.parse.quote(usuario)}&y={api_key}&i={console_id}"
                        req = urllib.request.Request(url_list, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
                        with urllib.request.urlopen(req, timeout=5) as response:
                            lista = json.loads(response.read().decode('utf-8'))
                        for g in lista:
                            s_title = simplificar(g.get("Title", ""))
                            if s_jogo in s_title or s_title in s_jogo:
                                game_id = g.get("ID")
                                break
                    except: pass

            if not game_id:
                self.app.after(0, lambda: lbl_status.configure(text="❌ Jogo não localizado no banco de dados online do RetroAchievements."))
                return

            # Consulta Mestra: Baixa TODAS as conquistas do jogo e o progresso do usuário!
            try:
                url_prog = f"https://retroachievements.org/API/API_GetGameInfoAndUserProgress.php?z={urllib.parse.quote(usuario)}&y={api_key}&u={urllib.parse.quote(usuario)}&g={game_id}"
                req = urllib.request.Request(url_prog, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    game_data = json.loads(response.read().decode('utf-8'))
            except Exception as e:
                self.app.after(0, lambda: lbl_status.configure(text=f"❌ Erro de conexão ao baixar conquistas: {e}"))
                return

            achievements = game_data.get("Achievements", {})
            if not achievements:
                self.app.after(0, lambda: lbl_status.configure(text="⚠️ Este jogo ainda não possui conquistas cadastradas na plataforma."))
                return
            
            # Organiza na ordem de exibição oficial
            lista_achs = list(achievements.values())
            lista_achs.sort(key=lambda x: int(x.get("DisplayOrder", 0)))
            
            self.app.after(0, lbl_status.destroy)
            
            # Recupera as Cores do Tema Atual
            tema_atual = self.app.config_atual.get("tema", "Padrão DARK")
            try:
                from launcher import THEMES
                cor_primaria = THEMES.get(tema_atual, THEMES["Padrão DARK"])["primary"]
            except ImportError:
                cor_primaria = "#4169E1"
            
            def desenhar_ui():
                # --- O DASHBOARD DE PROGRESSO GLOBAL (CORRIGIDO) ---
                trofeus_totais = len(lista_achs)
                trofeus_ganhos = 0
                pontos_totais = 0
                pontos_ganhos = 0
                
                # O motor conta sozinho as medalhas direto da fonte!
                for ach in lista_achs:
                    pts = int(ach.get("Points", "0"))
                    pontos_totais += pts
                    if ach.get("DateEarned"): # Se tem data, foi conquistado!
                        trofeus_ganhos += 1
                        pontos_ganhos += pts
                        
                progresso_pct = (trofeus_ganhos / trofeus_totais) if trofeus_totais > 0 else 0
                
                frame_dash = ctk.CTkFrame(win_ra, fg_color="#1a1a1a", corner_radius=10)
                frame_dash.pack(fill="x", padx=10, pady=(10, 5))
                
                lbl_resumo = ctk.CTkLabel(frame_dash, text=f"Progresso Geral: {int(progresso_pct * 100)}%", font=ctk.CTkFont(size=14, weight="bold"))
                lbl_resumo.pack(anchor="w", padx=15, pady=(10, 0))
                
                bar_progresso = ctk.CTkProgressBar(frame_dash, progress_color=cor_primaria, width=700)
                bar_progresso.pack(fill="x", padx=15, pady=10)
                bar_progresso.set(progresso_pct)
                
                lbl_stats = ctk.CTkLabel(frame_dash, text=f"🏆 Troféus: {trofeus_ganhos}/{trofeus_totais}   |   💎 Pontos: {pontos_ganhos}/{pontos_totais}", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
                lbl_stats.pack(anchor="e", padx=15, pady=(0, 10))
                
                scroll = ctk.CTkScrollableFrame(win_ra, fg_color="transparent")
                scroll.pack(fill="both", expand=True, padx=5, pady=5)
                
                install_path = self.app.entry_path.get()
                ach_dir = os.path.join(install_path, "data", "achievements")
                os.makedirs(ach_dir, exist_ok=True)
                
                for ach in lista_achs:
                    title = ach.get("Title", "Conquista")
                    desc = ach.get("Description", "")
                    pts = ach.get("Points", "0")
                    badge = ach.get("BadgeName", "")
                    date_earned = ach.get("DateEarned")
                    
                    is_unlocked = date_earned is not None
                    
                    # Se está desbloqueado, o fundo recebe o destaque escuro, se não, fica mais cinza.
                    frame_ach = ctk.CTkFrame(scroll, fg_color="#1a1a2e" if is_unlocked else "#2b2b2b", corner_radius=8)
                    frame_ach.pack(fill="x", pady=5, padx=5)
                    
                    badge_file = f"{badge}.png" if is_unlocked else f"{badge}_lock.png"
                    badge_path = os.path.join(ach_dir, badge_file)
                    
                    # O Download Inteligente com Cache!
                    if not os.path.exists(badge_path):
                        url_img = f"https://media.retroachievements.org/Badge/{badge_file}"
                        try:
                            req_img = urllib.request.Request(url_img, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req_img, timeout=3) as resp_img, open(badge_path, 'wb') as f_img:
                                f_img.write(resp_img.read())
                        except: pass
                    
                    if HAS_PIL and os.path.exists(badge_path):
                        try:
                            pil_img = Image.open(badge_path).resize((64, 64), Image.Resampling.LANCZOS)
                            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(64, 64))
                            lbl_img = ctk.CTkLabel(frame_ach, image=ctk_img, text="")
                            lbl_img.pack(side="left", padx=10, pady=10)
                        except: pass
                    else:
                        lbl_img = ctk.CTkLabel(frame_ach, text="🏆", font=ctk.CTkFont(size=30))
                        lbl_img.pack(side="left", padx=15, pady=10)
                        
                    frame_text = ctk.CTkFrame(frame_ach, fg_color="transparent")
                    frame_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                    
                    # O título usa a cor Primária do Tema se estiver liberado!
                    cor_titulo = cor_primaria if is_unlocked else "gray"
                    lbl_t = ctk.CTkLabel(frame_text, text=title, font=ctk.CTkFont(size=16, weight="bold"), text_color=cor_titulo, anchor="w")
                    lbl_t.pack(fill="x")
                    
                    lbl_d = ctk.CTkLabel(frame_text, text=desc, font=ctk.CTkFont(size=12), text_color="#AAAAAA", anchor="w", justify="left")
                    lbl_d.pack(fill="x")
                    
                    lbl_p = ctk.CTkLabel(frame_text, text=f"💎 {pts} pts", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFD700" if is_unlocked else "#888888", anchor="w")
                    lbl_p.pack(fill="x", pady=(5,0))
                    
                    if is_unlocked:
                        # Exibe a data e a hora do desbloqueio formatada
                        data_formatada = date_earned[:10].split("-")
                        data_bonita = f"{data_formatada[2]}/{data_formatada[1]}/{data_formatada[0]}"
                        hora_bonita = date_earned[11:16]
                        
                        lbl_date = ctk.CTkLabel(frame_ach, text=f"✔️ {data_bonita} às {hora_bonita}", font=ctk.CTkFont(size=11, weight="bold"), text_color="#00FF7F")
                        lbl_date.pack(side="right", padx=15)
                        
            self.app.after(0, desenhar_ui)

        import threading
        threading.Thread(target=rotina_carregamento, daemon=True).start()

    def sortear_jogo(self):
        import random
        if not hasattr(self, 'jogos_agrupados_cache') or not self.jogos_agrupados_cache:
            mb.showinfo("Roleta", "Nenhum jogo encontrado na biblioteca para sortear!", parent=self.app)
            return
        
        jogo_sorteado = random.choice(list(self.jogos_agrupados_cache.keys()))
        arquivos = self.jogos_agrupados_cache[jogo_sorteado]
        
        self.app.log(f"🎲 Roleta: A sorte escolheu '{jogo_sorteado}'!")
        self.selecionar_disco(jogo_sorteado, arquivos)

    def abrir_seletor_jogos(self, titulo, callback_exportacao):
        if not hasattr(self, 'jogos_agrupados_cache') or not self.jogos_agrupados_cache:
            mb.showinfo(titulo, "Nenhum jogo encontrado na biblioteca!", parent=self.app)
            return

        top = ctk.CTkToplevel(self.app)
        top.title(titulo)
        top.geometry("450x550")
        top.attributes("-topmost", True)
        top.grab_set()

        lbl_desc = ctk.CTkLabel(top, text="Selecione os jogos que deseja exportar:", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_desc.pack(pady=(15, 10))

        frame_botoes_top = ctk.CTkFrame(top, fg_color="transparent")
        frame_botoes_top.pack(fill="x", padx=20, pady=5)

        vars_jogos = {}

        def selecionar_todos():
            for var in vars_jogos.values(): var.set(True)

        def limpar_todos():
            for var in vars_jogos.values(): var.set(False)

        btn_all = ctk.CTkButton(frame_botoes_top, text="✔️ Todos", width=100, height=26, command=selecionar_todos)
        btn_all.pack(side="left", padx=5)

        btn_none = ctk.CTkButton(frame_botoes_top, text="❌ Nenhum", width=100, height=26, fg_color="#555555", hover_color="#777777", command=limpar_todos)
        btn_none.pack(side="right", padx=5)

        scroll_frame = ctk.CTkScrollableFrame(top, fg_color="#1a1a1a", corner_radius=10)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        for nome_jogo in sorted(self.jogos_agrupados_cache.keys()):
            var = tk.BooleanVar(value=True) 
            vars_jogos[nome_jogo] = var
            chk = ctk.CTkCheckBox(scroll_frame, text=nome_jogo, variable=var)
            chk.pack(anchor="w", padx=10, pady=5)

        def confirmar():
            selecionados = [jogo for jogo, var in vars_jogos.items() if var.get()]
            if not selecionados:
                mb.showwarning("Aviso", "Nenhum jogo selecionado para exportar!", parent=top)
                return
            top.destroy()
            callback_exportacao(selecionados)

        btn_confirmar = ctk.CTkButton(top, text="🚀 Confirmar Exportação", font=ctk.CTkFont(weight="bold"), height=35, fg_color="#228B22", hover_color="#006400", command=confirmar)
        btn_confirmar.pack(pady=(10, 15))

    def garantir_arquivos_essenciais(self):
        import shutil
        import sys
        install_path = ""
        
        if hasattr(self.app, 'entry_path') and self.app.entry_path:
            try: install_path = self.app.entry_path.get()
            except: pass
        
        if not install_path and hasattr(self.app, 'config_atual'):
            install_path = self.app.config_atual.get("install_path", "")
            
        if not install_path: install_path = os.getcwd()
            
        # --- MÁGICA DO PYINSTALLER ---
        try: base_embutida = sys._MEIPASS
        except Exception: base_embutida = os.path.dirname(os.path.abspath(__file__))
        # -----------------------------
            
        # 1. GARANTIR A IMAGEM NO_COVER.JPG
        boxart_dir = os.path.join(install_path, "data", "boxart")
        try: os.makedirs(boxart_dir, exist_ok=True)
        except: pass
            
        dest_cover = os.path.join(boxart_dir, "no_cover.jpg")
        if not os.path.exists(dest_cover):
            for src in [
                os.path.join(base_embutida, "no_cover.jpg"), # Extrai do .EXE
                os.path.join(os.getcwd(), "no_cover.jpg"),
                os.path.join(os.getcwd(), "..", "no_cover.jpg")
            ]:
                if os.path.exists(src):
                    try:
                        shutil.copy2(src, dest_cover)
                        self.app.log(f"🖼️ 'no_cover.jpg' extraído e copiado para a galeria com sucesso.")
                        break
                    except Exception as e:
                        self.app.log(f"⚠️ Erro ao copiar 'no_cover.jpg': {e}")
                        
        # 2. GARANTIR O BANCO DE DADOS XML
        nomes_xml = ["DC-game.xml", "DC-gamedb.xml"]
        dest_xml = os.path.join(install_path, "DC-game.xml") 
        
        if not os.path.exists(dest_xml):
            xml_copiado = False
            for nome_arquivo in nomes_xml:
                if xml_copiado: break
                for src in [
                    os.path.join(base_embutida, nome_arquivo), # Extrai do .EXE
                    os.path.join(os.getcwd(), nome_arquivo),
                    os.path.join(os.getcwd(), "..", nome_arquivo)
                ]:
                    if os.path.exists(src):
                        try:
                            shutil.copy2(src, dest_xml)
                            self.app.log(f"🗄️ Banco de dados '{nome_arquivo}' extraído e instalado no emulador.")
                            xml_copiado = True
                            break
                        except Exception as e:
                            self.app.log(f"⚠️ Erro ao extrair '{nome_arquivo}': {e}")

    def exportar_para_steam(self, jogos_selecionados=None):
        if jogos_selecionados is None:
            self.abrir_seletor_jogos("Exportar para Steam", self.exportar_para_steam)
            return

        if not getattr(sys, 'frozen', False):
            mb.showwarning("Aviso", "Esta mágica requer a versão compilada (.exe) do Updater para clonar os executáveis.", parent=self.app)
            return

        install_path = self.app.entry_path.get()
        steam_dir = os.path.join(install_path, "Steam_Shortcuts")
        os.makedirs(steam_dir, exist_ok=True)
        
        flycast_exe = os.path.join(install_path, "flycast.exe")
        if not os.path.exists(flycast_exe):
            mb.showerror("Erro", "Executável do Flycast não foi encontrado.", parent=self.app)
            return

        self.app.log(f"☁️ Iniciando Clonagem Steam para {len(jogos_selecionados)} jogos...")
        
        sucessos = 0
        mapping = {}
        map_file = os.path.join(steam_dir, "steam_mapping.json")
        
        if os.path.exists(map_file):
            try:
                with open(map_file, "r", encoding="utf-8") as f: mapping = json.load(f)
            except: pass

        exe_original = sys.executable
        
        for nome_jogo in jogos_selecionados:
            arquivos = self.jogos_agrupados_cache[nome_jogo]
            rom_path = arquivos[0] 
            nome_seguro = re.sub(r'[\\/*?:"<>|]', "", nome_jogo)
            nome_atalho = f"{nome_seguro} [Flycast].exe"
            exe_destino = os.path.join(steam_dir, nome_atalho)
            
            try:
                shutil.copy2(exe_original, exe_destino)
                mapping[nome_atalho] = {"rom": rom_path, "flycast": flycast_exe}
                sucessos += 1
            except Exception as e:
                self.app.log(f"❌ Erro ao clonar launcher para {nome_jogo}: {e}")

        if mapping:
            try:
                with open(map_file, "w", encoding="utf-8") as f: json.dump(mapping, f, indent=4)
            except Exception as e:
                self.app.log(f"❌ Erro ao salvar o mapa da Steam: {e}")

        self.app.log(f"✔️ {sucessos} launchers (.exe) criados ou atualizados para a Steam.")
        
        msg = (
            f"Foram exportados {sucessos} jogos selecionados na pasta:\n"
            f"📁 {steam_dir}\n\n"
            "Caso seja um atalho novo, adicione-o na sua biblioteca Steam usando a opção "
            "'Adicionar um jogo não Steam...' e selecione o arquivo .exe gerado."
        )
        mb.showinfo("Integração Atualizada", msg, parent=self.app)
        
        try: os.startfile(steam_dir)
        except Exception: pass

    def exportar_para_desktop(self, jogos_selecionados=None):
        if jogos_selecionados is None:
            self.abrir_seletor_jogos("Atalhos no Desktop", self.exportar_para_desktop)
            return

        install_path = self.app.entry_path.get()
        desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
        games_dir = os.path.join(desktop_path, "Flycast Jogos")
        os.makedirs(games_dir, exist_ok=True)
        
        icons_dir = os.path.join(games_dir, "Icones_Originais")
        os.makedirs(icons_dir, exist_ok=True)

        flycast_exe = os.path.join(install_path, "flycast.exe")
        if not os.path.exists(flycast_exe):
            mb.showerror("Erro", "Executável do Flycast não foi encontrado.", parent=self.app)
            return

        self.app.log(f"🖥️ Forjando {len(jogos_selecionados)} atalhos Premium com Capas Originais...")
        
        pastas_capas = [
            os.path.join(install_path, "data", "covers"),
            os.path.join(install_path, "data", "boxart"),
            os.path.join(install_path, "covers"),
            os.path.join(install_path, "boxarts"),
            os.path.join(install_path, "media", "covers")
        ]
        
        sucessos = 0
        for nome_jogo in jogos_selecionados:
            arquivos = self.jogos_agrupados_cache[nome_jogo]
            rom_path = arquivos[0]
            nome_seguro = re.sub(r'[\\/*?:"<>|]', "", nome_jogo)
            
            lnk_path = os.path.join(games_dir, f"{nome_seguro}.lnk")
            if os.path.exists(lnk_path):
                try: os.remove(lnk_path)
                except: pass

            rom_basename = os.path.splitext(os.path.basename(rom_path))[0].lower()
            clean_name = re.sub(r'\(.*?\)|\[.*?\]', '', nome_jogo).strip().lower()
            nomes_para_testar = [nome_jogo.lower(), nome_seguro.lower(), clean_name, rom_basename]
            
            icon_location = f"{flycast_exe}, 0"
            capa_encontrada = None
            
            db_paths = [
                os.path.join(install_path, "data", "flycast-gamedb.json"),
                os.path.join(install_path, "data", "boxart", "flycast-gamedb.json"),
                os.path.join(install_path, "flycast-gamedb.json")
            ]
            
            for db_path in db_paths:
                if capa_encontrada: break
                if os.path.exists(db_path):
                    try:
                        with open(db_path, "r", encoding="utf-8") as f:
                            db_data = json.load(f)
                        for key, info in db_data.items():
                            if isinstance(info, dict):
                                db_name = info.get("name", "").lower()
                                db_file = str(info.get("fileName", "")).lower()
                                
                                match = False
                                for nt in nomes_para_testar:
                                    if nt == db_name or nt in db_file or (len(nt) > 3 and nt in db_name):
                                        match = True
                                        break
                                
                                if match:
                                    img_field = info.get("boxart_path", "") or info.get("boxart", "")
                                    if img_field:
                                        img_name = os.path.basename(img_field)
                                        caminho_teste = os.path.join(install_path, "data", "boxart", img_name)
                                        if os.path.exists(caminho_teste):
                                            capa_encontrada = caminho_teste
                                            break
                    except Exception: 
                        pass

            if not capa_encontrada:
                for pasta in pastas_capas:
                    if capa_encontrada: break
                    if not os.path.exists(pasta): continue
                    
                    try:
                        arquivos_pasta = os.listdir(pasta)
                        for f in arquivos_pasta:
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                                nome_arq = os.path.splitext(f)[0].lower()
                                if nome_arq in nomes_para_testar:
                                    capa_encontrada = os.path.join(pasta, f)
                                    break
                                    
                        if not capa_encontrada:
                            for f in arquivos_pasta:
                                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                                    nome_arq = os.path.splitext(f)[0].lower()
                                    for nt in nomes_para_testar:
                                        if len(nt) > 3 and (nt in nome_arq or nome_arq in nt):
                                            capa_encontrada = os.path.join(pasta, f)
                                            break
                                if capa_encontrada: break
                    except: pass

            if capa_encontrada:
                self.app.log(f"🖼️ Decodificado: Capa encontrada! -> {os.path.basename(capa_encontrada)}")
                icon_path = os.path.join(icons_dir, f"{nome_seguro}.ico")
                
                if not os.path.exists(icon_path):
                    try:
                        from PIL import Image
                        with Image.open(capa_encontrada) as img:
                            img = img.convert("RGBA")
                            w, h = img.size
                            ratio = min(256/w, 256/h)
                            new_w, new_h = int(w * ratio), int(h * ratio)
                            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                            
                            icon_img = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
                            offset_x = (256 - new_w) // 2
                            offset_y = (256 - new_h) // 2
                            icon_img.paste(img, (offset_x, offset_y))
                            
                            icon_img.save(icon_path, format="ICO", sizes=[(256, 256)])
                        
                        icon_location = icon_path
                        self.app.log(f"✅ Ícone forjado com sucesso!")
                    except Exception as e:
                        self.app.log(f"⚠️ Falha ao converter ícone {nome_jogo}: {e}")
                else:
                    icon_location = icon_path
            else:
                self.app.log(f"❌ Nenhuma arte encontrada para {nome_jogo}. Usando rodamoinho padrão.")

            ps_script = f'''
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{lnk_path}")
            $Shortcut.TargetPath = "{flycast_exe}"
            $Shortcut.Arguments = "`"{rom_path}`""
            $Shortcut.WorkingDirectory = "{install_path}"
            $Shortcut.Description = "Jogar {nome_seguro} (Flycast)"
            $Shortcut.IconLocation = "{icon_location}"
            $Shortcut.Save()
            '''
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.run(['powershell', '-NoProfile', '-Command', ps_script], startupinfo=startupinfo, capture_output=True)
                sucessos += 1
            except Exception as e:
                self.app.log(f"❌ Erro ao criar atalho de Desktop para {nome_jogo}: {e}")

        self.app.log(f"✔️ {sucessos} atalhos Premium criados no Desktop.")
        
        msg = (
            f"Foram gerados {sucessos} atalhos (.lnk) para os jogos selecionados!\n\n"
            f"Eles foram organizados de forma limpa na pasta:\n"
            f"📁 Área de Trabalho -> Flycast Jogos\n\n"
            "O banco de dados do emulador foi lido com sucesso e as capas originais foram convertidas e aplicadas no formato de ícone nativo do Windows (.ico)."
        )
        mb.showinfo("Coleção Premium Criada", msg, parent=self.app)
        mb.showinfo("Coleção Premium Criada", msg, parent=self.app)
        
        try: os.startfile(games_dir)
        except Exception: pass
        
    def escanear_jogos(self):
        import concurrent.futures
        
        for widget in self.app.frame_grid_games.winfo_children(): widget.destroy()
        self.ra_labels = {} 
        install_path = self.app.entry_path.get()
        boxart_dir = os.path.join(install_path, "data", "boxart")
        os.makedirs(boxart_dir, exist_ok=True)
        
        # --- ROBÔ COPIADOR BLINDADO MULTI-PATH ---
        fallback_src1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "no_cover.jpg")
        fallback_src2 = os.path.join(os.getcwd(), "no_cover.jpg")
        no_cover_src = fallback_src1 if os.path.exists(fallback_src1) else fallback_src2
        no_cover_dest = os.path.join(boxart_dir, "no_cover.jpg")
        
        if not os.path.exists(no_cover_dest) and os.path.exists(no_cover_src):
            try:
                import shutil
                shutil.copy2(no_cover_src, no_cover_dest)
                self.app.log("🖼️ Imagem padrão 'no_cover.jpg' copiada com sucesso para a galeria do emulador.")
            except Exception as e:
                self.app.log(f"⚠️ Erro ao copiar 'no_cover.jpg': {e}")
                
        # Garante que o sistema saiba qual imagem usar, seja da pasta do emulador ou do VS Code
        path_final_no_cover = no_cover_dest if os.path.exists(no_cover_dest) else no_cover_src
        
        termo_busca = getattr(self.app, "entry_busca_jogos", None)
        filtro = termo_busca.get().lower() if termo_busca else ""

        usuario = self.app.entry_ra_user.get().strip()
        db_ra_path = os.path.join(install_path, "RAlocal.db")
        ra_db = {}
        if os.path.exists(db_ra_path):
            try:
                with open(db_ra_path, "r", encoding="utf-8") as f: ra_db = json.load(f)
            except Exception: pass
        
        playtime_db = ra_db.setdefault("_Playtime_", {})
        playtime_antigo = self.app.config_atual.get("playtime", {})
        if playtime_antigo:
            for k, v in playtime_antigo.items():
                if k not in playtime_db: playtime_db[k] = v
            self.app.config_atual["playtime"] = {}
            self.app.salvar_estado_atual()
            try:
                with open(db_ra_path, "w", encoding="utf-8") as f: json.dump(ra_db, f, indent=4)
            except Exception: pass
        
        favs = ra_db.get("_Favorites_", [])
        
        soma_tempo_total = sum(playtime_db.values())
        soma_ra_total = 0

        user_db = ra_db.get(usuario, {})
        is_hardcore = getattr(self.app, "switch_hardcore", ctk.BooleanVar(value=False)).get() == 1
        tag_modo = " (Hardcore)" if is_hardcore else ""

        for nome_jogo, dados_ra in user_db.items():
            pts = int(dados_ra.get('score_hc', '0')) if is_hardcore else int(dados_ra.get('score', '0'))
            soma_ra_total += pts

        if hasattr(self.app, "lbl_dash_tempo"):
            h_tot, m_tot = soma_tempo_total // 3600, (soma_tempo_total % 3600) // 60
            self.app.lbl_dash_tempo.configure(text=f"⏱️ Tempo Total: {h_tot}h {m_tot}m")
            self.app.lbl_dash_ra.configure(text=f"🏆 Total RA: {soma_ra_total} pts")

            if playtime_db:
                top5 = sorted(playtime_db.items(), key=lambda x: x[1], reverse=True)[:5]
                texto_top5 = "🏆 HALL DA FAMA (Top 5) 🏆\n" + "-"*35 + "\n"
                medalhas = ["🥇", "🥈", "🥉", "🏅", "🏅"]
                for i, (jogo_nome, segs) in enumerate(top5):
                    h, m = segs // 3600, (segs % 3600) // 60
                    tempo_str = f"{h}h {m}m" if h > 0 else f"{m}m"
                    nome_curto = jogo_nome[:22] + "..." if len(jogo_nome) > 22 else jogo_nome
                    texto_top5 += f"{medalhas[i]} {nome_curto} ({tempo_str})\n"
                
                if hasattr(self.app.lbl_dash_tempo, '_tooltip'): self.app.lbl_dash_tempo._tooltip.update_text(texto_top5.strip())
                else: self.app.lbl_dash_tempo._tooltip = ToolTip(self.app.lbl_dash_tempo, texto_top5.strip())
            else:
                if not hasattr(self.app.lbl_dash_tempo, '_tooltip'): self.app.lbl_dash_tempo._tooltip = ToolTip(self.app.lbl_dash_tempo, "Jogue para construir seu Hall da Fama!")

        if not self.app.rom_paths_list:
            lbl = ctk.CTkLabel(self.app.frame_grid_games, text=self.app._("msg_no_games", default="Nenhuma pasta configurada."), font=ctk.CTkFont(size=14, slant="italic"), text_color="gray")
            lbl.pack(pady=40)
            return

        extensoes_suportadas = ('.cdi', '.gdi', '.chd', '.cue')
        jogos_fisicos = []
        for path_atual in self.app.rom_paths_list:
            if not os.path.exists(path_atual): continue
            try:
                for f in os.listdir(path_atual):
                    if f.lower().endswith(extensoes_suportadas):
                        caminho_arquivo = os.path.join(path_atual, f)
                        if os.path.getsize(caminho_arquivo) > 1024 * 1024: 
                            jogos_fisicos.append((f, path_atual))
            except Exception: pass

        if not jogos_fisicos:
            lbl = ctk.CTkLabel(self.app.frame_grid_games, text=self.app._("msg_no_games", default="Nenhum jogo encontrado."), font=ctk.CTkFont(size=14, slant="italic"), text_color="gray")
            lbl.pack(pady=40)
            return

        db_path = os.path.join(boxart_dir, "flycast-gamedb.json")
        game_db = {}
        if os.path.exists(db_path):
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    for item in json.load(f):
                        if item.get("file_name"):
                            game_db[item["file_name"]] = {"boxart_path": item.get("boxart_path", ""), "name": item.get("name", ""), "overview": item.get("overview", ""), "release_date": item.get("release_date", "")}
            except Exception: pass

        jogos_agrupados = {}
        padrao_disco = re.compile(r'(?i)\s*[\(\[-]?\s*disc\s*[0-9a-z]+\s*[\)\]]?')
        for jogo, r_path in jogos_fisicos:
            db_info = game_db.get(jogo)
            if db_info and db_info.get("name"):
                chave_grupo = db_info["name"]
            else:
                nome_limpo = os.path.splitext(jogo)[0]
                chave_grupo = padrao_disco.sub('', nome_limpo).strip()
                
            if chave_grupo not in jogos_agrupados: jogos_agrupados[chave_grupo] = []
            jogos_agrupados[chave_grupo].append(os.path.join(r_path, jogo))

        self.jogos_agrupados_cache = jogos_agrupados
        
        screen_width = self.app.winfo_screenwidth()
        max_cols = max(3, (screen_width - 80) // 190)
        row, col = 0, 0

        executor_capas = concurrent.futures.ThreadPoolExecutor(max_workers=8)

        for nome_exibicao in sorted(jogos_agrupados.keys()):
            if filtro and filtro not in nome_exibicao.lower():
                continue
            if getattr(self, "show_favorites_only", False) and nome_exibicao not in favs:
                continue

            arquivos_jogo = jogos_agrupados[nome_exibicao]
            jogo_ref = os.path.basename(arquivos_jogo[0])
            roms_path_ref = os.path.dirname(arquivos_jogo[0])
            nome_limpo_ref = os.path.splitext(jogo_ref)[0]
            
            card = ctk.CTkFrame(self.app.frame_grid_games, width=170, height=275, corner_radius=12, fg_color="#2b2b2b")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
            card.grid_propagate(False) 

            capa_lbl = None
            img_carregada = False
            db_info = game_db.get(jogo_ref)

            if HAS_PIL:
                caminhos_img = []
                if db_info and db_info.get("boxart_path"): caminhos_img.append(os.path.join(boxart_dir, db_info["boxart_path"]))
                caminhos_img.extend([
                    os.path.join(boxart_dir, f"{jogo_ref}.png"), os.path.join(boxart_dir, f"{jogo_ref}.jpg"), 
                    os.path.join(boxart_dir, f"{nome_limpo_ref}.png"), os.path.join(boxart_dir, f"{nome_limpo_ref}.jpg"),
                    os.path.join(boxart_dir, f"{nome_exibicao}.png"), os.path.join(boxart_dir, f"{nome_exibicao}.jpg"),
                    os.path.join(roms_path_ref, f"{nome_limpo_ref}.png"), os.path.join(roms_path_ref, f"{nome_limpo_ref}.jpg")
                ])
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
                # --- MÁGICA: USA O NO_COVER GARANTIDO COMO TELA DE ESPERA ---
                if HAS_PIL and os.path.exists(path_final_no_cover):
                    try:
                        pil_img = Image.open(path_final_no_cover).resize((150, 150), Image.Resampling.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(150, 150))
                        capa_lbl = ctk.CTkLabel(card, image=ctk_img, text="")
                    except:
                        capa_lbl = ctk.CTkLabel(card, text="🎮\nFLYCAST", width=150, height=150, fg_color="#1a1a1a", corner_radius=8, font=ctk.CTkFont(size=14, weight="bold"))
                else:
                    texto_dl = self.app._("lbl_downloading_cover", default="🎮\n(Baixando...)") if HAS_PIL else "🎮\nFLYCAST"
                    capa_lbl = ctk.CTkLabel(card, text=texto_dl, width=150, height=150, fg_color="#1a1a1a", corner_radius=8, font=ctk.CTkFont(size=14, weight="bold"))
                    
                # Aciona o Auto-Scraper passando o caminho do no_cover para caso ele falhe no download!
                if HAS_PIL: executor_capas.submit(self.baixar_capa_libretro, nome_exibicao, boxart_dir, capa_lbl, path_final_no_cover)

            capa_lbl.pack(pady=(10, 5), padx=10)

            # --- AQUI É ONDE O NOVO MOTOR ENTRA EM AÇÃO NOS CARDS ---
            data_ra = self.buscar_dados_ra(user_db, nome_exibicao, arquivos_jogo)
            if data_ra:
                pts = data_ra.get('score_hc', '0') if is_hardcore else data_ra.get('score', '0')
                tot = data_ra.get('total_score', '0')
                ach = int(data_ra.get('achieved_hc', '0')) if is_hardcore else int(data_ra.get('achieved', '0'))
                tot_ach = int(data_ra.get('total_achievements', '0'))
                
                if ach == tot_ach and tot_ach > 0:
                    texto_inicial_ra = f"🌀 PLATINA{tag_modo}"
                    cor_ra = "#00BFFF"
                else:
                    texto_inicial_ra = f"🏆 {pts}/{tot} pts{tag_modo}"
                    cor_ra = "gray" if pts == "0" else "#00FF7F"
            else:
                texto_inicial_ra = f"🏆 Buscando..."
                cor_ra = "#FFD700"

            lbl_ra = ctk.CTkLabel(card, text=texto_inicial_ra, font=ctk.CTkFont(size=10), text_color=cor_ra)
            lbl_ra.pack(pady=(0, 2))
            self.ra_labels[nome_exibicao] = (lbl_ra, nome_exibicao)

            total_segundos = playtime_db.get(nome_exibicao, 0)
            horas, minutos = total_segundos // 3600, (total_segundos % 3600) // 60
            if horas > 0: str_tempo = f"⏱️ {horas}h {minutos}m"
            elif minutos > 0: str_tempo = f"⏱️ {minutos}m"
            else: str_tempo = f"⏱️ {self.app._('playtime_new', default='Novo')}"

            lbl_tempo = ctk.CTkLabel(card, text=str_tempo, font=ctk.CTkFont(size=10), text_color="gray")
            lbl_tempo.pack(pady=(0, 2))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(pady=(2, 10))

            cor_fav = "#FFD700" if nome_exibicao in favs else "gray"
            btn_fav = ctk.CTkButton(btn_frame, text="⭐", width=26, height=26, fg_color="transparent", text_color=cor_fav, hover_color="#333333")
            btn_fav.configure(command=lambda b=nome_exibicao, bw=btn_fav: self.toggle_favorito(b, bw))
            btn_fav.pack(side="left", padx=(0, 5))
            
            btn_fav._tooltip = ToolTip(btn_fav, "Adicionar aos Favoritos")

            tema_atual = self.app.config_atual.get("tema", "Padrão DARK")
            try:
                from launcher import THEMES
                cor_primaria = THEMES.get(tema_atual, THEMES["Padrão DARK"])["primary"]
                cor_hover = THEMES.get(tema_atual, THEMES["Padrão DARK"])["hover"]
                cor_texto = THEMES.get(tema_atual, THEMES["Padrão DARK"])["text"]
            except ImportError:
                cor_primaria = "#4169E1"
                cor_hover = "#1E90FF"
                cor_texto = "white"

            btn_play = ctk.CTkButton(btn_frame, text="▶️ Jogar", width=85, height=26, fg_color=cor_primaria, hover_color=cor_hover, text_color=cor_texto, command=lambda b=nome_exibicao, a=arquivos_jogo: self.selecionar_disco(b, a))
            btn_play.pack(side="left", padx=(0, 5))

            btn_info = ctk.CTkButton(btn_frame, text="ℹ️", width=26, height=26, fg_color="#555555", hover_color="#777777", command=lambda b=nome_exibicao, d=db_info: self.mostrar_info_jogo(b, d))
            btn_info.pack(side="left")
            
            btn_info._tooltip = ToolTip(btn_info, "Ver Detalhes, Diário e Saves")

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        if self.ra_labels and not filtro: threading.Thread(target=self.sincronizar_retroachievements, daemon=True).start()