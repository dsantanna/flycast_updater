import os
import json
import configparser

CONFIG_FILE = "config.json"

def carregar_configuracao():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: pass
    return {}

def salvar_configuracao(dados):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception: pass

def atualizar_emu_cfg(install_path, roms_path=None, ra_enabled=None, ra_user=None, ra_pass=None, ra_hardcore=None, 
                      vmu_individual=None, fetch_boxart=None, vga_cable=None, discord_presence=None,
                      show_osd_vmu=None, vmu_sound=None, bios_path=None, vmu_path=None, state_path=None, save_path=None,
                      vid_api=None, vid_res=None, vid_full=None, vid_int=None, vid_lin=None, vid_vsync=None,
                      streamer_mode=None, cheat_enable=None, window_left=None, window_top=None, widescreen_hack=None, use_hle=None):
    
    caminhos_possiveis = [os.path.join(install_path, "emu.cfg"), os.path.join(install_path, "data", "emu.cfg")]
    cfg_path = next((p for p in caminhos_possiveis if os.path.exists(p)), os.path.join(install_path, "emu.cfg"))

    config = configparser.RawConfigParser(strict=False)
    config.optionxform = str 
    if os.path.exists(cfg_path):
        try: config.read(cfg_path, encoding='utf-8')
        except Exception: return False

    for section in ['achievements', 'config', 'audio', 'window']:
        if not config.has_section(section): config.add_section(section)

    if ra_enabled is not None: 
        config.set('achievements', 'Enabled', 'yes' if ra_enabled else 'no')
        config.set('achievements', 'OsdEnabled', 'no') 
        config.set('achievements', 'ChallengeModeOsd', 'no')
        config.set('achievements', 'ShowProgressOsd', 'no')
        
    if ra_hardcore is not None: config.set('achievements', 'HardcoreMode', 'yes' if ra_hardcore else 'no')
    if ra_user is not None: config.set('achievements', 'UserName', ra_user)
    if ra_pass is not None: config.set('achievements', 'Token', ra_pass)

    if roms_path is not None: 
        if isinstance(roms_path, list):
            caminhos_formatados = ";".join([p.replace("/", "\\") for p in roms_path])
            config.set('config', 'Dreamcast.ContentPath', caminhos_formatados)
        else:
            config.set('config', 'Dreamcast.ContentPath', roms_path.replace("/", "\\"))

    if vmu_individual is not None: config.set('config', 'PerGameVmu', 'yes' if vmu_individual else 'no')
    if fetch_boxart is not None:
        config.set('config', 'FetchBoxart', 'yes' if fetch_boxart else 'no')
        config.set('config', 'BoxartDisplayMode', 'yes' if fetch_boxart else 'no')
    if vga_cable is not None: config.set('config', 'Dreamcast.Cable', '0' if vga_cable else '3') 
    if discord_presence is not None: config.set('config', 'DiscordPresence', 'yes' if discord_presence else 'no')
    if show_osd_vmu is not None: 
        config.set('config', 'ShowOsdVmu', 'yes' if show_osd_vmu else 'no')
        config.set('config', 'rend.FloatVMUs', 'yes' if show_osd_vmu else 'no')
    if streamer_mode is not None: config.set('config', 'OsdMessages', 'no' if streamer_mode else 'yes')
    if cheat_enable is not None: config.set('config', 'Cheat', 'yes' if cheat_enable else 'no')
    if use_hle is not None: config.set('config', 'UseReios', 'yes' if use_hle else 'no')

    def _set_or_remove(sec, k, val):
        if val: config.set(sec, k, val.replace("/", "\\"))
        elif config.has_option(sec, k): config.remove_option(sec, k)

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
    if widescreen_hack is not None: config.set('config', 'WidescreenGameHacks', 'yes' if widescreen_hack else 'no')

    if window_left is not None: config.set('window', 'left', str(window_left))
    if window_top is not None: config.set('window', 'top', str(window_top))

    try:
        os.makedirs(os.path.dirname(os.path.abspath(cfg_path)), exist_ok=True)
        with open(cfg_path, 'w', encoding='utf-8') as f: config.write(f, space_around_delimiters=True)
        return True
    except Exception: return False