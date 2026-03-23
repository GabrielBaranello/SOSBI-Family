import os, psutil

def es_extraible(device):
    try:
        disk_name = device.replace('/dev/', '').rstrip('0123456789')
        with open(f'/sys/block/{disk_name}/removable', 'r') as f:
            return f.read().strip() == '1'
    except:
        return False
discos = psutil.disk_partitions()

def detectar_usbs():
    return [d.device for d in discos if '/media' in d.mountpoint or es_extraible(d.device)]