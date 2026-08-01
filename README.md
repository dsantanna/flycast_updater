# 🌀 Flycast Auto-Updater (v1.0)

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/dsantanna/flycast_updater)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/dsantanna/flycast_updater)
[![Language](https://img.shields.io/badge/language-Python%20%2F%2F%20Multilingual-green.svg)](https://github.com/dsantanna/flycast_updater)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

O **Flycast Auto-Updater** é uma ferramenta inteligente e automatizada desenvolvida para gerenciar o download, a instalação e a atualização contínua do emulador **Flycast** (Sega Dreamcast / Naomi / Atomiswave) no Windows.

---

## ⚠️ Avisos Importantes (Disclaimer)

* **Isenção de Autoria:** O **Flycast Auto-Updater** não é de autoria dos criadores do emulador. Este projeto é apenas um script utilitário que automatiza o processo de download e atualização. **Todos os créditos, direitos autorais e méritos do Flycast pertencem exclusivamente aos seus desenvolvedores e mantenedores oficiais.**
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
* `-path <diretriz>` *(Apenas versão PT)* : Define um diretório de instalação personalizado.

Exemplo:
```cmd
FlycastUpdater.exe -dev
