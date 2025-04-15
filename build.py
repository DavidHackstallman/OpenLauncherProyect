import os
import sys
import subprocess
import shutil

def build_executable():
    print("Iniciando la creación del ejecutable...")
    
    # Verificar si PyInstaller está instalado
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller no está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
        print("PyInstaller instalado correctamente.")
    
    # Limpiar carpeta dist si existe
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Comando de PyInstaller
    comando = [
        sys.executable,
        "-m", "PyInstaller",
        "interfaz.py",                    # Tu archivo principal
        "--name=OpenLauncherProyect",     # Nombre del ejecutable
        "--onefile",                      # Un solo archivo ejecutable
        "--windowed",                     # Sin consola
        "--clean",                        # Limpiar archivos temporales
    ]
    
    # Agregar icono si existe
    if os.path.exists("icon.ico"):
        comando.append("--icon=icon.ico")
    else:
        print("Advertencia: No se encontró 'icon.ico'. El ejecutable usará un ícono por defecto.")
    
    # Ejecutar PyInstaller
    print("Ejecutando PyInstaller...")
    subprocess.call(comando)
    
    print("\n¡Ejecutable creado con éxito!")
    print(f"Ubicación: {os.path.abspath('dist/OpenLauncherProyect.exe')}")
    print("\nNota: Asegúrate de que los siguientes archivos estén en la misma carpeta que el ejecutable:")
    print("- funciones.py")
    print("- perfiles.py")
    
    # Verificar que la carpeta dist existe antes de copiar
    if not os.path.exists("dist"):
        os.makedirs("dist")
        
    # Copiar archivos necesarios a la carpeta dist
    print("\nCopiando archivos necesarios a la carpeta dist...")
    for archivo in ["funciones.py", "perfiles.py","interfaz.py"]:
        if os.path.exists(archivo):
            dest_path = os.path.join("dist", archivo)
            shutil.copy(archivo, dest_path)
            print(f"- {archivo} copiado correctamente")
        else:
            print(f"- ERROR: No se encontró {archivo}")

if __name__ == "__main__":
    build_executable()