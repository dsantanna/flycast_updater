import os
import json
import subprocess

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