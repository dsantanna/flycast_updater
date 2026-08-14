import os
import shutil
import zipfile
import datetime
import configparser
import tkinter.messagebox as mb

try:
    import cloud_saves
except ImportError:
    cloud_saves = None

class SaveManager:
    def __init__(self, app_instance):
        self.app = app_instance

    def verificar_caminho_nuvem(self, escolha):
        if not cloud_saves: return False
        caminho = None
        if escolha == "Google Drive": caminho = cloud_saves.get_gdrive_path()
        elif escolha == "OneDrive": caminho = cloud_saves.get_onedrive_path()
        return caminho is not None and os.path.exists(caminho)

    def limpar_backups_antigos(self):
        limite_str = self.app.config_atual.get("backup_limit", "5")
        if limite_str in ["Ilimitado", "Unlimited", "Illimité", "Unbegrenzt", "无限制", "無制限", "Неограничено", "غير محدود", "असीमित"]: return
        try: limite = int(limite_str)
        except ValueError: return
        
        cloud_prov = self.app.config_atual.get("cloud_provider", "nenhum")
        if not cloud_prov or cloud_prov == "nenhum": return
        
        caminho_base = None
        if cloud_prov == "gdrive" and cloud_saves: caminho_base = cloud_saves.get_gdrive_path()
        elif cloud_prov == "onedrive" and cloud_saves: caminho_base = cloud_saves.get_onedrive_path()
        if not caminho_base or not os.path.exists(caminho_base): return

        caminho_nuvem = os.path.join(caminho_base, "Flycast_Saves_Backup")
        if not os.path.exists(caminho_nuvem): return
        arquivos_zip = [f for f in os.listdir(caminho_nuvem) if f.lower().endswith(".zip") and f != "flycast_backup.zip"]
        if len(arquivos_zip) <= limite: return

        arquivos_zip.sort(key=lambda x: os.path.getmtime(os.path.join(caminho_nuvem, x)))
        for i in range(len(arquivos_zip) - limite):
            try: os.remove(os.path.join(caminho_nuvem, arquivos_zip[i]))
            except Exception: pass

    def buscar_backups_saves(self):
        cloud_prov = self.app.cloud_var.get()
        if cloud_prov == "nenhum": return
        caminho_base = None
        if cloud_prov == "gdrive" and cloud_saves: caminho_base = cloud_saves.get_gdrive_path()
        elif cloud_prov == "onedrive" and cloud_saves: caminho_base = cloud_saves.get_onedrive_path()
        if not caminho_base or not os.path.exists(caminho_base): return

        caminho_nuvem = os.path.join(caminho_base, "Flycast_Saves_Backup")
        if not os.path.exists(caminho_nuvem):
            self.app.combo_backups.configure(values=[self.app._("log_not_found")])
            self.app.combo_backups.set(self.app._("log_not_found"))
            self.app.btn_restaurar_save.configure(state="disabled")
            return

        try:
            self.limpar_backups_antigos() 
            arquivos_zip = [f for f in os.listdir(caminho_nuvem) if f.lower().endswith(".zip") and f != "flycast_backup.zip"]
            if not arquivos_zip:
                self.app.combo_backups.configure(values=[self.app._("log_not_found")])
                self.app.combo_backups.set(self.app._("log_not_found"))
                self.app.btn_restaurar_save.configure(state="disabled")
                return

            arquivos_zip.sort(key=lambda x: os.path.getmtime(os.path.join(caminho_nuvem, x)), reverse=True)
            self.app.arquivos_backup_encontrados = {}
            nomes_exibicao = []
            for f in arquivos_zip:
                caminho_completo = os.path.join(caminho_nuvem, f)
                data_mod = datetime.datetime.fromtimestamp(os.path.getmtime(caminho_completo)).strftime('%d/%m/%Y %H:%M')
                nome_exib = f"{f}  [{data_mod}]"
                nomes_exibicao.append(nome_exib)
                self.app.arquivos_backup_encontrados[nome_exib] = caminho_completo

            self.app.combo_backups.configure(values=nomes_exibicao)
            self.app.combo_backups.set(nomes_exibicao[0])
            self.app.btn_restaurar_save.configure(state="normal")
            self.app.mostrar_toast("Nuvem", f"{len(arquivos_zip)} backups encontrados com sucesso!", "info")
        except Exception: pass

    def restaurar_backup_selecionado(self):
        selecionado = self.app.combo_backups.get()
        caminho_zip = self.app.arquivos_backup_encontrados.get(selecionado)
        if not caminho_zip or not os.path.exists(caminho_zip): return
        install_path = self.app.entry_path.get()
        if not install_path or not os.path.exists(install_path): return
        
        # AQUI CONTINUA SENDO O MESSAGE BOX, POIS O USUÁRIO PRECISA CLICAR EM SIM/NÃO!
        if not mb.askyesno("Confirmar", f"Extrair arquivos de:\n{selecionado}\n\nContinuar?", parent=self.app): return
        
        custom_vmu = ""
        custom_save = ""
        cfg_path = os.path.join(install_path, "emu.cfg")
        if not os.path.exists(cfg_path): cfg_path = os.path.join(install_path, "data", "emu.cfg")
            
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
                        dest_dir = os.path.join(install_path, "data", "mappings")
                    else:
                        if basename.startswith('vmu') and custom_vmu: dest_dir = custom_vmu
                        elif custom_save: dest_dir = custom_save
                        else: dest_dir = os.path.join(install_path, "data")
                    os.makedirs(dest_dir, exist_ok=True)
                    with zip_ref.open(file_info.filename) as source, open(os.path.join(dest_dir, basename), "wb") as target:
                        shutil.copyfileobj(source, target)
            self.app.mostrar_toast("Extração Completa", "Seus saves e configurações foram restaurados com sucesso!", "success")
        except Exception as e:
            self.app.mostrar_toast("Erro na Restauração", f"Falha ao extrair: {e}", "error")

    def realizar_backup_configs(self):
        cloud_prov = self.app.cloud_var.get()
        if cloud_prov == "nenhum":
            self.app.mostrar_toast("Aviso", "Selecione um provedor de nuvem (Google Drive ou OneDrive) no topo da aba primeiro.", "warning")
            return
            
        caminho_base = None
        if cloud_prov == "gdrive" and cloud_saves: caminho_base = cloud_saves.get_gdrive_path()
        elif cloud_prov == "onedrive" and cloud_saves: caminho_base = cloud_saves.get_onedrive_path()
        
        if not caminho_base or not os.path.exists(caminho_base):
            self.app.mostrar_toast("Erro de Conexão", "Pasta da nuvem não foi encontrada no seu computador.", "error")
            return

        caminho_nuvem = os.path.join(caminho_base, "Flycast_Configs_Backup")
        os.makedirs(caminho_nuvem, exist_ok=True)
        
        agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"config_backup_{agora}.zip"
        zip_path = os.path.join(caminho_nuvem, zip_name)
        
        install_path = self.app.entry_path.get()
        arquivos_para_backup = []
        
        if hasattr(self.app, 'sw_bkp_emu') and self.app.sw_bkp_emu.get() == 1:
            p1 = os.path.join(install_path, "emu.cfg")
            p2 = os.path.join(install_path, "data", "emu.cfg")
            if os.path.exists(p1): arquivos_para_backup.append((p1, "emu.cfg"))
            if os.path.exists(p2): arquivos_para_backup.append((p2, "data/emu.cfg"))
        
        if hasattr(self.app, 'sw_bkp_upd') and self.app.sw_bkp_upd.get() == 1:
            p_conf = "config.json"
            if os.path.exists(p_conf): arquivos_para_backup.append((p_conf, os.path.basename(p_conf)))
            
        if hasattr(self.app, 'sw_bkp_ra') and self.app.sw_bkp_ra.get() == 1:
            p_ra = os.path.join(install_path, "RAlocal.db")
            if os.path.exists(p_ra): arquivos_para_backup.append((p_ra, "RAlocal.db"))
            
        if not arquivos_para_backup:
            self.app.mostrar_toast("Atenção", "Nenhum arquivo encontrado para backup com os switches selecionados.", "warning")
            return
            
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filepath, arcname in arquivos_para_backup:
                    zipf.write(filepath, arcname)
            
            self.app.log(f"💾 Backup de configurações criado na nuvem: {zip_name}")
            self.app.mostrar_toast("Backup Concluído", "Configurações salvas na nuvem com sucesso!", "success")
            self.buscar_backups_configs()
        except Exception as e:
            self.app.mostrar_toast("Erro no Backup", f"Falha ao criar o arquivo Zip: {e}", "error")

    def buscar_backups_configs(self):
        cloud_prov = self.app.cloud_var.get()
        if cloud_prov == "nenhum": return
        caminho_base = None
        if cloud_prov == "gdrive" and cloud_saves: caminho_base = cloud_saves.get_gdrive_path()
        elif cloud_prov == "onedrive" and cloud_saves: caminho_base = cloud_saves.get_onedrive_path()
        if not caminho_base or not os.path.exists(caminho_base): return

        caminho_nuvem = os.path.join(caminho_base, "Flycast_Configs_Backup")
        if not os.path.exists(caminho_nuvem):
            self.app.combo_backups_cfg.configure(values=[self.app._("log_not_found")])
            self.app.combo_backups_cfg.set(self.app._("log_not_found"))
            self.app.btn_restaurar_cfg.configure(state="disabled")
            return

        try:
            arquivos_zip = [f for f in os.listdir(caminho_nuvem) if f.lower().endswith(".zip")]
            if not arquivos_zip:
                self.app.combo_backups_cfg.configure(values=[self.app._("log_not_found")])
                self.app.combo_backups_cfg.set(self.app._("log_not_found"))
                self.app.btn_restaurar_cfg.configure(state="disabled")
                return

            arquivos_zip.sort(key=lambda x: os.path.getmtime(os.path.join(caminho_nuvem, x)), reverse=True)
            self.app.arquivos_cfg_encontrados = {}
            nomes_exibicao = []
            for f in arquivos_zip:
                caminho_completo = os.path.join(caminho_nuvem, f)
                data_mod = datetime.datetime.fromtimestamp(os.path.getmtime(caminho_completo)).strftime('%d/%m/%Y %H:%M')
                nome_exib = f"{f}  [{data_mod}]"
                nomes_exibicao.append(nome_exib)
                self.app.arquivos_cfg_encontrados[nome_exib] = caminho_completo

            self.app.combo_backups_cfg.configure(values=nomes_exibicao)
            self.app.combo_backups_cfg.set(nomes_exibicao[0])
            self.app.btn_restaurar_cfg.configure(state="normal")
        except Exception: pass

    def restaurar_backup_configs(self):
        selecionado = self.app.combo_backups_cfg.get()
        caminho_zip = self.app.arquivos_cfg_encontrados.get(selecionado)
        if not caminho_zip or not os.path.exists(caminho_zip): return
        install_path = self.app.entry_path.get()
        if not install_path or not os.path.exists(install_path): return
        
        if not mb.askyesno("Atenção - Sobrescrever", f"Extrair de:\n{selecionado}\n\nIsso irá substituir completamente as suas configurações atuais.\nContinuar?", parent=self.app): return
        
        try:
            with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.filename.endswith('/'): continue
                    
                    if file_info.filename == "config.json":
                        dest_path = os.path.join(os.getcwd(), "config.json")
                    elif file_info.filename == "emu.cfg":
                        dest_path = os.path.join(install_path, "emu.cfg")
                    elif file_info.filename == "data/emu.cfg":
                        dest_path = os.path.join(install_path, "data", "emu.cfg")
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    elif file_info.filename == "RAlocal.db":
                        dest_path = os.path.join(install_path, "RAlocal.db")
                    else:
                        continue
                        
                    with zip_ref.open(file_info.filename) as source, open(dest_path, "wb") as target:
                        shutil.copyfileobj(source, target)
                        
            # Recarrega no App principal
            import launcher
            self.app.config_atual = launcher.carregar_configuracao()
            self.app.carregar_dados_atuais_emu_cfg()
            self.app.game_manager.escanear_jogos()
            self.app.mostrar_toast("Restauração Concluída", "O Launcher foi atualizado com as configs da nuvem!", "success")
        except Exception as e:
            self.app.mostrar_toast("Erro Fatal", f"Falha ao restaurar configurações: {e}", "error")

    def auto_sync_saves(self):
        """Mágica da Fase 2: Pega os saves atuais e sobe para a nuvem silenciosamente."""
        cloud_prov = self.app.config_atual.get("cloud_provider", "nenhum")
        if not cloud_prov or cloud_prov == "nenhum":
            return # Se não tem nuvem configurada, aborta a missão sem incomodar o usuário.

        caminho_base = None
        if cloud_prov == "gdrive" and cloud_saves: caminho_base = cloud_saves.get_gdrive_path()
        elif cloud_prov == "onedrive" and cloud_saves: caminho_base = cloud_saves.get_onedrive_path()

        if not caminho_base or not os.path.exists(caminho_base):
            self.app.log("⚠️ Auto-Sync: Pasta da nuvem não encontrada no computador.")
            return

        caminho_nuvem = os.path.join(caminho_base, "Flycast_Saves_Backup")
        os.makedirs(caminho_nuvem, exist_ok=True)

        agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"auto_save_{agora}.zip"
        zip_path = os.path.join(caminho_nuvem, zip_name)

        install_path = self.app.entry_path.get()
        pastas_alvo = []

        # Consulta o emu.cfg para ver onde estão os saves e states
        cfg_path = os.path.join(install_path, "emu.cfg")
        if not os.path.exists(cfg_path): cfg_path = os.path.join(install_path, "data", "emu.cfg")
        
        custom_vmu, custom_save, custom_state = "", "", ""
        if os.path.exists(cfg_path):
            try:
                c = configparser.RawConfigParser(strict=False)
                c.read(cfg_path, encoding='utf-8')
                if c.has_section('config'):
                    custom_vmu = c.get('config', 'Dreamcast.VmuPath', fallback='')
                    custom_save = c.get('config', 'Dreamcast.SavePath', fallback='')
                    custom_state = c.get('config', 'Dreamcast.SavestatePath', fallback='')
            except: pass

        # Resolve os caminhos (se o usuário escolheu caminhos customizados ou os originais)
        path_vmu = custom_vmu if custom_vmu and os.path.isabs(custom_vmu) else os.path.join(install_path, custom_vmu or "vmu")
        path_save = custom_save if custom_save and os.path.isabs(custom_save) else os.path.join(install_path, custom_save or "saves")
        path_state = custom_state if custom_state and os.path.isabs(custom_state) else os.path.join(install_path, custom_state or "save_state")
        path_mappings = os.path.join(install_path, "data", "mappings")

        if os.path.exists(path_vmu): pastas_alvo.append((path_vmu, "vmu"))
        if os.path.exists(path_save): pastas_alvo.append((path_save, "saves"))
        if os.path.exists(path_state): pastas_alvo.append((path_state, "save_state"))
        if self.app.config_atual.get("backup_mappings", False) and os.path.exists(path_mappings):
            pastas_alvo.append((path_mappings, "mappings"))

        if not pastas_alvo:
            return

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for pasta_abs, prefixo in pastas_alvo:
                    for root, _, files in os.walk(pasta_abs):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # Preserva a estrutura interna da pasta
                            arcname = os.path.join(prefixo, os.path.relpath(file_path, pasta_abs))
                            zipf.write(file_path, arcname)
            
            self.app.log(f"☁️ Auto-Sync: Saves enviados para a nuvem ({zip_name}).")
            self.app.mostrar_toast("Auto-Sync Concluído", "Seu progresso foi salvo na nuvem com sucesso!", "success")
            
            # Chama a função de limpar as velhas para nunca lotar o Drive do usuário!
            self.limpar_backups_antigos() 
            self.buscar_backups_saves() # Atualiza a lista na UI caso a aba esteja aberta
        except Exception as e:
            self.app.log(f"❌ Auto-Sync: Erro ao fazer backup automático: {e}")