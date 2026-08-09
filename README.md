# 🌀 Flycast Updater (v5.0) - Windows

[![Version](https://img.shields.io/badge/version-5.0-blue.svg)](https://github.com/dsantanna/flycast_updater)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/dsantanna/flycast_updater)[cite: 9]
[![Language](https://img.shields.io/badge/language-Python%20%2F%2F%20Multilingual-green.svg)](https://github.com/dsantanna/flycast_updater)[cite: 9]
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)[cite: 9]

O **Flycast Updater** transcendeu sua função original. Hoje ele atua como o gestor, integrador em nuvem e a interface gráfica completa (Frontend) para revolucionar a sua experiência de emulação no **Flycast** (Sega Dreamcast / Naomi / Atomiswave) no Windows.[cite: 9]

---
## 🎬 Funcionalidades Principais (v5.0 - Director's Cut)

- **Lançador de Jogos Rápido (Mini-Frontend):** Nova aba que exibe sua biblioteca de jogos em um elegante design de capas (cards), permitindo iniciar a emulação com apenas um duplo clique.
- **Auto-Scraper Inteligente:** Integração livre com o repositório Libretro. Capas faltantes são procuradas, baixadas e alocadas automaticamente de forma limpa.
- **Detecção de Múltiplos Discos:** O motor interno limpa os nomes dos arquivos e une jogos multi-CD (como Shenmue) sob uma única capa, fornecendo um popup para a seleção do disco no momento do carregamento.
- **Playtime Tracker:** O seu tempo de emulação agora é valioso! O sistema cronometra, unifica (em jogos de multi-CD) e salva de forma persistente suas estatísticas de jogo na base dos cards.
- **Injeção de Perfis de Controle (Auto-Mapping):** Configure o seu Joystick em um clique. Aba dedicada que injeta arquivos `.cfg` otimizados para controles do Xbox, PlayStation e 8BitDo direto no emulador.
- **Modo Criador de Conteúdo / Streamer:** Modifique as variáveis do `emu.cfg` com um clique, desativando os sons do VMU e pop-ups irritantes para gravações e lives impecáveis.
- **Injeção de Cheats & Widescreen:** Inicie a ROM já carregando a aba de truques ou hacks de expansão visual, com monitoramento ativo para alertar sobre o bloqueio das conquistas do RetroAchievements.

---
## 🌟 Funcionalidades Anteriores (Destaques)

- **Detecção de Hardware & Drivers:** Identifica sua placa de vídeo e direciona para os drivers oficiais compatíveis.[cite: 9]
- **Tradução em Tempo Real (i18n):** Mude instantaneamente entre 10 idiomas (incluindo PT-BR, EN-US e JA-JP) sem reiniciar.[cite: 9]
- **Assistente Inteligente de BIOS:** Varre, detecta, auto-renomeia arquivos `.bin` incorretos e extrai as BIOS diretamente de pacotes `.zip`.[cite: 9]
- **Custom Paths Dinâmicos:** Direcione a criação e leitura de BIOS, VMU, Save States e Saves para as pastas que você desejar.[cite: 9]
- **Restaurador de Backup Avançado (Cloud Saves):** Descompactador contextual que rastreia limites de retenção e restaura arquivos mapeando os diretórios dinamicamente para o Google Drive ou OneDrive.[cite: 9]
- **Super Logger Integrado:** Aba de auditoria em tempo real detalhando todas as injeções e transações mecânicas.[cite: 9]
- **Semáforo Interativo de Status:** Verificação visual para status de updates das "Daily Builds" ou da branch "Master".[cite: 9]

---

## ⚠️ Avisos Importantes (Disclaimer)

* **Isenção de Autoria:** O **Flycast Updater** não é de autoria dos criadores do emulador.[cite: 9] Todos os créditos pertencem aos desenvolvedores oficiais do Flycast.[cite: 9]
* **Ausência de BIOS e ROMs:** Nenhum arquivo de BIOS, firmware ou ROM/ISO é fornecido ou distribuído.[cite: 9]
* **Dependência Visual:** Para utilizar o Mini-Frontend com capas, instale a biblioteca de imagens: `pip install Pillow` via terminal.

---

## 🚀 Como Usar

1. Acesse a aba [Releases](https://github.com/dsantanna/flycast_updater/releases).[cite: 9]
2. Baixe o arquivo **`FlycastUpdater.exe`**.[cite: 9]
3. Execute-o e navegue pela Interface Gráfica.[cite: 9]

---

## ⚙️ Parâmetros de Linha de Comando (CLI)

* `-nogui` : Executa em modo texto.[cite: 9]
* `-dev` / `-master` : Força a versão de desenvolvimento ou estável.[cite: 9]
* `-rollback` : Restaura o último backup funcional.[cite: 9]
* `-silent` : Executa em segundo plano.[cite: 9]
* `-backup` : Executa apenas o backup na nuvem.[cite: 9]
* `-reset` : Refaz a configuração inicial.[cite: 9]