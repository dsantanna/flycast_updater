import customtkinter as ctk

class ToastNotification:
    def __init__(self, master, title, message, tipo="info", duracao=3000):
        self.top = ctk.CTkToplevel(master)
        # Remove as bordas padrão do Windows
        self.top.overrideredirect(True)
        self.top.attributes("-topmost", True)
        self.top.attributes("-alpha", 0.0) # Começa 100% invisível
        
        # Paleta de cores dinâmica baseada no tipo da notificação
        cores = {
            "success": ("#228B22", "✔️"), # Verde
            "error": ("#FF4C4C", "❌"),   # Vermelho
            "warning": ("#FFD700", "⚠️"), # Amarelo
            "info": ("#1E90FF", "ℹ️")     # Azul
        }
        cor_borda, icone = cores.get(tipo, cores["info"])
        
        self.top.configure(fg_color="#1a1a1a")
        
        # Frame principal com a borda colorida
        self.frame = ctk.CTkFrame(self.top, fg_color="#2b2b2b", border_width=2, border_color=cor_borda, corner_radius=10)
        self.frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.lbl_titulo = ctk.CTkLabel(self.frame, text=f"{icone} {title}", font=ctk.CTkFont(size=14, weight="bold"), text_color=cor_borda)
        self.lbl_titulo.pack(anchor="w", padx=15, pady=(10, 2))
        
        self.lbl_msg = ctk.CTkLabel(self.frame, text=message, font=ctk.CTkFont(size=12), justify="left", text_color="#CCCCCC", wraplength=260)
        self.lbl_msg.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Força o Tkinter a calcular o tamanho real do frame com o texto
        self.top.update_idletasks()
        largura = 300
        altura = self.top.winfo_reqheight() + 10
        
        # Posiciona a notificação no canto inferior direito do seu Monitor
        x = master.winfo_screenwidth() - largura - 30
        y = master.winfo_screenheight() - altura - 60
        self.top.geometry(f"{largura}x{altura}+{x}+{y}")
        
        # Engatilha a animação
        self.fade_in()
        self.top.after(duracao, self.fade_out)

    def fade_in(self):
        """Aparece suavemente."""
        try:
            alpha = self.top.attributes("-alpha")
            if alpha < 0.95:
                self.top.attributes("-alpha", alpha + 0.1)
                self.top.after(20, self.fade_in)
        except Exception: pass

    def fade_out(self):
        """Desaparece suavemente e se autodestrói."""
        try:
            alpha = self.top.attributes("-alpha")
            if alpha > 0:
                self.top.attributes("-alpha", alpha - 0.1)
                self.top.after(20, self.fade_out)
            else:
                self.top.destroy()
        except Exception: pass