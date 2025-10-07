# inventory_cli.py
from app import app, db, Product

def add_product(name, quantity, price):
    with app.app_context():
        p = Product(name=name, quantity=quantity, price=price)
        db.session.add(p)
        db.session.commit()
        return p.id

def delete_product(pid):
    with app.app_context():
        p = Product.query.get(pid)
        if p:
            db.session.delete(p)
            db.session.commit()
            return True
        return False

def update_product(pid, **fields):
    with app.app_context():
        p = Product.query.get(pid)
        if p:
            for key, value in fields.items():
                setattr(p, key, value)
            db.session.commit()
            return True
        return False

def search_products(name):
    with app.app_context():
        products = Product.query.filter(Product.name.like(f'%{name}%')).all()
        return products

def get_all_products():
    with app.app_context():
        products = Product.query.all()
        return products

def main_menu():
    while True:
        print("\n--- Inventario (SQLAlchemy) ---")
        print("1) Añadir producto")
        print("2) Eliminar por ID")
        print("3) Actualizar por ID")
        print("4) Buscar por nombre")
        print("5) Mostrar todos")
        print("0) Salir")
        opt = input("Elige opción: ").strip()
        if opt == '1':
            n = input("Nombre: ")
            q = int(input("Cantidad: "))
            p = float(input("Precio: "))
            pid = add_product(n, q, p)
            print("Añadido id:", pid)
        elif opt == '2':
            pid = int(input("ID a eliminar: "))
            if delete_product(pid):
                print("Eliminado")
            else:
                print("Producto no encontrado")
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
                if update_product(pid, **campos):
                    print("Actualizado")
                else:
                    print("Producto no encontrado")
            else:
                print("Nada para actualizar")
        elif opt == '4':
            res = search_products(input("Nombre a buscar: "))
            for r in res:
                print(f"ID: {r.id}, Nombre: {r.name}, Cantidad: {r.quantity}, Precio: {r.price}")
        elif opt == '5':
            for r in get_all_products():
                print(f"ID: {r.id}, Nombre: {r.name}, Cantidad: {r.quantity}, Precio: {r.price}")
        elif opt == '0':
            break
        else:
            print("Opción no válida")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    main_menu()