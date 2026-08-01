"""
Flycast Auto-Updater Script
---------------------------
Version: 1.0
Author: Daniel de Souza Sant'Anna (with the help of Gemini)

This script automates the download and update of the Flycast emulator.
It includes the ability to auto-copy itself, automatically generate Desktop shortcuts,
and maintain an incremental audit log of executions and updates.
"""

import os
import sys            
import json           
import urllib.request 
from urllib.error import HTTPError, URLError
import zipfile        
import subprocess     
import shutil         
import tempfile       
import datetime       

# --- GLOBAL VARIABLES AND DIRECTORIES ---
SCRIPT_VERSION = "1.0"
INSTALL_DIR = os.getcwd()
SHOULD_CREATE_SHORTCUT = False 

args_lower = [arg.lower() for arg in sys.argv]

# --- HELP MENU ---
if any(h in args_lower for h in ['-help', '--help', '-h', 'help']):
    print("\n=== Flycast Updater Help ===")
    print("Usage: python flycast_update_en_us.py [arguments]\n")
    print("Optional arguments:")
    print("  -help, --help, -h  Shows this help menu and exits.")
    print("  -dev               Forces the configuration and download of the DEV version (Daily build).")
    print("  -master            Forces the configuration and download of the MASTER version (Stable release).")
    print("  -path              <directory>")
    print("                     Sets a custom installation directory.")
    print("                     Example: python flycast_update_en_us.py -path \"D:\\Emulators\\Flycast\"\n")
    print("Default behavior:")
    print("If run without arguments, the script will use saved settings")
    print("(or ask on the first run) and install in the current directory.")
    print("============================\n")
    sys.exit(0)

for param in ['-path']:
    if param in args_lower:
        idx = args_lower.index(param)
        if len(sys.argv) > idx + 1:
            INSTALL_DIR = os.path.abspath(sys.argv[idx + 1])
            break

if not os.path.exists(INSTALL_DIR):
    os.makedirs(INSTALL_DIR)

# --- LOG SYSTEM ---
LOG_FILE = os.path.join(INSTALL_DIR, "flycast_updater.log")

