# Copyright (c) 2026 Gabriel Baranello
# Licensed under the Apache License, Version 2.0
import os
import subprocess
import shutil
import time
import webbrowser
import threading
from log_utils import write_log
from state_utils import write_state, read_state
from log_server import start_server
from windows.windows_py import detectar_usbs, download, _7Z_RUTA, _RCLONE_RUTA, _VENTOY_RUTA, _DONE_RUTA, _LOG_RUTA, instalar_ventoy_gpt, detectar_particiones
# --- CONFIGURACIÓN DE SISTEMAS (Pon tus links directos aquí) ---
copy = False
usb = True

SISTEMAS = {
    "1": {"nombre": "Tomex OS", "url": "https://tu-servidor.com"},
    "2": {"nombre": "Chot OS", "url": "https://tu-servidor.com"},
    "3": {"nombre": "Mini OS", "url": "https://tu-servidor.com"},
    "4": {"nombre": "Ubuntu", "url": "https://releases.ubuntu.com"},
    "5": {"nombre": "Windows 10", "url": "https://tu-servidor.com"},
    "6": {"nombre": "Windows 11", "url": "https://tu-servidor.com"},
}
"""
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
            copy = True
            return ruta_local
        else:
            "print(\"Archivo no encontrado. Volviendo al menú.\")"
            return seleccionar_os()
    elif opcion == "0":
        "print(\"Saliendo...\")"
        exit()
    return SISTEMAS.get(opcion, {}).get("url")
"""
def backup_y_subida(origen, nombre_backup, letra_usb):
    temp_usb = f"{letra_usb}\\.temp_backup"
    if not os.path.exists(temp_usb): os.makedirs(temp_usb)
    
    "print(f\"\\nRespaldando {origen}...\")"
    # -p indica contraseña opcional, -v2g fragmentos, -ssw archivos abiertos
    subprocess.run(f'{_7Z_RUTA} a "{temp_usb}\\{nombre_backup}.7z" "{origen}" -v2g -mx1 -ssw -xr!AppData', shell=True, timeout=3600)
    
    "print(\"Subiendo a la nube mediante Rclone...\")"
    subprocess.run(f'{_RCLONE_RUTA} move "{temp_usb}" "remote:backups/{nombre_backup}" --progress', shell=True)

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


def copiar_iso_a_usb(origen, usb_drive):
    usb_root = usb_drive.rstrip("\\") + "\\"
    if os.path.exists(origen):
        nombre = os.path.basename(origen) or "os_setup.iso"
        destino = os.path.join(usb_root, nombre)
        if os.path.abspath(origen).lower() == os.path.abspath(destino).lower():
            return destino
        write_log(f"Copiando ISO a {destino}", "info")
        shutil.copy2(origen, destino)
        return destino
    return None

def main():
    global copy, usb
    with open("log.json", "w") as archivo:
        pass # No se escribe nada, el archivo queda vacío
    write_state({'start_install': False})
    # 1. Detectar USB
    discos, usbs = detectar_usbs()
    # Guardar la detección en el state.json para que la UI la consuma
    """partitions = [
        {
            'device': d.device.rstrip('\\'),
            'mountpoint': d.mountpoint,
            'fstype': d.fstype,
            'opts': d.opts,
        }
        for d in discos if 'fixed' in d.opts
    ]"""
    partitions = detectar_particiones()
    write_state({'usb_devices': usbs, 'systems': SISTEMAS, 'partitions': partitions})
    # "print(\"Error: No se detectó ningún USB.\")"
    if not usbs:
        write_log("No se detectó ningún USB.", "error")
        return
    write_log("Unidades extraibles detectadas:", "info")
    """if len(usbs) == 1:
        target_usb = usbs[0]
        write_log(f"Seleccionando automáticamente: {target_usb}", "info")
        write_state({'selected_usb': target_usb})
    """
    
    for i in range(len(usbs)):
        "print(f\"{i}. unidad USB {usbs[i]}\")"
    "target_usb = usbs[int(input(\"Elija un USB para generar el medio de instalacion: \"))]"
    # 3. Respaldos (USB + Usuarios + Particiones)
    # Interacción con el usuario ahora via UI: se espera que la webview POSTee selections
    """if input(f\"\n¿Desea respaldar el contenido del USB {target_usb}? (s/n): \").lower() == 's':\n
    backup_y_subida(target_usb, \"Backup_USB\", target_usb)
    """
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
        if selected == "Usb Less Instaler":
            usb = False
        else:
            usb = True
            target_usb = selected
    else:
        write_log('No se recibió selección de USB desde la interfaz.', 'warning')
        return
    #backup_y_subida("C:\\Users", "Backup_Usuarios", target_usb)
    
    # 4. Otras particiones (desde UI)
    st = read_state()
    selected_parts = st.get('selected_partitions') or []
    if selected_parts:
        for p in selected_parts:
            write_log(f"Respaldando partición: {p}", "info")
            try:
                backup_y_subida(p, f"Backup_Disco_{p[0]}", target_usb)
            except Exception as e:
                write_log(f"Error respaldando {p}: {e}", "error")
    else:
        write_log("No se seleccionaron particiones para respaldo.", "info")

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
    elif selected_sys and isinstance(selected_sys, str) and os.path.exists(selected_sys):
        url_descarga = selected_sys
        copy = True
    if not url_descarga:
        write_log("URL no válida.", "error")
        return

    # Esperar señal desde la pantalla de instalación
    start_install = None
    for _ in range(600):
        st = read_state()
        start_install = st.get('start_install')
        if start_install:
            break
        time.sleep(0.5)
    if not start_install:
        write_log('No se recibió inicio desde la pantalla de instalación.', 'warning')
        

    # "print(f\"Descargando archivos de sistema desde: {url_descarga}\")"
    if not instalar_ventoy_gpt(target_usb):
        return
    # Descargar o copiar ISO después de instalar Ventoy (evita que se borre)
    if url_descarga and isinstance(url_descarga, str) and os.path.exists(url_descarga):
        copiar_iso_a_usb(url_descarga, target_usb)
    else:
        nombre = os.path.basename(url_descarga) if isinstance(url_descarga, str) else "os_setup.iso"
        if not nombre or "." not in nombre:
            nombre = "os_setup.iso"
        archivo_dest = f"{target_usb}\\{nombre}"
        download(url_descarga, archivo_dest)

    # 6. Finalizar
    write_log("Proceso completado: USB booteable generado.", "info")
    input("Presione Enter para continuar con el reinicio...")
    subprocess.run("shutdown /r /fw /t 15", shell=True)

if __name__ == "__main__":
    # Levanta el servidor HTTP para la UI (estado/logs)
    start_server()
    # Ejecuta la lógica principal en un hilo para mantener viva la UI
    threading.Thread(target=main, daemon=True).start()
    # Abre la interfaz en webview (fallback al navegador si no está instalado)
    try:
        import webview
        webview.create_window("S.O.S.B.I Wizard", "http://127.0.0.1:8000/index.html")
        webview.start()
    except Exception:
        try:
            webbrowser.open("http://127.0.0.1:8000/index.html")
        except Exception:
            pass

# Ejemplo de uso integrado:
# letra_usb = "F:\\"
# url_elegida = "https://tu-enlace-directo.com"
# descargar_y_descomprimir(url_elegida, letra_usb)

#generar_lista_programas()
