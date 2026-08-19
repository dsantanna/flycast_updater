import os
import json
import subprocess
import shutil
import zipfile
import tkinter.messagebox as mb
import customtkinter as ctk
import config_manager

def obter_gpus_windows():
    if os.name != 'nt': return []
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion | ConvertTo-Json"'
        result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)
        if result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, dict): data = [data]
            return [{"nome": g.get("Name", "Desconhecida"), "driver": g.get("DriverVersion", "Desconhecido")} for g in data if g.get("Name")]
    except Exception: pass
    return []

def obter_monitores_windows():
    if os.name != 'nt': return [{"nome": "Monitor Padrão", "left": 0, "top": 0}]
    import ctypes
    monitores = []
    try:
        user32 = ctypes.windll.user32
        class RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
        def _callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            r = lprcMonitor.contents
            idx = len(monitores) + 1
            nome = f"Monitor {idx} ({r.right - r.left}x{r.bottom - r.top})"
            if r.left == 0 and r.top == 0: nome += " [Principal]"
            monitores.append({"nome": nome, "left": r.left, "top": r.top})
            return 1
        MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(RECT), ctypes.c_void_p)
        user32.EnumDisplayMonitors(0, None, MonitorEnumProc(_callback), 0)
    except Exception:
        monitores.append({"nome": "Monitor Padrão", "left": 0, "top": 0})
    return monitores

# ==========================================
# GERENCIAMENTO DE BIOS E ARQUIVOS (BIG BLUE)
# ==========================================

def procurar_e_instalar_bios(app, install_path, custom_bios_path):
    app.log("🔍 Usuário abriu seletor de arquivos de BIOS.")
    arquivo = ctk.filedialog.askopenfilename(title="Select BIOS (.bin) or ZIP (.zip)", filetypes=[("BIOS / ZIP", "*.bin *.zip"), ("All files", "*.*")])
    if not arquivo: return
        
    target_dir = custom_bios_path if custom_bios_path else os.path.join(install_path, "data")
    os.makedirs(target_dir, exist_ok=True)
    app.log(f"📂 Diretório alvo da BIOS: {target_dir}")
    
    if arquivo.lower().endswith(".zip"):
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
                if encontrou: mb.showinfo("Sucesso", app._("msg_bios_zip_success"), parent=app)
                else: mb.showwarning("Aviso", "O ZIP não continha dc_boot.bin ou dc_flash.bin.", parent=app)
        except Exception as e:
            mb.showerror("Erro", f"Erro: {e}", parent=app)
    elif arquivo.lower().endswith(".bin"):
        orig_basename = os.path.basename(arquivo).lower()
        target_basename = orig_basename
        if "boot" in orig_basename and "dc_boot.bin" not in orig_basename: target_basename = "dc_boot.bin"
        elif "flash" in orig_basename and "dc_flash.bin" not in orig_basename: target_basename = "dc_flash.bin"
        
        try:
            shutil.copy(arquivo, os.path.join(target_dir, target_basename))
            has_boot = os.path.exists(os.path.join(target_dir, "dc_boot.bin")) or os.path.exists(os.path.join(target_dir, "DC_BOOT.BIN"))
            has_flash = os.path.exists(os.path.join(target_dir, "dc_flash.bin")) or os.path.exists(os.path.join(target_dir, "DC_FLASH.BIN"))
            missing_other = None
            if not has_boot: missing_other = "dc_boot.bin"
            elif not has_flash: missing_other = "dc_flash.bin"
            
            if missing_other:
                resp = mb.askyesno(app._("title_bios_partial"), app._("msg_bios_partial").format(missing=missing_other), parent=app)
                if resp: procurar_e_instalar_bios(app, install_path, custom_bios_path)
            else:
                mb.showinfo("Sucesso", app._("msg_bios_bin_success"), parent=app)
        except Exception as e:
            mb.showerror("Erro", f"Erro: {e}", parent=app)
    app.atualizar_status_diretorio(install_path)

