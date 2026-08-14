import os
import configparser
import customtkinter as ctk

class DevicesManager:
    def __init__(self, app_instance):
        self.app = app_instance
        
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

                    if hasattr(self.app, 'combos_devices'):
                        self.app.combos_devices[f"{porta}_main"].set(nome_main)
                        self.app.combos_devices[f"{porta}_s1"].set(nome_s1)
                        self.app.combos_devices[f"{porta}_s2"].set(nome_s2)
                        
                        # Ativa o gatilho da interface que acabamos de criar!
                        if hasattr(self.app, 'atualizar_ui_slots'):
                            self.app.atualizar_ui_slots(porta, nome_main)

            # --- LÊ AS CORES DAS MIRAS DA SESSÃO [rend] ---
            if config.has_section('rend') and hasattr(self.app, 'cores_mira'):
                for porta, idx in [("A", 1), ("B", 2), ("C", 3), ("D", 4)]:
                    cor_int = config.get('rend', f'CrossHairColor{idx}', fallback='0')
                    self.app.cores_mira[porta] = cor_int
                    try:
                        c = int(cor_int)
                        if c != 0:
                            r = (c >> 16) & 255
                            g = (c >> 8) & 255
                            b = c & 255
                            # Pinta o botão com a cor salva
                            self.app.btn_color_pickers[porta].configure(fg_color=f"#{r:02x}{g:02x}{b:02x}") 
                    except: pass
                            
        if hasattr(self.app, 'atualizar_lista_fisicos'):
            self.app.atualizar_lista_fisicos()

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
            val_main_str = self.app.combos_devices[f"{porta}_main"].get() or "Nenhum"
            val_s1_str = self.app.combos_devices[f"{porta}_s1"].get() or "Nenhum"
            val_s2_str = self.app.combos_devices[f"{porta}_s2"].get() or "Nenhum"

            val_main = self.mapa_controles.get(val_main_str, "3")
            val_s1 = self.mapa_acessorios.get(val_s1_str, "0")
            val_s2 = self.mapa_acessorios.get(val_s2_str, "0")

            config.set('input', f'device{idx}', val_main)
            config.set('input', f'device{idx}.1', val_s1)
            config.set('input', f'device{idx}.2', val_s2)

        if hasattr(self.app, 'combos_fisicos'):
            for key, cb in self.app.combos_fisicos.items():
                porta_str = cb.get()
                if porta_str == "Nenhum":
                    if config.has_option('input', key): config.remove_option('input', key)
                else:
                    val_porta = self.rev_mapa_portas_fisicas.get(porta_str, "0")
                    config.set('input', key, val_porta)

        # --- SALVA AS CORES DAS MIRAS ---
        if hasattr(self.app, 'cores_mira'):
            if not config.has_section('rend'): config.add_section('rend')
            for porta, idx in [("A", 1), ("B", 2), ("C", 3), ("D", 4)]:
                config.set('rend', f'CrossHairColor{idx}', str(self.app.cores_mira[porta]))

        try:
            with open(cfg_path, 'w', encoding='utf-8') as f: config.write(f, space_around_delimiters=True)
            if args and not force:
                self.app.log("🔌 Hardware: Cabos reconectados e gravados com sucesso.")
                self.app.mostrar_toast("Hardware Atualizado", "Periféricos mapeados com sucesso!", "success")
        except Exception as e:
            self.app.log(f"❌ Erro de Hardware: {e}")