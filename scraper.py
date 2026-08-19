import os
import re
import threading
import urllib.request
import urllib.parse

class AutoScraper:
    def __init__(self, app_instance=None):
        self.app = app_instance
        self.base_url_img = "https://raw.githubusercontent.com/libretro-thumbnails/libretro-thumbnails/master/Sega%20-%20Dreamcast"
        
    def limpar_nome_jogo(self, filename):
        nome = os.path.splitext(filename)[0]
        nome_limpo = re.sub(r'\(.*?\)|\[.*?\]', '', nome).strip()
        return nome_limpo if nome_limpo else nome

    def baixar_arte(self, nome_exato, install_path, tipo="Named_Boxarts"):
        if tipo == "Named_Boxarts": pasta_destino = os.path.join(install_path, "data", "boxart")
        elif tipo == "Named_Titles": pasta_destino = os.path.join(install_path, "data", "logos")
        elif tipo == "Named_Snaps": pasta_destino = os.path.join(install_path, "data", "snaps")
        else: pasta_destino = os.path.join(install_path, "data", tipo.split('_')[1].lower())
            
        os.makedirs(pasta_destino, exist_ok=True)
        arquivo_destino = os.path.join(pasta_destino, f"{nome_exato}.png")
        
        if os.path.exists(arquivo_destino): return arquivo_destino 
            
        nome_seguro = re.sub(r'[&*/:`<>?\|]', '_', nome_exato)
        url = f"{self.base_url_img}/{tipo}/{urllib.parse.quote(nome_seguro)}.png"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response, open(arquivo_destino, 'wb') as out_file:
                out_file.write(response.read())
            return arquivo_destino
        except: return None 

    def processar_rom_background(self, install_path, filename, nome_xml=None, callback_ui=None):
        def rotina():
            nome_exato = os.path.splitext(filename)[0]
            nome_limpo = self.limpar_nome_jogo(filename)
            
            # A MÁGICA: O Scraper tenta o nome do XML primeiro (A chave-mestra do Libretro!)
            nomes_para_testar = [nome_xml, nome_exato, nome_limpo] if nome_xml else [nome_exato, nome_limpo]
            
            atualizou_algo = False
            for tipo in ["Named_Boxarts", "Named_Titles", "Named_Snaps"]:
                for n in nomes_para_testar:
                    if not n: continue
                    if self.baixar_arte(n, install_path, tipo):
                        atualizou_algo = True
                        if self.app and tipo == "Named_Boxarts": self.app.log(f"🖼️ Scraper: Arte baixada usando a chave '{n}'")
                        break # Se achou a arte para este tipo, vai para o próximo (Logo, Snap...)

            if atualizou_algo and callback_ui: callback_ui()

        threading.Thread(target=rotina, daemon=True).start()