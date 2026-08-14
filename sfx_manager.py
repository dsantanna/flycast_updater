import os
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
import customtkinter as ctk

class SFXManager:
    def __init__(self, install_path):
        self.sfx_dir = os.path.join(install_path, "media", "sfx")
        self.enabled = HAS_PYGAME
        self.sounds = {}
        
        if self.enabled:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                self._load_sounds()
            except Exception:
                self.enabled = False

    def _load_sounds(self):
        # Garante que a pasta exista para o usuário colocar os sons
        os.makedirs(self.sfx_dir, exist_ok=True)
        
        # Mapeia os arquivos esperados
        sfx_files = {
            "hover": "nav.wav",      # Passar o mouse / Mover controle
            "success": "save.wav",   # Som de moeda ou confirmar
            "error": "error.wav",    # Som de bloqueio / erro
            "start": "start.wav"     # Som épico ao iniciar o jogo
        }
        
        for name, filename in sfx_files.items():
            filepath = os.path.join(self.sfx_dir, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                    self.sounds[name].set_volume(0.5) # Volume padrão
                except: pass

    def play(self, sound_name):
        if self.enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except: pass

    def apply_hover_to_all_widgets(self, widget_root):
        """Varre toda a interface e injeta o som de hover sem poluir as classes principais."""
        if not self.enabled or "hover" not in self.sounds: return
        
        botoes_ignorados = ["X", "⭐", "?", "👁", "🙈", "⏮", "▶️ Play", "▶", "⏸ Pause", "⏹", "⏭"] 
        
        def varrer_widgets(pai):
            for widget in pai.winfo_children():
                # Injeta som em Botões
                if isinstance(widget, ctk.CTkButton):
                    if widget.cget("text") not in botoes_ignorados:
                        widget.bind("<Enter>", lambda e: self.play("hover"), add="+")
                
                # Injeta som em Switches e Radio Buttons
                elif isinstance(widget, ctk.CTkSwitch) or isinstance(widget, ctk.CTkRadioButton):
                    widget.bind("<Enter>", lambda e: self.play("hover"), add="+")
                
                # Busca recursiva para entrar nos Frames
                varrer_widgets(widget) 
                
        varrer_widgets(widget_root)