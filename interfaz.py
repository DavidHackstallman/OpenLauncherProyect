from tkinter import messagebox, StringVar, Toplevel, ttk
import os
import webbrowser
from functools import partial
import tkinter as tk
from funciones import MINECRAFT_DIR
from funciones import obtener_versiones_instaladas, instalar_version, instalar_forge, instalar_fabric, ejecutar_minecraft
from tkinter import StringVar, Toplevel, messagebox
import perfiles  # Importamos el módulo de perfiles simplificado

# ========== Componentes Personalizados ==========
class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="", color='grey', **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg = self['fg']
        
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._restore_placeholder)
        
        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def _clear_placeholder(self, event):
        if self['fg'] == self.placeholder_color:
            self.delete(0, tk.END)
            self['fg'] = self.default_fg

    def _restore_placeholder(self, event):
        if not self.get():
            self.put_placeholder()

    def get_clean(self):
        if self['fg'] == self.placeholder_color:
            return ""
        return self.get()
    
    def set_text(self, text):
        self.delete(0, tk.END)
        if text:
            self.insert(0, text)
            self['fg'] = self.default_fg
        else:
            self.put_placeholder()

class PlayButton(tk.Canvas):
    def __init__(self, master=None, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bd=0, highlightthickness=0, width=120, height=40)
        self.command = command
        
        # Fondo con efecto hover
        self.bg = self.create_rectangle(0, 0, 120, 40, fill="#27ae60", outline="")
        
        # Triángulo de play
        self.create_polygon(40, 10, 40, 30, 60, 20, fill='white')
        
        # Texto
        self.create_text(80, 20, text="JUGAR", fill='white', 
                       font=('Arial', 10, 'bold'))
        
        # Eventos
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, event):
        self.itemconfig(self.bg, fill="#219d54")

    def _on_leave(self, event):
        self.itemconfig(self.bg, fill="#27ae60")

    def _on_click(self, event):
        if self.command:
            self.command()

