import psutil, subprocess

_SOLO_RUTA = ".\\windows\\"
_RCLONE_RUTA = _SOLO_RUTA + "rclone.exe"
_7Z_RUTA = _SOLO_RUTA + "7z.exe"
_VENTOY_RUTA = _SOLO_RUTA + "Ventoy2Disk.exe"
_DONE_RUTA = _SOLO_RUTA + "cli_done.txt"
_LOG_RUTA = _SOLO_RUTA + "cli_log.txt"
USUARIO = "rltvty2"
REPO = "ulli"
NOMBRE_PS1 = "ulli-windows.ps1"

def es_extraible(device):
    try:
        disk_name = device.replace('/dev/', '').rstrip('0123456789')
        with open(f'/sys/block/{disk_name}/removable', 'r') as f:
            return f.read().strip() == '1'
    except:
        return False
discos = psutil.disk_partitions()

def detectar_usbs():
    return [d.device for d in discos if '/media' in d.mountpoint or es_extraible(d.device)] + ["Usb Less Instaler (only Linux)"]

def download(url, destino):
    subprocess.run(f'curl -L {url} -o {destino}', shell=True)

def detectar_particiones():
    return ["There are no partitions due to the GNU file system."]

def instalar_ventoy_gpt(target):
    pass