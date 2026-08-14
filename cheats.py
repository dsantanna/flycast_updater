import os
import urllib.request
import urllib.parse
import json
import re

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
    
    # Prepara o nome com o ID oficial, limpando caracteres que o Windows não aceita
    destino_id = None
    if game_id:
        safe_id = re.sub(r'[\\/*?:"<>|]', "", game_id).strip()
        destino_id = os.path.join(cheat_dir, f"{safe_id}.cht")
    
    # Se o cheat com o ID já existe, o jogo já está pronto!
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
                
                # Salva Backup de segurança
                with open(destino_rom, 'wb') as out_file:
                    out_file.write(content)
                    
                # MÁGICA: Salva cópia exata para auto-loading do Flycast
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