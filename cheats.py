import os
import urllib.request
import urllib.parse
import json
import re
import threading
import customtkinter as ctk
import tkinter.messagebox as mb
import tkinter as tk

# Variável global para guardar a lista do Github e não sobrecarregar a rede
_CHEATS_CACHE = []

def baixar_cheat(nome_jogo, rom_basename, game_id, cheat_dir, log_callback):
    global _CHEATS_CACHE
    
    try:
        os.makedirs(cheat_dir, exist_ok=True)
    except Exception as e:
        log_callback(f"❌ Cheats: Erro ao preparar pasta - {e}")
        return False
        
    destino_rom = os.path.join(cheat_dir, f"{rom_basename}.cht")
    
    destino_id = None
    if game_id:
        safe_id = re.sub(r'[\\/*?:"<>|]', "", game_id).strip()
        destino_id = os.path.join(cheat_dir, f"{safe_id}.cht")
    
    if (destino_id and os.path.exists(destino_id)) or os.path.exists(destino_rom):
        log_callback(f"🛡️ Cheats: Arquivos de trapaça já estão prontos para '{nome_jogo}'.")
        return True

    nome_busca = nome_jogo.replace("_", " ").lower()
    nome_limpo = re.sub(r'\(.*?\)|\[.*?\]', '', nome_busca).strip().lower()
    rom_lower = rom_basename.lower()
    
    if not _CHEATS_CACHE:
        api_url = "https://api.github.com/repos/libretro/libretro-database/contents/cht/Sega%20-%20Dreamcast"
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                dados = json.loads(response.read().decode('utf-8'))
                _CHEATS_CACHE = [item for item in dados if item['name'].endswith('.cht')]
        except Exception as e:
            log_callback(f"⚠️ Cheats: Limite da API ou erro de conexão - {e}")
            
    arquivo_alvo = None
    for item in _CHEATS_CACHE:
        nome_repo = item['name'].lower()
        nome_repo_sem_ext = nome_repo.replace('.cht', '')
        
        if nome_repo_sem_ext == nome_busca or nome_repo_sem_ext == nome_limpo or nome_repo_sem_ext == rom_lower:
            arquivo_alvo = item
            break
            
    if not arquivo_alvo:
        for item in _CHEATS_CACHE:
            nome_repo = item['name'].lower()
            if len(nome_limpo) > 3 and (nome_limpo in nome_repo or nome_repo.replace('.cht', '') in nome_limpo):
                arquivo_alvo = item
                break

    if arquivo_alvo:
        download_url = arquivo_alvo['download_url']
        try:
            req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read()
                
                with open(destino_rom, 'wb') as out_file:
                    out_file.write(content)
                    
                if destino_id:
                    with open(destino_id, 'wb') as out_file:
                        out_file.write(content)
                    log_callback(f"👾 Cheats: Trapaça forjada como '{safe_id}.cht' (Auto-Load ativado)!")
                else:
                    log_callback(f"👾 Cheats: Trapaças baixadas com sucesso! ({arquivo_alvo['name']})")
                    
            return True
        except Exception as e:
            log_callback(f"❌ Cheats: Falha no download - {e}")
            return False
            
    log_callback(f"⚠️ Cheats: Poxa... Nenhuma trapaça localizada na nuvem para '{nome_jogo}'.")
    return False

