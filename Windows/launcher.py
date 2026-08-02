import ctypes
import sys

def is_portuguese():
    """
    Comunica-se com a API do Windows para descobrir o idioma da interface.
    O código 0x16 (22 em decimal) representa a família da língua Portuguesa 
    (englobando pt-BR, pt-PT, etc).
    """
    try:
        # Puxa o ID do idioma padrão do usuário no Windows
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        # Filtra apenas o identificador principal do idioma, ignorando o dialeto/região
        primary_lang_id = lang_id & 0x03FF
        return primary_lang_id == 0x16
    except Exception:
        # Em caso de falha de leitura, assume Inglês como fallback de segurança
        return False

if __name__ == "__main__":
    # Como o import carrega as variáveis globais, nós o colocamos DENTRO do if.
    # Assim, apenas a versão correta do script é lida e executada.
    if is_portuguese():
        import Windows.update_flycast as update_flycast
        update_flycast.main()
    else:
        import Windows.flycast_update_en_us as flycast_update_en_us
        flycast_update_en_us.main()