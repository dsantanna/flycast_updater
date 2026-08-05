import sys
import os

# --- INTERCEPTADOR NOGUI ---
# Se o usuário quiser apenas o terminal, pulamos a interface gráfica instantaneamente.
args_lower = [arg.lower() for arg in sys.argv]
if "-nogui" in args_lower:
    import launcher
    launcher.main()
    sys.exit(0)

# Se não tem -nogui, carregamos a interface gráfica!
import customtkinter as ctk
import threading
import json
import launcher
import update_flycast
try:
    import cloud_saves
except ImportError:
    cloud_saves = None

# Configuração visual padrão (Dark Mode)
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue") 

class ConsoleRedirector:
    """Captura os prints do motor e envia para a Interface Gráfica de forma segura."""
    def __init__(self, app):
        self.app = app

    def write(self, message):
        texto = message.strip()
        if not texto:
            return
            
        # Se for a linha de progresso, extraímos a porcentagem para a barra
        if "[*] Progresso:" in texto:
            try:
                # O formato é: [*] Progresso: |███...| 45% (2.3 MB / 5.0 MB)
                pct_str = texto.split("%")[0].split(" ")[-1]
                pct_float = float(pct_str) / 100.0
                
                # Atualiza a barra e o texto na thread da GUI
                self.app.after(0, self.app.progressbar.set, pct_float)
                self.app.after(0, self.app.label_status.configure, {"text": f"Baixando: {texto.split('(')[1].replace(')', '')} - {pct_str}%"})
            except Exception:
                pass
        else:
            # Qualquer outro print vira o texto de status
            self.app.after(0, self.app.label_status.configure, {"text": texto})
            
    def flush(self):
        pass

class FlycastUpdaterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🌀 Flycast Updater - v2.0 (GUI)")
        self.geometry("550x550")
        self.resizable(False, False)

        # Carrega preferências antigas, se existirem
        self.config_atual = launcher.carregar_configuracao()

        # --- TÍTULO ---
        self.label_titulo = ctk.CTkLabel(self, text="Flycast Auto-Updater", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_titulo.pack(pady=(20, 5))

        self.label_sub = ctk.CTkLabel(self, text="Gerenciador de Atualizações e Cloud Saves", text_color="gray")
        self.label_sub.pack(pady=(0, 20))

        # --- FRAME PRINCIPAL ---
        self.frame_opcoes = ctk.CTkFrame(self)
        self.frame_opcoes.pack(pady=10, padx=40, fill="both", expand=True)

        # 1. Escolha da Branch
        self.label_branch = ctk.CTkLabel(self.frame_opcoes, text="Versão do Emulador:", font=ctk.CTkFont(weight="bold"))
        self.label_branch.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.combo_branch = ctk.CTkComboBox(self.frame_opcoes, values=["Master", "Dev"])
        self.combo_branch.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="e")
        branch_salva = self.config_atual.get("branch", "dev").capitalize()
        self.combo_branch.set(branch_salva)

        # 2. Cloud Saves
        self.label_cloud = ctk.CTkLabel(self.frame_opcoes, text="Backup na Nuvem:", font=ctk.CTkFont(weight="bold"))
        self.label_cloud.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.combo_cloud = ctk.CTkComboBox(self.frame_opcoes, values=["Nenhum", "Google Drive", "OneDrive"])
        self.combo_cloud.grid(row=1, column=1, padx=20, pady=10, sticky="e")
        nuvem_salva = self.config_atual.get("cloud_provider", "nenhum")
        if nuvem_salva == "gdrive": self.combo_cloud.set("Google Drive")
        elif nuvem_salva == "onedrive": self.combo_cloud.set("OneDrive")
        else: self.combo_cloud.set("Nenhum")

        # 3. Switches (Atalhos)
        self.switch_desktop = ctk.CTkSwitch(self.frame_opcoes, text="Criar Atalho no Desktop")
        self.switch_desktop.grid(row=2, column=0, columnspan=2, padx=20, pady=15, sticky="w")
        if self.config_atual.get("create_shortcut", False): self.switch_desktop.select()

        self.switch_startup = ctk.CTkSwitch(self.frame_opcoes, text="Iniciar com o Windows (Silencioso)")
        self.switch_startup.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="w")
        if self.config_atual.get("create_startup", False): self.switch_startup.select()

        # --- PROGRESSO (Escondido por padrão) ---
        self.progressbar = ctk.CTkProgressBar(self, width=400)
        self.progressbar.set(0)
        
        self.label_status = ctk.CTkLabel(self, text="Aguardando...", text_color="cyan")

        # --- BOTÃO DE ATUALIZAR ---
        self.btn_atualizar = ctk.CTkButton(self, text="🚀 ATUALIZAR FLYCAST", height=40, font=ctk.CTkFont(weight="bold"), command=self.disparar_atualizacao)
        self.btn_atualizar.pack(pady=20)

    def disparar_atualizacao(self):
        """Prepara a interface e inicia a thread do motor para não travar a janela."""
        self.btn_atualizar.configure(state="disabled", text="PROCESSANDO...")
        
        # Exibe a barra de progresso
        self.progressbar.pack(pady=(10, 0))
        self.label_status.pack(pady=(5, 10))
        
        # Roda o motor em background
        threading.Thread(target=self.rodar_motor, daemon=True).start()

    def rodar_motor(self):
        """Faz a ponte entre as escolhas da GUI e o motor original."""
        # 1. Redireciona o terminal para a nossa interface
        terminal_original = sys.stdout
        sys.stdout = ConsoleRedirector(self)

        try:
            # 2. Configura as variáveis do motor baseadas na interface
            branch_escolhida = self.combo_branch.get().lower()
            criar_desktop = self.switch_desktop.get() == 1
            criar_startup = self.switch_startup.get() == 1
            
            nuvem_escolhida = self.combo_cloud.get()
            cloud_prov = None
            cloud_path = None
            
            if nuvem_escolhida == "Google Drive" and cloud_saves:
                cloud_prov = "gdrive"
                cloud_path = cloud_saves.get_gdrive_path()
            elif nuvem_escolhida == "OneDrive" and cloud_saves:
                cloud_prov = "onedrive"
                cloud_path = cloud_saves.get_onedrive_path()

            install_path = self.config_atual.get("install_path", os.getcwd())

            # Salva no config.json
            launcher.salvar_configuracao(branch_escolhida, criar_desktop, criar_startup, install_path, cloud_prov, cloud_path)

            # 3. Injeta os dados no motor (Monkeypatching)
            update_flycast.SCRIPT_VERSION = "2.0 (GUI)"
            update_flycast.INSTALL_DIR = install_path
            update_flycast.SHOULD_CREATE_SHORTCUT = criar_desktop
            update_flycast.SHOULD_CREATE_STARTUP = criar_startup
            update_flycast.CLOUD_PROVIDER = cloud_prov
            update_flycast.CLOUD_PATH = cloud_path
            update_flycast.VERSION_FILE = os.path.join(install_path, "version.txt")
            update_flycast.LOG_FILE = os.path.join(install_path, "flycast_updater.log")
            update_flycast.get_user_preference = lambda: branch_escolhida

            # 4. Aciona a ignição do motor original
            update_flycast.main()

        except Exception as e:
            self.after(0, self.label_status.configure, {"text": f"Erro crítico: {e}", "text_color": "red"})
        finally:
            # Restaura o terminal original e rehabilita o botão
            sys.stdout = terminal_original
            self.after(0, self.btn_atualizar.configure, {"state": "normal", "text": "ATUALIZAÇÃO CONCLUÍDA"})

if __name__ == "__main__":
    app = FlycastUpdaterApp()
    app.mainloop()