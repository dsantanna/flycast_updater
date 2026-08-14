import os
import socket
import configparser
import customtkinter as ctk
import tkinter.messagebox as mb

class NetplayManager(ctk.CTkToplevel):
    def __init__(self, master, nome_jogo, rom_path, install_path, game_manager):
        super().__init__(master)
        self.title(f"🌐 Netplay - {nome_jogo}")
        self.geometry("500x520")
        self.attributes("-topmost", True)
        self.grab_set()

        self.nome_jogo = nome_jogo
        self.rom_path = rom_path
        self.install_path = install_path
        self.game_manager = game_manager

        # Caça o IP Local para facilitar a vida do Host
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.meu_ip = s.getsockname()[0]
            s.close()
        except:
            self.meu_ip = "Desconhecido"

        self.construir_ui()

    def construir_ui(self):
        lbl_title = ctk.CTkLabel(self, text="Multiplayer Online (Flycast Netplay)", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_title.pack(pady=(15, 5))

        self.tabview = ctk.CTkTabview(self, height=270)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=5)

        self.tab_host = self.tabview.add("🏠 Criar Sala (Host)")
        self.tab_join = self.tabview.add("🔗 Entrar (Join)")

        # --- ABA HOST ---
        lbl_host_desc = ctk.CTkLabel(self.tab_host, text="Seja o Host da partida.\nSeu amigo deve se conectar ao seu IP.", justify="center")
        lbl_host_desc.pack(pady=10)

        frame_ip = ctk.CTkFrame(self.tab_host, fg_color="#1a1a2e", corner_radius=8)
        frame_ip.pack(fill="x", padx=20, pady=10)

        lbl_ip_title = ctk.CTkLabel(frame_ip, text="Seu IP Local:", font=ctk.CTkFont(weight="bold", size=12))
        lbl_ip_title.pack(pady=(10, 0))

        lbl_ip_val = ctk.CTkLabel(frame_ip, text=self.meu_ip, font=ctk.CTkFont(weight="bold", size=24), text_color="#00FF7F")
        lbl_ip_val.pack(pady=(0, 10))

        lbl_rede = ctk.CTkLabel(self.tab_host, text="Dica: Para jogar pela internet, use VPNs como Radmin ou ZeroTier.", text_color="gray", font=ctk.CTkFont(size=11))
        lbl_rede.pack(pady=5)

        btn_host = ctk.CTkButton(self.tab_host, text="🏠 Iniciar como Host", height=35, fg_color="#228B22", hover_color="#006400", font=ctk.CTkFont(weight="bold"), command=self.host_game)
        btn_host.pack(pady=(10, 10))

        # --- ABA JOIN ---
        lbl_join_desc = ctk.CTkLabel(self.tab_join, text="Entre na partida de um amigo\ndigitando o IP dele abaixo.", justify="center")
        lbl_join_desc.pack(pady=10)

        self.entry_ip = ctk.CTkEntry(self.tab_join, placeholder_text="Ex: 192.168.0.15 ou IP do Radmin", width=280, height=35, justify="center")
        self.entry_ip.pack(pady=15)

        btn_join = ctk.CTkButton(self.tab_join, text="🔗 Conectar ao Host", height=35, fg_color="#1E90FF", hover_color="#4169E1", font=ctk.CTkFont(weight="bold"), command=self.join_game)
        btn_join.pack(pady=(25, 10))

        # --- OPÇÕES GERAIS ---
        self.frame_opts = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.frame_opts.pack(fill="x", padx=20, pady=(0, 15))

        self.switch_ggpo = ctk.CTkSwitch(self.frame_opts, text="Ativar GGPO (Rollback Netcode) - Ideal para Luta!")
        self.switch_ggpo.pack(pady=15)
        self.switch_ggpo.select() # Já vem ligado porque Rollback é Vida!

    def configurar_emu_netplay(self, is_host, ip_host=""):
        cfg_path = os.path.join(self.install_path, "emu.cfg")
        if not os.path.exists(cfg_path):
            cfg_path = os.path.join(self.install_path, "data", "emu.cfg")

        config = configparser.RawConfigParser(strict=False)
        config.optionxform = str
        if os.path.exists(cfg_path):
            config.read(cfg_path, encoding='utf-8')

        if not config.has_section('network'):
            config.add_section('network')

        # Injeta as regras do Netplay
        config.set('network', 'Enable', 'yes')
        config.set('network', 'ActAsServer', 'yes' if is_host else 'no')
        config.set('network', 'server', ip_host if not is_host else '')
        config.set('network', 'LocalPort', '37391')
        config.set('network', 'GGPO', 'yes' if self.switch_ggpo.get() == 1 else 'no')
        config.set('network', 'GGPODelay', '0')

        with open(cfg_path, 'w', encoding='utf-8') as f:
            config.write(f, space_around_delimiters=True)

    def lancar_netplay(self):
        # Fecha a janela de info e do Netplay para não poluir a tela
        if isinstance(self.master, ctk.CTkToplevel):
            self.master.destroy()
        self.destroy()
        # Chama a ROM avisando ao Launcher que isso É uma partida Online!
        self.game_manager.lancar_jogo(self.rom_path, self.nome_jogo, is_netplay=True)

    def host_game(self):
        self.configurar_emu_netplay(is_host=True)
        self.lancar_netplay()

    def join_game(self):
        ip = self.entry_ip.get().strip()
        if not ip:
            mb.showerror("Erro", "Você precisa digitar o IP do Host para conectar!", parent=self)
            return
        self.configurar_emu_netplay(is_host=False, ip_host=ip)
        self.lancar_netplay()