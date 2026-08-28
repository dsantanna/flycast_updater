import os
import json
import zipfile
import threading
import urllib.request
import customtkinter as ctk
import tkinter.messagebox as mb

class HomebrewShop:
    def __init__(self, app_instance):
        self.app = app_instance
        self.catalogo = []
        self.parent_frame_ref = None
        
        # Catálogo de segurança local (Fallback caso o usuário esteja sem internet)
        self.catalogo_fallback = [
            {
                "id": "hb_doom",
                "nome": "Doom (Port - Offline)",
                "dev": "Comunidade",
                "tamanho": "12 MB",
                "desc": "Catálogo offline ativado. Conecte-se à internet para carregar os homebrews mais recentes da nuvem.",
                "url": ""
            }
        ]

    def construir_interface(self, parent_frame):
        self.parent_frame_ref = parent_frame
        
        self.scroll_main = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.scroll_main.pack(fill="both", expand=True)

        self.frame_header = ctk.CTkFrame(self.scroll_main, fg_color="#1a1a1a", corner_radius=10)
        self.frame_header.pack(fill="x", padx=10, pady=(10, 15), ipadx=10, ipady=10)
        
        lbl_title = ctk.CTkLabel(self.frame_header, text="🌍 Central de Homebrews & Indies", font=ctk.CTkFont(size=18, weight="bold"), text_color="#00FF7F")
        lbl_title.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.lbl_status_loja = ctk.CTkLabel(self.frame_header, text="⏳ Sincronizando catálogo com a nuvem...", text_color="cyan")
        self.lbl_status_loja.pack(anchor="w", padx=10, pady=(0, 5))

        # Dispara a busca assíncrona do JSON na nuvem
        threading.Thread(target=self.carregar_catalogo_online, daemon=True).start()

    def carregar_catalogo_online(self):
        # 💡 DICA: Quando subir seu JSON para o GitHub, cole o link "Raw" (cru) aqui!
        url_json = "https://raw.githubusercontent.com/dsantanna/flycast_updater_shop/main/homebrews.json"
        
        try:
            self.app.log("🛒 Loja: Sincronizando índice de homebrews na nuvem...")
            req = urllib.request.Request(url_json, headers={'User-Agent': 'FlycastUpdater/v6.4'})
            with urllib.request.urlopen(req, timeout=5) as response:
                dados_json = json.loads(response.read().decode('utf-8'))
                if isinstance(dados_json, list) and dados_json:
                    self.catalogo = dados_json
                    self.app.log(f"✅ Loja: {len(self.catalogo)} jogos carregados da nuvem com sucesso.")
        except Exception as e:
            self.app.log(f"⚠️ Loja: Falha ao buscar catálogo online ({e}). Ativando catálogo de segurança local.")
            self.catalogo = self.catalogo_fallback

        # Devolve o controle para a Thread Principal para desenhar os cards na tela com segurança
        self.app.after(0, self.renderizar_vitrine)

    def renderizar_vitrine(self):
        # Limpa widgets anteriores caso haja um re-carregamento
        for widget in self.scroll_main.winfo_children():
            if widget != self.frame_header:
                widget.destroy()

        if hasattr(self, 'lbl_status_loja') and self.lbl_status_loja.winfo_exists():
            self.lbl_status_loja.configure(text=f"Catálogo online sincronizado ({len(self.catalogo)} itens disponíveis na nuvem).", text_color="#00FF7F")

        for jogo in self.catalogo:
            self._criar_card_jogo(self.scroll_main, jogo)

    def _criar_card_jogo(self, parent, jogo):
        card = ctk.CTkFrame(parent, fg_color="#2b2b2b", corner_radius=8)
        card.pack(fill="x", padx=10, pady=6)
        
        lbl_icon = ctk.CTkLabel(card, text="🕹️", font=ctk.CTkFont(size=40), width=80, height=80, fg_color="#1a1a1a", corner_radius=8)
        lbl_icon.pack(side="left", padx=10, pady=10)
        
        frame_info = ctk.CTkFrame(card, fg_color="transparent")
        frame_info.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame_info, text=jogo["nome"], font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(frame_info, text=f"Dev: {jogo['dev']}  |  Tamanho: {jogo['tamanho']}", font=ctk.CTkFont(size=11, slant="italic"), text_color="gray", anchor="w").pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(frame_info, text=jogo["desc"], font=ctk.CTkFont(size=12), text_color="#AAAAAA", anchor="w", justify="left").pack(fill="x")

        btn_baixar = ctk.CTkButton(card, text="⬇️ Baixar e Instalar", width=140, fg_color="#1E90FF", hover_color="#4169E1", font=ctk.CTkFont(weight="bold"))
        btn_baixar.configure(command=lambda j=jogo, b=btn_baixar: self.iniciar_download(j, b))
        btn_baixar.pack(side="right", padx=15)

    def iniciar_download(self, jogo, btn_widget):
        if not hasattr(self.app, 'rom_paths_list') or not self.app.rom_paths_list:
            mb.showwarning("Aviso", "Nenhuma pasta de ROMs configurada! Mapeie uma pasta na aba 'Configurações' primeiro.", parent=self.app)
            return

        if not jogo["url"]:
            mb.showerror("Link Indisponível", f"O jogo '{jogo['nome']}' não possui um link de download direto válido cadastrado no índice remoto.", parent=self.app)
            return

        pasta_destino_roms = self.app.rom_paths_list[0]
        arquivo_zip_temp = os.path.join(pasta_destino_roms, f"{jogo['id']}_temp.zip")
        
        btn_widget.configure(text="⏳ Baixando...", state="disabled", fg_color="#FF8C00")
        
        def rotina_worker():
            try:
                self.app.log(f"🛒 Loja: Iniciando download de {jogo['nome']}...")
                urllib.request.urlretrieve(jogo["url"], arquivo_zip_temp)
                
                self.app.after(0, lambda: btn_widget.configure(text="📦 Extraindo..."))
                self.app.log(f"🛒 Loja: Extraindo {jogo['nome']} para {pasta_destino_roms}...")
                
                if os.path.exists(arquivo_zip_temp):
                    with zipfile.ZipFile(arquivo_zip_temp, 'r') as zip_ref:
                        zip_ref.extractall(pasta_destino_roms)
                    os.remove(arquivo_zip_temp)
                
                self.app.log(f"✨ Loja: {jogo['nome']} instalado com sucesso!")
                self.app.after(0, lambda: btn_widget.configure(text="✔️ Instalado", fg_color="#228B22"))
                self.app.after(0, lambda: self.app.mostrar_toast("Download Concluído", f"{jogo['nome']} foi adicionado à sua biblioteca!", "success"))
                
                if hasattr(self.app, 'game_manager'):
                    self.app.after(1500, self.app.game_manager.escanear_jogos)
                
            except Exception as e:
                self.app.log(f"❌ Erro na Loja ({jogo['nome']}): {e}")
                if os.path.exists(arquivo_zip_temp): os.remove(arquivo_zip_temp)
                self.app.after(0, lambda: btn_widget.configure(text="❌ Falha", fg_color="#8B0000"))
                self.app.after(0, lambda: mb.showerror("Erro de Download", f"Não foi possível baixar {jogo['nome']}.\n\nDetalhe: {e}", parent=self.app))
                self.app.after(3000, lambda: btn_widget.configure(text="⬇️ Tentar Novamente", state="normal", fg_color="#1E90FF"))

        threading.Thread(target=rotina_worker, daemon=True).start()