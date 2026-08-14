import os
import sys
import json
import xml.etree.ElementTree as ET
import re
import urllib.request
import urllib.parse

def traduzir_texto(texto, idioma_destino="pt"):
    if not texto or len(texto) < 5: return texto
    try:
        # Motor de tradução silencioso via API pública do Google
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={idioma_destino}&dt=t&q={urllib.parse.quote(texto)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            resultado = json.loads(response.read().decode('utf-8'))
            texto_traduzido = "".join([frase[0] for frase in resultado[0] if frase[0]])
            return texto_traduzido
    except Exception:
        # Se estiver offline ou a API falhar, devolve o texto original
        return texto

def simplificar(texto):
    return re.sub(r'[^a-z0-9]', '', str(texto).lower())

def gerar_estrelas(nota_str):
    try:
        nota = float(nota_str)
        cheias = int(round(nota))
        if cheias > 5: cheias = 5
        if cheias < 0: cheias = 0
        vazias = 5 - cheias
        return f"{'★' * cheias}{'☆' * vazias} ({nota_str}/5.0)"
    except:
        return ""

# --- ADICIONAMOS O PARÂMETRO 'idioma_app' ---
def buscar_metadados(nome_jogo, rom_path, install_path, idioma_app="pt"):
    dados = {
        "score": "", "manufacturer": "", "rating": "", "player": "", "story": ""
    }
    
    try: base_embutida = sys._MEIPASS
    except Exception: base_embutida = os.path.dirname(os.path.abspath(__file__))
    
    s_jogo = simplificar(nome_jogo)
    rom_basename = os.path.splitext(os.path.basename(rom_path))[0] if rom_path else ""
    s_rom = simplificar(rom_basename) if rom_basename else ""
    
    nomes_xml = ["DC-game.xml", "DC-gamedb.xml"]
    xml_encontrado = None
    
    for nome_arquivo in nomes_xml:
        xml_paths = [
            os.path.join(install_path, nome_arquivo), 
            os.path.join(base_embutida, nome_arquivo), 
            os.path.join(os.getcwd(), nome_arquivo), 
            os.path.join(os.getcwd(), "..", nome_arquivo) 
        ]
        for xp in xml_paths:
            if os.path.exists(xp):
                xml_encontrado = xp
                break
        if xml_encontrado: break
            
    if xml_encontrado:
        try:
            tree = ET.parse(xml_encontrado)
            root = tree.getroot()
            match_node = None
            
            for game in root.findall('game'):
                g_name = game.get('name', '')
                s_gname = simplificar(g_name)
                if s_jogo == s_gname or (s_rom and s_rom == s_gname):
                    match_node = game
                    break
                    
            if not match_node:
                for game in root.findall('game'):
                    g_name = game.get('name', '')
                    s_gname = simplificar(g_name)
                    if (len(s_jogo) > 3 and (s_jogo in s_gname or s_gname in s_jogo)) or \
                       (s_rom and len(s_rom) > 3 and (s_rom in s_gname or s_gname in s_rom)):
                        match_node = game
                        break
                        
            if match_node is not None:
                n_score = match_node.find('score')
                if n_score is not None and n_score.text: dados["score"] = n_score.text
                
                n_manuf = match_node.find('manufacturer')
                if n_manuf is not None and n_manuf.text: dados["manufacturer"] = n_manuf.text
                
                n_rating = match_node.find('rating')
                if n_rating is not None and n_rating.text: dados["rating"] = n_rating.text
                
                n_player = match_node.find('player')
                if n_player is not None and n_player.text: dados["player"] = n_player.text
                
                n_story = match_node.find('story')
                if n_story is not None and n_story.text: dados["story"] = n_story.text
        except: pass

    if not dados["story"]:
        db_paths = [
            os.path.join(install_path, "data", "flycast-gamedb.json"),
            os.path.join(install_path, "data", "boxart", "flycast-gamedb.json"),
            os.path.join(install_path, "flycast-gamedb.json")
        ]
        sinopse_parcial = None
        for db_path in db_paths:
            if os.path.exists(db_path):
                try:
                    with open(db_path, "r", encoding="utf-8") as f:
                        db_data = json.load(f)
                    lista_db = db_data if isinstance(db_data, list) else db_data.values()
                    for info in lista_db:
                        if isinstance(info, dict):
                            db_name = simplificar(info.get("name", info.get("title", "")))
                            db_file = simplificar(info.get("file_name", info.get("fileName", "")))
                            
                            if s_jogo == db_name or (s_rom and s_rom == db_file):
                                overview = info.get("overview", "")
                                if overview:
                                    dados["story"] = overview
                                    break
                            if not sinopse_parcial:
                                if (len(s_jogo) > 3 and (s_jogo in db_name or s_jogo in db_file)) or \
                                   (len(db_name) > 3 and db_name in s_jogo) or \
                                   (s_rom and len(s_rom) > 3 and s_rom in db_file):
                                    overview = info.get("overview", "")
                                    if overview: sinopse_parcial = overview
                except: pass
            if dados["story"]: break
            
        if not dados["story"] and sinopse_parcial:
            dados["story"] = sinopse_parcial
            
    if not dados["story"]:
        dados["story"] = "Nenhuma sinopse oficial encontrada no banco de dados."
    else:
        # --- MÁGICA FINAL: TRADUZ PARA O IDIOMA ATUAL DA INTERFACE ---
        # Se a interface não estiver em inglês, ele aciona o tradutor mágico.
        if idioma_app != "en":
            dados["story"] = traduzir_texto(dados["story"], idioma_app)
            
    return dados