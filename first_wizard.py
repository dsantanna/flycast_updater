import os
import customtkinter as ctk
import tkinter.messagebox as mb
import config_manager

class FirstRunWizard(ctk.CTkToplevel):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.app = app_instance
        
        self.title("Bem-vindo ao Flycast Updater (Big Blue)")
        self.geometry("650x530")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        
        self.grab_set()
        
        self.current_step = 0
        self.rom_paths = []
        
        # Variáveis de Controle
        self.var_lang = ctk.StringVar(value=self.app.lang)
        self.var_theme = ctk.StringVar(value="Padrão DARK")
        self.var_path = ctk.StringVar(value=os.path.normpath(os.getcwd()))
        self.var_branch = ctk.StringVar(value="dev")
        self.var_play_behavior = ctk.StringVar(value="Utilizar o Flycast Updater Launcher")
        self.var_ra_user = ctk.StringVar(value="")
        self.var_ra_pass = ctk.StringVar(value="")
        self.var_ra_api = ctk.StringVar(value="")
        self.var_ra_hardcore = ctk.BooleanVar(value=False)
        self.var_cloud = ctk.StringVar(value="nenhum")

        # Layout Principal
        self.frame_top = ctk.CTkFrame(self, height=60, fg_color="#1E90FF", corner_radius=0)
        self.frame_top.pack(fill="x", side="top")
        
        self.lbl_titulo = ctk.CTkLabel(self.frame_top, text="Assistente de Configuração Inicial", font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        self.lbl_titulo.pack(pady=15)

        self.frame_bottom = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.frame_bottom.pack(fill="x", side="bottom", padx=20, pady=10)

        self.frame_container = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.btn_back = ctk.CTkButton(self.frame_bottom, text="◀ Voltar", width=100, fg_color="#444", hover_color="#666", command=self.prev_step)
        self.btn_back.pack(side="left")

        self.btn_next = ctk.CTkButton(self.frame_bottom, text="Avançar ▶", width=100, font=ctk.CTkFont(weight="bold"), command=self.next_step)
        self.btn_next.pack(side="right")

        # Lista de Passos
        self.steps = []
        self.criar_passo_1()
        self.criar_passo_2()
        self.criar_passo_3()
        self.criar_passo_4()
        self.criar_passo_5()
        self.criar_passo_6() # NOVO: Passo extra condicional

        self.mostrar_passo(0)

    def criar_passo_1(self):
        frame = ctk.CTkFrame(self.frame_container, fg_color="transparent")
        self.steps.append(frame)
        
        lbl = ctk.CTkLabel(frame, text="👋 Olá, Player 1!", font=ctk.CTkFont(size=24, weight="bold"))
        lbl.pack(pady=(10, 5))
        
        desc = ctk.CTkLabel(frame, text="Parece que esta é a sua primeira vez por aqui.\nVamos preparar o seu ambiente para a melhor experiência Dreamcast e Arcade.", text_color="gray")
        desc.pack(pady=(0, 20))
        
        lbl_lang = ctk.CTkLabel(frame, text="🌐 Escolha seu Idioma:", font=ctk.CTkFont(weight="bold"))
        lbl_lang.pack(anchor="w", padx=40)
        combo_lang = ctk.CTkComboBox(frame, values=list(self.app.lang_map.keys()), variable=self.var_lang, state="readonly", width=300)
        combo_lang.pack(pady=5)
        combo_lang.set("Português (BR)")

        lbl_theme = ctk.CTkLabel(frame, text="🎨 Escolha um Tema Visual:", font=ctk.CTkFont(weight="bold"))
        lbl_theme.pack(anchor="w", padx=40, pady=(15, 0))
        combo_theme = ctk.CTkComboBox(frame, values=["Padrão DARK", "Sonic The Hedgehog", "Crazy Taxi", "Shenmue", "Marvel vs Capcom 2"], variable=self.var_theme, state="readonly", width=300)
        combo_theme.pack(pady=5)

    def criar_passo_2(self):
        frame = ctk.CTkFrame(self.frame_container, fg_color="transparent")
        self.steps.append(frame)
        
        lbl = ctk.CTkLabel(frame, text="⚙️ Emulador e Inicialização", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(pady=(10, 10))
        
        lbl_path = ctk.CTkLabel(frame, text="Selecione a pasta onde o Flycast está (ou será) instalado:", font=ctk.CTkFont(weight="bold"))
        lbl_path.pack(anchor="w", padx=20)
        
        f_path = ctk.CTkFrame(frame, fg_color="transparent")
        f_path.pack(fill="x", padx=20, pady=5)
        
        entry_path = ctk.CTkEntry(f_path, textvariable=self.var_path, state="readonly")
        entry_path.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        def buscar_pasta():
            dir_escolhido = ctk.filedialog.askdirectory(parent=self)
            if dir_escolhido:
                self.var_path.set(os.path.normpath(dir_escolhido))
                
        btn_path = ctk.CTkButton(f_path, text="Procurar...", width=80, command=buscar_pasta)
        btn_path.pack(side="left")

        lbl_branch = ctk.CTkLabel(frame, text="🚀 Qual versão do emulador você prefere?", font=ctk.CTkFont(weight="bold"))
        lbl_branch.pack(anchor="w", padx=20, pady=(15, 0))
        
        rb_dev = ctk.CTkRadioButton(frame, text="Dev (Atualizações diárias)", variable=self.var_branch, value="dev")
        rb_dev.pack(anchor="w", padx=40, pady=5)
        
        rb_master = ctk.CTkRadioButton(frame, text="Master (Atualizações estáveis oficiais)", variable=self.var_branch, value="master")
        rb_master.pack(anchor="w", padx=40, pady=5)

        # NOVO: Comportamento do Botão Jogar
        lbl_behavior = ctk.CTkLabel(frame, text="🎮 O que o botão azul 'JOGAR' deve fazer?", font=ctk.CTkFont(weight="bold"))
        lbl_behavior.pack(anchor="w", padx=20, pady=(15, 0))

        combo_behavior = ctk.CTkComboBox(frame, values=["Utilizar o Flycast Updater Launcher", "Abrir Bigpicture", "Abrir Flycast"], variable=self.var_play_behavior, state="readonly", width=300)
        combo_behavior.pack(anchor="w", padx=40, pady=5)

    def criar_passo_3(self):
        frame = ctk.CTkFrame(self.frame_container, fg_color="transparent")
        self.steps.append(frame)
        
        lbl = ctk.CTkLabel(frame, text="🕹️ Biblioteca de Jogos", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(pady=(10, 10))
        
        desc = ctk.CTkLabel(frame, text="Adicione agora as pastas onde você guarda suas ROMs de Dreamcast/Naomi/Atomiswave.\nIsso impede que o modo TV (Big Picture) inicie vazio!", text_color="gray")
        desc.pack(pady=(0, 15))
        
        def adicionar_pasta():
            dir_escolhido = ctk.filedialog.askdirectory(parent=self)
            if dir_escolhido and dir_escolhido not in self.rom_paths:
                self.rom_paths.append(os.path.normpath(dir_escolhido))
                self.atualizar_lista_roms_wizard()
                
        btn_add = ctk.CTkButton(frame, text="➕ Adicionar Pasta de Jogos", fg_color="#228B22", hover_color="#006400", command=adicionar_pasta)
        btn_add.pack(side="bottom", pady=10)
        
        self.frame_lista_roms = ctk.CTkScrollableFrame(frame, height=120, fg_color="#1a1a1a")
        self.frame_lista_roms.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.atualizar_lista_roms_wizard()

    def atualizar_lista_roms_wizard(self):
        for widget in self.frame_lista_roms.winfo_children(): widget.destroy()
        if not self.rom_paths:
            ctk.CTkLabel(self.frame_lista_roms, text="Nenhuma pasta adicionada ainda.", text_color="gray").pack(pady=10)
        for p in self.rom_paths:
            f = ctk.CTkFrame(self.frame_lista_roms, fg_color="transparent")
            f.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(f, text=p, font=ctk.CTkFont(size=12)).pack(side="left")
            btn_del = ctk.CTkButton(f, text="🗑", width=30, height=24, fg_color="#8B0000", hover_color="#A52A2A", command=lambda path=p: self.remover_pasta(path))
            btn_del.pack(side="right")

    def remover_pasta(self, path):
        if path in self.rom_paths:
            self.rom_paths.remove(path)
            self.atualizar_lista_roms_wizard()

    def criar_passo_4(self):
        frame = ctk.CTkFrame(self.frame_container, fg_color="transparent")
        self.steps.append(frame)
        
        lbl = ctk.CTkLabel(frame, text="🏆 Conquistas e Nuvem", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(pady=(10, 15))
        
        lbl_ra = ctk.CTkLabel(frame, text="Sua Conta RetroAchievements (Opcional):", font=ctk.CTkFont(weight="bold"))
        lbl_ra.pack(anchor="w", padx=20)
        
        f_creds = ctk.CTkFrame(frame, fg_color="transparent")
        f_creds.pack(anchor="w", padx=40, pady=5)
        e_user = ctk.CTkEntry(f_creds, textvariable=self.var_ra_user, placeholder_text="Usuário", width=140)
        e_user.pack(side="left", padx=(0, 10))
        e_pass = ctk.CTkEntry(f_creds, textvariable=self.var_ra_pass, placeholder_text="Senha / Token", show="*", width=140)
        e_pass.pack(side="left")

        lbl_api = ctk.CTkLabel(frame, text="Web API Key (Para habilitar o Painel Global e Big Picture):", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_api.pack(anchor="w", padx=20, pady=(10, 2))
        f_api = ctk.CTkFrame(frame, fg_color="transparent")
        f_api.pack(anchor="w", padx=40, fill="x")
        e_api = ctk.CTkEntry(f_api, textvariable=self.var_ra_api, placeholder_text="Cole sua Web API Key aqui...", show="*", width=290)
        e_api.pack(side="left", padx=(0, 10))
        
        import webbrowser
        btn_api = ctk.CTkButton(f_api, text="🔑 Pegar Chave", width=100, fg_color="#8B008B", hover_color="#A52A2A", command=lambda: webbrowser.open("https://retroachievements.org/settings?tab=applications"))
        btn_api.pack(side="left")
        
        desc_api = ctk.CTkLabel(frame, text="💡 Obrigatória para o Updater desenhar conquistas e integrar com a TV.", text_color="gray", justify="left", font=ctk.CTkFont(size=11))
        desc_api.pack(anchor="w", padx=40, pady=(2, 5))

        chk_hc = ctk.CTkSwitch(frame, text="🔥 Modo Hardcore (Desativa Save States, Dobro de Pontos)", variable=self.var_ra_hardcore, progress_color="#8B0000")
        chk_hc.pack(anchor="w", padx=40, pady=(5, 5))

        ctk.CTkFrame(frame, height=2, fg_color="#333").pack(fill="x", padx=20, pady=10)

        lbl_cloud = ctk.CTkLabel(frame, text="☁️ Provedor de Cloud Saves (Auto-Backup):", font=ctk.CTkFont(weight="bold"))
        lbl_cloud.pack(anchor="w", padx=20, pady=(5, 5))
        f_cloud = ctk.CTkFrame(frame, fg_color="transparent")
        f_cloud.pack(anchor="w", padx=40)
        ctk.CTkRadioButton(f_cloud, text="Nenhum", variable=self.var_cloud, value="nenhum").pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(f_cloud, text="Google Drive", variable=self.var_cloud, value="gdrive").pack(side="left", padx=10)
        ctk.CTkRadioButton(f_cloud, text="OneDrive", variable=self.var_cloud, value="onedrive").pack(side="left", padx=10)

    def criar_passo_5(self):
        frame = ctk.CTkFrame(self.frame_container, fg_color="transparent")
        self.steps.append(frame)
        
        lbl = ctk.CTkLabel(frame, text="✅ Tudo Pronto!", font=ctk.CTkFont(size=28, weight="bold"), text_color="#00FF7F")
        lbl.pack(pady=(40, 20))
        
        desc = ctk.CTkLabel(frame, text="A sua estação de emulação foi configurada com sucesso.\n\nAo avançar, o Big Blue irá salvar todas as suas preferências\ne gerar os arquivos essenciais de forma transparente.", justify="center", font=ctk.CTkFont(size=14))
        desc.pack(pady=10)

    def criar_passo_6(self):
        # NOVO: O Passo Oculto da Instalação Mágica
        frame = ctk.CTkFrame(self.frame_container, fg_color="transparent")
        self.steps.append(frame)
        
        lbl = ctk.CTkLabel(frame, text="📥 Instalação Necessária", font=ctk.CTkFont(size=26, weight="bold"), text_color="#FFD700")
        lbl.pack(pady=(30, 20))
        
        texto = (
            "Detectamos que o emulador Flycast ainda não existe na pasta escolhida.\n\n"
            "Mas fique tranquilo! O Big Blue fará o download da versão\n"
            "mais recente automaticamente direto dos servidores oficiais.\n\n"
            "Clique abaixo para iniciar o download e abrir o aplicativo."
        )
        desc = ctk.CTkLabel(frame, text=texto, justify="center", font=ctk.CTkFont(size=14))
        desc.pack(pady=10)

    def mostrar_passo(self, index):
        for frame in self.steps: frame.pack_forget()
        self.steps[index].pack(fill="both", expand=True)
        
        self.btn_back.configure(state="normal" if index > 0 else "disabled")
        
        # Lógica Dinâmica: O emulador já existe na pasta?
        exe_path = os.path.join(self.var_path.get(), "flycast.exe")
        emu_exists = os.path.exists(exe_path)

        if index == 4: # Estamos no Passo 5 (Tudo Pronto)
            if emu_exists:
                self.btn_next.configure(text="Concluir ✔️", fg_color="#228B22", hover_color="#006400")
            else:
                self.btn_next.configure(text="Avançar ▶", fg_color="#1E90FF", hover_color="#0055FF")
                
        elif index == 5: # Estamos no Passo 6 (Instalação)
            self.btn_next.configure(text="Instalar Emulador 🚀", fg_color="#FF8C00", hover_color="#CD853F")
            
        else: # Passos normais
            self.btn_next.configure(text="Avançar ▶", fg_color="#1E90FF", hover_color="#0055FF")
            
        total_steps = 5 if emu_exists else 6
        current_display = index + 1
        self.lbl_titulo.configure(text=f"Passo {current_display} de {total_steps}")

    def next_step(self):
        exe_path = os.path.join(self.var_path.get(), "flycast.exe")
        emu_exists = os.path.exists(exe_path)

        if self.current_step == 4:
            if emu_exists:
                self.finalizar_wizard(instalar=False)
            else:
                self.current_step += 1
                self.mostrar_passo(self.current_step)
        elif self.current_step == 5:
            self.finalizar_wizard(instalar=True)
        else:
            self.current_step += 1
            self.mostrar_passo(self.current_step)

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.mostrar_passo(self.current_step)

    def finalizar_wizard(self, instalar=False):
        self.btn_next.configure(state="disabled", text="Salvando...")
        self.update()
        
        novo_lang = self.app.lang_map.get(self.var_lang.get(), "pt")
        self.app.lang = novo_lang
        self.app.config_atual["language"] = novo_lang
        
        self.app.config_atual["tema"] = self.var_theme.get()
        self.app.config_atual["install_path"] = self.var_path.get()
        self.app.config_atual["branch"] = self.var_branch.get()
        
        # 🛡️ BUGFIX 1: Sincroniza a variável Visual do Launcher ANTES de salvar!
        self.app.cloud_var.set(self.var_cloud.get())
        if self.var_cloud.get() != "nenhum":
            self.app.config_atual["cloud_provider"] = self.var_cloud.get()
            try:
                import cloud_saves
                if self.var_cloud.get() == "gdrive": self.app.config_atual["cloud_path"] = cloud_saves.get_gdrive_path()
                elif self.var_cloud.get() == "onedrive": self.app.config_atual["cloud_path"] = cloud_saves.get_onedrive_path()
            except ImportError: pass
        else:
            self.app.config_atual["cloud_provider"] = "nenhum"

        self.app.config_atual["setup_completed"] = True
        
        # 🛡️ BUGFIX 2: Sincroniza a variável Visual do Comportamento de Play!
        self.app.combo_play_behavior.set(self.var_play_behavior.get())
        
        self.app.entry_path.configure(state="normal")
        self.app.entry_path.delete(0, 'end')
        self.app.entry_path.insert(0, self.var_path.get())
        self.app.entry_path.configure(state="readonly")
        self.app.branch_var.set(self.var_branch.get())
        self.app.combo_lang.set(self.var_lang.get())
        
        if self.rom_paths:
            self.app.rom_paths_list = self.rom_paths.copy()
            self.app.atualizar_lista_ui_roms()
            
        ra_user = self.var_ra_user.get().strip()
        ra_pass = self.var_ra_pass.get().strip()
        ra_api = self.var_ra_api.get().strip()
        
        if ra_api:
            self.app.config_atual["ra_api_key"] = ra_api
            if hasattr(self.app, 'entry_ra_api'):
                self.app.entry_ra_api.delete(0, 'end')
                self.app.entry_ra_api.insert(0, ra_api)

        if ra_user and ra_pass:
            if hasattr(self.app, 'entry_ra_user'):
                self.app.switch_ra.select()
                self.app.entry_ra_user.delete(0, 'end')
                self.app.entry_ra_user.insert(0, ra_user)
                self.app.entry_ra_pass.delete(0, 'end')
                self.app.entry_ra_pass.insert(0, ra_pass)
                if self.var_ra_hardcore.get() and hasattr(self.app, 'switch_hardcore'):
                    self.app.switch_hardcore.select()

        self.app.salvar_estado_atual()
        self.app.aplicar_tema()
        self.app.atualizar_textos_ui()
        self.app.salvar_configuracoes_emulador(silencioso=True)
        self.app.atualizar_status_diretorio(self.var_path.get())
        self.app.tabview.set(self.app._("tab_games", default="🕹️ Launcher"))

        self.grab_release()
        self.destroy()

        # A MÁGICA FINAL: Se o emulador não existe, o Wizard fecha e diz para a tela principal começar a baixar!
        if instalar:
            self.app.after(500, lambda: self.app.preparar_motor("atualizar"))