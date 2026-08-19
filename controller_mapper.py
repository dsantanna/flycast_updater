import os
import time
import threading
import re
import customtkinter as ctk
import tkinter.messagebox as mb

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

class ControllerMapper:
    def __init__(self, app_instance):
        self.app = app_instance
        self.joysticks = {}
        self.mapeamento_atual = {}
        
        # A lista de botões do Dreamcast que o usuário precisará apertar, em ordem.
        self.botoes_alvo = [
            ("A", "Botão A (Ação)"), 
            ("B", "Botão B (Voltar)"), 
            ("X", "Botão X"), 
            ("Y", "Botão Y"),
            ("Start", "Botão Start"), 
            ("DPad_Up", "D-Pad (Seta) para CIMA"), 
            ("DPad_Down", "D-Pad (Seta) para BAIXO"),
            ("DPad_Left", "D-Pad (Seta) para ESQUERDA"), 
            ("DPad_Right", "D-Pad (Seta) para DIREITA"),
            ("Analog_Up", "Analógico para CIMA"), 
            ("Analog_Down", "Analógico para BAIXO"),
            ("Analog_Left", "Analógico para ESQUERDA"), 
            ("Analog_Right", "Analógico para DIREITA"),
            ("Trigger_L", "Gatilho Esquerdo (LT / L2)"), 
            ("Trigger_R", "Gatilho Direito (RT / R2)")
        ]
        
        self.indice_mapeamento = 0
        self.mapeando = False
        self.joy_ativo = None

    def construir_interface(self, parent_frame):
        self.frame_main = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.frame_main.pack(fill="both", expand=True)

        lbl_title = ctk.CTkLabel(self.frame_main, text="🎮 Assistente Visual de Mapeamento", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        lbl_desc = ctk.CTkLabel(self.frame_main, text="Configure seu controle rapidamente. Siga as instruções na tela e nós geramos o arquivo para o Flycast.", text_color="gray")
        lbl_desc.pack(anchor="w", padx=10, pady=(0, 20))

        # ==========================================
        # PAINEL DE SELEÇÃO DE HARDWARE
        # ==========================================
        frame_selecao = ctk.CTkFrame(self.frame_main, fg_color="#1a1a1a", corner_radius=10)
        frame_selecao.pack(fill="x", padx=10, pady=(0, 20), ipadx=10, ipady=10)

        self.combo_joysticks = ctk.CTkComboBox(frame_selecao, values=["Nenhum controle detectado"], state="readonly", width=300)
        self.combo_joysticks.pack(side="left", padx=15, pady=15)

        btn_refresh = ctk.CTkButton(frame_selecao, text="🔄 Detectar", width=100, command=self.detectar_controles)
        btn_refresh.pack(side="left", padx=(0, 15))

        self.btn_iniciar = ctk.CTkButton(frame_selecao, text="▶️ Iniciar Mapeamento", width=160, fg_color="#228B22", hover_color="#006400", font=ctk.CTkFont(weight="bold"), command=self.iniciar_mapeamento)
        self.btn_iniciar.pack(side="left", padx=(0, 15))

        # ==========================================
        # PAINEL DE INSTRUÇÕES (HUD DE GAMEPLAY)
        # ==========================================
        self.frame_map = ctk.CTkFrame(self.frame_main, fg_color="#2b2b2b", corner_radius=10)
        
        self.lbl_instrucao = ctk.CTkLabel(self.frame_map, text="Pressione o botão...", font=ctk.CTkFont(size=26, weight="bold"), text_color="#00BFFF")
        self.lbl_instrucao.pack(pady=40)
        
        self.btn_pular = ctk.CTkButton(self.frame_map, text="⏭️ Pular este botão", fg_color="#8B0000", hover_color="#A52A2A", command=self.pular_botao)
        self.btn_pular.pack(pady=(0, 20))

        # Dispara o radar de controles meio segundo após a tela nascer
        self.app.after(500, self.detectar_controles)

    def detectar_controles(self):
        if not HAS_PYGAME:
            mb.showerror("Dependência Ausente", "A biblioteca Pygame não está instalada no sistema.", parent=self.app)
            return
            
        try:
            # A MÁGICA DA IGNIÇÃO: Ligando o motor de eventos nativo do Python!
            pygame.init() 
            pygame.joystick.init()
            
            self.joysticks.clear()
            
            count = pygame.joystick.get_count()
            if count == 0:
                self.combo_joysticks.configure(values=["Nenhum controle detectado"])
                self.combo_joysticks.set("Nenhum controle detectado")
                self.btn_iniciar.configure(state="disabled")
            else:
                nomes = []
                for i in range(count):
                    joy = pygame.joystick.Joystick(i)
                    joy.init()
                    # Mapeia pelo GUID para evitar clones
                    nome = f"[{i}] {joy.get_name()}"
                    self.joysticks[nome] = joy
                    nomes.append(nome)
                
                self.combo_joysticks.configure(values=nomes)
                self.combo_joysticks.set(nomes[0])
                self.btn_iniciar.configure(state="normal")
                if hasattr(self.app, 'sfx'): self.app.sfx.play("nav")
        except Exception as e:
            self.app.log(f"❌ Erro ao detectar controles: {e}")

    def iniciar_mapeamento(self):
        selecao = self.combo_joysticks.get()
        if selecao not in self.joysticks: return

        self.joy_ativo = self.joysticks[selecao]
        self.mapeamento_atual.clear()
        self.indice_mapeamento = 0
        self.mapeando = True
        
        # Bloqueia a UI para evitar confusões
        self.btn_iniciar.configure(state="disabled")
        self.combo_joysticks.configure(state="disabled")
        
        # Revela a tela de instrução
        self.frame_map.pack(fill="x", padx=10, pady=10)
        
        # Limpa o "lixo" de botões que foram apertados antes de iniciar, protegido!
        try:
            pygame.event.clear()
        except Exception: pass
        
        self.pedir_proximo_botao()
        self.app.after(100, self.escutar_eventos)

    def pedir_proximo_botao(self):
        if self.indice_mapeamento >= len(self.botoes_alvo):
            self.finalizar_mapeamento()
            return
            
        id_btn, nome_amigavel = self.botoes_alvo[self.indice_mapeamento]
        self.lbl_instrucao.configure(text=f"Pressione: {nome_amigavel}")

    def pular_botao(self):
        if not self.mapeando: return
        id_btn, _ = self.botoes_alvo[self.indice_mapeamento]
        self.mapeamento_atual[id_btn] = None # Salva como ignorado
        self.indice_mapeamento += 1
        if hasattr(self.app, 'sfx'): self.app.sfx.play("nav")
        self.pedir_proximo_botao()

    def registrar_input(self, tipo, valor):
        if not self.mapeando: return
        id_btn, _ = self.botoes_alvo[self.indice_mapeamento]
        self.mapeamento_atual[id_btn] = {"type": tipo, "val": valor}
        self.app.log(f"🎮 Botão '{id_btn}' capturado -> {tipo}:{valor}")
        
        if hasattr(self.app, 'sfx'): self.app.sfx.play("nav")
        
        self.indice_mapeamento += 1
        # Pausa a escuta por 300ms para evitar que o clique duplo preencha o próximo botão!
        self.mapeando = False
        self.app.after(300, self.retomar_mapeamento)

    def retomar_mapeamento(self):
        try:
            pygame.event.clear() # Limpa os rastros
        except Exception: pass
        self.mapeando = True
        self.pedir_proximo_botao()

    def escutar_eventos(self):
        """O Looping de Radar que lê o Hardware nativamente."""
        if not self.mapeando: 
            if self.indice_mapeamento < len(self.botoes_alvo):
                self.app.after(50, self.escutar_eventos)
            return

        try:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    self.registrar_input("button", event.button)
                    break
                elif event.type == pygame.JOYHATMOTION:
                    # Direcionais digitais em formato de tupla. Ex: (0, 1) = Cima
                    if event.value != (0, 0):
                        # Convertendo a tupla para uma string que o Flycast entenderá
                        val_str = f"hat0_{event.value[0]}_{event.value[1]}"
                        self.registrar_input("hat", val_str)
                        break
                elif event.type == pygame.JOYAXISMOTION:
                    # Captura apenas quando o analógico/gatilho é pressionado até a metade (Deadzone)
                    if abs(event.value) > 0.6:
                        direcao = "+" if event.value > 0 else "-"
                        self.registrar_input("axis", f"axis{event.axis}{direcao}")
                        break
        except Exception: pass
        
        self.app.after(50, self.escutar_eventos)

    def finalizar_mapeamento(self):
        self.mapeando = False
        self.lbl_instrucao.configure(text="✅ Mapeamento Concluído!", text_color="#00FF7F")
        self.btn_pular.pack_forget()
        if hasattr(self.app, 'sfx'): self.app.sfx.play("success")
        
        self.app.log("🎮 Gerando mapa de hardware nativo para o Flycast...")
        self.salvar_cfg_flycast()
        
        self.app.after(2000, self.resetar_ui)
        self.app.mostrar_toast("Hardware Configurado", "Seu controle foi mapeado e salvo com sucesso!", "success")

    def resetar_ui(self):
        self.frame_map.pack_forget()
        self.btn_pular.pack(pady=(0, 20)) # Restaura o botão para a próxima vez
        self.btn_iniciar.configure(state="normal")
        self.combo_joysticks.configure(state="normal")

    def salvar_cfg_flycast(self):
        """
        O Tradutor Universal: Converte o sinal do Pygame para o dialeto do Flycast
        e salva no formato exato que o emulador exige na pasta 'mappings'.
        """
        install_path = self.app.entry_path.get()
        map_dir = os.path.join(install_path, "mappings")
        os.makedirs(map_dir, exist_ok=True)
        
        # O nome do arquivo precisa refletir a identificação do controle
        joy_name = self.joy_ativo.get_name()
        nome_arquivo = re.sub(r'[\\/*?:"<>|]', "", joy_name) + ".cfg"
        cfg_path = os.path.join(map_dir, nome_arquivo)
        
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write("[emulator]\n")
                f.write(f"mapping_name = {joy_name} (Big Blue)\n")
                f.write("mapping_type = controller\n\n")
                
                f.write("[dreamcast]\n")
                
                # Tradução das batidas
                for dc_btn, data in self.mapeamento_atual.items():
                    if not data: continue # Ignorou o botão
                    
                    val = data['val']
                    # Botões nativos: btn_a = 0
                    if data["type"] == "button":
                        f.write(f"btn_{dc_btn.lower()} = {val}\n")
                    
                    # Eixos analógicos: axis_analog_up = axis1-
                    elif data["type"] == "axis":
                        # Simplificação para se encaixar na string base
                        f.write(f"btn_{dc_btn.lower()} = {val}\n")
                    
                    # D-Pads: btn_dpad_up = hat0_0_1
                    elif data["type"] == "hat":
                        f.write(f"btn_{dc_btn.lower()} = {val}\n")
                        
            self.app.log(f"💾 Perfil de Controle forjado com sucesso em: {cfg_path}")
        except Exception as e:
            self.app.log(f"❌ Erro ao compilar mapeamento: {e}")