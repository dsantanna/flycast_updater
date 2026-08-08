import os
import sys
import json
import subprocess
import time
import urllib.request
import urllib.parse
import datetime
import threading
import configparser
import zipfile
import shutil
import tkinter as tk 
import tkinter.messagebox as mb
import webbrowser 

try:
    import cloud_saves
except ImportError:
    cloud_saves = None

# ==========================================
# Flycast Updater - Launcher v4.1 (Another Day Edition)
# Desenvolvido por DaniboySan & Geminix
# ==========================================

VERSION = "4.1"
CONFIG_FILE = "config.json"
REPO_UPDATER = "dsantanna/flycast_updater"

# ==========================================
# DICIONÁRIO GLOBAL DE INTERNACIONALIZAÇÃO (i18n) - v4.1 FULL
# ==========================================
TRANSLATIONS = {
    "pt": {
        "title_sub": "Gerenciador de Atualizações, Nuvem e Configurações", "btn_help": "❔ Sobre", "tab_cloud": "🚀 Atualização", "tab_emu": "⚙️ Emulador", "tab_vid": "🖥️ Vídeo", "tab_saves": "🔄 Saves", "tab_logs": "📝 Logs",
        "lbl_path": "Local de Instalação do Emulador:", "btn_browse": "Procurar...", "lbl_branch": "Versão do Emulador:",
        "rb_master_desc": "Lançamentos oficiais e\nestáveis do emulador.", "rb_dev_desc": "Builds diárias da nuvem.\nNovos recursos e correções.",
        "lbl_cloud": "Sincronização de Saves na Nuvem:", "rb_none": "Nenhum", "sw_desk": "Criar Atalho no Desktop",
        "sw_start": "Iniciar com o Windows (Modo Silencioso)", "sw_nogui": "Desabilitar Ambiente Gráfico (-nogui)", "sw_map": "Backup de Controles / Mappings (Opcional)",
        "lbl_backup_limit": "Limite de Backups:", "limit_unlimited": "Ilimitado",
        "btn_reconfig": "⚙️ Reconfigurar Emulador e ROMs", "lbl_roms": "Pasta de Jogos (ROMs / ISOs / GDI):", "lbl_ra": "RetroAchievements & Conquistas:",
        "sw_custom_paths": "Usar Locais Personalizados (Paths)", "lbl_bios_path": "Pastas da BIOS:", "lbl_vmu_path": "Pasta do VMU:", "lbl_state_path": "Pastas de Save State:", "lbl_save_path": "Pasta de Save do Jogo:",
        "sw_ra": "Ativar RetroAchievements no Emulador", "lbl_user": "Usuário:", "lbl_pass": "Senha / Token:", "sw_hard": "Modo Hardcore (Desativa Save States e Trapaças)",
        "lbl_qol": "Melhorias e Qualidade de Vida (QoL):", "sw_vmu": "VMU Individual por Jogo", "sw_box": "Baixar Capas Automático",
        "sw_vga": "Otimizar Gráficos (VGA)", "sw_disc": "Status no Discord", "sw_osd": "Mostrar VMU na Tela", "sw_vmu_snd": "Ativar Sons do VMU",
        "btn_save_emu": "💾 Salvar Configurações do Emulador", "lbl_vid_title": "Configurações de Vídeo (Básicas)",
        "lbl_vid_warn": "⚠️ Aviso: Estas são configurações básicas do emulador.\nVerifique o menu do próprio Flycast para opções avançadas.",
        "lbl_api": "Gráficos API:", "lbl_res": "Resolução Interna:", "sw_full": "Tela Cheia", "sw_int": "Escala Inteira",
        "sw_lin": "Interpolação Linear", "sw_vsync": "Sincronização Vertical (V-Sync)", "btn_save_vid": "💾 Salvar Configurações de Vídeo",
        "lbl_saves_title": "Restaurar Backups da Nuvem", "lbl_saves_desc": "Selecione um arquivo .zip de backup do seu Google Drive ou OneDrive\npara extrair de volta na pasta do emulador.",
        "btn_search_saves": "🔄 Buscar Backups", "combo_saves_def": "Clique em Buscar Backups...", "btn_extract": "📥 Extrair e Restaurar Saves",
        "lbl_logs_title": "Auditoria e Diagnóstico (Logs)", "btn_log_refresh": "🔄 Atualizar", "btn_log_copy": "📋 Copiar", "btn_log_clear": "🗑️ Limpar",
        "log_not_found": "Nenhum arquivo de log encontrado.", "btn_verify": "🚀 VERIFICANDO...", "btn_rollback": "↩️ REVERTER",
        "btn_play": "JOGAR", "btn_update_act": "ATUALIZAR", "btn_install_act": "INSTALAR", "btn_starting": "INICIANDO...", "btn_processing": "PROCESSANDO...", "btn_reverting": "REVERTENDO...",
        "emu_status_checking": "Emulador: 🔵 Verificando versão na nuvem...", "emu_status_updated": "Emulador: 🟢 Atualizado", "emu_status_outdated": "Emulador: 🟡 Desatualizado", 
        "emu_status_offline": "Emulador: 🟡 Sem internet", "emu_status_missing": "Emulador: 🔴 Ausente", "emu_status_error": "Emulador: 🔴 Erro", 
        "bios_ok": "BIOS: 🟢 OK", "bios_custom": "BIOS: 🟢 OK (Custom)", "bios_wrong": "BIOS: 🟡 Local incorreto", "bios_missing": "BIOS: 🔴 Ausente", "bios_error": "BIOS: 🔴 Erro",
        "msg_success": "Operação realizada com sucesso!", "msg_error": "Erro durante a operação.",
        "msg_updater_update": "Uma nova versão do Flycast Updater foi detectada!\nO programa será atualizado junto com o emulador.",
        "tt_help": "Clique aqui para ler sobre o aplicativo e instruções.", "tt_bios": "Verifica os arquivos dc_boot.bin e dc_flash.bin.", "tt_path": "Este é o local onde o Flycast está (ou será) instalado.",
        "tt_master": "Estável. Atualiza apenas quando há lançamentos fechados.", "tt_dev": "Baixa as modificações diárias do criador.", "tt_nogui": "Abre o app em modo texto/CLI nas próximas vezes.",
        "tt_reconfig": "Abre a aba para alterar pastas de ROMs e credenciais.", "tt_opengl": "API clássica e madura. Ideal para PCs antigos.", "tt_vulkan": "API moderna. Altíssimo desempenho e baixo uso de CPU.", 
        "tt_dx9": "Legado do Windows. Útil apenas se o PC for extremamente antigo.", "tt_dx11": "Ótima alternativa ao Vulkan no Windows.", "tt_custom_paths": "Permite definir pastas separadas para BIOS, Saves e States.",
        "msg_bios_missing": "Os seguintes arquivos de BIOS estão faltando:\n- {files}\n\nDeseja procurá-los no seu computador (ou selecionar um .zip)?",
        "title_bios_missing": "BIOS Ausente",
        "msg_bios_partial": "Arquivo copiado com sucesso.\n\nAinda falta o arquivo:\n- {missing}\n\nDeseja procurá-lo agora?",
        "title_bios_partial": "BIOS Incompleta",
        "msg_bios_zip_success": "Arquivos de BIOS extraídos e instalados com sucesso do ZIP!",
        "msg_bios_bin_success": "Todos os arquivos de BIOS foram instalados com sucesso!",
        "msg_bios_unsupported": "Formato de arquivo não suportado."
    },
    "en": {
        "title_sub": "Update, Cloud and Configuration Manager", "btn_help": "❔ About", "tab_cloud": "🚀 Update", "tab_emu": "⚙️ Emulator", "tab_vid": "🖥️ Video", "tab_saves": "🔄 Saves", "tab_logs": "📝 Logs",
        "lbl_path": "Emulator Install Path:", "btn_browse": "Browse...", "lbl_branch": "Emulator Version:",
        "rb_master_desc": "Official and stable\nemulator releases.", "rb_dev_desc": "Daily cloud builds.\nNew features and fixes.",
        "lbl_cloud": "Cloud Save Synchronization:", "rb_none": "None", "sw_desk": "Create Desktop Shortcut",
        "sw_start": "Start with Windows (Silent Mode)", "sw_nogui": "Disable GUI (-nogui)", "sw_map": "Backup Controllers / Mappings (Optional)",
        "lbl_backup_limit": "Backup Limit:", "limit_unlimited": "Unlimited",
        "btn_reconfig": "⚙️ Reconfigure Emulator & ROMs", "lbl_roms": "Games Folder (ROMs / ISOs):", "lbl_ra": "RetroAchievements:",
        "sw_custom_paths": "Use Custom Paths", "lbl_bios_path": "BIOS Folders:", "lbl_vmu_path": "VMU Folder:", "lbl_state_path": "Save State Folders:", "lbl_save_path": "Game Save Folder:",
        "sw_ra": "Enable RetroAchievements", "lbl_user": "Username:", "lbl_pass": "Password / Token:", "sw_hard": "Hardcore Mode (Disables Save States)",
        "lbl_qol": "Quality of Life (QoL) Tweaks:", "sw_vmu": "Per-Game VMU", "sw_box": "Auto Download Boxart",
        "sw_vga": "Optimize Graphics (VGA)", "sw_disc": "Discord Rich Presence", "sw_osd": "Show VMU on Screen", "sw_vmu_snd": "Enable VMU Sounds",
        "btn_save_emu": "💾 Save Emulator Settings", "lbl_vid_title": "Video Settings (Basic)",
        "lbl_vid_warn": "⚠️ Warning: These are basic emulator settings.\nCheck the Flycast menu for advanced visual options.",
        "lbl_api": "Graphics API:", "lbl_res": "Internal Resolution:", "sw_full": "Fullscreen", "sw_int": "Integer Scaling",
        "sw_lin": "Linear Interpolation", "sw_vsync": "Vertical Sync (V-Sync)", "btn_save_vid": "💾 Save Video Settings",
        "lbl_saves_title": "Restore Cloud Backups", "lbl_saves_desc": "Select a backup .zip file from your Google Drive or OneDrive\nto extract it back into the emulator folder.",
        "btn_search_saves": "🔄 Fetch Backups", "combo_saves_def": "Click Fetch Backups...", "btn_extract": "📥 Extract and Restore Saves",
        "lbl_logs_title": "Audit and Diagnostics (Logs)", "btn_log_refresh": "🔄 Refresh", "btn_log_copy": "📋 Copy", "btn_log_clear": "🗑️ Clear",
        "log_not_found": "No log file found.", "btn_verify": "🚀 CHECKING...", "btn_rollback": "↩️ ROLLBACK",
        "btn_play": "PLAY", "btn_update_act": "UPDATE", "btn_install_act": "INSTALL", "btn_starting": "STARTING...", "btn_processing": "PROCESSING...", "btn_reverting": "ROLLING BACK...",
        "emu_status_checking": "Emulator: 🔵 Checking cloud version...", "emu_status_updated": "Emulator: 🟢 Up to date", "emu_status_outdated": "Emulator: 🟡 Outdated",
        "emu_status_offline": "Emulator: 🟡 Offline", "emu_status_missing": "Emulator: 🔴 Missing", "emu_status_error": "Emulator: 🔴 Error",
        "bios_ok": "BIOS: 🟢 OK", "bios_custom": "BIOS: 🟢 OK (Custom)", "bios_wrong": "BIOS: 🟡 Incorrect path", "bios_missing": "BIOS: 🔴 Missing", "bios_error": "BIOS: 🔴 Error",
        "msg_success": "Operation completed successfully!", "msg_error": "Error during the operation.",
        "msg_updater_update": "A new version of Flycast Updater has been detected!\nThe program will be updated along with the emulator.",
        "tt_help": "Click here to read more about the app.", "tt_bios": "Checks for dc_boot.bin and dc_flash.bin.", "tt_path": "This is where Flycast is (or will be) installed.",
        "tt_master": "Stable. Updates only when there are official releases.", "tt_dev": "Downloads daily modifications from the creator.", "tt_nogui": "Opens directly in text/CLI mode next time.",
        "tt_reconfig": "Opens the tab to change ROM folders and credentials.", "tt_opengl": "Classic API. Very compatible.", "tt_vulkan": "Modern API. Extremely high performance.",
        "tt_dx9": "Windows legacy. For extremely old PCs.", "tt_dx11": "Great alternative to Vulkan on Windows.", "tt_custom_paths": "Allows setting separate folders for BIOS, Saves, and States.",
        "msg_bios_missing": "The following BIOS files are missing:\n- {files}\n\nDo you want to locate them on your computer (or select a .zip)?",
        "title_bios_missing": "Missing BIOS",
        "msg_bios_partial": "File copied successfully.\n\nThe following file is still missing:\n- {missing}\n\nDeseja procurá-lo agora?",
        "title_bios_partial": "Incomplete BIOS",
        "msg_bios_zip_success": "BIOS successfully extracted and installed from ZIP!",
        "msg_bios_bin_success": "All BIOS files installed successfully!",
        "msg_bios_unsupported": "Unsupported file format."
    },
    "es": {
        "title_sub": "Gestor de Actualizaciones, Nube y Configuración", "btn_help": "❔ Acerca de", "tab_cloud": "🚀 Actualizar", "tab_emu": "⚙️ Emulador", "tab_vid": "🖥️ Video", "tab_saves": "🔄 Saves", "tab_logs": "📝 Logs",
        "lbl_path": "Ruta de instalación:", "btn_browse": "Explorar...", "lbl_branch": "Versión del Emulador:",
        "rb_master_desc": "Versiones oficiales y estables.", "rb_dev_desc": "Builds diarios de la nube.",
        "lbl_cloud": "Sincronización en la Nube:", "rb_none": "Ninguno", "sw_desk": "Crear Acceso Directo",
        "sw_start": "Iniciar con Windows (Silencioso)", "sw_nogui": "Desactivar Interfaz (-nogui)", "sw_map": "Respaldo de Controles (Opcional)",
        "lbl_backup_limit": "Límite de Respaldos:", "limit_unlimited": "Ilimitado",
        "btn_reconfig": "⚙️ Reconfigurar Emulador y ROMs", "lbl_roms": "Carpeta de Juegos (ROMs/ISOs):", "lbl_ra": "RetroAchievements:",
        "sw_custom_paths": "Usar Rutas Personalizadas", "lbl_bios_path": "Carpetas de BIOS:", "lbl_vmu_path": "Carpeta de VMU:", "lbl_state_path": "Carpetas de Save State:", "lbl_save_path": "Carpeta de Save del Juego:",
        "sw_ra": "Activar RetroAchievements", "lbl_user": "Usuario:", "lbl_pass": "Contraseña / Token:", "sw_hard": "Modo Hardcore",
        "lbl_qol": "Mejoras de Calidad de Vida (QoL):", "sw_vmu": "VMU Individual por Juego", "sw_box": "Descargar Carátulas",
        "sw_vga": "Optimizar Gráficos (VGA)", "sw_disc": "Estado en Discord", "sw_osd": "Mostrar VMU en Pantalla", "sw_vmu_snd": "Activar Sonidos de VMU",
        "btn_save_emu": "💾 Guardar Configuración", "lbl_vid_title": "Configuración de Video",
        "lbl_vid_warn": "⚠️ Advertencia: Configuraciones básicas.\nConsulta el menú de Flycast para más opciones.",
        "lbl_api": "API Gráfica:", "lbl_res": "Resolución Interna:", "sw_full": "Pantalla Completa", "sw_int": "Escala Entera",
        "sw_lin": "Interpolación Lineal", "sw_vsync": "Sincronización Vertical (V-Sync)", "btn_save_vid": "💾 Guardar Configuración de Video",
        "lbl_saves_title": "Restaurar Copias de Seguridad", "lbl_saves_desc": "Selecciona un archivo .zip de tu nube para extraerlo.",
        "btn_search_saves": "🔄 Buscar Respaldos", "combo_saves_def": "Haz clic en Buscar Respaldos...", "btn_extract": "📥 Extraer y Restaurar Saves",
        "lbl_logs_title": "Auditoría y Diagnóstico (Logs)", "btn_log_refresh": "🔄 Actualizar", "btn_log_copy": "📋 Copiar", "btn_log_clear": "🗑️ Borrar",
        "log_not_found": "No se encontró archivo de log.", "btn_verify": "🚀 VERIFICANDO...", "btn_rollback": "↩️ RESTAURAR",
        "btn_play": "JUGAR", "btn_update_act": "ACTUALIZAR", "btn_install_act": "INSTALAR", "btn_starting": "INICIANDO...", "btn_processing": "PROCESANDO...", "btn_reverting": "RESTAURANDO...",
        "emu_status_checking": "Emulador: 🔵 Comprobando nube...", "emu_status_updated": "Emulador: 🟢 Actualizado", "emu_status_outdated": "Emulador: 🟡 Desactualizado",
        "emu_status_offline": "Emulador: 🟡 Sin internet", "emu_status_missing": "Emulador: 🔴 Falta Emulador", "emu_status_error": "Emulador: 🔴 Error",
        "bios_ok": "BIOS: 🟢 OK", "bios_custom": "BIOS: 🟢 OK (Custom)", "bios_wrong": "BIOS: 🟡 Ruta incorrecta", "bios_missing": "BIOS: 🔴 Falta BIOS", "bios_error": "BIOS: 🔴 Error",
        "msg_success": "¡Operación completada con éxito!", "msg_error": "Error durante la operación.",
        "msg_updater_update": "¡Se ha detectado una nueva versión de Flycast Updater!\nEl programa se actualizará junto con el emulador.",
        "tt_help": "Haz clic aquí para leer sobre la aplicación.", "tt_bios": "Verifica los archivos de BIOS.", "tt_path": "Aquí se instalará Flycast.",
        "tt_master": "Estable. Solo lanzamientos oficiales.", "tt_dev": "Descarga builds diarios.", "tt_nogui": "Abre en modo consola (CLI).",
        "tt_reconfig": "Abre la pestaña de ROMs.", "tt_opengl": "API clásica. Ideal para PCs antiguos.", "tt_vulkan": "API moderna. Máximo rendimiento.",
        "tt_dx9": "Para PCs con Windows muy antiguos.", "tt_dx11": "Excelente alternativa a Vulkan en Windows.", "tt_custom_paths": "Permite definir carpetas separadas para BIOS, Saves y States.",
        "msg_bios_missing": "Faltan los siguientes archivos de BIOS:\n- {files}\n\n¿Deseas buscarlos en tu computadora (o seleccionar un .zip)?",
        "title_bios_missing": "BIOS Faltante",
        "msg_bios_partial": "Archivo copiado con éxito.\n\nAún falta el archivo:\n- {missing}\n\n¿Deseas buscarlo ahora?",
        "title_bios_partial": "BIOS Incompleta",
        "msg_bios_zip_success": "¡BIOS extraída e instalada con éxito del archivo ZIP!",
        "msg_bios_bin_success": "¡Archivos de BIOS instalados con éxito!",
        "msg_bios_unsupported": "Formato de archivo no suportado."
    },
    "fr": {
        "title_sub": "Gestionnaire de Mises à jour, Cloud et Config", "btn_help": "❔ À propos", "tab_cloud": "🚀 M. à jour", "tab_emu": "⚙️ Émulateur", "tab_vid": "🖥️ Vidéo", "tab_saves": "🔄 Saves", "tab_logs": "📝 Logs",
        "lbl_path": "Chemin d'installation:", "btn_browse": "Parcourir...", "lbl_branch": "Version de l'Émulateur:",
        "rb_master_desc": "Versions officielles et stables.", "rb_dev_desc": "Builds cloud quotidiens.",
        "lbl_cloud": "Synchronisation Cloud:", "rb_none": "Aucun", "sw_desk": "Créer un raccourci bureau",
        "sw_start": "Démarrer avec Windows (Silencieux)", "sw_nogui": "Désactiver l'interface (-nogui)", "sw_map": "Sauvegarde des contrôles",
        "lbl_backup_limit": "Limite de Sauvegardes:", "limit_unlimited": "Illimité",
        "btn_reconfig": "⚙️ Reconfigurer Émulateur et ROMs", "lbl_roms": "Dossier de Jeux (ROMs):", "lbl_ra": "RetroAchievements:",
        "sw_custom_paths": "Utiliser des chemins personnalisés", "lbl_bios_path": "Dossiers BIOS:", "lbl_vmu_path": "Dossier VMU:", "lbl_state_path": "Dossiers Save State:", "lbl_save_path": "Dossier Save de Jeu:",
        "sw_ra": "Activer RetroAchievements", "lbl_user": "Utilisateur:", "lbl_pass": "Mot de passe / Token:", "sw_hard": "Mode Hardcore",
        "lbl_qol": "Améliorations de qualité de vie:", "sw_vmu": "VMU par Jeu", "sw_box": "Télécharger Jaquettes",
        "sw_vga": "Optimiser Graphiques (VGA)", "sw_disc": "Statut Discord", "sw_osd": "Afficher VMU à l'écran", "sw_vmu_snd": "Sons VMU",
        "btn_save_emu": "💾 Enregistrer Configuration", "lbl_vid_title": "Paramètres Vidéo",
        "lbl_vid_warn": "⚠️ Avertissement: Paramètres de base.", "lbl_api": "API Graphique:", "lbl_res": "Résolution Interne:",
        "sw_full": "Plein écran", "sw_int": "Mise à l'échelle entière", "sw_lin": "Interpolation linéaire", "sw_vsync": "V-Sync",
        "btn_save_vid": "💾 Enregistrer Vidéo", "lbl_saves_title": "Restaurer Sauvegardes Cloud", "lbl_saves_desc": "Sélectionnez un .zip de sauvegarde.",
        "btn_search_saves": "🔄 Chercher", "combo_saves_def": "Cliquez pour chercher...", "btn_extract": "📥 Extraire",
        "lbl_logs_title": "Journaux (Logs)", "btn_log_refresh": "🔄 Actualiser", "btn_log_copy": "📋 Copier", "btn_log_clear": "🗑️ Effacer",
        "log_not_found": "Aucun log trouvé.", "btn_verify": "🚀 VÉRIFICATION...", "btn_rollback": "↩️ RETOUR",
        "btn_play": "JOUER", "btn_update_act": "METTRE À JOUR", "btn_install_act": "INSTALLER", "btn_starting": "DÉMARRAGE...",
        "btn_processing": "TRAITEMENT...", "btn_reverting": "RESTAURATION...", "emu_status_checking": "Émulateur: 🔵 Vérification...",
        "emu_status_updated": "Émulateur: 🟢 À jour", "emu_status_outdated": "Émulateur: 🟡 Obsolète", "emu_status_offline": "Émulateur: 🟡 Hors ligne",
        "emu_status_missing": "Émulateur: 🔴 Absent", "emu_status_error": "Émulateur: 🔴 Erreur", "bios_ok": "BIOS: 🟢 OK",
        "bios_custom": "BIOS: 🟢 OK (Custom)", "bios_wrong": "BIOS: 🟡 Mauvais chemin", "bios_missing": "BIOS: 🔴 Manquant", "bios_error": "BIOS: 🔴 Erreur",
        "msg_success": "Opération réussie !", "msg_error": "Erreur pendant l'opération.",
        "msg_updater_update": "Une nouvelle version de Flycast Updater a été détectée !\nLe programme sera mis à jour en même temps que l'émulateur.",
        "tt_help": "Aide", "tt_bios": "Vérifie les BIOS.", "tt_path": "Chemin d'installation", "tt_master": "Stable", "tt_dev": "Dev",
        "tt_nogui": "Mode CLI", "tt_reconfig": "Reconfigurer", "tt_opengl": "OpenGL", "tt_vulkan": "Vulkan", "tt_dx9": "DX9", "tt_dx11": "DX11",
        "tt_custom_paths": "Chemins personnalisés", "msg_bios_missing": "Fichiers BIOS manquants:\n- {files}", "title_bios_missing": "BIOS Manquant",
        "msg_bios_partial": "Fichier copié. Manque:\n- {missing}", "title_bios_partial": "BIOS Incomplet", "msg_bios_zip_success": "BIOS extrait du ZIP !",
        "msg_bios_bin_success": "BIOS installé !", "msg_bios_unsupported": "Format non supporté."
    },
    "de": {
        "title_sub": "Update-, Cloud- und Konfigurationsmanager", "btn_help": "❔ Über", "tab_cloud": "🚀 Update", "tab_emu": "⚙️ Emulator", "tab_vid": "🖥️ Video", "tab_saves": "🔄 Saves", "tab_logs": "📝 Logs",
        "lbl_path": "Installationspfad:", "btn_browse": "Durchsuchen...", "lbl_branch": "Emulator-Version:",
        "rb_master_desc": "Offizielle stabile Versionen.", "rb_dev_desc": "Tägliche Cloud-Builds.",
        "lbl_cloud": "Cloud-Save-Synchronisierung:", "rb_none": "Keine", "sw_desk": "Desktop-Verknüpfung erstellen",
        "sw_start": "Mit Windows starten (Stumm)", "sw_nogui": "Grafische Oberfläche deaktivieren (-nogui)", "sw_map": "Controller-Backup",
        "lbl_backup_limit": "Backup-Limit:", "limit_unlimited": "Unbegrenzt",
        "btn_reconfig": "⚙️ Emulator & ROMs neu konfigurieren", "lbl_roms": "Spieleordner (ROMs):", "lbl_ra": "RetroAchievements:",
        "sw_custom_paths": "Benutzerdefinierte Pfade", "lbl_bios_path": "BIOS-Ordner:", "lbl_vmu_path": "VMU-Ordner:", "lbl_state_path": "Save-State-Ordner:", "lbl_save_path": "Spielstand-Ordner:",
        "sw_ra": "RetroAchievements aktivieren", "lbl_user": "Benutzername:", "lbl_pass": "Passwort / Token:", "sw_hard": "Hardcore-Modus",
        "lbl_qol": "Qualitätsverbesserungen:", "sw_vmu": "VMU pro Spiel", "sw_box": "Cover automatisch laden",
        "sw_vga": "Grafik optimieren (VGA)", "sw_disc": "Discord-Status", "sw_osd": "VMU auf Bildschirm anzeigen", "sw_vmu_snd": "VMU-Sounds aktivieren",
        "btn_save_emu": "💾 Einstellungen speichern", "lbl_vid_title": "Video-Einstellungen",
        "lbl_vid_warn": "⚠️ Warnung: Grundeinstellungen.", "lbl_api": "Grafik-API:", "lbl_res": "Interne Auflösung:",
        "sw_full": "Vollbild", "sw_int": "Ganzzahlige Skalierung", "sw_lin": "Lineare Interpolation", "sw_vsync": "V-Sync",
        "btn_save_vid": "💾 Video speichern", "lbl_saves_title": "Cloud-Backups wiederherstellen", "lbl_saves_desc": "Wählen Sie ein Backup-ZIP aus.",
        "btn_search_saves": "🔄 Suchen", "combo_saves_def": "Klicken zum Suchen...", "btn_extract": "📥 Extrahieren",
        "lbl_logs_title": "Protokolle (Logs)", "btn_log_refresh": "🔄 Aktualisieren", "btn_log_copy": "📋 Kopieren", "btn_log_clear": "🗑️ Löschen",
        "log_not_found": "Kein Log gefunden.", "btn_verify": "🚀 PRÜFE...", "btn_rollback": "↩️ ZURÜCKSETZEN",
        "btn_play": "SPIELEN", "btn_update_act": "AKTUALISIEREN", "btn_install_act": "INSTALLIEREN", "btn_starting": "STARTET...",
        "btn_processing": "VERARBEITET...", "btn_reverting": "SETZT ZURÜCK...", "emu_status_checking": "Emulator: 🔵 Prüfe...",
        "emu_status_updated": "Emulator: 🟢 Aktuell", "emu_status_outdated": "Emulator: 🟡 Veraltet", "emu_status_offline": "Emulator: 🟡 Offline",
        "emu_status_missing": "Emulator: 🔴 Fehlt", "emu_status_error": "Emulator: 🔴 Fehler", "bios_ok": "BIOS: 🟢 OK",
        "bios_custom": "BIOS: 🟢 OK (Custom)", "bios_wrong": "BIOS: 🟡 Falscher Pfad", "bios_missing": "BIOS: 🔴 Fehlt", "bios_error": "BIOS: 🔴 Fehler",
        "msg_success": "Operation erfolgreich!", "msg_error": "Fehler bei der Operation.",
        "msg_updater_update": "Eine neue Version des Flycast Updaters wurde erkannt!\nDas Programm wird zusammen mit dem Emulator aktualisiert.",
        "tt_help": "Hilfe", "tt_bios": "Prüft BIOS.", "tt_path": "Installationspfad", "tt_master": "Stabel", "tt_dev": "Dev",
        "tt_nogui": "CLI-Modus", "tt_reconfig": "Neu konfigurieren", "tt_opengl": "OpenGL", "tt_vulkan": "Vulkan", "tt_dx9": "DX9", "tt_dx11": "DX11",
        "tt_custom_paths": "Eigene Pfade", "msg_bios_missing": "Fehlende BIOS-Dateien:\n- {files}", "title_bios_missing": "BIOS fehlt",
        "msg_bios_partial": "Datei kopiert. Fehlt noch:\n- {missing}", "title_bios_partial": "BIOS unvollständig", "msg_bios_zip_success": "BIOS aus ZIP extrahiert!",
        "msg_bios_bin_success": "BIOS installiert!", "msg_bios_unsupported": "Nicht unterstütztes Format."
    },
    "zh": {
        "title_sub": "更新、云端和配置管理器", "btn_help": "❔ 关于", "tab_cloud": "🚀 更新", "tab_emu": "⚙️ 模拟器", "tab_vid": "🖥️ 视频", "tab_saves": "🔄 存档", "tab_logs": "📝 日志",
        "lbl_path": "模拟器安装路径:", "btn_browse": "浏览...", "lbl_branch": "模拟器版本:",
        "rb_master_desc": "官方稳定版。", "rb_dev_desc": "每日云端构建。",
        "lbl_cloud": "云端存档同步:", "rb_none": "无", "sw_desk": "创建桌面快捷方式",
        "sw_start": "随Windows启动 (静默模式)", "sw_nogui": "禁用图形界面 (-nogui)", "sw_map": "备份控制器映射",
        "lbl_backup_limit": "备份限制:", "limit_unlimited": "无限制",
        "btn_reconfig": "⚙️ 重新配置模拟器和ROM", "lbl_roms": "游戏文件夹 (ROMs):", "lbl_ra": "RetroAchievements 成就:",
        "sw_custom_paths": "使用自定义路径", "lbl_bios_path": "BIOS 文件夹:", "lbl_vmu_path": "VMU 文件夹:", "lbl_state_path": "即时存档文件夹:", "lbl_save_path": "游戏存档文件夹:",
        "sw_ra": "启用 RetroAchievements", "lbl_user": "用户名:", "lbl_pass": "密码 / 令牌:", "sw_hard": "硬核模式 (禁用即时存档)",
        "lbl_qol": "生活质量优化 (QoL):", "sw_vmu": "每游戏独立 VMU", "sw_box": "自动下载封面",
        "sw_vga": "优化图形 (VGA)", "sw_disc": "Discord 状态", "sw_osd": "屏幕显示 VMU", "sw_vmu_snd": "启用 VMU 声音",
        "btn_save_emu": "💾 保存模拟器设置", "lbl_vid_title": "视频设置 (基础)",
        "lbl_vid_warn": "⚠️ 警告: 这些是基础设置。", "lbl_api": "图形 API:", "lbl_res": "内部分辨率:",
        "sw_full": "全屏", "sw_int": "整数缩放", "sw_lin": "线性插值", "sw_vsync": "垂直同步 (V-Sync)",
        "btn_save_vid": "💾 保存视频设置", "lbl_saves_title": "恢复云端备份", "lbl_saves_desc": "选择云端备份的 .zip 文件解压。",
        "btn_search_saves": "🔄 查找备份", "combo_saves_def": "点击查找备份...", "btn_extract": "📥 提取并恢复",
        "lbl_logs_title": "审计和诊断 (日志)", "btn_log_refresh": "🔄 刷新", "btn_log_copy": "📋 复制", "btn_log_clear": "🗑️ 清除",
        "log_not_found": "未找到日志文件。", "btn_verify": "🚀 正在检查...", "btn_rollback": "↩️ 回滚",
        "btn_play": "游玩", "btn_update_act": "更新", "btn_install_act": "安装", "btn_starting": "启动中...",
        "btn_processing": "处理中...", "btn_reverting": "正在回滚...", "emu_status_checking": "模拟器: 🔵 检查云端版本...",
        "emu_status_updated": "模拟器: 🟢 已是最新", "emu_status_outdated": "模拟器: 🟡 需要更新", "emu_status_offline": "模拟器: 🟡 离线",
        "emu_status_missing": "模拟器: 🔴 缺失", "emu_status_error": "模拟器: 🔴 错误", "bios_ok": "BIOS: 🟢 正常",
        "bios_custom": "BIOS: 🟢 正常 (自定义)", "bios_wrong": "BIOS: 🟡 路径不正确", "bios_missing": "BIOS: 🔴 缺失", "bios_error": "BIOS: 🔴 错误",
        "msg_success": "操作成功完成！", "msg_error": "操作期间发生错误。",
        "msg_updater_update": "检测到新版本的 Flycast Updater！\n程序将与模拟器一起更新。",
        "tt_help": "点击这里阅读帮助。", "tt_bios": "检查 BIOS 文件。", "tt_path": "安装路径。", "tt_master": "稳定版。", "tt_dev": "开发版。",
        "tt_nogui": "命令行模式。", "tt_reconfig": "重新配置。", "tt_opengl": "OpenGL API。", "tt_vulkan": "Vulkan API。", "tt_dx9": "DX9 API。", "tt_dx11": "DX11 API。",
        "tt_custom_paths": "自定义路径。", "msg_bios_missing": "缺少以下 BIOS 文件:\n- {files}", "title_bios_missing": "缺少 BIOS",
        "msg_bios_partial": "文件复制成功。\n缺少文件:\n- {missing}", "title_bios_partial": "BIOS 不完整", "msg_bios_zip_success": "BIOS 解压并安装成功！",
        "msg_bios_bin_success": "BIOS 安装成功！", "msg_bios_unsupported": "不支持的文件格式."
    },
    "ja": {
        "title_sub": "アップデート、クラウド、設定マネージャー", "btn_help": "❔ 概要", "tab_cloud": "🚀 更新", "tab_emu": "⚙️ エミュレータ", "tab_vid": "🖥️ ビデオ", "tab_saves": "🔄 セーブ", "tab_logs": "📝 ログ",
        "lbl_path": "インストール先:", "btn_browse": "参照...", "lbl_branch": "エミュレータバージョン:",
        "rb_master_desc": "公式安定版リリース。", "rb_dev_desc": "毎日のクラウドビルド。",
        "lbl_cloud": "クラウドセーブ同期:", "rb_none": "なし", "sw_desk": "デスクトップショートカット作成",
        "sw_start": "Windowsと同時に起動 (サイレント)", "sw_nogui": "GUI無効化 (-nogui)", "sw_map": "コントローラーマッピングのバックアップ",
        "lbl_backup_limit": "バックアップ制限:", "limit_unlimited": "無制限",
        "btn_reconfig": "⚙️ エミュレータとROMの再設定", "lbl_roms": "ゲームフォルダ (ROMs):", "lbl_ra": "RetroAchievements:",
        "sw_custom_paths": "カスタムパスを使用", "lbl_bios_path": "BIOSフォルダ:", "lbl_vmu_path": "VMUフォルダ:", "lbl_state_path": "ステートセーブフォルダ:", "lbl_save_path": "セーブフォルダ:",
        "sw_ra": "RetroAchievementsを有効化", "lbl_user": "ユーザー名:", "lbl_pass": "パスワード / トークン:", "sw_hard": "ハードコアモード",
        "lbl_qol": "品質向上 (QoL) 調整:", "sw_vmu": "ゲーム別VMU", "sw_box": "ジャケット自動ダウンロード",
        "sw_vga": "グラフィック最適化 (VGA)", "sw_disc": "Discordプレゼンス", "sw_osd": "画面にVMUを表示", "sw_vmu_snd": "VMUサウンド有効化",
        "btn_save_emu": "💾 設定を保存", "lbl_vid_title": "ビデオ設定 (基本)",
        "lbl_vid_warn": "⚠️ 警告: 基本的な設定です。", "lbl_api": "グラフィックAPI:", "lbl_res": "内部解像度:",
        "sw_full": "フルスクリーン", "sw_int": "整数スケーリング", "sw_lin": "線形補間", "sw_vsync": "垂直同期 (V-Sync)",
        "btn_save_vid": "💾 ビデオ設定を保存", "lbl_saves_title": "クラウドバックアップの復元", "lbl_saves_desc": "バックアップの .zip を選択してください。",
        "btn_search_saves": "🔄 検索", "combo_saves_def": "バックアップを検索...", "btn_extract": "📥 抽出して復元",
        "lbl_logs_title": "ログと診断", "btn_log_refresh": "🔄 更新", "btn_log_copy": "📋 コピー", "btn_log_clear": "🗑️ クリア",
        "log_not_found": "ログが見つかりません。", "btn_verify": "🚀 確認中...", "btn_rollback": "↩️ ロールバック",
        "btn_play": "プレイ", "btn_update_act": "アップデート", "btn_install_act": "インストール", "btn_starting": "起動中...",
        "btn_processing": "処理中...", "btn_reverting": "ロールバック中...", "emu_status_checking": "エミュレータ: 🔵 確認中...",
        "emu_status_updated": "エミュレータ: 🟢 最新", "emu_status_outdated": "エミュレータ: 🟡 古いバージョン", "emu_status_offline": "エミュレータ: 🟡 オフライン",
        "emu_status_missing": "エミュレータ: 🔴 不足", "emu_status_error": "エミュレータ: 🔴 エラー", "bios_ok": "BIOS: 🟢 OK",
        "bios_custom": "BIOS: 🟢 OK (カスタム)", "bios_wrong": "BIOS: 🟡 パス不正", "bios_missing": "BIOS: 🔴 不足", "bios_error": "BIOS: 🔴 エラー",
        "msg_success": "操作が完了しました！", "msg_error": "エラーが発生しました。",
        "msg_updater_update": "Flycast Updaterの新バージョンが検出されました！\nエミュレータとともにプログラムが更新されます。",
        "tt_help": "ヘルプを表示。", "tt_bios": "BIOSを確認。", "tt_path": "インストール先。", "tt_master": "安定版。", "tt_dev": "開発版。",
        "tt_nogui": "CUIモード。", "tt_reconfig": "再設定。", "tt_opengl": "OpenGL API。", "tt_vulkan": "Vulkan API。", "tt_dx9": "DX9 API。", "tt_dx11": "DX11 API。",
        "tt_custom_paths": "カスタムパス。", "msg_bios_missing": "次のBIOSファイルが不足しています:\n- {files}", "title_bios_missing": "BIOS不足",
        "msg_bios_partial": "コピー成功。\n不足:\n- {missing}", "title_bios_partial": "BIOS不完全", "msg_bios_zip_success": "ZIPからBIOSをインストールしました！",
        "msg_bios_bin_success": "BIOSをインストールしました！", "msg_bios_unsupported": "サポートされていない形式です。"
    },
    "ru": {
        "title_sub": "Менеджер обновлений, облака и настроек", "btn_help": "❔ О программе", "tab_cloud": "🚀 Обновление", "tab_emu": "⚙️ Эмулятор", "tab_vid": "🖥️ Видео", "tab_saves": "🔄 Сейвы", "tab_logs": "📝 Логи",
        "lbl_path": "Путь установки эмулятора:", "btn_browse": "Обзор...", "lbl_branch": "Версия эмулятора:",
        "rb_master_desc": "Официальные и стабильные релизы.", "rb_dev_desc": "Ежедневные облачные сборки.",
        "lbl_cloud": "Синхронизация облачных сохранений:", "rb_none": "Нет", "sw_desk": "Создать ярлык на рабочем столе",
        "sw_start": "Запуск с Windows (Тихий режим)", "sw_nogui": "Отключить графический интерфейс (-nogui)", "sw_map": "Резервная копия управления",
        "lbl_backup_limit": "Лимит бэкапов:", "limit_unlimited": "Неограничено",
        "btn_reconfig": "⚙️ Перенастроить эмулятор и ROM", "lbl_roms": "Папка с играми (ROMs):", "lbl_ra": "RetroAchievements:",
        "sw_custom_paths": "Использовать свои пути", "lbl_bios_path": "Папки BIOS:", "lbl_vmu_path": "Папка VMU:", "lbl_state_path": "Папки Save State:", "lbl_save_path": "Папка сохранений:",
        "sw_ra": "Включить RetroAchievements", "lbl_user": "Имя пользователя:", "lbl_pass": "Пароль / Токен:", "sw_hard": "Хардкорный режим",
        "lbl_qol": "Улучшения качества жизни:", "sw_vmu": "VMU для каждой игры", "sw_box": "Автозагрузка обложек",
        "sw_vga": "Оптимизация графики (VGA)", "sw_disc": "Статус в Discord", "sw_osd": "Показать VMU на экране", "sw_vmu_snd": "Включить звуки VMU",
        "btn_save_emu": "💾 Сохранить настройки", "lbl_vid_title": "Настройки видео (Базовые)",
        "lbl_vid_warn": "⚠️ Внимание: Базовые настройки.", "lbl_api": "Графический API:", "lbl_res": "Внутреннее разрешение:",
        "sw_full": "Полноэкранный режим", "sw_int": "Целочисленное масштабирование", "sw_lin": "Линейная интерполяция", "sw_vsync": "Вертикальная синхронизация",
        "btn_save_vid": "💾 Сохранить видео", "lbl_saves_title": "Восстановить бэкапы", "lbl_saves_desc": "Выберите .zip архив бэкапа.",
        "btn_search_saves": "🔄 Найти", "combo_saves_def": "Нажмите Поиск...", "btn_extract": "📥 Извлечь и восстановить",
        "lbl_logs_title": "Аудит и диагностика (Логи)", "btn_log_refresh": "🔄 Обновить", "btn_log_copy": "📋 Копировать", "btn_log_clear": "🗑️ Очистить",
        "log_not_found": "Файл лога не найден.", "btn_verify": "🚀 ПРОВЕРКА...", "btn_rollback": "↩️ ОТКАТ",
        "btn_play": "ИГРАТЬ", "btn_update_act": "ОБНОВИТЬ", "btn_install_act": "УСТАНОВИТЬ", "btn_starting": "ЗАПУСК...",
        "btn_processing": "ОБРАБОТКА...", "btn_reverting": "ОТКАТ...", "emu_status_checking": "Эмулятор: 🔵 Проверка...",
        "emu_status_updated": "Эмулятор: 🟢 Актуально", "emu_status_outdated": "Эмулятор: 🟡 Устарел", "emu_status_offline": "Эмулятор: 🟡 Нет сети",
        "emu_status_missing": "Эмулятор: 🔴 Отсутствует", "emu_status_error": "Эмулятор: 🔴 Ошибка", "bios_ok": "BIOS: 🟢 OK",
        "bios_custom": "BIOS: 🟢 OK (Свой)", "bios_wrong": "BIOS: 🟡 Неверный путь", "bios_missing": "BIOS: 🔴 Нет", "bios_error": "BIOS: 🔴 Ошибка",
        "msg_success": "Операция успешно завершена!", "msg_error": "Ошибка во время операции.",
        "msg_updater_update": "Обнаружена новая версия Flycast Updater!\nПрограмма будет обновлена вместе с эмулятором.",
        "tt_help": "Справка", "tt_bios": "Проверка BIOS.", "tt_path": "Путь установки.", "tt_master": "Стабильная.", "tt_dev": "Разработка.",
        "tt_nogui": "Режим CLI.", "tt_reconfig": "Перенастроить.", "tt_opengl": "OpenGL API.", "tt_vulkan": "Vulkan API.", "tt_dx9": "DX9 API.", "tt_dx11": "DX11 API.",
        "tt_custom_paths": "Свои пути.", "msg_bios_missing": "Отсутствуют файлы BIOS:\n- {files}", "title_bios_missing": "Нет BIOS",
        "msg_bios_partial": "Файл скопирован.\nОстался:\n- {missing}", "title_bios_partial": "Неполный BIOS", "msg_bios_zip_success": "BIOS успешно извлечен!",
        "msg_bios_bin_success": "Файлы BIOS установлены!", "msg_bios_unsupported": "Формат не поддерживается."
    },
    "ar": {
        "title_sub": "مدير التحديثات والسحابة والإعدادات", "btn_help": "❔ حول", "tab_cloud": "🚀 التحديث", "tab_emu": "⚙️ المحاكي", "tab_vid": "🖥️ الفيديو", "tab_saves": "🔄 الحفظ", "tab_logs": "📝 السجلات",
        "lbl_path": "مسار تثبيت المحاكي:", "btn_browse": "استعراض...", "lbl_branch": "إصدار المحاكي:",
        "rb_master_desc": "الإصدارات الرسمية والمستقرة.", "rb_dev_desc": "Builds يومية.",
        "lbl_cloud": "مزامنة الحفظ السحابي:", "rb_none": "لا يوجد", "sw_desk": "إنشاء اختصار سطح المكتب",
        "sw_start": "البدء مع ويندوز", "sw_nogui": "تعطيل الواجهة الرسومية", "sw_map": "نسخ احتياطي للتحكم",
        "lbl_backup_limit": "حد النسخ الاحتياطي:", "limit_unlimited": "غير محدود",
        "btn_reconfig": "⚙️ إعادة تكوين المحاكي والألعاب", "lbl_roms": "مجلد الألعاب (ROMs):", "lbl_ra": "RetroAchievements:",
        "sw_custom_paths": "استخدام مسارات مخصصة", "lbl_bios_path": "مجلدات BIOS:", "lbl_vmu_path": "مجلد VMU:", "lbl_state_path": "مجلدات الحفظ السريع:", "lbl_save_path": "مجلد حفظ اللعبة:",
        "sw_ra": "تفعيل RetroAchievements", "lbl_user": "اسم المستخدم:", "lbl_pass": "كلمة المرور / الرمز:", "sw_hard": "وضع Hardcore",
        "lbl_qol": "تحسينات جودة الحياة:", "sw_vmu": "VMU فردي لكل لعبة", "sw_box": "تحميل الأغلفة تلقائياً",
        "sw_vga": "تحسين الرسومات (VGA)", "sw_disc": "حالة Discord", "sw_osd": "إظهار VMU على الشاشة", "sw_vmu_snd": "تفعيل أصوات VMU",
        "btn_save_emu": "💾 حفظ إعدادات المحاكي", "lbl_vid_title": "إعدادات الفيديو",
        "lbl_vid_warn": "⚠️ تحذير: إعدادات أساسية.", "lbl_api": "واجهة برمجة الرسومات:", "lbl_res": "الدقة الداخلية:",
        "sw_full": "ملء الشاشة", "sw_int": "تحجيم صحيح", "sw_lin": "استيفاء خطي", "sw_vsync": "مزامنة رأسية",
        "btn_save_vid": "💾 حفظ إعدادات الفيديو", "lbl_saves_title": "استعادة النسخ الاحتياطية", "lbl_saves_desc": "اختر ملف .zip للاستعادة.",
        "btn_search_saves": "🔄 بحث", "combo_saves_def": "انقر للبحث...", "btn_extract": "📥 استخراج واستعادة",
        "lbl_logs_title": "التدقيق والتشخيص (السجلات)", "btn_log_refresh": "🔄 تحديث", "btn_log_copy": "📋 نسخ", "btn_log_clear": "🗑️ مسح",
        "log_not_found": "لم يتم العثور على سجل.", "btn_verify": "🚀 جاري التحقق...", "btn_rollback": "↩️ التراجع",
        "btn_play": "تشغيل", "btn_update_act": "تحديث", "btn_install_act": "تثبيت", "btn_starting": "جاري البدء...",
        "btn_processing": "جاري المعالجة...", "btn_reverting": "جاري التراجع...", "emu_status_checking": "المحاكي: 🔵 جاري التحقق...",
        "emu_status_updated": "المحاكي: 🟢 محدث", "emu_status_outdated": "المحاكي: 🟡 قديم", "emu_status_offline": "المحاكي: 🟡 بدون إنترنت",
        "emu_status_missing": "المحاكي: 🔴 مفقود", "emu_status_error": "المحاكي: 🔴 خطأ", "bios_ok": "BIOS: 🟢 جاهز",
        "bios_custom": "BIOS: 🟢 جاهز (مخصص)", "bios_wrong": "BIOS: 🟡 مسار خاطئ", "bios_missing": "BIOS: 🔴 مفقود", "bios_error": "BIOS: 🔴 خطأ",
        "msg_success": "تمت العملية بنجاح!", "msg_error": "حدث خطأ أثناء العملية.",
        "msg_updater_update": "تم اكتشاف إصدار جديد من Flycast Updater!\nسيتم تحديث البرنامج مع المحاكي.",
        "tt_help": "مساعدة", "tt_bios": "فحص ملفات BIOS.", "tt_path": "مسار التثبيت.", "tt_master": "مستقر.", "tt_dev": "تطوير.",
        "tt_nogui": "وضع CLI.", "tt_reconfig": "إعادة تكوين.", "tt_opengl": "OpenGL.", "tt_vulkan": "Vulkan.", "tt_dx9": "DX9.", "tt_dx11": "DX11.",
        "tt_custom_paths": "مسارات مخصصة.", "msg_bios_missing": "ملفات BIOS التالية مفقودة:\n- {files}", "title_bios_missing": "BIOS مفقود",
        "msg_bios_partial": "تم النسخ.\nمفقود:\n- {missing}", "title_bios_partial": "BIOS غير مكتمل", "msg_bios_zip_success": "BIOS extrait du ZIP !",
        "msg_bios_bin_success": "تم تثبيت BIOS بنجاح!", "msg_bios_unsupported": "صيغة غير مدعومة."
    },
    "hi": {
        "title_sub": "أبडेट، کلاؤڈ اور کنفیگریشن مینیجر", "btn_help": "❔ کے بارے میں", "tab_cloud": "🚀 اپ ڈیٹ", "tab_emu": "⚙️ ایمولیٹر", "tab_vid": "🖥️ ویڈیو", "tab_saves": "🔄 سیو", "tab_logs": "📝 لاگز",
        "lbl_path": "ایمولیٹر انسٹال پاتھ:", "btn_browse": "براؤز...", "lbl_branch": "ایمولیٹر ورژن:",
        "rb_master_desc": "سرکاری اور مستحکم ورژن۔", "rb_dev_desc": "روزانہ کلاؤڈ بلڈز۔",
        "lbl_cloud": "کلاؤڈ سیو ہم آہنگی:", "rb_none": "کوئی نہیں", "sw_desk": "ڈیسک ٹاپ شارٹ کٹ بنائیں",
        "sw_start": "ونڈوز کے ساتھ شروع کریں", "sw_nogui": "GUI غیر فعال کریں", "sw_map": "کنٹرولر بیک اپ",
        "lbl_backup_limit": "بیک اپ حد:", "limit_unlimited": "لامحدود",
        "btn_reconfig": "⚙️ ایمولیٹر اور ROMs دوبارہ ترتیب دیں", "lbl_roms": "گیمز فولڈر (ROMs):", "lbl_ra": "RetroAchievements:",
        "sw_custom_paths": "حسب ضرورت پاتھ استعمال کریں", "lbl_bios_path": "BIOS فولڈرز:", "lbl_vmu_path": "VMU فولڈر:", "lbl_state_path": "سیو اسٹیٹ فولڈرز:", "lbl_save_path": "گیم سیو فولڈر:",
        "sw_ra": "RetroAchievements فعال کریں", "lbl_user": "صارف نام:", "lbl_pass": "پاس ورڈ / ٹوکن:", "sw_hard": "ہارڈکور موڈ",
        "lbl_qol": "کوالٹی آف لائف ٹویکس:", "sw_vmu": "فی گیم VMU", "sw_box": "خودکار باکس آرٹ ڈاؤن لوڈ",
        "sw_vga": "گرافکس کو بہتر بنائیں (VGA)", "sw_disc": "Discord موجودگی", "sw_osd": "اسکرین پر VMU دکھائیں", "sw_vmu_snd": "VMU آوازیں فعال کریں",
        "btn_save_emu": "💾 ایمولیٹر کی ترتیبات محفوظ کریں", "lbl_vid_title": "ویڈیو کی ترتیبات",
        "lbl_vid_warn": "⚠️ انتباہ: بنیادی ترتیبات۔", "lbl_api": "گرافکس API:", "lbl_res": "اندرونی ریزولوشن:",
        "sw_full": "فل اسکرین", "sw_int": "انٹیجر سکیلنگ", "sw_lin": "لینیئر انٹرپولیشن", "sw_vsync": "ورٹیکل سنک",
        "btn_save_vid": "💾 ویڈیو ترتیبات محفوظ کریں", "lbl_saves_title": "کلاؤڈ بیک اپ بحال کریں", "lbl_saves_desc": "ایک بیک اپ .zip فائل منتخب کریں۔",
        "btn_search_saves": "🔄 تلاش کریں", "combo_saves_def": "تلاش پر کلک کریں...", "btn_extract": "📥 نکالیں اور بحال کریں",
        "lbl_logs_title": "آڈٹ اور تشخیص (لاگز)", "btn_log_refresh": "🔄 ریفریش", "btn_log_copy": "📋 کاپی کریں", "btn_log_clear": "🗑️ صاف کریں",
        "log_not_found": "کوئی لاگ فائل نہیں ملی۔", "btn_verify": "🚀 جانچ ہو رہی ہے...", "btn_rollback": "↩️ رول بیک",
        "btn_play": "کھیلیں", "btn_update_act": "اپ ڈیٹ", "btn_install_act": "انسٹال", "btn_starting": "شروع ہو رہا ہے...",
        "btn_processing": "پروسیسنگ...", "btn_reverting": "رول بیک ہو رہا ہے...", "emu_status_checking": "ایمولیٹر: 🔵 جانچ ہو رہی ہے...",
        "emu_status_updated": "ایمولیٹر: 🟢 اپ ٹو ڈیٹ", "emu_status_outdated": "ایمولیٹر: 🟡 پرانا", "emu_status_offline": "ایمولیٹر: 🟡 آف لائن",
        "emu_status_missing": "ایمولیٹر: 🔴 غائب", "emu_status_error": "ایمولیٹر: 🔴 خرابی", "bios_ok": "BIOS: 🟢 ٹھیک ہے",
        "bios_custom": "BIOS: 🟢 ٹھیک ہے (حسب ضرورت)", "bios_wrong": "BIOS: 🟡 غلط پاتھ", "bios_missing": "BIOS: 🔴 غائب", "bios_error": "BIOS: 🔴 خرابی",
        "msg_success": "آپریشن کامیابی سے مکمل ہو گیا!", "msg_error": "آپریشن کے دوران خرابی۔",
        "msg_updater_update": "Flycast Updater کا نیا ورژن مل گیا ہے!\nप्रोग्राम को एमुलेटर के साथ अपडेट किया जाएगा।",
        "tt_help": "مدد", "tt_bios": "BIOS چیک کرتا ہے۔", "tt_path": "انسٹالیشن پاتھ۔", "tt_master": "مستحکم۔", "tt_dev": "ڈویلپمنٹ۔",
        "tt_nogui": "CLI موڈ۔", "tt_reconfig": "دوبارہ ترتیب دیں۔", "tt_opengl": "OpenGL API۔", "tt_vulkan": "Vulkan API۔", "tt_dx9": "DX9 API۔", "tt_dx11": "DX11 API۔",
        "tt_custom_paths": "حسب ضرورت پاتھ۔", "msg_bios_missing": "مندرجہ ذیل BIOS فائلیں غائب ہیں:\n- {files}", "title_bios_missing": "BIOS غائب",
        "msg_bios_partial": "فائل کاپی ہو گئی۔ غائب:\n- {missing}", "title_bios_partial": "نامکمل BIOS", "msg_bios_zip_success": "BIOS کامیابی سے زپ سے نکالا گیا!",
        "msg_bios_bin_success": "BIOS انسٹال ہو گیا!", "msg_bios_unsupported": "غیر تعاون یافتہ فارمیٹ."
    }
}

