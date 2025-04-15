import minecraft_launcher_lib
import subprocess
import os
import requests
import hashlib
from tkinter import messagebox
from tkinter import Tk, Text

MINECRAFT_DIR = os.path.join(os.getenv("APPDATA"), ".minecraftLauncher")
txt_mensajes = None
def configurar_mensajes(widget):
    global txt_mensajes
    txt_mensajes = widget

def mostrar_mensaje(mensaje, tipo="info"):
    if txt_mensajes:
        # Limitar a 15 líneas máximo
        lineas = int(txt_mensajes.index('end-1c').split('.')[0])
        if lineas > 15:
            txt_mensajes.delete(1.0, 5.0)
            
        # Añadir mensaje con formato
        txt_mensajes.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}\n", tipo)
        txt_mensajes.see(tk.END)  # Auto-scroll
def obtener_versiones_instaladas():
    versiones = minecraft_launcher_lib.utils.get_installed_versions(MINECRAFT_DIR)
    return [v['id'] for v in versiones] or ['sin versiones instaladas']
def mostrar_info_inicial():
    mensaje = """
    ⚠️ Antes de jugar:
    1. Java 8 instalado -> {}
    2. Carpeta de mods -> {}
    3. Versión 1.16.5 requiere Forge/Fabric específico
    """.format(
        verificar_java_instalado(),
        os.path.join(MINECRAFT_DIR, "mods")
    )
    return mensaje

def verificar_java_instalado():
    try:
        # Verificar versión de Java
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        return "✅ Instalado" if "1.8" in result.stderr else "❌ Versión incorrecta"
    except:
        return "❌ No detectado"
def instalar_version(version):
    try:
        minecraft_launcher_lib.install.install_minecraft_version(version, MINECRAFT_DIR)
        messagebox.showinfo("Éxito", "Descarga terminada")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo descargar la versión:\n{e}")

def instalar_forge(version):
    try:
        forge_version = minecraft_launcher_lib.forge.find_forge_version(version)
        minecraft_launcher_lib.forge.install_forge_version(forge_version, MINECRAFT_DIR)
        messagebox.showinfo("Éxito", "Forge instalado correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo instalar Forge:\n{e}")

def instalar_fabric(version):
    try:
        # Verificar conexión
        requests.get("https://api.modrinth.com", timeout=5)
        
        minecraft_launcher_lib.fabric.install_fabric(version, MINECRAFT_DIR)
        MODS_DIR = os.path.join(MINECRAFT_DIR, "mods")
        os.makedirs(MODS_DIR, exist_ok=True)

        url = "https://api.modrinth.com/v2/project/P7dR8mSH/version"
        response = requests.get(url)
        response.raise_for_status()

        fabric_api_url = None
        for v in response.json():
            if version in v.get("game_versions", []):
                fabric_api_url = v["files"][0]["url"]
                filename = v["files"][0]["filename"]
                break

        if fabric_api_url:
            fabric_api_path = os.path.join(MODS_DIR, filename)
            with open(fabric_api_path, "wb") as f:
                f.write(requests.get(fabric_api_url).content)
            messagebox.showinfo("Éxito", "Fabric y API instalados")
        else:
            messagebox.showwarning("Aviso", f"Fabric API no disponible para {version}")

    except requests.ConnectionError:
        messagebox.showerror("Error", "¡Sin conexión a Internet!")
    except Exception as e:
        messagebox.showerror("Error", f"Error en Fabric:\n{e}")

def generar_uuid_offline(nombre):
    md5 = hashlib.md5(f"OfflinePlayer:{nombre}".encode()).hexdigest()
    return f"{md5[:8]}-{md5[8:12]}-{md5[12:16]}-{md5[16:20]}-{md5[20:]}"

def ejecutar_minecraft(nombre, version, ram, cerrar_launcher):
    try:
        if not ram.isdigit():
            raise ValueError("La RAM debe ser un número entero")

        options = {
            'username': nombre,
            'uuid': generar_uuid_offline(nombre),
            'token': '',
            'jvArguments': [f"-Xms{ram}G", f"-Xmx{ram}G"],
            'launcherVersion': "0.0.2"
        }

        cerrar_launcher()
        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
            version, MINECRAFT_DIR, options
        )
        subprocess.run(minecraft_command, cwd=MINECRAFT_DIR)

    # Bloque except añadido ↓
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar el juego:\n{str(e)}")
