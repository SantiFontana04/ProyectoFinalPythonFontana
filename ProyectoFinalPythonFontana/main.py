
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------- CONFIG DB ------------------
conn = sqlite3.connect('torneo_futbol.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS Equipos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    ciudad TEXT,
    dt TEXT,
    categoria TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS Jugadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    edad INTEGER,
    posicion TEXT,
    id_equipo INTEGER,
    FOREIGN KEY(id_equipo) REFERENCES Equipos(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS Partidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo_local INTEGER,
    equipo_visitante INTEGER,
    fecha TEXT,
    resultado TEXT,
    FOREIGN KEY(equipo_local) REFERENCES Equipos(id),
    FOREIGN KEY(equipo_visitante) REFERENCES Equipos(id)
)''')

conn.commit()

# ----------------- FUNCIONES EQUIPOS ------------------
def agregar_equipo():
    nombre = entry_nombre.get()
    ciudad = entry_ciudad.get()
    dt = entry_dt.get()
    categoria = combo_categoria.get()

    if not nombre:
        messagebox.showerror("Error", "El nombre es obligatorio")
        return

    c.execute("INSERT INTO Equipos (nombre, ciudad, dt, categoria) VALUES (?, ?, ?, ?)",
              (nombre, ciudad, dt, categoria))
    conn.commit()
    messagebox.showinfo("Éxito", "Equipo agregado correctamente")
    limpiar_campos_equipo()
    mostrar_equipos()
    cargar_combo_equipos()
    cargar_combo_equipos_partido()

def limpiar_campos_equipo():
    entry_nombre.delete(0, tk.END)
    entry_ciudad.delete(0, tk.END)
    entry_dt.delete(0, tk.END)
    combo_categoria.set("")

def mostrar_equipos():
    for row in tree.get_children():
        tree.delete(row)

    c.execute("SELECT * FROM Equipos")
    for equipo in c.fetchall():
        tree.insert("", tk.END, iid=equipo[0], text=equipo[0], values=equipo[1:])

def eliminar_equipo():
    selected = tree.focus()
    if selected:
        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este equipo?")
        if confirm:
            c.execute("DELETE FROM Equipos WHERE id=?", (selected,))
            conn.commit()
            mostrar_equipos()
            cargar_combo_equipos()
            cargar_combo_equipos_partido()

# ----------------- FUNCIONES JUGADORES ------------------
def cargar_combo_equipos():
    c.execute("SELECT id, nombre FROM Equipos")
    equipos = c.fetchall()
    combo_equipos_jugador['values'] = [f"{e[0]} - {e[1]}" for e in equipos]

def agregar_jugador():
    nombre = entry_nombre_jugador.get()
    edad = entry_edad_jugador.get()
    posicion = combo_posicion_jugador.get()
    equipo = combo_equipos_jugador.get()

    if not (nombre and edad and posicion and equipo):
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return

    try:
        edad = int(edad)
    except:
        messagebox.showerror("Error", "La edad debe ser un número")
        return

    id_equipo = int(equipo.split(" - ")[0])

    c.execute("INSERT INTO Jugadores (nombre, edad, posicion, id_equipo) VALUES (?, ?, ?, ?)",
              (nombre, edad, posicion, id_equipo))
    conn.commit()
    messagebox.showinfo("Éxito", "Jugador agregado correctamente")
    limpiar_campos_jugador()
    mostrar_jugadores()

def limpiar_campos_jugador():
    entry_nombre_jugador.delete(0, tk.END)
    entry_edad_jugador.delete(0, tk.END)
    combo_posicion_jugador.set("")
    combo_equipos_jugador.set("")

def mostrar_jugadores():
    for row in tree_jugadores.get_children():
        tree_jugadores.delete(row)

    c.execute("SELECT j.id, j.nombre, j.edad, j.posicion, e.nombre FROM Jugadores j JOIN Equipos e ON j.id_equipo = e.id")
    for jugador in c.fetchall():
        tree_jugadores.insert("", tk.END, iid=jugador[0], text=jugador[0], values=jugador[1:])

# ----------------- FUNCIONES PARTIDOS ------------------
def cargar_combo_equipos_partido():
    c.execute("SELECT id, nombre FROM Equipos")
    equipos = c.fetchall()
    opciones = [f"{e[0]} - {e[1]}" for e in equipos]
    combo_local['values'] = opciones
    combo_visitante['values'] = opciones

def agregar_partido():
    local = combo_local.get()
    visitante = combo_visitante.get()
    fecha = entry_fecha.get()
    resultado = entry_resultado.get()

    if not (local and visitante and fecha and resultado):
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return

    id_local = int(local.split(" - ")[0])
    id_visitante = int(visitante.split(" - ")[0])

    if id_local == id_visitante:
        messagebox.showerror("Error", "Un equipo no puede jugar contra sí mismo")
        return

    c.execute("INSERT INTO Partidos (equipo_local, equipo_visitante, fecha, resultado) VALUES (?, ?, ?, ?)",
              (id_local, id_visitante, fecha, resultado))
    conn.commit()
    messagebox.showinfo("Éxito", "Partido agregado correctamente")
    mostrar_partidos()

def mostrar_partidos():
    for row in tree_partidos.get_children():
        tree_partidos.delete(row)

    c.execute('''SELECT p.id, e1.nombre, e2.nombre, p.fecha, p.resultado
                 FROM Partidos p
                 JOIN Equipos e1 ON p.equipo_local = e1.id
                 JOIN Equipos e2 ON p.equipo_visitante = e2.id''')
    for partido in c.fetchall():
        tree_partidos.insert("", tk.END, iid=partido[0], text=partido[0], values=partido[1:])

# ----------------- UI ------------------
root = tk.Tk()
root.title("Gestor de Torneos de Fútbol")
root.geometry("900x600")
root.config(bg="#E8F6F3")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# TAB 1: Equipos
frame_equipos = tk.Frame(notebook, bg="#E8F6F3")
notebook.add(frame_equipos, text="Equipos")

label_nombre = tk.Label(frame_equipos, text="Nombre del equipo:", font=('Arial', 12, 'bold'), bg="#E8F6F3", fg="#145A32")
label_nombre.grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_nombre = tk.Entry(frame_equipos, width=30)
entry_nombre.grid(row=0, column=1, padx=10, pady=5)

label_ciudad = tk.Label(frame_equipos, text="Ciudad:", font=('Arial', 12, 'bold'), bg="#E8F6F3", fg="#145A32")
label_ciudad.grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_ciudad = tk.Entry(frame_equipos, width=30)
entry_ciudad.grid(row=1, column=1, padx=10, pady=5)

label_dt = tk.Label(frame_equipos, text="Director Técnico:", font=('Arial', 12, 'bold'), bg="#E8F6F3", fg="#145A32")
label_dt.grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_dt = tk.Entry(frame_equipos, width=30)
entry_dt.grid(row=2, column=1, padx=10, pady=5)

label_categoria = tk.Label(frame_equipos, text="Categoría:", font=('Arial', 12, 'bold'), bg="#E8F6F3", fg="#145A32")
label_categoria.grid(row=3, column=0, padx=10, pady=5, sticky="w")
combo_categoria = ttk.Combobox(frame_equipos, values=["Libre", "+35", "+45"], state="readonly")
combo_categoria.grid(row=3, column=1, padx=10, pady=5)

btn_agregar = tk.Button(frame_equipos, text="Agregar equipo", command=agregar_equipo)
btn_agregar.config(width=20, font=('Arial', 12, 'bold'), fg='#FFFFFF', bg='#1C500B', cursor='hand2', activebackground='#3FD83F', activeforeground='#000000')
btn_agregar.grid(row=4, column=0, columnspan=2, pady=15)

tree = ttk.Treeview(frame_equipos, columns=("Nombre", "Ciudad", "DT", "Categoría"))
tree.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
tree.heading("#0", text="ID")
tree.heading("Nombre", text="Nombre")
tree.heading("Ciudad", text="Ciudad")
tree.heading("DT", text="Director Técnico")
tree.heading("Categoría", text="Categoría")

scroll = ttk.Scrollbar(frame_equipos, orient='vertical', command=tree.yview)
tree.configure(yscrollcommand=scroll.set)
scroll.grid(row=5, column=2, sticky='ns')

btn_eliminar = tk.Button(frame_equipos, text="Eliminar equipo", command=eliminar_equipo)
btn_eliminar.config(width=20, font=('Arial', 12, 'bold'), fg='#FFFFFF', bg='#A90A0A', cursor='hand2', activebackground='#F35B5B', activeforeground='#000000')
btn_eliminar.grid(row=6, column=0, columnspan=2, pady=10)

# TAB 2: Jugadores
frame_jugadores = tk.Frame(notebook, bg="#E8F6F3")
notebook.add(frame_jugadores, text="Jugadores")

label_nombre_jugador = tk.Label(frame_jugadores, text="Nombre del jugador:", font=('Arial', 12, 'bold'), bg="#E8F6F3", fg="#145A32")
label_nombre_jugador.grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_nombre_jugador = tk.Entry(frame_jugadores, width=30)
entry_nombre_jugador.grid(row=0, column=1, padx=10, pady=5)

label_edad_jugador = tk.Label(frame_jugadores, text="Edad:", font=('Arial', 12, 'bold'), bg="#E8F6F3", fg="#145A32")
label_edad_jugador.grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_edad_jugador = tk.Entry(frame_jugadores, width=30)
entry_edad_jugador.grid(row=1, column=1, padx=10, pady=5)

label_posicion_jugador = tk.Label(frame_jugadores, text="Posición:", font=('Arial', 12, 'bold'), bg="#E8F6F3", fg="#145A32")
label_posicion_jugador.grid(row=2, column=0, padx=10, pady=5, sticky="w")
combo_posicion_jugador = ttk.Combobox(frame_jugadores, values=["Arquero", "Defensor", "Mediocampista", "Delantero"], state="readonly")
combo_posicion_jugador.grid(row=2, column=1, padx=10, pady=5)

label_equipo_jugador = tk.Label(frame_jugadores, text="Equipo:", font=('Arial', 12, 'bold'), bg="#E8F6F3", fg="#145A32")
label_equipo_jugador.grid(row=3, column=0, padx=10, pady=5, sticky="w")
combo_equipos_jugador = ttk.Combobox(frame_jugadores, state="readonly")
combo_equipos_jugador.grid(row=3, column=1, padx=10, pady=5)

btn_agregar_jugador = tk.Button(frame_jugadores, text="Agregar jugador", command=agregar_jugador)
btn_agregar_jugador.config(width=20, font=('Arial', 12, 'bold'), fg='#FFFFFF', bg='#1C500B', cursor='hand2', activebackground='#3FD83F', activeforeground='#000000')
btn_agregar_jugador.grid(row=4, column=0, columnspan=2, pady=15)

tree_jugadores = ttk.Treeview(frame_jugadores, columns=("Nombre", "Edad", "Posición", "Equipo"))
tree_jugadores.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
tree_jugadores.heading("#0", text="ID")
tree_jugadores.heading("Nombre", text="Nombre")
tree_jugadores.heading("Edad", text="Edad")
tree_jugadores.heading("Posición", text="Posición")
tree_jugadores.heading("Equipo", text="Equipo")

scroll_jug = ttk.Scrollbar(frame_jugadores, orient='vertical', command=tree_jugadores.yview)
tree_jugadores.configure(yscrollcommand=scroll_jug.set)
scroll_jug.grid(row=5, column=2, sticky='ns')

# TAB 3: Partidos
frame_partidos = tk.Frame(notebook, bg="#E8F6F3")
notebook.add(frame_partidos, text="Partidos")

label_local = tk.Label(frame_partidos, text="Equipo Local:", font=('Arial', 12, 'bold'), bg="#E8F6F3", fg="#145A32")
label_local.grid(row=0, column=0, padx=10, pady=5, sticky="w")
combo_local = ttk.Combobox(frame_partidos, state="readonly")
combo_local.grid(row=0, column=1, padx=10, pady=5)

label_visitante = tk.Label(frame_partidos, text="Equipo Visitante:", font=('Arial', 12, 'bold'), bg="#E8F6F3", fg="#145A32")
label_visitante.grid(row=1, column=0, padx=10, pady=5, sticky="w")
combo_visitante = ttk.Combobox(frame_partidos, state="readonly")
combo_visitante.grid(row=1, column=1, padx=10, pady=5)

label_fecha = tk.Label(frame_partidos, text="Fecha:", font=('Arial', 12, 'bold'), bg="#E8F6F3", fg="#145A32")
label_fecha.grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_fecha = tk.Entry(frame_partidos, width=30)
entry_fecha.grid(row=2, column=1, padx=10, pady=5)

label_resultado = tk.Label(frame_partidos, text="Resultado:", font=('Arial', 12, 'bold'), bg="#E8F6F3", fg="#145A32")
label_resultado.grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_resultado = tk.Entry(frame_partidos, width=30)
entry_resultado.grid(row=3, column=1, padx=10, pady=5)

btn_agregar_partido = tk.Button(frame_partidos, text="Agregar partido", command=agregar_partido)
btn_agregar_partido.config(width=20, font=('Arial', 12, 'bold'), fg='#FFFFFF', bg='#1C500B', cursor='hand2', activebackground='#3FD83F', activeforeground='#000000')
btn_agregar_partido.grid(row=4, column=0, columnspan=2, pady=15)

tree_partidos = ttk.Treeview(frame_partidos, columns=("Local", "Visitante", "Fecha", "Resultado"))
tree_partidos.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
tree_partidos.heading("#0", text="ID")
tree_partidos.heading("Local", text="Local")
tree_partidos.heading("Visitante", text="Visitante")
tree_partidos.heading("Fecha", text="Fecha")
tree_partidos.heading("Resultado", text="Resultado")
scroll_partidos = ttk.Scrollbar(frame_partidos, orient='vertical', command=tree_partidos.yview)
tree_partidos.configure(yscrollcommand=scroll_partidos.set)
scroll_partidos.grid(row=5, column=2, sticky='ns')

# ----------------- INICIALIZAR ------------------
mostrar_equipos()
cargar_combo_equipos()
mostrar_jugadores()
cargar_combo_equipos_partido()
mostrar_partidos()

root.mainloop()