VERSION = "4.1"
CONFIG_FILE = "config.json"
REPO_UPDATER = "dsantanna/flycast_updater"

# ==========================================
# FUNÇÕES NUCLEARES E PERSISTÊNCIA
# ==========================================
def carregar_configuracao():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def salvar_configuracao(dados):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception:
        pass

def obter_token_retroachievements(usuario, senha):
    url = f"https://retroachievements.org/dorequest.php?r=login&u={urllib.parse.quote(usuario)}&p={urllib.parse.quote(senha)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': f'FlycastUpdater/{VERSION}'})
        with urllib.request.urlopen(req, timeout=5) as response:
            resposta = json.loads(response.read().decode('utf-8'))
            if resposta.get("Success"):
                return resposta.get("Token")
    except Exception:
        pass
    return None

def atualizar_emu_cfg(install_path, roms_path=None, ra_enabled=None, ra_user=None, ra_pass=None, ra_hardcore=None, 
                      vmu_individual=None, fetch_boxart=None, vga_cable=None, discord_presence=None,
                      show_osd_vmu=None, vmu_sound=None, bios_path=None, vmu_path=None, state_path=None, save_path=None,
                      vid_api=None, vid_res=None, vid_full=None, vid_int=None, vid_lin=None, vid_vsync=None):
    caminhos_possiveis = [
        os.path.join(install_path, "emu.cfg"),
        os.path.join(install_path, "data", "emu.cfg")
    ]
    
    cfg_path = None
    for p in caminhos_possiveis:
        if os.path.exists(p):
            cfg_path = p
            break
            
    if not cfg_path:
        cfg_path = os.path.join(install_path, "emu.cfg")

    config = configparser.RawConfigParser(strict=False)
    config.optionxform = str 
    
    if os.path.exists(cfg_path):
        try:
            config.read(cfg_path, encoding='utf-8')
        except Exception:
            return False

    for section in ['achievements', 'config', 'audio', 'window']:
        if not config.has_section(section):
            config.add_section(section)

    if ra_enabled is not None: config.set('achievements', 'Enabled', 'yes' if ra_enabled else 'no')
    if ra_hardcore is not None: config.set('achievements', 'HardcoreMode', 'yes' if ra_hardcore else 'no')
    if ra_user is not None: config.set('achievements', 'UserName', ra_user)
    if ra_pass is not None: config.set('achievements', 'Token', ra_pass)

    if roms_path: config.set('config', 'Dreamcast.ContentPath', roms_path.replace("/", "\\"))
    if vmu_individual is not None: config.set('config', 'PerGameVmu', 'yes' if vmu_individual else 'no')
    if fetch_boxart is not None:
        config.set('config', 'FetchBoxart', 'yes' if fetch_boxart else 'no')
        config.set('config', 'BoxartDisplayMode', 'yes' if fetch_boxart else 'no')
    if vga_cable is not None: config.set('config', 'Dreamcast.Cable', '0' if vga_cable else '3') 
    if discord_presence is not None: config.set('config', 'DiscordPresence', 'yes' if discord_presence else 'no')
    if show_osd_vmu is not None: config.set('config', 'ShowOsdVmu', 'yes' if show_osd_vmu else 'no')
    
    def _set_or_remove(sec, k, val):
        if val: config.set(sec, k, val.replace("/", "\\"))
        else:
            if config.has_option(sec, k): config.remove_option(sec, k)

    if bios_path is not None: 
        if bios_path: os.makedirs(bios_path, exist_ok=True)
        _set_or_remove('config', 'Dreamcast.BiosPath', bios_path)
    if vmu_path is not None: 
        if vmu_path: os.makedirs(vmu_path, exist_ok=True)
        _set_or_remove('config', 'Dreamcast.VmuPath', vmu_path)
    if state_path is not None: 
        if state_path: os.makedirs(state_path, exist_ok=True)
        _set_or_remove('config', 'Dreamcast.SavestatePath', state_path)
    if save_path is not None: 
        if save_path: os.makedirs(save_path, exist_ok=True)
        _set_or_remove('config', 'Dreamcast.SavePath', save_path)

    if vid_api is not None:
        api_map = {"OpenGL": "0", "DirectX 9": "1", "DirectX 11": "2", "Vulkan": "4"}
        config.set('config', 'pvr.rend', api_map.get(vid_api, "4"))
    if vid_res is not None: config.set('config', 'rend.Resolution', vid_res)
    if vid_int is not None: config.set('config', 'rend.IntegerScale', 'yes' if vid_int else 'no')
    if vid_lin is not None: config.set('config', 'rend.LinearInterpolation', 'yes' if vid_lin else 'no')
    if vid_vsync is not None: config.set('config', 'rend.vsync', 'yes' if vid_vsync else 'no')

    if vid_full is not None: config.set('window', 'fullscreen', 'yes' if vid_full else 'no')
    if vmu_sound is not None: config.set('audio', 'VmuSound', 'yes' if vmu_sound else 'no')

    try:
        os.makedirs(os.path.dirname(os.path.abspath(cfg_path)), exist_ok=True)
        with open(cfg_path, 'w', encoding='utf-8') as f:
            config.write(f, space_around_delimiters=True)
        return True
    except Exception:
        return False

