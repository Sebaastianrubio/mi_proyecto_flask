# app.py
import os          # Para manejar rutas de archivos y directorios
import csv         # Para guardar/exportar datos en formato CSV
import json        # Para guardar/exportar datos en formato JSON
from flask import Flask, render_template, request, redirect, url_for, jsonify  
# Flask: framework web
# render_template: para mostrar HTML
# request: para capturar datos de formularios
# redirect, url_for: para redireccionar páginas
# jsonify: para devolver datos en formato JSON

from flask_sqlalchemy import SQLAlchemy  
# SQLAlchemy: ORM que permite manejar la base de datos como objetos Python

# Definir la ruta base del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Crear instancia de Flask
app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'inventario.db')
# URI completa de la base de datos SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Evita mensajes de advertencia sobre cambios en objetos de SQLAlchemy

# Crear objeto SQLAlchemy
db = SQLAlchemy(app)

# ========================
# Definición del modelo Product (tabla productos)
# ========================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID autoincremental
    name = db.Column(db.String(120), nullable=False)  # Nombre del producto, obligatorio
    quantity = db.Column(db.Integer, default=0)  # Cantidad en inventario
    price = db.Column(db.Float, default=0.0)     # Precio del producto

    # Método para convertir objeto a diccionario (útil para JSON)
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'quantity': self.quantity, 'price': self.price}

# ========================
# Rutas de la aplicación
# ========================

# Página principal que muestra todos los productos
@app.route('/')
def index():
    products = Product.query.all()  # Consulta todos los productos
    return render_template('index.html', products=products)  # Renderiza plantilla HTML

# Página "about"
@app.route('/about')
def about():
    return render_template('about.html')

# Agregar un nuevo producto
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':  # Si se envió el formulario
        name = request.form['name']  # Captura el nombre
        quantity = int(request.form['quantity'])  # Captura la cantidad
        price = float(request.form['price'])      # Captura el precio
        p = Product(name=name, quantity=quantity, price=price)  # Crea objeto Product
        db.session.add(p)   # Agrega a la sesión
        db.session.commit() # Guarda cambios en la base de datos
        return redirect(url_for('index'))  # Redirige a la página principal
    return render_template('formulario.html')  # Si GET, muestra formulario

# Eliminar un producto
@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)  # Busca producto por ID o 404
    db.session.delete(p)   # Elimina de la base de datos
    db.session.commit()    # Guarda cambios
    return redirect(url_for('index'))

# Actualizar producto
@app.route('/update/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    p = Product.query.get_or_404(product_id)  # Busca producto
    if request.method == 'POST':
        # Actualiza campos con los datos del formulario
        p.name = request.form['name']
        p.quantity = int(request.form['quantity'])
        p.price = float(request.form['price'])
        db.session.commit()  # Guarda cambios
        return redirect(url_for('index'))
    return render_template('formulario.html', product=p)  # Renderiza formulario con datos

# ========================
# Guardar productos en archivos
# ========================

# Guardar en TXT
@app.route('/save/txt')
def save_txt():
    products = Product.query.all()
    path = os.path.join(BASE_DIR, 'datos', 'datos.txt')  # Ruta del archivo
    os.makedirs(os.path.dirname(path), exist_ok=True)     # Crear carpeta si no existe
    with open(path, 'w', encoding='utf-8') as f:
        for p in products:
            f.write(f"{p.id}\t{p.name}\t{p.quantity}\t{p.price}\n")
    return f"Guardado {len(products)} productos en datos/datos.txt"

# Guardar en JSON
@app.route('/save/json')
def save_json():
    products = [p.to_dict() for p in Product.query.all()]
    path = os.path.join(BASE_DIR, 'datos', 'datos.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    return jsonify(products)  # Devuelve JSON en navegador o API

# Guardar en CSV
@app.route('/save/csv')
def save_csv():
    products = Product.query.all()
    path = os.path.join(BASE_DIR, 'datos', 'datos.csv')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id','name','quantity','price'])  # Encabezado
        for p in products:
            writer.writerow([p.id, p.name, p.quantity, p.price])
    return f"Guardado en datos/datos.csv"

# ========================
# API para productos (JSON)
# ========================
@app.route('/api/products')
def api_products():
    return jsonify([p.to_dict() for p in Product.query.all()])

# ========================
# Inicialización de la app
# ========================
if __name__ == '__main__':
    # Crear carpeta database si no existe
    os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    # Ejecutar servidor Flask en modo debug
    app.run(debug=True)