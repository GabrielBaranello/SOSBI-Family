# pyright: reportUndefinedVariable=false
import subprocess, os, psutil, ctypes

_RCLONE_RUTA = ".\\windows\\rclone.exe"
_7Z_RUTA = ".\\windows\\7z.exe"
_RUFUS_RUTA = ".\\windows\\rufus-4.13.exe"


def es_extraible(device):
    try:
        disk_name = device.replace('/dev/', '').rstrip('0123456789')
        with open(f'/sys/block/{disk_name}/removable', 'r') as f:
            return f.read().strip() == '1'
    except:
        return False

discos = psutil.disk_partitions()
def detectar_usbs():
    return discos, [d.device.rstrip('\\') for d in discos if 'removable' in d.opts]

def formatear(target):
    print(f"\nLimpiando USB {target}...")
    subprocess.run(f'format {target} /FS:FAT32 /Q /Y', shell=True)

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

def es_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def hacer_booteable(usb_path, iso_path):
    subprocess.run([_RUFUS_RUTA, "--iso", iso_path, "--device", usb_path, "--mode", "0", "--format", "--filesystem", "fat32"], shell=True)
