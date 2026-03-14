# Copyright (c) 2026 Gabriel Baranello
# Licensed under the Apache License, Version 2.0
import os
import subprocess
import winreg
import psutil, shutil
import time
from log_utils import write_log
from state_utils import write_state, read_state
from windows.windows_py import formatear, download, _7Z_RUTA, _RCLONE_RUTA, backup_estructura_correspondiente, hacer_booteable
# --- CONFIGURACIÓN DE SISTEMAS (Pon tus links directos aquí) ---
copy = True
SISTEMAS = {
    "1": {"nombre": "Tomex OS", "url": "https://tu-servidor.com"},
    "2": {"nombre": "Chot OS", "url": "https://tu-servidor.com"},
    "3": {"nombre": "Mini OS", "url": "https://tu-servidor.com"},
    "4": {"nombre": "Ubuntu", "url": "https://releases.ubuntu.com"},
    "5": {"nombre": "Windows 10", "url": "https://tu-servidor.com"},
    "6": {"nombre": "Windows 11", "url": "https://tu-servidor.com"},
}

def seleccionar_os():
    global copy
    "print(\"\\n--- SELECCIÓN DE SISTEMA OPERATIVO ---\")"
    for k, v in SISTEMAS.items():
        "print(f\"{k}. {v['nombre']}\")"
    "print(\"7. Descargar otro (Ingresar URL manual)\")"
    "print(\"8. Ruta en local (Ej: D:\\\\descargas\\\\windows10.iso)\")"
    "print(\"0. Salir\")"
    
    opcion = input("\nElige una opción: ")
    if opcion == "7":
        return input("Pega la URL directa del .zip o .iso: ")
    elif opcion == "8":
        ruta_local = input("Ingresa la ruta completa del archivo local: ")
        if os.path.exists(ruta_local):
            return ruta_local
        else:
            "print(\"Archivo no encontrado. Volviendo al menú.\")"
            return seleccionar_os()
            copy = True
    elif opcion == "0":
        "print(\"Saliendo...\")"
        exit()
    return SISTEMAS.get(opcion, {}).get("url")

def backup_y_subida(origen, nombre_backup, letra_usb):
    temp_usb = f"{letra_usb}\\.temp_backup"
    if not os.path.exists(temp_usb): os.makedirs(temp_usb)
    
    "print(f\"\\nRespaldando {origen}...\")"
    # -p indica contraseña opcional, -v2g fragmentos, -ssw archivos abiertos
    subprocess.run(f'{_7Z_RUTA} a "{temp_usb}\\{nombre_backup}.7z" "{origen}" -v2g -mx1 -ssw -xr!AppData', shell=True, timeout=3600)
    
    "print(\"Subiendo a la nube mediante Rclone...\")"
    subprocess.run(f'{_RCLONE_RUTA} move "{temp_usb}" "remote:backups/{nombre_backup}" --progress', shell=True)

def main():
    # 1. Detectar USB
    discos = psutil.disk_partitions()
    usbs = [d.device.rstrip('\\') for d in discos if 'removable' in d.opts]
    # Guardar la detección en el state.json para que la UI la consuma
    write_state({'usb_devices': usbs, 'systems': SISTEMAS})
    # "print(\"Error: No se detectó ningún USB.\")"
    if not usbs:
        write_log("No se detectó ningún USB.", "error")
        return
    write_log("Unidades extraibles detectadas:", "info")
    if len(usbs) == 1:
        target_usb = usbs[0]
        write_log(f"Seleccionando automáticamente: {target_usb}", "info")
        write_state({'selected_usb': target_usb})
    else:
        for i in range(len(usbs)):
            "print(f\"{i}. unidad USB {usbs[i]}\")"
        "target_usb = usbs[int(input(\"Elija un USB para generar el medio de instalacion: \"))]"
    write_log(f"Trabajando en: {target_usb}", "info")

    # 3. Respaldos (USB + Usuarios + Particiones)
    # Interacción con el usuario ahora via UI: se espera que la webview POSTee selections
    # "if input(f\"\n¿Desea respaldar el contenido del USB {target_usb}? (s/n): \").lower() == 's':\n        #backup_y_subida(target_usb, \"Backup_USB\", target_usb)"
    # Esperar selección de UI en state.json
    selected = None
    for _ in range(600):
        st = read_state()
        selected = st.get('selected_usb')
        if selected:
            break
        time.sleep(0.5)
    if selected:
        write_log(f"Usuario seleccionó USB: {selected}", 'info')
        # Aquí se puede continuar usando `selected` como target_usb
        target_usb = selected
    else:
        write_log('No se recibió selección de USB desde la interfaz.', 'warning')
        return
    #backup_y_subida("C:\\Users", "Backup_Usuarios", target_usb)
    
    # 4. Otras particiones
    backup_estructura_correspondiente()

    # 5. Formatear y Descargar
    # Esperar selección de sistema desde UI
    selected_sys = None
    for _ in range(600):
        st = read_state()
        selected_sys = st.get('selected_system')
        if selected_sys:
            break
        time.sleep(0.5)
    if selected_sys:
        write_log(f"Usuario seleccionó sistema: {selected_sys}", 'info')
    else:
        write_log('No se recibió selección de sistema desde la interfaz.', 'warning')
        return

    # Resolver URL según selección
    url_descarga = None
    if selected_sys in SISTEMAS:
        url_descarga = SISTEMAS[selected_sys].get('url')
    elif selected_sys and isinstance(selected_sys, str) and selected_sys.startswith(("http://", "https://")):
        url_descarga = selected_sys
    if not url_descarga:
        write_log("URL no válida.", "error")
        return

    # "print(f\"Descargando archivos de sistema desde: {url_descarga}\")"
    # Usamos curl (nativo en Win10/11) para descargar al USB
    archivo_dest = f"{target_usb}\\os_setup.iso"
    if copy:
        archivo_dest = url_descarga
    else:
        download(url_descarga, archivo_dest)
    #subprocess.run(f'curl -L {url_descarga} -o {archivo_dest}', shell=True)
    
    #print("Extrayendo archivos en la raíz del USB...")
    #subprocess.run(f'{_7Z_RUTA} x {archivo_dest} -o{target_usb}', shell=True)
    #os.remove(archivo_dest)
    
    hacer_booteable(target_usb, archivo_dest)

    # 6. Finalizar
    write_log("Proceso completado: USB booteable generado.", "info")
    input("Presione Enter para continuar con el reinicio...")
    subprocess.run("shutdown /r /fw /t 15", shell=True)




if __name__ == "__main__":
    main()

# Ejemplo de uso integrado:
# letra_usb = "F:\\"
# url_elegida = "https://tu-enlace-directo.com"
# descargar_y_descomprimir(url_elegida, letra_usb)

#generar_lista_programas()
