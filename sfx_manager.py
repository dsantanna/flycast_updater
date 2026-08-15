import os
import sys
import customtkinter as ctk

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

def obter_caminho_base():
    """Retorna o diretório mágico do PyInstaller ou a pasta local do projeto."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS 
    return os.path.dirname(os.path.abspath(__file__)) 

class SFXManager:
    def __init__(self, install_path):
        self.install_path = install_path
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
        # Pasta Customizada (onde o emulador está instalado)
        custom_dir = os.path.join(self.install_path, "media", "sfx")
        # Pasta Embutida (dentro do executável)
        bundled_dir = os.path.join(obter_caminho_base(), "media", "sfx")
        
        # Garante que a pasta customizada exista para o usuário
        os.makedirs(custom_dir, exist_ok=True)
        
        sfx_files = {
            "hover": "nav.wav",      
            "success": "save.wav",   
            "error": "error.wav",    
            "start": "start.wav"     
        }
        
        for name, filename in sfx_files.items():
            custom_path = os.path.join(custom_dir, filename)
            bundled_path = os.path.join(bundled_dir, filename)
            
            # MAGIA DO FALLBACK: Tenta o customizado primeiro. Se não existir, pega o oficial embutido!
            filepath = custom_path if os.path.exists(custom_path) else bundled_path
            
            if os.path.exists(filepath):
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                    self.sounds[name].set_volume(0.5) 
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
                if isinstance(widget, ctk.CTkButton):
                    if widget.cget("text") not in botoes_ignorados:
                        widget.bind("<Enter>", lambda e: self.play("hover"), add="+")
                elif isinstance(widget, ctk.CTkSwitch) or isinstance(widget, ctk.CTkRadioButton):
                    widget.bind("<Enter>", lambda e: self.play("hover"), add="+")
                
                varrer_widgets(widget) 
                
        varrer_widgets(widget_root)