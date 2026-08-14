import time
import threading

try:
    from pypresence import Presence
    HAS_PYPRESENCE = True
except ImportError:
    HAS_PYPRESENCE = False

class DiscordManager:
    def __init__(self, app_instance, client_id=1537663220041383997): 
        self.app = app_instance
        self.client_id = client_id
        self.rpc = None
        self.connected = False
        self.start_time = int(time.time())

    def conectar(self):
        if not HAS_PYPRESENCE: 
            self.app.log("⚠️ Discord RPC: Biblioteca 'pypresence' não instalada.")
            return
        
        # Só conecta se a chave "DiscordPresence" estiver ativa na sua aba QoL
        if hasattr(self.app, 'switch_discord') and self.app.switch_discord.get() == 0:
            return

        def _conectar():
            try:
                self.rpc = Presence(self.client_id)
                self.rpc.connect()
                self.connected = True
                self.app.log("🎮 Discord RPC: Conectado com sucesso!")
                self.atualizar_menu()
            except Exception as e:
                self.connected = False
                self.app.log(f"⚠️ Discord RPC: Não conectou (Discord fechado ou ID inválido).")
        
        threading.Thread(target=_conectar, daemon=True).start()

    def atualizar_status(self, detalhes, estado):
        if not self.connected: return
        
        # Se o usuário desativou no meio da sessão, a gente corta a conexão
        if hasattr(self.app, 'switch_discord') and self.app.switch_discord.get() == 0:
            self.desconectar()
            return
            
        def _atualizar():
            try:
                self.rpc.update(
                    details=detalhes,
                    state=estado,
                    start=self.start_time
                )
            except:
                self.connected = False
                
        threading.Thread(target=_atualizar, daemon=True).start()

    def atualizar_menu(self):
        self.atualizar_status(detalhes="Navegando na Biblioteca", estado="No Launcher Principal")

    def atualizar_jogo(self, nome_jogo):
        nome = nome_jogo if nome_jogo else "Jogo Desconhecido"
        self.atualizar_status(detalhes="Jogando Clássicos", estado=nome)

    def desconectar(self):
        if self.connected and self.rpc:
            try:
                self.rpc.clear()
                self.rpc.close()
            except: pass
        self.connected = False
        self.app.log("🔌 Discord RPC: Desconectado.")