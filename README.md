# 🌀 Flycast Updater (v1.1) - Windows


[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/dsantanna/flycast_updater)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/dsantanna/flycast_updater)
[![Language](https://img.shields.io/badge/language-Python%20%2F%2F%20Multilingual-green.svg)](https://github.com/dsantanna/flycast_updater)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

O **Flycast Updater** é uma ferramenta inteligente e automatizada desenvolvida para gerenciar o download, a instalação e a atualização contínua do emulador **Flycast** (Sega Dreamcast / Naomi / Atomiswave) no Windows.

---
## 🚀 Funcionalidades Principais (v1.1)

- **Arquitetura Inteligente (Launcher + Motor):** Separação clara entre o cérebro de controle (`launcher.py`) e o motor de download (`update_flycast.py`).
- **Auto-Atualização do Launcher:** Verifica automaticamente na API do GitHub se há uma nova versão do próprio atualizador, baixando e aplicando atualizações de forma transparente.
- **Barra de Progresso Visual em Tempo Real:** Monitoramento do download via blocos de bytes, exibindo a porcentagem exata e o volume transferido em megabytes (`MB`).
- **Trilha de Auditoria Unificada (`flycast_updater.log`):** Sistema de logs detalhado e incremental, rotulado rigorosamente com a versão ativa e carimbos de data/hora de cada ação realizada.
- **Verificação Passiva de BIOS:** Inspeção local e estritamente educacional para alertar o usuário caso os arquivos fundamentais de sistema (`dc_boot.bin`, `dc_flash.bin`) estejam ausentes, mantendo total conformidade legal (sem distribuição de arquivos proprietários).
- **Persistência de Preferências (`config.json`):** Salva automaticamente as escolhas de branch, caminho de instalação e criação de atalhos, evitando perguntas repetitivas em execuções futuras.
- **Geração Automatizada de Atalhos:** Criação de atalhos personalizados na Área de Trabalho do Windows apontando para o binário do Flycast com o ícone oficial do emulador.

## ⚠️ Avisos Importantes (Disclaimer)

* **Isenção de Autoria:** O **Flycast Updater** não é de autoria dos criadores do emulador. Este projeto é apenas um script utilitário que automatiza o processo de download e atualização. **Todos os créditos, direitos autorais e méritos do Flycast pertencem exclusivamente aos seus desenvolvedores e mantenedores oficiais.**
* **Ausência de BIOS e ROMs:** **Nenhum arquivo de BIOS, firmware ou ROM/ISO de jogos** é fornecido, hospedado ou distribuído através deste repositório. 
* **Uso Legal:** Para utilizar o emulador Flycast, o usuário deve possuir os arquivos de BIOS extraídos de seu próprio hardware e ter os **jogos originais** legalmente adquiridos.

---

## 🌟 Principais Recursos

* **Suporte Multilíngue Automático:** O inicializador detecta o idioma do sistema operacional Windows e executa a versão ideal (Português do Brasil ou Inglês - US).
* **Duas Branches Suportadas:** 
  * `Master`: Versão estável oficial (via GitHub Releases).
  * `Dev`: Versão de desenvolvimento / builds diárias da nuvem (via S3 Buckets e commits do GitHub).
* **Auto-Cópia Inteligente:** O script/executável gerencia sua própria cópia para o diretório de destino do emulador.
* **Atalhos Automatizados:** Criação opcional de atalhos na Área de Trabalho com o ícone oficial customizado de atualização.
* **Sistema de Auditoria por Logs:** Mantém um histórico incremental de execuções (`flycast_updater.log`) registrando data, hora e a versão exata do script.
* **Menu de Ajuda Integrado:** Suporte a parâmetros de linha de comando (`-help`, `-h`, `--help`).

---

## 🚀 Como Usar

Para a grande maioria dos usuários, basta baixar a versão pronta para uso:
1. Acesse a aba [Releases](https://github.com/dsantanna/flycast_updater/releases).
2. Baixe o arquivo **`FlycastUpdater.exe`**.
3. Execute-o na pasta onde deseja manter o emulador. Na primeira execução, o programa solicitará que você escolha a branch desejada e se deseja criar um atalho na Área de Trabalho.

---

## 🛡️ Solução de Problemas (FAQ)

* **O Windows Defender / SmartScreen bloqueou o executável ao abrir:**
  * Como o arquivo `.exe` foi compilado de forma independente via PyInstaller (e não possui uma assinatura digital comercial paga), o Windows pode exibir uma janela de aviso (*"O Windows protegeu o seu computador"*). 
  * **Como resolver:** Basta clicar em **"Mais informações"** e, em seguida, no botão **"Executar assim mesmo"**. O programa é totalmente seguro e de código aberto.

---

## ⚙️ Parâmetros de Linha de Comando (CLI)

Você pode executar o atualizador via terminal passando argumentos opcionais:

* `-help`, `-h`, `--help` : Exibe o menu de ajuda e encerra.
* `-dev` : Força a configuração e o download da versão diária (Dev).
* `-master` : Força a configuração e o download da versão estável (Master).
* `-reset` : Ignora o arquivo `config.json` salvo e exibe o menu interativo de reconfiguração inicial.
* `-path <diretriz>` *(Apenas versão PT)* : Define um diretório de instalação personalizado.

Exemplo:
```cmd
FlycastUpdater.exe -dev -path <caminho_completo>
```
## 🛠️ Tecnologias Utilizadas

- **Python 3.x** (Linguagem principal)
- **PyInstaller** (Compilação para executável standalone `.exe`)
- **GitHub Actions** (CI/CD para build e release automatizadas)

# 🌀 Flycast Updater Linux (v1.0)

The **Flycast Updater** is a smart, automated tool developed to manage the download, installation, and continuous updating of the **Flycast** emulator (Sega Dreamcast / Naomi / Atomiswave) on Windows.

---

## ⚠️ Important Notices (Disclaimer)

* **Authorship Disclaimer:** The **Flycast Updater** is not authored by the creators of the emulator. This project is merely a utility script that automates the download and update process. **All credits, copyrights, and merits of Flycast belong exclusively to its official developers and maintainers.**
* **Absence of BIOS and ROMs:** **No BIOS, firmware, or game ROM/ISO files** are provided, hosted, or distributed through this repository. 
* **Legal Use:** To use the Flycast emulator, the user must own the BIOS files extracted from their own hardware and have legally acquired **original games**.

---

## 🌟 Key Features

* **Automatic Multilingual Support:** The launcher detects the Windows operating system language and runs the ideal version (Brazilian Portuguese or US English).
* **Two Supported Branches:** 
  * `Master`: Official stable version (via GitHub Releases).
  * `Dev`: Development version / daily cloud builds (via S3 Buckets and GitHub commits).
* **Smart Self-Copy:** The script/executable manages its own copy to the emulator's destination directory.
* **Automated Shortcuts:** Optional creation of Desktop shortcuts with the official custom update icon.
* **Log Audit System:** Maintains an incremental execution history (`flycast_updater.log`) recording the date, time, and exact version of the script.
* **Integrated Help Menu:** Support for command-line parameters (`-help`, `-h`, `--help`).

---

## 🚀 How to Use

For the vast majority of users, simply download the ready-to-use version:
1. Go to the [Releases](https://github.com/dsantanna/flycast_updater/releases) tab.
2. Download the **`FlycastUpdater.exe`** file.
3. Run it in the folder where you want to keep the emulator. On the first run, the program will ask you to choose the desired branch and whether you want to create a Desktop shortcut.

---

## 🛡️ Troubleshooting (FAQ)

* **Windows Defender / SmartScreen blocked the executable upon opening:**
  * Since the `.exe` file was independently compiled via PyInstaller (and does not have a paid commercial digital signature), Windows may display a warning window (*"Windows protected your PC"*). 
  * **How to fix:** Simply click on **"More info"** and then on the **"Run anyway"** button. The program is completely safe and open source.

---

## ⚙️ Command-Line Parameters (CLI)

You can run the updater via the terminal by passing optional arguments:

* `-help`, `-h`, `--help` : Displays the help menu and exits.
* `-dev` : Forces the configuration and download of the daily version (Dev).
* `-master` : Forces the configuration and download of the stable version (Master).
* `-path <directory>` *(PT version only)* : Sets a custom installation directory.

Example:
```cmd
FlycastUpdater.exe -dev -path <full_path>
```

# Flycast Updater (Linux) - v1.0

Ferramenta automatizada em Python para gerenciar, atualizar e iniciar o emulador **Flycast** no Linux (Ubuntu e derivados), com suporte completo às versões estáveis (**Master**) e de desenvolvimento diário (**Dev**).

---

## 🚀 Funcionalidades

* **Múltiplas Branches:** Suporte oficial à branch **Master** (Releases oficiais do GitHub) e à branch **Dev** (Builds diárias integradas à nuvem Scaleway).
* **Formatos Flexíveis:** Compatibilidade com pacotes compactados tradicionais e formato **AppImage**.
* **Atalhos Nativos:** Criação opcional de atalhos personalizados tanto na **Área de Trabalho** quanto no **Menu de Aplicativos** do Ubuntu, com suporte a ícones gráficos.
* **Modo CLI Completo:** Permite a execução direta via linha de comando para automação ou uso em scripts.
* **Diretório Personalizado:** Suporte para definir caminhos de instalação customizados.
* **Sistema de Logs:** Registro automático de auditoria e status no arquivo `flycast_updater.log`.

---

## 📂 Estrutura do Projeto

```text
.
├── launcher_linux.py          # Inicializador interativo e gerenciador de atalhos
├── update_flycast_linux.py    # Motor principal de verificação, download e extração
└── flycast_updater.png        # Ícone gráfico oficial da aplicação
