# 🌀 Flycast Updater (v6.2 - Big Blue) - Windows

[![Version](https://img.shields.io/badge/version-6.2-blue.svg)](https://github.com/dsantanna/flycast_updater)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/dsantanna/flycast_updater)
[![Language](https://img.shields.io/badge/language-Python%20%2F%2F%20Multilingual%20(10%20Langs)-green.svg)](https://github.com/dsantanna/flycast_updater)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

> **🔥 THE MODULAR & TOOLS UPDATE (v6.2)**
> A versão 6.2 do **Big Blue** introduz a poderosa **Aba de Ferramentas (CHDMAN)** para compressão avançada em lote da sua biblioteca, um novo sistema de **Filtros Dinâmicos** para separar Arcade e Dreamcast com um clique, e uma **refatoração arquitetural gigantesca** sob o capô, deixando o aplicativo mais leve, modular e resistente a erros de interface (DPI Scaling) e autenticação de API!

O **Flycast Updater** transcendeu completamente sua função original de atualizador. Hoje ele atua como a suíte definitiva de gerenciamento, integração em nuvem e interface gráfica avançada para elevar a sua experiência de emulação no **Flycast** (Sega Dreamcast / Naomi / Atomiswave) no Windows a um patamar profissional.

---
## 🛠️ Novidades da Versão 6.2 & Funcionalidades Principais

- **Nova Aba de Ferramentas (CHD Compressor):** Comprima suas imagens pesadas `.GDI` ou `.CUE` para o formato ultraleve `.CHD` (ou reverta o processo) diretamente pela interface do aplicativo.
- **Gerenciamento Portátil do CHDMAN:** Instalação automática do utilitário `chdman.exe` na pasta interna `/tools/`, acompanhado de um painel de *Semáforo Visual* que indica o status de prontidão da ferramenta.
- **Barra de Progresso Integrada (Regex):** Adeus janelas de CMD confusas! O Big Blue agora exibe o progresso de compressão nativamente dentro do aplicativo utilizando interceptação silenciosa de logs.
- **Filtro Dinâmico por Sistema:** Novos atalhos estilizados (`[ Todos ] [ Dreamcast ] [ Arcade ]`) no topo da biblioteca de jogos. Com um único clique, o sistema aciona uma heurística de "Bala de Prata" para varrer extensões e separar perfeitamente jogos de fliperama dos de console.
- **Engenharia de Software (Clean Code):** Arquivo principal emagrecido em centenas de linhas. Motores de rede, saves, nuvem e autenticação foram isolados em módulos cirúrgicos para garantir máxima performance.
- **DPI / Scaling Bugfix:** Layout blindado e perfeitamente responsivo, independentemente de o usuário utilizar escalas de Windows em 100%, 125% ou 150%.
- **Autenticação RA Corrigida:** O protocolo seguro legado foi reinjetado de forma modular no sistema de API, garantindo logins precisos no RetroAchievements.

## 🎬 Funcionalidades Herdadas (Big Blue Core)

- **Modo Big Picture (Interface de TV Fullscreen):** Uma experiência cinematográfica imersiva em tela cheia que cobre a área de trabalho, permitindo navegação fluida por teclado e controle pelas capas dos jogos, com reprodução automática e dinâmica de Video Snaps (`video_snaps.py`).
- **Galeria de Conquistas do RetroAchievements (Vitrine Gold):** Tela interativa avançada de conquistas detalhadas por jogo, exibindo insígnias originais (com cache local e suporte a ícones de bloqueado/desbloqueado), barra de progresso global em tempo real e carimbo de data/hora dos troféus obtidos.
- **Overlay Animado de Troféus (PlayStation/Xbox Style):** Rastreador assíncrono avançado que monitora as sessões de jogo e dispara um *popup* holográfico e sonorizado na tela sempre que você desbloqueia um troféu, com total suporte a múltiplos monitores.
- **Gestão Consolidada de Controles e VMU:** Unificação total das abas de mapeamento e portas virtuais em um painel fluido com rolagem automática (*Autofit*), detecção dinâmica de dispositivos físicos (via `devices.py`) e seletor RGB de cor personalizado para a mira da pistola de luz.
- **Sincronização de Saves Sob Demanda (One-Click Sync):** Esqueça a espera pelo fechamento do emulador! Clique no status da Nuvem para forçar instantaneamente o backup de todo o seu progresso de VMU direto para o Google Drive ou OneDrive.
- **Rádio Ambiente Modular (`radio_flycast.py`) & Leitor ID3:** Motor de áudio totalmente refatorado em módulo independente. O Mini-Player e o Big Picture extraem metadados ID3 reais (títulos das faixas MP3) direto dos arquivos de áudio, exibindo a faixa atual com dicas de ferramentas (*Tooltip*) e controle de volume em tempo real.
- **Customização de Áudio (Sound Test):** Guia embutido na interface e suporte à pastas dedicadas (`/media/music` e `/media/sfx`) para criar a própria identidade sonora do *Frontend* (efeitos `.wav` de navegação, *start*, *save* e erro).
- **Apoio ao Projeto (Insert Coin):** Área dedicada à filosofia do software livre com opção de doação via PIX para manter a resiliência dos servidores e o desenvolvimento do Big Blue sempre em alta velocidade.
- **Gestor de Netplay & Rollback (GGPO):** Aba de Multiplayer online integrada diretamente na interface principal e no Big Picture, permitindo gerenciar salas (Host) ou conectar a amigos (Join) com controle total de portas de rede.
- **Enciclopédia de Metadados XML (`DC-game.xml`):** Integração profunda com o banco de dados oficial de metadados do Dreamcast, exibindo avaliações estelares (★), produtoras oficiais (`manufacturer`), classificações indicativas e quantidade de jogadores.
- **Suporte Expandido a Placas Arcade (Naomi, Naomi 2 & Atomiswave):** Inclusão de seletores dedicados na aba de BIOS e Emu para gerenciar, compactar e instalar as BIOS de Arcade exigidas pelo Flycast.
- **Temas Visuais Dinâmicos:** Suporte à personalização cromática em tempo real para combinar com o seu estilo (Padrão DARK, Sonic The Hedgehog, Crazy Taxi, Shenmue e Marvel vs Capcom 2).
- **Hall da Fama (Top 5) & Roleta de Jogos (🎲):** Exibição dos 5 jogos mais jogados no Tooltip do Dashboard baseados no Playtime Tracker e ferramenta interativa de sorteio aleatório de títulos.
- **A Platina da SEGA:** O motor detecta o status de "Mastered" (100%) em um jogo e exibe uma recompensa visual exclusiva "🌀 PLATINA" em azul SEGA nos seus cards.
- **Lançador de Jogos Rápido (Frontend):** Aba que exibe sua biblioteca de jogos em um elegante design de capas (cards), permitindo iniciar a emulação com apenas um duplo clique.
- **Auto-Scraper Inteligente (Multithread):** Integração livre com o repositório Libretro. Capas faltantes são procuradas e baixadas de forma paralela e ultrarrápida, sem travar a interface.
- **Galeria Visual de Save States:** A janela de detalhes captura automaticamente as fotos tiradas pelo emulador e gera um mosaico dos seus saves com data, hora e peso em KB.
- **Diário de Bordo:** Roteirize seus vídeos, anote timestamps ou salve códigos num bloco de notas interno dedicado a cada jogo, salvando nativamente tudo na sua base de dados.
- **Injeção de Perfis de Controle (Auto-Mapping):** Configure o seu Joystick em um clique. Aba dedicada que injeta arquivos `.cfg` otimizados para controles do Xbox, PlayStation e 8BitDo direto no emulador.
- **Modo Criador de Conteúdo / Streamer (OBS Ready):** Gere *widgets* de chroma key dinâmicos com sua arte de capa, integre textos do `Now Playing` direto no OBS Studio e oculte pastas sensíveis com o novo motor Anti-Leak Holográfico.
- **Clean Desktop (Auto-Ocultar):** A interface some silenciosamente da Área de Trabalho ao carregar um jogo, retornando magicamente assim que a gameplay for encerrada.

---

## ⚠️ Avisos Importantes (Disclaimer)

* **Isenção de Autoria:** O **Flycast Updater** não é de autoria dos criadores do emulador. Todos os créditos pertencem aos desenvolvedores oficiais do Flycast.
* **Ausência de BIOS e ROMs:** Nenhum arquivo de BIOS, firmware ou ROM/ISO é fornecido ou distribuído.
* **Dependência Visual e Sonora:** Para utilizar o Mini-Frontend com capas e rádio, são necessárias dependências como `Pillow` e `pygame-ce` embutidas no processo de build.

---

## 🚀 Como Usar

1. Acesse a aba [Releases](https://github.com/dsantanna/flycast_updater/releases).
2. Baixe o arquivo **`FlycastUpdater.exe`**.
3. Execute-o e navegue pela Interface Gráfica.

---

## ⚙️ Parâmetros de Linha de Comando (CLI)

* `-nogui` : Executa em modo texto.
* `-dev` / `-master` : Força a versão de desenvolvimento ou estável.
* `-rollback` : Restaura o último backup funcional.
* `-silent` : Executa em segundo plano.
* `-backup` : Executa apenas o backup na nuvem.
* `-reset` : Refaz a configuração inicial.