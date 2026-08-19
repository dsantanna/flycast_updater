import os
import configparser
import customtkinter as ctk
import tkinter.messagebox as mb
from tkinter import colorchooser

# --- A MÁGICA DO TRANSPLANTE: Importamos o Mapeador Aqui! ---
import controller_mapper 

PERFIS_CONTROLES = {
    "Xbox (360 / One / Series)": {"arquivo": "XInput Controller.cfg", "conteudo": "[emulator]\nmapping_name = XInput Controller\n\n[dreamcast]\nbtn_a = 0\nbtn_b = 1\nbtn_x = 2\nbtn_y = 3\nbtn_start = 7\nbtn_dpad1_up = 11\nbtn_dpad1_down = 12\nbtn_dpad1_left = 13\nbtn_dpad1_right = 14\naxis_x = 0\naxis_y = 1\naxis_trigger_left = 4\naxis_trigger_right = 5\n"},
    "PlayStation (PS4 / PS5)": {"arquivo": "PS4 Controller.cfg", "conteudo": "[emulator]\nmapping_name = PS4 Controller\n\n[dreamcast]\nbtn_a = 1\nbtn_b = 2\nbtn_x = 0\nbtn_y = 3\nbtn_start = 9\nbtn_dpad1_up = 11\nbtn_dpad1_down = 12\nbtn_dpad1_left = 13\nbtn_dpad1_right = 14\naxis_x = 0\naxis_y = 1\naxis_trigger_left = 4\naxis_trigger_right = 5\n"},
    "Nintendo Switch (Pro Controller)": {"arquivo": "Switch Pro Controller.cfg", "conteudo": "[emulator]\nmapping_name = Switch Pro Controller\n\n[dreamcast]\nbtn_a = 1\nbtn_b = 0\nbtn_x = 3\nbtn_y = 2\nbtn_start = 9\nbtn_dpad1_up = 11\nbtn_dpad1_down = 12\nbtn_dpad1_left = 13\nbtn_dpad1_right = 14\naxis_x = 0\naxis_y = 1\naxis_trigger_left = 4\naxis_trigger_right = 5\n"},
    "8BitDo (Pro 2 / Ultimate / SN30)": {"arquivo": "8BitDo Controller.cfg", "conteudo": "[emulator]\nmapping_name = 8BitDo Controller\n\n[dreamcast]\nbtn_a = 1\nbtn_b = 0\nbtn_x = 3\nbtn_y = 2\nbtn_start = 11\nbtn_dpad1_up = 15\nbtn_dpad1_down = 16\nbtn_dpad1_left = 17\nbtn_dpad1_right = 18\naxis_x = 0\naxis_y = 1\naxis_trigger_left = 4\naxis_trigger_right = 5\n"},
    "Controle Genérico (USB / DirectInput)": {"arquivo": "Generic USB.cfg", "conteudo": "[emulator]\nmapping_name = Generic USB Joystick\n\n[dreamcast]\nbtn_a = 2\nbtn_b = 1\nbtn_x = 3\nbtn_y = 0\nbtn_start = 9\nbtn_dpad1_up = 12\nbtn_dpad1_down = 13\nbtn_dpad1_left = 14\nbtn_dpad1_right = 15\naxis_x = 0\naxis_y = 1\naxis_trigger_left = 4\naxis_trigger_right = 5\n"},
    "Arcade Stick (Controle de Luta)": {"arquivo": "Arcade Stick.cfg", "conteudo": "[emulator]\nmapping_name = Arcade Stick\n\n[dreamcast]\nbtn_a = 0\nbtn_b = 1\nbtn_x = 2\nbtn_y = 3\nbtn_c = 4\nbtn_z = 5\nbtn_start = 7\naxis_x = 0\naxis_y = 1\n"}
}

