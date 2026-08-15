import os
import re
import json
import time
import customtkinter as ctk
from PIL import Image
# --- IMPORTS DE OUTROS MÓDULOS DO PROJETO ---
import pygame 
import radio_flycast
import video_snaps
import dc_gamesdb
# --- A MÁGICA SECRETA DO WINDOWS PARA EVITAR ENTRADA DUPLA NO XIMPUT ---
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

class ModoBigPicture(ctk.CTkToplevel):
    def __init__(self, master, game_manager):
        super().__init__(master)
        self.app = master
        self.game_manager = game_manager
        
        self.radio = radio_flycast.RadioFlycast()
        self.radio.carregar_playlist(self.app.entry_path.get())
        self.radio.play()
        
        self.jogos = sorted(list(self.game_manager.jogos_agrupados_cache.keys()))
        self.index_atual = 0
        self.index_menu = 0 # 0=Play, 1=Manual, 2=Conquistas, 3=Netplay
        self.jogo_em_execucao = False 
        
        self.tipo_controle = "XBOX"
        self.is_dinput_ps = False
        
        if not self.jogos:
            self.destroy()
            return
            
        # --- MÁGICA: INICIA NO MONITOR SELECIONADO NA ABA VÍDEO ---
        monitor_str = self.app.combo_monitor.get() if hasattr(self.app, 'combo_monitor') else ""
        if hasattr(self.app, 'lista_monitores'):
            for m in self.app.lista_monitores:
                if m['nome'] == monitor_str:
                    self.geometry(f"+{m['left']}+{m['top']}")
                    self.update_idletasks() # Força a interface a se posicionar antes do Fullscreen!
                    break
        # -----------------------------------------------------------
        
        # --- MÁGICA DO MULTI-MONITOR BLINDADA ---
        self.title("Big Blue - TV Mode")
        self.configure(fg_color="#050508")
        self.attributes("-topmost", True)
        
        monitor_str = self.app.combo_monitor.get() if hasattr(self.app, 'combo_monitor') else ""
        alinhado_secundario = False
        
        if hasattr(self.app, 'lista_monitores'):
            for m in self.app.lista_monitores:
                if m['nome'] == monitor_str:
                    try:
                        # Extrai a resolução exata do nome "Monitor 2 (1920x1080)"
                        dim = m['nome'].split('(')[1].split(')')[0]
                        w, h = dim.split('x')
                        self.geometry(f"{w}x{h}+{m['left']}+{m['top']}")
                        self.overrideredirect(True) # Arranca as bordas e domina o monitor escolhido!
                        alinhado_secundario = True
                    except: pass
                    break
        
        if not alinhado_secundario:
            self.attributes("-fullscreen", True) # Fallback seguro para o Monitor 1
        
        self.bind("<Escape>", lambda e: self.sair())
        self.bind("<Right>", self.proximo_jogo)
        self.bind("<Left>", self.jogo_anterior)
        self.bind("<Up>", lambda e: self.navegar_menu(-1))
        self.bind("<Down>", lambda e: self.navegar_menu(1))
        self.bind("<Return>", lambda e: self.executar_acao_menu())

        self.joysticks = []
        self.ultimo_input = 0
        self.leitura_controle_ativa = True
        
        try:
            pygame.init() 
            pygame.joystick.init()
            self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            for joy in self.joysticks: joy.init()
                
            if self.joysticks:
                nome_joy = self.joysticks[0].get_name().lower()
                self.app.log(f"🎮 Controle detectado na TV: {self.joysticks[0].get_name()}")
                if "playstation" in nome_joy or "dualshock" in nome_joy or "dualsense" in nome_joy or "wireless controller" in nome_joy:
                    self.tipo_controle = "PS"
                    if "wireless controller" in nome_joy: self.is_dinput_ps = True
                elif "8bitdo" in nome_joy or "nintendo" in nome_joy or "snes" in nome_joy or "pro controller" in nome_joy:
                    self.tipo_controle = "8BITDO"
        except Exception: pass
            
        self.construir_interface()

        # --- INIT DO MOTOR DE VÍDEO ---
        self.video_manager = video_snaps.VideoSnapManager(self.lbl_capa, delay_ms=800)
        # Mapeia os botões para o Joystick
        self.botoes_menu = [self.btn_play, self.btn_manual, self.btn_conquistas, self.btn_netplay]
        
        self.atualizar_tela()
        self.focus_force()
        self.verificar_controle()

    # --- MÁGICA DO CONTROLE (MENU + BLOQUEIO DE FANTASMAS) ---
    def verificar_controle(self):
        if not self.leitura_controle_ativa or not self.winfo_exists(): return
        
        agora = time.time()
        
        # --- A MAGIA: I-FRAMES DE INVENCIBILIDADE ---
        # Se a interface acabou de acordar, destrói qualquer input residual (Ghost Input)
        if agora < getattr(self, 'tempo_desbloqueio', 0):
            try: pygame.event.clear()
            except: pass
            self.after(50, self.verificar_controle)
            return

        # O FANTASMA EXORCIZADO: Se o jogo tá rodando, descartamos a fila.
        if self.jogo_em_execucao or not self.winfo_viewable():
            try: pygame.event.clear()
            except: pass
        else:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.JOYHATMOTION:
                        if event.value[0] == 1: self.proximo_jogo()       
                        elif event.value[0] == -1: self.jogo_anterior()   
                        elif event.value[1] == 1: self.navegar_menu(-1)   
                        elif event.value[1] == -1: self.navegar_menu(1)   
                        
                    elif event.type == pygame.JOYAXISMOTION:
                        if agora - self.ultimo_input > 0.2:
                            if event.axis == 0:
                                if event.value > 0.7: 
                                    self.proximo_jogo()
                                    self.ultimo_input = agora
                                elif event.value < -0.7: 
                                    self.jogo_anterior()
                                    self.ultimo_input = agora
                            elif event.axis == 1:
                                if event.value > 0.7: 
                                    self.navegar_menu(1)
                                    self.ultimo_input = agora
                                elif event.value < -0.7: 
                                    self.navegar_menu(-1)
                                    self.ultimo_input = agora
                                    
                    elif event.type == pygame.JOYBUTTONDOWN:
                        if self.is_dinput_ps:
                            botoes_confirmar = [1, 9]
                            botoes_voltar = [2, 8]
                        else:
                            botoes_confirmar = [0, 7]
                            botoes_voltar = [1, 6]
                            
                        if event.button in botoes_confirmar: self.executar_acao_menu()
                        elif event.button in botoes_voltar: self.sair()
                        elif event.button == 14: self.proximo_jogo()
                        elif event.button == 13: self.jogo_anterior()
                        elif event.button == 4: 
                            novo_vol = max(0.0, self.slider_volume.get() - 0.1)
                            self.slider_volume.set(novo_vol)
                            self.mudar_volume(novo_vol)
                        elif event.button == 5: 
                            novo_vol = min(1.0, self.slider_volume.get() + 0.1)
                            self.slider_volume.set(novo_vol)
                            self.mudar_volume(novo_vol)
            except Exception: pass
            
        self.after(50, self.verificar_controle)

    # --- NAVEGAÇÃO DO MENU LATERAL ---
    def navegar_menu(self, direcao):
        if hasattr(self.app, 'sfx'): self.app.sfx.play("hover")
        max_idx = len(self.botoes_menu) - 1
        for _ in range(max_idx + 1):
            self.index_menu += direcao
            if self.index_menu < 0: self.index_menu = max_idx
            elif self.index_menu > max_idx: self.index_menu = 0
            
            # Pula o Manual se ele estiver desabilitado!
            if self.index_menu == 1 and self.botoes_menu[1].cget("state") == "disabled":
                continue
            break
        self.atualizar_foco_menu()
        
    def atualizar_foco_menu(self):
        cores_normais = ["#228B22", "#4169E1", "#8B008B", "#FF4500"]
        cores_hover = ["#32CD32", "#1E90FF", "#9400D3", "#FF6347"]
        
        for i, btn in enumerate(self.botoes_menu):
            is_disabled = (i == 1 and btn.cget("state") == "disabled")
            if is_disabled:
                btn.configure(fg_color="#333333", border_width=0)
            else:
                if i == self.index_menu:
                    btn.configure(fg_color=cores_hover[i], border_width=3, border_color="white")
                else:
                    btn.configure(fg_color=cores_normais[i], border_width=0)

    def executar_acao_menu(self):
        if self.index_menu == 0: self.iniciar_jogo()
        elif self.index_menu == 1: self.abrir_manual()
        elif self.index_menu == 2: self.abrir_conquistas()
        elif self.index_menu == 3: self.abrir_netplay()

    def simplificar(self, texto): return re.sub(r'[^a-z0-9]', '', str(texto).lower())

    def construir_interface(self):
        self.frame_main = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_main.pack(fill="both", expand=True, padx=50, pady=50)
        
        self.frame_esq = ctk.CTkFrame(self.frame_main, fg_color="transparent", width=450)
        self.frame_esq.pack(side="left", fill="y", padx=(0, 40))
        
        self.lbl_capa = ctk.CTkLabel(self.frame_esq, text="")
        self.lbl_capa.pack(pady=(20, 20))
        
        self.btn_play = ctk.CTkButton(self.frame_esq, text="▶️ JOGAR", font=ctk.CTkFont(weight="bold", size=22), height=50, fg_color="#228B22", hover_color="#32CD32", command=self.iniciar_jogo)
        self.btn_play.pack(fill="x", padx=20, pady=(0, 15))

        self.btn_manual = ctk.CTkButton(self.frame_esq, text="📖 Ler Manual", font=ctk.CTkFont(weight="bold", size=18), height=45, fg_color="#4169E1", hover_color="#1E90FF", command=self.abrir_manual)
        self.btn_manual.pack(fill="x", padx=20)

        self.btn_conquistas = ctk.CTkButton(self.frame_esq, text="🏆 Conquistas", font=ctk.CTkFont(weight="bold", size=18), height=45, fg_color="#8B008B", hover_color="#9400D3", command=self.abrir_conquistas)
        self.btn_conquistas.pack(fill="x", padx=20, pady=(15, 0))

        self.btn_netplay = ctk.CTkButton(self.frame_esq, text="🌐 Netplay", font=ctk.CTkFont(weight="bold", size=18), height=45, fg_color="#FF4500", hover_color="#FF6347", command=self.abrir_netplay)
        self.btn_netplay.pack(fill="x", padx=20, pady=(15, 0))

        self.frame_dir = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.frame_dir.pack(side="right", fill="both", expand=True)
        
        self.lbl_nome = ctk.CTkLabel(self.frame_dir, text="", font=ctk.CTkFont(size=52, weight="bold"), text_color="#FFFFFF", anchor="w")
        self.lbl_nome.pack(fill="x", pady=(20, 5))

        self.frame_meta = ctk.CTkFrame(self.frame_dir, fg_color="transparent")
        self.frame_meta.pack(fill="x", pady=(0, 15))
        
        self.lbl_meta_score = ctk.CTkLabel(self.frame_meta, text="", font=ctk.CTkFont(size=18, weight="bold"), text_color="#FFD700")
        self.lbl_meta_score.pack(side="left", padx=(0, 15))
        
        self.lbl_meta_manuf = ctk.CTkLabel(self.frame_meta, text="", font=ctk.CTkFont(size=15, weight="bold"), text_color="#00FFFF")
        self.lbl_meta_manuf.pack(side="left", padx=(0, 15))
        
        self.lbl_meta_player = ctk.CTkLabel(self.frame_meta, text="", font=ctk.CTkFont(size=14), text_color="#CCCCCC")
        self.lbl_meta_player.pack(side="left", padx=(0, 15))
        
        self.lbl_meta_rating = ctk.CTkLabel(self.frame_meta, text="", font=ctk.CTkFont(size=14), text_color="#FF4500")
        self.lbl_meta_rating.pack(side="left")

        self.frame_ra = ctk.CTkFrame(self.frame_dir, fg_color="#1a1a2e", corner_radius=10)
        self.frame_ra.pack(fill="x", pady=(0, 20))
        self.lbl_ra = ctk.CTkLabel(self.frame_ra, text="🏆 Buscando Conquistas...", font=ctk.CTkFont(size=18, weight="bold"), text_color="#FFD700")
        self.lbl_ra.pack(pady=15, padx=20, anchor="w")
        
        self.textbox_desc = ctk.CTkTextbox(self.frame_dir, font=ctk.CTkFont(size=18), text_color="#CCCCCC", fg_color="#0F0F16", wrap="word")
        self.textbox_desc.pack(fill="both", expand=True, pady=(0, 20))
        
        self.frame_rodape = ctk.CTkFrame(self, fg_color="#0F0F16", height=80, corner_radius=0)
        self.frame_rodape.pack(side="bottom", fill="x")
        
        # MÁGICA: Instruções atualizadas para o novo menu e controle de volume!
        if self.tipo_controle == "PS": instrucoes = "⬅️ ➡️ Jogos   |   ⬆️ ⬇️ Menu   |   L1 / R1 Vol.   |   ✖ Confirma   |   ◯ Sair"
        elif self.tipo_controle == "8BITDO": instrucoes = "⬅️ ➡️ Jogos   |   ⬆️ ⬇️ Menu   |   L1 / R1 Vol.   |   Ⓑ Confirma   |   Ⓐ Sair"
        else: instrucoes = "⬅️ ➡️ Jogos   |   ⬆️ ⬇️ Menu   |   LB / RB Vol.   |   Ⓐ Confirma   |   Ⓑ Sair"
        
        self.lbl_instrucoes = ctk.CTkLabel(self.frame_rodape, text=instrucoes, font=ctk.CTkFont(size=16, weight="bold"), text_color="#888888")
        self.lbl_instrucoes.pack(side="left", padx=50, pady=25)
        
        self.frame_radio = ctk.CTkFrame(self.frame_rodape, fg_color="transparent")
        self.frame_radio.pack(side="right", padx=50, pady=20)
        
        ctk.CTkButton(self.frame_radio, text="⏮", width=40, command=self.radio.prev_track, fg_color="#333333").pack(side="left", padx=5)
        ctk.CTkButton(self.frame_radio, text="▶️ Play", width=60, command=self.radio.play, fg_color="#228B22").pack(side="left", padx=5)
        ctk.CTkButton(self.frame_radio, text="⏸ Pause", width=60, command=self.radio.pause, fg_color="#FF8C00").pack(side="left", padx=5)
        ctk.CTkButton(self.frame_radio, text="⏭", width=40, command=self.radio.next_track, fg_color="#333333").pack(side="left", padx=5)
        
        ctk.CTkLabel(self.frame_radio, text="🔊", font=ctk.CTkFont(size=20)).pack(side="left", padx=(20, 5))
        self.slider_volume = ctk.CTkSlider(self.frame_radio, from_=0.0, to=1.0, width=120, command=lambda v: self.radio.set_volume(v))
        self.slider_volume.set(0.5)
        self.slider_volume.pack(side="left", padx=(0, 5))

    def mudar_volume(self, valor):
        self.radio.set_volume(valor)

    def proximo_jogo(self, event=None):
        self.index_atual = (self.index_atual + 1) % len(self.jogos)
        if hasattr(self.app, 'sfx'): self.app.sfx.play("hover")
        self.atualizar_tela()

    def jogo_anterior(self, event=None):
        self.index_atual = (self.index_atual - 1) % len(self.jogos)
        if hasattr(self.app, 'sfx'): self.app.sfx.play("hover")
        self.atualizar_tela()

    def extrair_dados_ra(self, nome_jogo, rom_path):
        install_path = self.app.entry_path.get()
        ralocal_path = os.path.join(install_path, "RAlocal.db")
        texto_ra = "🏆 RetroAchievements: Base local não encontrada."

        if os.path.exists(ralocal_path):
            try:
                with open(ralocal_path, "r", encoding="utf-8") as f: ra_data = json.load(f)
                user_data = ra_data.get(self.app.entry_ra_user.get(), {})
                arquivos = self.game_manager.jogos_agrupados_cache.get(nome_jogo, [rom_path])
                game_ra = self.game_manager.buscar_dados_ra(user_db=user_data, nome_jogo=nome_jogo, arquivos=arquivos)
                        
                if game_ra:
                    ach = game_ra.get("achieved", "0")
                    tot_ach = game_ra.get("total_achievements", "0")
                    pts = game_ra.get("score", "0")
                    tot_pts = game_ra.get("total_score", "0")
                    texto_ra = f"🏆 Conquistas: {ach}/{tot_ach}   |   💎 Pontos: {pts}/{tot_pts}"
                else:
                    texto_ra = "🏆 RetroAchievements: Jogo não rastreado no seu perfil."
            except: pass
        return texto_ra

    def rastrear_manual(self, nome_jogo, rom_path):
        install_path = self.app.entry_path.get()
        pasta_manuais = os.path.join(install_path, "manuals")
        if not os.path.exists(pasta_manuais): return None
            
        nome_seguro = re.sub(r'[\\/*?:"<>|]', "", nome_jogo)
        rom_basename = os.path.splitext(os.path.basename(rom_path))[0].lower()
        clean_name = re.sub(r'\(.*?\)|\[.*?\]', '', nome_jogo).strip().lower()
        
        simples_jogo = self.simplificar(nome_jogo)
        simples_rom = self.simplificar(rom_basename)
        simples_clean = self.simplificar(clean_name)
        
        nomes_testes = [nome_jogo.lower(), nome_seguro.lower(), clean_name, rom_basename]
        testes_simples = [simples_jogo, simples_rom, simples_clean]
        
        try:
            for f in os.listdir(pasta_manuais):
                if f.lower().endswith('.pdf'):
                    nome_arq = os.path.splitext(f)[0].lower()
                    s_nome_arq = self.simplificar(nome_arq)
                    if nome_arq in nomes_testes or any(ts == s_nome_arq for ts in testes_simples) or any(len(ts) > 3 and ts in s_nome_arq for ts in testes_simples):
                        return os.path.join(pasta_manuais, f)
        except: pass
        return None

    def rastrear_capa(self, nome_jogo, rom_path):
        install_path = self.app.entry_path.get()
        boxart_dir = os.path.join(install_path, "data", "boxart")
        covers_dir = os.path.join(install_path, "data", "covers")
        
        rom_basename = os.path.splitext(os.path.basename(rom_path))[0]
        nome_limpo = re.sub(r'\(.*?\)|\[.*?\]', '', nome_jogo).strip()
        
        caminhos_exatos = [
            os.path.join(boxart_dir, f"{rom_basename}.png"), os.path.join(boxart_dir, f"{rom_basename}.jpg"),
            os.path.join(boxart_dir, f"{nome_jogo}.png"), os.path.join(boxart_dir, f"{nome_jogo}.jpg"),
            os.path.join(boxart_dir, f"{nome_limpo}.png"), os.path.join(boxart_dir, f"{nome_limpo}.jpg"),
            os.path.join(covers_dir, f"{rom_basename}.png"), os.path.join(covers_dir, f"{rom_basename}.jpg"),
            os.path.join(covers_dir, f"{nome_jogo}.png"), os.path.join(covers_dir, f"{nome_jogo}.jpg"),
        ]
        
        for p in caminhos_exatos:
            if os.path.exists(p): return p
                
        db_paths = [os.path.join(install_path, "data", "flycast-gamedb.json"), os.path.join(install_path, "data", "boxart", "flycast-gamedb.json"), os.path.join(install_path, "flycast-gamedb.json")]
        
        s_jogo = self.simplificar(nome_jogo)
        s_rom = self.simplificar(rom_basename)
        capa_parcial = None
        
        for db_path in db_paths:
            if os.path.exists(db_path):
                try:
                    with open(db_path, "r", encoding="utf-8") as f: db_data = json.load(f)
                    lista_db = db_data if isinstance(db_data, list) else db_data.values()
                    for info in lista_db:
                        if isinstance(info, dict):
                            db_name = self.simplificar(info.get("name", info.get("title", "")))
                            db_file = self.simplificar(info.get("file_name", info.get("fileName", "")))
                            is_exact = (s_jogo == db_name or s_rom == db_file)
                            is_partial = (len(s_jogo) > 3 and (s_jogo in db_name or s_jogo in db_file)) or (len(s_rom) > 3 and s_rom in db_file)
                            
                            if is_exact or is_partial:
                                img_field = info.get("boxart_path", "") or info.get("boxart", "")
                                if img_field:
                                    img_name = os.path.basename(img_field)
                                    caminho_teste = os.path.join(boxart_dir, img_name)
                                    if not os.path.exists(caminho_teste): caminho_teste = os.path.join(covers_dir, img_name)
                                    if os.path.exists(caminho_teste):
                                        if is_exact: return caminho_teste 
                                        elif not capa_parcial: capa_parcial = caminho_teste 
                except: pass
                
        if capa_parcial: return capa_parcial
            
        pastas_capas = [os.path.join(install_path, "data", "covers"), os.path.join(install_path, "data", "boxart"), os.path.join(install_path, "covers"), os.path.join(install_path, "boxarts"), os.path.join(install_path, "media", "covers")]
        testes_simples = [s_jogo, s_rom, self.simplificar(nome_limpo)]
        for pasta in pastas_capas:
            if not os.path.exists(pasta): continue
            try:
                for f in os.listdir(pasta):
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        s_nome_arq = self.simplificar(os.path.splitext(f)[0])
                        if any(len(ts) > 3 and ts in s_nome_arq for ts in testes_simples):
                            return os.path.join(pasta, f)
            except: pass
        return None

    def rastrear_video(self, nome_jogo, rom_path):
        install_path = self.app.entry_path.get()
        # Ele vai caçar o vídeo na pasta media/snaps!
        pastas_snaps = [
            os.path.join(install_path, "media", "snaps"),
            os.path.join(install_path, "data", "snaps"),
            os.path.join(install_path, "snaps")
        ]
        
        rom_basename = os.path.splitext(os.path.basename(rom_path))[0].lower()
        nome_limpo = re.sub(r'\(.*?\)|\[.*?\]', '', nome_jogo).strip().lower()
        simples_jogo = self.simplificar(nome_jogo)
        simples_rom = self.simplificar(rom_basename)
        simples_clean = self.simplificar(nome_limpo)
        
        testes = [simples_jogo, simples_rom, simples_clean]
        
        for pasta in pastas_snaps:
            if not os.path.exists(pasta): continue
            try:
                for f in os.listdir(pasta):
                    if f.lower().endswith(('.mp4', '.avi', '.mkv', '.webm')):
                        s_nome_arq = self.simplificar(os.path.splitext(f)[0])
                        if any(len(ts) > 3 and ts in s_nome_arq for ts in testes):
                            return os.path.join(pasta, f)
            except Exception: pass
        return None

    def atualizar_tela(self):
        nome_jogo = self.jogos[self.index_atual]
        arquivos = self.game_manager.jogos_agrupados_cache[nome_jogo]
        rom_path = arquivos[0]
        
        self.lbl_nome.configure(text=nome_jogo)
        self.lbl_ra.configure(text=self.extrair_dados_ra(nome_jogo, rom_path))
        
        meta = dc_gamesdb.buscar_metadados(nome_jogo, rom_path, self.app.entry_path.get(), self.app.lang)
        
        self.lbl_meta_score.configure(text=dc_gamesdb.gerar_estrelas(meta["score"]) if meta["score"] else "")
        self.lbl_meta_manuf.configure(text=f"🏢 {meta['manufacturer']}" if meta["manufacturer"] else "")
        self.lbl_meta_player.configure(text=f"👥 {meta['player']}" if meta["player"] else "")
        self.lbl_meta_rating.configure(text=f"🔞 {meta['rating']}" if meta["rating"] else "")
        
        self.textbox_desc.configure(state="normal")
        self.textbox_desc.delete("1.0", "end")
        self.textbox_desc.insert("1.0", meta["story"])
        self.textbox_desc.configure(state="disabled")
        
        capa_path = self.rastrear_capa(nome_jogo, rom_path)
        
        if not capa_path or not os.path.exists(capa_path):
            install_path = self.app.entry_path.get()
            fallback_dest = os.path.join(install_path, "data", "boxart", "no_cover.jpg")
            fallback_src1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "no_cover.jpg")
            fallback_src2 = os.path.join(os.getcwd(), "no_cover.jpg")
            
            if os.path.exists(fallback_dest): capa_path = fallback_dest
            elif os.path.exists(fallback_src1): capa_path = fallback_src1
            elif os.path.exists(fallback_src2): capa_path = fallback_src2

        if capa_path and os.path.exists(capa_path):
            try:
                img = Image.open(capa_path)
                w, h = img.size
                ratio = min(400/w, 400/h)
                new_w, new_h = int(w * ratio), int(h * ratio)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(new_w, new_h))
                self.lbl_capa.configure(image=ctk_img, text="")
            except:
                self.lbl_capa.configure(image="", text="⚠️ Capa Corrompida", font=ctk.CTkFont(size=20))
        else:
            self.lbl_capa.configure(image="", text="🌀 Imagem Indisponível", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E90FF")

        # --- GATILHO DA FASE 4: INVOCA O VÍDEO! ---
        caminho_video = self.rastrear_video(nome_jogo, rom_path)
        if hasattr(self, 'video_manager'):
            self.video_manager.focar_jogo(caminho_video, cover_image_obj=ctk_img)

        self.manual_atual = self.rastrear_manual(nome_jogo, rom_path)
        if self.manual_atual: self.btn_manual.configure(state="normal", fg_color="#4169E1")
        else: self.btn_manual.configure(state="disabled", fg_color="#333333")
        
        if self.index_menu == 1 and self.btn_manual.cget("state") == "disabled":
            self.index_menu = 0
        self.atualizar_foco_menu()

    def abrir_manual(self):
        if self.manual_atual and os.path.exists(self.manual_atual):
            try: 
                os.startfile(self.manual_atual)
                self.attributes("-topmost", False)
                self.iconify()
            except: pass

    def abrir_conquistas(self):
        nome_jogo = self.jogos[self.index_atual]
        self.game_manager.exibir_janela_conquistas(nome_jogo)

    def abrir_netplay(self):
        import netplay
        nome_jogo = self.jogos[self.index_atual]
        arquivos = self.game_manager.jogos_agrupados_cache[nome_jogo]
        netplay.NetplayManager(self, nome_jogo, arquivos[0], self.app.entry_path.get(), self.game_manager)

    def iniciar_jogo(self, event=None):
        if self.jogo_em_execucao: return 

        if hasattr(self, 'video_manager'):
            self.video_manager.parar_video()
        
        self.jogo_em_execucao = True 
        self.app.janela_bp = self
        nome_jogo = self.jogos[self.index_atual]
        arquivos = self.game_manager.jogos_agrupados_cache[nome_jogo]
        
        self.game_manager.selecionar_disco(nome_jogo, arquivos, from_bp=True)

    def sair(self):
        self.leitura_controle_ativa = False 
        self.radio.stop()
        if hasattr(self, 'video_manager'):
            self.video_manager.parar_video()
        self.destroy()
        self.app.deiconify()