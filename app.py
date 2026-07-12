import os
import random
import datetime
from datetime import time
from zoneinfo import ZoneInfo
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
    # NUEVO: Almacenar puntos históricos acumulados de todas las temporadas
    puntos_general = db.Column(db.Integer, default=0)
    ultimo_juego_fecha = db.Column(db.Date, nullable=True)
    partidas_jugadas = db.Column(db.Integer, default=0)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- BASE DE DATOS AUTOMÁTICA DE TRAYECTORIAS (64 JUGADORES) ---

JUGADORES_DB = {
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
    "Griezmann": [("Real Sociedad", 2009, 2014), ("Atletico", 2014, 2019), ("Barcelona", 2019, 2021), ("Atletico", 2021, 2026)],
    "Falcao": [("Porto", 2009, 2011), ("Atletico", 2011, 2013), ("Monaco", 2013, 2019), ("Manchester United", 2014, 2015), ("Chelsea", 2015, 2016)],
    "Godín": [("Villarreal", 2007, 2010), ("Atletico", 2010, 2019), ("Inter", 2019, 2020)],
    "Oblak": [("Benfica", 2010, 2014), ("Atletico", 2014, 2026)],
    "Diego Costa": [("Atletico", 2010, 2014), ("Chelsea", 2014, 2017), ("Atletico", 2018, 2020)],
    "Joaquín": [("Real Betis", 2000, 2006), ("Valencia", 2006, 2011), ("Malaga", 2011, 2013), ("Fiorentina", 2013, 2015), ("Real Betis", 2015, 2023)],
    "Fekir": [("Lyon", 2013, 2019), ("Real Betis", 2019, 2024)],
    "Canales": [("Real Madrid", 2010, 2012), ("Valencia", 2011, 2014), ("Real Sociedad", 2014, 2018), ("Real Betis", 2018, 2023)],
    "Isco": [("Valencia", 2010, 2011), ("Malaga", 2011, 2013), ("Real Madrid", 2013, 2022), ("Sevilla", 2022, 2022), ("Real Betis", 2023, 2026)],
    "Bellerín": [("Arsenal", 2013, 2022), ("Real Betis", 2021, 2022), ("Barcelona", 2022, 2023), ("Real Betis", 2023, 2026)],
    "Jesús Navas": [("Sevilla", 2003, 2013), ("Manchester City", 2013, 2017), ("Sevilla", 2017, 2026)],
    "Rakitic": [("Schalke", 2007, 2011), ("Sevilla", 2011, 2014), ("Barcelona", 2014, 2020), ("Sevilla", 2020, 2024)],
    "Banega": [("Valencia", 2008, 2014), ("Atletico", 2008, 2009), ("Sevilla", 2014, 2016), ("Inter", 2016, 2017), ("Sevilla", 2017, 2020)],
    "Luuk de Jong": [("Monchengladbach", 2012, 2014), ("PSV", 2014, 2019), ("Sevilla", 2019, 2022), ("Barcelona", 2021, 2022), ("PSV", 2022, 2026)]
}


# --- CONTROL DE TEMPORADAS AUTOMÁTICAS (20 DÍAS) ---