class DevicesManager:
    def __init__(self, app_instance):
        self.app = app_instance
        
        # --- INICIALIZAMOS O MAPPER AQUI! ---
        self.control_mgr = controller_mapper.ControllerMapper(self.app)
        
        self.combos_devices = {}
        self.combos_fisicos = {}
        self.btn_color_pickers = {}
        self.cores_mira = {"A": "0", "B": "0", "C": "0", "D": "0"}
        
        self.mapa_controles = {
            "Nenhum": "3", "Controle Sega": "0", "Controle de Alavanca Dupla": "8",
            "Controle de Arcade/Ascii": "4", "Controle Marcas": "12", "Controle de Pesca": "13",
            "Controle de música Pop'n": "14", "Controle de Corrida": "15", "Controle Densha de Go": "16",
            "Controle Panther DC": "18", "Controlador DreamParaPara": "19", "Teclado": "5",
            "Mouse": "6", "Pistola de Luz": "7"
        }
        
        self.mapa_acessorios = {
            "Nenhum": "0", "Sega VMU": "1", "Microfone": "2",
            "Pacote de Vibração": "3", "DreamPotato": "4"
        }

        self.rev_mapa_controles = {v: k for k, v in self.mapa_controles.items()}
        self.rev_mapa_acessorios = {v: k for k, v in self.mapa_acessorios.items()}

        self.mapa_portas_fisicas = {"0": "Porta A", "1": "Porta B", "2": "Porta C", "3": "Porta D"}
        self.rev_mapa_portas_fisicas = {v: k for k, v in self.mapa_portas_fisicas.items()}

    def construir_aba_dispositivos(self, tab):
        # ==========================================
        # CRIAÇÃO DAS SUB-ABAS
        # ==========================================
        self.tabview_devices = ctk.CTkTabview(tab)
        self.tabview_devices.pack(fill="both", expand=True, padx=5, pady=0)
        
        tab_geral = self.tabview_devices.add("⚙️ Hardware e Portas")
        tab_mapper = self.tabview_devices.add("🎮 Mapear Controles")
        
        # 1. Injetamos a interface do Mapeador na segunda sub-aba
        self.control_mgr.construir_interface(tab_mapper)
        
        # 2. Construímos todo o restante original na primeira sub-aba (tab_geral)
        self.scroll_devices = ctk.CTkScrollableFrame(tab_geral, fg_color="transparent")
        self.scroll_devices.pack(fill="both", expand=True)

        # --- INJEÇÃO DE PERFIS DE CONTROLE ---
        self.label_ctrl_title = ctk.CTkLabel(self.scroll_devices, text=self.app._("lbl_ctrl_title", default="Injeção de Perfis de Controle"), font=ctk.CTkFont(size=16, weight="bold"))
        self.label_ctrl_title.pack(anchor="w", padx=10, pady=(10, 5))

        self.label_ctrl_desc = ctk.CTkLabel(self.scroll_devices, text=self.app._("lbl_ctrl_desc", default="Selecione o modelo abaixo e injete na pasta mappings."), text_color="gray", justify="left")
        self.label_ctrl_desc.pack(anchor="w", padx=10, pady=(0, 10))

        self.frame_ctrl = ctk.CTkFrame(self.scroll_devices, fg_color="transparent")
        self.frame_ctrl.pack(fill="x", padx=10, pady=(0, 15))

        self.combo_ctrl = ctk.CTkComboBox(self.frame_ctrl, values=list(PERFIS_CONTROLES.keys()), width=350, state="readonly")
        self.combo_ctrl.pack(side="left", fill="x", expand=True, padx=(0, 10))
        if list(PERFIS_CONTROLES.keys()):
            self.combo_ctrl.set(list(PERFIS_CONTROLES.keys())[0])

        self.btn_injetar_ctrl = ctk.CTkButton(self.frame_ctrl, text=self.app._("btn_inject", default="Injetar Perfil de Controle"), width=200, height=30, font=ctk.CTkFont(weight="bold"), fg_color="#8B008B", hover_color="#A52A2A", command=self.injetar_controle)
        self.btn_injetar_ctrl.pack(side="right")

        self.frame_divisor_ctrl = ctk.CTkFrame(self.scroll_devices, height=2, fg_color="#444")
        self.frame_divisor_ctrl.pack(fill="x", padx=10, pady=(5, 15))

        # --- DISPOSITIVOS FÍSICOS REAIS ---
        frame_fisicos_header = ctk.CTkFrame(self.scroll_devices, fg_color="transparent")
        frame_fisicos_header.pack(fill="x", padx=10, pady=(0, 5))
        
        self.label_fisicos_title = ctk.CTkLabel(frame_fisicos_header, text="🎮 Dispositivos Mapeados (emu.cfg)", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_fisicos_title.pack(side="left")

        self.btn_rescan_fisicos = ctk.CTkButton(frame_fisicos_header, text="🔄 Rescanear", width=90, height=24, fg_color="#4169E1", hover_color="#1E90FF", font=ctk.CTkFont(weight="bold"), command=self.carregar_dispositivos)
        self.btn_rescan_fisicos.pack(side="right")

        self.frame_fisicos_list = ctk.CTkFrame(self.scroll_devices, fg_color="#1a1a1a", corner_radius=10)
        self.frame_fisicos_list.pack(fill="x", padx=10, pady=(0, 15))

        # --- DISPOSITIVOS VIRTUAIS DO DREAMCAST ---
        self.label_devices_title = ctk.CTkLabel(self.scroll_devices, text="🖥️ Portas Virtuais do Dreamcast", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_devices_title.pack(anchor="w", padx=10, pady=(5, 5))
        
        self.frame_devices_grid = ctk.CTkFrame(self.scroll_devices, fg_color="#1a1a1a", corner_radius=10)
        self.frame_devices_grid.pack(fill="x", padx=10, pady=5)

        portas = ["A", "B", "C", "D"]
        opcoes_controles = list(self.mapa_controles.keys())
        opcoes_acessorios = list(self.mapa_acessorios.keys())

        ctk.CTkLabel(self.frame_devices_grid, text="Porta", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkLabel(self.frame_devices_grid, text="Controle Principal", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=10)
        ctk.CTkLabel(self.frame_devices_grid, text="Slot 1 (VMU)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=10)
        ctk.CTkLabel(self.frame_devices_grid, text="Slot 2 (Extra)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=10)

        for i, p in enumerate(portas):
            lbl = ctk.CTkLabel(self.frame_devices_grid, text=f"Porta {p}", font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=i+1, column=0, padx=10, pady=10, sticky="e")

            cb_main = ctk.CTkComboBox(self.frame_devices_grid, values=opcoes_controles, width=190, state="readonly", command=lambda val, p=p: self.ao_trocar_controle_main(p, val))
            cb_main.grid(row=i+1, column=1, padx=5, pady=10)
            cb_main.set("Nenhum")
            self.combos_devices[f"{p}_main"] = cb_main

            cb_s1 = ctk.CTkComboBox(self.frame_devices_grid, values=opcoes_acessorios, width=140, state="readonly", command=self.salvar_dispositivos)
            cb_s1.grid(row=i+1, column=2, padx=5, pady=10)
            cb_s1.set("Nenhum")
            self.combos_devices[f"{p}_s1"] = cb_s1

            cb_s2 = ctk.CTkComboBox(self.frame_devices_grid, values=opcoes_acessorios, width=140, state="readonly", command=self.salvar_dispositivos)
            cb_s2.grid(row=i+1, column=3, padx=5, pady=10)
            cb_s2.set("Nenhum")
            self.combos_devices[f"{p}_s2"] = cb_s2

            btn_color = ctk.CTkButton(self.frame_devices_grid, text="🎯 Cor da Mira", width=140, fg_color="#333333", text_color="white", command=lambda p=p: self.escolher_cor_mira(p))
            btn_color.grid(row=i+1, column=3, padx=5, pady=10)
            btn_color.grid_remove()
            self.btn_color_pickers[p] = btn_color

        texto_dica = (
            "💡 Recomendações de Hardware:\n"
            "• Setup Padrão: 'Controle Sega' e 'Sega VMU' no Slot 1 da Porta A.\n"
            "• Vibração: Conecte o 'Pacote de Vibração' no Slot 2 da Porta A para Force Feedback.\n"
            "• Arcades: Jogos como Marvel vs Capcom ficam excelentes com 'Controle de Arcade/Ascii'."
        )
        self.lbl_devices_dica = ctk.CTkLabel(self.scroll_devices, text=texto_dica, text_color="gray", justify="left", font=ctk.CTkFont(size=12))
        self.lbl_devices_dica.pack(anchor="w", padx=15, pady=(15, 0))
        
        # --- RADAR DE FIRMWARE 8BITDO ---
        frame_8bitdo = ctk.CTkFrame(self.scroll_devices, fg_color="#1a1a1a", corner_radius=8)
        frame_8bitdo.pack(fill="x", padx=10, pady=(15, 0))
        
        lbl_8bitdo_title = ctk.CTkLabel(frame_8bitdo, text="🛠️ Manutenção de Hardware", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_8bitdo_title.pack(side="left", padx=15, pady=10)
        
        btn_8bitdo_update = ctk.CTkButton(frame_8bitdo, text="🎮 Checar Firmware 8BitDo", fg_color="#8B008B", hover_color="#A52A2A", font=ctk.CTkFont(weight="bold"), command=self.checar_firmware_8bitdo)
        btn_8bitdo_update.pack(side="right", padx=15, pady=10)
        
        self.frame_divisor_vmu = ctk.CTkFrame(self.scroll_devices, height=2, fg_color="#444")
        self.frame_divisor_vmu.pack(fill="x", padx=10, pady=(15, 10))

    # =========================================================================
    # DEMAIS MÉTODOS MANTIDOS INTACTOS (Mágica da Orientação a Objetos)
    # =========================================================================

    def injetar_controle(self):
        controle_selecionado = self.combo_ctrl.get()
        perfil = PERFIS_CONTROLES.get(controle_selecionado)
        if not perfil: return

        install_path = self.app.entry_path.get()
        if not install_path or not os.path.exists(install_path):
            mb.showerror("Erro", self.app._("msg_error"), parent=self.app)
            return

        mappings_dir = os.path.join(install_path, "data", "mappings")
        os.makedirs(mappings_dir, exist_ok=True)
        
        arquivo_destino = os.path.join(mappings_dir, perfil["arquivo"])
        try:
            with open(arquivo_destino, "w", encoding="utf-8") as f:
                f.write(perfil["conteudo"])
            self.app.log(f"🎮 Injeção: '{perfil['arquivo']}' injetado em data/mappings/ com sucesso.")
            self.app.mostrar_toast("Controle Injetado", "O perfil de controle foi aplicado com sucesso e está pronto para uso!", "success")
        except Exception as e:
            self.app.log(f"❌ Erro ao injetar o controle: {e}")
            self.app.mostrar_toast("Falha na Injeção", f"Não foi possível aplicar o controle: {e}", "error")

    def obter_dispositivos_fisicos(self):
        install_path = self.app.entry_path.get()
        cfg_path = next((p for p in [os.path.join(install_path, "emu.cfg"), os.path.join(install_path, "data", "emu.cfg")] if os.path.exists(p)), "")
        
        dispositivos = {}
        if cfg_path:
            config = configparser.RawConfigParser(strict=False)
            config.optionxform = str
            config.read(cfg_path, encoding='utf-8')
            if config.has_section('input'):
                for key, val in config.items('input'):
                    if key.startswith('maple_'): dispositivos[key] = val
        return dispositivos

    def atualizar_lista_fisicos(self):
        for widget in getattr(self, 'frame_fisicos_list', ctk.CTkFrame(self.app)).winfo_children():
            widget.destroy()
        
        dispositivos = self.obter_dispositivos_fisicos()
        self.combos_fisicos = {}

        joysticks_conectados = 0
        try:
            import pygame
            pygame.joystick.quit()
            pygame.joystick.init()
            joysticks_conectados = pygame.joystick.get_count()
        except Exception:
            pass
        
        if not dispositivos:
            lbl = ctk.CTkLabel(self.frame_fisicos_list, text="Nenhum dispositivo mapeado no emu.cfg.\nAbra um jogo no Flycast pelo menos uma vez com o controle conectado.", text_color="gray", justify="left")
            lbl.pack(pady=20, padx=10, anchor="w")
            return
            
        import re
        for i, (key, val) in enumerate(dispositivos.items()):
            nome_formatado = key.replace('maple_', '').replace('_', ' ').title()
            icone = "🔌"
            is_desconectado = False
            
            if "keyboard" in key.lower(): 
                icone = "⌨️"
            elif "mouse" in key.lower(): 
                icone = "🖱️"
            elif "joystick" in key.lower() or "xinput" in key.lower():
                icone = "🎮"
                match = re.search(r'\d+', key)
                if match:
                    idx = int(match.group())
                    if idx >= joysticks_conectados:
                        is_desconectado = True
                        
            cor_texto = "gray" if is_desconectado else "white"
            texto_exibicao = f"{nome_formatado} (Desconectado)" if is_desconectado else nome_formatado

            f = ctk.CTkFrame(self.frame_fisicos_list, fg_color="transparent")
            f.pack(fill="x", pady=2)
            
            lbl_icon = ctk.CTkLabel(f, text=icone, width=25)
            lbl_icon.pack(side="left", padx=(10, 0))
            
            lbl = ctk.CTkLabel(f, text=texto_exibicao, width=220, anchor="w", font=ctk.CTkFont(weight="bold"), text_color=cor_texto)
            lbl.pack(side="left", padx=5)
            
            cb = ctk.CTkComboBox(f, values=["Porta A", "Porta B", "Porta C", "Porta D", "Nenhum"], width=100, state="readonly", command=self.salvar_dispositivos)
            cb.pack(side="right", padx=10)
            
            porta_nome = self.mapa_portas_fisicas.get(val, "Nenhum")
            cb.set(porta_nome)
            
            self.combos_fisicos[key] = cb

    def atualizar_ui_slots(self, porta, valor):
        sem_slots = ["Controle Marcas", "Teclado", "Mouse", "Nenhum", "Controle Densha de Go", "Controle de música Pop'n", "Controle de Pesca", "Controlador DreamParaPara"]
        um_slot = ["Controle de Alavanca Dupla", "Controle de Corrida"]
        
        cb_s1 = self.combos_devices.get(f"{porta}_s1")
        cb_s2 = self.combos_devices.get(f"{porta}_s2")
        btn_color = self.btn_color_pickers.get(porta)
        
        if not cb_s1 or not cb_s2: return
        
        cb_s1.configure(state="readonly")
        cb_s2.grid()
        cb_s2.configure(state="readonly")
        if btn_color: btn_color.grid_remove()
        
        if valor in sem_slots:
            cb_s1.set("Nenhum")
            cb_s1.configure(state="disabled")
            cb_s2.set("Nenhum")
            cb_s2.configure(state="disabled")
        elif valor in um_slot:
            cb_s2.set("Nenhum")
            cb_s2.configure(state="disabled")
        elif valor == "Pistola de Luz":
            cb_s2.grid_remove()
            if btn_color: btn_color.grid()

    def ao_trocar_controle_main(self, porta, valor):
        self.atualizar_ui_slots(porta, valor)
        self.salvar_dispositivos()

    def escolher_cor_mira(self, porta):
        cor = colorchooser.askcolor(title=f"Cor da Mira - Porta {porta}")
        if cor[1]: 
            r, g, b = int(cor[1][1:3], 16), int(cor[1][3:5], 16), int(cor[1][5:7], 16)
            argb = (255 << 24) | (r << 16) | (g << 8) | b 
            self.cores_mira[porta] = str(argb)
            self.btn_color_pickers[porta].configure(fg_color=cor[1])
            self.salvar_dispositivos()

    def carregar_dispositivos(self):
        cfg_path = next((p for p in [os.path.join(self.app.entry_path.get(), "emu.cfg"), os.path.join(self.app.entry_path.get(), "data", "emu.cfg")] if os.path.exists(p)), "")

        if cfg_path:
            config = configparser.RawConfigParser(strict=False)
            config.optionxform = str
            config.read(cfg_path, encoding='utf-8')

            if config.has_section('input'):
                for porta, idx in [("A", 1), ("B", 2), ("C", 3), ("D", 4)]:
                    val_main = config.get('input', f'device{idx}', fallback='3')
                    val_s1 = config.get('input', f'device{idx}.1', fallback='0')
                    val_s2 = config.get('input', f'device{idx}.2', fallback='0')

                    nome_main = self.rev_mapa_controles.get(val_main, "Nenhum")
                    nome_s1 = self.rev_mapa_acessorios.get(val_s1, "Nenhum")
                    nome_s2 = self.rev_mapa_acessorios.get(val_s2, "Nenhum")

                    if f"{porta}_main" in self.combos_devices:
                        self.combos_devices[f"{porta}_main"].set(nome_main)
                        self.combos_devices[f"{porta}_s1"].set(nome_s1)
                        self.combos_devices[f"{porta}_s2"].set(nome_s2)
                        self.atualizar_ui_slots(porta, nome_main)

            if config.has_section('rend') and hasattr(self, 'cores_mira'):
                for porta, idx in [("A", 1), ("B", 2), ("C", 3), ("D", 4)]:
                    cor_int = config.get('rend', f'CrossHairColor{idx}', fallback='0')
                    self.cores_mira[porta] = cor_int
                    try:
                        c = int(cor_int)
                        if c != 0:
                            r = (c >> 16) & 255
                            g = (c >> 8) & 255
                            b = c & 255
                            self.btn_color_pickers[porta].configure(fg_color=f"#{r:02x}{g:02x}{b:02x}") 
                    except: pass
                            
        self.atualizar_lista_fisicos()
        self.app.log("🔌 Hardware: Acessórios virtuais e periféricos físicos sincronizados com sucesso.")

    def salvar_dispositivos(self, *args, force=False):
        install_path = self.app.entry_path.get()
        cfg_path = os.path.join(install_path, "emu.cfg")
        if not os.path.exists(cfg_path): cfg_path = os.path.join(install_path, "data", "emu.cfg")
        if not os.path.exists(cfg_path): cfg_path = os.path.join(install_path, "emu.cfg")

        config = configparser.RawConfigParser(strict=False)
        config.optionxform = str
        if os.path.exists(cfg_path):
            try: config.read(cfg_path, encoding='utf-8')
            except Exception: pass

        if not config.has_section('input'): config.add_section('input')

        for porta, idx in [("A", 1), ("B", 2), ("C", 3), ("D", 4)]:
            val_main_str = self.combos_devices[f"{porta}_main"].get() or "Nenhum"
            val_s1_str = self.combos_devices[f"{porta}_s1"].get() or "Nenhum"
            val_s2_str = self.combos_devices[f"{porta}_s2"].get() or "Nenhum"

            val_main = self.mapa_controles.get(val_main_str, "3")
            val_s1 = self.mapa_acessorios.get(val_s1_str, "0")
            val_s2 = self.mapa_acessorios.get(val_s2_str, "0")

            config.set('input', f'device{idx}', val_main)
            config.set('input', f'device{idx}.1', val_s1)
            config.set('input', f'device{idx}.2', val_s2)

        if hasattr(self, 'combos_fisicos'):
            for key, cb in self.combos_fisicos.items():
                porta_str = cb.get()
                if porta_str == "Nenhum":
                    if config.has_option('input', key): config.remove_option('input', key)
                else:
                    val_porta = self.rev_mapa_portas_fisicas.get(porta_str, "0")
                    config.set('input', key, val_porta)

        if hasattr(self, 'cores_mira'):
            if not config.has_section('rend'): config.add_section('rend')
            for porta, idx in [("A", 1), ("B", 2), ("C", 3), ("D", 4)]:
                config.set('rend', f'CrossHairColor{idx}', str(self.cores_mira[porta]))

        try:
            with open(cfg_path, 'w', encoding='utf-8') as f: config.write(f, space_around_delimiters=True)
            if args and not force:
                self.app.log("🔌 Hardware: Cabos reconectados e gravados com sucesso.")
                self.app.mostrar_toast("Hardware Atualizado", "Periféricos mapeados com sucesso!", "success")
        except Exception as e:
            self.app.log(f"❌ Erro de Hardware: {e}")

    def checar_firmware_8bitdo(self):
        import webbrowser
        self.app.log("🎮 Redirecionando para a central de Firmwares da 8BitDo...")
        url_suporte = "https://support.8bitdo.com/firmware-updater.html"
        webbrowser.open(url_suporte)
        
        msg = (
            "Para garantir a menor latência e a melhor compatibilidade dos seus controles 8BitDo, "
            "é recomendado rodar o 'Upgrade Tool' periodicamente.\n\n"
            "O site oficial foi aberto no seu navegador!"
        )
        mb.showinfo("Atualização de Hardware", msg, parent=self.app)