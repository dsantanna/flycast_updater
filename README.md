# 🌀 Flycast Updater (v4.2) - Windows

[![Version](https://img.shields.io/badge/version-4.2-blue.svg)](https://github.com/dsantanna/flycast_updater)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/dsantanna/flycast_updater)[cite: 7]
[![Language](https://img.shields.io/badge/language-Python%20%2F%2F%20Multilingual-green.svg)](https://github.com/dsantanna/flycast_updater)[cite: 7]
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)[cite: 7]

O **Flycast Updater** é uma ferramenta inteligente e automatizada desenvolvida para gerenciar o download, a instalação e a atualização contínua do emulador **Flycast** (Sega Dreamcast / Naomi / Atomiswave) no Windows.[cite: 7]

---
## 🌟 Funcionalidades Principais (v4.2 - Another Day Edition)

- **Detecção de Hardware Gráfico:** Nova seção na aba de Vídeo que identifica automaticamente todas as placas de vídeo (integradas e dedicadas) do sistema, através de varredura silenciosa via PowerShell.
- **Sugestão Inteligente de Drivers:** O aplicativo reconhece a fabricante da sua placa (NVIDIA, AMD ou Intel) e oferece um botão seguro de acesso direto para baixar os drivers oficiais mais recentes.
- **Layout Dinâmico para Notebooks:** O design se adapta dinamicamente para mostrar informações limpas e usar separadores visuais elegantes quando o computador tiver mais de uma GPU.
- **Tradução em Tempo Real (i18n Dinâmico):** Ao alterar o idioma no menu superior, a interface gráfica é atualizada instantaneamente, eliminando a necessidade de reiniciar o aplicativo.[cite: 7]
- **Cobertura Global Completa de Idiomas:** Todos os 10 idiomas suportados (PT-BR, EN-US, ES-ES, FR-FR, DE-DE, ZH-CN, JA-JP, RU-RU, AR-SA, HI-IN) foram totalmente preenchidos e revisados para contemplar todas as abas, botões, logs e opções avançadas.[cite: 7]
- **Aviso Inteligente de Atualização do Launcher:** O sistema agora exibe um alerta claro e multilíngue quando uma nova versão do próprio *Flycast Updater* é detectada, informando que a ferramenta será atualizada em conjunto com o emulador.[cite: 7]
- **Internacionalização Global (i18n):** O Flycast Updater fala com o mundo com suporte nativo e instantâneo.[cite: 7]
- **Assistente Inteligente de BIOS:** Novo motor autônomo que varre, detecta, auto-renomeia arquivos `.bin` incorretos e extrai as BIOS (`dc_boot.bin`, `dc_flash.bin`) de pacotes `.zip`.[cite: 7]
- **Custom Paths Dinâmicos:** Suporte completo à configuração de pastas personalizadas para BIOS, VMU, Save States e Saves de Jogo, com criação automática de diretórios e integração ao `emu.cfg`.[cite: 7]
- **Restaurador de Backup Avançado:** Descompactador de nuvem com inteligência contextual para direcionamento de VMU e Mappings ativos.[cite: 7]
- **Gerenciamento Passivo de Nuvem:** Sistema de limite de armazenamento para Cloud Saves (1, 3, 5, 10, 15 ou Ilimitado) com limpeza automática de arquivos antigos.[cite: 7]
- **Super Logger Integrado (Aba de Logs):** Modo tagarela com aba de diagnóstico e auditoria em tempo real.[cite: 7]

---
## 🌴 Funcionalidades Principais (v3.1 - Emerald Coast Edition - Bugfix)

- **Modo CLI Persistente (-nogui na UI):** Adicionado novo switch na aba de Nuvem para permitir que o usuário desative permanentemente o ambiente gráfico.[cite: 7]
- **Correção da Autoatualização Gráfica:** Ajustado o encerramento do processo de auto-update utilizando `os._exit(0)`, permitindo que o script `.bat` substitua o executável com sucesso.[cite: 7]
- **Mapeamento Exato da API Gráfica:** Correção definitiva dos índices do parâmetro `pvr.rend` no `emu.cfg` (`0 = OpenGL`, `1 = DirectX 9`, `2 = DirectX 11`, `4 = Vulkan`).[cite: 7]

---
## 🌴 Funcionalidades Principais (v3.0 - Emerald Coast Edition)

- **Hub Completo de Configuração:** Interface gráfica expandida organizada em abas intuitivas (`Nuvem`, `Emulador`, `Vídeo`, `Saves`), centralizando toda a experiência de gerenciamento.[cite: 7]
- **Restaurador de Saves na Nuvem:** Nova aba dedicada a listar e extrair com um clique os arquivos `.zip` de backup armazenados na nuvem (Google Drive/OneDrive).[cite: 7]
- **Assistente de BIOS Inteligente:** Detecta automaticamente arquivos de BIOS mal posicionados na raiz e oferece soluções automatizadas.[cite: 7]
- **Aba de Vídeo e Gráficos Básicos:** Controle direto sobre a API Gráfica com tooltips informativos e opções visuais avançadas.[cite: 7]
- **Olho Mágico (Toggle de Senha):** Botão interativo para mascarar ou revelar senhas e Tokens do RetroAchievements.[cite: 7]

---
## 🚀 Funcionalidades Anteriores (v2.0 a v1.2)

- **Interface Gráfica (GUI) Premium:** Desenvolvida em CustomTkinter com tema escuro nativo e tooltips interativos.[cite: 7]
- **Semáforo Interativo de Status:** Verificação em tempo real (🟢/🟡/🔴) para instalação e atualização.[cite: 7]
- **Cloud Saves Passivo e Rollback:** Proteção de dados na nuvem e sistema de cápsulas do tempo locais.[cite: 7]

---

## ⚠️ Avisos Importantes (Disclaimer)

* **Isenção de Autoria:** O **Flycast Updater** não é de autoria dos criadores do emulador.[cite: 7] Todos os créditos pertencem aos desenvolvedores oficiais do Flycast.[cite: 7]
* **Ausência de BIOS e ROMs:** Nenhum arquivo de BIOS, firmware ou ROM/ISO é fornecido ou distribuído.[cite: 7]
* **Uso Legal:** O usuário deve utilizar arquivos extraídos de seu próprio hardware e jogos legalmente adquiridos.[cite: 7]

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

Exemplo:
```cmd
FlycastUpdater.exe -dev -silent -gdrive