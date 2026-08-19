import os
import json
import urllib.request
import urllib.parse
import threading
import time
import customtkinter as ctk

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class RetroAchievementsManager:
    def __init__(self, app_instance):
        self.app = app_instance
        self.base_url = "https://retroachievements.org/API/"
        self.img_refs = [] 
        self.cache_dir = None 
        self.monitorando = False
        self.conquistas_desbloqueadas_iniciais = set()

    def _obter_credenciais(self):
        try:
            usuario = self.app.entry_ra_user.get().strip()
            api_key = self.app.config_atual.get("ra_api_key", "").strip()
            if not self.cache_dir:
                self.cache_dir = os.path.join(self.app.entry_path.get(), "data", "ra_cache")
                os.makedirs(self.cache_dir, exist_ok=True)
            return usuario, api_key
        except Exception:
            return "", ""

    def construir_aba_global(self, frame_pai):
        self.frame_pai = frame_pai
        
        self.frame_header = ctk.CTkFrame(frame_pai, fg_color="#1a1a2e", corner_radius=10)
        self.frame_header.pack(fill="x", padx=15, pady=(15, 10))
        
        self.lbl_avatar = ctk.CTkLabel(self.frame_header, text="👤", font=ctk.CTkFont(size=40))
        self.lbl_avatar.pack(side="left", padx=15, pady=10)
        
        self.frame_user_info = ctk.CTkFrame(self.frame_header, fg_color="transparent")
        self.frame_user_info.pack(side="left", fill="both", expand=True, pady=10)
        
        self.lbl_user_nome = ctk.CTkLabel(self.frame_user_info, text="Conecte sua conta...", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_user_nome.pack(anchor="w")
        
        self.lbl_user_stats = ctk.CTkLabel(self.frame_user_info, text="Pontos: 0 | Rank: ---", font=ctk.CTkFont(size=14), text_color="#FFD700")
        self.lbl_user_stats.pack(anchor="w")
        
        self.btn_refresh = ctk.CTkButton(self.frame_header, text="🔄 Sincronizar Painel", width=120, command=lambda: self.carregar_dados_globais(silencioso=False))
        self.btn_refresh.pack(side="right", padx=15)

        self.lbl_recent_title = ctk.CTkLabel(frame_pai, text="🎮 Jogados Recentemente (Global)", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_recent_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.scroll_cards = ctk.CTkScrollableFrame(frame_pai, fg_color="transparent")
        self.scroll_cards.pack(fill="both", expand=True, padx=5, pady=5)

    def carregar_dados_globais(self, silencioso=False):
        usuario, api_key = self._obter_credenciais()
        if not usuario or not api_key:
            if not silencioso: self.app.mostrar_toast("Aviso", "Configure o Usuário e a Web API Key primeiro.", "warning")
            return
            
        self.btn_refresh.configure(state="disabled", text="⏳ Carregando...")
        for widget in self.scroll_cards.winfo_children(): widget.destroy()
        self.img_refs.clear()

        prefixo_log = "[AUTO] " if silencioso else "[MANUAL] "
        self.app.log(f"🏆 RetroAchievements: {prefixo_log}Iniciando sincronização global...")

        def rotina():
            from launcher import VERSION
            try:
                url_sum = f"{self.base_url}API_GetUserSummary.php?z={urllib.parse.quote(usuario)}&y={api_key}&u={urllib.parse.quote(usuario)}"
                req_sum = urllib.request.Request(url_sum, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
                with urllib.request.urlopen(req_sum, timeout=5) as resp:
                    data_sum = json.loads(resp.read().decode('utf-8'))
                
                pts, rank, avatar_url = data_sum.get("TotalPoints", "0"), data_sum.get("Rank", "---"), data_sum.get("UserPic", "")
                
                self.app.after(0, lambda: self.lbl_user_nome.configure(text=usuario))
                self.app.after(0, lambda: self.lbl_user_stats.configure(text=f"💎 Pontos: {pts}  |  🌍 Rank Global: {rank}"))
                self.app.log("✔️ RA Global: Resumo do perfil baixado com sucesso.")
                
                if HAS_PIL and avatar_url:
                    avatar_path = os.path.join(self.cache_dir, "avatar.png")
                    url_pic = f"https://media.retroachievements.org{avatar_url}"
                    try:
                        req_pic = urllib.request.Request(url_pic, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req_pic, timeout=3) as r_pic, open(avatar_path, 'wb') as f_pic:
                            f_pic.write(r_pic.read())
                        img_pil = Image.open(avatar_path).resize((50, 50), Image.Resampling.LANCZOS)
                        img_ctk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(50, 50))
                        self.img_refs.append(img_ctk)
                        self.app.after(0, lambda: self.lbl_avatar.configure(image=img_ctk, text=""))
                    except: pass

                url_rec = f"{self.base_url}API_GetUserRecentlyPlayedGames.php?z={urllib.parse.quote(usuario)}&y={api_key}&u={urllib.parse.quote(usuario)}&c=20"
                req_rec = urllib.request.Request(url_rec, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
                with urllib.request.urlopen(req_rec, timeout=8) as resp:
                    jogos_recentes = json.loads(resp.read().decode('utf-8'))

                self.app.log(f"✔️ RA Global: {len(jogos_recentes)} jogos recentes encontrados.")
                self.app.after(0, lambda: self._desenhar_cards_recentes(jogos_recentes))

            except Exception as e:
                self.app.log(f"❌ Erro na API do RetroAchievements: {e}")
                if not silencioso: self.app.after(0, lambda: self.app.mostrar_toast("Erro", "Falha de Conexão.", "error"))
            finally:
                self.app.after(0, lambda: self.btn_refresh.configure(state="normal", text="🔄 Sincronizar Painel"))

        threading.Thread(target=rotina, daemon=True).start()

    def _desenhar_cards_recentes(self, lista_jogos):
        tema_atual = self.app.config_atual.get("tema", "Padrão DARK")
        try:
            from launcher import THEMES
            cor_primaria = THEMES.get(tema_atual, THEMES["Padrão DARK"])["primary"]
            cor_hover = THEMES.get(tema_atual, THEMES["Padrão DARK"])["hover"]
        except ImportError:
            cor_primaria, cor_hover = "#4169E1", "#1E90FF"

        for jogo in lista_jogos:
            game_id, title, console, icon_url = jogo.get("GameID"), jogo.get("Title", "Jogo"), jogo.get("ConsoleName", "Console"), jogo.get("ImageIcon", "")
            ach_ganhos, ach_totais = int(jogo.get("NumAchieved", 0)), int(jogo.get("NumPossibleAchievements", 1))
            pts_ganhos, pts_totais = jogo.get("ScoreAchieved", "0"), jogo.get("PossibleScore", "0")
            pct = ach_ganhos / ach_totais if ach_totais > 0 else 0
            
            card = ctk.CTkFrame(self.scroll_cards, fg_color="#2b2b2b", corner_radius=8)
            card.pack(fill="x", padx=10, pady=6)
            
            lbl_icon = ctk.CTkLabel(card, text="🎮", font=ctk.CTkFont(size=40), width=80, height=80)
            lbl_icon.pack(side="left", padx=10, pady=10)
            
            if HAS_PIL and icon_url:
                icon_file = os.path.basename(icon_url)
                icon_path = os.path.join(self.cache_dir, icon_file)
                def baixar_icon(u=icon_url, p=icon_path, l=lbl_icon):
                    if not os.path.exists(p):
                        try:
                            full_url = f"https://media.retroachievements.org{u}"
                            req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req, timeout=3) as r, open(p, 'wb') as f: f.write(r.read())
                        except: return
                    try:
                        img = Image.open(p).resize((70, 70), Image.Resampling.LANCZOS)
                        ctk_i = ctk.CTkImage(light_image=img, dark_image=img, size=(70, 70))
                        self.img_refs.append(ctk_i)
                        self.app.after(0, lambda: l.configure(image=ctk_i, text=""))
                    except: pass
                threading.Thread(target=baixar_icon, daemon=True).start()

            frame_info = ctk.CTkFrame(card, fg_color="transparent")
            frame_info.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(frame_info, text=title, font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(frame_info, text=console, font=ctk.CTkFont(size=12, slant="italic"), text_color="gray", anchor="w").pack(fill="x", pady=(0, 5))
            
            pb = ctk.CTkProgressBar(frame_info, progress_color=cor_primaria, height=8)
            pb.pack(fill="x", pady=(5, 5))
            pb.set(pct)
            
            ctk.CTkLabel(frame_info, text=f"{int(pct*100)}%  |  {ach_ganhos}/{ach_totais} Troféus  |  {pts_ganhos}/{pts_totais} Pontos", font=ctk.CTkFont(size=11, weight="bold"), text_color="#00FF7F", anchor="w").pack(fill="x")

            btn_detalhes = ctk.CTkButton(card, text="Ver Conquistas", fg_color=cor_primaria, hover_color=cor_hover, font=ctk.CTkFont(weight="bold"),
                                         command=lambda gid=game_id, n=title: self.abrir_detalhes_jogo_global(gid, n))
            btn_detalhes.pack(side="right", padx=15)

    def abrir_detalhes_jogo_global(self, game_id, nome_jogo):
        from launcher import VERSION
        usuario, api_key = self._obter_credenciais()
        win_ra = ctk.CTkToplevel(self.app)
        win_ra.title(f"🏆 Galeria: {nome_jogo}")
        win_ra.geometry("780x680")
        win_ra.attributes("-topmost", True)
        win_ra.grab_set() 
        
        lbl_status = ctk.CTkLabel(win_ra, text="⏳ Baixando detalhes do jogo...", font=ctk.CTkFont(size=16))
        lbl_status.pack(expand=True)

        def rotina_carregamento():
            try:
                url_prog = f"{self.base_url}API_GetGameInfoAndUserProgress.php?z={urllib.parse.quote(usuario)}&y={api_key}&u={urllib.parse.quote(usuario)}&g={game_id}"
                req = urllib.request.Request(url_prog, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    game_data = json.loads(response.read().decode('utf-8'))
            except Exception as e:
                self.app.after(0, lambda: lbl_status.configure(text=f"❌ Erro de conexão: {e}"))
                return

            achievements = game_data.get("Achievements", {})
            if not achievements:
                self.app.after(0, lambda: lbl_status.configure(text="⚠️ Este jogo não possui conquistas cadastradas."))
                return
            
            lista_achs = sorted(list(achievements.values()), key=lambda x: int(x.get("DisplayOrder", 0)))
            self.app.after(0, lbl_status.destroy)
            
            tema_atual = self.app.config_atual.get("tema", "Padrão DARK")
            from launcher import THEMES
            cor_primaria = THEMES.get(tema_atual, THEMES["Padrão DARK"]).get("primary", "#4169E1")
            
            def desenhar_ui():
                trofeus_totais, trofeus_ganhos, pontos_totais, pontos_ganhos = len(lista_achs), 0, 0, 0
                for ach in lista_achs:
                    pts = int(ach.get("Points", "0"))
                    pontos_totais += pts
                    if ach.get("DateEarned"):
                        trofeus_ganhos += 1; pontos_ganhos += pts
                        
                progresso_pct = (trofeus_ganhos / trofeus_totais) if trofeus_totais > 0 else 0
                
                frame_dash = ctk.CTkFrame(win_ra, fg_color="#1a1a1a", corner_radius=10)
                frame_dash.pack(fill="x", padx=10, pady=(10, 5))
                
                ctk.CTkLabel(frame_dash, text=f"Progresso Geral: {int(progresso_pct * 100)}%", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 0))
                
                bar_progresso = ctk.CTkProgressBar(frame_dash, progress_color=cor_primaria, width=700)
                bar_progresso.pack(fill="x", padx=15, pady=10)
                bar_progresso.set(progresso_pct)
                
                ctk.CTkLabel(frame_dash, text=f"🏆 Troféus: {trofeus_ganhos}/{trofeus_totais}   |   💎 Pontos: {pontos_ganhos}/{pontos_totais}", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="e", padx=15, pady=(0, 10))
                
                scroll = ctk.CTkScrollableFrame(win_ra, fg_color="transparent")
                scroll.pack(fill="both", expand=True, padx=5, pady=5)
                
                ach_dir = os.path.join(self.app.entry_path.get(), "data", "achievements")
                os.makedirs(ach_dir, exist_ok=True)
                
                for ach in lista_achs:
                    title, desc, pts, badge, date_earned = ach.get("Title", ""), ach.get("Description", ""), ach.get("Points", "0"), ach.get("BadgeName", ""), ach.get("DateEarned")
                    is_unlocked = date_earned is not None
                    
                    frame_ach = ctk.CTkFrame(scroll, fg_color="#1a1a2e" if is_unlocked else "#2b2b2b", corner_radius=8)
                    frame_ach.pack(fill="x", pady=5, padx=5)
                    
                    badge_file = f"{badge}.png" if is_unlocked else f"{badge}_lock.png"
                    badge_path = os.path.join(ach_dir, badge_file)
                    
                    if not os.path.exists(badge_path):
                        try:
                            req_img = urllib.request.Request(f"https://media.retroachievements.org/Badge/{badge_file}", headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req_img, timeout=3) as resp_img, open(badge_path, 'wb') as f_img: f_img.write(resp_img.read())
                        except: pass
                    
                    if HAS_PIL and os.path.exists(badge_path):
                        try:
                            img = Image.open(badge_path).resize((64, 64), Image.Resampling.LANCZOS)
                            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(64, 64))
                            self.img_refs.append(ctk_img)
                            ctk.CTkLabel(frame_ach, image=ctk_img, text="").pack(side="left", padx=10, pady=10)
                        except: pass
                    else: ctk.CTkLabel(frame_ach, text="🏆", font=ctk.CTkFont(size=30)).pack(side="left", padx=15, pady=10)
                        
                    frame_text = ctk.CTkFrame(frame_ach, fg_color="transparent")
                    frame_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                    
                    ctk.CTkLabel(frame_text, text=title, font=ctk.CTkFont(size=16, weight="bold"), text_color=cor_primaria if is_unlocked else "gray", anchor="w").pack(fill="x")
                    ctk.CTkLabel(frame_text, text=desc, font=ctk.CTkFont(size=12), text_color="#AAAAAA", anchor="w", justify="left").pack(fill="x")
                    ctk.CTkLabel(frame_text, text=f"💎 {pts} pts", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFD700" if is_unlocked else "#888888", anchor="w").pack(fill="x", pady=(5,0))
                    
                    if is_unlocked:
                        data_f = date_earned[:10].split("-")
                        ctk.CTkLabel(frame_ach, text=f"✔️ {data_f[2]}/{data_f[1]}/{data_f[0]} às {date_earned[11:16]}", font=ctk.CTkFont(size=11, weight="bold"), text_color="#00FF7F").pack(side="right", padx=15)
                        
            self.app.after(0, desenhar_ui)

        threading.Thread(target=rotina_carregamento, daemon=True).start()

   # =========================================================
    # A MAGIA DE BOSS: O ESPIÃO DE GAMEPLAY (BACKGROUND TRACKER)
    # =========================================================
    def iniciar_rastreio_em_gameplay(self, nome_jogo):
        """Descobre o ID do jogo e solta o espião para rodar enquanto o emulador está aberto."""
        usuario, api_key = self._obter_credenciais()
        if not usuario or not api_key: return
        
        self.app.log(f"🔎 RA Rastreador: Tentando descobrir o ID de '{nome_jogo}' para o modo Overlay...")
        
        def iniciar_espiao():
            from launcher import VERSION
            game_id = None
            import re
            def simplificar(t): return re.sub(r'[^a-z0-9]', '', str(t).lower())
            s_jogo = simplificar(nome_jogo)

            try:
                # 1. Busca rápida nos jogos recentes do usuário
                url_rec = f"{self.base_url}API_GetUserRecentlyPlayedGames.php?z={urllib.parse.quote(usuario)}&y={api_key}&u={urllib.parse.quote(usuario)}&c=50"
                req = urllib.request.Request(url_rec, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    for g in json.loads(response.read().decode('utf-8')):
                        if simplificar(g.get("Title", "")) in s_jogo or s_jogo in simplificar(g.get("Title", "")):
                            game_id = g.get("GameID")
                            break
            except: pass

            # 🛡️ BUGFIX 1: Se o jogo for novo (nunca jogado), o ID é buscado na base Global de Dreamcast e Arcade!
            if not game_id:
                for console_id in [23, 27]:
                    if game_id: break
                    try:
                        url_list = f"{self.base_url}API_GetGameList.php?z={urllib.parse.quote(usuario)}&y={api_key}&i={console_id}"
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
                self.app.log(f"⚠️ RA Rastreador: ID do jogo não encontrado. O Overlay dinâmico não funcionará para este jogo.")
                return

            self.app.log(f"🟢 RA Rastreador: ID {game_id} encontrado! Inicializando captura do estado atual das conquistas...")
            
            # Fotografa quais conquistas você JÁ TEM para não notificar coisa velha!
            url_prog = f"{self.base_url}API_GetGameInfoAndUserProgress.php?z={urllib.parse.quote(usuario)}&y={api_key}&u={urllib.parse.quote(usuario)}&g={game_id}"
            try:
                req = urllib.request.Request(url_prog, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    prog_data = json.loads(response.read().decode('utf-8'))
                
                for ach in prog_data.get("Achievements", {}).values():
                    if ach.get("DateEarned"):
                        self.conquistas_desbloqueadas_iniciais.add(str(ach.get("ID")))
            except: pass

            self.monitorando = True
            self.app.log(f"🕵️ RA Espião: Entrando em modo Stealth... Polling a cada 15s engatilhado.")
            
            # O Loop de Espionagem:
            while self.monitorando:
                time.sleep(15) # Esquivando do limite da API (Hit-Kill)
                if not self.monitorando: break
                
                try:
                    # 🛡️ BUGFIX 2: Adiciona timestamp na URL para quebrar o Cache HTTP do Windows e forçar dados reais!
                    url_dinamica = f"{url_prog}&_t={time.time()}"
                    req_loop = urllib.request.Request(url_dinamica, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
                    with urllib.request.urlopen(req_loop, timeout=5) as resp_loop:
                        estado_atual = json.loads(resp_loop.read().decode('utf-8'))
                    
                    for ach in estado_atual.get("Achievements", {}).values():
                        a_id = str(ach.get("ID"))
                        if ach.get("DateEarned") and a_id not in self.conquistas_desbloqueadas_iniciais:
                            # ACONTECEU! UMA CONQUISTA NOVA!
                            self.conquistas_desbloqueadas_iniciais.add(a_id)
                            self.app.log(f"🏆 RA Rastreador: CONQUISTA DESBLOQUEADA EM TEMPO REAL: {ach.get('Title')}!")
                            
                            # --- DOWNLOAD INSTANTÂNEO DA ARTE COLORIDA ---
                            badge = ach.get("BadgeName", "")
                            if badge:
                                badge_file = f"{badge}.png"
                                badge_path = os.path.join(self.cache_dir, badge_file)
                                if not os.path.exists(badge_path):
                                    try:
                                        url_img = f"https://media.retroachievements.org/Badge/{badge_file}"
                                        req_img = urllib.request.Request(url_img, headers={'User-Agent': 'Mozilla/5.0'})
                                        with urllib.request.urlopen(req_img, timeout=3) as r, open(badge_path, 'wb') as f:
                                            f.write(r.read())
                                    except: pass
                            # ---------------------------------------------
                            
                            self.app.after(0, lambda a=ach: self.gerar_popup_animado(a))
                except Exception as e:
                    pass # <-- O Paraquedas que salva o nosso código do Crash!

        threading.Thread(target=iniciar_espiao, daemon=True).start()

    def parar_rastreio(self):
        self.monitorando = False
        self.conquistas_desbloqueadas_iniciais.clear()
        self.app.log(f"🛑 RA Espião: Jogo finalizado. Rastreador desativado.")

    def gerar_popup_animado(self, ach_data):
        """O cobiçado Overlay ao estilo Troféu de PlayStation 5."""
        if hasattr(self.app, 'sfx'): self.app.sfx.play("success") # Toca o som épico!

        # Janela invisível e sem bordas
        overlay = ctk.CTkToplevel(self.app)
        
        # 🛡️ BUGFIX 3: Desconecta a janela do "pai" (Big Blue invisível) e força ela a nascer livremente na tela!
        overlay.transient("") 
        
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.0)
        overlay.configure(fg_color="#0F0F16") 
        overlay.deiconify() # Tira a janela das sombras!

        # Borda dourada/primária da Barbie Customizada
        tema_atual = self.app.config_atual.get("tema", "Padrão DARK")
        from launcher import THEMES
        cor = THEMES.get(tema_atual, THEMES["Padrão DARK"]).get("primary", "#4169E1")

        frame_borda = ctk.CTkFrame(overlay, fg_color=cor, corner_radius=15)
        frame_borda.pack(fill="both", expand=True, padx=2, pady=2)

        frame_fundo = ctk.CTkFrame(frame_borda, fg_color="#181822", corner_radius=13)
        frame_fundo.pack(fill="both", expand=True, padx=2, pady=2)

        # Baixa a Badge rapidinho para colocar no popup
        badge_file = f"{ach_data.get('BadgeName')}.png"
        badge_path = os.path.join(self.cache_dir, badge_file) if self.cache_dir else ""
        
        lbl_img = ctk.CTkLabel(frame_fundo, text="🏆", font=ctk.CTkFont(size=35), width=64, height=64)
        lbl_img.pack(side="left", padx=10)

        if HAS_PIL and badge_path and os.path.exists(badge_path):
            try:
                img = Image.open(badge_path).resize((50, 50), Image.Resampling.LANCZOS)
                ctk_i = ctk.CTkImage(light_image=img, dark_image=img, size=(50, 50))
                lbl_img.configure(image=ctk_i, text="")
            except: pass

        frame_textos = ctk.CTkFrame(frame_fundo, fg_color="transparent")
        frame_textos.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(frame_textos, text="Conquista Desbloqueada!", font=ctk.CTkFont(size=10, weight="bold"), text_color="gray", anchor="w").pack(fill="x")
        ctk.CTkLabel(frame_textos, text=ach_data.get('Title', 'Conquista'), font=ctk.CTkFont(size=14, weight="bold"), text_color="white", anchor="w").pack(fill="x", pady=(2, 0))
        ctk.CTkLabel(frame_textos, text=f"💎 {ach_data.get('Points', '0')} Pontos", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFD700", anchor="w").pack(fill="x")

        # --- A FÍSICA DO POSICIONAMENTO ---
        monitor_str = self.app.combo_monitor.get() if hasattr(self.app, 'combo_monitor') else ""
        m_left, m_top = 0, 0
        sw, sh = overlay.winfo_screenwidth(), overlay.winfo_screenheight()
        
        if hasattr(self.app, 'lista_monitores'):
            for m in self.app.lista_monitores:
                if m['nome'] == monitor_str:
                    m_left, m_top = m['left'], m['top']
                    try:
                        dim = m['nome'].split('(')[1].split(')')[0]
                        sw, sh = int(dim.split('x')[0]), int(dim.split('x')[1])
                    except: pass
                    break

        w, h = 380, 85
        pos = self.app.config_atual.get("ra_overlay_pos", "Cima-Direita")
        pad = 25
        
        # O X e Y agora nascem a partir do monitor selecionado!
        if pos == "Cima-Esquerda": x, y = m_left + pad, m_top + pad
        elif pos == "Cima-Direita": x, y = m_left + sw - w - pad, m_top + pad
        elif pos == "Cima-Centro": x, y = m_left + (sw - w)//2, m_top + pad
        elif pos == "Baixo-Esquerda": x, y = m_left + pad, m_top + sh - h - pad
        elif pos == "Baixo-Direita": x, y = m_left + sw - w - pad, m_top + sh - h - pad
        else: x, y = m_left + (sw - w)//2, m_top + sh - h - pad # Baixo-Centro

        overlay.geometry(f"{w}x{h}+{x}+{y}")

        # --- A ANIMAÇÃO DO POPUP ---
        def fade_in(alpha=0.0):
            if alpha < 0.95:
                overlay.attributes("-alpha", alpha)
                overlay.after(30, fade_in, alpha + 0.1)
            else:
                overlay.after(6000, fade_out, 0.95) # Fica na tela por 6 segundos!
                
        def fade_out(alpha=0.95):
            if alpha > 0.0:
                overlay.attributes("-alpha", alpha)
                overlay.after(30, fade_out, alpha - 0.1)
            else:
                overlay.destroy()

        fade_in()

    def parar_rastreio(self):
        self.monitorando = False
        self.conquistas_desbloqueadas_iniciais.clear()
        self.app.log(f"🛑 RA Espião: Jogo finalizado. Rastreador desativado.")

    

def obter_token_retroachievements(usuario, senha_ou_hash):
    """
    Bate no endpoint oficial legado do RetroAchievements para validar as 
    credenciais e gerar o Token de acesso seguro de longa duração.
    """
    import urllib.request
    import urllib.parse
    import json
    
    # Puxa a versão em tempo real direto do arquivo principal para o cabeçalho
    try:
        from launcher import VERSION
    except ImportError:
        VERSION = "6.2"

    # A URL exata e consagrada que você usava no launcher!
    url = f"https://retroachievements.org/dorequest.php?r=login&u={urllib.parse.quote(usuario)}&p={urllib.parse.quote(senha_ou_hash)}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
        with urllib.request.urlopen(req, timeout=6) as response:
            resposta = json.loads(response.read().decode('utf-8'))
            
            # Valida o sucesso do login e extrai o Token de persistência
            if isinstance(resposta, dict) and resposta.get("Success") is True:
                return resposta.get("Token")
    except Exception:
        pass
    return None