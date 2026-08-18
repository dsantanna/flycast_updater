import customtkinter as ctk
import webbrowser

def mostrar_janela_sobre(parent, version, repo_url, tradutor):
    win_sobre = ctk.CTkToplevel(parent)
    win_sobre.title(tradutor("btn_help", default="Sobre o Flycast Updater"))
    win_sobre.geometry("620x520")
    win_sobre.attributes("-topmost", True)
    win_sobre.grab_set()

    # Cabeçalho da Janela
    lbl_title = ctk.CTkLabel(win_sobre, text=f"🌀 Flycast Updater - v{version}", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E90FF")
    lbl_title.pack(pady=(20, 5))

    lbl_sub = ctk.CTkLabel(win_sobre, text="Desenvolvido por DaniboySan & Geminix", text_color="gray", font=ctk.CTkFont(size=14))
    lbl_sub.pack(pady=(0, 15))

    # Sistema de Abas interno para organizar os textos longos
    tabview_sobre = ctk.CTkTabview(win_sobre, width=580, height=360)
    tabview_sobre.pack(padx=20, pady=5, fill="both", expand=True)

    tab_info = tabview_sobre.add("ℹ️ Informações")
    tab_licenca = tabview_sobre.add("📜 Licença (GPL v3)")
    tab_legal = tabview_sobre.add("⚖️ Aviso Legal")

    # --- ABA 1: INFORMAÇÕES GERAIS ---
    texto_info = (
        "O Flycast Updater (Big Blue) é um ecossistema completo para gerenciamento, "
        "integração em nuvem e Frontend avançado focado no emulador Flycast.\n\n"
        "Criado de fãs para fãs, nosso objetivo é preservar o legado do Sega Dreamcast, "
        "Naomi e Atomiswave, entregando a melhor e mais moderna experiência de "
        "emulação em computadores modernos.\n\n"
        "Para ler tutoriais, obter suporte técnico ou conferir o código-fonte, "
        "visite o nosso repositório oficial."
    )
    lbl_info = ctk.CTkLabel(tab_info, text=texto_info, justify="left", wraplength=540, font=ctk.CTkFont(size=13))
    lbl_info.pack(padx=20, pady=(20, 15), anchor="w")

    btn_github = ctk.CTkButton(tab_info, text="🌐 Visitar GitHub Oficial", width=220, height=35, fg_color="#228B22", hover_color="#006400", font=ctk.CTkFont(weight="bold"), command=lambda: webbrowser.open(f"https://github.com/{repo_url}"))
    btn_github.pack(pady=(10, 20))

    # --- ABA 2: LICENÇA OPEN-SOURCE ---
    texto_licenca = (
        "Este software é de código aberto (Open-Source) e distribuído sob a licença GNU GPL v3.\n\n"
        "Você é totalmente livre para usar, estudar, compartilhar e modificar o código-fonte "
        "deste aplicativo, desde que as suas modificações também sejam mantidas de código aberto "
        "e distribuídas sob a mesma licença (GPL v3).\n\n"
        "O Flycast Updater é, e sempre será, um projeto estritamente sem fins lucrativos."
    )
    lbl_licenca = ctk.CTkLabel(tab_licenca, text=texto_licenca, justify="left", wraplength=540, font=ctk.CTkFont(size=13))
    lbl_licenca.pack(padx=20, pady=20, anchor="w")

    # --- ABA 3: DISCLAIMER / AVISO LEGAL ---
    texto_legal = (
        "⚠️ ISENÇÃO DE AUTORIA:\n"
        "O Flycast Updater não é de autoria dos criadores originais do emulador. "
        "Todos os direitos e créditos do núcleo de emulação 'Flycast' pertencem "
        "exclusivamente aos seus desenvolvedores oficiais (flyinghead e contribuidores).\n\n"
        "🚫 POLÍTICA CONTRA A PIRATARIA:\n"
        "Nenhum arquivo de BIOS (dc_boot.bin, dc_flash.bin, etc.), firmware de fliperamas ou "
        "jogos em formato de imagem (ROM/ISO/GDI/CHD) são fornecidos, embutidos ou "
        "distribuídos por este software.\n\n"
        "Este aplicativo é estritamente uma ferramenta de automação visual. O usuário "
        "é o único responsável por adquirir e utilizar arquivos de origem legal "
        "(realizados a partir de cópias de segurança de mídias físicas originais de sua propriedade)."
    )
    lbl_legal = ctk.CTkLabel(tab_legal, text=texto_legal, justify="left", wraplength=540, font=ctk.CTkFont(size=13))
    lbl_legal.pack(padx=20, pady=15, anchor="w")