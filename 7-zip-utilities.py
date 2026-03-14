# Copyright (c) 2026 Gabriel Baranello
# Licensed under the Apache License, Version 2.0

import winreg
import requests
import os
import zipfile
from tqdm import tqdm # pip install tqdm (para ver la barra de progreso)

def descargar_y_descomprimir(url, destino_usb):
    # 1. Definir ruta temporal para el archivo comprimido
    archivo_zip = os.path.join(destino_usb, "os_setup.zip")
    
    print(f"Iniciando descarga desde: {url}")
    
    try:
        # 2. Descarga con flujo (stream) para manejar archivos grandes
        respuesta = requests.get(url, stream=True, allow_redirects=True)
        respuesta.raise_for_status() # Lanza error si el link está caído
        
        total_size = int(respuesta.headers.get('content-length', 0))
        
        # Barra de progreso visual
        with open(archivo_zip, 'wb') as f, tqdm(
            desc="Descargando",
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for datos in respuesta.iter_content(chunk_size=1024 * 1024): # Bloques de 1MB
                f.write(datos)
                bar.update(len(datos))

        # 3. Descompresión automática
        print(f"\nExtrayendo archivos en {destino_usb}...")
        with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
            # extractall() pone todo el árbol de archivos en la raíz del USB
            zip_ref.extractall(destino_usb)
        
        # 4. Limpieza: Borrar el .zip para dejar espacio
        os.remove(archivo_zip)
        print("✅ Instalación completada en el USB.")
        return True

    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")
        return False

# Ejemplo de uso integrado:
# letra_usb = "F:\\"
# url_elegida = "https://tu-enlace-directo.com"
# descargar_y_descomprimir(url_elegida, letra_usb)