def aplicar_auto_atualizacao(url_download, install_path, modo_gui=False, app_gui=None):
    exe_atual = sys.executable
    dir_atual = os.path.dirname(exe_atual)
    exe_novo = os.path.join(dir_atual, "FlycastUpdater_novo.exe")
    script_bat = os.path.join(dir_atual, "atualiza_updater.bat")
    
    if modo_gui and app_gui:
        app_gui.after(0, app_gui.label_status.configure, {"text": "Baixando nova versão do Atualizador...", "text_color": "orange"})
    
    try:
        urllib.request.urlretrieve(url_download, exe_novo)
        nome_exe = os.path.basename(exe_atual)
        conteudo_bat = f"""@echo off\ntimeout /t 2 /nobreak > NUL\ndel "{nome_exe}"\nren "FlycastUpdater_novo.exe" "{nome_exe}"\nstart "" "{nome_exe}"\n(goto) 2>nul & del "%~f0"\n"""
        with open(script_bat, "w") as f:
            f.write(conteudo_bat)
            
        subprocess.Popen(script_bat, shell=True)
        if modo_gui and app_gui:
            app_gui.after(0, app_gui.destroy)
        time.sleep(0.5)
        os._exit(0)
    except Exception:
        if os.path.exists(exe_novo):
            os.remove(exe_novo)

