# 🌀 Flycast Updater (v6.0 - Big Blue) - Windows

[![Version](https://img.shields.io/badge/version-6.0-blue.svg)](https://github.com/dsantanna/flycast_updater)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/dsantanna/flycast_updater)[cite: 6]
[![Language](https://img.shields.io/badge/language-Python%20%2F%2F%20Multilingual%20(10%20Langs)-green.svg)](https://github.com/dsantanna/flycast_updater)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)[cite: 6]

> **🔥 A MAIOR E MAIS REVOLUCIONÁRIA ATUALIZAÇÃO DA HISTÓRIA DO PROJETO!** 
> A versão 6.0 transforma definitivamente o Flycast Updater de uma excelente ferramenta utilitária para uma **Central Multimídia e Frontend Completo de Alto Desempenho**. Esta edição histórica introduz o impressionante **Modo Big Picture (Interface de TV Fullscreen com reprodução automática de Video Snaps)**, uma **Vitrine Interativa Gold de Conquistas do RetroAchievements** com insígnias e cache otimizado, **Gestão Unificada de Controles e VMU** com rolagem automática (*Autofit*), detecção dinâmica de hardware físico e um motor de rádio modularizado com suporte a metadados ID3 reais.

O **Flycast Updater** transcendeu completamente sua função original de atualizador[cite: 6]. Hoje ele atua como a suíte definitiva de gerenciamento, integração em nuvem e interface gráfica avançada para elevar a sua experiência de emulação no **Flycast** (Sega Dreamcast / Naomi / Atomiswave) no Windows a um patamar profissional[cite: 6].

---
## 🎬 Funcionalidades Principais (v6.0 - Big Blue - GOLD Edition)

- **Modo Big Picture (Interface de TV Fullscreen):** Uma experiência cinematográfica imersiva em tela cheia que cobre a área de trabalho, permitindo navegação fluida por teclado e controle pelas capas dos jogos, com reprodução automática e dinâmica de Video Snaps (`video_snaps.py`).
- **Galeria de Conquistas do RetroAchievements (Vitrine Gold):** Tela interativa avançada de conquistas detalhadas por jogo, exibindo insígnias originais (com cache local e suporte a ícones de bloqueado/desbloqueado), barra de progresso global em tempo real e carimbo de data/hora dos troféus obtidos.
- **Gestão Consolidada de Controles e VMU:** Unificação total das abas de mapeamento e portas virtuais em um painel fluido com rolagem automática (*Autofit*), detecção dinâmica de dispositivos físicos (via `devices.py`) e seletor RGB de cor personalizado para a mira da pistola de luz.
- **Rádio Ambiente Modular (`radio_flycast.py`) & Leitor ID3:** Motor de áudio totalmente refatorado em módulo independente. O Mini-Player e o Big Picture extraem metadados ID3 reais (títulos das faixas MP3) direto dos arquivos de áudio, exibindo a faixa atual com dicas de ferramentas (*Tooltip*) e controle de volume em tempo real.
- **Gestor de Netplay & Rollback (GGPO):** Nova aba de Multiplayer online integrada diretamente na interface principal e no Big Picture, permitindo gerenciar salas (Host) ou conectar a amigos (Join) com controle total de portas de rede.
- **Enciclopédia de Metadados XML (`DC-game.xml`):** Integração profunda com o banco de dados oficial de metadados do Dreamcast, exibindo avaliações estelares (★), produtoras oficiais (`manufacturer`), classificações indicativas e quantidade de jogadores.
- **Motor Tradutor Silencioso (PT-BR Automático):** Tradução em tempo real das sinopses em inglês para o Português do Brasil com base nas configurações globais do aplicativo.
- **Suporte Expandido a Placas Arcade (Naomi, Naomi 2 & Atomiswave):** Inclusão de seletores dedicados na aba de BIOS e Emu para gerenciar, compactar e instalar as BIOS de Arcade exigidas pelo Flycast.
- **Atalhos de Lançamento e Manuais Inteligentes no Big Picture:** Botão dedicado para iniciar títulos instantaneamente e um atalho otimizado de leitura de manuais que minimiza o Big Picture de forma inteligente.
- **Forçamento Temporário de Fullscreen (QoL):** O Big Picture injeta automaticamente o comando de tela cheia no `emu.cfg` e via argumentos de linha de comando no boot do jogo, revertendo a preferência original ao encerrar a emulação.
- **Temas Visuais Dinâmicos:** Suporte à personalização cromática em tempo real para combinar com o seu estilo (Padrão DARK, Sonic The Hedgehog, Crazy Taxi, Shenmue e Marvel vs Capcom 2).
- **Hall da Fama (Top 5) & Roleta de Jogos (🎲):** Exibição dos 5 jogos mais jogados no Tooltip do Dashboard baseados no Playtime Tracker e ferramenta interativa de sorteio aleatório de títulos.
- **Refatoração Estrutural e Arquitetura Modular:** Separação completa em módulos independentes (`bigpicture.py`, `radio_flycast.py`, `game_launcher.py`, `netplay.py`, `dc_gamesdb.py`, `devices.py`, `video_snaps.py`), eliminando redundâncias e elevando a estabilidade da aplicação em nível profissional.
- **RetroAchievements via API Oficial:** Conexão direta via REST API de forma segura e oficial, trazendo estatísticas em tempo real sem bloqueios de firewall[cite: 6].
- **A Platina da SEGA:** O motor detecta o status de "Mastered" (100%) em um jogo e exibe uma recompensa visual exclusiva "🌀 PLATINA" em azul SEGA nos seus cards[cite: 6].
- **Placar de Pontuação Dinâmico:** Os cards de jogos exibem de forma clara a pontuação exata obtida em relação ao total possível (ex: `7/401 pts`), adaptando-se automaticamente ao Modo Hardcore[cite: 6].
- **Lançador de Jogos Rápido (Frontend):** Aba que exibe sua biblioteca de jogos em um elegante design de capas (cards), permitindo iniciar a emulação com apenas um duplo clique[cite: 6].
- **Barra de Pesquisa e Favoritos:** Filtre sua biblioteca instantaneamente enquanto digita ou marque títulos com a "⭐" para criar sua coleção personalizada de favoritos[cite: 6].
- **Auto-Scraper Inteligente (Multithread):** Integração livre com o repositório Libretro[cite: 6]. Capas faltantes são procuradas e baixadas de forma paralela e ultrarrápida, sem travar a interface[cite: 6].
- **Detecção de Múltiplos Discos e Regiões:** O motor interno une jogos multi-CD (como Shenmue) e funde ROMs duplicadas de regiões (USA/Japan) sob uma única capa, fornecendo um popup para a seleção no momento do carregamento[cite: 6].
- **Galeria Visual de Save States:** A janela de detalhes agora captura automaticamente as fotos tiradas pelo emulador e gera um mosaico dos seus saves com data, hora e peso em KB[cite: 6].
- **Diário de Bordo:** Roteirize seus vídeos, anote timestamps ou salve códigos num bloco de notas interno dedicado a cada jogo, salvando nativamente tudo na sua base de dados[cite: 6].
- **Backup Total na Nuvem:** Proteja mais do que apenas saves! Um clique agora engloba seus arquivos `emu.cfg`, `config.json` e o `RAlocal.db` com extração e recarregamento automático no ambiente[cite: 6].
- **Injeção de Perfis de Controle (Auto-Mapping):** Configure o seu Joystick em um clique[cite: 6]. Aba dedicada que injeta arquivos `.cfg` otimizados para controles do Xbox, PlayStation e 8BitDo direto no emulador[cite: 6].
- **Modo Criador de Conteúdo / Streamer (OBS Ready):** Gere *widgets* de chroma key dinâmicos com sua arte de capa, integre textos do `Now Playing` direto no OBS Studio e oculte pastas sensíveis com o novo motor Anti-Leak Holográfico[cite: 6].
- **Clean Desktop (Auto-Ocultar):** A interface some silenciosamente da Área de Trabalho ao carregar um jogo, retornando magicamente assim que a gameplay for encerrada[cite: 6].

---

## ⚠️ Avisos Importantes (Disclaimer)

* **Isenção de Autoria:** O **Flycast Updater** não é de autoria dos criadores do emulador[cite: 6]. Todos os créditos pertencem aos desenvolvedores oficiais do Flycast[cite: 6].
* **Ausência de BIOS e ROMs:** Nenhum arquivo de BIOS, firmware ou ROM/ISO é fornecido ou distribuído[cite: 6].
* **Dependência Visual e Sonora:** Para utilizar o Mini-Frontend com capas e rádio, são necessárias dependências como `Pillow` e `pygame-ce` embutidas no processo de build[cite: 6].

---

## 🚀 Como Usar

1. Acesse a aba [Releases](https://github.com/dsantanna/flycast_updater/releases)[cite: 6].
2. Baixe o arquivo **`FlycastUpdater.exe`**[cite: 6].
3. Execute-o e navegue pela Interface Gráfica[cite: 6].

---

## ⚙️ Parâmetros de Linha de Comando (CLI)

* `-nogui` : Executa em modo texto[cite: 6].
* `-dev` / `-master` : Força a versão de desenvolvimento ou estável[cite: 6].
* `-rollback` : Restaura o último backup funcional[cite: 6].
* `-silent` : Executa em segundo plano[cite: 6].
* `-backup` : Executa apenas o backup na nuvem[cite: 6].
* `-reset` : Refaz a configuração inicial[cite: 6].