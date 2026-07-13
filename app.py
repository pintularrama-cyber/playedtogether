import os
import random
import datetime
from datetime import time
from zoneinfo import ZoneInfo
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# IMPORTAMOS LA BASE DE DATOS EXTERNA
from jugadores import JUGADORES_DB

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
    usuarios = db.relationship('User', backref='grupo', lazy=True)

class Temporada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, default=1)
    fecha_inicio = db.Column(db.Date, nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    puntos_temporada = db.Column(db.Integer, default=0)
    puntos_general = db.Column(db.Integer, default=0)
    ultimo_juego_fecha = db.Column(db.Date, nullable=True)
    partidas_jugadas = db.Column(db.Integer, default=0)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- OBTENER LISTA ÚNICA DE TODOS LOS CLUBES DEL JUEGO ---
ALL_CLUBS = list(set([club for p in JUGADORES_DB.values() for club, _, _ in p["carrera"]]))


# --- CONTROL DE TEMPORADAS AUTOMÁTICAS (20 DÍAS) ---

def actualizar_y_obtener_temporada():
    tz = ZoneInfo("Europe/Madrid")
    hoy = datetime.datetime.now(tz).date()
    
    temporada_activa = Temporada.query.order_by(Temporada.id.desc()).first()
    
    if not temporada_activa:
        temporada_activa = Temporada(numero=1, fecha_inicio=hoy)
        db.session.add(temporada_activa)
        db.session.commit()
        
    dias_transcurridos = (hoy - temporada_activa.fecha_inicio).days
    
    if dias_transcurridos >= 20:
        nueva_temporada = Temporada(
            numero=temporada_activa.numero + 1,
            fecha_inicio=hoy
        )
        db.session.add(nueva_temporada)
        
        usuarios = User.query.all()
        for usuario in usuarios:
            usuario.puntos_temporada = 0
            usuario.ultimo_juego_fecha = None
            
        db.session.commit()
        temporada_activa = nueva_temporada
        dias_transcurridos = 0
        
    dias_restantes = 20 - dias_transcurridos
    return temporada_activa.numero, dias_restantes


# --- CONTROL DE ALTERNANCIA DIARIA DE 3 DÍAS ---

def obtener_tipo_juego_hoy(fecha_juego):
    """Alterna cíclicamente: Día 0 'grid', Día 1 'ordenar', Día 2 'trayectoria'."""
    modulo = fecha_juego.toordinal() % 3
    if modulo == 0:
        return "grid"
    elif modulo == 1:
        return "ordenar"
    else:
        return "trayectoria"


# --- LÓGICA DE CONTROL DE CICLO DIARIO (11:00 AM) ---

def obtener_fecha_juego_actual():
    tz = ZoneInfo("Europe/Madrid")
    ahora = datetime.datetime.now(tz)
    
    if ahora.time() < time(11, 0):
        return (ahora - datetime.timedelta(days=1)).date()
    else:
        return ahora.date()

def compartieron_club(carrera1, carrera2):
    for club1, entrada1, salida1 in carrera1:
        for club2, entrada2, salida2 in carrera2:
            if club1 == club2:
                inicio_comun = max(entrada1, entrada2)
                fin_comun = min(salida1, salida2)
                if inicio_comun <= fin_comun:
                    return True
    return False


# --- GENERADOR JUEGO 1: CUADRÍCULA ---
def obtener_juego_del_dia(fecha_juego):
    hoy_str = fecha_juego.strftime('%Y%m%d')
    semilla = int(hoy_str)
    
    pool_jugadores = list(JUGADORES_DB.keys())
    
    intentos = 0
    while intentos < 100:
        random.seed(semilla + intentos)
        
        jugadores_disponibles = list(pool_jugadores)
        random.shuffle(jugadores_disponibles)
        
        parejas_seleccionadas = []
        jugadores_seleccionados = set()
        
        for p1 in jugadores_disponibles:
            if p1 in jugadores_seleccionados:
                continue
            
            posibles_companeros = [p for p in jugadores_disponibles if p != p1 and p not in jugadores_seleccionados]
            random.shuffle(posibles_companeros)
            
            for p2 in posibles_companeros:
                if compartieron_club(JUGADORES_DB[p1]["carrera"], JUGADORES_DB[p2]["carrera"]):
                    parejas_seleccionadas.append((p1, p2))
                    jugadores_seleccionados.add(p1)
                    jugadores_seleccionados.add(p2)
                    break
            
            if len(parejas_seleccionadas) == 8:
                break
        
        if len(parejas_seleccionadas) == 8:
            break
        intentos += 1
        
    jugadores_hoy = list(jugadores_seleccionados)
    
    conexiones_hoy = []
    for i in range(len(jugadores_hoy)):
        for j in range(i + 1, len(jugadores_hoy)):
            u1 = jugadores_hoy[i]
            u2 = jugadores_hoy[j]
            if compartieron_club(JUGADORES_DB[u1]["carrera"], JUGADORES_DB[u2]["carrera"]):
                conexiones_hoy.append((u1, u2))
                
    conexiones_hoy = list(set(conexiones_hoy))
    return jugadores_hoy, conexiones_hoy


# --- GENERADOR JUEGO 2: ORDENAR (TOP 5) ---
def obtener_juego_ordenar(fecha_juego):
    hoy_str = fecha_juego.strftime('%Y%m%d')
    semilla = int(hoy_str)
    random.seed(semilla)
    
    pool_jugadores = list(JUGADORES_DB.keys())
    jugadores_hoy = random.sample(pool_jugadores, 5)
    
    metricas = ["goles", "asistencias", "tarjetas", "partidos", "europa", "mundial", "internacional"]
    metrica_seleccionada = random.choice(metricas)
    
    titulos_metrica = {
        "goles": "Goles en su Carrera ⚽",
        "asistencias": "Asistencias de Gol 🎯",
        "tarjetas": "Tarjetas Amarillas Recibidas 🟨",
        "partidos": "Partidos Oficiales de Clubes Disputados 🏟️",
        "europa": "Partidos en Competición Europea de Clubes 🇪🇺",
        "mundial": "Partidos Disputados en la Copa del Mundo 🏆",
        "internacional": "Partidos Internacionales con su Selección 🌍"
    }
    titulo_bonito = titulos_metrica[metrica_seleccionada]
    
    solucion_ordenada = sorted(jugadores_hoy, key=lambda p: JUGADORES_DB[p][metrica_seleccionada], reverse=True)
    
    random.seed()
    jugadores_desordenados = list(jugadores_hoy)
    random.shuffle(jugadores_desordenados)
    
    return jugadores_desordenados, titulo_bonito, solucion_ordenada, metrica_seleccionada


# --- GENERADOR JUEGO 3: TRAYECTORIA ---
def obtener_juego_trayectoria(fecha_juego):
    hoy_str = fecha_juego.strftime('%Y%m%d')
    semilla = int(hoy_str)
    random.seed(semilla)
    
    pool_jugadores = list(JUGADORES_DB.keys())
    jugadores_rondas = random.sample(pool_jugadores, 3)
    
    rondas_data = []
    for index, jugador in enumerate(jugadores_rondas):
        clubes_reales = []
        for club, _, _ in JUGADORES_DB[jugador]["carrera"]:
            if club not in clubes_reales:
                clubes_reales.append(club)
        
        clubes_intrusos = [c for c in ALL_CLUBS if c not in clubes_reales]
        num_intrusos = 9 - len(clubes_reales)
        
        random.seed(semilla + index + len(clubes_reales))
        intrusos_seleccionados = random.sample(clubes_intrusos, num_intrusos)
        
        cuadricula_9 = clubes_reales + intrusos_seleccionados
        random.shuffle(cuadricula_9)
        
        rondas_data.append({
            "jugador": jugador,
            "cuadricula": cuadricula_9,
            "solucion": clubes_reales,
            "pista_num": len(clubes_reales)
        })
        
    return rondas_data


# --- RUTAS ---

@app.route('/')
@login_required
def index():
    num_temporada, dias_restantes = actualizar_y_obtener_temporada()

    if current_user.username == 'admin':
        usuarios_temporada = User.query.filter(User.username != 'admin').all()
        usuarios_general = User.query.filter(User.username != 'admin').all()
        nombre_grupo = "Administración (Ver todo)"
        bloqueado_hora = False
        ha_jugado_hoy = False
    elif current_user.grupo_id:
        usuarios_temporada = User.query.filter_by(grupo_id=current_user.grupo_id).filter(User.username != 'admin').order_by(User.puntos_temporada.desc()).all()
        usuarios_general = User.query.filter_by(grupo_id=current_user.grupo_id).filter(User.username != 'admin').order_by(User.puntos_general.desc()).all()
        
        nombre_grupo = current_user.grupo.nombre
        
        fecha_activa = obtener_fecha_juego_actual()
        ha_jugado_hoy = (current_user.ultimo_juego_fecha == fecha_activa)
        bloqueado_hora = ha_jugado_hoy
    else:
        usuarios_temporada = []
        usuarios_general = []
        nombre_grupo = "Ninguno (Sin asignar)"
        bloqueado_hora = False
        ha_jugado_hoy = False
        
    return render_template(
        'index.html', 
        usuarios_temporada=usuarios_temporada, 
        usuarios_general=usuarios_general, 
        nombre_grupo=nombre_grupo, 
        bloqueado_hora=bloqueado_hora, 
        ha_jugado_hoy=ha_jugado_hoy,
        num_temporada=num_temporada,
        dias_restantes=dias_restantes
    )


@app.route('/jugar')
@login_required
def jugar():
    if current_user.username == 'admin':
        flash("El administrador no puede participar en las partidas.", "error")
        return redirect(url_for('index'))

    fecha_activa = obtener_fecha_juego_actual()
    
    if current_user.ultimo_juego_fecha == fecha_activa:
        flash("Ya has participado en el reto activo. ¡Vuelve mañana!", "error")
        return redirect(url_for('index'))

    tipo_juego = obtener_tipo_juego_hoy(fecha_activa)

    if tipo_juego == "grid":
        jugadores_hoy, conexiones_hoy = obtener_juego_del_dia(fecha_activa)
        random.seed()
        jugadores_mezclados = list(jugadores_hoy)
        random.shuffle(jugadores_mezclados)
        return render_template('jugar.html', jugadores=jugadores_mezclados, conexiones=conexiones_hoy)
    elif tipo_juego == "ordenar":
        jugadores_desordenados, titulo_bonito, solucion_ordenada, metrica = obtener_juego_ordenar(fecha_activa)
        valores_reales = {p: JUGADORES_DB[p][metrica] for p in jugadores_desordenados}
        return render_template(
            'ordenar.html', 
            jugadores=jugadores_desordenados, 
            titulo_bonito=titulo_bonito, 
            solucion=solucion_ordenada,
            valores_reales=valores_reales
        )
    else:
        rondas_data = obtener_juego_trayectoria(fecha_activa)
        return render_template('trayectoria.html', rondas_data=rondas_data)


@app.route('/admin/test_grid')
@login_required
def test_grid():
    if current_user.username != 'admin':
        flash("Acceso denegado.", "error")
        return redirect(url_for('index'))
    
    fecha_activa = obtener_fecha_juego_actual()
    jugadores_hoy, conexiones_hoy = obtener_juego_del_dia(fecha_activa)
    random.seed()
    jugadores_mezclados = list(jugadores_hoy)
    random.shuffle(jugadores_mezclados)
    return render_template('jugar.html', jugadores=jugadores_mezclados, conexiones=conexiones_hoy)


@app.route('/admin/test_ordenar')
@login_required
def test_ordenar():
    if current_user.username != 'admin':
        flash("Acceso denegado.", "error")
        return redirect(url_for('index'))
    
    fecha_activa = obtener_fecha_juego_actual()
    jugadores_desordenados, titulo_bonito, solucion_ordenada, metrica = obtener_juego_ordenar(fecha_activa)
    valores_reales = {p: JUGADORES_DB[p][metrica] for p in jugadores_desordenados}
    return render_template(
        'ordenar.html', 
        jugadores=jugadores_desordenados, 
        titulo_bonito=titulo_bonito, 
        solucion=solucion_ordenada,
        valores_reales=valores_reales
    )


@app.route('/admin/test_trayectoria')
@login_required
def test_trayectoria():
    if current_user.username != 'admin':
        flash("Acceso denegado.", "error")
        return redirect(url_for('index'))
    
    fecha_activa = obtener_fecha_juego_actual()
    rondas_data = obtener_juego_trayectoria(fecha_activa)
    return render_template('trayectoria.html', rondas_data=rondas_data)


@app.route('/guardar_puntuacion', methods=['POST'])
@login_required
def guardar_puntuacion():
    if current_user.username == 'admin':
        return jsonify({"status": "ok", "message": "Simulacion de test completada"}), 200

    fecha_activa = obtener_fecha_juego_actual()
    
    if current_user.ultimo_juego_fecha == fecha_activa:
        return jsonify({"status": "error", "message": "Ya has jugado este reto"}), 400

    datos = request.get_json()
    segundos = datos.get('segundos', 9999)
    completado = datos.get('completado', False)
    puntos_enviados = datos.get('puntos')

    if completado:
        if puntos_enviados is not None:
            puntos_obtenidos = puntos_enviados
        else:
            puntos_obtenidos = max(100, 1000 - segundos) 
            
        current_user.puntos_temporada += puntos_obtenidos
        current_user.puntos_general += puntos_obtenidos
        current_user.ultimo_juego_fecha = fecha_activa
        current_user.partidas_jugadas += 1
        db.session.commit()
        
        flash(f"¡Reto completado! Sumas {puntos_obtenidos} puntos.", "success")
        return jsonify({"status": "ok"})
    
    return jsonify({"status": "error", "message": "Datos inválidos"}), 400


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


@app.route('/reset_clasificacion', methods=['POST'])
@login_required
def reset_clasificacion():
    if current_user.username != 'admin':
        flash("No tienes permisos de administrador.", "error")
        return redirect(url_for('index'))
    
    usuarios = User.query.all()
    for usuario in usuarios:
        usuario.puntos_temporada = 0
        usuario.ultimo_juego_fecha = None
        usuario.partidas_jugadas = 0
    
    temporada_activa = Temporada.query.order_by(Temporada.id.desc()).first()
    if temporada_activa:
        tz = ZoneInfo("Europe/Madrid")
        temporada_activa.fecha_inicio = datetime.datetime.now(tz).date()
        
    db.session.commit()
    flash("La clasificación de la temporada actual ha sido reiniciada.", "success")
    return redirect(url_for('index'))


@app.route('/borrar_usuario/<int:user_id>', methods=['POST'])
@login_required
def borrar_usuario(user_id):
    if current_user.username != 'admin':
        flash("No tienes permisos de administrador.", "error")
        return redirect(url_for('index'))
    
    usuario = User.query.get(user_id)
    if usuario:
        if usuario.username == 'admin':
            flash("No puedes eliminar la cuenta de administrador.", "error")
            return redirect(url_for('index'))
        
        nombre_eliminado = usuario.username
        db.session.delete(usuario)
        db.session.commit()
        flash(f"El usuario '{nombre_eliminado}' ha sido eliminado con éxito.", "success")
    else:
        flash("Usuario no encontrado.", "error")
        
    return redirect(url_for('index'))


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


@app.route('/registro', methods=['GET', 'POST'])
def registro():
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
    current_user.ultimo_juego_fecha = None
    db.session.commit()
    flash("Se ha reiniciado tu estado para pruebas.", "success")
    return redirect(url_for('index'))


with app.app_context():
    db.create_all()
    
    rotonda_existe = Grupo.query.filter_by(nombre='Rotonda').first()
    if not rotonda_existe:
        rotonda_inicial = Grupo(nombre='Rotonda')
        db.session.add(rotonda_inicial)
        db.session.commit()
    
    admin_existe = User.query.filter_by(username='admin').first()
    if not admin_existe:
        pass_encriptada = generate_password_hash('admin')
        nuevo_admin = User(username='admin', password_hash=pass_encriptada)
        db.session.add(nuevo_admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)