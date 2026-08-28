import os
import configparser
import tkinter.messagebox as mb
import customtkinter as ctk

class AudioSettingsManager(ctk.CTkToplevel):
    def __init__(self, master, install_path):
        super().__init__(master)
        self.app = master
        self.install_path = install_path
        self.cfg_path = os.path.join(self.install_path, "emu.cfg")
        
        self.title("🔊 Engenharia de Áudio")
        self.geometry("450x420")
        self.attributes("-topmost", True)
        self.grab_set()

        # Variáveis de Controle
        self.val_dsp = ctk.BooleanVar(value=True)
        self.val_volume = ctk.IntVar(value=100)
        self.val_latency = ctk.IntVar(value=64)
        self.val_backend = ctk.StringVar(value="auto")

        self.ler_configuracoes_nativas()
        self.construir_interface()

    def ler_configuracoes_nativas(self):
        """Faz a extração cirúrgica direto do emu.cfg"""
        if not os.path.exists(self.cfg_path):
            return
            
        config = configparser.RawConfigParser(strict=False)
        config.optionxform = str
        config.read(self.cfg_path, encoding='utf-8')
        
        if config.has_section('audio'):
            self.val_dsp.set(config.get('audio', 'EnableDSP', fallback='yes') == 'yes')
            self.val_volume.set(int(config.get('audio', 'Volume', fallback='100')))
            self.val_latency.set(int(config.get('audio', 'BufferSize', fallback='64')))
            self.val_backend.set(config.get('audio', 'backend', fallback='auto'))

    def construir_interface(self):
        ctk.CTkLabel(self, text="Painel de Controle de Áudio", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E90FF").pack(pady=(15, 10))
        ctk.CTkLabel(self, text="Controle o som nativo do emulador sem abrir o Flycast.", text_color="gray", font=ctk.CTkFont(size=11)).pack(pady=(0, 10))
        
        frame_opts = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=10)
        frame_opts.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # 1. DSP (Processamento Digital)
        sw_dsp = ctk.CTkSwitch(frame_opts, text="Ativar DSP (Melhora fidelidade sonora)", variable=self.val_dsp, font=ctk.CTkFont(weight="bold"), progress_color="#4169E1")
        sw_dsp.pack(anchor="w", padx=20, pady=(20, 15))

        # 2. Volume Global
        frame_vol = ctk.CTkFrame(frame_opts, fg_color="transparent")
        frame_vol.pack(fill="x", padx=20, pady=(5, 5))
        
        self.lbl_vol = ctk.CTkLabel(frame_vol, text=f"Nível de Volume: {self.val_volume.get()}%", font=ctk.CTkFont(weight="bold"))
        self.lbl_vol.pack(anchor="w")
        
        slider_vol = ctk.CTkSlider(frame_opts, from_=0, to=100, variable=self.val_volume, progress_color="#228B22", command=lambda v: self.lbl_vol.configure(text=f"Nível de Volume: {int(v)}%"))
        slider_vol.pack(fill="x", padx=20, pady=(0, 15))

        # 3. Latência (Buffer)
        frame_lat = ctk.CTkFrame(frame_opts, fg_color="transparent")
        frame_lat.pack(fill="x", padx=20, pady=(5, 5))
        
        self.lbl_lat = ctk.CTkLabel(frame_lat, text=f"Latência (Atraso): {self.val_latency.get()} ms", font=ctk.CTkFont(weight="bold"))
        self.lbl_lat.pack(anchor="w")
        
        slider_lat = ctk.CTkSlider(frame_opts, from_=16, to=256, number_of_steps=240, variable=self.val_latency, progress_color="#FF8C00", command=lambda v: self.lbl_lat.configure(text=f"Latência (Atraso): {int(v)} ms"))
        slider_lat.pack(fill="x", padx=20, pady=(0, 15))

        # 4. Controlador de Áudio (Backend)
        frame_backend = ctk.CTkFrame(frame_opts, fg_color="transparent")
        frame_backend.pack(fill="x", padx=20, pady=(5, 20))
        
        ctk.CTkLabel(frame_backend, text="Controlador de Áudio:", font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        # Mapeamento do Dropdown (Exatamente como o emulador usa internamente)
        opcoes_backend = ["auto", "directsound", "sdl2", "null"]
        combo_backend = ctk.CTkComboBox(frame_backend, values=opcoes_backend, variable=self.val_backend, state="readonly", width=140)
        combo_backend.pack(side="right")

        # Botão de Ação
        btn_salvar = ctk.CTkButton(self, text="💾 Injetar no Emulador", font=ctk.CTkFont(weight="bold", size=14), height=40, fg_color="#228B22", hover_color="#006400", command=self.salvar_configuracoes)
        btn_salvar.pack(fill="x", padx=20, pady=(0, 20))

    def salvar_configuracoes(self):
        """Forja o arquivo cfg com as novas regulagens"""
        if not os.path.exists(self.install_path):
            mb.showerror("Erro", "O diretório do emulador não foi encontrado!")
            return
            
        config = configparser.RawConfigParser(strict=False)
        config.optionxform = str
        
        if os.path.exists(self.cfg_path):
            config.read(self.cfg_path, encoding='utf-8')
        
        if not config.has_section('audio'):
            config.add_section('audio')

        # Injeta as variáveis puras no padrão do Flycast
        config.set('audio', 'EnableDSP', 'yes' if self.val_dsp.get() else 'no')
        config.set('audio', 'Volume', str(self.val_volume.get()))
        config.set('audio', 'BufferSize', str(self.val_latency.get()))
        config.set('audio', 'backend', self.val_backend.get())

        try:
            with open(self.cfg_path, 'w', encoding='utf-8') as f:
                config.write(f, space_around_delimiters=True)
                
            if hasattr(self.app, 'mostrar_toast'):
                self.app.mostrar_toast("Áudio Salvo", "Configurações de som gravadas com sucesso!", "success")
                if hasattr(self.app, 'sfx'): self.app.sfx.play("save")
            else:
                mb.showinfo("Sucesso", "Configurações de áudio salvas no emulador!")
            self.destroy()
            
        except Exception as e:
            mb.showerror("Erro Crítico", f"Falha ao reescrever emu.cfg:\n{e}")