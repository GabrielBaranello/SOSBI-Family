# pyright: reportUndefinedVariable=false
import subprocess, psutil, ctypes, os, json, urllib.request, zipfile
from log_utils import write_log

#error intencionar
# sdgjhg

_SOLO_RUTA = ".\\windows\\"
_RCLONE_RUTA = _SOLO_RUTA + "rclone.exe"
_7Z_RUTA = _SOLO_RUTA + "7z.exe"
_VENTOY_RUTA = _SOLO_RUTA + "Ventoy2Disk.exe"
_DONE_RUTA = _SOLO_RUTA + "cli_done.txt"
_LOG_RUTA = _SOLO_RUTA + "cli_log.txt"
USUARIO = "rltvty2"
REPO = "ulli"
NOMBRE_PS1 = "ulli-windows.ps1"
executedULLI = False
discos = psutil.disk_partitions()

def es_extraible(device):
    try:
        disk_name = device.replace('/dev/', '').rstrip('0123456789')
        with open(f'/sys/block/{disk_name}/removable', 'r') as f:
            return f.read().strip() == '1'
    except:
        return False

def detectar_usbs():
    return [d.device.rstrip('\\') for d in discos if 'removable' in d.opts] + ["Usb Less Instaler (only Linux)"]

def download(url, destino):
    subprocess.run(f'curl -L {url} -o {destino}', shell=True)
    with open(destino, "rb") as f:
        data = f.read(1024 * 1024)  # leer 1MB
        if b"<html" in data.lower():
            write_log("Descargaste HTML, no una ISO", "error")
        if b"CD001" not in data:
            write_log(f"{destino} no parece una ISO válida", "error")
        if os.path.getsize(destino) < 100 * 1024 * 1024:  # <500MB
            res = input(f"Archivo demasiado chico para ser ISO: {os.path.getsize(destino) / (1024 * 1024)} MB ¿desea  continua igualmente? (y/n)")
            if res.lower() == "n":
                write_log(f"El usuario decidio no continuar porque el archibo era muy pequeño: {os.path.getsize(destino) / (1024 * 1024)} MB", "error")

def backup_estructura_correspondiente():
    r = input(f"¿Desea respaldar el contenido de la carpeta de usuarios? (all/I/No): ").lower()
    if r == 'i':
        backup_y_subida("C:\\Users\\{os.getlogin()}", "Backup_Usuario_Actual", target_usb) # ignore
    elif r == 'all':
        if es_admin():
            backup_y_subida("C:\\Users", "Backup_Usuarios", target_usb)
        else:
            print("No se tienen permisos de administrador. No se respaldarán los otros usuarios.")
            backup_y_subida("C:\\Users\\{os.getlogin()}", "Backup_Usuario_Actual", target_usb)
    elif r == 'no':
        print("No se respaldará la carpeta de usuarios.")
    for p in [d.device.rstrip('\\') for d in discos if 'fixed' in d.opts and 'C:' not in d.device]:
        if input(f"¿Respaldar partición {p}? (s/n): ").lower() == 's':
            backup_y_subida(p, f"Backup_Disco_{p[0]}", target_usb)

def detectar_particiones():
    return [
        {
            'device': p,
            'mountpoint': next((d.mountpoint for d in discos if d.device.rstrip('\\') == p), ''),
            'fstype': next((d.fstype for d in discos if d.device.rstrip('\\') == p), ''),
            'opts': next((d.opts for d in discos if d.device.rstrip('\\') == p), ''),
        }
        for p in [d.device.rstrip('\\') for d in discos if 'fixed' in d.opts and 'C:' not in d.device]
    ]

