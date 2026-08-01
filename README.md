# 🌀 Flycast Auto-Updater (v1.0)

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/dsantanna/flycast_updater)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/dsantanna/flycast_updater)
[![Language](https://img.shields.io/badge/language-Python%20%2F%2F%20Multilingual-green.svg)](https://github.com/dsantanna/flycast_updater)

O **Flycast Auto-Updater** é uma ferramenta inteligente e automatizada desenvolvida para gerenciar o download, a instalação e a atualização contínua do emulador **Flycast** (Sega Dreamcast / Naomi / Atomiswave) no Windows.

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

Basta baixar a versão mais atual para uso na aba [Releases](https://github.com/dsantanna/flycast_updater/releases) (`FlycastUpdater.exe`) e executá-la. Na primeira execução, o programa solicitará que você escolha a branch desejada e se deseja criar um atalho na Área de Trabalho.

### ⚙️ Parâmetros de Linha de Comando (CLI)

Você pode executar o atualizador via terminal passando argumentos opcionais:

* `-help`, `-h`, `--help` : Exibe o menu de ajuda e encerra.
* `-dev` : Força a configuração e o download da versão diária (Dev).
* `-master` : Força a configuração e o download da versão estável (Master).
* `-path <diretriz>` *(Apenas versão PT)* : Define um diretório de instalação personalizado.

Exemplo:
```cmd
FlycastUpdater.exe -dev