def log_event(message):
    """Writes events incrementally to the log file with a timestamp and script version."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [v{SCRIPT_VERSION}] {message}\n")
    except Exception as e:
        print(f"Warning: Failed to write to the log file. Details: {e}")

# --- AUTO-COPY (PyInstaller Compatible) ---
if getattr(sys, 'frozen', False):
    current_script_path = sys.executable
else:
    current_script_path = os.path.abspath(__file__)

dest_script_path = os.path.join(INSTALL_DIR, os.path.basename(current_script_path))

if current_script_path != dest_script_path:
    try:
        shutil.copy2(current_script_path, dest_script_path)
    except Exception as e:
        print(f"Warning: Could not copy the script to the destination. Details: {e}")

VERSION_FILE = os.path.join(INSTALL_DIR, "version.txt")
CONFIG_FILE = os.path.join(INSTALL_DIR, "branch_config.txt")

S3_BUCKETS = [
    "https://flycast-builds.s3.fr-par.scw.cloud",
    "https://flycast-builds.s3.amazonaws.com"
]

def get_user_preference():
    global SHOULD_CREATE_SHORTCUT
    
    if '-dev' in args_lower:
        print("'-dev' parameter detected. Changing configuration to DEV version...")
        with open(CONFIG_FILE, "w") as f:
            f.write('dev')
        log_event("User option (via parameter): Branch changed to DEV.")
        return 'dev'
    elif '-master' in args_lower:
        print("'-master' parameter detected. Changing configuration to MASTER version...")
        with open(CONFIG_FILE, "w") as f:
            f.write('master')
        log_event("User option (via parameter): Branch changed to MASTER.")
        return 'master'
        
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            choice = f.read().strip().lower()
            if choice in ['master', 'dev']:
                return choice

    print("\n=== Flycast Updater Initial Setup ===")
    print(f"Target directory: {INSTALL_DIR}")
    if current_script_path != dest_script_path:
        print(f"(The updater script will copy itself to this directory)")
    print("\nWhich emulator version do you want to download and keep updated?")
    print("[1] Master (Stable Version / Official Main)")
    print("[2] Dev    (Development Version / Cloud Daily)")
    
    while True:
        resp = input("Type 1 or 2 and press Enter: ").strip()
        if resp == '1':
            choice = 'master'
            break
        elif resp == '2':
            choice = 'dev'
            break
        else:
            print("Invalid option. Type 1 for Master or 2 for Dev.")
            
    with open(CONFIG_FILE, "w") as f:
        f.write(choice)
        
    log_event(f"Initial setup completed. Chosen branch: {choice.upper()}.")
        
    print("\nDo you want to create a Desktop shortcut for this updater?")
    print("It will automatically use the correct parameters and have the official emulator icon.")
    while True:
        resp_shortcut = input("Create shortcut? (Y/N): ").strip().upper()
        if resp_shortcut == 'Y':
            SHOULD_CREATE_SHORTCUT = True
            log_event("User option: Desktop shortcut creation requested.")
            break
        elif resp_shortcut == 'N':
            log_event("User option: Shortcut creation declined.")
            break
        else:
            print("Please type 'Y' for Yes or 'N' for No.")
            
    return choice

def create_desktop_shortcut(branch_choice):
    try:
        python_exe = sys.executable
        flycast_exe = os.path.join(INSTALL_DIR, "flycast.exe")
        
        vbs_content = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sDesktop = oWS.SpecialFolders("Desktop")
Set oLink = oWS.CreateShortcut(sDesktop & "\\Flycast ({branch_choice.capitalize()}).lnk")
oLink.TargetPath = "{python_exe}"
oLink.Arguments = Chr(34) & "{dest_script_path}" & Chr(34) & " -{branch_choice} -path " & Chr(34) & "{INSTALL_DIR}" & Chr(34)
oLink.WorkingDirectory = "{INSTALL_DIR}"
oLink.IconLocation = "{flycast_exe}, 0"
oLink.Save
"""
        vbs_path = os.path.join(tempfile.gettempdir(), "create_flycast_shortcut.vbs")
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_content)
            
        subprocess.run(['cscript.exe', '//Nologo', vbs_path], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(vbs_path):
            os.remove(vbs_path)
            
        print(f"\n[+] '{branch_choice.capitalize()}' shortcut successfully created on the Desktop!")
        log_event(f"Desktop shortcut successfully generated (Branch: {branch_choice.upper()}).")
    except Exception as e:
        print(f"\n[-] Warning: Could not generate the shortcut. Error: {e}")
        log_event(f"Error generating shortcut: {e}")

def get_stable_release():
    print("Querying the GitHub API for the latest Stable Release (Master)...")
    api_url = "https://api.github.com/repos/flyinghead/flycast/releases/latest"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            release = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error accessing the GitHub API: {e}")
        return None, None

    remote_version = release.get("tag_name")
    
    for asset in release.get("assets", []):
        name = asset["name"].lower()
        if ("win" in name or "windows" in name) and ("debug" not in name) and name.endswith(".zip"):
            return asset["browser_download_url"], remote_version
            
    return None, None

def get_dev_release():
    print("Fetching code history for the 'DEV' branch...")
    api_url = "https://api.github.com/repos/flyinghead/flycast/commits?sha=dev&per_page=15"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            commits = json.loads(response.read().decode('utf-8'))
            commit_hashes = [commit["sha"] for commit in commits]
    except Exception as e:
        print(f"Error querying the commits API: {e}")
        return None, None

    print("Probing S3 servers for the latest daily build for Windows...")
    for commit in commit_hashes:
        for bucket in S3_BUCKETS:
            url = f"{bucket}/win/heads/dev-{commit}/flycast.zip"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
                urllib.request.urlopen(req)
                return url, commit
            except (HTTPError, URLError):
                continue
                
    return None, None

def launch_emulator():
    exe_path = os.path.join(INSTALL_DIR, "flycast.exe")
    if os.path.exists(exe_path):
        print("Starting Flycast...")
        log_event("Script execution finished. Starting the emulator.")
        subprocess.Popen([exe_path], cwd=INSTALL_DIR)
    else:
        msg = f"Warning: Executable not found at: {exe_path}"
        print(f"\n{msg}")
        log_event(msg)

def main():
    log_event("--- Script started ---")
    branch_choice = get_user_preference()
    
    download_url = None
    remote_version = None
    
    if branch_choice == 'master':
        download_url, remote_version = get_stable_release()
    else:
        download_url, remote_version = get_dev_release()
        
    if not download_url:
        msg_error = f"Error: Could not locate the files for the {branch_choice.upper()} version."
        print(msg_error)
        log_event(msg_error)
        return

    print(f"Valid package found! (Version/Commit: {remote_version[:10]})")

    local_version = ""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            local_version = f.read().strip()

    if local_version == remote_version:
        print(f"Flycast ({branch_choice.upper()}) is already updated to the latest available version!")
        log_event(f"Check completed. The {branch_choice.upper()} branch was already up to date (ID: {remote_version[:10]}).")
        
        if SHOULD_CREATE_SHORTCUT:
            create_desktop_shortcut(branch_choice)
            
        launch_emulator()
        return

    print(f"New version detected. Starting download from:\n{download_url}")
    log_event(f"New version detected for the {branch_choice.upper()} branch. Starting download of package {remote_version[:10]}.")
    download_path = os.path.join(INSTALL_DIR, "flycast_update.zip")
    
    try:
        req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(download_path, 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        msg_error = f"Error during download: {e}"
        print(msg_error)
        log_event(msg_error)
        return

    print("Download complete. Extracting files and replacing the old version...")
    try:
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(INSTALL_DIR)
    except Exception as e:
        msg_error = f"Error during extraction: {e}"
        print(msg_error)
        log_event(msg_error)
    finally:
        if os.path.exists(download_path):
            os.remove(download_path)

    with open(VERSION_FILE, "w") as f:
        f.write(remote_version)

    print(f"Success! Flycast ({branch_choice.upper()}) was successfully updated.")
    log_event(f"Update completed successfully. Flycast updated to version {remote_version[:10]}.")
    
    if SHOULD_CREATE_SHORTCUT:
        create_desktop_shortcut(branch_choice)
        
    launch_emulator()

if __name__ == "__main__":
    main()