import customtkinter as ctk
import tkinter.messagebox as mb

class QoLManager:
    def __init__(self, app_instance):
        self.app = app_instance
        self.overlays = {}

    def ao_trocar_cheats(self):
        if self.app.switch_cheats.get() == 1:
            self.app.mostrar_toast("Atenção", "Ativar trapaças desabilita o Modo Hardcore do RetroAchievements!", "warning")
            
            if hasattr(self.app, 'switch_hardcore') and self.app.switch_hardcore.get() == 1:
                self.app.switch_hardcore.deselect()
                self.app.config_atual["hardcore_suspended"] = True
                self.app.log("⚠️ UI: Modo Hardcore desativado temporariamente (incompatível com Cheats).")
        else:
            if self.app.config_atual.get("hardcore_suspended", False):
                resposta = mb.askyesno(
                    "RetroAchievements", 
                    "Os Cheats foram desativados.\n\nDeseja reativar o Modo Hardcore para voltar a ganhar conquistas valendo o dobro de pontos?", 
                    parent=self.app
                )
                if resposta:
                    if hasattr(self.app, 'switch_hardcore'):
                        self.app.switch_hardcore.select()
                    self.app.log("🏆 UI: Modo Hardcore reativado pelo usuário!")
                
                self.app.config_atual["hardcore_suspended"] = False
                
        # Auto-save ativado!
        self.app.salvar_estado_atual()
        self.app.salvar_configuracoes_emulador(silencioso=True)

    def toggle_privacy_overlay(self, entry_widget, enable, texto="[ Caminho Protegido - Anti-Leak ]"):
        if enable:
            if entry_widget not in self.overlays:
                overlay = ctk.CTkLabel(entry_widget.master, text=texto, fg_color="#1a1a1a", text_color="#00FF7F", corner_radius=6, font=ctk.CTkFont(weight="bold"))
                self.overlays[entry_widget] = overlay
            self.overlays[entry_widget].place(in_=entry_widget, relx=0, rely=0, relwidth=1, relheight=1)
        else:
            if entry_widget in self.overlays:
                self.overlays[entry_widget].place_forget()

    def ao_trocar_streamer(self):
        is_streamer = getattr(self.app, "switch_streamer", ctk.BooleanVar(value=False)).get() == 1
        if is_streamer:
            self.app.switch_osd_vmu.deselect()
            self.app.switch_vmu_sound.deselect()
            self.toggle_privacy_overlay(self.app.entry_path, True)
            self.toggle_privacy_overlay(self.app.entry_bios_path, True)
            self.toggle_privacy_overlay(self.app.entry_vmu_path, True)
            self.toggle_privacy_overlay(self.app.entry_state_path, True)
            self.toggle_privacy_overlay(self.app.entry_save_path, True)
            self.toggle_privacy_overlay(self.app.entry_ra_user, True, "[ Usuário Protegido ]")
            self.toggle_privacy_overlay(self.app.entry_manual_path, True)
            self.app.log("🎥 Modo Streamer Ativo: OBS Data, Widget Chroma e Privacidade (Anti-Leak) LIGADOS.")
        else:
            self.toggle_privacy_overlay(self.app.entry_path, False)
            self.toggle_privacy_overlay(self.app.entry_bios_path, False)
            self.toggle_privacy_overlay(self.app.entry_vmu_path, False)
            self.toggle_privacy_overlay(self.app.entry_state_path, False)
            self.toggle_privacy_overlay(self.app.entry_save_path, False)
            self.toggle_privacy_overlay(self.app.entry_ra_user, False)
            self.toggle_privacy_overlay(self.app.entry_manual_path, False)
            self.app.log("🎥 Modo Streamer Desativado.")
        
        # Auto-save ativado!
        self.app.salvar_estado_atual()
        self.app.salvar_configuracoes_emulador(silencioso=True)