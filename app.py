import os
import random
import datetime
from datetime import time  # <-- NUEVA IMPORTACIÓN
from zoneinfo import ZoneInfo  # <-- NUEVA IMPORTACIÓN
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

def es_antes_de_las_11():
    # Usamos la zona horaria de España para que funcione igual en el servidor de Render
    tz = ZoneInfo("Europe/Madrid")
    ahora = datetime.datetime.now(tz)
    # Retorna True si la hora actual es menor que las 11:00:00
    return ahora.time() < time(11, 0)

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

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    puntos_temporada = db.Column(db.Integer, default=0)
    jugado_hoy = db.Column(db.Boolean, default=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- BASE DE DATOS AUTOMÁTICA DE TRAYECTORIAS (64 JUGADORES) ---

JUGADORES_DB = {
    # Real Madrid / Barcelona / PSG Core
    "Messi": [("Barcelona", 2004, 2021), ("PSG", 2021, 2023), ("Inter Miami", 2023, 2026)],
    "C. Ronaldo": [("Manchester United", 2003, 2009), ("Real Madrid", 2009, 2018), ("Juventus", 2018, 2021), ("Manchester United", 2021, 2022)],
    "Benzema": [("Lyon", 2004, 2009), ("Real Madrid", 2009, 2023)],
    "Neymar": [("Barcelona", 2013, 2017), ("PSG", 2017, 2023)],
    "Mbappé": [("Monaco", 2015, 2017), ("PSG", 2017, 2024), ("Real Madrid", 2024, 2026)],
    "Sergio Ramos": [("Sevilla", 2003, 2005), ("Real Madrid", 2005, 2021), ("PSG", 2021, 2023), ("Sevilla", 2023, 2024)],
    "Modric": [("Tottenham", 2008, 2012), ("Real Madrid", 2012, 2026)],
    "Kroos": [("Bayern", 2007, 2014), ("Bayer Leverkusen", 2009, 2010), ("Real Madrid", 2014, 2024)],
    "Casemiro": [("Real Madrid", 2013, 2022), ("Porto", 2014, 2015), ("Manchester United", 2022, 2026)],
    "Varane": [("Real Madrid", 2011, 2021), ("Manchester United", 2021, 2024)],
    "Marcelo": [("Real Madrid", 2007, 2022), ("Olympiacos", 2022, 2023), ("Fluminense", 2023, 2025)],
    "Di María": [("Benfica", 2007, 2010), ("Real Madrid", 2010, 2014), ("Manchester United", 2014, 2015), ("PSG", 2015, 2022), ("Juventus", 2022, 2023), ("Benfica", 2023, 2025)],
    "Ibrahimovic": [("Ajax", 2001, 2004), ("Juventus", 2004, 2006), ("Inter", 2006, 2009), ("Barcelona", 2009, 2010), ("Milan", 2010, 2012), ("PSG", 2012, 2016), ("Manchester United", 2016, 2018), ("Milan", 2020, 2023)],
    "Cavani": [("Palermo", 2007, 2010), ("Napoli", 2010, 2013), ("PSG", 2013, 2020), ("Manchester United", 2020, 2022), ("Valencia", 2022, 2023)],
    "Thiago Silva": [("Milan", 2009, 2012), ("PSG", 2012, 2020), ("Chelsea", 2020, 2024)],
    "Marquinhos": [("Roma", 2012, 2013), ("PSG", 2013, 2026)],
    
    # Premier League / Barcelona / Bayern / Otros
    "Suárez": [("Ajax", 2007, 2011), ("Liverpool", 2011, 2014), ("Barcelona", 2014, 2020), ("Atletico", 2020, 2022), ("Inter Miami", 2024, 2026)],
    "Iniesta": [("Barcelona", 2002, 2018)],
    "Xavi": [("Barcelona", 1998, 2015)],
    "Busquets": [("Barcelona", 2008, 2023), ("Inter Miami", 2023, 2026)],
    "Jordi Alba": [("Valencia", 2009, 2012), ("Barcelona", 2012, 2023), ("Inter Miami", 2023, 2026)],
    "Piqué": [("Manchester United", 2004, 2008), ("Zaragoza", 2006, 2007), ("Barcelona", 2008, 2022)],
    "Puyol": [("Barcelona", 1999, 2014)],
    "Dani Alves": [("Sevilla", 2002, 2008), ("Barcelona", 2008, 2016), ("Juventus", 2016, 2017), ("PSG", 2017, 2019), ("Barcelona", 2021, 2022)],
    "Mascherano": [("West Ham", 2006, 2007), ("Liverpool", 2007, 2010), ("Barcelona", 2010, 2018)],
    "De Bruyne": [("Chelsea", 2012, 2014), ("Wolfsburg", 2014, 2015), ("Manchester City", 2015, 2026)],
    "Haaland": [("Salzburg", 2019, 2020), ("Dortmund", 2020, 2022), ("Manchester City", 2022, 2026)],
    "David Silva": [("Valencia", 2004, 2010), ("Manchester City", 2010, 2020), ("Real Sociedad", 2020, 2023)],
    "Agüero": [("Atletico", 2006, 2011), ("Manchester City", 2010, 2021), ("Barcelona", 2021, 2021)],
    "Yaya Touré": [("Monaco", 2006, 2007), ("Barcelona", 2007, 2010), ("Manchester City", 2010, 2018)],
    "Tévez": [("West Ham", 2006, 2007), ("Manchester United", 2007, 2009), ("Manchester City", 2009, 2013), ("Juventus", 2013, 2015)],
    "Rooney": [("Everton", 2002, 2004), ("Manchester United", 2004, 2017), ("Everton", 2017, 2018)],
    "Pogba": [("Manchester United", 2011, 2012), ("Juventus", 2012, 2016), ("Manchester United", 2016, 2022), ("Juventus", 2022, 2024)],
    "Rashford": [("Manchester United", 2015, 2026)],
    "De Gea": [("Atletico", 2009, 2011), ("Manchester United", 2011, 2023), ("Fiorentina", 2024, 2026)],
    "Lewandowski": [("Dortmund", 2010, 2014), ("Bayern", 2014, 2022), ("Barcelona", 2022, 2026)],
    "Müller": [("Bayern", 2008, 2026)],
    "Robben": [("Chelsea", 2004, 2007), ("Real Madrid", 2007, 2009), ("Bayern", 2009, 2019)],
    "Ribéry": [("Marseille", 2005, 2007), ("Bayern", 2007, 2019), ("Fiorentina", 2019, 2021)],
    "Alaba": [("Bayern", 2010, 2021), ("Hoffenheim", 2011, 2011), ("Real Madrid", 2021, 2026)],
    "Lahm": [("Bayern", 2001, 2017), ("Stuttgart", 2003, 2005)],
    "Schweinsteiger": [("Bayern", 2002, 2015), ("Manchester United", 2015, 2017)],
    "Thiago": [("Barcelona", 2009, 2013), ("Bayern", 2013, 2020), ("Liverpool", 2020, 2024)],
    "Hazard": [("Lille", 2007, 2012), ("Chelsea", 2012, 2019), ("Real Madrid", 2019, 2023)],
    "Lampard": [("Chelsea", 2001, 2014), ("Manchester City", 2014, 2015)],
    "Terry": [("Chelsea", 1998, 2017)],
    "Drogba": [("Marseille", 2003, 2004), ("Chelsea", 2004, 2012), ("Galatasaray", 2013, 2014), ("Chelsea", 2014, 2015)],
    "Čech": [("Rennes", 2002, 2004), ("Chelsea", 2004, 2015), ("Arsenal", 2015, 2019)],
    "Fàbregas": [("Arsenal", 2003, 2011), ("Barcelona", 2011, 2014), ("Chelsea", 2014, 2019), ("Monaco", 2019, 2022)],
    "Henry": [("Monaco", 1994, 1999), ("Juventus", 1999, 1999), ("Arsenal", 1999, 2007), ("Barcelona", 2007, 2010)],
    "Ronaldinho": [("PSG", 2001, 2003), ("Barcelona", 2003, 2008), ("Milan", 2008, 2011)],
    "Eto'o": [("Real Madrid", 1997, 2000), ("Mallorca", 2000, 2004), ("Barcelona", 2004, 2009), ("Inter", 2009, 2011), ("Chelsea", 2013, 2014), ("Everton", 2014, 2015)],

    # --- NUEVOS: ATLÉTICO DE MADRID ---
    "Griezmann": [("Real Sociedad", 2009, 2014), ("Atletico", 2014, 2019), ("Barcelona", 2019, 2021), ("Atletico", 2021, 2026)],
    "Falcao": [("Porto", 2009, 2011), ("Atletico", 2011, 2013), ("Monaco", 2013, 2019), ("Manchester United", 2014, 2015), ("Chelsea", 2015, 2016)],
    "Godín": [("Villarreal", 2007, 2010), ("Atletico", 2010, 2019), ("Inter", 2019, 2020)],
    "Oblak": [("Benfica", 2010, 2014), ("Atletico", 2014, 2026)],
    "Diego Costa": [("Atletico", 2010, 2014), ("Chelsea", 2014, 2017), ("Atletico", 2018, 2020)],

    # --- NUEVOS: REAL BETIS ---
    "Joaquín": [("Real Betis", 2000, 2006), ("Valencia", 2006, 2011), ("Malaga", 2011, 2013), ("Fiorentina", 2013, 2015), ("Real Betis", 2015, 2023)],
    "Fekir": [("Lyon", 2013, 2019), ("Real Betis", 2019, 2024)],
    "Canales": [("Real Madrid", 2010, 2012), ("Valencia", 2011, 2014), ("Real Sociedad", 2014, 2018), ("Real Betis", 2018, 2023)],
    "Isco": [("Valencia", 2010, 2011), ("Malaga", 2011, 2013), ("Real Madrid", 2013, 2022), ("Sevilla", 2022, 2022), ("Real Betis", 2023, 2026)],
    "Bellerín": [("Arsenal", 2013, 2022), ("Real Betis", 2021, 2022), ("Barcelona", 2022, 2023), ("Real Betis", 2023, 2026)],

    # --- NUEVOS: SEVILLA FC ---
    "Jesús Navas": [("Sevilla", 2003, 2013), ("Manchester City", 2013, 2017), ("Sevilla", 2017, 2026)],
    "Rakitic": [("Schalke", 2007, 2011), ("Sevilla", 2011, 2014), ("Barcelona", 2014, 2020), ("Sevilla", 2020, 2024)],
    "Banega": [("Valencia", 2008, 2014), ("Atletico", 2008, 2009), ("Sevilla", 2014, 2016), ("Inter", 2016, 2017), ("Sevilla", 2017, 2020)],
    "Luuk de Jong": [("Monchengladbach", 2012, 2014), ("PSV", 2014, 2019), ("Sevilla", 2019, 2022), ("Barcelona", 2021, 2022), ("PSV", 2022, 2026)]
}


# --- ALGORITMO DE COINCIDENCIA AUTOMÁTICA EN CLUBES ---

def compartieron_club(carrera1, carrera2):
    for club1, entrada1, salida1 in carrera1:
        for club2, entrada2, salida2 in carrera2:
            if club1 == club2:
                # Comprobar solapamiento de años en el mismo club
                inicio_comun = max(entrada1, entrada2)
                fin_comun = min(salida1, salida2)
                if inicio_comun <= fin_comun:
                    return True
    return False

def obtener_juego_del_dia():
    # Usamos la fecha de hoy como semilla para asegurar un juego único por día
    hoy_str = datetime.date.today().strftime('%Y%m%d')
    semilla = int(hoy_str)
    
    # Seleccionamos 16 jugadores de forma aleatoria y estable para el día de hoy
    pool_jugadores = list(JUGADORES_DB.keys())
    random.seed(semilla)
    jugadores_hoy = random.sample(pool_jugadores, 16)
    
    # Calculamos de forma matemática todas las conexiones posibles para esos 16
    conexiones_hoy = []
    for i in range(len(jugadores_hoy)):
        for j in range(i + 1, len(jugadores_hoy)):
            p1 = jugadores_hoy[i]
            p2 = jugadores_hoy[j]
            if compartieron_club(JUGADORES_DB[p1], JUGADORES_DB[p2]):
                conexiones_hoy.append((p1, p2))
                
    return jugadores_hoy, conexiones_hoy


# --- RUTAS ---

@app.route('/')
@login_required
def index():
    if current_user.username == 'admin':
        # El administrador ve a todos los usuarios ordenados por nombre
        usuarios = User.query.filter(User.username != 'admin').order_by(User.username.asc()).all()
        nombre_grupo = "Administración"
    elif current_user.grupo_id:
        # Los usuarios normales ven la clasificación de su propio grupo
        usuarios = User.query.filter_by(grupo_id=current_user.grupo_id).filter(User.username != 'admin').order_by(User.puntos_temporada.desc()).all()
        nombre_grupo = current_user.grupo.nombre
    else:
        usuarios = []
        nombre_grupo = "Sin grupo"
    
    bloqueado_hora = es_antes_de_las_11()
    
    return render_template('index.html', usuarios=usuarios, nombre_grupo=nombre_grupo, bloqueado_hora=bloqueado_hora)


@app.route('/jugar')
@login_required
def jugar():
    # Protección estricta: Si intentan entrar antes de las 11, se les expulsa
    if es_antes_de_las_11():
        flash("El reto de hoy aún no está activo. Abre a las 11:00 AM.", "error")
        return redirect(url_for('index'))

    if current_user.jugado_hoy:
        flash("Ya has participado en el reto de hoy. ¡Vuelve mañana!", "error")
        return redirect(url_for('index'))

    jugadores_hoy, conexiones_hoy = obtener_juego_del_dia()

    random.seed()
    jugadores_mezclados = list(jugadores_hoy)
    random.shuffle(jugadores_mezclados)

    return render_template('jugar.html', jugadores=jugadores_mezclados, conexiones=conexiones_hoy)


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

# --- ADMIN: ELIMINAR USUARIO ---
@app.route('/borrar_usuario/<int:user_id>', methods=['POST'])
@login_required
def borrar_usuario(user_id):
    if current_user.username != 'admin':
        flash("No tienes permisos de administrador.", "error")
        return redirect(url_for('index'))
    
    usuario = User.query.get(user_id)
    if usuario:
        # Evitar que el admin borre su propia cuenta accidentalmente
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


@app.route('/reset_clasificacion', methods=['POST'])
@login_required
def reset_clasificacion():
    if current_user.username != 'admin':
        flash("No tienes permisos de administrador.", "error")
        return redirect(url_for('index'))
    
    usuarios = User.query.all()
    for usuario in usuarios:
        usuario.puntos_temporada = 0
        usuario.jugado_hoy = False
    db.session.commit()
    flash("La clasificación general ha sido reiniciada a 0.", "success")
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
    current_user.jugado_hoy = False
    db.session.commit()
    flash("Se ha reiniciado tu estado para pruebas.", "success")
    return redirect(url_for('index'))


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