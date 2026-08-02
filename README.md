# Flycast Auto-Updater (Linux) - v1.0

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
