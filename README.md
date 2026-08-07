# 🌀 Flycast Updater (v3.0) - Windows

[![Version](https://img.shields.io/badge/version-3.0-blue.svg)](https://github.com/dsantanna/flycast_updater)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/dsantanna/flycast_updater)
[![Language](https://img.shields.io/badge/language-Python%20%2F%2F%20Multilingual-green.svg)](https://github.com/dsantanna/flycast_updater)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

O **Flycast Updater** é uma ferramenta inteligente e automatizada desenvolvida para gerenciar o download, a instalação e a atualização contínua do emulador **Flycast** (Sega Dreamcast / Naomi / Atomiswave) no Windows.

---
## 🌴 Funcionalidades Principais (v3.0 - Emerald Coast Edition)

- **Hub Completo de Configuração:** Interface gráfica expandida organizada em abas intuitivas (`Nuvem`, `Emulador`, `Vídeo`, `Saves`), centralizando toda a experiência de gerenciamento.
- **Restaurador de Saves na Nuvem:** Nova aba dedicada a listar e extrair com um clique os arquivos `.zip` de backup armazenados na nuvem (Google Drive/OneDrive), ordenados do mais recente para o mais antigo.
- **Assistente de BIOS Inteligente:** Detecta automaticamente arquivos de BIOS mal posicionados na raiz e oferece duas soluções automatizadas: movê-los para a pasta `data` ou registrar um caminho personalizado no `emu.cfg`.
- **Aba de Vídeo e Gráficos Básicos:** Controle direto sobre a API Gráfica (OpenGL, Vulkan, DirectX 9, DirectX 11) com tooltips informativos de vantagens e desvantagens, Resolução Interna, Tela Cheia, Escala Inteira, Interpolação Linear e V-Sync.
- **Olho Mágico (Toggle de Senha):** Botão interativo para ocultar ou revelar a senha ou Token do RetroAchievements durante a digitação.
- **Interface Gráfica (GUI) Premium:** Desenvolvida em CustomTkinter, oferecendo uma experiência visual fluida, tema escuro nativo e Tooltips (dicas flutuantes) interativos.
- **Semáforo Interativo de Status:** Verificação em tempo real e em background alertando se o emulador precisa ser instalado (Vermelho), atualizado (Amarelo) ou se já está pronto para jogar (Verde).
- **Validação de Nuvem Inteligente:** Detecção dinâmica da instalação do Google Drive e OneDrive na máquina do usuário. O sistema desabilita botões caso os aplicativos de nuvem não sejam localizados localmente.
- **Cloud Saves Passivo:** Backup automatizado de saves (VMU/SRAM) detectando e utilizando instâncias locais do Google Drive ou OneDrive, de forma totalmente segura (sem requerer senhas ou credenciais).
- **Sistema de Rollback Inteligente:** Geração automática de "cápsulas do tempo" locais. O botão de reversão da interface reage à presença do backup (`flycast_backup.zip`) e se desabilita se não houver um ponto de restauração disponível.
- **Modo Híbrido (CLI/GUI):** O aplicativo oculta perfeitamente a tela preta ao ser aberto via duplo-clique no Windows, mas retoma o controle nativo do terminal (incluindo o questionário interativo) quando acionado pelo comando `-nogui`.
- **Trilha de Auditoria Unificada (`flycast_updater.log`):** Sistema de logs detalhado e incremental, rotulado rigorosamente com a versão ativa e parâmetros definidos pelo usuário.
- **Persistência de Preferências (`config.json`):** Salva automaticamente as escolhas de branch, caminho de instalação, provedor de nuvem e criação de atalhos.
- **Geração Automatizada de Atalhos:** Criação de atalhos personalizados na Área de Trabalho e de inicialização oculta apontando de maneira robusta para a pasta correta escolhida.

---
## 🚀 Funcionalidades Principais (v2.0 - Gold Master GUI Edition)

- **Interface Gráfica (GUI) Premium:** Desenvolvida em CustomTkinter, oferecendo uma experiência visual fluida, tema escuro nativo e Tooltips (dicas flutuantes) interativos.
- **Semáforo Interativo de Status:** Verificação em tempo real e em background alertando se o emulador precisa ser instalado (Vermelho), atualizado (Amarelo) ou se já está pronto para jogar (Verde).
- **Validação de Nuvem Inteligente:** Detecção dinâmica da instalação do Google Drive e OneDrive na máquina do usuário. O sistema desabilita botões caso os aplicativos de nuvem não sejam localizados localmente.
- **Cloud Saves Passivo:** Backup automatizado de saves (VMU/SRAM) detectando e utilizando instâncias locais do Google Drive ou OneDrive, de forma totalmente segura (sem requerer senhas ou credenciais).
- **Sistema de Rollback Inteligente:** Geração automática de "cápsulas do tempo" locais. O botão de reversão da interface reage à presença do backup (`flycast_backup.zip`) e se desabilita se não houver um ponto de restauração disponível.
- **Modo Híbrido (CLI/GUI):** O aplicativo oculta perfeitamente a tela preta ao ser aberto via duplo-clique no Windows, mas retoma o controle nativo do terminal (incluindo o questionário interativo) quando acionado pelo comando `-nogui`.
- **Trilha de Auditoria Unificada (`flycast_updater.log`):** Sistema de logs detalhado e incremental, rotulado rigorosamente com a versão ativa e parâmetros definidos pelo usuário.
- **Verificação Passiva de BIOS:** Inspeção local e estritamente educacional para alertar o usuário através de um semáforo visual na interface (🟢/🟡/🔴) caso os arquivos de sistema (`dc_boot.bin`, `dc_flash.bin`) estejam incorretos ou ausentes.
- **Persistência de Preferências (`config.json`):** Salva automaticamente as escolhas de branch, caminho de instalação, provedor de nuvem e criação de atalhos.
- **Geração Automatizada de Atalhos:** Criação de atalhos personalizados na Área de Trabalho e de inicialização oculta apontando de maneira robusta para a pasta correta escolhida.

---
## 🚀 Funcionalidades Principais (v1.2 - Cloud Save Edition)

- **Cloud Saves Passivo:** Backup automatizado de saves (VMU/SRAM) detectando e utilizando instâncias locais do Google Drive ou OneDrive, de forma totalmente segura (sem requerer senhas ou credenciais).
- **Sistema de Rollback:** Geração automática de "cápsulas do tempo" locais antes de cada extração, permitindo reverter o emulador para a versão anterior caso uma build diária apresente instabilidade.
- **Modo Silencioso (Background):** Capacidade de rodar o atualizador de forma invisível, com integração nativa à pasta de Inicialização (Startup) do Windows.
- **Arquitetura Inteligente (Launcher + Motor):** Separação clara entre o cérebro de controle (`launcher.py`) e o motor de download (`update_flycast.py`), agora totalmente sincronizados.
- **Auto-Atualização do Launcher:** Verifica automaticamente na API do GitHub se há uma nova versão do próprio atualizador, baixando e aplicando atualizações de forma transparente.
- **Barra de Progresso Visual em Tempo Real:** Monitoramento do download via blocos de bytes, exibindo a porcentagem exata e o volume transferido em megabytes (`MB`).
- **Trilha de Auditoria Unificada (`flycast_updater.log`):** Sistema de logs detalhado e incremental, rotulado rigorosamente com a versão ativa e parâmetros definidos pelo usuário.
- **Verificação Passiva de BIOS:** Inspeção local e estritamente educacional para alertar o usuário caso os arquivos fundamentais de sistema (`dc_boot.bin`, `dc_flash.bin`) estejam ausentes.
- **Persistência de Preferências (`config.json`):** Salva automaticamente as escolhas de branch, caminho de instalação, provedor de nuvem e criação de atalhos.
- **Geração Automatizada de Atalhos:** Criação de atalhos personalizados na Área de Trabalho do Windows apontando para o binário do Flycast com o ícone oficial do emulador.

---

## ⚠️ Avisos Importantes (Disclaimer)

* **Isenção de Autoria:** O **Flycast Updater** não é de autoria dos criadores do emulador. Este projeto é apenas um script utilitário que automatiza o processo de download e atualização. **Todos os créditos, direitos autorais e méritos do Flycast pertencem exclusivamente aos seus desenvolvedores e mantenedores oficiais.**
* **Ausência de BIOS e ROMs:** **Nenhum arquivo de BIOS, firmware ou ROM/ISO de jogos** é fornecido, hospedado ou distribuído através deste repositório.
* **Uso Legal:** Para utilizar o emulador Flycast, o usuário deve possuir os arquivos de BIOS extraídos de seu próprio hardware e ter os **jogos originais** legalmente adquiridos.

---

## 🌟 Principais Recursos

* **Duas Branches Suportadas:** 
  * `Master`: Versão estável oficial (via GitHub Releases).
  * `Dev`: Versão de desenvolvimento / builds diárias da nuvem (via S3 Buckets e commits do GitHub).
* **Auto-Cópia Inteligente:** O script/executável gerencia sua própria cópia para o diretório de destino do emulador após o usuário selecionar o caminho na interface gráfica.
* **Atalhos Automatizados:** Criação opcional de atalhos na Área de Trabalho com o ícone oficial customizado de atualização.
* **Sistema de Auditoria por Logs:** Mantém um histórico incremental de execuções (`flycast_updater.log`) registrando data, hora e a versão exata do script.

---

## 🚀 Como Usar

Para a grande maioria dos usuários, basta baixar a versão pronta para uso:
1. Acesse a aba [Releases](https://github.com/dsantanna/flycast_updater/releases).
2. Baixe o arquivo **`FlycastUpdater.exe`**.
3. Execute-o e navegue pela Interface Gráfica, escolhendo a pasta de instalação, a versão e os parâmetros de nuvem. Tudo muito simples e com dicas ao passar o mouse (Tooltips).

---

## 🛡️ Solução de Problemas (FAQ)

* **O Windows Defender / SmartScreen bloqueou o executável ao abrir:**
  * Como o arquivo `.exe` foi compilado de forma independente via PyInstaller (e não possui uma assinatura digital comercial paga), o Windows pode exibir uma janela de aviso (*"O Windows protegeu o seu computador"*).
  * **Como resolver:** Basta clicar em **"Mais informações"** e, em seguida, no botão **"Executar assim mesmo"**. O programa é totalmente seguro e de código aberto.

---

## ⚙️ Parâmetros de Linha de Comando (CLI)

Você pode executar o atualizador via terminal passando argumentos opcionais:

* `-nogui` : Executa em modo texto (Terminal Clássico).
* `-help`, `-h`, `--help` : Exibe o menu de ajuda e encerra.
* `-dev` : Força a configuração e o download da versão diária (Dev).
* `-master` : Força a configuração e o download da versão estável (Master).
* `-rollback` : Restaura o último backup funcional do emulador.
* `-silent` : Executa o atualizador em segundo plano (invisível) sem exibir o terminal.
* `-backup` : Executa apenas a rotina de backup dos saves na nuvem configurada e encerra.
* `-gdrive` / `-onedrive` : Força e ativa o uso do Google Drive ou OneDrive para backup dos saves.
* `-reset` : Ignora o arquivo `config.json` salvo e exibe o menu interativo de reconfiguração inicial na CLI.

Exemplo:
```cmd
FlycastUpdater.exe -dev -silent -gdrive