def verificar_atualizacao_updater(install_path, modo_gui=False, app_gui=None):
    api_url = f"https://api.github.com/repos/{REPO_UPDATER}/releases/latest"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            dados = json.loads(response.read().decode())
            
        versao_remota = dados.get("tag_name", "").replace("v", "")
        if versao_remota and versao_remota > VERSION:
            if modo_gui and app_gui:
                msg = app_gui._("msg_updater_update")
                mb.showinfo("Flycast Updater", msg, parent=app_gui)
            for asset in dados.get("assets", []):
                if asset["name"].endswith(".exe"):
                    aplicar_auto_atualizacao(asset["browser_download_url"], install_path, modo_gui, app_gui)
                    return True
    except Exception:
        pass
    return False

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def update_text(self, new_text):
        self.text = new_text

    def show_tooltip(self, event=None):
        try:
            if self.widget.cget("state") == "disabled" and "Rollback" not in self.text and "não detectado" not in self.text:
                return 
        except Exception: pass
            
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left', background="#2b2b2b", foreground="#ffffff", relief='solid', borderwidth=1, font=("Segoe UI", 9, "normal"), padx=8, pady=4)
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class ConsoleRedirector:
    def __init__(self, app):
        self.app = app

    def write(self, message):
        texto = message.strip()
        if not texto: return
        
        self.app.log(f"[MOTOR] {texto}", bypass_console=True)

        if "[*] Progresso:" in texto:
            try:
                pct_str = texto.split("%")[0].split(" ")[-1]
                pct_float = float(pct_str) / 100.0
                tamanhos = texto.split("(")[1].replace(")", "")
                self.app.after(0, self.app.progressbar.set, pct_float)
                self.app.after(0, self.app.label_status.configure, {"text": f"🦔 Velocidade Sônica! Baixando... {pct_str}% ({tamanhos})", "text_color": "cyan"})
            except Exception: pass
        elif "[!]" in texto or "Aviso de BIOS" in texto:
            self.app.after(0, self.app.label_status.configure, {"text": f"⚠️ {texto}", "text_color": "#FF8C00"})
        elif "Backup" in texto or "Sincronizando" in texto or "[✓]" in texto or "Rollback" in texto or "[+]" in texto:
            self.app.after(0, self.app.label_status.configure, {"text": f"💾 {texto}", "text_color": "#00FF7F"})
        elif "Erro" in texto or "[-]" in texto:
             self.app.after(0, self.app.label_status.configure, {"text": f"❌ {texto}", "text_color": "#FF4C4C"})
        else:
            self.app.after(0, self.app.label_status.configure, {"text": texto, "text_color": "cyan"})
            
    def flush(self): pass

