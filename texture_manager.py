import os
import zipfile
import threading
import customtkinter as ctk
from customtkinter import filedialog
import tkinter.messagebox as mb

class TextureManager:
    def __init__(self, app_instance):
        self.app = app_instance

    def construir_interface(self, parent_frame):
        scroll_main = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        scroll_main.pack(fill="both", expand=True)

        lbl_title = ctk.CTkLabel(scroll_main, text="✨ Gerenciador de Texturas HD & Mods", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        lbl_desc = ctk.CTkLabel(scroll_main, text="Instale pacotes de texturas em alta resolução para remasterizar seus jogos no Flycast.", text_color="gray")
        lbl_desc.pack(anchor="w", padx=10, pady=(0, 15))

        # ==========================================
        # INSTALAÇÃO MANUAL (DROPZONE VIRTUAL)
        # ==========================================
        frame_manual = ctk.CTkFrame(scroll_main, fg_color="#1a1a1a", corner_radius=10)
        frame_manual.pack(fill="x", padx=10, pady=(0, 20))
        
        ctk.CTkLabel(frame_manual, text="📁 Instalação Local (Arquivo .ZIP)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        # A Dropzone Simulada (Botão gigante com borda tracejada)
        self.btn_dropzone = ctk.CTkButton(
            frame_manual, 
            text="📥 Clique aqui para selecionar o pacote de texturas (.ZIP)", 
            height=80, 
            fg_color="#2b2b2b", 
            hover_color="#333333", 
            border_width=2, 
            border_spacing=5,
            border_color="#4169E1",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.instalar_zip_local
        )
        self.btn_dropzone.pack(fill="x", padx=15, pady=(5, 15))

    def instalar_zip_local(self):
        arquivo_zip = ctk.filedialog.askopenfilename(
            title="Selecione o pacote de texturas", 
            filetypes=[("Arquivos ZIP", "*.zip")]
        )
        
        if not arquivo_zip: return
        
        install_path = self.app.entry_path.get()
        pasta_texturas = os.path.join(install_path, "textures")
        
        # Muda o estado do botão para avisar que está trabalhando
        self.btn_dropzone.configure(text="⏳ Extraindo texturas... Por favor, aguarde.", state="disabled", border_color="#FF8C00")
        
        def rotina_extracao():
            try:
                os.makedirs(pasta_texturas, exist_ok=True)
                # Extração silenciosa em background
                with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
                    zip_ref.extractall(pasta_texturas)
                
                self.app.log(f"✨ Texturas do arquivo '{os.path.basename(arquivo_zip)}' instaladas com sucesso em /textures!")
                self.app.after(0, lambda: self.app.mostrar_toast("Texturas Instaladas!", "O pacote HD foi extraído e está pronto para uso.", "success"))
            except Exception as e:
                self.app.log(f"❌ Erro ao extrair texturas: {e}")
                self.app.after(0, lambda: self.app.mostrar_toast("Erro", "O arquivo ZIP parece estar corrompido ou inacessível.", "error"))
            finally:
                # Restaura o botão ao estado original
                self.app.after(0, lambda: self.btn_dropzone.configure(text="📥 Clique aqui para selecionar o pacote de texturas (.ZIP)", state="normal", border_color="#4169E1"))

        # Inicia a thread operária para não travar a interface
        threading.Thread(target=rotina_extracao, daemon=True).start()