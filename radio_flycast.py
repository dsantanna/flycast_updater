import os
import random
import pygame
import customtkinter as ctk

class RadioFlycast:
    def __init__(self, app_instance=None):
        self.app = app_instance
        self.playlist = []
        self.current_track_index = 0
        self.is_playing = False
        self.is_paused = False
        self.volume_atual = 0.5
        
        # Referências da Interface Gráfica
        self.frame_player = None
        self.lbl_now_playing = None
        self.btn_radio_play = None
        
        try:
            pygame.mixer.init()
        except Exception as e:
            if self.app: self.app.log(f"❌ Erro ao iniciar motor de áudio: {e}")

    def construir_player_ui(self, parent, row, column):
        """Constrói o Mini-Player nativamente na interface"""
        self.frame_player = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=8)
        self.frame_player.grid(row=row, column=column, padx=(10, 0), sticky="e")
        
        self.lbl_now_playing = ctk.CTkLabel(self.frame_player, text="🎵 Rádio Parada", font=ctk.CTkFont(size=11), width=160, anchor="center")
        self.lbl_now_playing.pack(side="top", padx=10, pady=(2, 0))

        frame_controls = ctk.CTkFrame(self.frame_player, fg_color="transparent")
        frame_controls.pack(side="top", pady=(0, 2))

        btn_prev = ctk.CTkButton(frame_controls, text="⏮", width=30, height=20, fg_color="transparent", hover_color="#333", command=self.ui_prev_track)
        btn_prev.pack(side="left", padx=2)

        self.btn_radio_play = ctk.CTkButton(frame_controls, text="▶", width=30, height=20, fg_color="transparent", hover_color="#333", command=self.ui_play_pause)
        self.btn_radio_play.pack(side="left", padx=2)

        btn_stop = ctk.CTkButton(frame_controls, text="⏹", width=30, height=20, fg_color="transparent", hover_color="#333", command=self.ui_stop)
        btn_stop.pack(side="left", padx=2)

        btn_next = ctk.CTkButton(frame_controls, text="⏭", width=30, height=20, fg_color="transparent", hover_color="#333", command=self.ui_next_track)
        btn_next.pack(side="left", padx=2)

    def iniciar_radio(self):
        if not self.app: return
        if self.app.config_atual.get("radio_on", False):
            self.carregar_playlist(self.app.entry_path.get())
            self.play()
            self.is_playing = True
            self.is_paused = False
            self.app.log("📻 Rádio Ambiente (Modulada) iniciada.")
            self.atualizar_interface()
            if self.btn_radio_play: self.btn_radio_play.configure(text="⏸")

    def toggle_radio(self):
        if not self.app: return
        if getattr(self.app, 'switch_radio', None) and self.app.switch_radio.get() == 1:
            install_path = self.app.entry_path.get()
            media_dir = os.path.join(install_path, "media", "music")
            
            if not os.path.exists(media_dir):
                try:
                    os.makedirs(media_dir, exist_ok=True)
                    self.app.mostrar_toast("Rádio Ambiente", "A pasta 'media/music' foi criada! Copie suas músicas para lá.", "success")
                except: pass
            
            self.app.config_atual["radio_on"] = True
            self.iniciar_radio()
        else:
            self.app.config_atual["radio_on"] = False
            self.ui_stop()
        self.app.salvar_estado_atual()

    def ui_play_pause(self):
        # Se clicar no play, mas o switch global estiver desligado, ele liga sozinho!
        if getattr(self.app, 'switch_radio', None) and self.app.switch_radio.get() == 0:
            self.app.switch_radio.select()
            self.toggle_radio()
            return

        if self.is_playing:
            if not self.is_paused:
                self.pause()
                self.is_paused = True
                if self.btn_radio_play: self.btn_radio_play.configure(text="▶")
                if self.lbl_now_playing: self.lbl_now_playing.configure(text="🎵 Rádio Pausada")
                if self.app: self.app.log("📻 Rádio: Pausada.")
            else:
                self.play()
                self.is_paused = False
                if self.btn_radio_play: self.btn_radio_play.configure(text="⏸")
                self.atualizar_interface()
                if self.app: self.app.log("📻 Rádio: Retomada.")
        else:
            if self.app and not self.playlist:
                self.carregar_playlist(self.app.entry_path.get())
            self.play()
            self.is_playing = True
            self.is_paused = False
            if self.btn_radio_play: self.btn_radio_play.configure(text="⏸")
            self.atualizar_interface()
            if self.app: self.app.log("📻 Rádio: Iniciada.")

    def ui_stop(self):
        self.stop()
        self.is_playing = False
        self.is_paused = False
        
        if getattr(self.app, 'switch_radio', None) and self.app.switch_radio.get() == 1:
            self.app.switch_radio.deselect()
            self.app.config_atual["radio_on"] = False
            self.app.salvar_estado_atual()
            
        if self.btn_radio_play: self.btn_radio_play.configure(text="▶")
        if self.lbl_now_playing: self.lbl_now_playing.configure(text="🎵 Rádio Parada")
        if self.app: self.app.log("📻 Rádio: Parada.")

    def ui_next_track(self):
        self.next_track()
        self.is_playing = True
        self.is_paused = False
        if self.btn_radio_play: self.btn_radio_play.configure(text="⏸")
        self.atualizar_interface()
        if self.app: self.app.log("📻 Rádio: Próxima faixa.")

    def ui_prev_track(self):
        self.prev_track()
        self.is_playing = True
        self.is_paused = False
        if self.btn_radio_play: self.btn_radio_play.configure(text="⏸")
        self.atualizar_interface()
        if self.app: self.app.log("📻 Rádio: Faixa anterior.")

    def atualizar_interface(self):
        if self.lbl_now_playing:
            titulo = self.obter_titulo_atual()
            nome_curto = titulo[:22] + "..." if len(titulo) > 22 else titulo
            self.lbl_now_playing.configure(text=f"🎵 {nome_curto}")
            try:
                from launcher import ToolTip
                if hasattr(self.lbl_now_playing, '_tooltip'):
                    self.lbl_now_playing._tooltip.update_text(titulo)
                else:
                    self.lbl_now_playing._tooltip = ToolTip(self.lbl_now_playing, titulo)
            except Exception: pass

    # ==========================================
    # LÓGICA DE ÁUDIO NATIVA (ID3 e Engine)
    # ==========================================
    def carregar_playlist(self, install_path):
        pastas_alvo = [
            os.path.join(install_path, "media"),
            os.path.join(install_path, "media", "music"),
            os.path.join(install_path, "music")
        ]
        self.playlist = []
        pasta_padrao = pastas_alvo[0]
        for pasta in pastas_alvo:
            if os.path.exists(pasta):
                for file in os.listdir(pasta):
                    if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                        caminho_arquivo = os.path.join(pasta, file)
                        if caminho_arquivo not in self.playlist:
                            self.playlist.append(caminho_arquivo)
        if self.playlist:
            random.shuffle(self.playlist)
        else:
            os.makedirs(pasta_padrao, exist_ok=True)

    def obter_titulo_atual(self):
        if not self.playlist: return "Rádio Parada"
        caminho_arquivo = self.playlist[self.current_track_index]
        nome_arquivo_limpo = os.path.splitext(os.path.basename(caminho_arquivo))[0]
        
        if caminho_arquivo.lower().endswith('.mp3'):
            try:
                with open(caminho_arquivo, 'rb') as f:
                    f.seek(-128, os.SEEK_END)
                    tag = f.read(128)
                    if tag[:3] == b'TAG':
                        titulo = tag[3:33].decode('latin1', errors='ignore').strip()
                        if titulo: return titulo
            except: pass
            try:
                with open(caminho_arquivo, 'rb') as f:
                    header = f.read(10)
                    if header[:3] == b'ID3':
                        content = f.read(2048)
                        idx = content.find(b'TIT2')
                        if idx != -1:
                            size_bytes = content[idx+4:idx+8]
                            size = sich = 0
                            for b in size_bytes: size = (size << 7) + b
                            title_bytes = content[idx+10:idx+10+min(size-1, 100)]
                            titulo = title_bytes.decode('utf-8', errors='ignore').replace('\x00', '').strip()
                            if titulo: return titulo
            except: pass
        return nome_arquivo_limpo

    def play(self, force_reload=False):
        if not self.playlist: return
        try:
            if force_reload or (not pygame.mixer.music.get_busy() and not self.is_playing):
                pygame.mixer.music.load(self.playlist[self.current_track_index])
                pygame.mixer.music.set_volume(self.volume_atual) 
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
        except: pass

    def pause(self):
        try: pygame.mixer.music.pause()
        except: pass

    def next_track(self):
        if not self.playlist: return
        try: pygame.mixer.music.stop()
        except: pass
        self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
        self.play(force_reload=True)

    def prev_track(self):
        if not self.playlist: return
        try: pygame.mixer.music.stop()
        except: pass
        self.current_track_index = (self.current_track_index - 1) % len(self.playlist)
        self.play(force_reload=True)

    def stop(self):
        try: pygame.mixer.music.stop()
        except: pass
        
    def set_volume(self, volume):
        self.volume_atual = float(volume)
        try: pygame.mixer.music.set_volume(self.volume_atual)
        except: pass