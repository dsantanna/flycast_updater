import os
import struct
import customtkinter as ctk
import tkinter.messagebox as mb

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class VMUXRayManager(ctk.CTkToplevel):
    def __init__(self, master, install_path, modo_filtro="global", pasta_jogo=None):
        super().__init__(master)
        self.title("💾 Gerenciador Visual de VMU")
        self.geometry("650x700")
        self.attributes("-topmost", True)
        self.grab_set()

        self.install_path = install_path
        self.modo_filtro = modo_filtro
        self.pasta_jogo = pasta_jogo
        self.vmu_files = self.localizar_arquivos_vmu()
        self.saves_encontrados = []
        self.arquivo_atual = None
        self.imagens_cache = [] # Evita que o Python limpe as imagens da memória!

        self.construir_ui()

    def localizar_arquivos_vmu(self):
        caminhos = []
        # FILTRO 1: Apenas os Memory Cards Globais Puros (Sem nenhum prefixo de jogo!)
        if self.modo_filtro == "global":
            pasta = os.path.join(self.install_path, "data")
            
            # Lista exata e estrita das 8 portas padrão do Dreamcast
            vmus_globais_permitidos = {
                "vmu_save_a1.bin", "vmu_save_a2.bin",
                "vmu_save_b1.bin", "vmu_save_b2.bin",
                "vmu_save_c1.bin", "vmu_save_c2.bin",
                "vmu_save_d1.bin", "vmu_save_d2.bin"
            }
            
            if os.path.exists(pasta):
                for f in os.listdir(pasta):
                    # Compara o nome exato em minúsculas
                    if f.lower() in vmus_globais_permitidos:
                        caminhos.append(os.path.join(pasta, f))
                        
        # FILTRO 2: Apenas a pasta isolada do Jogo Atual
        elif self.modo_filtro == "jogo" and self.pasta_jogo:
            if os.path.exists(self.pasta_jogo):
                for f in os.listdir(self.pasta_jogo):
                    if f.lower().endswith('.bin') and 'vmu' in f.lower():
                        caminhos.append(os.path.join(self.pasta_jogo, f))
        
        # Fallback de segurança genérico
        else:
            pastas_busca = [os.path.join(self.install_path, "data"), os.path.join(self.install_path, "vmu"), self.install_path]
            for pasta in pastas_busca:
                if os.path.exists(pasta):
                    for f in os.listdir(pasta):
                        if f.lower().endswith('.bin') and 'vmu' in f.lower():
                            caminhos.append(os.path.join(pasta, f))
                            
        return sorted(list(set(caminhos)))

    def construir_ui(self):
        lbl_title = ctk.CTkLabel(self, text="🔍 Scanner de Memory Card (VMU)", font=ctk.CTkFont(size=18, weight="bold"), text_color="#00FF7F")
        lbl_title.pack(pady=(20, 5))

        lbl_desc = ctk.CTkLabel(self, text="Selecione um arquivo de VMU para decodificar seus blocos e listar os saves internos.", text_color="gray", justify="center")
        lbl_desc.pack(pady=(0, 15))

        # --- SELETOR DE ARQUIVOS VMU ---
        frame_seletor = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=8)
        frame_seletor.pack(fill="x", padx=20, pady=5)

        lbl_sel = ctk.CTkLabel(frame_seletor, text="Unidade Conectada:", font=ctk.CTkFont(weight="bold"))
        lbl_sel.pack(side="left", padx=15, pady=15)

        nomes_arquivos = [os.path.basename(f) for f in self.vmu_files]
        self.combo_vmu = ctk.CTkComboBox(frame_seletor, values=nomes_arquivos if nomes_arquivos else ["Nenhum VMU encontrado"], width=250, state="readonly", command=self.ao_trocar_vmu)
        self.combo_vmu.pack(side="left", padx=10, pady=15)
        
        # --- ESTATÍSTICAS E BOTÃO BIOS ---
        self.frame_stats = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_stats.pack(fill="x", padx=20, pady=5)

        self.lbl_blocks = ctk.CTkLabel(self.frame_stats, text="Blocos Livres: -- / 200", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1E90FF")
        self.lbl_blocks.pack(side="left", padx=5)

        # 👇 O NOVO BOTÃO DE RESGATE DA NUVEM 👇
        self.btn_cloud = ctk.CTkButton(self.frame_stats, text="☁️ Resgate da Nuvem", fg_color="#1E90FF", hover_color="#4169E1", font=ctk.CTkFont(weight="bold"), command=self.abrir_resgate_nuvem)
        self.btn_cloud.pack(side="right", padx=(5, 0))

        # 👇 O BOTÃO DE ACESSO AO GERENCIADOR SEGURO NATIVO 👇
        self.btn_bios = ctk.CTkButton(self.frame_stats, text="🎮 Abrir BIOS (Para Copiar Saves)", fg_color="#FFD700", hover_color="#DAA520", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.iniciar_bios)
        self.btn_bios.pack(side="right", padx=5)

        # --- LISTA DE SAVES ---
        self.scroll_saves = ctk.CTkScrollableFrame(self, fg_color="#2b2b2b", corner_radius=10)
        self.scroll_saves.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        if nomes_arquivos:
            self.combo_vmu.set(nomes_arquivos[0])
            self.ao_trocar_vmu(nomes_arquivos[0])

    def iniciar_bios(self):
        """Abre um aviso orientando o usuário antes de lançar o emulador de forma limpa."""
        flycast_exe = os.path.join(self.install_path, "flycast.exe")
        if not os.path.exists(flycast_exe):
            mb.showerror("Erro", "O executável do Flycast não foi encontrado.", parent=self)
            return

        import subprocess

        # Cria a janela de Briefing (Aviso)
        win_aviso = ctk.CTkToplevel(self)
        win_aviso.title("Instruções de Acesso")
        win_aviso.geometry("520x340")
        win_aviso.attributes("-topmost", True)
        win_aviso.grab_set()

        lbl_title = ctk.CTkLabel(win_aviso, text="Como acessar o Gerenciador de VMU?", font=ctk.CTkFont(size=17, weight="bold"), text_color="#1E90FF")
        lbl_title.pack(pady=(20, 10))

        texto_instrucao = (
            "Para copiar ou organizar os saves, utilizaremos a interface original do próprio console.\n\n"
            "1. O emulador Flycast será aberto a seguir.\n"
            "2. Na grade de jogos, clique no primeiro quadro escrito 'Dreamcast'.\n"
            "3. A clássica espiral aparecerá e você entrará no menu do console!"
        )
        
        lbl_inst = ctk.CTkLabel(win_aviso, text=texto_instrucao, justify="left", wraplength=460, font=ctk.CTkFont(size=13))
        lbl_inst.pack(padx=20, pady=(0, 10))
        
        texto_aviso = "⚠️ Importante: O quadro 'Dreamcast' só aparecerá no emulador se os arquivos oficiais de BIOS (dc_boot.bin e dc_flash.bin) estiverem instalados corretamente."
        lbl_aviso = ctk.CTkLabel(win_aviso, text=texto_aviso, justify="left", wraplength=460, font=ctk.CTkFont(size=12, slant="italic"), text_color="#FFD700")
        lbl_aviso.pack(padx=20, pady=(0, 20))

        # Variável para controlar o tempo
        self.tempo_restante_bios = 10

        def executar_emulador():
            if win_aviso.winfo_exists():
                win_aviso.destroy()
            try:
                subprocess.Popen([flycast_exe], cwd=self.install_path)
                self.destroy() # Fecha o Raio-X do VMU
            except Exception as e:
                mb.showerror("Erro", f"Falha ao iniciar o Flycast: {e}", parent=self)

        btn_iniciar = ctk.CTkButton(win_aviso, text=f"Abrir Emulador ({self.tempo_restante_bios}s)", height=40, width=200, font=ctk.CTkFont(weight="bold"), fg_color="#228B22", hover_color="#006400", command=executar_emulador)
        btn_iniciar.pack(pady=(0, 10))

        def atualizar_contador():
            if not win_aviso.winfo_exists(): return
            self.tempo_restante_bios -= 1
            if self.tempo_restante_bios > 0:
                btn_iniciar.configure(text=f"Abrir Emulador ({self.tempo_restante_bios}s)")
                win_aviso.after(1000, atualizar_contador)
            else:
                executar_emulador()

        # Inicia a contagem de 1 segundo de forma recursiva
        win_aviso.after(1000, atualizar_contador)

    def ao_trocar_vmu(self, nome_arquivo):
        self.arquivo_atual = next((f for f in self.vmu_files if os.path.basename(f) == nome_arquivo), None)
        if self.arquivo_atual:
            self.escanear_vmu(self.arquivo_atual)

    def escanear_vmu(self, filepath):
        for widget in self.scroll_saves.winfo_children():
            widget.destroy()
            
        self.saves_encontrados = []
        self.imagens_cache.clear()
        blocos_usados = 0

        try:
            with open(filepath, "rb") as f:
                # 1. LÊ A TABELA FAT DO VMU (Bloco 254)
                f.seek(254 * 512)
                fat_data = f.read(512)
                fat = struct.unpack('<256H', fat_data)
                
                # 2. LÊ O DIRETÓRIO (Blocos 253 a 241)
                for bloco in range(253, 240, -1):
                    offset_bloco = bloco * 512
                    
                    for i in range(16):
                        offset_entrada = offset_bloco + (i * 32)
                        f.seek(offset_entrada)
                        dados_entrada = f.read(32)
                        
                        if len(dados_entrada) < 32: continue
                        
                        tipo_arquivo = dados_entrada[0]
                        # 0x33 = Data / Save, 0xCC = Jogo / DLC
                        if tipo_arquivo in (0x33, 0xCC):
                            try:
                                tamanho_blocos = struct.unpack('<H', dados_entrada[24:26])[0]
                                blocos_usados += tamanho_blocos
                                
                                # Nome de resgate caso o ícone/header esteja ausente
                                nome_cru = dados_entrada[4:16]
                                nome_limpo = nome_cru.split(b'\x00')[0].decode('ascii', errors='ignore').strip()
                                
                                primeiro_bloco = struct.unpack('<H', dados_entrada[2:4])[0]
                                header_offset = struct.unpack('<H', dados_entrada[26:28])[0]
                                
                                # Segue a tabela FAT para achar o bloco exato do VMS Header
                                b_atual = primeiro_bloco
                                for _ in range(header_offset):
                                    if b_atual >= 256 or b_atual == 0xFFFC: break
                                    b_atual = fat[b_atual]
                                    
                                # O Header do VMU + Ícone precisam de 640 bytes.
                                # Lemos 2 blocos (1024 bytes) seguindo a FAT para garantir!
                                vms_data = b""
                                for _ in range(2):
                                    if b_atual >= 256 or b_atual == 0xFFFC: break
                                    f.seek(b_atual * 512)
                                    vms_data += f.read(512)
                                    b_atual = fat[b_atual]
                                    
                                desc_curta = vms_data[0:16].decode('ascii', errors='ignore').replace('\x00', '').strip() if len(vms_data) >= 16 else ""
                                desc_longa = vms_data[16:48].decode('ascii', errors='ignore').replace('\x00', '').strip() if len(vms_data) >= 48 else ""
                                
                                titulo_real = desc_longa if desc_longa else (desc_curta if desc_curta else nome_limpo)
                                
                                img_tk = None
                                if HAS_PIL and len(vms_data) >= 640:
                                    try:
                                        num_icons = struct.unpack('<H', vms_data[0x40:0x42])[0]
                                        if num_icons > 0:
                                            palette = []
                                            for j in range(16):
                                                c = struct.unpack('<H', vms_data[0x60 + j*2 : 0x62 + j*2])[0]
                                                # ARGB4444: Separa os canais e converte pra escala 255
                                                a = ((c >> 12) & 0xF) * 17
                                                r = ((c >> 8) & 0xF) * 17
                                                g = ((c >> 4) & 0xF) * 17
                                                b_color = (c & 0xF) * 17
                                                palette.append((r, g, b_color, a))
                                            
                                            img = Image.new('RGBA', (32, 32))
                                            pixels = img.load()
                                            
                                            idx = 0
                                            for y in range(32):
                                                for x in range(0, 32, 2):
                                                    byte = vms_data[0x80 + idx]
                                                    idx += 1
                                                    p1 = (byte >> 4) & 0xF
                                                    p2 = byte & 0xF
                                                    pixels[x, y] = palette[p1]
                                                    pixels[x+1, y] = palette[p2]
                                            
                                            img = img.resize((64, 64), Image.Resampling.NEAREST)
                                            img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(64, 64))
                                    except Exception: pass

                                if titulo_real:
                                    self.saves_encontrados.append({
                                        "nome": titulo_real,
                                        "blocos": tamanho_blocos,
                                        "icone": img_tk
                                    })
                            except Exception: pass
                            
            self.renderizar_lista_saves(blocos_usados)
            
        except Exception as e:
            lbl_erro = ctk.CTkLabel(self.scroll_saves, text=f"❌ Ocorreu um erro ao ler o arquivo de VMU:\n{e}", text_color="#FF4C4C")
            lbl_erro.pack(pady=40)

    def renderizar_lista_saves(self, blocos_usados):
        blocos_livres = 200 - blocos_usados
        if blocos_livres < 0: blocos_livres = 0
        
        cor_bloco = "#FF4C4C" if blocos_livres < 10 else "#00FF7F"
        self.lbl_blocks.configure(text=f"Blocos Livres: {blocos_livres} / 200", text_color=cor_bloco)

        if not self.saves_encontrados:
            lbl_vazio = ctk.CTkLabel(self.scroll_saves, text="Este Memory Card está completamente vazio.", text_color="gray", font=ctk.CTkFont(slant="italic"))
            lbl_vazio.pack(pady=40)
            return

        for save in self.saves_encontrados:
            card = ctk.CTkFrame(self.scroll_saves, fg_color="#1a1a1a", corner_radius=8)
            card.pack(fill="x", padx=10, pady=5)
            
            # Aplica o Ícone extraído direto do bloco hex ou usa fallback
            if save["icone"]:
                self.imagens_cache.append(save["icone"]) # Protege do Garbage Collector
                lbl_icon = ctk.CTkLabel(card, image=save["icone"], text="")
                lbl_icon.pack(side="left", padx=15, pady=10)
            else:
                lbl_icon = ctk.CTkLabel(card, text="💾", font=ctk.CTkFont(size=28))
                lbl_icon.pack(side="left", padx=15, pady=10)
            
            frame_info = ctk.CTkFrame(card, fg_color="transparent")
            frame_info.pack(side="left", fill="both", expand=True, padx=5, pady=10)
            
            ctk.CTkLabel(frame_info, text=save["nome"], font=ctk.CTkFont(size=15, weight="bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(frame_info, text=f"Tamanho: {save['blocos']} blocos", font=ctk.CTkFont(size=12), text_color="gray", anchor="w").pack(fill="x")

    def abrir_resgate_nuvem(self):
        # Tenta buscar a rota da nuvem configurada no motor principal
        config = getattr(self.master, 'config_atual', {})
        cloud_path_root = config.get("cloud_path", "")
        
        if not cloud_path_root or not os.path.exists(cloud_path_root):
            mb.showwarning("Nuvem Desconectada", "O radar não encontrou sua Nuvem.\n\nConfigure o Google Drive ou OneDrive na aba de 'Saves' do Launcher principal antes de solicitar o Resgate Tático.", parent=self)
            return

        # 👇 O ALVO EXATO: Mira diretamente na pasta onde os backups são salvos! 👇
        pasta_alvo = os.path.join(cloud_path_root, "Flycast_Saves_Backup")
            
        win_cloud = ctk.CTkToplevel(self)
        win_cloud.title("☁️ Resgate Tático da Nuvem")
        win_cloud.geometry("650x500")
        win_cloud.attributes("-topmost", True)
        win_cloud.grab_set()
        
        ctk.CTkLabel(win_cloud, text="Arquivos de Save Sincronizados", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1E90FF").pack(pady=(15, 5))
        ctk.CTkLabel(win_cloud, text=f"Lendo de: {pasta_alvo}", text_color="gray", font=ctk.CTkFont(size=11)).pack(pady=(0, 10))
        
        scroll_cloud = ctk.CTkScrollableFrame(win_cloud, fg_color="#1a1a1a", corner_radius=10)
        scroll_cloud.pack(fill="both", expand=True, padx=20, pady=10)
        
        arquivos_nuvem = []
        if os.path.exists(pasta_alvo):
            try:
                # O escaneamento agora é instantâneo e à prova de falhas de permissão!
                for f in os.listdir(pasta_alvo):
                    if f.lower().endswith(('.bin', '.state', '.zip')):
                        arquivos_nuvem.append(os.path.join(pasta_alvo, f))
            except Exception as e:
                ctk.CTkLabel(scroll_cloud, text=f"Erro de varredura: {e}", text_color="#FF4C4C").pack(pady=20)
            
        if not arquivos_nuvem:
            ctk.CTkLabel(scroll_cloud, text="Nenhum backup compatível (.bin, .state ou .zip) localizado na sua Nuvem.", text_color="gray", font=ctk.CTkFont(slant="italic")).pack(pady=40)
            return
            
        # Ordena o arsenal: Os backups mais recentes ficam no topo!
        arquivos_nuvem.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        import datetime
        import shutil
        import zipfile
        
        def puxar_da_nuvem(caminho_origem):
            nome_arquivo = os.path.basename(caminho_origem)
            dest_dir = os.path.join(self.install_path, "data")
            os.makedirs(dest_dir, exist_ok=True)
            
            try:
                # SE O BACKUP FOR ZIP, ELE EXTRAI OS VMUS CIRURGICAMENTE
                if caminho_origem.lower().endswith('.zip'):
                    extraidos = 0
                    with zipfile.ZipFile(caminho_origem, 'r') as zip_ref:
                        for info in zip_ref.infolist():
                            if info.filename.endswith('/'): continue
                            basename = os.path.basename(info.filename)
                            # Puxa os Memory Cards e Saves SRM de volta pro emulador!
                            if (basename.lower().startswith('vmu') and basename.lower().endswith('.bin')) or basename.lower().endswith('.srm'):
                                dest_path = os.path.join(dest_dir, basename)
                                with zip_ref.open(info.filename) as src, open(dest_path, "wb") as tgt:
                                    shutil.copyfileobj(src, tgt)
                                extraidos += 1
                    mb.showinfo("Resgate Concluído", f"{extraidos} arquivos de save foram extraídos do backup '{nome_arquivo}' e injetados com sucesso!", parent=win_cloud)
                
                # SE FOR UM ARQUIVO SOLTO (.BIN / .STATE), APENAS COPIA
                else:
                    dest = os.path.join(dest_dir, nome_arquivo)
                    shutil.copy2(caminho_origem, dest)
                    mb.showinfo("Resgate Concluído", f"O arquivo '{nome_arquivo}' foi injetado com sucesso no emulador!", parent=win_cloud)
                
                # Força a interface a reler os VMUs locais e atualizar a tela do raio-x!
                self.vmu_files = self.localizar_arquivos_vmu()
                nomes_arquivos = [os.path.basename(f) for f in self.vmu_files]
                self.combo_vmu.configure(values=nomes_arquivos)
                if nomes_arquivos:
                    self.combo_vmu.set(nomes_arquivos[0])
                    self.ao_trocar_vmu(nomes_arquivos[0])
                    
            except Exception as e:
                mb.showerror("Falha no Resgate", f"Ocorreu um erro ao puxar o arquivo:\n{e}", parent=win_cloud)
        
        # Desenha a lista de suprimentos
        for caminho_completo in arquivos_nuvem:
            nome_arquivo = os.path.basename(caminho_completo)
            tamanho_kb = os.path.getsize(caminho_completo) // 1024
            data_mod = datetime.datetime.fromtimestamp(os.path.getmtime(caminho_completo)).strftime('%d/%m/%Y %H:%M')
            
            card = ctk.CTkFrame(scroll_cloud, fg_color="#2b2b2b", corner_radius=8)
            card.pack(fill="x", padx=5, pady=5)
            
            icone = "📦" if nome_arquivo.lower().endswith('.zip') else ("📸" if nome_arquivo.lower().endswith('.state') else "💾")
            ctk.CTkLabel(card, text=icone, font=ctk.CTkFont(size=24)).pack(side="left", padx=15, pady=10)
            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            ctk.CTkLabel(info_frame, text=nome_arquivo, font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(info_frame, text=f"Data: {data_mod} | Tam: {tamanho_kb} KB", font=ctk.CTkFont(size=11), text_color="gray", anchor="w").pack(fill="x")
            
            btn_baixar = ctk.CTkButton(card, text="📥 Injetar", width=80, fg_color="#228B22", hover_color="#006400", font=ctk.CTkFont(weight="bold"), command=lambda c=caminho_completo: puxar_da_nuvem(c))
            btn_baixar.pack(side="right", padx=15)