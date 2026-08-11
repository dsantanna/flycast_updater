# 🌀 Flycast Updater (v5.1) - Windows

[![Version](https://img.shields.io/badge/version-5.1-blue.svg)](https://github.com/dsantanna/flycast_updater)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/dsantanna/flycast_updater)[cite: 9]
[![Language](https://img.shields.io/badge/language-Python%20%2F%2F%20Multilingual%20(20%20Langs)-green.svg)](https://github.com/dsantanna/flycast_updater)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)[cite: 9]

O **Flycast Updater** transcendeu sua função original. Hoje ele atua como o gestor, integrador em nuvem e a interface gráfica completa (Frontend) para revolucionar a sua experiência de emulação no **Flycast** (Sega Dreamcast / Naomi / Atomiswave) no Windows[cite: 9].

---
## 🎬 Funcionalidades Principais (v5.1 - Official API & Director's Cut)

- **RetroAchievements via API Oficial:** Conexão direta via REST API de forma segura e oficial, trazendo estatísticas em tempo real sem bloqueios de firewall[cite: 9].
- **Banco de Dados `RAlocal.db`:** Gerenciamento local inteligente que armazena o histórico completo de conquistas e pontuações normais/hardcore de forma estruturada[cite: 9].
- **A Platina da SEGA:** O motor detecta o status de "Mastered" (100%) em um jogo e exibe uma recompensa visual exclusiva "🌀 PLATINA" em azul SEGA nos seus cards.
- **Placar de Pontuação Dinâmico:** Os cards de jogos exibem de forma clara a pontuação exata obtida em relação ao total possível (ex: `7/401 pts`), adaptando-se automaticamente ao Modo Hardcore[cite: 9].
- **Suporte Expandido a 10 Idiomas:** Arquitetura limpa com dicionário externo (`idiomas.py`) contemplando 10 localidades globais[cite: 9].
- **Lançador de Jogos Rápido (Frontend):** Nova aba que exibe sua biblioteca de jogos em um elegante design de capas (cards), permitindo iniciar a emulação com apenas um duplo clique[cite: 9].
- **Barra de Pesquisa e Favoritos:** Filtre sua biblioteca instantaneamente enquanto digita ou marque títulos com a "⭐" para criar sua coleção personalizada de favoritos.
- **Auto-Scraper Inteligente (Multithread):** Integração livre com o repositório Libretro. Capas faltantes são procuradas e baixadas de forma paralela e ultrarrápida, sem travar a interface[cite: 9].
- **Detecção de Múltiplos Discos e Regiões:** O motor interno une jogos multi-CD (como Shenmue) e funde ROMs duplicadas de regiões (USA/Japan) sob uma única capa, fornecendo um popup para a seleção no momento do carregamento[cite: 9].
- **Playtime Tracker e Dashboard:** O seu tempo de emulação agora é valioso! O sistema cronometra, unifica estatísticas em jogos de multi-CD e exibe seu progresso total de vida gamer num Dashboard interativo no topo da tela[cite: 9].
- **Galeria Visual de Save States:** A janela de detalhes agora captura automaticamente as fotos tiradas pelo emulador e gera um mosaico dos seus saves com data, hora e peso em KB.
- **Diário de Bordo:** Roteirize seus vídeos, anote timestamps ou salve códigos num bloco de notas interno dedicado a cada jogo, salvando nativamente tudo na sua base de dados.
- **Backup Total na Nuvem:** Proteja mais do que apenas saves! Um clique agora engloba seus arquivos `emu.cfg`, `config.json` e o `RAlocal.db` com extração e recarregamento automático no ambiente.
- **Injeção de Perfis de Controle (Auto-Mapping):** Configure o seu Joystick em um clique. Aba dedicada que injeta arquivos `.cfg` otimizados para controles do Xbox, PlayStation e 8BitDo direto no emulador[cite: 9].
- **Modo Criador de Conteúdo / Streamer (OBS Ready):** Gere *widgets* de chroma key dinâmicos com sua arte de capa, integre textos do `Now Playing` direto no OBS Studio e oculte pastas sensíveis com o novo motor Anti-Leak Holográfico[cite: 9].
- **Clean Desktop (Auto-Ocultar):** A interface some silenciosamente da Área de Trabalho ao carregar um jogo, retornando magicamente assim que a gameplay for encerrada.

---
## 🌟 Funcionalidades Anteriores (Destaques)

- **Detecção de Hardware & Drivers:** Identifica sua placa de vídeo e direciona para os drivers oficiais compatíveis[cite: 9].
- **Tradução em Tempo Real (i18n):** Mude instantaneamente entre 20 idiomas sem reiniciar[cite: 9].
- **Assistente Inteligente de BIOS:** Varre, detecta, auto-renomeia arquivos `.bin` incorretos e extrai as BIOS diretamente de pacotes `.zip`[cite: 9].
- **Custom Paths Dinâmicos:** Direcione a criação e leitura de BIOS, VMU, Save States e Saves para as pastas que você desejar[cite: 9].
- **Restaurador de Backup Avançado (Cloud Saves):** Descompactador contextual que rastreia limites de retenção e restaura arquivos mapeando os diretórios dinamicamente para o Google Drive ou OneDrive[cite: 9].
- **Super Logger Integrado:** Aba de auditoria em tempo real detalhando todas as injeções e transações mecânicas[cite: 9].
- **Semáforo Interativo de Status:** Verificação visual para status de updates das "Daily Builds" ou da branch "Master"[cite: 9].

---

## ⚠️ Avisos Importantes (Disclaimer)

* **Isenção de Autoria:** O **Flycast Updater** não é de autoria dos criadores do emulador[cite: 9]. Todos os créditos pertencem aos desenvolvedores oficiais do Flycast[cite: 9].
* **Ausência de BIOS e ROMs:** Nenhum arquivo de BIOS, firmware ou ROM/ISO é fornecido ou distribuído[cite: 9].
* **Dependência Visual:** Para utilizar o Mini-Frontend com capas, instale a biblioteca de imagens: `pip install Pillow` via terminal[cite: 9].

---

## 🚀 Como Usar

1. Acesse a aba [Releases](https://github.com/dsantanna/flycast_updater/releases)[cite: 9].
2. Baixe o arquivo **`FlycastUpdater.exe`**[cite: 9].
3. Execute-o e navegue pela Interface Gráfica[cite: 9].

---

## ⚙️ Parâmetros de Linha de Comando (CLI)

* `-nogui` : Executa em modo texto[cite: 9].
* `-dev` / `-master` : Força a versão de desenvolvimento ou estável[cite: 9].
* `-rollback` : Restaura o último backup funcional[cite: 9].
* `-silent` : Executa em segundo plano[cite: 9].
* `-backup` : Executa apenas o backup na nuvem[cite: 9].
* `-reset` : Refaz a configuração inicial[cite: 9].