def es_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
"""
def hacer_booteable(usb_path, iso_path):
    subprocess.run([_RUFUS_RUTA, "--iso", iso_path, "--device", usb_path, "--mode", "0", "--format", "--filesystem", "fat32"], shell=True)
"""
def instalar_ventoy_gpt(drive_letter):
    drive_letter = drive_letter.rstrip("\\")
    if not os.path.exists(_VENTOY_RUTA):
        write_log(f"No se encontró Ventoy2Disk.exe en {_VENTOY_RUTA}", "error")
        return False

    cmd_base = [_VENTOY_RUTA, "VTOYCLI"]

    def _run(cmd):
        write_log("Ejecutando Ventoy: " + " ".join(cmd), "info")
        result = subprocess.run(cmd, cwd=_SOLO_RUTA)
        done = _read_cli_done(_DONE_RUTA)
        if done == "0":
            return True
        if done == "1":
            _log_cli_tail(_LOG_RUTA)
            return False
        return result.returncode == 0

    # Intento de instalación en GPT
    if input("Desea instalar ventoy? (s/n) ").lower() == "n":
        return True
    if _run(cmd_base + ["/I", f"/Drive:{drive_letter}"]):
        write_log("Ventoy instalado en GPT.", "info")
        return True

    # Si falla, intentar update
    write_log("Instalación Ventoy falló, intentando update.", "warning")
    if _run(cmd_base + ["/U", f"/Drive:{drive_letter}"]):
        write_log("Ventoy actualizado correctamente.", "info")
        return True

    write_log("Ventoy falló en instalación/update.", "error")
    return False 

def obtener_url_ultimo_release():
    api_url = f"https://api.github.com/repos/{USUARIO}/{REPO}/releases/latest"
    try:
        # Consultar la API de GitHub
        with urllib.request.urlopen(api_url) as response:
            data = json.loads(response.read().decode())
            # 'zipball_url' apunta siempre al código fuente del último release
            return data['zipball_url']
    except Exception as e:
        print(f"Error al conectar con la API de GitHub: {e}")
        return None

def Execute_ULLI():
    global executedULLI
    if executedULLI == True: return
    # 1. Obtener URL y descargar (igual que antes)
    url_descarga = obtener_url_ultimo_release()
    if not url_descarga: return
    
    zip_local = "update.zip"
    carpeta_destino = "temp_folder"
    urllib.request.urlretrieve(url_descarga, zip_local)

    with zipfile.ZipFile(zip_local, 'r') as zip_ref:
        zip_ref.extractall(carpeta_destino)
    print("Execute_ULLI ejecutado")

    # 2. Lógica de búsqueda flexible
    archivo_a_ejecutar = None
    NOMBRE_ESPECIFICO = "ulli-windows.ps1" # El que prefieres
    
    todos_los_ps1 = []

    for raiz, dirs, archivos in os.walk(carpeta_destino):
        for archivo in archivos:
            if archivo.endswith(".ps1"):
                ruta_completa = os.path.join(raiz, archivo)
                todos_los_ps1.append(ruta_completa)
                
                # Si encontramos el específico, lo elegimos de inmediato
                if archivo.lower() == NOMBRE_ESPECIFICO.lower():
                    archivo_a_ejecutar = ruta_completa
                    break
        if archivo_a_ejecutar: break

    # 3. Si no encontró el específico, pero hay otros .bat
    if not archivo_a_ejecutar and todos_los_ps1:
        archivo_a_ejecutar = todos_los_ps1[0]
        print(f"⚠️ No se halló {NOMBRE_ESPECIFICO}. Usando el primero encontrado: {os.path.basename(archivo_a_ejecutar)}")

    # 4. Ejecución
    if archivo_a_ejecutar:
        archivo_a_ejecutar = ".\\" + archivo_a_ejecutar
        comando = [
            "powershell.exe", 
            "-ExecutionPolicy", "Bypass", 
            "-File", archivo_a_ejecutar
        ]
        print(f"🚀 Ejecutando: {archivo_a_ejecutar}")
        # 'cwd' asegura que el .bat se ejecute DENTRO de su carpeta (importante para rutas relativas)
        #subprocess.run([archivo_a_ejecutar], shell=True, cwd=os.path.dirname(archivo_a_ejecutar))
        subprocess.Popen(comando,  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
        executed_ULLI = True
    else:
        print("❌ Error: No se encontró ningún archivo .ps1 en el paquete.")

def _read_cli_done(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception:
        return None

def _log_cli_tail(path, max_lines=5):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines()
            tail = lines[-max_lines:] if len(lines) >= max_lines else lines
            if tail:
                write_log("Ventoy log: " + " | ".join(tail), "info")
    except Exception:
        pass

def cancel():
    print("Cancelando...")
    with open("state.json", "rw") as f:
        data = json.load(f)
        data.append({"canceled" : True})
        json.dump(data, f, indent=2)
