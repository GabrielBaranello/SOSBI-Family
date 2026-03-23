# pyright: reportUndefinedVariable=false
import subprocess, psutil, ctypes

_RCLONE_RUTA = ".\\windows\\rclone.exe"
_7Z_RUTA = ".\\windows\\7z.exe"
_VENTOY_RUTA = ".\\windows\\ventoy-1.1.10\\Ventoy2Disk.exe"
_DONE_RUTA = ".\\windows\\ventoy-1.1.10\\cli_done.txt"
_LOG_RUTA = ".\\windows\\ventoy-1.1.10\\cli_log.txt"
discos = psutil.disk_partitions()

def es_extraible(device):
    try:
        disk_name = device.replace('/dev/', '').rstrip('0123456789')
        with open(f'/sys/block/{disk_name}/removable', 'r') as f:
            return f.read().strip() == '1'
    except:
        return False

def detectar_usbs():
    return discos, [d.device.rstrip('\\') for d in discos if 'removable' in d.opts]

def download(url, destino):
    subprocess.run(f'curl -L {url} -o {destino}', shell=True)

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
        result = subprocess.run(cmd, cwd=_VENTOY_RUTA)
        done = _read_cli_done(_DONE_RUTA)
        if done == "0":
            return True
        if done == "1":
            _log_cli_tail(_LOG_RUTA)
            return False
        return result.returncode == 0

    # Intento de instalación en GPT
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