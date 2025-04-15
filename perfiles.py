import os
import json
from pathlib import Path

# Directorio para guardar los perfiles
PERFILES_DIR = os.path.join(os.path.expanduser("~"), ".openlauncherproyect")

# Asegurar que el directorio existe
if not os.path.exists(PERFILES_DIR):
    os.makedirs(PERFILES_DIR)

PERFILES_FILE = os.path.join(PERFILES_DIR, "perfiles.json")

def inicializar_perfiles():
    """Inicializa el archivo de perfiles si no existe."""
    if not os.path.exists(PERFILES_FILE):
        perfiles_default = {
            "default": {
                "nombre": "",
                "ram": "2"
            }
        }
        guardar_perfiles(perfiles_default)
        return perfiles_default
    return cargar_perfiles()

def cargar_perfiles():
    """Carga los perfiles desde el archivo JSON."""
    try:
        with open(PERFILES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Si hay un error, crea un perfil por defecto
        return inicializar_perfiles()

def guardar_perfiles(perfiles):
    """Guarda los perfiles en el archivo JSON."""
    with open(PERFILES_FILE, 'w') as f:
        json.dump(perfiles, f, indent=4)

def crear_perfil(nombre_perfil, nombre_usuario, ram):
    """
    Crea un nuevo perfil.
    
    Args:
        nombre_perfil (str): Nombre del perfil
        nombre_usuario (str): Nombre de usuario de Minecraft
        ram (str): Cantidad de RAM asignada
    
    Returns:
        bool: True si se creó correctamente, False si ya existía
    """
    perfiles = cargar_perfiles()
    
    if nombre_perfil in perfiles:
        return False
    
    perfiles[nombre_perfil] = {
        "nombre": nombre_usuario,
        "ram": ram
    }
    guardar_perfiles(perfiles)
    return True

def actualizar_perfil(nombre_perfil, nombre_usuario, ram):
    """
    Actualiza un perfil existente.
    
    Args:
        nombre_perfil (str): Nombre del perfil
        nombre_usuario (str): Nombre de usuario de Minecraft
        ram (str): Cantidad de RAM asignada
    
    Returns:
        bool: True si se actualizó correctamente, False si no existía
    """
    perfiles = cargar_perfiles()
    
    if nombre_perfil not in perfiles:
        return False
    
    perfiles[nombre_perfil] = {
        "nombre": nombre_usuario,
        "ram": ram
    }
    guardar_perfiles(perfiles)
    return True

def eliminar_perfil(nombre_perfil):
    """
    Elimina un perfil.
    
    Args:
        nombre_perfil (str): Nombre del perfil a eliminar
    
    Returns:
        bool: True si se eliminó correctamente, False si no existía
    """
    perfiles = cargar_perfiles()
    
    if nombre_perfil not in perfiles:
        return False
    
    # No permitir eliminar el perfil default
    if nombre_perfil == "default":
        return False
    
    del perfiles[nombre_perfil]
    guardar_perfiles(perfiles)
    return True

def obtener_perfil(nombre_perfil=None):
    """
    Obtiene un perfil específico o el por defecto si no se especifica.
    
    Args:
        nombre_perfil (str, optional): Nombre del perfil. Default None.
    
    Returns:
        dict: Datos del perfil (nombre y ram)
    """
    perfiles = cargar_perfiles()
    
    if nombre_perfil is None or nombre_perfil not in perfiles:
        return perfiles.get("default", {"nombre": "", "ram": "2"})
    
    return perfiles[nombre_perfil]

def listar_perfiles():
    """
    Lista todos los perfiles disponibles.
    
    Returns:
        list: Lista de nombres de perfiles
    """
    perfiles = cargar_perfiles()
    return list(perfiles.keys())