def actualizar_y_obtener_temporada():
    """Comprueba el estado de la temporada actual y maneja el reinicio cada 20 días."""
    tz = ZoneInfo("Europe/Madrid")
    hoy = datetime.datetime.now(tz).date()
    
    # Intentamos obtener la temporada más reciente
    temporada_activa = Temporada.query.order_by(Temporada.id.desc()).first()
    
    # Si no existe ninguna, inicializamos la Temporada 1 hoy mismo
    if not temporada_activa:
        temporada_activa = Temporada(numero=1, fecha_inicio=hoy)
        db.session.add(temporada_activa)
        db.session.commit()
        
    # Calcular días transcurridos desde que empezó la temporada activa
    dias_transcurridos = (hoy - temporada_activa.fecha_inicio).days
    
    # Si han transcurrido 20 días o más, finaliza la temporada e iniciamos la siguiente
    if dias_transcurridos >= 20:
        nueva_temporada = Temporada(
            numero=temporada_activa.numero + 1,
            fecha_inicio=hoy
        )
        db.session.add(nueva_temporada)
        
        # Resetear los marcadores de temporada de todos los usuarios
        # Nota: "puntos_general" y "partidas_jugadas" históricas no se tocan
        usuarios = User.query.all()
        for usuario in usuarios:
            usuario.puntos_temporada = 0
            usuario.ultimo_juego_fecha = None
            
        db.session.commit()
        temporada_activa = nueva_temporada
        dias_transcurridos = 0
        
    dias_restantes = 20 - dias_transcurridos
    return temporada_activa.numero, dias_restantes


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
                if compartieron_club(JUGADORES_DB[p1], JUGADORES_DB[p2]):
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
            if compartieron_club(JUGADORES_DB[u1], JUGADORES_DB[u2]):
                conexiones_hoy.append((u1, u2))
                
    conexiones_hoy = list(set(conexiones_hoy))
    return jugadores_hoy, conexiones_hoy


# --- RUTAS ---

@app.route('/')
@login_required
def index():
    # Comprobar si hay reinicio de temporada automatizado
    num_temporada, dias_restantes = actualizar_y_obtener_temporada()

    if current_user.username == 'admin':
        usuarios_temporada = User.query.filter(User.username != 'admin').all()
        usuarios_general = User.query.filter(User.username != 'admin').all()
        nombre_grupo = "Administración (Ver todo)"
        bloqueado_hora = False
        ha_jugado_hoy = False
    elif current_user.grupo_id:
        # Obtenemos la clasificación de la temporada (ordenada por puntos_temporada)
        usuarios_temporada = User.query.filter_by(grupo_id=current_user.grupo_id).filter(User.username != 'admin').order_by(User.puntos_temporada.desc()).all()
        # Obtenemos la clasificación histórica general (ordenada por puntos_general)
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
        flash("El administrador no puede participar en las partidas de juego.", "error")
        return redirect(url_for('index'))

    fecha_activa = obtener_fecha_juego_actual()
    
    if current_user.ultimo_juego_fecha == fecha_activa:
        flash("Ya has participado en el reto activo. ¡Vuelve cuando se abra el siguiente!", "error")
        return redirect(url_for('index'))

    jugadores_hoy, conexiones_hoy = obtener_juego_del_dia(fecha_activa)

    random.seed()
    jugadores_mezclados = list(jugadores_hoy)
    random.shuffle(jugadores_mezclados)

    return render_template('jugar.html', jugadores=jugadores_mezclados, conexiones=conexiones_hoy)


@app.route('/guardar_puntuacion', methods=['POST'])
@login_required
def guardar_puntuacion():
    if current_user.username == 'admin':
        return jsonify({"status": "error", "message": "El administrador no guarda puntuación"}), 400

    fecha_activa = obtener_fecha_juego_actual()
    
    if current_user.ultimo_juego_fecha == fecha_activa:
        return jsonify({"status": "error", "message": "Ya has jugado este reto"}), 400

    datos = request.get_json()
    segundos = datos.get('segundos', 9999)
    completado = datos.get('completado', False)

    if completado:
        puntos_obtenidos = max(100, 1000 - segundos) 
        # Sumar a la temporada actual
        current_user.puntos_temporada += puntos_obtenidos
        # Sumar al histórico general
        current_user.puntos_general += puntos_obtenidos
        
        current_user.ultimo_juego_fecha = fecha_activa
        current_user.partidas_jugadas += 1
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


@app.route('/reset_clasificacion', methods=['POST'])
@login_required
def reset_clasificacion():
    """El administrador puede resetear la temporada de forma manual si lo desea."""
    if current_user.username != 'admin':
        flash("No tienes permisos de administrador.", "error")
        return redirect(url_for('index'))
    
    usuarios = User.query.all()
    for usuario in usuarios:
        usuario.puntos_temporada = 0
        usuario.ultimo_juego_fecha = None
        # Las partidas jugadas y el puntos_general se mantienen en el reset de temporada
    
    # También forzamos el reinicio de la fecha de la temporada activa a hoy
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