def tratar_bios_ausente(app, path, custom_bios_path, has_boot, has_flash):
    if getattr(app, 'bios_prompt_done', False): return
    app.bios_prompt_done = True
    missing = []
    if not has_boot: missing.append("dc_boot.bin")
    if not has_flash: missing.append("dc_flash.bin")
    if not missing: return
    
    msg = app._("msg_bios_missing").format(files="\n- ".join(missing))
    resposta = mb.askyesno(app._("title_bios_missing"), msg, parent=app)
    
    if resposta: 
        procurar_e_instalar_bios(app, path, custom_bios_path)
    else:
        # O usuário recusou o envio manual. A Tática do HLE entra em ação!
        msg_hle = (
            "Você optou por não fornecer os arquivos originais de BIOS.\n\n"
            "O Flycast possui um recurso de 'BIOS HLE', que simula o sistema original "
            "e permite iniciar os jogos sem os arquivos oficiais.\n\n"
            "Deseja ativar a BIOS HLE agora para garantir o funcionamento do emulador?"
        )
        resposta_hle = mb.askyesno("Ativar BIOS HLE Automática?", msg_hle, parent=app)
        if resposta_hle:
            if hasattr(app, 'switch_hle'):
                app.switch_hle.select()
                app.ao_trocar_hle() # O motor salva e pinta a tela de verde automaticamente!
        else:
            app.log("⚠️ Usuário recusou a BIOS oficial e a emulação HLE. Os jogos poderão não iniciar.")

def resolver_bios_mal_posicionada(app, path):
    if getattr(app, 'bios_prompt_done', False): return
    app.bios_prompt_done = True
    
    # Pergunta 1: Deseja mover os arquivos para a pasta 'data'?
    resposta_mover = mb.askyesno(app._("msg_bios_move_title"), app._("msg_bios_move_desc"), parent=app)
    if resposta_mover:
        pasta_data = os.path.join(path, "data")
        os.makedirs(pasta_data, exist_ok=True)
        try:
            shutil.move(os.path.join(path, "dc_boot.bin"), os.path.join(pasta_data, "dc_boot.bin"))
            shutil.move(os.path.join(path, "dc_flash.bin"), os.path.join(pasta_data, "dc_flash.bin"))
            mb.showinfo("Sucesso", app._("msg_success"), parent=app)
            app.atualizar_status_diretorio(path)
        except Exception: pass
    else:
        # Pergunta 2: Já que não quer mover, deseja registrar esse local no emu.cfg?
        resposta_config = mb.askyesno("BIOS", app._("msg_bios_register_desc"), parent=app)
        if resposta_config:
            if config_manager.atualizar_emu_cfg(install_path=path, bios_path=path):
                app.atualizar_status_diretorio(path)
        else:
            # Pergunta 3 (A Tática do HLE): O usuário recusou organizar os arquivos. Oferecemos o HLE!
            msg_hle = (
                "Como os arquivos não foram movidos nem registrados, o emulador poderá apresentar falhas ao iniciar.\n\n"
                "O Flycast possui um recurso avançado chamado 'BIOS HLE', que simula "
                "o sistema nativo do console em software, ignorando o uso da BIOS original\n"
                "(dc_boot.bin). Alguns jogos independentes e homebrews recentes (como o clássico\n"
                "RPG Pier Solar) SÓ funcionam se esta opção estiver ATIVADA."
            )
            resposta_hle = mb.askyesno("Ativar BIOS HLE Automática?", msg_hle, parent=app)
            
            if resposta_hle:
                if hasattr(app, 'switch_hle'):
                    app.switch_hle.select()
                    app.ao_trocar_hle() # O motor salva no emu.cfg e pinta o semáforo de VERDE!
                    if hasattr(app, 'mostrar_toast'):
                        app.mostrar_toast("HLE Ativado", "A BIOS HLE foi ativada com sucesso!", "success")
            else:
                app.log("⚠️ Usuário manteve a BIOS no local incorreto e recusou a ativação da emulação HLE.")