def iniciar_gui():
    import customtkinter as ctk
    from customtkinter import filedialog
    
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("blue") 

    class FlycastUpdaterApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.config_atual = carregar_configuracao()
            self.lang = self.config_atual.get("language", "pt")
            
            self.title(f"🌀 Flycast Updater - v{VERSION} (Another Day Edition)")
            self.geometry("620x960") 
            self.resizable(False, False)
            self.token_ra_salvo = "" 
            self.bios_prompt_done = False

            # --- CABEÇALHO ---
            self.frame_header = ctk.CTkFrame(self, fg_color="transparent")
            self.frame_header.pack(fill="x", padx=20, pady=(15, 0))
            
            self.label_titulo = ctk.CTkLabel(self.frame_header, text="Flycast Updater", font=ctk.CTkFont(size=24, weight="bold"))
            self.label_titulo.pack(side="top")
            
            self.label_sub = ctk.CTkLabel(self.frame_header, text=self._("title_sub"), text_color="gray")
            self.label_sub.pack(side="top", pady=(0, 10))

            self.frame_top_right = ctk.CTkFrame(self.frame_header, fg_color="transparent")
            self.frame_top_right.place(relx=1.0, rely=0.0, anchor="ne")
            
            self.lang_map = {
                "PT-BR": "pt", "EN-US": "en", "ES-ES": "es", "FR-FR": "fr",
                "DE-DE": "de", "ZH-CN": "zh", "JA-JP": "ja", "RU-RU": "ru",
                "AR-SA": "ar", "HI-IN": "hi"
            }
            self.rev_lang_map = {v: k for k, v in self.lang_map.items()}

            self.combo_lang = ctk.CTkComboBox(self.frame_top_right, values=list(self.lang_map.keys()), width=95, height=28, command=self.mudar_idioma)
            self.combo_lang.pack(side="left", padx=5)
            self.combo_lang.set(self.rev_lang_map.get(self.lang, "PT-BR"))

            self.btn_help = ctk.CTkButton(self.frame_top_right, text=self._("btn_help"), width=70, height=28, fg_color="#444", hover_color="#666", command=self.abrir_janela_ajuda)
            self.btn_help.pack(side="left")
            self.tt_help = ToolTip(self.btn_help, self._("tt_help"))

            # --- SISTEMA DE ABAS ---
            self.tabview = ctk.CTkTabview(self, width=580, height=660)
            self.tabview.pack(pady=5, padx=20, fill="both", expand=True)
            
            self.tab_atualizador = self.tabview.add(self._("tab_cloud"))
            self.tab_config = self.tabview.add(self._("tab_emu"))
            self.tab_video = self.tabview.add(self._("tab_vid"))
            self.tab_saves = self.tabview.add(self._("tab_saves"))
            self.tab_logs = self.tabview.add(self._("tab_logs"))

            self.construir_aba_nuvem()
            self.construir_aba_emulador()
            self.construir_aba_video()
            self.construir_aba_saves()
            self.construir_aba_logs()

            caminho_inicial = os.path.normpath(self.config_atual.get("install_path", os.getcwd()))
            self.entry_path.configure(state="normal")
            self.entry_path.delete(0, 'end')
            self.entry_path.insert(0, caminho_inicial)
            self.entry_path.configure(state="readonly")
            
            self.carregar_dados_atuais_emu_cfg()

            # --- PROGRESSO E STATUS GERAL ---
            self.progressbar = ctk.CTkProgressBar(self, width=540)
            self.progressbar.set(0)
            self.label_status = ctk.CTkLabel(self, text="...", text_color="cyan")

            # --- SEMÁFORO DO EMULADOR ---
            self.lbl_emulador_status = ctk.CTkLabel(self, text=self._("emu_status_checking"), font=ctk.CTkFont(size=14, weight="bold"))
            self.lbl_emulador_status.pack(pady=(2, 5))

            # --- BOTÕES DE AÇÃO PRINCIPAL ---
            self.frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
            self.frame_botoes.pack(pady=(0, 10))

            self.btn_atualizar = ctk.CTkButton(self.frame_botoes, text=self._("btn_verify"), width=220, height=38, font=ctk.CTkFont(weight="bold"), command=lambda: self.preparar_motor("atualizar"))
            self.btn_atualizar.grid(row=0, column=0, padx=10)

            self.btn_rollback = ctk.CTkButton(self.frame_botoes, text=self._("btn_rollback"), width=180, height=38, fg_color="#8B0000", hover_color="#A52A2A", font=ctk.CTkFont(weight="bold"), command=lambda: self.preparar_motor("rollback"))
            self.btn_rollback.grid(row=0, column=1, padx=10)
            self.tt_rollback = ToolTip(self.btn_rollback, "") 

            self.lbl_rodape = ctk.CTkLabel(self, text="Desenvolvido por DaniboySan & Geminix • github.com/dsantanna", text_color="#1E90FF", cursor="hand2", font=ctk.CTkFont(size=11, underline=True))
            self.lbl_rodape.pack(side="bottom", pady=(0, 5))
            self.lbl_rodape.bind("<Button-1>", lambda e: webbrowser.open(f"https://github.com/{REPO_UPDATER}"))

            self.log(f"🚀 Flycast Updater v{VERSION} iniciado. Cinto apertado e pronto para a velocidade sônica!")
            self.atualizar_status_diretorio(self.entry_path.get())
            self.after(200, self.verificar_primeiro_acesso)

        def log(self, mensagem, bypass_console=False):
            try:
                path = self.entry_path.get()
                if path and os.path.exists(path):
                    log_file = os.path.join(path, "flycast_updater.log")
                    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    prefixo = "" if bypass_console else "[LAUNCHER] "
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(f"[{agora}] {prefixo}{mensagem}\n")
                    
                    if hasattr(self, 'textbox_logs') and self.textbox_logs.winfo_exists():
                        self.textbox_logs.configure(state="normal")
                        self.textbox_logs.insert(tk.END, f"[{agora}] {prefixo}{mensagem}\n")
                        self.textbox_logs.see(tk.END)
                        self.textbox_logs.configure(state="disabled")
            except Exception: pass

        def _(self, key, **kwargs):
            fallback = TRANSLATIONS.get("pt", {}).get(key, key)
            texto = TRANSLATIONS.get(self.lang, TRANSLATIONS["pt"]).get(key, fallback)
            if kwargs:
                try: return texto.format(**kwargs)
                except Exception: pass
            return texto

        def mudar_idioma(self, escolha):
            novo_lang = self.lang_map.get(escolha, "pt")
            if novo_lang != self.lang:
                self.log(f"🌐 Idioma alterado em tempo real pelo usuário para: {escolha}")
                self.lang = novo_lang
                self.config_atual["language"] = novo_lang
                self.salvar_estado_atual()
                self.atualizar_textos_ui()

        def atualizar_textos_ui(self):
            """Atualiza todos os textos da interface instantaneamente sem reiniciar."""
            self.label_sub.configure(text=self._("title_sub"))
            self.btn_help.configure(text=self._("btn_help"))
            self.tt_help.update_text(self._("tt_help"))
            
            # Aba Atualização
            self.label_path.configure(text=self._("lbl_path"))
            self.entry_path.configure(state="normal")
            ToolTip(self.entry_path, self._("tt_path"))
            self.entry_path.configure(state="readonly")
            self.btn_path.configure(text=self._("btn_browse"))
            self.label_branch.configure(text=self._("lbl_branch"))
            self.lbl_dev_desc.configure(text=self._("rb_dev_desc"))
            self.lbl_master_desc.configure(text=self._("rb_master_desc"))
            self.switch_desktop.configure(text=self._("sw_desk"))
            self.switch_startup.configure(text=self._("sw_start"))
            self.switch_nogui.configure(text=self._("sw_nogui"))
            self.btn_reconfig.configure(text=self._("btn_reconfig"))

            # Aba Emulador
            self.label_roms_title.configure(text=self._("lbl_roms"))
            self.btn_roms.configure(text=self._("btn_browse"))
            self.switch_custom_paths.configure(text=self._("sw_custom_paths"))
            self.lbl_bios_path.configure(text=self._("lbl_bios_path"))
            self.btn_bios_path.configure(text=self._("btn_browse"))
            self.lbl_vmu_path.configure(text=self._("lbl_vmu_path"))
            self.btn_vmu_path.configure(text=self._("btn_browse"))
            self.lbl_state_path.configure(text=self._("lbl_state_path"))
            self.btn_state_path.configure(text=self._("btn_browse"))
            self.lbl_save_path.configure(text=self._("lbl_save_path"))
            self.btn_save_path.configure(text=self._("btn_browse"))
            self.label_ra_title.configure(text=self._("lbl_ra"))
            self.switch_ra.configure(text=self._("sw_ra"))
            self.lbl_ra_user.configure(text=self._("lbl_user"))
            self.lbl_ra_pass.configure(text=self._("lbl_pass"))
            self.switch_hardcore.configure(text=self._("sw_hard"))
            self.label_qol_title.configure(text=self._("lbl_qol"))
            self.switch_vmu.configure(text=self._("sw_vmu"))
            self.switch_boxart.configure(text=self._("sw_box"))
            self.switch_vga.configure(text=self._("sw_vga"))
            self.switch_discord.configure(text=self._("sw_disc"))
            self.switch_osd_vmu.configure(text=self._("sw_osd"))
            self.switch_vmu_sound.configure(text=self._("sw_vmu_snd"))
            self.btn_salvar_config_emu.configure(text=self._("btn_save_emu"))

            # Aba Vídeo
            self.label_video_title.configure(text=self._("lbl_vid_title"))
            self.label_video_aviso.configure(text=self._("lbl_vid_warn"))
            self.lbl_api.configure(text=self._("lbl_api"))
            self.lbl_res.configure(text=self._("lbl_res"))
            self.switch_fullscreen.configure(text=self._("sw_full"))
            self.switch_integer.configure(text=self._("sw_int"))
            self.switch_linear.configure(text=self._("sw_lin"))
            self.switch_vsync.configure(text=self._("sw_vsync"))
            self.btn_salvar_video.configure(text=self._("btn_save_vid"))

            # Aba Saves
            self.label_cloud.configure(text=self._("lbl_cloud"))
            self.switch_mappings.configure(text=self._("sw_map"))
            self.lbl_limit.configure(text=self._("lbl_backup_limit"))
            self.label_saves_title.configure(text=self._("lbl_saves_title"))
            self.label_saves_desc.configure(text=self._("lbl_saves_desc"))
            self.btn_buscar_saves.configure(text=self._("btn_search_saves"))
            self.btn_restaurar_save.configure(text=self._("btn_extract"))

            # Aba Logs
            self.label_logs_title.configure(text=self._("lbl_logs_title"))
            self.btn_refresh_log.configure(text=self._("btn_log_refresh"))
            self.btn_copy_log.configure(text=self._("btn_log_copy"))
            self.btn_clear_log.configure(text=self._("btn_log_clear"))

        def construir_aba_nuvem(self):
            self.frame_path_title = ctk.CTkFrame(self.tab_atualizador, fg_color="transparent")
            self.frame_path_title.pack(fill="x", padx=10, pady=(10, 2))
            
            self.label_path = ctk.CTkLabel(self.frame_path_title, text=self._("lbl_path"), font=ctk.CTkFont(weight="bold"))
            self.label_path.pack(side="left")
            
            self.lbl_bios = ctk.CTkLabel(self.frame_path_title, text="BIOS: ...", font=ctk.CTkFont(size=12, weight="bold"))
            self.lbl_bios.pack(side="right")
            ToolTip(self.lbl_bios, self._("tt_bios"))

            self.frame_path = ctk.CTkFrame(self.tab_atualizador, fg_color="transparent")
            self.frame_path.pack(fill="x", padx=10, pady=(0, 10))
            self.frame_path.columnconfigure(0, weight=1)

            self.entry_path = ctk.CTkEntry(self.frame_path)
            self.entry_path.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            self.entry_path.configure(state="readonly") 
            ToolTip(self.entry_path, self._("tt_path"))

            self.btn_path = ctk.CTkButton(self.frame_path, text=self._("btn_browse"), width=80, command=self.escolher_diretorio)
            self.btn_path.grid(row=0, column=1)

            self.label_branch = ctk.CTkLabel(self.tab_atualizador, text=self._("lbl_branch"), font=ctk.CTkFont(weight="bold"))
            self.label_branch.pack(anchor="w", padx=10, pady=(5, 2))

            self.branch_var = ctk.StringVar(value=self.config_atual.get("branch", "dev").lower())

            self.frame_branches = ctk.CTkFrame(self.tab_atualizador, fg_color="transparent")
            self.frame_branches.pack(fill="x", padx=10, pady=(0, 10))
            self.frame_branches.columnconfigure(0, weight=1)
            self.frame_branches.columnconfigure(1, weight=1)

            self.rb_dev = ctk.CTkRadioButton(self.frame_branches, text="Branch Dev", font=ctk.CTkFont(weight="bold"), variable=self.branch_var, value="dev", command=self.ao_trocar_branch)
            self.rb_dev.grid(row=0, column=0, sticky="w", padx=(0, 10))
            self.lbl_dev_desc = ctk.CTkLabel(self.frame_branches, text=self._("rb_dev_desc"), text_color="gray", font=ctk.CTkFont(size=11), justify="left")
            self.lbl_dev_desc.grid(row=1, column=0, sticky="nw", padx=(28, 0))
            ToolTip(self.rb_dev, self._("tt_dev"))

            self.rb_master = ctk.CTkRadioButton(self.frame_branches, text="Branch Master", font=ctk.CTkFont(weight="bold"), variable=self.branch_var, value="master", command=self.ao_trocar_branch)
            self.rb_master.grid(row=0, column=1, sticky="w", padx=(0, 10))
            self.lbl_master_desc = ctk.CTkLabel(self.frame_branches, text=self._("rb_master_desc"), text_color="gray", font=ctk.CTkFont(size=11), justify="left")
            self.lbl_master_desc.grid(row=1, column=1, sticky="nw", padx=(28, 0)) 
            ToolTip(self.rb_master, self._("tt_master"))

            self.switch_desktop = ctk.CTkSwitch(self.tab_atualizador, text=self._("sw_desk"))
            self.switch_desktop.pack(anchor="w", padx=10, pady=(15, 5))
            if self.config_atual.get("create_shortcut", False): self.switch_desktop.select()

            self.switch_startup = ctk.CTkSwitch(self.tab_atualizador, text=self._("sw_start"))
            self.switch_startup.pack(anchor="w", padx=10, pady=5)
            if self.config_atual.get("create_startup", False): self.switch_startup.select()

            self.switch_nogui = ctk.CTkSwitch(self.tab_atualizador, text=self._("sw_nogui"))
            self.switch_nogui.pack(anchor="w", padx=10, pady=5)
            if self.config_atual.get("nogui", False): self.switch_nogui.select()
            ToolTip(self.switch_nogui, self._("tt_nogui"))

            self.btn_reconfig = ctk.CTkButton(self.tab_atualizador, text=self._("btn_reconfig"), width=220, height=28, fg_color="#333", hover_color="#555", command=lambda: self.tabview.set(self._("tab_emu")))
            self.btn_reconfig.pack(anchor="w", padx=10, pady=(15, 5))
            ToolTip(self.btn_reconfig, self._("tt_reconfig"))

        def definir_entry_custom(self, entry_widget, texto):
            entry_widget.configure(state="normal")
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, texto)
            entry_widget.configure(state="readonly")

        def escolher_dir_custom_path(self, entry_widget):
            dir_escolhido = ctk.filedialog.askdirectory()
            if dir_escolhido:
                dir_escolhido = os.path.normpath(dir_escolhido)
                self.definir_entry_custom(entry_widget, dir_escolhido)

        def toggle_custom_paths(self):
            if self.switch_custom_paths.get() == 1:
                self.frame_custom_paths.pack(fill="x", padx=10, pady=(5, 5))
            else:
                self.frame_custom_paths.pack_forget()

        def construir_aba_emulador(self):
            self.label_roms_title = ctk.CTkLabel(self.tab_config, text=self._("lbl_roms"), font=ctk.CTkFont(weight="bold"))
            self.label_roms_title.pack(anchor="w", padx=10, pady=(5, 2))

            self.frame_roms = ctk.CTkFrame(self.tab_config, fg_color="transparent")
            self.frame_roms.pack(fill="x", padx=10, pady=(0, 5))
            self.frame_roms.columnconfigure(0, weight=1)

            self.entry_roms = ctk.CTkEntry(self.frame_roms)
            self.entry_roms.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            self.entry_roms.configure(state="readonly")
            
            self.btn_roms = ctk.CTkButton(self.frame_roms, text=self._("btn_browse"), width=80, command=self.escolher_diretorio_roms)
            self.btn_roms.grid(row=0, column=1)

            self.switch_custom_paths = ctk.CTkSwitch(self.tab_config, text=self._("sw_custom_paths"), command=self.toggle_custom_paths)
            self.switch_custom_paths.pack(anchor="w", padx=10, pady=(5, 5))
            ToolTip(self.switch_custom_paths, self._("tt_custom_paths"))

            self.container_custom_paths = ctk.CTkFrame(self.tab_config, fg_color="transparent", height=0)
            self.container_custom_paths.pack(fill="x", padx=0, pady=0)

            self.frame_custom_paths = ctk.CTkFrame(self.container_custom_paths, fg_color="#2b2b2b", corner_radius=6)
            self.frame_custom_paths.columnconfigure(1, weight=1)

            self.lbl_bios_path = ctk.CTkLabel(self.frame_custom_paths, text=self._("lbl_bios_path"))
            self.lbl_bios_path.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=(5, 2))
            self.entry_bios_path = ctk.CTkEntry(self.frame_custom_paths, state="readonly", height=24)
            self.entry_bios_path.grid(row=0, column=1, sticky="ew", padx=5, pady=(5, 2))
            self.btn_bios_path = ctk.CTkButton(self.frame_custom_paths, text=self._("btn_browse"), width=50, height=24, command=lambda: self.escolher_dir_custom_path(self.entry_bios_path))
            self.btn_bios_path.grid(row=0, column=2, padx=(5, 10), pady=(5, 2))

            self.lbl_vmu_path = ctk.CTkLabel(self.frame_custom_paths, text=self._("lbl_vmu_path"))
            self.lbl_vmu_path.grid(row=1, column=0, sticky="w", padx=(10, 5), pady=2)
            self.entry_vmu_path = ctk.CTkEntry(self.frame_custom_paths, state="readonly", height=24)
            self.entry_vmu_path.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
            self.btn_vmu_path = ctk.CTkButton(self.frame_custom_paths, text=self._("btn_browse"), width=50, height=24, command=lambda: self.escolher_dir_custom_path(self.entry_vmu_path))
            self.btn_vmu_path.grid(row=1, column=2, padx=(5, 10), pady=2)

            self.lbl_state_path = ctk.CTkLabel(self.frame_custom_paths, text=self._("lbl_state_path"))
            self.lbl_state_path.grid(row=2, column=0, sticky="w", padx=(10, 5), pady=2)
            self.entry_state_path = ctk.CTkEntry(self.frame_custom_paths, state="readonly", height=24)
            self.entry_state_path.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
            self.btn_state_path = ctk.CTkButton(self.frame_custom_paths, text=self._("btn_browse"), width=50, height=24, command=lambda: self.escolher_dir_custom_path(self.entry_state_path))
            self.btn_state_path.grid(row=2, column=2, padx=(5, 10), pady=2)

            self.lbl_save_path = ctk.CTkLabel(self.frame_custom_paths, text=self._("lbl_save_path"))
            self.lbl_save_path.grid(row=3, column=0, sticky="w", padx=(10, 5), pady=(2, 10))
            self.entry_save_path = ctk.CTkEntry(self.frame_custom_paths, state="readonly", height=24)
            self.entry_save_path.grid(row=3, column=1, sticky="ew", padx=5, pady=(2, 10))
            self.btn_save_path = ctk.CTkButton(self.frame_custom_paths, text=self._("btn_browse"), width=50, height=24, command=lambda: self.escolher_dir_custom_path(self.entry_save_path))
            self.btn_save_path.grid(row=3, column=2, padx=(5, 10), pady=(2, 10))

            self.frame_divisor = ctk.CTkFrame(self.tab_config, height=2, fg_color="#444")
            self.frame_divisor.pack(fill="x", padx=10, pady=(5, 5))

            self.label_ra_title = ctk.CTkLabel(self.tab_config, text=self._("lbl_ra"), font=ctk.CTkFont(weight="bold"))
            self.label_ra_title.pack(anchor="w", padx=10, pady=(5, 2))

            self.switch_ra = ctk.CTkSwitch(self.tab_config, text=self._("sw_ra"))
            self.switch_ra.pack(anchor="w", padx=10, pady=5)

            self.frame_ra_cred = ctk.CTkFrame(self.tab_config, fg_color="transparent")
            self.frame_ra_cred.pack(fill="x", padx=10, pady=2)
            self.frame_ra_cred.columnconfigure(1, weight=1)

            self.lbl_ra_user = ctk.CTkLabel(self.frame_ra_cred, text=self._("lbl_user"))
            self.lbl_ra_user.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=2)
            self.entry_ra_user = ctk.CTkEntry(self.frame_ra_cred, height=26)
            self.entry_ra_user.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)

            self.lbl_ra_pass = ctk.CTkLabel(self.frame_ra_cred, text=self._("lbl_pass"))
            self.lbl_ra_pass.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=2)
            
            self.entry_ra_pass = ctk.CTkEntry(self.frame_ra_cred, show="*", height=26)
            self.entry_ra_pass.grid(row=1, column=1, sticky="ew", pady=2)
            
            self.btn_toggle_senha = ctk.CTkButton(self.frame_ra_cred, text="👁", width=30, height=26, fg_color="transparent", border_width=1, text_color="gray", hover_color="#444", command=self.toggle_senha_visibility)
            self.btn_toggle_senha.grid(row=1, column=2, padx=(5, 0), pady=2)

            self.switch_hardcore = ctk.CTkSwitch(self.tab_config, text=self._("sw_hard"))
            self.switch_hardcore.pack(anchor="w", padx=10, pady=(5, 5))

            self.frame_divisor2 = ctk.CTkFrame(self.tab_config, height=2, fg_color="#444")
            self.frame_divisor2.pack(fill="x", padx=10, pady=(5, 5))

            self.label_qol_title = ctk.CTkLabel(self.tab_config, text=self._("lbl_qol"), font=ctk.CTkFont(weight="bold"))
            self.label_qol_title.pack(anchor="w", padx=10, pady=(5, 5))

            self.frame_qol = ctk.CTkFrame(self.tab_config, fg_color="transparent")
            self.frame_qol.pack(fill="x", padx=10)
            self.frame_qol.columnconfigure(0, weight=1)
            self.frame_qol.columnconfigure(1, weight=1)

            self.switch_vmu = ctk.CTkSwitch(self.frame_qol, text=self._("sw_vmu"))
            self.switch_vmu.grid(row=0, column=0, sticky="w", pady=5)
            self.switch_boxart = ctk.CTkSwitch(self.frame_qol, text=self._("sw_box"))
            self.switch_boxart.grid(row=0, column=1, sticky="w", pady=5)
            self.switch_vga = ctk.CTkSwitch(self.frame_qol, text=self._("sw_vga"))
            self.switch_vga.grid(row=1, column=0, sticky="w", pady=5)
            self.switch_discord = ctk.CTkSwitch(self.frame_qol, text=self._("sw_disc"))
            self.switch_discord.grid(row=1, column=1, sticky="w", pady=5)
            self.switch_osd_vmu = ctk.CTkSwitch(self.frame_qol, text=self._("sw_osd"))
            self.switch_osd_vmu.grid(row=2, column=0, sticky="w", pady=5)
            self.switch_vmu_sound = ctk.CTkSwitch(self.frame_qol, text=self._("sw_vmu_snd"))
            self.switch_vmu_sound.grid(row=2, column=1, sticky="w", pady=5)

            self.frame_divisor3 = ctk.CTkFrame(self.tab_config, height=2, fg_color="#444")
            self.frame_divisor3.pack(fill="x", padx=10, pady=(15, 5))

            self.btn_salvar_config_emu = ctk.CTkButton(self.tab_config, text=self._("btn_save_emu"), width=280, height=35, font=ctk.CTkFont(weight="bold"), command=self.salvar_configuracoes_emulador)
            self.btn_salvar_config_emu.pack(anchor="center", pady=(10, 10))

        def construir_aba_video(self):
            self.label_video_title = ctk.CTkLabel(self.tab_video, text=self._("lbl_vid_title"), font=ctk.CTkFont(size=16, weight="bold"))
            self.label_video_title.pack(anchor="w", padx=10, pady=(15, 5))

            self.label_video_aviso = ctk.CTkLabel(self.tab_video, text=self._("lbl_vid_warn"), text_color="#FFD700", justify="left")
            self.label_video_aviso.pack(anchor="w", padx=10, pady=(0, 15))

            self.frame_video_options = ctk.CTkFrame(self.tab_video, fg_color="transparent")
            self.frame_video_options.pack(fill="x", padx=10)

            self.api_var = ctk.StringVar(value="DirectX 11")

            self.lbl_api = ctk.CTkLabel(self.frame_video_options, text=self._("lbl_api"), font=ctk.CTkFont(weight="bold"))
            self.lbl_api.grid(row=0, column=0, sticky="w", pady=(5, 0), padx=(0, 10))

            self.frame_api_rb = ctk.CTkFrame(self.frame_video_options, fg_color="transparent")
            self.frame_api_rb.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 15))

            self.rb_opengl = ctk.CTkRadioButton(self.frame_api_rb, text="OpenGL", variable=self.api_var, value="OpenGL")
            self.rb_opengl.pack(side="left", padx=(0, 15))
            ToolTip(self.rb_opengl, self._("tt_opengl"))
            
            self.rb_vulkan = ctk.CTkRadioButton(self.frame_api_rb, text="Vulkan", variable=self.api_var, value="Vulkan")
            self.rb_vulkan.pack(side="left", padx=(0, 15))
            ToolTip(self.rb_vulkan, self._("tt_vulkan"))
            
            self.rb_dx9 = ctk.CTkRadioButton(self.frame_api_rb, text="DirectX 9", variable=self.api_var, value="DirectX 9")
            self.rb_dx9.pack(side="left", padx=(0, 15))
            ToolTip(self.rb_dx9, self._("tt_dx9"))
            
            self.rb_dx11 = ctk.CTkRadioButton(self.frame_api_rb, text="DirectX 11", variable=self.api_var, value="DirectX 11")
            self.rb_dx11.pack(side="left", padx=(0, 15))
            ToolTip(self.rb_dx11, self._("tt_dx11"))

            self.lbl_res = ctk.CTkLabel(self.frame_video_options, text=self._("lbl_res"))
            self.lbl_res.grid(row=2, column=0, sticky="w", pady=5, padx=(0, 10))
            self.combo_res = ctk.CTkComboBox(self.frame_video_options, values=[
                "640x480 (Nativo)", "960x720 (1.5x)", "1280x960 (2x)", 
                "1440x1080 (3x)", "1920x1440 (4x)", "2880x2160 (6x)"
            ], state="readonly", width=180)
            self.combo_res.grid(row=2, column=1, sticky="w", pady=5)
            self.combo_res.set("640x480 (Nativo)")

            self.switch_fullscreen = ctk.CTkSwitch(self.frame_video_options, text=self._("sw_full"))
            self.switch_fullscreen.grid(row=3, column=0, columnspan=2, sticky="w", pady=(15, 5))
            self.switch_integer = ctk.CTkSwitch(self.frame_video_options, text=self._("sw_int"))
            self.switch_integer.grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
            self.switch_linear = ctk.CTkSwitch(self.frame_video_options, text=self._("sw_lin"))
            self.switch_linear.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
            self.switch_vsync = ctk.CTkSwitch(self.frame_video_options, text=self._("sw_vsync"))
            self.switch_vsync.grid(row=6, column=0, columnspan=2, sticky="w", pady=5)

            self.btn_salvar_video = ctk.CTkButton(self.tab_video, text=self._("btn_save_vid"), width=280, height=35, font=ctk.CTkFont(weight="bold"), command=self.salvar_configuracoes_video)
            self.btn_salvar_video.pack(pady=(30, 10))

        def construir_aba_saves(self):
            self.label_cloud = ctk.CTkLabel(self.tab_saves, text=self._("lbl_cloud"), font=ctk.CTkFont(weight="bold", size=14))
            self.label_cloud.pack(anchor="w", padx=10, pady=(15, 2))
            
            self.cloud_var = ctk.StringVar(value="nenhum")
            self.frame_cloud = ctk.CTkFrame(self.tab_saves, fg_color="transparent")
            self.frame_cloud.pack(fill="x", padx=10, pady=(0, 5))

            has_gdrive = self.verificar_caminho_nuvem("Google Drive")
            has_onedrive = self.verificar_caminho_nuvem("OneDrive")

            self.rb_cloud_none = ctk.CTkRadioButton(self.frame_cloud, text=self._("rb_none"), font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="nenhum")
            self.rb_cloud_none.pack(side="left", padx=(0, 15))

            self.rb_cloud_gdrive = ctk.CTkRadioButton(self.frame_cloud, text="Google Drive", font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="gdrive")
            self.rb_cloud_gdrive.pack(side="left", padx=(0, 15))
            if not has_gdrive: self.rb_cloud_gdrive.configure(state="disabled")

            self.rb_cloud_onedrive = ctk.CTkRadioButton(self.frame_cloud, text="OneDrive", font=ctk.CTkFont(weight="bold"), variable=self.cloud_var, value="onedrive")
            self.rb_cloud_onedrive.pack(side="left", padx=(0, 15))
            if not has_onedrive: self.rb_cloud_onedrive.configure(state="disabled")

            nuvem_salva = self.config_atual.get("cloud_provider", "nenhum")
            if nuvem_salva == "gdrive" and has_gdrive: self.cloud_var.set("gdrive")
            elif nuvem_salva == "onedrive" and has_onedrive: self.cloud_var.set("onedrive")
            else: self.cloud_var.set("nenhum")

            self.switch_mappings = ctk.CTkSwitch(self.tab_saves, text=self._("sw_map"))
            self.switch_mappings.pack(anchor="w", padx=10, pady=(5, 10))
            if self.config_atual.get("backup_mappings", False): self.switch_mappings.select()

            self.frame_limit = ctk.CTkFrame(self.tab_saves, fg_color="transparent")
            self.frame_limit.pack(fill="x", padx=10, pady=(0, 10))
            self.lbl_limit = ctk.CTkLabel(self.frame_limit, text=self._("lbl_backup_limit"))
            self.lbl_limit.pack(side="left")
            
            self.combo_limit = ctk.CTkComboBox(self.frame_limit, values=["1", "3", "5", "10", "15", self._("limit_unlimited")], width=100, state="readonly", command=lambda x: self.salvar_estado_atual())
            self.combo_limit.pack(side="left", padx=10)
            
            val_salvo = self.config_atual.get("backup_limit", "5")
            if val_salvo in ["Ilimitado", "Unlimited", "Illimité", "Unbegrenzt", "无限制", "無制限", "Неограничено", "غير محدود", "असीमित"]:
                self.combo_limit.set(self._("limit_unlimited"))
            elif val_salvo in ["1", "3", "5", "10", "15"]:
                self.combo_limit.set(val_salvo)
            else:
                self.combo_limit.set("5")

            self.frame_divisor = ctk.CTkFrame(self.tab_saves, height=2, fg_color="#444")
            self.frame_divisor.pack(fill="x", padx=10, pady=(5, 10))

            self.label_saves_title = ctk.CTkLabel(self.tab_saves, text=self._("lbl_saves_title"), font=ctk.CTkFont(size=14, weight="bold"))
            self.label_saves_title.pack(anchor="w", padx=10, pady=(5, 5))
            
            self.label_saves_desc = ctk.CTkLabel(self.tab_saves, text=self._("lbl_saves_desc"), text_color="gray", justify="left")
            self.label_saves_desc.pack(anchor="w", padx=10, pady=(0, 10))

            self.frame_saves_list = ctk.CTkFrame(self.tab_saves, fg_color="transparent")
            self.frame_saves_list.pack(fill="x", padx=10, pady=5)

            self.btn_buscar_saves = ctk.CTkButton(self.frame_saves_list, text=self._("btn_search_saves"), width=140, command=self.buscar_backups_saves)
            self.btn_buscar_saves.pack(side="left", padx=(0, 10))

            self.combo_backups = ctk.CTkComboBox(self.frame_saves_list, values=[self._("combo_saves_def")], width=350, state="readonly")
            self.combo_backups.pack(side="left", fill="x", expand=True)
            self.combo_backups.set(self._("combo_saves_def"))

            self.btn_restaurar_save = ctk.CTkButton(self.tab_saves, text=self._("btn_extract"), width=280, height=35, font=ctk.CTkFont(weight="bold"), fg_color="#228B22", hover_color="#006400", command=self.restaurar_backup_selecionado)
            self.btn_restaurar_save.pack(pady=(20, 10))
            self.btn_restaurar_save.configure(state="disabled")
            self.arquivos_backup_encontrados = {}

        def construir_aba_logs(self):
            self.label_logs_title = ctk.CTkLabel(self.tab_logs, text=self._("lbl_logs_title"), font=ctk.CTkFont(size=16, weight="bold"))
            self.label_logs_title.pack(anchor="w", padx=10, pady=(10, 0))

            self.frame_logs_botoes = ctk.CTkFrame(self.tab_logs, fg_color="transparent")
            self.frame_logs_botoes.pack(fill="x", padx=10, pady=5)

            self.btn_refresh_log = ctk.CTkButton(self.frame_logs_botoes, text=self._("btn_log_refresh"), width=100, command=self.carregar_logs)
            self.btn_refresh_log.pack(side="left", padx=5)

            self.btn_copy_log = ctk.CTkButton(self.frame_logs_botoes, text=self._("btn_log_copy"), width=100, command=self.copiar_logs)
            self.btn_copy_log.pack(side="left", padx=5)

            self.btn_clear_log = ctk.CTkButton(self.frame_logs_botoes, text=self._("btn_log_clear"), width=100, fg_color="#8B0000", hover_color="#A52A2A", command=self.limpar_logs)
            self.btn_clear_log.pack(side="left", padx=5)

            self.textbox_logs = ctk.CTkTextbox(self.tab_logs, width=540, height=450, state="disabled")
            self.textbox_logs.pack(padx=10, pady=5, fill="both", expand=True)

        def carregar_logs(self):
            log_path = os.path.join(self.entry_path.get(), "flycast_updater.log")
            self.textbox_logs.configure(state="normal")
            self.textbox_logs.delete("1.0", tk.END)
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        self.textbox_logs.insert(tk.END, f.read())
                    self.textbox_logs.see(tk.END)
                except Exception:
                    pass
            else:
                self.textbox_logs.insert(tk.END, self._("log_not_found"))
            self.textbox_logs.configure(state="disabled")

        def copiar_logs(self):
            self.clipboard_clear()
            self.clipboard_append(self.textbox_logs.get("1.0", tk.END))
            mb.showinfo("Copiado", self._("msg_success"), parent=self)

        def limpar_logs(self):
            log_path = os.path.join(self.entry_path.get(), "flycast_updater.log")
            if os.path.exists(log_path):
                try:
                    os.remove(log_path)
                    self.carregar_logs()
                    self.log("🗑️ Log limpo pelo usuário.")
                except Exception:
                    pass

        def salvar_estado_atual(self):
            self.config_atual["branch"] = self.branch_var.get()
            self.config_atual["create_shortcut"] = self.switch_desktop.get() == 1
            self.config_atual["create_startup"] = self.switch_startup.get() == 1
            self.config_atual["install_path"] = self.entry_path.get()
            self.config_atual["cloud_provider"] = self.cloud_var.get() if self.cloud_var.get() != "nenhum" else None
            self.config_atual["nogui"] = self.switch_nogui.get() == 1
            self.config_atual["language"] = self.lang
            self.config_atual["backup_mappings"] = self.switch_mappings.get() == 1
            self.config_atual["backup_limit"] = self.combo_limit.get()
            
            salvar_configuracao(self.config_atual)

        def toggle_senha_visibility(self):
            if self.entry_ra_pass.cget("show") == "*":
                self.entry_ra_pass.configure(show="")
                self.btn_toggle_senha.configure(text="🙈") 
            else:
                self.entry_ra_pass.configure(show="*")
                self.btn_toggle_senha.configure(text="👁")

        def verificar_primeiro_acesso(self):
            completo = self.config_atual.get("setup_completed", False)
            recusado = self.config_atual.get("setup_declined", False)
            
            if not completo and not recusado:
                self.log("🚀 Primeiro acesso detectado. Exibindo assistente de configuração.")
                resposta = mb.askyesno(
                    "Flycast Updater - v4.1 (Another Day Edition)",
                    "Bem-vindo / Welcome!\n\nDeseja ajuda para configurar rapidamente a pasta de ROMs e o RetroAchievements agora?",
                    parent=self
                )
                if resposta:
                    self.tabview.set(self._("tab_emu"))
                    self.config_atual["setup_completed"] = True
                else:
                    self.config_atual["setup_declined"] = True
                self.salvar_estado_atual()
            
            self.carregar_logs()

        def procurar_e_instalar_bios(self, install_path, custom_bios_path):
            self.log("🔍 Usuário abriu seletor de arquivos de BIOS.")
            arquivo = ctk.filedialog.askopenfilename(
                title="Select BIOS (.bin) or ZIP (.zip)",
                filetypes=[("BIOS / ZIP", "*.bin *.zip"), ("All files", "*.*")]
            )
            if not arquivo:
                self.log("❌ Seleção de BIOS cancelada pelo usuário.")
                return
                
            target_dir = custom_bios_path if custom_bios_path else os.path.join(install_path, "data")
            os.makedirs(target_dir, exist_ok=True)
            self.log(f"📂 Diretório alvo da BIOS: {target_dir}")
            
            if arquivo.lower().endswith(".zip"):
                self.log(f"📦 Extraindo BIOS de arquivo ZIP: {arquivo}")
                try:
                    with zipfile.ZipFile(arquivo, 'r') as zip_ref:
                        encontrou = False
                        for file_info in zip_ref.infolist():
                            basename = os.path.basename(file_info.filename).lower()
                            if basename in ['dc_boot.bin', 'dc_flash.bin']:
                                source = zip_ref.open(file_info.filename)
                                target = open(os.path.join(target_dir, basename), "wb")
                                with source, target:
                                    shutil.copyfileobj(source, target)
                                encontrou = True
                                self.log(f"✔️ Extraído com sucesso: {basename}")
                        if encontrou:
                            mb.showinfo("Sucesso", self._("msg_bios_zip_success"), parent=self)
                        else:
                            self.log("⚠️ Nenhuma BIOS (dc_boot.bin ou dc_flash.bin) encontrada dentro do ZIP.")
                            mb.showwarning("Aviso", "O ZIP não continha dc_boot.bin ou dc_flash.bin.", parent=self)
                except Exception as e:
                    self.log(f"❌ Erro fatal ao extrair ZIP da BIOS: {e}")
                    mb.showerror("Erro", f"Erro: {e}", parent=self)
            elif arquivo.lower().endswith(".bin"):
                self.log(f"📄 Arquivo BIN selecionado: {arquivo}")
                orig_basename = os.path.basename(arquivo).lower()
                target_basename = orig_basename
                
                if "boot" in orig_basename and "dc_boot.bin" not in orig_basename:
                    target_basename = "dc_boot.bin"
                    self.log(f"🔄 Auto-renomeando {orig_basename} para dc_boot.bin")
                elif "flash" in orig_basename and "dc_flash.bin" not in orig_basename:
                    target_basename = "dc_flash.bin"
                    self.log(f"🔄 Auto-renomeando {orig_basename} para dc_flash.bin")
                
                try:
                    shutil.copy(arquivo, os.path.join(target_dir, target_basename))
                    self.log(f"✔️ {target_basename} copiado com sucesso para a pasta alvo.")
                    
                    has_boot = os.path.exists(os.path.join(target_dir, "dc_boot.bin")) or os.path.exists(os.path.join(target_dir, "DC_BOOT.BIN"))
                    has_flash = os.path.exists(os.path.join(target_dir, "dc_flash.bin")) or os.path.exists(os.path.join(target_dir, "DC_FLASH.BIN"))
                    
                    missing_other = None
                    if not has_boot: missing_other = "dc_boot.bin"
                    elif not has_flash: missing_other = "dc_flash.bin"
                    
                    if missing_other:
                        self.log(f"⚠️ AINDA FALTA a BIOS: {missing_other}")
                        resp = mb.askyesno(self._("title_bios_partial"), self._("msg_bios_partial", missing=missing_other), parent=self)
                        if resp:
                            self.procurar_e_instalar_bios(install_path, custom_bios_path)
                            return
                    else:
                        self.log("✅ Toutes les BIOS nécessaires ont été installées avec succès.")
                        mb.showinfo("Sucesso", self._("msg_bios_bin_success"), parent=self)
                except Exception as e:
                    self.log(f"❌ Erro ao copiar o arquivo BIN da BIOS: {e}")
                    mb.showerror("Erro", f"Erro: {e}", parent=self)
            else:
                self.log("❌ Formato de BIOS não suportado selecionado.")
                mb.showerror("Erro", self._("msg_bios_unsupported"), parent=self)
                
            self.atualizar_status_diretorio(install_path)

        def tratar_bios_ausente(self, path, custom_bios_path, has_boot, has_flash):
            if getattr(self, 'bios_prompt_done', False):
                return
            self.bios_prompt_done = True
            
            missing = []
            if not has_boot: missing.append("dc_boot.bin")
            if not has_flash: missing.append("dc_flash.bin")
            
            if not missing: return
            
            msg = self._("msg_bios_missing", files="\n- ".join(missing))
            resposta = mb.askyesno(self._("title_bios_missing"), msg, parent=self)
            
            if resposta:
                self.procurar_e_instalar_bios(path, custom_bios_path)

        def resolver_bios_mal_posicionada(self, path):
            if getattr(self, 'bios_prompt_done', False):
                return
            self.bios_prompt_done = True
            
            self.log("⚠️ BIOS detectada no diretório raiz do emulador. Oferecendo correção ao usuário.")
            resposta_mover = mb.askyesno(
                "BIOS",
                "Os arquivos da BIOS foram encontrados na pasta raiz do emulador.\n\nO padrão do Flycast é armazená-los na pasta 'data'. Mover automaticamente?",
                parent=self
            )
            
            if resposta_mover:
                pasta_data = os.path.join(path, "data")
                os.makedirs(pasta_data, exist_ok=True)
                try:
                    shutil.move(os.path.join(path, "dc_boot.bin"), os.path.join(pasta_data, "dc_boot.bin"))
                    shutil.move(os.path.join(path, "dc_flash.bin"), os.path.join(pasta_data, "dc_flash.bin"))
                    self.log("✔️ BIOS movida com sucesso para a pasta data.")
                    mb.showinfo("Sucesso", self._("msg_success"), parent=self)
                    self.atualizar_status_diretorio(path)
                except Exception as e:
                    self.log(f"❌ Falha ao tentar mover a BIOS para a pasta data: {e}")
                    pass
            else:
                resposta_config = mb.askyesno(
                    "BIOS",
                    "Deseja registrar essa pasta raiz nas opções do emulador para resolver o aviso?",
                    parent=self
                )
                if resposta_config:
                    self.log("⚙️ Registrando a pasta raiz atual como o Custom Path para BIOS no emu.cfg.")
                    sucesso = atualizar_emu_cfg(install_path=path, bios_path=path)
                    if sucesso:
                        self.atualizar_status_diretorio(path)

        def limpar_backups_antigos(self):
            limite_str = self.config_atual.get("backup_limit", "5")
            if limite_str in ["Ilimitado", "Unlimited", "Illimité", "Unbegrenzt", "无限制", "無制限", "Неограничено", "غير محدود", "असीमित"]:
                return
                
            try:
                limite = int(limite_str)
            except ValueError:
                return

            cloud_prov = self.config_atual.get("cloud_provider", "nenhum")
            if not cloud_prov or cloud_prov == "nenhum": return
            
            caminho_base = None
            if cloud_prov == "gdrive" and cloud_saves:
                caminho_base = cloud_saves.get_gdrive_path()
            elif cloud_prov == "onedrive" and cloud_saves:
                caminho_base = cloud_saves.get_onedrive_path()

            if not caminho_base or not os.path.exists(caminho_base): return

            caminho_nuvem = os.path.join(caminho_base, "Flycast_Saves_Backup")
            if not os.path.exists(caminho_nuvem): return

            arquivos_zip = [f for f in os.listdir(caminho_nuvem) if f.lower().endswith(".zip") and f != "flycast_backup.zip"]
            if len(arquivos_zip) <= limite: return

            self.log(f"🧹 Verificando limite de {limite} backups na nuvem. Total atual: {len(arquivos_zip)}")
            arquivos_zip.sort(key=lambda x: os.path.getmtime(os.path.join(caminho_nuvem, x)))

            excedente = len(arquivos_zip) - limite
            for i in range(excedente):
                file_to_del = os.path.join(caminho_nuvem, arquivos_zip[i])
                try:
                    os.remove(file_to_del)
                    self.log(f"🗑️ Removido backup mais antigo: {arquivos_zip[i]}")
                except Exception as e:
                    self.log(f"❌ Erro ao tentar remover backup antigo ({arquivos_zip[i]}): {e}")

        def buscar_backups_saves(self):
            self.log("🔄 Iniciando varredura por backups salvos na nuvem.")
            cloud_prov = self.cloud_var.get()
            if cloud_prov == "nenhum": 
                self.log("⚠️ Busca de backups cancelada: Nenhuma nuvem configurada.")
                return

            caminho_base = None
            if cloud_prov == "gdrive" and cloud_saves:
                caminho_base = cloud_saves.get_gdrive_path()
            elif cloud_prov == "onedrive" and cloud_saves:
                caminho_base = cloud_saves.get_onedrive_path()

            if not caminho_base or not os.path.exists(caminho_base): 
                self.log(f"❌ Caminho base da nuvem ({cloud_prov}) não encontrado no disco local.")
                return

            caminho_nuvem = os.path.join(caminho_base, "Flycast_Saves_Backup")
            
            if not os.path.exists(caminho_nuvem):
                self.combo_backups.configure(values=[self._("log_not_found")])
                self.combo_backups.set(self._("log_not_found"))
                self.btn_restaurar_save.configure(state="disabled")
                self.log("⚠️ Pasta 'Flycast_Saves_Backup' ainda não existe na nuvem.")
                return

            try:
                self.limpar_backups_antigos() 
                
                arquivos_zip = []
                for f in os.listdir(caminho_nuvem):
                    if f.lower().endswith(".zip") and f != "flycast_backup.zip":
                        arquivos_zip.append(f)
                
                if not arquivos_zip:
                    self.combo_backups.configure(values=[self._("log_not_found")])
                    self.combo_backups.set(self._("log_not_found"))
                    self.btn_restaurar_save.configure(state="disabled")
                    self.log("⚠️ Nenhum arquivo .zip de backup encontrado.")
                    return

                arquivos_zip.sort(key=lambda x: os.path.getmtime(os.path.join(caminho_nuvem, x)), reverse=True)

                self.arquivos_backup_encontrados = {}
                nomes_exibicao = []
                for f in arquivos_zip:
                    caminho_completo = os.path.join(caminho_nuvem, f)
                    data_mod = datetime.datetime.fromtimestamp(os.path.getmtime(caminho_completo)).strftime('%d/%m/%Y %H:%M')
                    nome_exib = f"{f}  [{data_mod}]"
                    nomes_exibicao.append(nome_exib)
                    self.arquivos_backup_encontrados[nome_exib] = caminho_completo

                self.combo_backups.configure(values=nomes_exibicao)
                self.combo_backups.set(nomes_exibicao[0])
                self.btn_restaurar_save.configure(state="normal")
                self.log(f"✔️ {len(arquivos_zip)} arquivos de backup encontrados e listados.")

            except Exception as e:
                self.log(f"❌ Erro ao buscar backups: {e}")

        def restaurar_backup_selecionado(self):
            selecionado = self.combo_backups.get()
            caminho_zip = self.arquivos_backup_encontrados.get(selecionado)

            if not caminho_zip or not os.path.exists(caminho_zip): return

            install_path = self.entry_path.get()
            if not install_path or not os.path.exists(install_path): return
            
            resposta = mb.askyesno("Confirmar", f"Extrair arquivos de:\n{selecionado}\n\nContinuar?", parent=self)
            if not resposta: return
            
            self.log(f"📥 Iniciando restauração do backup: {selecionado}")
            
            custom_vmu = ""
            custom_save = ""
            cfg_path = os.path.join(install_path, "emu.cfg")
            if not os.path.exists(cfg_path):
                cfg_path = os.path.join(install_path, "data", "emu.cfg")
                
            if os.path.exists(cfg_path):
                try:
                    c = configparser.RawConfigParser(strict=False)
                    c.read(cfg_path, encoding='utf-8')
                    if c.has_section('config'):
                        custom_vmu = c.get('config', 'Dreamcast.VmuPath', fallback='')
                        custom_save = c.get('config', 'Dreamcast.SavePath', fallback='')
                except Exception: pass

            if custom_vmu and not os.path.isabs(custom_vmu): custom_vmu = os.path.join(install_path, custom_vmu)
            if custom_save and not os.path.isabs(custom_save): custom_save = os.path.join(install_path, custom_save)
                
            try:
                with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                    for file_info in zip_ref.infolist():
                        if file_info.filename.endswith('/'): continue
                        basename = os.path.basename(file_info.filename)
                        
                        if file_info.filename.startswith('mappings/') or basename.endswith('.cfg'):
                            dest_dir = os.path.join(install_path, "mappings")
                        else:
                            if basename.startswith('vmu') and custom_vmu:
                                dest_dir = custom_vmu
                            elif custom_save:
                                dest_dir = custom_save
                            else:
                                dest_dir = os.path.join(install_path, "data")
                                
                        os.makedirs(dest_dir, exist_ok=True)
                        with zip_ref.open(file_info.filename) as source, open(os.path.join(dest_dir, basename), "wb") as target:
                            shutil.copyfileobj(source, target)

                self.log(f"✔️ Restauração do backup concluída com sucesso.")
                mb.showinfo("Sucesso", self._("msg_success"), parent=self)
            except Exception as e:
                self.log(f"❌ Erro fatal durante a extração do backup: {e}")
                mb.showerror("Erro", f"Erro na extração: {e}", parent=self)

        def carregar_dados_atuais_emu_cfg(self):
            install_path = os.path.normpath(self.entry_path.get())
            
            def_bios = os.path.join(install_path, "bios")
            def_vmu = os.path.join(install_path, "vmu")
            def_state = os.path.join(install_path, "save_state")
            def_save = os.path.join(install_path, "saves")
            
            self.definir_entry_custom(self.entry_bios_path, def_bios)
            self.definir_entry_custom(self.entry_vmu_path, def_vmu)
            self.definir_entry_custom(self.entry_state_path, def_state)
            self.definir_entry_custom(self.entry_save_path, def_save)
            
            self.switch_custom_paths.deselect()
            self.toggle_custom_paths()

            caminhos = [os.path.join(install_path, "emu.cfg"), os.path.join(install_path, "data", "emu.cfg")]
            for p in caminhos:
                if os.path.exists(p):
                    try:
                        config = configparser.RawConfigParser(strict=False)
                        config.optionxform = str
                        config.read(p, encoding='utf-8')
                        self.log(f"⚙️ Lendo arquivo de configuração: {p}")
                        
                        if config.has_section('config'):
                            if config.has_option('config', 'Dreamcast.ContentPath'):
                                self.entry_roms.configure(state="normal")
                                self.entry_roms.delete(0, 'end')
                                self.entry_roms.insert(0, config.get('config', 'Dreamcast.ContentPath').replace("/", "\\"))
                                self.entry_roms.configure(state="readonly")
                                
                            bios_p = config.get('config', 'Dreamcast.BiosPath', fallback='')
                            vmu_p = config.get('config', 'Dreamcast.VmuPath', fallback='')
                            state_p = config.get('config', 'Dreamcast.SavestatePath', fallback='')
                            save_p = config.get('config', 'Dreamcast.SavePath', fallback='')
                            
                            if bios_p or vmu_p or state_p or save_p:
                                self.switch_custom_paths.select()
                                self.toggle_custom_paths()
                                if bios_p: self.definir_entry_custom(self.entry_bios_path, bios_p)
                                if vmu_p: self.definir_entry_custom(self.entry_vmu_path, vmu_p)
                                if state_p: self.definir_entry_custom(self.entry_state_path, state_p)
                                if save_p: self.definir_entry_custom(self.entry_save_path, save_p)

                            if config.get('config', 'PerGameVmu', fallback='no').lower() == 'yes': self.switch_vmu.select()
                            if config.get('config', 'FetchBoxart', fallback='no').lower() == 'yes': self.switch_boxart.select()
                            if config.get('config', 'Dreamcast.Cable', fallback='3') == '0': self.switch_vga.select()
                            if config.get('config', 'DiscordPresence', fallback='no').lower() == 'yes': self.switch_discord.select()
                            if config.get('config', 'ShowOsdVmu', fallback='no').lower() == 'yes': self.switch_osd_vmu.select()
                            
                        if config.has_section('achievements'):
                            if config.get('achievements', 'Enabled', fallback='no').lower() == 'yes': self.switch_ra.select()
                            if config.get('achievements', 'HardcoreMode', fallback='no').lower() == 'yes': self.switch_hardcore.select()
                            if config.has_option('achievements', 'UserName'):
                                self.entry_ra_user.insert(0, config.get('achievements', 'UserName'))
                            if config.has_option('achievements', 'Token'):
                                token_lido = config.get('achievements', 'Token')
                                self.entry_ra_pass.insert(0, token_lido)
                                self.token_ra_salvo = token_lido 

                        if config.has_section('audio'):
                            if config.get('audio', 'VmuSound', fallback='no').lower() == 'yes': self.switch_vmu_sound.select()
                            
                        if config.has_section('config'):
                            if config.has_option('config', 'pvr.rend'):
                                val = config.get('config', 'pvr.rend')
                                api_rev_map = {"0": "OpenGL", "1": "DirectX 9", "2": "DirectX 11", "4": "Vulkan"}
                                self.api_var.set(api_rev_map.get(val, "DirectX 11"))
                                
                            if config.has_option('config', 'rend.Resolution'):
                                val = config.get('config', 'rend.Resolution')
                                res_map = {
                                    "480": "640x480 (Nativo)", 
                                    "720": "960x720 (1.5x)", 
                                    "960": "1280x960 (2x)", 
                                    "1080": "1440x1080 (3x)", 
                                    "1440": "1920x1440 (4x)", 
                                    "2160": "2880x2160 (6x)"
                                }
                                self.combo_res.set(res_map.get(val, "640x480 (Nativo)"))

                            if config.get('config', 'rend.IntegerScale', fallback='no').lower() == 'yes': self.switch_integer.select()
                            if config.get('config', 'rend.LinearInterpolation', fallback='no').lower() == 'yes': self.switch_linear.select()
                            if config.get('config', 'rend.vsync', fallback='no').lower() == 'yes': self.switch_vsync.select()

                        if config.has_section('window'):
                            if config.get('window', 'fullscreen', fallback='no').lower() == 'yes': self.switch_fullscreen.select()

                        break
                    except Exception as e:
                        self.log(f"❌ Erro ao ler emu.cfg: {e}")

        def escolher_diretorio_roms(self):
            dir_escolhido = ctk.filedialog.askdirectory()
            if dir_escolhido:
                dir_escolhido = os.path.normpath(dir_escolhido)
                self.entry_roms.configure(state="normal")
                self.entry_roms.delete(0, 'end')
                self.entry_roms.insert(0, dir_escolhido)
                self.entry_roms.configure(state="readonly")
                self.log(f"📁 Pasta de ROMs definida para: {dir_escolhido}")

        def salvar_configuracoes_emulador(self):
            install_path = self.entry_path.get()
            roms_path = self.entry_roms.get()
            ra_on = self.switch_ra.get() == 1
            ra_user = self.entry_ra_user.get().strip()
            ra_pass_input = self.entry_ra_pass.get().strip()
            ra_hard = self.switch_hardcore.get() == 1
            
            qol_vmu = self.switch_vmu.get() == 1
            qol_boxart = self.switch_boxart.get() == 1
            qol_vga = self.switch_vga.get() == 1
            qol_discord = self.switch_discord.get() == 1
            qol_osd_vmu = self.switch_osd_vmu.get() == 1
            qol_vmu_sound = self.switch_vmu_sound.get() == 1

            use_custom = self.switch_custom_paths.get() == 1
            bios_p = self.entry_bios_path.get() if use_custom else ""
            vmu_p = self.entry_vmu_path.get() if use_custom else ""
            state_p = self.entry_state_path.get() if use_custom else ""
            save_p = self.entry_save_path.get() if use_custom else ""

            ra_token_final = ""
            if ra_on and ra_user and ra_pass_input:
                if getattr(self, 'token_ra_salvo', '') == ra_pass_input:
                    ra_token_final = self.token_ra_salvo
                else:
                    self.log(f"⏳ Solicitando novo Token para a conta RetroAchievements: {ra_user}")
                    self.btn_salvar_config_emu.configure(text="⏳ Autenticando...")
                    self.update() 
                    token_api = obter_token_retroachievements(ra_user, ra_pass_input)
                    if token_api:
                        ra_token_final = token_api
                        self.token_ra_salvo = token_api
                        self.log("✔️ Autenticação bem sucedida. Token recebido.")
                    else:
                        self.log("❌ Falha na autenticação do RetroAchievements. Credenciais inválidas.")
                        mb.showerror("Login", self._("msg_error"), parent=self)
                        self.btn_salvar_config_emu.configure(text=self._("btn_save_emu"))
                        return 
            else:
                ra_token_final = ra_pass_input

            sucesso = atualizar_emu_cfg(
                install_path=install_path, roms_path=roms_path if roms_path else None,
                ra_enabled=ra_on, ra_user=ra_user, ra_pass=ra_token_final, ra_hardcore=ra_hard,
                vmu_individual=qol_vmu, fetch_boxart=qol_boxart, vga_cable=qol_vga,
                discord_presence=qol_discord, show_osd_vmu=qol_osd_vmu, vmu_sound=qol_vmu_sound,
                bios_path=bios_p, vmu_path=vmu_p, state_path=state_p, save_path=save_p
            )

            self.config_atual["setup_completed"] = True
            self.salvar_estado_atual()
            self.btn_salvar_config_emu.configure(text=self._("btn_save_emu"))

            if sucesso:
                self.log("💾 Todas as configurações do Emulador foram gravadas no emu.cfg com sucesso.")
                mb.showinfo("Sucesso", self._("msg_success"), parent=self)
            else:
                self.log("❌ Falha crítica ao tentar gravar as configurações no emu.cfg.")
                mb.showerror("Erro", self._("msg_error"), parent=self)

        def salvar_configuracoes_video(self):
            install_path = self.entry_path.get()
            api = self.api_var.get()
            res_str = self.combo_res.get()
            res_val = "480"
            if "720" in res_str: res_val = "720"
            elif "960" in res_str: res_val = "960"
            elif "1080" in res_str: res_val = "1080"
            elif "1440" in res_str: res_val = "1440"
            elif "2160" in res_str: res_val = "2160"

            full = self.switch_fullscreen.get() == 1
            integer = self.switch_integer.get() == 1
            linear = self.switch_linear.get() == 1
            vsync = self.switch_vsync.get() == 1

            sucesso = atualizar_emu_cfg(
                install_path=install_path, vid_api=api, vid_res=res_val,
                vid_full=full, vid_int=integer, vid_lin=linear, vid_vsync=vsync
            )

            self.salvar_estado_atual()
            if sucesso:
                self.log(f"🖥️ Configurações de vídeo aplicadas (API: {api}, Res: {res_str}, Fullscreen: {full})")
                mb.showinfo("Sucesso", self._("msg_success"), parent=self)
            else:
                self.log("❌ Erro ao salvar as configurações de vídeo.")
                mb.showerror("Erro", self._("msg_error"), parent=self)

        def ao_trocar_branch(self):
            self.log(f"🌿 Branch alterada pelo usuário para: {self.branch_var.get().upper()}")
            self.atualizar_status_diretorio(self.entry_path.get())

        def verificar_caminho_nuvem(self, escolha):
            if not cloud_saves: return False
            caminho = None
            if escolha == "Google Drive": caminho = cloud_saves.get_gdrive_path()
            elif escolha == "OneDrive": caminho = cloud_saves.get_onedrive_path()
            return caminho is not None and os.path.exists(caminho)

        def verificar_versao_em_background(self, path, branch):
            def rotina():
                self.lbl_emulador_status.configure(text=self._("emu_status_checking"), text_color="cyan")
                self.btn_atualizar.configure(text=self._("btn_verify"))
                
                version_file = os.path.join(path, "version.txt")
                local_version = ""
                if os.path.exists(version_file):
                    with open(version_file, "r") as f:
                        local_version = f.read().strip()
                
                if not local_version:
                    self.lbl_emulador_status.configure(text=self._("emu_status_outdated"), text_color="#FFD700")
                    self.btn_atualizar.configure(text=f"🚀 {self._('btn_update_act')}")
                    return

                remote_version = None
                try:
                    if branch == 'master':
                        api_url = "https://api.github.com/repos/flyinghead/flycast/releases/latest"
                        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=3) as response:
                            release = json.loads(response.read().decode('utf-8'))
                            remote_version = release.get("tag_name")
                    else:
                        api_url = "https://api.github.com/repos/flyinghead/flycast/commits?sha=dev&per_page=1"
                        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=3) as response:
                            commits = json.loads(response.read().decode('utf-8'))
                            if commits: remote_version = commits[0]["sha"]
                except Exception:
                    self.lbl_emulador_status.configure(text=self._("emu_status_offline"), text_color="#FFD700")
                    self.btn_atualizar.configure(text=f"🚀 {self._('btn_update_act')}")
                    return

                if remote_version and (local_version == remote_version or local_version.startswith(remote_version)):
                    self.lbl_emulador_status.configure(text=self._("emu_status_updated"), text_color="#00FF7F")
                    self.btn_atualizar.configure(text=f"🚀 {self._('btn_play')}")
                else:
                    self.lbl_emulador_status.configure(text=self._("emu_status_outdated"), text_color="#FFD700")
                    self.btn_atualizar.configure(text=f"🚀 {self._('btn_update_act')}")

            threading.Thread(target=rotina, daemon=True).start()

        def atualizar_status_diretorio(self, path):
            if not path or not os.path.exists(path):
                self.lbl_bios.configure(text=self._("bios_error"), text_color="#FF4C4C")
                self.lbl_emulador_status.configure(text=self._("emu_status_error"), text_color="#FF4C4C")
                self.btn_rollback.configure(state="disabled")
                self.btn_atualizar.configure(text=f"🚀 {self._('btn_install_act')}")
                return
                
            custom_bios_path = None
            caminhos_cfg = [os.path.join(path, "emu.cfg"), os.path.join(path, "data", "emu.cfg")]
            for p in caminhos_cfg:
                if os.path.exists(p):
                    try:
                        config = configparser.RawConfigParser(strict=False)
                        config.optionxform = str
                        config.read(p, encoding='utf-8')
                        if config.has_option('config', 'Dreamcast.BiosPath'):
                            custom_bios_path = config.get('config', 'Dreamcast.BiosPath').strip()
                            if not custom_bios_path: custom_bios_path = None
                        break
                    except: pass

            boot_data = os.path.exists(os.path.join(path, "data", "dc_boot.bin"))
            flash_data = os.path.exists(os.path.join(path, "data", "dc_flash.bin"))
            boot_root = os.path.exists(os.path.join(path, "dc_boot.bin"))
            flash_root = os.path.exists(os.path.join(path, "dc_flash.bin"))
            
            boot_custom = False
            flash_custom = False
            if custom_bios_path:
                if not os.path.isabs(custom_bios_path):
                    custom_bios_path = os.path.join(path, custom_bios_path)
                if os.path.exists(custom_bios_path):
                    boot_custom = os.path.exists(os.path.join(custom_bios_path, "dc_boot.bin"))
                    flash_custom = os.path.exists(os.path.join(custom_bios_path, "dc_flash.bin"))

            if boot_data and flash_data:
                self.lbl_bios.configure(text=self._("bios_ok"), text_color="#00FF7F")
            elif custom_bios_path and boot_custom and flash_custom:
                self.lbl_bios.configure(text=self._("bios_custom"), text_color="#00FF7F")
            elif boot_root and flash_root:
                self.lbl_bios.configure(text=self._("bios_wrong"), text_color="#FFD700")
                self.after(500, lambda: self.resolver_bios_mal_posicionada(path))
            else:
                self.lbl_bios.configure(text=self._("bios_missing"), text_color="#FF4C4C")
                has_boot = boot_data or (custom_bios_path and boot_custom)
                has_flash = flash_data or (custom_bios_path and flash_custom)
                self.after(500, lambda p=path, cb=custom_bios_path, hb=has_boot, hf=has_flash: self.tratar_bios_ausente(p, cb, hb, hf))

            flycast_exe = os.path.join(path, "flycast.exe")
            if os.path.exists(flycast_exe):
                self.btn_atualizar.configure(text=self._("btn_verify"))
                self.verificar_versao_em_background(path, self.branch_var.get())
            else:
                self.lbl_emulador_status.configure(text=self._("emu_status_missing"), text_color="#FF4C4C")
                self.btn_atualizar.configure(text=f"🚀 {self._('btn_install_act')}")

            backup_path = os.path.join(path, "flycast_backup.zip")
            if os.path.exists(backup_path):
                self.btn_rollback.configure(state="normal")
            else:
                self.btn_rollback.configure(state="disabled")

        def escolher_diretorio(self):
            dir_escolhido = ctk.filedialog.askdirectory()
            if dir_escolhido:
                dir_escolhido = os.path.normpath(dir_escolhido)
                self.entry_path.configure(state="normal")
                self.entry_path.delete(0, 'end')
                self.entry_path.insert(0, dir_escolhido)
                self.entry_path.configure(state="readonly")
                self.bios_prompt_done = False 
                self.log(f"📁 Root do emulador modificado para: {dir_escolhido}")
                self.atualizar_status_diretorio(dir_escolhido)
                self.carregar_dados_atuais_emu_cfg()

        def abrir_janela_ajuda(self):
            win_ajuda = ctk.CTkToplevel(self)
            win_ajuda.title("Sobre / About")
            win_ajuda.geometry("550x550")
            win_ajuda.attributes("-topmost", True)
            
            texto_ajuda = (
                f"🌀 FLYCAST UPDATER - v{VERSION}\n\n"
                "• Branch Master: Lançamentos estáveis / Stable releases.\n"
                "• Branch Dev: Lançamentos diários / Daily builds.\n\n"
                "🖧 USO PELO TERMINAL (CLI) / COMMAND LINE:\n"
                "-nogui, -dev, -master, -rollback, -silent, -reset\n"
            )
            lbl_texto = ctk.CTkLabel(win_ajuda, text=texto_ajuda, justify="left", font=ctk.CTkFont(size=12))
            lbl_texto.pack(padx=20, pady=20, fill="both", expand=True)
            self.log("❔ Janela de 'Sobre' aberta pelo usuário.")

        def preparar_motor(self, acao):
            texto_atual = self.btn_atualizar.cget("text")
            
            self.btn_atualizar.configure(state="disabled")
            self.btn_rollback.configure(state="disabled")
            
            if acao == "atualizar": 
                if self._("btn_play") in texto_atual:
                    self.btn_atualizar.configure(text=self._("btn_starting"))
                    self.log("🚀 Usuário solicitou o lançamento do emulador. Boot sequence initiated.")
                else:
                    self.btn_atualizar.configure(text=self._("btn_processing"))
                    self.log("🚀 Motor de atualização acionado.")
            else: 
                self.btn_rollback.configure(text=self._("btn_reverting"))
                self.log("↩️ Procedimento de Rollback acionado pelo usuário.")

            self.progressbar.pack(pady=(2, 0))
            self.label_status.pack(pady=(2, 5))
            threading.Thread(target=self.rodar_motor, args=(acao,), daemon=True).start()

        def rodar_motor(self, acao):
            terminal_original = sys.stdout
            sys.stdout = ConsoleRedirector(self)
            try:
                install_path = self.entry_path.get()
                
                if getattr(sys, 'frozen', False) and acao != "rollback":
                    atualizou = verificar_atualizacao_updater(install_path, modo_gui=True, app_gui=self)
                    if atualizou: return 

                branch_escolhida = self.branch_var.get()
                criar_desktop = self.switch_desktop.get() == 1
                criar_startup = self.switch_startup.get() == 1
                
                cloud_escolhida = self.cloud_var.get()
                cloud_prov, cloud_path = None, None
                
                if cloud_escolhida == "gdrive" and cloud_saves:
                    cloud_prov, cloud_path = "gdrive", cloud_saves.get_gdrive_path()
                elif cloud_escolhida == "onedrive" and cloud_saves:
                    cloud_prov, cloud_path = "onedrive", cloud_saves.get_onedrive_path()

                self.salvar_estado_atual()

                import update_flycast
                update_flycast.SCRIPT_VERSION = f"{VERSION} (GUI)"
                
                if acao == "rollback": update_flycast.args_lower = ['-rollback']
                else: update_flycast.args_lower = []
                    
                update_flycast.INSTALL_DIR = install_path
                update_flycast.SHOULD_CREATE_SHORTCUT = criar_desktop
                update_flycast.SHOULD_CREATE_STARTUP = criar_startup
                update_flycast.CLOUD_PROVIDER = cloud_prov
                update_flycast.CLOUD_PATH = cloud_path
                update_flycast.VERSION_FILE = os.path.join(install_path, "version.txt")
                update_flycast.LOG_FILE = os.path.join(install_path, "flycast_updater.log")
                update_flycast.get_user_preference = lambda: branch_escolhida
                update_flycast.BACKUP_MAPPINGS = self.switch_mappings.get() == 1
                
                update_flycast.main()
                self.limpar_backups_antigos()
                
                self.log("✅ Ciclo de atualização/operação finalizado com sucesso.")
                self.after(2000, self.destroy)
            except SystemExit:
                self.limpar_backups_antigos()
                self.log("✅ Ciclo encerrado com SystemExit (Success).")
                self.after(2000, self.destroy)
            except Exception as e:
                self.log(f"💥 Erro CRÍTICO durante a execução do motor: {e}")
                self.after(0, self.label_status.configure, {"text": f"Erro crítico: {e}", "text_color": "red"})
            finally:
                sys.stdout = terminal_original
                self.after(0, self.btn_atualizar.configure, {"state": "normal"})
                self.after(0, self.atualizar_status_diretorio, self.entry_path.get())

    app = FlycastUpdaterApp()
    app.mainloop()

