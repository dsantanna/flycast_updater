import os
import random
import pygame

class RadioFlycast:
    def __init__(self):
        self.playlist = []
        self.current_track_index = 0
        self.is_playing = False
        self.volume_atual = 0.5
        
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"❌ Erro ao iniciar motor de áudio: {e}")

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
            print(f"📻 Rádio Flycast: Playlist pronta com {len(self.playlist)} faixas!")
        else:
            os.makedirs(pasta_padrao, exist_ok=True)
            print(f"⚠️ Rádio Flycast: Silêncio... Nenhuma música encontrada em:\n📁 {pasta_padrao}")

    def obter_titulo_atual(self):
        if not self.playlist:
            return "Rádio Parada"
        
        caminho_arquivo = self.playlist[self.current_track_index]
        nome_arquivo_limpo = os.path.splitext(os.path.basename(caminho_arquivo))[0]
        
        # Leitor Nativo de ID3 Tag (Suporte a MP3 v1 e v2 sem bibliotecas externas)
        if caminho_arquivo.lower().endswith('.mp3'):
            try:
                with open(caminho_arquivo, 'rb') as f:
                    f.seek(-128, os.SEEK_END)
                    tag = f.read(128)
                    if tag[:3] == b'TAG':
                        # ID3v1 encontrado
                        titulo = tag[3:33].decode('latin1', errors='ignore').strip()
                        if titulo: return titulo
            except: pass
            
            try:
                # Tenta ler ID3v2 (Início do arquivo)
                with open(caminho_arquivo, 'rb') as f:
                    header = f.read(10)
                    if header[:3] == b'ID3':
                        # Leitor rápido para o frame TIT2 (Título)
                        content = f.read(2048)
                        idx = content.find(b'TIT2')
                        if idx != -1:
                            size_bytes = content[idx+4:idx+8]
                            # Converte o tamanho do frame ID3v2
                            size = sich = 0
                            for b in size_bytes:
                                size = (size << 7) + b
                            title_bytes = content[idx+10:idx+10+min(size-1, 100)]
                            # Remove bytes nulos e decodifica
                            titulo = title_bytes.decode('utf-8', errors='ignore').replace('\x00', '').strip()
                            if titulo: return titulo
            except: pass

        return nome_arquivo_limpo

    def play(self, force_reload=False):
        if not self.playlist:
            return
        
        try:
            if force_reload or (not pygame.mixer.music.get_busy() and not self.is_playing):
                pygame.mixer.music.load(self.playlist[self.current_track_index])
                pygame.mixer.music.set_volume(self.volume_atual) 
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            self.is_playing = True
        except: pass

    def pause(self):
        try:
            pygame.mixer.music.pause()
            self.is_playing = False
        except: pass

    def next_track(self):
        if not self.playlist: return
        try: pygame.mixer.music.stop()
        except: pass
        self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
        self.is_playing = False
        self.play(force_reload=True)

    def prev_track(self):
        if not self.playlist: return
        try: pygame.mixer.music.stop()
        except: pass
        self.current_track_index = (self.current_track_index - 1) % len(self.playlist)
        self.is_playing = False
        self.play(force_reload=True)

    def stop(self):
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
        except: pass
        
    def set_volume(self, volume):
        self.volume_atual = float(volume)
        try:
            pygame.mixer.music.set_volume(self.volume_atual)
        except: pass