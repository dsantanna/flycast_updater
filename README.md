# 🌀 Flycast Updater (v4.0) - Windows

[![Version](https://img.shields.io/badge/version-4.0-blue.svg)](https://github.com/dsantanna/flycast_updater)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/dsantanna/flycast_updater)
[![Language](https://img.shields.io/badge/language-Python%20%2F%2F%20Multilingual-green.svg)](https://github.com/dsantanna/flycast_updater)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

O **Flycast Updater** é uma ferramenta inteligente e automatizada desenvolvida para gerenciar o download, a instalação e a atualização contínua do emulador **Flycast** (Sega Dreamcast / Naomi / Atomiswave) no Windows.[cite: 4]

---
## 🌟 Funcionalidades Principais (v4.0 - Another Day Edition)

- **Internacionalização Global (i18n):** O Flycast Updater agora fala com o mundo![cite: 1] Suporte nativo e instantâneo para os 10 idiomas mais falados (PT-BR, EN-US, ES-ES, FR-FR, DE-DE, ZH-CN, JA-JP, RU-RU, AR-SA, HI-IN).[cite: 1]
- **Assistente Inteligente de BIOS:** Novo motor autônomo que varre, detecta, auto-renomeia arquivos `.bin` incorretos e até extrai as BIOS (`dc_boot.bin` e `dc_flash.bin`) diretamente de pacotes `.zip` para a pasta correta.[cite: 1]
- **Custom Paths Dinâmicos:** Suporte completo à configuração de pastas personalizadas para BIOS, VMU, Save States e Saves de Jogo, com criação física automática de diretórios no Windows e integração total ao arquivo `emu.cfg`.[cite: 1]
- **Restaurador de Backup Avançado:** O descompactador de nuvem agora age com inteligência contextual.[cite: 1] Ao restaurar um backup antigo, ele direciona automaticamente os arquivos do VMU e Mappings para os caminhos personalizados ativos.[cite: 1]
- **Gerenciamento Passivo de Nuvem:** Implementado sistema de limite de armazenamento para os Cloud Saves (1, 3, 5, 10, 15 ou Ilimitado).[cite: 1] O motor agora limpa e deleta automaticamente os backups mais velhos para poupar espaço no Google Drive / OneDrive.[cite: 1]
- **Super Logger Integrado (Aba de Logs):** O motor interno ganhou um sistema de eventos detalhado (Modo Tagarela).[cite: 1] Uma nova aba "Logs" foi adicionada à interface, atualizando em tempo real com todo o fluxo de diagnóstico e auditoria.[cite: 1]
- **UX & UI Design Refinado:** Novo layout adaptativo com a Branch "Dev" priorizada, campos de texto dinâmicos que sugerem as ramificações padrões baseadas no local de instalação e separadores visuais que melhoram a fluidez da interface.[cite: 1]
- **Sincronização de Mappings (Opcional):** Adicionado suporte para incluir o backup dos arquivos de mapeamento de controles (`.cfg`) diretamente nos pacotes salvos na nuvem.[cite: 1]

---
## 🌴 Funcionalidades Principais (v3.1 - Emerald Coast Edition - Bugfix)

- **Modo CLI Persistente (-nogui na UI):** Adicionado novo switch na aba de Nuvem para permitir que o usuário desative permanentemente o ambiente gráfico.[cite: 1]
- **Correção da Autoatualização Gráfica:** Ajustado o encerramento do processo de auto-update utilizando `os._exit(0)`, permitindo que o script `.bat` substitua o executável com sucesso.[cite: 1]
- **Mapeamento Exato da API Gráfica:** Correção definitiva dos índices do parâmetro `pvr.rend` no `emu.cfg` (`0 = OpenGL`, `1 = DirectX 9`, `2 = DirectX 11`, `4 = Vulkan`).[cite: 1]

---
## 🌴 Funcionalidades Principais (v3.0 - Emerald Coast Edition)

- **Hub Completo de Configuração:** Interface gráfica expandida organizada em abas intuitivas (`Nuvem`, `Emulador`, `Vídeo`, `Saves`), centralizando toda a experiência de gerenciamento.[cite: 4]
- **Restaurador de Saves na Nuvem:** Nova aba dedicada a listar e extrair com um clique os arquivos `.zip` de backup armazenados na nuvem (Google Drive/OneDrive), ordenados do mais recente para o mais antigo.[cite: 4]
- **Assistente de BIOS Inteligente:** Detecta automaticamente arquivos de BIOS mal posicionados na raiz e oferece duas soluções automatizadas: movê-los para a pasta `data` ou registrar um caminho personalizado no `emu.cfg`.[cite: 4]
- **Aba de Vídeo e Gráficos Básicos:** Controle direto sobre a API Gráfica (OpenGL, Vulkan, DirectX 9, DirectX 11) com tooltips informativos de vantagens e desvantagens, Resolução Interna, Tela Cheia, Escala Inteira, Interpolação Linear e V-Sync.[cite: 4]
- **Olho Mágico (Toggle de Senha):** Botão interativo para ocultar ou revelar a senha ou Token do RetroAchievements durante a digitação.[cite: 4]
- **Interface Gráfica (GUI) Premium:** Desenvolvida em CustomTkinter, oferecendo uma experiência visual fluida, tema escuro nativo e Tooltips (dicas flutuantes) interativos.[cite: 4]
- **Semáforo Interativo de Status:** Verificação em tempo real e em background alertando se o emulador precisa ser instalado (Vermelho), atualizado (Amarelo) ou se já está pronto para jogar (Verde).[cite: 4]
- **Validação de Nuvem Inteligente:** Detecção dinâmica da instalação do Google Drive e OneDrive na máquina do usuário.[cite: 4] O sistema desabilita botões caso os aplicativos de nuvem não sejam localizados localmente.[cite: 4]
- **Cloud Saves Passivo:** Backup automatizado de saves (VMU/SRAM) detectando e utilizando instâncias locais do Google Drive ou OneDrive, de forma totalmente segura (sem requerer senhas ou credenciais).[cite: 4]
- **Sistema de Rollback Inteligente:** Geração automática de "cápsulas do tempo" locais.[cite: 4] O botão de reversão da interface reage à presença do backup (`flycast_backup.zip`) e se desabilita se não houver um ponto de restauração disponível.[cite: 4]
- **Modo Híbrido (CLI/GUI):** O aplicativo oculta perfeitamente a tela preta ao ser aberto via duplo-clique no Windows, mas retoma o controle nativo do terminal (incluindo o questionário interativo) quando acionado pelo comando `-nogui`.[cite: 4]
- **Trilha de Auditoria Unificada (`flycast_updater.log`):** Sistema de logs detalhado e incremental, rotulado rigorosamente com a versão ativa e parâmetros definidos pelo usuário.[cite: 4]
- **Persistência de Preferências (`config.json`):** Salva automaticamente as escolhas de branch, caminho de instalação, provedor de nuvem e criação de atalhos.[cite: 4]
- **Geração Automatizada de Atalhos:** Criação de atalhos personalizados na Área de Trabalho e de inicialização oculta apontando de maneira robusta para a pasta correta escolhida.[cite: 4]

---
## 🚀 Funcionalidades Principais (v2.0 - Gold Master GUI Edition)

- **Interface Gráfica (GUI) Premium:** Desenvolvida em CustomTkinter, oferecendo uma experiência visual fluida, tema escuro nativo e Tooltips (dicas flutuantes) interativos.[cite: 4]
- **Semáforo Interativo de Status:** Verificação em tempo real e em background alertando se o emulador precisa ser instalado (Vermelho), atualizado (Amarelo) ou se já está pronto para jogar (Verde).[cite: 4]
- **Validação de Nuvem Inteligente:** Detecção dinâmica da instalação do Google Drive e OneDrive na máquina do usuário.[cite: 4] O sistema desabilita botões caso os aplicativos de nuvem não sejam localizados localmente.[cite: 4]
- **Cloud Saves Passivo:** Backup automatizado de saves (VMU/SRAM) detectando e utilizando instâncias locais do Google Drive ou OneDrive, de forma totalmente segura (sem requerer senhas ou credenciais).[cite: 4]
- **Sistema de Rollback Inteligente:** Geração automática de "cápsulas do tempo" locais.[cite: 4] O botão de reversão da interface reage à presença do backup (`flycast_backup.zip`) e se desabilita se não houver um ponto de restauração disponível.[cite: 4]
- **Modo Híbrido (CLI/GUI):** O aplicativo oculta perfeitamente a tela preta ao ser aberto via duplo-clique no Windows, mas retoma o controle nativo do terminal (incluindo o questionário interativo) quando acionado pelo comando `-nogui`.[cite: 4]
- **Trilha de Auditoria Unificada (`flycast_updater.log`):** Sistema de logs detalhado e incremental, rotulado rigorosamente com a versão ativa e parâmetros definidos pelo usuário.[cite: 4]
- **Verificação Passiva de BIOS:** Inspeção local e estritamente educacional para alertar o usuário através de um semáforo visual na interface (🟢/🟡/🔴) caso os arquivos de sistema (`dc_boot.bin`, `dc_flash.bin`) estejam incorretos ou ausentes.[cite: 4]
- **Persistência de Preferências (`config.json`):** Salva automaticamente as escolhas de branch, caminho de instalação, provedor de nuvem e criação de atalhos.[cite: 4]
- **Geração Automatizada de Atalhos:** Criação de atalhos personalizados na Área de Trabalho e de inicialização oculta apontando de maneira robusta para a pasta correta escolhida.[cite: 4]

---
## 🚀 Funcionalidades Principais (v1.2 - Cloud Save Edition)

- **Cloud Saves Passivo:** Backup automatizado de saves (VMU/SRAM) detectando e utilizando instâncias locais do Google Drive ou OneDrive, de forma totalmente segura (sem requerer senhas ou credenciais).[cite: 4]
- **Sistema de Rollback:** Geração automática de "cápsulas do tempo" locais antes de cada extração, permitindo reverter o emulador para a versão anterior caso uma build diária apresente instabilidade.[cite: 4]
- **Modo Silencioso (Background):** Capacidade de rodar o atualizador de forma invisível, com integração nativa à pasta de Inicialização (Startup) do Windows.[cite: 4]
- **Arquitetura Inteligente (Launcher + Motor):** Separação clara entre o cérebro de controle (`launcher.py`) e o motor de download (`update_flycast.py`), agora totalmente sincronizados.[cite: 4]
- **Auto-Atualização do Launcher:** Verifica automaticamente na API do GitHub se há uma nova versão do próprio atualizador, baixando e aplicando atualizações de forma transparente.[cite: 4]
- **Barra de Progresso Visual em Tempo Real:** Monitoramento do download via blocos de bytes, exibindo a porcentagem exata e o volume transferido em megabytes (`MB`).[cite: 4]
- **Trilha de Auditoria Unificada (`flycast_updater.log`):** Sistema de logs detalhado e incremental, rotulado rigorosamente com a versão ativa e parâmetros definidos pelo usuário.[cite: 4]
- **Verificação Passiva de BIOS:** Inspeção local e estritamente educacional para alertar o usuário caso os arquivos fundamentais de sistema (`dc_boot.bin`, `dc_flash.bin`) estejam ausentes.[cite: 4]
- **Persistência de Preferências (`config.json`):** Salva automaticamente as escolhas de branch, caminho de instalação, provedor de nuvem e criação de atalhos.[cite: 4]
- **Geração Automatizada de Atalhos:** Criação de atalhos personalizados na Área de Trabalho do Windows apontando para o binário do Flycast com o ícone oficial do emulador.[cite: 4]

---

## ⚠️ Avisos Importantes (Disclaimer)

* **Isenção de Autoria:** O **Flycast Updater** não é de autoria dos criadores do emulador.[cite: 4] Este projeto é apenas um script utilitário que automatiza o processo de download e atualização.[cite: 4] **Todos os créditos, direitos autorais e méritos do Flycast pertencem exclusivamente aos seus desenvolvedores e mantenedores oficiais.**[cite: 4]
* **Ausência de BIOS e ROMs:** **Nenhum arquivo de BIOS, firmware ou ROM/ISO de jogos** é fornecido, hospedado ou distribuído através deste repositório.[cite: 4]
* **Uso Legal:** Para utilizar o emulador Flycast, o usuário deve possuir os arquivos de BIOS extraídos de seu próprio hardware e ter os **jogos originais** legalmente adquiridos.[cite: 4]

---

## 🌟 Principais Recursos

* **Duas Branches Suportadas:**[cite: 4]
  * `Master`: Versão estável oficial (via GitHub Releases).[cite: 4]
  * `Dev`: Versão de desenvolvimento / builds diárias da nuvem (via S3 Buckets e commits do GitHub).[cite: 4]
* **Auto-Cópia Inteligente:** O script/executável gerencia sua própria cópia para o diretório de destino do emulador após o usuário selecionar o caminho na interface gráfica.[cite: 4]
* **Atalhos Automatizados:** Criação opcional de atalhos na Área de Trabalho com o ícone oficial customizado de atualização.[cite: 4]
* **Sistema de Auditoria por Logs:** Mantém um histórico incremental de execuções (`flycast_updater.log`) registrando data, hora e a versão exata do script.[cite: 4]

---

## 🚀 Como Usar

Para a grande maioria dos usuários, basta baixar a versão pronta para uso:[cite: 4]
1. Acesse a aba [Releases](https://github.com/dsantanna/flycast_updater/releases).[cite: 4]
2. Baixe o arquivo **`FlycastUpdater.exe`**.[cite: 4]
3. Execute-o e navegue pela Interface Gráfica, escolhendo a pasta de instalação, a versão e os parâmetros de nuvem.[cite: 4] Tudo muito simples e com dicas ao passar o mouse (Tooltips).[cite: 4]

---

## 🛡️ Solução de Problemas (FAQ)

* **O Windows Defender / SmartScreen bloqueou o executável ao abrir:**[cite: 4]
  * Como o arquivo `.exe` foi compilado de forma independente via PyInstaller (e não possui uma assinatura digital comercial paga), o Windows pode exibir uma janela de aviso (*"O Windows protegeu o seu computador"*).[cite: 4]
  * **Como resolver:** Basta clicar em **"Mais informações"** e, em seguida, no botão **"Executar assim mesmo"**.[cite: 4] O programa é totalmente seguro e de código aberto.[cite: 4]

---

## ⚙️ Parâmetros de Linha de Comando (CLI)

Você pode executar o atualizador via terminal passando argumentos opcionais:[cite: 4]

* `-nogui` : Executa em modo texto (Terminal Clássico).[cite: 4]
* `-help`, `-h`, `--help` : Exibe o menu de ajuda e encerra.[cite: 4]
* `-dev` : Força a configuração e o download da versão diária (Dev).[cite: 4]
* `-master` : Força a configuração e o download da versão estável (Master).[cite: 4]
* `-rollback` : Restaura o último backup funcional do emulador.[cite: 4]
* `-silent` : Executa o atualizador em segundo plano (invisível) sem exibir o terminal.[cite: 4]
* `-backup` : Executa apenas a rotina de backup dos saves na nuvem configurada e encerra.[cite: 4]
* `-gdrive` / `-onedrive` : Força e ativa o uso do Google Drive ou OneDrive para backup dos saves.[cite: 4]
* `-reset` : Ignora o arquivo `config.json` salvo e exibe o menu interativo de reconfiguração inicial na CLI.[cite: 4]

Exemplo:[cite: 4]
```cmd
FlycastUpdater.exe -dev -silent -gdrive