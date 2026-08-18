import os
import shutil
import subprocess
import threading
import urllib.request
import tkinter as tk
import customtkinter as ctk
import tkinter.filedialog as fd
import tkinter.messagebox as mb

class ToolsManager:
    def __init__(self, app):
        self.app = app
        self.chdman_path = ""
        self.arquivos_para_converter = []
        self.vars_arquivos = {}  # Guarda o estado de cada checkbox (Marcado/Desmarcado)
        self.convertendo = False

    def construir_aba_ferramentas(self, tab):
        self.scroll_tools = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.scroll_tools.pack(fill="both", expand=True)

        # --- Cabeçalho ---
        lbl_title = ctk.CTkLabel(self.scroll_tools, text="🗜️ Compressor e Extrator de Imagens (CHDMAN)", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_title.pack(anchor="w", padx=10, pady=(10, 5))

        desc = (
            "Converta jogos (.GDI / .CUE) para um único arquivo comprimido (.CHD) para economizar espaço.\n"
            "Ou reverta o processo, extraindo seus arquivos .CHD de volta para .GDI ou .CUE (Padrão ISO) "
            "caso precise modificar os arquivos internos do jogo."
        )
        lbl_desc = ctk.CTkLabel(self.scroll_tools, text=desc, text_color="gray", justify="left", wraplength=700)
        lbl_desc.pack(anchor="w", padx=10, pady=(0, 15))

        # --- Painel do CHDMAN com Semáforo Visual ---
        frame_chdman = ctk.CTkFrame(self.scroll_tools, fg_color="#1a1a1a", corner_radius=8)
        frame_chdman.pack(fill="x", padx=10, pady=5)

        lbl_chdman = ctk.CTkLabel(frame_chdman, text="Status do CHDMAN:", font=ctk.CTkFont(weight="bold"))
        lbl_chdman.pack(side="left", padx=15, pady=12)

        # 🚦 O SEMÁFORO VISUAL NATIVO
        self.lbl_chdman_status = ctk.CTkLabel(frame_chdman, text="🔴 Ausente", text_color="#FF4C4C", font=ctk.CTkFont(weight="bold", size=13))
        self.lbl_chdman_status.pack(side="left", padx=5, pady=12)

        self.btn_baixar_chdman = ctk.CTkButton(frame_chdman, text="📥 Baixar CHDMAN", width=130, fg_color="#228B22", hover_color="#006400", font=ctk.CTkFont(weight="bold"), command=self.baixar_chdman)
        self.btn_baixar_chdman.pack(side="right", padx=15, pady=12)

        btn_chdman = ctk.CTkButton(frame_chdman, text="Procurar local...", width=100, command=self.buscar_chdman)
        btn_chdman.pack(side="right", padx=(0, 5), pady=12)

        # --- Ações (Painel de Botões) ---
        frame_acoes = ctk.CTkFrame(self.scroll_tools, fg_color="transparent")
        frame_acoes.pack(fill="x", padx=10, pady=15)

        self.btn_scan = ctk.CTkButton(frame_acoes, text="🔍 Escanear ROMs (GDI/CUE/CHD)", width=180, font=ctk.CTkFont(weight="bold"), command=self.escanear_roms)
        self.btn_scan.grid(row=0, column=0, padx=(0, 10), pady=5)

        self.btn_converter = ctk.CTkButton(frame_acoes, text="🚀 Criar .CHD", width=120, font=ctk.CTkFont(weight="bold"), fg_color="#8B008B", hover_color="#A52A2A", command=lambda: self.iniciar_conversao("to_chd"), state="disabled")
        self.btn_converter.grid(row=0, column=1, padx=(0, 10), pady=5)

        self.btn_to_gdi = ctk.CTkButton(frame_acoes, text="⏪ Extrair para .GDI", width=140, font=ctk.CTkFont(weight="bold"), fg_color="#FF8C00", hover_color="#CD853F", command=lambda: self.iniciar_conversao("to_gdi"), state="disabled")
        self.btn_to_gdi.grid(row=0, column=2, padx=(0, 10), pady=5)

        self.btn_to_cue = ctk.CTkButton(frame_acoes, text="⏪ Extrair para ISO (.CUE)", width=160, font=ctk.CTkFont(weight="bold"), fg_color="#4169E1", hover_color="#1E90FF", command=lambda: self.iniciar_conversao("to_cue"), state="disabled")
        self.btn_to_cue.grid(row=0, column=3, padx=(0, 10), pady=5)

        self.lbl_status = ctk.CTkLabel(self.scroll_tools, text="", text_color="cyan", font=ctk.CTkFont(weight="bold"))
        self.lbl_status.pack(anchor="w", padx=20, pady=(0, 5))
        # 📊 BARRA DE PROGRESSO (Nasce invisível e só aparece na hora da ação)
        self.progressbar_chd = ctk.CTkProgressBar(self.scroll_tools, width=500, height=12, progress_color="#FF8C00")
        self.progressbar_chd.set(0)
        # --- Seletor de Pasta de Destino ---
        frame_destino = ctk.CTkFrame(self.scroll_tools, fg_color="#1a1a1a", corner_radius=8)
        frame_destino.pack(fill="x", padx=10, pady=(5, 15))
        frame_destino.columnconfigure(1, weight=1)

        lbl_destino = ctk.CTkLabel(frame_destino, text="💾 Salvar Convertidos em:", font=ctk.CTkFont(weight="bold"))
        lbl_destino.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.entry_destino = ctk.CTkEntry(frame_destino, state="readonly", placeholder_text="Se vazio, salvará na mesma pasta da ROM original")
        self.entry_destino.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        btn_destino = ctk.CTkButton(frame_destino, text="Escolher Pasta...", width=120, command=self.buscar_destino)
        btn_destino.grid(row=0, column=2, padx=10, pady=10)

        # --- Controles da Lista (Marcar/Desmarcar Todos) ---
        frame_controles_lista = ctk.CTkFrame(self.scroll_tools, fg_color="transparent")
        frame_controles_lista.pack(fill="x", padx=15, pady=(0, 0))
        
        lbl_selecao = ctk.CTkLabel(frame_controles_lista, text="Selecione os jogos para operação:", font=ctk.CTkFont(weight="bold", size=13))
        lbl_selecao.pack(side="left")

        btn_none = ctk.CTkButton(frame_controles_lista, text="Desmarcar Todos", width=110, height=24, fg_color="#555555", hover_color="#777777", command=lambda: self.toggle_todas_checkboxes(False))
        btn_none.pack(side="right", padx=(5, 0))

        btn_all = ctk.CTkButton(frame_controles_lista, text="Marcar Todos", width=100, height=24, command=lambda: self.toggle_todas_checkboxes(True))
        btn_all.pack(side="right")

        # --- Lista de Arquivos (Checkboxes) ---
        self.frame_lista = ctk.CTkScrollableFrame(self.scroll_tools, height=200, fg_color="#2b2b2b")
        self.frame_lista.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        lbl_lista_vazia = ctk.CTkLabel(self.frame_lista, text="Nenhum arquivo escaneado. Clique em 'Escanear ROMs'.", text_color="gray")
        lbl_lista_vazia.pack(pady=20)

        # Tenta auto-localizar o chdman na nova pasta padrão
        self.app.after(300, self.auto_localizar_chdman)

    def toggle_todas_checkboxes(self, estado):
        for var in self.vars_arquivos.values():
            var.set(estado)

    def buscar_destino(self):
        dir_escolhido = fd.askdirectory(title="Selecione a pasta de destino para os jogos convertidos")
        if dir_escolhido:
            self.entry_destino.configure(state="normal")
            self.entry_destino.delete(0, 'end')
            self.entry_destino.insert(0, os.path.normpath(dir_escolhido))
            self.entry_destino.configure(state="readonly")

    def auto_localizar_chdman(self):
        """Varre a pasta global /tools/ do emulador em busca do chdman.exe"""
        install_path = self.app.entry_path.get()
        if not install_path: return

        # Caminho oficial consolidado na pasta de ferramentas
        tools_dir = os.path.join(install_path, "tools")
        caminho_oficial = os.path.join(tools_dir, "chdman.exe")

        # Fallbacks históricos caso ele já tenha deixado o arquivo solto em algum lugar antes
        caminhos_tentativa = [
            caminho_oficial,
            os.path.join(install_path, "chdman.exe"),
            os.path.join(os.getcwd(), "tools", "chdman.exe"),
            os.path.join(os.getcwd(), "chdman.exe")
        ]

        for p in caminhos_tentativa:
            if os.path.exists(p):
                # Se achamos em um local antigo, move/copia para a pasta oficial /tools/
                if p != caminho_oficial:
                    try:
                        os.makedirs(tools_dir, exist_ok=True)
                        shutil.copy2(p, caminho_oficial)
                    except Exception:
                        pass
                
                self.chdman_path = caminho_oficial
                self.lbl_chdman_status.configure(text="🟢 Instalado (/tools)", text_color="#00FF7F")
                self.btn_baixar_chdman.grid_remove() # Oculta se já estiver pronto
                return
        
        # Caso não ache em nenhum lugar, ativa o semáforo vermelho e o botão de baixar
        self.chdman_path = ""
        self.lbl_chdman_status.configure(text="🔴 Ausente", text_color="#FF4C4C")
        self.btn_baixar_chdman.grid()

    def baixar_chdman(self):
        install_path = self.app.entry_path.get()
        if not install_path or not os.path.exists(install_path):
            mb.showerror("Erro", "Configure a pasta de instalação do emulador na aba de BIOS e Emu primeiro.", parent=self.app)
            return

        tools_dir = os.path.join(install_path, "tools")
        os.makedirs(tools_dir, exist_ok=True)
        chdman_dest = os.path.join(tools_dir, "chdman.exe")

        def rotina_download():
            self.app.after(0, self.btn_baixar_chdman.configure, {"state": "disabled", "text": "⏳ Baixando..."})
            self.app.log("🌐 Iniciando download automático do CHDMAN...")
            
            try:
                url_chdman = "https://github.com/dsantanna/flycast_updater/releases/download/v6.1/chdman.exe"
                req = urllib.request.Request(url_chdman, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15) as response, open(chdman_dest, 'wb') as out_file:
                    out_file.write(response.read())

                self.app.log(f"✅ CHDMAN baixado e armazenado com sucesso em: {chdman_dest}")
                self.chdman_path = chdman_dest
                self.app.after(0, lambda: self.lbl_chdman_status.configure(text="🟢 Instalado (/tools)", text_color="#00FF7F"))
                self.app.after(0, lambda: self.app.mostrar_toast("Ferramenta Pronta", "O CHDMAN foi baixado e instalado com sucesso na pasta /tools!", "success"))
                self.app.after(0, self.btn_baixar_chdman.grid_remove) 
                
            except Exception as e:
                self.app.log(f"❌ Erro crítico ao baixar CHDMAN: {e}")
                self.app.after(0, lambda err=e: mb.showerror("Falha no Download", f"Verifique sua conexão com a internet.\n\nErro Técnico:\n{err}", parent=self.app))
                self.app.after(0, self.btn_baixar_chdman.configure, {"state": "normal", "text": "📥 Baixar CHDMAN"})

        threading.Thread(target=rotina_download, daemon=True).start()

    def buscar_chdman(self):
        """Abre o seletor. Se o usuário escolher o arquivo, clona ele direto pra pasta /tools/"""
        install_path = self.app.entry_path.get()
        if not install_path:
            mb.showerror("Erro", "Configure a pasta do emulador primeiro na aba BIOS e Emu.", parent=self.app)
            return

        arquivo = fd.askopenfilename(title="Selecione o chdman.exe", filetypes=[("Executável", "chdman.exe"), ("Todos", "*.*")])
        if arquivo:
            tools_dir = os.path.join(install_path, "tools")
            os.makedirs(tools_dir, exist_ok=True)
            destino_oficial = os.path.join(tools_dir, "chdman.exe")
            
            try:
                # Copia preservando metadados se o arquivo for diferente do destino
                if os.path.normpath(arquivo) != os.path.normpath(destino_oficial):
                    shutil.copy2(arquivo, destino_oficial)
                
                self.chdman_path = destino_oficial
                self.lbl_chdman_status.configure(text="🟢 Instalado (/tools)", text_color="#00FF7F")
                self.btn_baixar_chdman.grid_remove()
                self.app.log(f"🗜️ CHDMAN importado com sucesso para: {destino_oficial}")
                self.app.mostrar_toast("Ferramenta Importada", "O CHDMAN foi copiado de forma portable para a pasta /tools!", "success")
            except Exception as e:
                mb.showerror("Erro de Importação", f"Não foi possível copiar o executável para a pasta /tools/.\n\nErro: {e}", parent=self.app)

    def escanear_roms(self):
        if not self.app.rom_paths_list:
            mb.showwarning("Aviso", "Nenhuma pasta de ROMs configurada. Vá na aba de Configurações e adicione seus diretórios de jogos primeiro.", parent=self.app)
            return

        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        self.arquivos_para_converter = []
        self.vars_arquivos.clear()
        
        tem_nao_comprimido = False
        tem_chd = False
        extensoes_alvo = (".gdi", ".cue", ".chd")

        for pasta in self.app.rom_paths_list:
            if not os.path.exists(pasta): continue
            
            for root, dirs, files in os.walk(pasta):
                for file in files:
                    ext = file.lower()
                    if ext.endswith(extensoes_alvo):
                        caminho_completo = os.path.join(root, file)
                        self.arquivos_para_converter.append(caminho_completo)
                        
                        if ext.endswith((".gdi", ".cue")): tem_nao_comprimido = True
                        elif ext.endswith(".chd"): tem_chd = True
                        
                        f = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
                        f.pack(fill="x", pady=2)
                        
                        var_chk = tk.BooleanVar(value=True)
                        self.vars_arquivos[caminho_completo] = var_chk
                        
                        chk = ctk.CTkCheckBox(
                            f, text=file, variable=var_chk, 
                            font=ctk.CTkFont(weight="bold"), 
                            text_color="#00BFFF" if ext.endswith(".chd") else "white",
                            width=250
                        )
                        chk.pack(side="left", padx=5)
                        
                        lbl_caminho = ctk.CTkLabel(f, text=root, text_color="gray", font=ctk.CTkFont(size=11), anchor="w")
                        lbl_caminho.pack(side="left", fill="x", expand=True)

        if self.arquivos_para_converter:
            self.btn_converter.configure(state="normal" if tem_nao_comprimido else "disabled")
            self.btn_to_gdi.configure(state="normal" if tem_chd else "disabled")
            self.btn_to_cue.configure(state="normal" if tem_chd else "disabled")
            self.lbl_status.configure(text=f"{len(self.arquivos_para_converter)} jogo(s) encontrado(s) e pronto(s) para operação!", text_color="#00FF7F")
        else:
            self.btn_converter.configure(state="disabled")
            self.btn_to_gdi.configure(state="disabled")
            self.btn_to_cue.configure(state="disabled")
            lbl_vazio = ctk.CTkLabel(self.frame_lista, text="Nenhum arquivo .GDI, .CUE ou .CHD foi encontrado nas suas pastas.", text_color="#FFD700")
            lbl_vazio.pack(pady=20)
            self.lbl_status.configure(text="")

    def iniciar_conversao(self, modo):
        if not self.chdman_path or not os.path.exists(self.chdman_path):
            mb.showerror("Erro", "O executável chdman.exe não foi encontrado na pasta /tools/. Clique em 'Baixar CHDMAN' primeiro.", parent=self.app)
            return
            
        selecionados = [f for f in self.arquivos_para_converter if self.vars_arquivos.get(f, tk.BooleanVar()).get()]
        if not selecionados:
            mb.showwarning("Aviso", "Você não marcou nenhum jogo na lista para converter!", parent=self.app)
            return

        alvos = []
        acao_desc = ""

        if modo == "to_chd":
            alvos = [f for f in selecionados if f.lower().endswith(('.gdi', '.cue'))]
            acao_desc = "compactar para .CHD"
        elif modo == "to_gdi":
            alvos = [f for f in selecionados if f.lower().endswith('.chd')]
            acao_desc = "extrair de volta para .GDI"
        elif modo == "to_cue":
            alvos = [f for f in selecionados if f.lower().endswith('.chd')]
            acao_desc = "extrair de volta para ISO (.CUE/BIN)"

        if not alvos: 
            mb.showinfo("Aviso", "Os arquivos selecionados não correspondem ao tipo da operação.", parent=self.app)
            return

        resposta = mb.askyesno("Confirmar Operação", f"Você está prestes a {acao_desc} de {len(alvos)} jogo(s) selecionado(s).\n\nDeseja continuar?", parent=self.app)
        if not resposta: return

        self.convertendo = True
        self.btn_scan.configure(state="disabled")
        self.btn_converter.configure(state="disabled")
        self.btn_to_gdi.configure(state="disabled")
        self.btn_to_cue.configure(state="disabled")
        self.app.log(f"🚀 Iniciando lote de operação: {acao_desc}...")

        threading.Thread(target=self._processo_conversao, args=(modo, alvos), daemon=True).start()

    def _processo_conversao(self, modo, alvos):
        sucessos, erros, total = 0, 0, len(alvos)
        destino_base = self.entry_destino.get()

        for i, input_file in enumerate(alvos):
            if not self.convertendo: break
            nome_base = os.path.splitext(os.path.basename(input_file))[0]
            pasta_destino = destino_base if destino_base and os.path.exists(destino_base) else os.path.dirname(input_file)
            
            if modo == "to_chd":
                output_file = os.path.join(pasta_destino, nome_base + ".chd")
                comando = [self.chdman_path, "createcd", "-i", input_file, "-o", output_file]
                verbo = "Compactando"
            elif modo == "to_gdi":
                output_file = os.path.join(pasta_destino, nome_base + ".gdi")
                comando = [self.chdman_path, "extractcd", "-i", input_file, "-o", output_file]
                verbo = "Extraindo"
            elif modo == "to_cue":
                output_file = os.path.join(pasta_destino, nome_base + ".cue")
                comando = [self.chdman_path, "extractcd", "-i", input_file, "-o", output_file]
                verbo = "Extraindo"
            
            if os.path.exists(output_file):
                self.app.log(f"⏩ Pulando {os.path.basename(input_file)} (Arquivo já existe).")
                continue

            self.app.after(0, self.lbl_status.configure, {"text": f"{verbo} {i+1}/{total}: {os.path.basename(input_file)}...", "text_color": "#FFD700"})
            self.app.log(f"🗜️ {verbo}: {input_file} -> {output_file}")
            
            try:
                # 1. Traz a barra para a tela e zera ela
                self.app.after(0, lambda: self.progressbar_chd.pack(anchor="w", padx=20, pady=(0, 15), after=self.lbl_status))
                self.app.after(0, self.progressbar_chd.set, 0)
                
                import re
                # 2. Inicia o processo em modo 'Escuta' (Popen) lendo o Stdout
                processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, universal_newlines=True, creationflags=0x08000000)
                
                # 3. Intercepta as falas do CHDMAN (Ex: "Compressing, 45.3% complete...")
                for linha in processo.stdout:
                    match = re.search(r'(\d+\.\d+)%', linha)
                    if match:
                        pct = float(match.group(1)) / 100.0
                        self.app.after(0, self.progressbar_chd.set, pct)

                processo.wait()
                
                if processo.returncode == 0:
                    sucessos += 1
                    self.app.after(0, self.progressbar_chd.set, 1.0) # Crava em 100%
                    self.app.log(f"✅ Sucesso: {os.path.basename(output_file)} gerado com sucesso.")
                else:
                    erros += 1
                    self.app.log(f"❌ Erro na operação {os.path.basename(input_file)}")
                    if os.path.exists(output_file): os.remove(output_file)
            except Exception as e:
                erros += 1
                self.app.log(f"❌ Falha de execução no chdman: {e}")

        self.convertendo = False
        self.app.after(0, self.progressbar_chd.pack_forget) # 🧹 Esconde a barra ao terminar o lote
        msg_final = f"Operação concluída! {sucessos} sucesso(s), {erros} erro(s)."
        self.app.log(f"🏁 {msg_final}")
        
        self.app.after(0, self.lbl_status.configure, {"text": msg_final, "text_color": "#00FF7F"})
        self.app.after(0, self.btn_scan.configure, {"state": "normal"})
        self.app.after(0, self.escanear_roms)
        
        if hasattr(self.app, 'game_manager'):
            self.app.after(1000, self.app.game_manager.escanear_jogos)
            
        self.app.after(0, lambda: self.app.mostrar_toast("Processo Finalizado", msg_final, "success" if erros == 0 else "warning"))