# ==========================================
# MODO TERMINAL (CLI)
# ==========================================
def configurar_interativamente():
    print("\n[?] Nenhuma configuração encontrada (ou -reset ativado).")
    print("-" * 50)
    
    while True:
        b = input("[1] Qual versão do Flycast deseja? [M]aster (Estável) ou [D]ev (Diária): ").strip().lower()
        if b in ['m', 'd', 'master', 'dev']:
            branch_choice = 'master' if b.startswith('m') else 'dev'
            break
    
    desk = input("[2] Criar atalho na Área de Trabalho? [S/N]: ").strip().lower()
    create_desktop = desk == 's'
    
    start = input("[3] Iniciar junto com o Windows (Modo Silencioso)? [S/N]: ").strip().lower()
    create_startup = start == 's'

    cloud_prov = None
    cloud_path = None
    if cloud_saves:
        print("\n[4] Backup na Nuvem (Cloud Saves)")
        print("  0 = Nenhum")
        print("  1 = Google Drive")
        print("  2 = OneDrive")
        c = input("-> Escolha o provedor [0/1/2]: ").strip()
        
        if c == '1':
            path = cloud_saves.get_gdrive_path()
            if path and os.path.exists(path):
                cloud_prov, cloud_path = 'gdrive', path
            else:
                print("[-] Aviso: Google Drive não encontrado no seu PC.")
        elif c == '2':
            path = cloud_saves.get_onedrive_path()
            if path and os.path.exists(path):
                cloud_prov, cloud_path = 'onedrive', path
            else:
                print("[-] Aviso: OneDrive não encontrado no seu PC.")

    install_path = os.getcwd()
    salvar_configuracao({
        "branch": branch_choice, "create_shortcut": create_desktop, "create_startup": create_startup,
        "install_path": install_path, "cloud_provider": cloud_prov, "cloud_path": cloud_path, "setup_completed": True
    })
    print("\n[+] Preferências salvas com sucesso!\n")
    
    return {
        "branch": branch_choice,
        "create_shortcut": create_desktop,
        "create_startup": create_startup,
        "install_path": install_path,
        "cloud_provider": cloud_prov,
        "cloud_path": cloud_path,
        "setup_completed": True
    }

