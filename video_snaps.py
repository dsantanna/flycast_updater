import os
import cv2
from PIL import Image, ImageTk
import customtkinter as ctk

class VideoSnapManager:
    def __init__(self, widget_alvo, delay_ms=800):
        """
        :param widget_alvo: O CTkLabel onde a capa (e o vídeo) aparecem.
        :param delay_ms: Tempo em milissegundos para esperar antes de tocar (evita travamentos ao rolar a lista rápido).
        """
        self.widget = widget_alvo 
        self.delay_ms = delay_ms
        self.video_path = None
        self.cap = None
        self.is_playing = False
        self.after_id_delay = None
        self.after_id_frame = None
        self.cover_fallback = None

    def focar_jogo(self, caminho_video, cover_image_obj=None):
        """Chame isso quando o usuário parar o cursor em cima de um jogo."""
        self.parar_video()
        self.cover_fallback = cover_image_obj
        self.video_path = caminho_video
        
        # Garante que a capa estática está aparecendo
        if self.cover_fallback:
            self.widget.configure(image=self.cover_fallback)
        
        # Se o arquivo de vídeo existir, arma o gatilho para tocar daqui a X milissegundos!
        if self.video_path and os.path.exists(self.video_path):
            self.after_id_delay = self.widget.after(self.delay_ms, self._iniciar_reproducao)

    def _iniciar_reproducao(self):
        """Inicia a extração de frames do vídeo."""
        if not self.video_path or not os.path.exists(self.video_path): return
        
        self.cap = cv2.VideoCapture(self.video_path)
        self.is_playing = True
        self._tocar_frame()

    def _tocar_frame(self):
        """Lê um frame do vídeo e pinta no CTkLabel."""
        if not self.is_playing or not self.cap: return
        
        ret, frame = self.cap.read()
        
        # Se o vídeo acabou, rebobina e toca de novo (Loop infinito!)
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                self.parar_video()
                return

        # O OpenCV lê em BGR, mas a tela precisa ser RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Lê o tamanho atual do quadro na tela para o vídeo caber certinho
        w = self.widget.winfo_width()
        h = self.widget.winfo_height()
        if w < 10 or h < 10: w, h = 400, 400 # Tamanho de segurança
        
        img = Image.fromarray(frame_rgb).resize((w, h), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        
        self.widget.configure(image=img_tk)
        self.widget.image = img_tk # Protege contra o Garbage Collector do Python
        
        # Chama o próximo frame em ~33ms (o que dá aproximadamente 30 FPS)
        self.after_id_frame = self.widget.after(33, self._tocar_frame)

    def parar_video(self):
        """Mata o vídeo na hora e devolve a capa estática."""
        self.is_playing = False
        
        if self.after_id_delay:
            self.widget.after_cancel(self.after_id_delay)
            self.after_id_delay = None
            
        if self.after_id_frame:
            self.widget.after_cancel(self.after_id_frame)
            self.after_id_frame = None
            
        if self.cap:
            self.cap.release()
            self.cap = None
            
        if hasattr(self, 'cover_fallback') and self.cover_fallback:
            self.widget.configure(image=self.cover_fallback)