# app.py
import os
import csv
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:000000@localhost/dbsolidarias'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    donations = db.relationship('Donation', backref='donor', lazy=True)

class Category(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    donations = db.relationship('Donation', backref='category', lazy=True)

class Status(db.Model):
    __tablename__ = 'estados'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    donations = db.relationship('Donation', backref='status', lazy=True)

class Donation(db.Model):
    __tablename__ = 'donaciones'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    value = db.Column(db.Float, default=0.0)
    category_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('estados.id'), nullable=False)

class Product(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'description': self.description, 'quantity': self.quantity, 'value': self.value, 'status': self.status.name}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/donations')
def donations():
    donations = Donation.query.all()
    return render_template('donations.html', donations=donations)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/add', methods=['GET', 'POST'])
def add_donation():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para agregar una donación', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        description = request.form['description']
        quantity = int(request.form['quantity'])
        value = float(request.form['price'])
        category_id = int(request.form['category_id'])
        user_id = session['user_id']
        status = Status.query.filter_by(name='Recibido').first()
        donation = Donation(description=description, quantity=quantity, value=value, category_id=category_id, user_id=user_id, status_id=status.id)
        db.session.add(donation)
        db.session.commit()
        flash('Donación agregada con éxito', 'success')
        return redirect(url_for('index'))
    categories = Category.query.all()
    return render_template('formulario.html', categories=categories)

@app.route('/delete/<int:donation_id>', methods=['POST'])
def delete_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    if 'user_id' not in session or donation.user_id != session['user_id']:
        flash('No tienes permiso para eliminar esta donación.', 'danger')
        return redirect(url_for('donations'))
    db.session.delete(donation)
    db.session.commit()
    flash('Donación eliminada con éxito', 'success')
    return redirect(url_for('donations'))

@app.route('/update/<int:donation_id>', methods=['GET', 'POST'])
def update_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    if 'user_id' not in session or donation.user_id != session['user_id']:
        flash('No tienes permiso para editar esta donación.', 'danger')
        return redirect(url_for('donations'))
    if request.method == 'POST':
        donation.description = request.form['description']
        donation.quantity = int(request.form['quantity'])
        donation.value = float(request.form['price'])
        donation.category_id = int(request.form['category_id'])
        db.session.commit()
        flash('Donación actualizada con éxito', 'success')
        return redirect(url_for('donations'))
    categories = Category.query.all()
    return render_template('formulario.html', donation=donation, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('El nombre de usuario ya existe.', 'danger')
            return redirect(url_for('register'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('El correo electrónico ya está en uso.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(username=username, password=hashed_password, email=email)
        db.session.add(user)
        db.session.commit()
        flash('Usuario creado con éxito', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Has iniciado sesión con éxito', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Add some initial categories if they don't exist
        if not Category.query.first():
            db.session.add(Category(name='Ropa'))
            db.session.add(Category(name='Alimentos'))
            db.session.add(Category(name='Dinero'))
            db.session.commit()
        if not Status.query.first():
            db.session.add(Status(name='Recibido'))
            db.session.add(Status(name='En proceso'))
            db.session.add(Status(name='Entregado'))
            db.session.commit()
    app.run(debug=True)