# ========== Función Principal ==========
def lanzar_launcher():
    ventana = tk.Tk()
    ventana.title("OpenLauncherProyect")
    ventana.geometry("700x600")
    ventana.configure(bg="#2c3e50")
    ventana.resizable(False, False)

    # Inicializar perfiles
    perfiles.inicializar_perfiles()
    perfil_actual = StringVar(value="default")

    # Configuración de estilo
    estilo_botones = {
        'bg': "#3498db",
        'fg': "white",
        'font': ('Arial', 10),
        'relief': 'flat',
        'activebackground': "#2980b9"
    }

    # ===== Cabecera =====
    frame_cabecera = tk.Frame(ventana, bg="#34495e")
    frame_cabecera.pack(fill='x', pady=10)
    
    tk.Label(frame_cabecera, 
           text="Open Launcher Proyect",
           font=('Arial', 14, 'bold'),
           bg="#34495e",
           fg="white").pack(pady=10)

    # ===== Cuerpo Principal =====
    frame_principal = tk.Frame(ventana, bg="#2c3e50")
    frame_principal.pack(fill='both', expand=True)

    # === Panel Izquierdo (Controles) ===
    frame_controles = tk.Frame(frame_principal, bg="#2c3e50")
    frame_controles.grid(row=0, column=0, padx=20, pady=10, sticky='nsew')

    # Frame para perfiles
    frame_perfiles = tk.Frame(frame_controles, bg="#2c3e50")
    frame_perfiles.pack(fill='x', pady=5)
    
    tk.Label(frame_perfiles, text="Perfil:", bg="#2c3e50", fg="white").pack(side='left', padx=5)
    
    # Cargar lista de perfiles
    lista_perfiles = perfiles.listar_perfiles()
    
    def cargar_perfil(*args):
        datos_perfil = perfiles.obtener_perfil(perfil_actual.get())
        entry_nombre.set_text(datos_perfil.get("nombre", ""))
        entry_ram.set_text(datos_perfil.get("ram", ""))
    
    perfil_menu = ttk.Combobox(frame_perfiles, textvariable=perfil_actual, values=lista_perfiles, state="readonly")
    perfil_menu.pack(side='left', padx=5, fill='x', expand=True)
    perfil_actual.trace("w", cargar_perfil)
    
    # Botones de gestión de perfiles
    btn_guardar_perfil = tk.Button(frame_perfiles, text="💾", 
                                  command=lambda: mostrar_guardar_perfil(), **estilo_botones)
    btn_guardar_perfil.pack(side='left', padx=2)
    
    btn_nuevo_perfil = tk.Button(frame_perfiles, text="➕", 
                               command=lambda: mostrar_nuevo_perfil(), **estilo_botones)
    btn_nuevo_perfil.pack(side='left', padx=2)
    
    btn_eliminar_perfil = tk.Button(frame_perfiles, text="❌", 
                                  command=lambda: eliminar_perfil_actual(), **estilo_botones)
    btn_eliminar_perfil.pack(side='left', padx=2)

    # Campos de entrada
    entry_nombre = PlaceholderEntry(frame_controles, 
                                  placeholder="Nombre de Minecraft",
                                  width=30)
    entry_nombre.pack(pady=10)

    entry_ram = PlaceholderEntry(frame_controles, 
                              placeholder="RAM (GB)",
                              width=15)
    entry_ram.pack(pady=10)

    # Selector de versión
    versiones_lista = obtener_versiones_instaladas()
    vers_var = StringVar(value=versiones_lista[0] if versiones_lista else "")
    
    def actualizar_versiones():
        nuevas_versiones = obtener_versiones_instaladas()
        versiones_lista = nuevas_versiones
        if nuevas_versiones:
            vers_var.set(nuevas_versiones[0])
        else:
            vers_var.set("")
        menu = versiones_menu["menu"]
        menu.delete(0, "end")
        for version in nuevas_versiones:
            menu.add_command(label=version, command=lambda v=version: vers_var.set(v))
    
    versiones_menu = tk.OptionMenu(frame_controles, vers_var, *versiones_lista)
    versiones_menu.config(bg="#3498db", fg="white")
    versiones_menu.pack(pady=10)
    
    # Botón para instalar versiones
    def abrir_ventana_instalacion():
        ventana_instalar = Toplevel()
        ventana_instalar.title("Instalar versión")
        ventana_instalar.geometry("300x250")
        ventana_instalar.configure(bg="#2c3e50")

        tk.Label(ventana_instalar, text="Versión:", bg="#2c3e50", fg="white").pack(pady=5)
        entry_version = tk.Entry(ventana_instalar)
        entry_version.pack(pady=5)

        tipo_instalacion = StringVar(value="vanilla")
        tk.Radiobutton(ventana_instalar, text="Vanilla", variable=tipo_instalacion, value="vanilla", 
                      bg="#2c3e50", fg="white", selectcolor="#34495e").pack()
        tk.Radiobutton(ventana_instalar, text="Forge", variable=tipo_instalacion, value="forge", 
                      bg="#2c3e50", fg="white", selectcolor="#34495e").pack()
        tk.Radiobutton(ventana_instalar, text="Fabric", variable=tipo_instalacion, value="fabric", 
                      bg="#2c3e50", fg="white", selectcolor="#34495e").pack()

        label_estado = tk.Label(ventana_instalar, text="", bg="#2c3e50", fg="white")
        label_estado.pack(pady=5)

        def instalar():
            version = entry_version.get()
            if not version:
                messagebox.showwarning("Error", "Ingresa una versión")
                return

            label_estado.config(text="Descargando...")
            ventana_instalar.update()

            try:
                if tipo_instalacion.get() == "vanilla":
                    instalar_version(version)
                elif tipo_instalacion.get() == "forge":
                    instalar_forge(version)
                elif tipo_instalacion.get() == "fabric":
                    instalar_fabric(version)

                label_estado.config(text="¡Listo!")
                actualizar_versiones()
                ventana_instalar.after(1500, ventana_instalar.destroy)
            except Exception as e:
                label_estado.config(text="Error")
                messagebox.showerror("Error", str(e))

        btn_instalar = tk.Button(ventana_instalar, text="Instalar", command=instalar, **estilo_botones)
        btn_instalar.pack(pady=10)
    
    # Funciones para manejar perfiles
    def mostrar_nuevo_perfil():
        ventana_nuevo = Toplevel(ventana)
        ventana_nuevo.title("Nuevo Perfil")
        ventana_nuevo.geometry("300x100")
        ventana_nuevo.configure(bg="#2c3e50")
        
        tk.Label(ventana_nuevo, text="Nombre del perfil:", bg="#2c3e50", fg="white").pack(pady=5)
        entry_nombre_perfil = tk.Entry(ventana_nuevo, width=30)
        entry_nombre_perfil.pack(pady=5)
        
        def crear_nuevo():
            nombre = entry_nombre_perfil.get().strip()
            if not nombre:
                messagebox.showwarning("Error", "Debes ingresar un nombre")
                return
                
            exito = perfiles.crear_perfil(
                nombre, 
                entry_nombre.get_clean(),
                entry_ram.get_clean()
            )
            
            if exito:
                # Actualizar lista de perfiles
                nueva_lista = perfiles.listar_perfiles()
                perfil_menu['values'] = nueva_lista
                perfil_actual.set(nombre)
                ventana_nuevo.destroy()
            else:
                messagebox.showwarning("Error", "Ya existe un perfil con ese nombre")
        
        btn_crear = tk.Button(ventana_nuevo, text="Crear", command=crear_nuevo, **estilo_botones)
        btn_crear.pack(pady=10)
    
    def mostrar_guardar_perfil():
        nombre = perfil_actual.get()
        if nombre:
            perfiles.actualizar_perfil(
                nombre,
                entry_nombre.get_clean(),
                entry_ram.get_clean()
            )
            messagebox.showinfo("Éxito", f"Perfil '{nombre}' guardado")
    
    def eliminar_perfil_actual():
        nombre = perfil_actual.get()
        if nombre == "default":
            messagebox.showwarning("Error", "No puedes eliminar el perfil por defecto")
            return
            
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar el perfil '{nombre}'?"):
            if perfiles.eliminar_perfil(nombre):
                nueva_lista = perfiles.listar_perfiles()
                perfil_menu['values'] = nueva_lista
                perfil_actual.set("default")
                messagebox.showinfo("Éxito", f"Perfil '{nombre}' eliminado")
    
    # Cargar perfil inicial
    cargar_perfil()
    
    # Botón para abrir la ventana de instalación
    btn_instalar_version = tk.Button(frame_controles, text="Instalar Versiones", 
                                   command=abrir_ventana_instalacion, **estilo_botones)
    btn_instalar_version.pack(pady=10)

    # Botón de play
    def ejecutar_juego():
        # Guardar el perfil actual antes de ejecutar
        perfiles.actualizar_perfil(
            perfil_actual.get(),
            entry_nombre.get_clean(),
            entry_ram.get_clean()
        )
        
        # Ejecutar el juego
        ejecutar_minecraft(
            entry_nombre.get_clean(),
            vers_var.get(),
            entry_ram.get_clean(),
            ventana.destroy
        )
    
    PlayButton(frame_controles, command=ejecutar_juego).pack(pady=20)

    # === Panel Derecho (Avisos) ===
    frame_avisos = tk.Frame(frame_principal, bg="white", bd=2, relief='groove')
    frame_avisos.grid(row=0, column=1, padx=20, pady=10, sticky='nsew')

    contenido_avisos = """
    🚨 Requisitos Obligatorios:
    
    • Java 8 instalado
    • Conexión estable
    
    📍 Carpeta de mods:
    {mods_path}
    
    ⚠️ Para la 1.16.5:
    • Usar modo offline
    • Forge 36.2.39
    
    ✉️ Soporte:
    proyectopenminecraft@gmail.com
    """.format(mods_path=os.path.join(MINECRAFT_DIR, "mods"))

    txt_avisos = tk.Text(frame_avisos, wrap=tk.WORD, height=20, width=35)
    txt_avisos.insert('end', contenido_avisos)
    txt_avisos.tag_config('link', foreground='blue', underline=True)
    txt_avisos.insert('end', "\n\nDescargar Java 8", 'link')
    txt_avisos.tag_bind('link', '<Button-1>', 
                      lambda e: webbrowser.open("https://adoptium.net/temurin/releases/?version=8"))
    txt_avisos.config(state='disabled', padx=10, pady=10)
    txt_avisos.pack(fill='both')

    # ===== Área de Mensajes =====
    frame_mensajes = tk.Frame(ventana, bg="#34495e")
    frame_mensajes.pack(fill='x', padx=10, pady=10)

    txt_mensajes = tk.Text(frame_mensajes, height=6, wrap=tk.WORD, 
                         bg="#2c3e50", fg="white")
    scroll = tk.Scrollbar(frame_mensajes, command=txt_mensajes.yview)
    txt_mensajes.configure(yscrollcommand=scroll.set)
    
    scroll.pack(side='right', fill='y')
    txt_mensajes.pack(side='left', fill='both', expand=True)
    
    # Configurar tags para mensajes
    for tag, color in [('exito', '#2ecc71'), ('error', '#e74c3c'),
                      ('advertencia', '#f1c40f'), ('info', '#3498db')]:
        txt_mensajes.tag_config(tag, foreground=color)

    ventana.mainloop()

if __name__ == "__main__":
    lanzar_launcher()
