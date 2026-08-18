import os
import zipfile

# Banco de dados nativo de ROMs de Arcade conhecidas com assinatura de arquivos internos cruciais
ARCADE_DB = {
    "atomiswave": {
        "bios": "awbios.zip",
        "jogos": {
            "kofxi.zip": {"titulo": "The King of Fighters XI", "arquivos_criticos": ["b01a", "ic1.u1"]},
            "ngbc.zip": {"titulo": "NeoGeo Battle Coliseum", "arquivos_criticos": ["b01a", "ic1.u1"]},
            "samsho6.zip": {"titulo": "Samurai Shodown VI", "arquivos_criticos": ["ic1"]},
            "mslug6.zip": {"titulo": "Metal Slug 6", "arquivos_criticos": ["aw_mslug6_slot"]},
            "fotns.zip": {"titulo": "Fist of the North Star", "arquivos_criticos": ["ic1.u1"]},
            "ggisuka.zip": {"titulo": "Guilty Gear Isuka", "arquivos_criticos": ["ic1.u1"]},
            "dolphin.zip": {"titulo": "Dolphin Blue", "arquivos_criticos": ["ic1.u1"]},
            "rumblef.zip": {"titulo": "The Rumble Fish", "arquivos_criticos": ["ic1"]},
            "rumblef2.zip": {"titulo": "The Rumble Fish 2", "arquivos_criticos": ["ic1"]},
            "demofist.zip": {"titulo": "Demolish Fist", "arquivos_criticos": ["ic1.u1"]},
            "kovseven.zip": {"titulo": "Knights of Valour: The Seven Spirits", "arquivos_criticos": ["ic1.u1"]},
            "xtrmhunt.zip": {"titulo": "Extreme Hunting", "arquivos_criticos": ["ic1"]}
        }
    },
    "naomi": {
        "bios": "naomi.zip",
        "jogos": {
            "mvsc2.zip": {"titulo": "Marvel vs. Capcom 2", "arquivos_criticos": ["epr-23062.ic1", "mpr-23061.ic2"]},
            "cvs2.zip": {"titulo": "Capcom vs. SNK 2", "arquivos_criticos": ["epr-23910.ic1"]},
            "doa2.zip": {"titulo": "Dead or Alive 2", "arquivos_criticos": ["epr-22564.ic1"]},
            "crazytaxi.zip": {"titulo": "Crazy Taxi", "arquivos_criticos": ["epr-22786.ic1"]},
            "ikaruga.zip": {"titulo": "Ikaruga", "arquivos_criticos": ["epr-24202.ic1"]},
            "slashout.zip": {"titulo": "Slashout", "arquivos_criticos": ["epr-23398.ic1"]},
            "pstone.zip": {"titulo": "Power Stone", "arquivos_criticos": ["epr-21918.ic1"]},
            "pstone2.zip": {"titulo": "Power Stone 2", "arquivos_criticos": ["epr-23011.ic1"]},
            "vt2.zip": {"titulo": "Virtua Tennis 2", "arquivos_criticos": ["epr-23916.ic1"]},
            "zombrvn.zip": {"titulo": "Zombie Revenge", "arquivos_criticos": ["epr-22154a.ic1"]},
            "capsnk.zip": {"titulo": "Capcom vs. SNK", "arquivos_criticos": ["epr-23214.ic1"]},
            "ggxx.zip": {"titulo": "Guilty Gear XX", "arquivos_criticos": ["epr-24250.ic1"]},
            "ggxxrl.zip": {"titulo": "Guilty Gear XX #Reload", "arquivos_criticos": ["epr-25219.ic1"]},
            "spikers.zip": {"titulo": "SpikeOut", "arquivos_criticos": ["epr-21727.ic1"]},
            "totd.zip": {"titulo": "The Typing of the Dead", "arquivos_criticos": ["epr-22924.ic1"]},
            "hotd2.zip": {"titulo": "The House of the Dead 2", "arquivos_criticos": ["epr-21845c.ic1"]}
        }
    },
    "naomi2": {
        "bios": "naomi2.zip",
        "jogos": {
            "vf4.zip": {"titulo": "Virtua Fighter 4", "arquivos_criticos": ["epr-23984.ic1"]},
            "vf4evo.zip": {"titulo": "Virtua Fighter 4 Evolution", "arquivos_criticos": ["epr-25171.ic1"]},
            "vf4tuned.zip": {"titulo": "Virtua Fighter 4 Final Tuned", "arquivos_criticos": ["epr-26038.ic1"]},
            "initd.zip": {"titulo": "Initial D Arcade Stage", "arquivos_criticos": ["epr-25091.ic1"]},
            "beachspi.zip": {"titulo": "Beach Spikers", "arquivos_criticos": ["epr-24754.ic1"]},
            "clubk2k3.zip": {"titulo": "Club Kart", "arquivos_criticos": ["epr-25010.ic1"]}
        }
    }
}

