# inventory_cli.py
import sqlite3
from dataclasses import dataclass

DB = 'database/inventario.db'

@dataclass
class Product:
    id: int = None
    name: str = ''
    quantity: int = 0
    price: float = 0.0

class Inventory:
    def __init__(self, db_path=DB):
        self.db_path = db_path
        self._ensure_table()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _ensure_table(self):
        with self._conn() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER DEFAULT 0,
                price REAL DEFAULT 0.0
            )''')

    def add(self, name, quantity, price):
        with self._conn() as conn:
            cur = conn.execute("INSERT INTO products (name, quantity, price) VALUES (?,?,?)",
                               (name, quantity, price))
            conn.commit()
            return cur.lastrowid

    def delete(self, pid):
        with self._conn() as conn:
            conn.execute("DELETE FROM products WHERE id=?", (pid,))
            conn.commit()

    def update(self, pid, **fields):
        parts = ", ".join(f"{k}=?" for k in fields.keys())
        params = list(fields.values()) + [pid]
        with self._conn() as conn:
            conn.execute(f"UPDATE products SET {parts} WHERE id=?", params)
            conn.commit()

    def search(self, name):
        with self._conn() as conn:
            cur = conn.execute("SELECT id, name, quantity, price FROM products WHERE name LIKE ?", (f'%{name}%',))
            return cur.fetchall()

    def all(self):
        with self._conn() as conn:
            cur = conn.execute("SELECT id, name, quantity, price FROM products")
            return cur.fetchall()

def main_menu():
    inv = Inventory()
    while True:
        print("\n--- Inventario ---")
        print("1) Añadir producto")
        print("2) Eliminar por ID")
        print("3) Actualizar por ID")
        print("4) Buscar por nombre")
        print("5) Mostrar todos")
        print("0) Salir")
        opt = input("Elige opción: ").strip()
        if opt == '1':
            n = input("Nombre: "); q = int(input("Cantidad: ")); p = float(input("Precio: "))
            pid = inv.add(n,q,p); print("Añadido id:", pid)
        elif opt == '2':
            inv.delete(int(input("ID a eliminar: "))); print("Eliminado")
        elif opt == '3':
            pid = int(input("ID a actualizar: "))
            campos = {}
            name = input("Nuevo nombre (enter=omitir): ").strip()
            if name: campos['name'] = name
            q = input("Nueva cantidad (enter=omitir): ").strip()
            if q: campos['quantity'] = int(q)
            pr = input("Nuevo precio (enter=omitir): ").strip()
            if pr: campos['price'] = float(pr)
            if campos:
                inv.update(pid, **campos)
                print("Actualizado")
            else:
                print("Nada para actualizar")
        elif opt == '4':
            res = inv.search(input("Nombre a buscar: "))
            for r in res: print(r)
        elif opt == '5':
            for r in inv.all(): print(r)
        elif opt == '0':
            break
        else:
            print("Opción no válida")

if __name__ == '__main__':
    main_menu()
