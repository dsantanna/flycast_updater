import os
import shutil
import subprocess
import threading
import urllib.request
import tkinter as tk
import customtkinter as ctk
import tkinter.filedialog as fd
import tkinter.messagebox as mb

import texture_manager 
#import shop    # LOJA EM CONSTRUÇÃO

class ToolsManager:
    def __init__(self, app):
        self.app = app
        #self.shop_mgr = shop.HomebrewShop(self.app) # LOJA EM CONSTRUÇÃO
        # --- Variáveis do CHDMAN ---
        self.chdman_path = ""
        self.arquivos_para_converter = []
        self.vars_arquivos = {}
        self.convertendo = False
        
        # --- Instâncias dos Módulos ---
        self.texture_mgr = texture_manager.TextureManager(self.app)

    def construir_aba_ferramentas(self, tab):
        self.tabview_tools = ctk.CTkTabview(tab)
        self.tabview_tools.pack(fill="both", expand=True, padx=5, pady=0)
        
        # Adicionando as sub-abas
        tab_texturas = self.tabview_tools.add("✨ Texturas HD e Mods")
        tab_chdman = self.tabview_tools.add("🗜️ Compressor CHDMAN")
        tab_scraper = self.tabview_tools.add("🖼️ Caçador de Artes (Scraper)") # 👇 NOVA ABA
        tab_radar = self.tabview_tools.add("📡 Radar de Integridade")
        # tab_shop = self.tabview_tools.add("🌍 Homebrews & Indies")  # LOJA EM CONSTRUÇÃO
        
        # 1. Constrói o Gerenciador de Texturas
        self.texture_mgr.construir_interface(tab_texturas)
        
        # 2. CONSTRUÇÃO DO CHDMAN NA SEGUNDA ABA
        self.scroll_tools = ctk.CTkScrollableFrame(tab_chdman, fg_color="transparent")
        self.scroll_tools.pack(fill="both", expand=True)

        # 3. Constrói o Radar
        self.construir_aba_radar(tab_radar)

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

        self.app.after(300, self.auto_localizar_chdman)

        self.construir_aba_scraper(tab_scraper)
        # self.shop_mgr.construir_interface(tab_shop) # LOJA EM CRONSTRUÇÃO

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
        install_path = self.app.entry_path.get()
        if not install_path: return

        tools_dir = os.path.join(install_path, "tools")
        caminho_oficial = os.path.join(tools_dir, "chdman.exe")

        caminhos_tentativa = [
            caminho_oficial,
            os.path.join(install_path, "chdman.exe"),
            os.path.join(os.getcwd(), "tools", "chdman.exe"),
            os.path.join(os.getcwd(), "chdman.exe")
        ]

        for p in caminhos_tentativa:
            if os.path.exists(p):
                if p != caminho_oficial:
                    try:
                        os.makedirs(tools_dir, exist_ok=True)
                        shutil.copy2(p, caminho_oficial)
                    except Exception:
                        pass
                
                self.chdman_path = caminho_oficial
                self.lbl_chdman_status.configure(text="🟢 Instalado (/tools)", text_color="#00FF7F")
                self.btn_baixar_chdman.grid_remove()
                return
        
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
                self.app.after(0, lambda: self.progressbar_chd.pack(anchor="w", padx=20, pady=(0, 15), after=self.lbl_status))
                self.app.after(0, self.progressbar_chd.set, 0)
                
                import re
                processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, universal_newlines=True, creationflags=0x08000000)
                
                for linha in processo.stdout:
                    match = re.search(r'(\d+\.\d+)%', linha)
                    if match:
                        pct = float(match.group(1)) / 100.0
                        self.app.after(0, self.progressbar_chd.set, pct)

                processo.wait()
                
                if processo.returncode == 0:
                    sucessos += 1
                    self.app.after(0, self.progressbar_chd.set, 1.0)
                    self.app.log(f"✅ Sucesso: {os.path.basename(output_file)} gerado com sucesso.")
                else:
                    erros += 1
                    self.app.log(f"❌ Erro na operação {os.path.basename(input_file)}")
                    if os.path.exists(output_file): os.remove(output_file)
            except Exception as e:
                erros += 1
                self.app.log(f"❌ Falha de execução no chdman: {e}")

        self.convertendo = False
        self.app.after(0, self.progressbar_chd.pack_forget)
        msg_final = f"Operação concluída! {sucessos} sucesso(s), {erros} erro(s)."
        self.app.log(f"🏁 {msg_final}")
        
        self.app.after(0, self.lbl_status.configure, {"text": msg_final, "text_color": "#00FF7F"})
        self.app.after(0, self.btn_scan.configure, {"state": "normal"})
        self.app.after(0, self.escanear_roms)
        
        if hasattr(self.app, 'game_manager'):
            self.app.after(1000, self.app.game_manager.escanear_jogos)
            
        self.app.after(0, lambda: self.app.mostrar_toast("Processo Finalizado", msg_final, "success" if erros == 0 else "warning"))

        # ==========================================
    # 3. CONSTRUÇÃO DO RADAR DE INTEGRIDADE
    # ==========================================
    def construir_aba_radar(self, tab):
        self.scroll_radar = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.scroll_radar.pack(fill="both", expand=True)

        lbl_title = ctk.CTkLabel(self.scroll_radar, text="📡 Radar de Integridade (Raio-X da Biblioteca)", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_title.pack(anchor="w", padx=10, pady=(10, 5))

        desc = (
            "Faça uma varredura tática em todas as suas pastas mapeadas. O Radar detecta ROMs de Arcade "
            "corrompidas, arquivos sem capas (Metadados) e alerta sobre formatos pesados e não otimizados "
            "(como .ZIPs gigantes que travam a leitura e deveriam ser convertidos para .CHD)."
        )
        lbl_desc = ctk.CTkLabel(self.scroll_radar, text=desc, text_color="gray", justify="left", wraplength=700)
        lbl_desc.pack(anchor="w", padx=10, pady=(0, 15))

        self.btn_iniciar_radar = ctk.CTkButton(self.scroll_radar, text="🔍 Iniciar Varredura Tática", width=250, height=35, font=ctk.CTkFont(weight="bold"), fg_color="#8B008B", hover_color="#5C005C", command=self.iniciar_radar)
        self.btn_iniciar_radar.pack(pady=10)

        self.lbl_status_radar = ctk.CTkLabel(self.scroll_radar, text="", text_color="cyan", font=ctk.CTkFont(weight="bold"))
        self.lbl_status_radar.pack(pady=(0, 10))

        self.frame_resultados_radar = ctk.CTkFrame(self.scroll_radar, fg_color="#1a1a1a", corner_radius=10, height=350)
        self.frame_resultados_radar.pack(fill="both", expand=True, padx=10, pady=5)
        self.frame_resultados_radar.pack_propagate(False) # Mantém a altura fixa mesmo vazio
        
        lbl_resultado_vazio = ctk.CTkLabel(self.frame_resultados_radar, text="Aguardando ordens para iniciar varredura...", text_color="gray", font=ctk.CTkFont(slant="italic"))
        lbl_resultado_vazio.pack(pady=80)

    def iniciar_radar(self):
        if not self.app.rom_paths_list:
            mb.showwarning("Aviso", "Nenhuma pasta de jogos configurada no emulador.", parent=self.app)
            return

        self.btn_iniciar_radar.configure(state="disabled", text="⏳ Escaneando...")
        self.lbl_status_radar.configure(text="Inspecionando integridade das pastas. Isso pode levar alguns segundos...", text_color="#FFD700")
        
        for widget in self.frame_resultados_radar.winfo_children():
            widget.destroy()

        threading.Thread(target=self._processo_radar, daemon=True).start()

    def _processo_radar(self):
        alertas_arcade = []
        alertas_formato = []
        alertas_metadados = []

        extensoes_rom = ('.cdi', '.gdi', '.chd', '.cue', '.zip', '.7z')
        install_path = getattr(self.app.entry_path, 'get', lambda: "")().strip()
        boxart_dir = os.path.join(install_path, "data", "boxart")
        
        # Ignoramos as bios e arquivos do sistema pra não gerar falso-positivo
        arquivos_de_sistema = ['awbios.zip', 'naomi.zip', 'naomi2.zip', 'syssp.zip', 'hikaru.zip', 'flycast_backup.zip']
        
        for pasta in self.app.rom_paths_list:
            if not os.path.exists(pasta): continue
            
            for root, _, files in os.walk(pasta):
                for f in files:
                    ext = f.lower()
                    if ext.endswith(extensoes_rom):
                        f_lower = f.lower()
                        if f_lower in arquivos_de_sistema or f_lower.startswith(('gds-', 'gdl-', 'gdv-')):
                            continue
                            
                        caminho_completo = os.path.join(root, f)
                        nome_limpo = os.path.splitext(f)[0]
                        is_arcade = hasattr(self.app.game_manager, 'arcade_manager') and self.app.game_manager.arcade_manager.is_arcade_rom(f)
                        
                        # 1. Verifica Formato Não Otimizado (.ZIP/.7Z Gigantes de Dreamcast)
                        if ext.endswith(('.zip', '.7z')) and not is_arcade:
                            tamanho_mb = os.path.getsize(caminho_completo) / (1024 * 1024)
                            # Se for maior que 60MB e for arquivo de Dreamcast zipado, alerta!
                            if tamanho_mb > 60:
                                alertas_formato.append(f"⚠️ {f} ({int(tamanho_mb)}MB): Formato não otimizado para Dreamcast. Extraia e use o CHDMAN para compactar em .CHD.")
                        
                        # 2. Verifica Integridade Arcade
                        if is_arcade:
                            valido, msg = self.app.game_manager.arcade_manager.verificar_integridade_rom(caminho_completo)
                            if not valido:
                                alertas_arcade.append(f"❌ {f}: ROM de Arcade Corrompida ou Faltando arquivos.")
                                
                        # 3. Verifica Metadados/Capas
                        capa_encontrada = False
                        for p_img in [os.path.join(boxart_dir, f"{f}.png"), os.path.join(boxart_dir, f"{f}.jpg"), os.path.join(boxart_dir, f"{nome_limpo}.png"), os.path.join(boxart_dir, f"{nome_limpo}.jpg")]:
                            if os.path.exists(p_img):
                                capa_encontrada = True
                                break
                        if not capa_encontrada:
                            alertas_metadados.append(f"🖼️ {f}: Arte de capa ausente no sistema.")

        # Retorna para a Thread Principal para pintar os dados na tela
        self.app.after(0, self._renderizar_resultados_radar, alertas_arcade, alertas_formato, alertas_metadados)

    def _renderizar_resultados_radar(self, alertas_arcade, alertas_formato, alertas_metadados):
        total_alertas = len(alertas_arcade) + len(alertas_formato) + len(alertas_metadados)
        
        self.btn_iniciar_radar.configure(state="normal", text="🔍 Refazer Varredura Tática")
        
        if total_alertas == 0:
            self.lbl_status_radar.configure(text="✅ Tudo limpo! Sua biblioteca está em perfeitas condições.", text_color="#00FF7F")
            lbl = ctk.CTkLabel(self.frame_resultados_radar, text="Nenhuma anomalia ou problema detectado.", text_color="gray", font=ctk.CTkFont(slant="italic"))
            lbl.pack(pady=80)
            if hasattr(self.app, 'sfx'): self.app.sfx.play("success")
            return
            
        self.lbl_status_radar.configure(text=f"⚠️ Varredura concluída. {total_alertas} aviso(s) encontrado(s).", text_color="#FFD700")
        
        scroll_res = ctk.CTkScrollableFrame(self.frame_resultados_radar, fg_color="transparent")
        scroll_res.pack(fill="both", expand=True, padx=5, pady=5)
        
        def add_secao(titulo, alertas, cor):
            if alertas:
                ctk.CTkLabel(scroll_res, text=titulo, font=ctk.CTkFont(weight="bold", size=14), text_color=cor).pack(anchor="w", pady=(10, 5), padx=5)
                for a in alertas:
                    # Texto menorzinho para não estourar a tela se o caminho for longo
                    ctk.CTkLabel(scroll_res, text=a, font=ctk.CTkFont(size=12), text_color="white", justify="left").pack(anchor="w", padx=15, pady=2)

        # Imprime na ordem de prioridade (Críticos primeiro!)
        add_secao("🔴 NÍVEL CRÍTICO: ROMs de Arcade Corrompidas", alertas_arcade, "#FF4C4C")
        add_secao("🟡 NÍVEL DE AVISO: Formatos Pesados Não Otimizados", alertas_formato, "#FFD700")
        add_secao("🔵 NÍVEL INFO: Metadados / Capas Ausentes", alertas_metadados, "#1E90FF")
        
        if hasattr(self.app, 'sfx'): 
            if alertas_arcade: self.app.sfx.play("error")
            else: self.app.sfx.play("nav")
    # ==========================================
    # CONSTRUÇÃO DO SCRAPER MASSIVO
    # ==========================================
    def construir_aba_scraper(self, tab):
        scroll_scraper = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_scraper.pack(fill="both", expand=True)

        lbl_title = ctk.CTkLabel(scroll_scraper, text="🖼️ Caçador de Artes e Mídias (Scraper Massivo)", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_title.pack(anchor="w", padx=10, pady=(10, 5))

        desc = (
            "Esta ferramenta de varredura profunda inspeciona toda a sua biblioteca de jogos e conecta-se "
            "aos servidores do Libretro para baixar automaticamente Capas (Boxarts), Logos de Título e "
            "Vídeos (Snaps) que estejam faltando.\n\n"
            "O processo utiliza múltiplas conexões simultâneas e pula inteligentemente o que você já possui."
        )
        lbl_desc = ctk.CTkLabel(scroll_scraper, text=desc, text_color="gray", justify="left", wraplength=700)
        lbl_desc.pack(anchor="w", padx=10, pady=(0, 20))

        self.btn_iniciar_scraper = ctk.CTkButton(scroll_scraper, text="🎯 INICIAR VARREDURA MASSIVA", width=300, height=45, font=ctk.CTkFont(weight="bold", size=14), fg_color="#228B22", hover_color="#006400", command=self.iniciar_scraper_massa)
        self.btn_iniciar_scraper.pack(pady=10)

        self.lbl_status_scraper = ctk.CTkLabel(scroll_scraper, text="", text_color="cyan", font=ctk.CTkFont(weight="bold"))
        self.lbl_status_scraper.pack(pady=(5, 10))

        # A barra nasce oculta e só aparece durante o tiroteio
        self.progress_scraper = ctk.CTkProgressBar(scroll_scraper, width=500, height=15, progress_color="#1E90FF")
        self.progress_scraper.set(0)
        
    def iniciar_scraper_massa(self):
        if not hasattr(self.app, 'game_manager') or not hasattr(self.app.game_manager, 'jogos_agrupados_cache'):
            mb.showwarning("Biblioteca Vazia", "Nenhum jogo encontrado na memória. Faça um escaneamento da sua pasta de ROMs primeiro na aba Launcher.", parent=self.app)
            return
            
        dicionario_jogos = self.app.game_manager.jogos_agrupados_cache
        if not dicionario_jogos: return
        
        self.btn_iniciar_scraper.configure(state="disabled", text="⏳ Baixando Artes...")
        self.lbl_status_scraper.configure(text="Conectando aos servidores. Por favor, aguarde...", text_color="#FFD700")
        self.progress_scraper.pack(pady=10)
        self.progress_scraper.set(0)
        
        def atualizar_progresso(processados, total):
            if not self.app.winfo_exists(): return
            pct = processados / total
            self.progress_scraper.set(pct)
            self.lbl_status_scraper.configure(text=f"Processando e baixando arquivos: {processados}/{total} jogos verificados...")

        def finalizar_scraper(sucessos):
            if not self.app.winfo_exists(): return
            self.progress_scraper.pack_forget()
            self.btn_iniciar_scraper.configure(state="normal", text="🎯 REFAZER VARREDURA MASSIVA")
            self.lbl_status_scraper.configure(text=f"✅ Varredura Concluída! {sucessos} novos jogos receberam mídias.", text_color="#00FF7F")
            self.app.mostrar_toast("Scraper Concluído", f"Foram baixadas novas artes e mídias para {sucessos} jogo(s)!", "success")
            if hasattr(self.app, 'sfx'): self.app.sfx.play("save")
            # Recarrega a grade do Launcher para as novas capas brotarem na tela!
            self.app.game_manager.escanear_jogos()

        install_path = self.app.entry_path.get()
        # Manda a ordem de disparo pro motor no scraper.py
        self.app.game_manager.auto_scraper.varredura_em_massa(
            install_path=install_path,
            dicionario_jogos=dicionario_jogos,
            callback_progresso=atualizar_progresso,
            callback_fim=finalizar_scraper
        )