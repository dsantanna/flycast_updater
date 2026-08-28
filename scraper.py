import os
import re
import threading
import urllib.request
import urllib.parse
import concurrent.futures

class AutoScraper:
    def __init__(self, app_instance=None):
        self.app = app_instance
        # 🔗 A MÁGICA: URL Oficial do RetroArch (CDN Cloudflare)
        # Muito mais rápida, não dá erro 429 e NUNCA sai do ar!
        self.base_url_img = "https://thumbnails.libretro.com/Sega%20-%20Dreamcast"
        
    def limpar_nome_jogo(self, filename):
        nome = os.path.splitext(filename)[0]
        # Remove parênteses e colchetes e limpa os espaços
        nome_limpo = re.sub(r'\(.*?\)|\[.*?\]', '', nome).strip()
        return nome_limpo if nome_limpo else nome

    def baixar_arte(self, nome_busca, install_path, tipo="Named_Boxarts", nome_salvar=None):
        # Se não informou nome de salvamento, usa o próprio nome da busca
        if not nome_salvar: nome_salvar = nome_busca
        
        if tipo == "Named_Boxarts": pasta_destino = os.path.join(install_path, "data", "boxart")
        elif tipo == "Named_Titles": pasta_destino = os.path.join(install_path, "data", "logos")
        elif tipo == "Named_Snaps": pasta_destino = os.path.join(install_path, "media", "snaps")
        else: pasta_destino = os.path.join(install_path, "data", tipo.split('_')[1].lower())
            
        os.makedirs(pasta_destino, exist_ok=True)
        arquivo_destino = os.path.join(pasta_destino, f"{nome_salvar}.png")
        
        # Se a arte já está na pasta do usuário, ele ignora para não gastar banda
        if os.path.exists(arquivo_destino): return "existe"
            
        # O Libretro oficial substitui esses caracteres especiais por '_'
        nome_seguro = re.sub(r'[&*/:`<>?\|]', '_', nome_busca)
        url = f"{self.base_url_img}/{tipo}/{urllib.parse.quote(nome_seguro)}.png"
        
        try:
            # Usamos o User-Agent do próprio RetroArch para passar liso pela segurança
            req = urllib.request.Request(url, headers={'User-Agent': 'RetroArch/1.19.0 (Windows)'})
            with urllib.request.urlopen(req, timeout=5) as response, open(arquivo_destino, 'wb') as out_file:
                out_file.write(response.read())
            return True 
        except Exception: 
            return False

    def varredura_em_massa(self, install_path, dicionario_jogos, callback_progresso=None, callback_fim=None):
        def rotina():
            if self.app: self.app.log("🌐 Scraper: Iniciando conexão segura com CDN do Libretro...")
            
            total = len(dicionario_jogos)
            processados = 0
            sucessos = 0
            
            # Como estamos na nuvem oficial, podemos aumentar a tropa para 6 operários simultâneos!
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                futuros = []
                for nome_xml, arquivos in dicionario_jogos.items():
                    if not arquivos: continue
                    filename = os.path.basename(arquivos[0])
                    futuros.append(executor.submit(self._varredura_individual, install_path, filename, nome_xml))
                
                for futuro in concurrent.futures.as_completed(futuros):
                    processados += 1
                    if futuro.result(): sucessos += 1
                    
                    if callback_progresso and self.app:
                        self.app.after(0, lambda p=processados, t=total: callback_progresso(p, t))
                        
            if self.app: self.app.log(f"✅ Scraper: Operação concluída. {sucessos} novos jogos receberam artes!")
            
            if callback_fim and self.app:
                self.app.after(0, lambda s=sucessos: callback_fim(s))

        threading.Thread(target=rotina, daemon=True).start()

    def processar_rom_background(self, install_path, filename, nome_xml=None, callback_ui=None):
        """Função clássica, caso você adicione um jogo por vez."""
        def rotina():
            baixou = self._varredura_individual(install_path, filename, nome_xml)
            if baixou and callback_ui and self.app: 
                self.app.after(0, callback_ui)
        threading.Thread(target=rotina, daemon=True).start()

    def _varredura_individual(self, install_path, filename, nome_xml):
        nome_exato = os.path.splitext(filename)[0]
        nome_limpo = self.limpar_nome_jogo(filename)
        
        nomes_para_testar = []
        if nome_xml: nomes_para_testar.append(nome_xml)
        nomes_para_testar.extend([nome_exato, nome_limpo])
        
        if nome_limpo:
            # 💡 INTELIGÊNCIA TÁTICA: O Pente Fino das Regiões do No-Intro!
            nomes_para_testar.extend([
                f"{nome_limpo} (USA)",
                f"{nome_limpo} (Europe)",
                f"{nome_limpo} (Japan)",
                f"{nome_limpo} (World)",
                nome_limpo.replace(" - ", " "),
                nome_limpo.replace(" ", " - ")
            ])
            
            # Gambiarra Mestra 1: Nomes colados ("SoulCalibur" vira "Soul Calibur")
            espacado = re.sub(r"(\w)([A-Z])", r"\1 \2", nome_limpo)
            if espacado != nome_limpo:
                nomes_para_testar.extend([espacado, f"{espacado} (USA)", f"{espacado} (Europe)", f"{espacado} (Japan)"])

            # Gambiarra Mestra 2: Code Veronica usa dois traços ("Resident Evil - Code - Veronica")
            if "Code" in nome_limpo and "Veronica" in nome_limpo:
                nomes_para_testar.extend([
                    "Resident Evil - Code - Veronica (USA)",
                    "Resident Evil - Code - Veronica (USA) (Disc 1)",
                    "Resident Evil - Code - Veronica (Europe)"
                ])
            
        # Limpa nomes duplicados na lista para o robô não procurar a mesma coisa duas vezes
        nomes_para_testar = list(dict.fromkeys(nomes_para_testar))
        
        baixou_algo = False
        # for tipo in ["Named_Boxarts", "Named_Titles", "Named_Snaps"]:
        for tipo in ["Named_Boxarts", "Named_Titles"]:
            for nome_busca in nomes_para_testar:
                if not nome_busca: continue
                # O TRUQUE: Engana o servidor buscando as variações de nomes,
                # MAS salva a imagem usando sempre o nome EXATO do seu arquivo original (nome_exato).
                status = self.baixar_arte(nome_busca, install_path, tipo, nome_salvar=nome_exato)
                if status == True:
                    baixou_algo = True
                    break  # Achou a arte para este tipo, para a busca de nomes e vai pro próximo tipo.
                elif status == "existe":
                    break  # Já tem a imagem salva localmente, pula a busca.
        return baixou_algo