class ArcadeManager:
    def __init__(self, app):
        self.app = app
        self.roms_conhecidas = {}
        for sistema, dados in ARCADE_DB.items():
            for rom_name, jogo_data in dados["jogos"].items():
                self.roms_conhecidas[rom_name.lower()] = {
                    "sistema": sistema,
                    "titulo": jogo_data["titulo"],
                    "bios_requirida": dados["bios"],
                    "arquivos_criticos": jogo_data["arquivos_criticos"]
                }

    def is_arcade_rom(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in [".zip", ".7z"]:
            return False
        return filename.lower() in self.roms_conhecidas

    def obter_info_rom(self, filename):
        return self.roms_conhecidas.get(filename.lower())

    def validar_bios_para_rom(self, rom_filename, install_path, custom_bios_path=None):
        info = self.obter_info_rom(rom_filename)
        if not info:
            return True, "Não catalogado como arcade."
        
        bios_requirida = info["bios_requirida"]
        sistema_nome = info["sistema"].capitalize()
        
        pasta_alvo = custom_bios_path if custom_bios_path else os.path.join(install_path, "data")
        caminho_bios = os.path.join(pasta_alvo, bios_requirida)
        
        if not os.path.exists(caminho_bios):
            erro_msg = (
                f"Você está tentando iniciar um jogo de {sistema_nome} ({info['titulo']}), "
                f"mas a BIOS obrigatória '{bios_requirida}' não foi encontrada!\n\n"
                f"Instale o arquivo correspondente na pasta:\n{pasta_alvo}"
            )
            return False, erro_msg
            
        return True, f"BIOS {bios_requirida} encontrada."

    def verificar_integridade_rom(self, caminho_completo_rom):
        """
        🛡️ MAME DAT Integrity Check
        Abre o arquivo .zip da ROM e checa se os sub-arquivos cruciais estão lá dentro.
        Nota: Suporte nativo completo para .zip. Para .7z, passa direto com aviso.
        """
        filename = os.path.basename(caminho_completo_rom)
        info = self.obter_info_rom(filename)
        if not info:
            return True, "OK"

        if caminho_completo_rom.lower().endswith(".7z"):
            return True, "7z detectado (Ignorando checagem profunda de sub-arquivos)."

        if not os.path.exists(caminho_completo_rom):
            return False, "Arquivo da ROM fisicamente ausente no disco."

        try:
            with zipfile.ZipFile(caminho_completo_rom, 'r') as z:
                lista_arquivos_internos = [os.path.basename(name).lower() for name in z.namelist()]
                
                arquivos_ausentes = []
                for critico in info["arquivos_criticos"]:
                    if critico.lower() not in lista_arquivos_internos:
                        arquivos_ausentes.append(critico)
                
                if arquivos_ausentes:
                    msg_erro = (
                        f"O arquivo '{filename}' está corrompido ou incompleto para o padrão MAME/Flycast!\n\n"
                        f"Detectamos que faltam as seguintes sub-roms cruciais dentro do arquivo compactado:\n"
                        f"- " + "\n- ".join(arquivos_ausentes) + "\n\n"
                        f"Consiga um Romset mais recente e atualizado deste jogo para evitar falhas."
                    )
                    return False, msg_erro
        except zipfile.BadZipFile:
            return False, f"O arquivo '{filename}' não é um arquivo ZIP válido ou está completamente corrompido."
        except Exception as e:
            return False, f"Erro ao ler integridade da ROM: {e}"

        return True, "OK"