# ==========================================
# NOVA INTERFACE GRÁFICA DO GERENCIADOR
# ==========================================
class VisualCheatManager:
    def __init__(self, app, nome_jogo, rom_path, game_id=None):
        self.app = app
        self.nome_jogo = nome_jogo
        self.rom_basename = os.path.splitext(os.path.basename(rom_path))[0] if rom_path else ""
        self.game_id = game_id
        
        install_path = self.app.entry_path.get()
        use_custom = getattr(self.app, 'switch_custom_paths', None) and self.app.switch_custom_paths.get() == 1
        
        if use_custom and hasattr(self.app, 'entry_cheat_path') and self.app.entry_cheat_path.get():
            self.cheat_dir = self.app.entry_cheat_path.get()
        else:
            self.cheat_dir = os.path.join(install_path, "data", "cheats")
            
        self.arquivo_cht = None
        self.lista_cheats = []
        self.vars_cheats = {}
        
        self.win = ctk.CTkToplevel(self.app)
        self.win.title(f"👾 Arsenal de Trapaças: {self.nome_jogo}")
        self.win.geometry("550x650")
        self.win.attributes("-topmost", True)
        self.win.grab_set()

        self.lbl_status = ctk.CTkLabel(self.win, text="🔍 Procurando trapaças no radar...", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_status.pack(pady=40)
        
        # Dispara o buscador assíncrono para não congelar a interface!
        threading.Thread(target=self.inicializar_radar, daemon=True).start()

    def inicializar_radar(self):
        # 1. Tenta achar o arquivo no disco rígido
        self.arquivo_cht = self._buscar_arquivo_local()
        
        # 2. Se não achar, chama o motor legado e baixa da nuvem (Libretro)
        if not self.arquivo_cht:
            self.app.after(0, lambda: self.lbl_status.configure(text="⏳ Baixando base de dados da nuvem (Libretro)...", text_color="#FFD700"))
            baixou = baixar_cheat(self.nome_jogo, self.rom_basename, self.game_id, self.cheat_dir, self.app.log)
            if baixou:
                self.arquivo_cht = self._buscar_arquivo_local()
                
        if not self.arquivo_cht:
            self.app.after(0, lambda: self.lbl_status.configure(text="❌ Nenhuma trapaça localizada no Libretro para este jogo.", text_color="#FF4C4C"))
            return
            
        # 3. Faz o Parse (Leitura) de todos os códigos de Hexadecimal
        self.lista_cheats = self._ler_arquivo_cht(self.arquivo_cht)
        
        if not self.lista_cheats:
            self.app.after(0, lambda: self.lbl_status.configure(text="⚠️ O arquivo foi baixado, mas não contém códigos no formato padrão.", text_color="#FF4C4C"))
            return
            
        self.app.after(0, self.construir_interface_lista)

    def _buscar_arquivo_local(self):
        if self.game_id:
            safe_id = re.sub(r'[\\/*?:"<>|]', "", self.game_id).strip()
            p1 = os.path.join(self.cheat_dir, f"{safe_id}.cht")
            if os.path.exists(p1): return p1
            
        p2 = os.path.join(self.cheat_dir, f"{self.rom_basename}.cht")
        if os.path.exists(p2): return p2
        return None
        
    def _ler_arquivo_cht(self, filepath):
        cheats = {}
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    linha = line.strip()
                    if linha.startswith('cheat') and '=' in linha:
                        partes = linha.split('=', 1)
                        chave = partes[0].strip()
                        valor = partes[1].strip().strip('"')
                        
                        match = re.match(r'cheat(\d+)_(.*)', chave)
                        if match:
                            idx = int(match.group(1))
                            prop = match.group(2)
                            
                            if idx not in cheats:
                                cheats[idx] = {"idx": idx, "desc": f"Trapaça {idx}", "enable": False}
                            
                            if prop == "desc":
                                cheats[idx]["desc"] = valor
                            elif prop == "enable":
                                cheats[idx]["enable"] = (valor.lower() == "true")
                                
            return [cheats[k] for k in sorted(cheats.keys())]
        except Exception as e:
            self.app.log(f"Erro ao desmembrar o .cht: {e}")
            return []

    def construir_interface_lista(self):
        self.lbl_status.destroy()
        
        lbl_title = ctk.CTkLabel(self.win, text="✔️ Arsenal Disponível", font=ctk.CTkFont(size=18, weight="bold"), text_color="#00FF7F")
        lbl_title.pack(pady=(15, 5))
        
        lbl_dica = ctk.CTkLabel(self.win, text="Marque as opções desejadas e clique em Salvar. O Flycast injetará os códigos selecionados automaticamente ao iniciar o jogo.", text_color="gray", wraplength=480)
        lbl_dica.pack(pady=(0, 15))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.win, fg_color="#1a1a1a", corner_radius=10)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        for c in self.lista_cheats:
            var = tk.BooleanVar(value=c["enable"])
            self.vars_cheats[c["idx"]] = var
            
            chk = ctk.CTkCheckBox(self.scroll_frame, text=c["desc"], variable=var, font=ctk.CTkFont(size=13, weight="bold"), text_color="#00BFFF", hover_color="#1E90FF")
            chk.pack(anchor="w", padx=10, pady=8)
            
        frame_botoes = ctk.CTkFrame(self.win, fg_color="transparent")
        frame_botoes.pack(fill="x", pady=20)
        
        btn_salvar = ctk.CTkButton(frame_botoes, text="💾 Salvar", width=200, height=35, font=ctk.CTkFont(weight="bold"), fg_color="#8B008B", hover_color="#A52A2A", command=self.salvar_e_fechar)
        btn_salvar.pack(side="left", expand=True, padx=10)
        
    def salvar_e_fechar(self):
        if not self.arquivo_cht or not os.path.exists(self.arquivo_cht): return
        
        try:
            with open(self.arquivo_cht, 'r', encoding='utf-8', errors='ignore') as f:
                linhas = f.readlines()
                
            with open(self.arquivo_cht, 'w', encoding='utf-8') as f:
                for linha in linhas:
                    linha_limpa = linha.strip()
                    modificada = False
                    
                    if linha_limpa.startswith('cheat') and '_enable' in linha_limpa:
                        match = re.match(r'cheat(\d+)_enable', linha_limpa)
                        if match:
                            idx = int(match.group(1))
                            if idx in self.vars_cheats:
                                novo_estado = "true" if self.vars_cheats[idx].get() else "false"
                                f.write(f'cheat{idx}_enable = {novo_estado}\n')
                                modificada = True
                    if not modificada:
                        f.write(linha)
                        
            self.app.log(f"👾 Cheats de {self.nome_jogo} atualizados e salvos com sucesso!")
            self.app.mostrar_toast("Arsenal Injetado", "Os códigos de trapaça foram configurados no jogo!", "success")
            if hasattr(self.app, 'sfx'): self.app.sfx.play("save")
            self.win.destroy()
            
        except Exception as e:
            self.app.log(f"❌ Erro ao salvar cheat: {e}")
            mb.showerror("Erro de Gravação", f"Não foi possível modificar o arquivo .cht:\n{e}", parent=self.win)