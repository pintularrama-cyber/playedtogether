import os
import random
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta_super_segura'

if os.path.exists('/data'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/playedtogether.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///playedtogether.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# --- MODELOS DE LA BASE DE DATOS ---

class Grupo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    # Relación uno a muchos: Un grupo tiene muchos usuarios
    usuarios = db.relationship('User', backref='grupo', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    puntos_temporada = db.Column(db.Integer, default=0)
    jugado_hoy = db.Column(db.Boolean, default=False)
    # Relación: Grupo al que pertenece el usuario (puede ser Null para el admin)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- DATOS DEL JUEGO ---
JUGADORES_HOY = [
    "Messi", "C. Ronaldo", "Benzema", "Modric", "Kroos", 
    "Sergio Ramos", "Casemiro", "Varane", "Marcelo", "Di María",
    "Mbappé", "Neymar", "Thiago Silva", "Marquinhos", "Ibrahimovic", 
    "Cavani"
]

CONEXIONES_REALES = [
    ("C. Ronaldo", "Benzema"), ("C. Ronaldo", "Modric"), ("C. Ronaldo", "Kroos"), 
    ("C. Ronaldo", "Sergio Ramos"), ("C. Ronaldo", "Casemiro"), ("C. Ronaldo", "Varane"), 
    ("C. Ronaldo", "Marcelo"), ("C. Ronaldo", "Di María"),
    ("Benzema", "Modric"), ("Benzema", "Kroos"), ("Benzema", "Sergio Ramos"), 
    ("Benzema", "Casemiro"), ("Benzema", "Varane"), ("Benzema", "Marcelo"), 
    ("Benzema", "Di María"), ("Benzema", "Mbappé"),
    ("Modric", "Kroos"), ("Modric", "Sergio Ramos"), ("Modric", "Casemiro"), 
    ("Modric", "Varane"), ("Modric", "Marcelo"), ("Modric", "Di María"),
    ("Kroos", "Sergio Ramos"), ("Kroos", "Casemiro"), ("Kroos", "Varane"), 
    ("Kroos", "Marcelo"), ("Kroos", "Di María"),
    ("Sergio Ramos", "Casemiro"), ("Sergio Ramos", "Varane"), ("Sergio Ramos", "Marcelo"), 
    ("Sergio Ramos", "Di María"), ("Sergio Ramos", "Messi"), ("Sergio Ramos", "Neymar"), 
    ("Sergio Ramos", "Mbappé"), ("Sergio Ramos", "Marquinhos"),
    ("Casemiro", "Varane"), ("Casemiro", "Marcelo"), ("Casemiro", "Di María"),
    ("Varane", "Marcelo"), ("Varane", "Di María"), ("Varane", "Mbappé"), 
    ("Marcelo", "Di María"),
    ("Messi", "Neymar"), ("Messi", "Mbappé"), ("Messi", "Di María"), ("Messi", "Ibrahimovic"),
    ("Neymar", "Mbappé"), ("Neymar", "Di María"), ("Neymar", "Marquinhos"), 
    ("Neymar", "Thiago Silva"), ("Neymar", "Cavani"), ("Neymar", "Ibrahimovic"),
    ("Mbappé", "Di María"), ("Mbappé", "Marquinhos"), ("Mbappé", "Thiago Silva"), 
    ("Mbappé", "Cavani"),
    ("Di María", "Marquinhos"), ("Di María", "Thiago Silva"), ("Di María", "Cavani"), 
    ("Di María", "Ibrahimovic"),
    ("Marquinhos", "Thiago Silva"), ("Marquinhos", "Cavani"),
    ("Thiago Silva", "Cavani"), ("Thiago Silva", "Ibrahimovic"),
    ("Ibrahimovic", "Cavani")
]


# --- RUTAS ---

@app.route('/')
@login_required
def index():
    # Si el usuario logueado tiene un grupo asignado, filtramos por su grupo
    if current_user.grupo_id:
        usuarios = User.query.filter_by(grupo_id=current_user.grupo_id).filter(User.username != 'admin').order_by(User.puntos_temporada.desc()).all()
        nombre_grupo = current_user.grupo.nombre
    else:
        # Si es el admin (que no tiene grupo), de momento mostramos una lista vacía o general
        usuarios = []
        nombre_grupo = "Administración (Sin grupo)"
        
    return render_template('index.html', usuarios=usuarios, nombre_grupo=nombre_grupo)


@app.route('/jugar')
@login_required
def jugar():
    if current_user.jugado_hoy:
        flash("Ya has participado en el reto de hoy. ¡Vuelve mañana!", "error")
        return redirect(url_for('index'))

    jugadores_mezclados = list(JUGADORES_HOY)
    random.seed(42)
    random.shuffle(jugadores_mezclados)

    return render_template('jugar.html', jugadores=jugadores_mezclados, conexiones=CONEXIONES_REALES)


@app.route('/guardar_puntuacion', methods=['POST'])
@login_required
def guardar_puntuacion():
    if current_user.jugado_hoy:
        return jsonify({"status": "error", "message": "Ya has jugado hoy"}), 400

    datos = request.get_json()
    segundos = datos.get('segundos', 9999)
    completado = datos.get('completado', False)

    if completado:
        puntos_obtenidos = max(100, 1000 - segundos) 
        current_user.puntos_temporada += puntos_obtenidos
        current_user.jugado_hoy = True
        db.session.commit()
        
        flash(f"¡Reto completado en {segundos} segundos! Sumas {puntos_obtenidos} puntos.", "success")
        return jsonify({"status": "ok"})
    
    return jsonify({"status": "error", "message": "Datos inválidos"}), 400


# --- ADMIN: CREAR NUEVOS GRUPOS ---
@app.route('/crear_grupo', methods=['POST'])
@login_required
def crear_grupo():
    if current_user.username != 'admin':
        flash("No tienes permisos de administrador.", "error")
        return redirect(url_for('index'))
    
    nombre_nuevo = request.form.get('nombre_grupo').strip()
    if nombre_nuevo:
        existe = Grupo.query.filter_by(nombre=nombre_nuevo).first()
        if existe:
            flash("Ese grupo ya existe.", "error")
        else:
            nuevo_grupo = Grupo(nombre=nombre_nuevo)
            db.session.add(nuevo_grupo)
            db.session.commit()
            flash(f"Grupo '{nombre_nuevo}' creado correctamente.", "success")
            
    return redirect(url_for('index'))


# --- ADMIN: RESETEAR CLASIFICACIÓN DEL GRUPO ACTUAL ---
@app.route('/reset_clasificacion', methods=['POST'])
@login_required
def reset_clasificacion():
    if current_user.username != 'admin':
        flash("No tienes permisos de administrador.", "error")
        return redirect(url_for('index'))
    
    # El administrador resetea todos los usuarios de la base de datos
    usuarios = User.query.all()
    for usuario in usuarios:
        usuario.puntos_temporada = 0
        usuario.jugado_hoy = False
        
    db.session.commit()
    flash("La clasificación general ha sido reiniciada a 0.", "success")
    return redirect(url_for('index'))


# --- INICIO DE SESIÓN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')


# --- REGISTRO DE USUARIOS CON GRUPO ---
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    # Obtenemos todos los grupos disponibles para mostrarlos en el desplegable
    grupos_disponibles = Grupo.query.all()

    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        grupo_id = request.form.get('grupo_id')
        
        if username.lower() == 'admin':
            flash('No puedes registrar un usuario con ese nombre.', 'error')
            return redirect(url_for('registro'))

        total_usuarios = User.query.count()
        if total_usuarios >= 20:
            flash('El grupo ya está lleno (máximo 20).', 'error')
            return redirect(url_for('registro'))
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Este usuario ya existe.', 'error')
            return redirect(url_for('registro'))
        
        nuevo_usuario = User(
            username=username, 
            password_hash=generate_password_hash(password),
            grupo_id=grupo_id
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Registro completado con éxito.', 'success')
        return redirect(url_for('login'))
        
    return render_template('registro.html', grupos=grupos_disponibles)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/reset_hoy')
@login_required
def reset_hoy():
    current_user.jugado_hoy = False
    db.session.commit()
    flash("Se ha reiniciado tu estado para pruebas.", "success")
    return redirect(url_for('index'))


# --- INICIALIZACIÓN DE TABLAS, ADMIN Y GRUPO "ROTONDA" ---
with app.app_context():
    db.create_all()
    
    # 1. Crear el grupo "Rotonda" automáticamente si no existe
    rotonda_existe = Grupo.query.filter_by(nombre='Rotonda').first()
    if not rotonda_existe:
        rotonda_inicial = Grupo(nombre='Rotonda')
        db.session.add(rotonda_inicial)
        db.session.commit()
    
    # 2. Crear el administrador por defecto si no existe
    admin_existe = User.query.filter_by(username='admin').first()
    if not admin_existe:
        pass_encriptada = generate_password_hash('admin')
        nuevo_admin = User(username='admin', password_hash=pass_encriptada)
        db.session.add(nuevo_admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)