# 🌀 Flycast Updater (v6.3 - Big Blue) - Windows

[![Version](https://img.shields.io/badge/version-6.3-blue.svg)](https://github.com/dsantanna/flycast_updater)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/dsantanna/flycast_updater)
[![Language](https://img.shields.io/badge/language-Python%20%2F%2F%20Multilingual%20(10%20Langs)-green.svg)](https://github.com/dsantanna/flycast_updater)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

> **🔥 THE ULTIMATE QoL & HARDWARE UPDATE (v6.3)**
> A versão 6.3 eleva o **Big Blue** ao status de Frontend definitivo! Diga adeus aos menus complexos de configuração: o novo **Mapeador Visual de Controles** guia você botão a botão com uma interface moderna. Adicionamos também o **Gerenciador de Texturas HD** (Dropzone) para remasterizar seus jogos com um clique, um sistema de sub-abas inteligente para organizar suas ferramentas e um poderoso escudo anti-crash para proteger o modo Big Picture de falhas de HD externo.

O **Flycast Updater** transcendeu completamente sua função original de atualizador.[cite: 7] Hoje ele atua como a suíte definitiva de gerenciamento, integração em nuvem e interface gráfica avançada para elevar a sua experiência de emulação no **Flycast** (Sega Dreamcast / Naomi / Atomiswave) no Windows a um patamar profissional.[cite: 7]

---
## 🛠️ Novidades da Versão 6.3 & Funcionalidades Principais

- **Mapeador Visual de Controles:** Configure o seu hardware como se estivesse em um console moderno. O assistente visual solicita os botões na tela em tempo real e gera automaticamente o arquivo de configuração (.cfg) nativo do Flycast.
- **Gerenciador de Texturas HD (Remasterizador):** Uma área de "Dropzone" virtual interativa. Basta apontar o pacote `.zip` de texturas em alta resolução que o Big Blue faz a extração e a alocação de forma segura e em segundo plano.
- **Coesão de Interface (Sub-Abas):** Experiência de usuário (UX) refinada. Funcionalidades foram agrupadas inteligentemente em sub-abas dinâmicas (Controles, Ferramentas, CHDMAN), mantendo o aplicativo limpo e responsivo.
- **Escudo Anti-Crash (Big Picture):** Novo sistema de tolerância a falhas. Se a sua unidade de armazenamento de ROMs estiver desconectada ou vazia, o sistema dialoga com você prevenindo o fechamento repentino e auxiliando no re-mapeamento.
- **Nova Aba de Ferramentas (CHD Compressor):** Comprima suas imagens pesadas `.GDI` ou `.CUE` para o formato ultraleve `.CHD` (ou reverta o processo) diretamente pela interface do aplicativo.[cite: 7]
- **Gerenciamento Portátil do CHDMAN:** Instalação automática do utilitário `chdman.exe` na pasta interna `/tools/`, acompanhado de um painel de *Semáforo Visual* que indica o status de prontidão da ferramenta.[cite: 7]
- **Filtro Dinâmico por Sistema:** Novos atalhos estilizados (`[ Todos ] [ Dreamcast ] [ Arcade ]`) no topo da biblioteca de jogos. Com um único clique, o sistema aciona uma heurística de "Bala de Prata" para varrer extensões e separar perfeitamente jogos de fliperama dos de console.[cite: 7]

## 🎬 Funcionalidades Herdadas (Big Blue Core)

- **Modo Big Picture (Interface de TV Fullscreen):** Uma experiência cinematográfica imersiva em tela cheia que cobre a área de trabalho, permitindo navegação fluida por teclado e controle pelas capas dos jogos, com reprodução automática e dinâmica de Video Snaps (`video_snaps.py`).[cite: 7]
- **Galeria de Conquistas do RetroAchievements (Vitrine Gold):** Tela interativa avançada de conquistas detalhadas por jogo, exibindo insígnias originais (com cache local e suporte a ícones de bloqueado/desbloqueado), barra de progresso global em tempo real e carimbo de data/hora dos troféus obtidos.[cite: 7]
- **Overlay Animado de Troféus (PlayStation/Xbox Style):** Rastreador assíncrono avançado que monitora as sessões de jogo e dispara um *popup* holográfico e sonorizado na tela sempre que você desbloqueia um troféu, com total suporte a múltiplos monitores.[cite: 7]
- **Gestão Consolidada de Controles e VMU:** Unificação total das abas de mapeamento e portas virtuais em um painel fluido com rolagem automática (*Autofit*), detecção dinâmica de dispositivos físicos (via `devices.py`) e seletor RGB de cor personalizado para a mira da pistola de luz.[cite: 7]
- **Sincronização de Saves Sob Demanda (One-Click Sync):** Esqueça a espera pelo fechamento do emulador! Clique no status da Nuvem para forçar instantaneamente o backup de todo o seu progresso de VMU direto para o Google Drive ou OneDrive.[cite: 7]
- **Rádio Ambiente Modular (`radio_flycast.py`) & Leitor ID3:** Motor de áudio totalmente refatorado em módulo independente. O Mini-Player e o Big Picture extraem metadados ID3 reais (títulos das faixas MP3) direto dos arquivos de áudio, exibindo a faixa atual com dicas de ferramentas (*Tooltip*) e controle de volume em tempo real.[cite: 7]
- **Customização de Áudio (Sound Test):** Guia embutido na interface e suporte à pastas dedicadas (`/media/music` e `/media/sfx`) para criar a própria identidade sonora do *Frontend* (efeitos `.wav` de navegação, *start*, *save* e erro).[cite: 7]
- **Apoio ao Projeto (Insert Coin):** Área dedicada à filosofia do software livre com opção de doação via PIX para manter a resiliência dos servidores e o desenvolvimento do Big Blue sempre em alta velocidade.[cite: 7]
- **Gestor de Netplay & Rollback (GGPO):** Aba de Multiplayer online integrada diretamente na interface principal e no Big Picture, permitindo gerenciar salas (Host) ou conectar a amigos (Join) com controle total de portas de rede.[cite: 7]
- **Enciclopédia de Metadados XML (`DC-game.xml`):** Integração profunda com o banco de dados oficial de metadados do Dreamcast, exibindo avaliações estelares (★), produtoras oficiais (`manufacturer`), classificações indicativas e quantidade de jogadores.[cite: 7]
- **Suporte Expandido a Placas Arcade (Naomi, Naomi 2 & Atomiswave):** Inclusão de seletores dedicados na aba de BIOS e Emu para gerenciar, compactar e instalar as BIOS de Arcade exigidas pelo Flycast.[cite: 7]
- **Temas Visuais Dinâmicos:** Suporte à personalização cromática em tempo real para combinar com o seu estilo (Padrão DARK, Sonic The Hedgehog, Crazy Taxi, Shenmue e Marvel vs Capcom 2).[cite: 7]
- **Hall da Fama (Top 5) & Roleta de Jogos (🎲):** Exibição dos 5 jogos mais jogados no Tooltip do Dashboard baseados no Playtime Tracker e ferramenta interativa de sorteio aleatório de títulos.[cite: 7]
- **A Platina da SEGA:** O motor detecta o status de "Mastered" (100%) em um jogo e exibe uma recompensa visual exclusiva "🌀 PLATINA" em azul SEGA nos seus cards.[cite: 7]
- **Lançador de Jogos Rápido (Frontend):** Aba que exibe sua biblioteca de jogos em um elegante design de capas (cards), permitindo iniciar a emulação com apenas um duplo clique.[cite: 7]
- **Auto-Scraper Inteligente (Multithread):** Integração livre com o repositório Libretro. Capas faltantes são procuradas e baixadas de forma paralela e ultrarrápida, sem travar a interface.[cite: 7]
- **Galeria Visual de Save States:** A janela de detalhes captura automaticamente as fotos tiradas pelo emulador e gera um mosaico dos seus saves com data, hora e peso em KB.[cite: 7]
- **Diário de Bordo:** Roteirize seus vídeos, anote timestamps ou salve códigos num bloco de notas interno dedicado a cada jogo, salvando nativamente tudo na sua base de dados.[cite: 7]
- **Injeção de Perfis de Controle (Auto-Mapping):** Configure o seu Joystick em um clique. Aba dedicada que injeta arquivos `.cfg` otimizados para controles do Xbox, PlayStation e 8BitDo direto no emulador.[cite: 7]
- **Modo Criador de Conteúdo / Streamer (OBS Ready):** Gere *widgets* de chroma key dinâmicos com sua arte de capa, integre textos do `Now Playing` direto no OBS Studio e oculte pastas sensíveis com o novo motor Anti-Leak Holográfico.[cite: 7]
- **Clean Desktop (Auto-Ocultar):** A interface some silenciosamente da Área de Trabalho ao carregar um jogo, retornando magicamente assim que a gameplay for encerrada.[cite: 7]

---

## ⚠️ Avisos Importantes (Disclaimer)

* **Isenção de Autoria:** O **Flycast Updater** não é de autoria dos criadores do emulador. Todos os créditos pertencem aos desenvolvedores oficiais do Flycast.[cite: 7]
* **Ausência de BIOS e ROMs:** Nenhum arquivo de BIOS, firmware ou ROM/ISO é fornecido ou distribuído.[cite: 7]
* **Dependência Visual e Sonora:** Para utilizar o Mini-Frontend com capas e rádio, são necessárias dependências como `Pillow` e `pygame-ce` embutidas no processo de build.[cite: 7]

---

## 🚀 Como Usar

1. Acesse a aba [Releases](https://github.com/dsantanna/flycast_updater/releases).[cite: 7]
2. Baixe o arquivo **`FlycastUpdater.exe`**.[cite: 7]
3. Execute-o e navegue pela Interface Gráfica.[cite: 7]

---

## ⚙️ Parâmetros de Linha de Comando (CLI)

* `-nogui` : Executa em modo texto.[cite: 7]
* `-dev` / `-master` : Força a versão de desenvolvimento ou estável.[cite: 7]
* `-rollback` : Restaura o último backup funcional.[cite: 7]
* `-silent` : Executa em segundo plano.[cite: 7]
* `-backup` : Executa apenas o backup na nuvem.[cite: 7]
* `-reset` : Refaz a configuração inicial.[cite: 7]