#pyright: reportUndefinedVariable=false
import subprocess, os


_SOLO_RUTA = ".\\windows\\"
_RCLONE_RUTA = _SOLO_RUTA + "rclone.exe"
_7Z_RUTA = _SOLO_RUTA + "7z.exe"
_VENTOY_RUTA = _SOLO_RUTA + "Ventoy2Disk.exe"
_DONE_RUTA = _SOLO_RUTA + "cli_done.txt"
_LOG_RUTA = _SOLO_RUTA + "cli_log.txt"
USUARIO = "rltvty2"
REPO = "ulli"
NOMBRE_PS1 = "ulli-windows.ps1"

discos = psutil.disk_partitions()

def instalar_ventoy_gpt(drive_letter):
    drive_letter = drive_letter.rstrip("\\")
    if not os.path.exists(_VENTOY_RUTA):
        write_log(f"No se encontró Ventoy2Disk.exe en {_VENTOY_RUTA}", "error")
        return False
    args = ["/I", f"/Drive:{drive_letter.rstrip('\\')}"]
    cmd_base = [_VENTOY_RUTA, "VTOYCLI"]

    def _run(cmd):
        write_log("Ejecutando Ventoy: " + " ".join(cmd), "info")
        result = subprocess.run(cmd, cwd=_VENTOY_RUTA)
        return result.returncode == 0

    # Intento de instalación en GPT
    if _run(cmd_base + args):
        write_log("Ventoy instalado en GPT.", "info")
        return True

    # Si falla, intentar update
    write_log("Instalación Ventoy falló, intentando update.", "warning")
    if _run(cmd_base + ["/U", f"/Drive:{drive_letter}"]):
        write_log("Ventoy actualizado correctamente.", "info")
        return True

    write_log("Ventoy falló en instalación/update.", "error")
    return False 

def es_extraible(device):
    # En Linux, buscamos en /sys/block/ si el dispositivo es 'removable'
    try:
        # Extraer el nombre del disco (ej: de '/dev/sdb1' a 'sdb')
        disk_name = device.replace('/dev/', '').rstrip('0123456789')
        with open(f'/sys/block/{disk_name}/removable', 'r') as f:
            return f.read().strip() == '1'
    except:
        return False

def detectar_usbs():
    return [d.device for d in discos if '/media' in d.mountpoint or es_extraible(d.device)] + ["Usb Less Instaler (only Linux)"]

def detectar_particiones():
    return ["There are no partitions due to the GNU file system."]

def download(url, archibo):
    subprocess.run(f"wget -O {archibo} {url}")