def iniciar_cli(args):
    try:
        import ctypes
        ctypes.windll.kernel32.AttachConsole(-1)
        sys.stdout = open('CONOUT$', 'w', encoding='utf-8')
        sys.stderr = open('CONOUT$', 'w', encoding='utf-8')
    except Exception:
        pass

    print(f"=" * 50)
    print(f"🌀 Flycast Updater - v{VERSION} (CLI Mode)")
    print(f"=" * 50)

    if "-help" in args or "-h" in args or "--help" in args:
        print("Uso: FlycastUpdater.exe [argumentos]")
        print("  -nogui        Executa em modo texto")
        print("  -dev          Força a versão de desenvolvimento")
        print("  -master       Força a versão estável")
        print("  -rollback     Restaura o último backup funcional")
        print("  -silent       Executa em segundo plano")
        print("  -backup       Apenas realiza o backup na nuvem")
        print("  -reset        Refaz a configuração inicial")
        sys.exit(0)

    if "-silent" in args:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    config = carregar_configuracao()
    
    flags_auto = ["-silent", "-backup", "-rollback", "-dev", "-master"]
    bypass_questions = any(f in args for f in flags_auto)
    
    if "-reset" in args or (not config and not bypass_questions):
        config = configurar_interativamente()
        
    install_path = config.get("install_path", os.getcwd())
    
    if getattr(sys, 'frozen', False) and "-rollback" not in args and "-backup" not in args:
        verificar_atualizacao_updater(install_path)

    import update_flycast
    update_flycast.SCRIPT_VERSION = f"{VERSION} (CLI)"
    update_flycast.args_lower = args
    update_flycast.INSTALL_DIR = install_path
    update_flycast.SHOULD_CREATE_SHORTCUT = config.get("create_shortcut", False)
    update_flycast.SHOULD_CREATE_STARTUP = config.get("create_startup", False)
    update_flycast.CLOUD_PROVIDER = config.get("cloud_provider")
    update_flycast.CLOUD_PATH = config.get("cloud_path")
    update_flycast.VERSION_FILE = os.path.join(install_path, "version.txt")
    update_flycast.LOG_FILE = os.path.join(install_path, "flycast_updater.log")
    
    branch = config.get("branch", "dev")
    if "-master" in args: branch = "master"
    if "-dev" in args: branch = "dev"
    update_flycast.get_user_preference = lambda: branch

    update_flycast.BACKUP_MAPPINGS = config.get("backup_mappings", False)

    update_flycast.main()

if __name__ == "__main__":
    args_lower = [arg.lower() for arg in sys.argv[1:]]
    gatilhos_cli = ['-nogui', '-silent', '-rollback', '-backup', '-dev', '-master', '-help', '-h', '--help', '-reset', '-gdrive', '-onedrive']
    
    config = carregar_configuracao()
    if config.get("nogui", False) and "-nogui" not in args_lower and "-reset" not in args_lower:
        args_lower.append("-nogui")

    if any(g in args_lower for g in gatilhos_cli):
        iniciar_cli(args_lower)
    else:
        if os.name == 'nt':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            
            process_ids = (ctypes.c_uint * 2)()
            num_procs = kernel32.GetConsoleProcessList(process_ids, 2)
            
            if num_procs <= 1:
                hwnd = kernel32.GetConsoleWindow()
                if hwnd:
                    user32.ShowWindow(hwnd, 0)
                    
        iniciar_gui()