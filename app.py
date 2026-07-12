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
    puntos_general = db.Column(db.Integer, default=0)
    ultimo_juego_fecha = db.Column(db.Date, nullable=True)
    partidas_jugadas = db.Column(db.Integer, default=0)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- BASE DE DATOS ESTADÍSTICA DE TRAYECTORIAS Y MÉTRICAS (64 JUGADORES) ---

JUGADORES_DB = {
    # Real Madrid / Barcelona / PSG
    "Messi": {
        "carrera": [("Barcelona", 2004, 2021), ("PSG", 2021, 2023), ("Inter Miami", 2023, 2026)],
        "goles": 835, "asistencias": 372, "tarjetas": 15, "partidos": 1062
    },
    "C. Ronaldo": {
        "carrera": [("Manchester United", 2003, 2009), ("Real Madrid", 2009, 2018), ("Juventus", 2018, 2021), ("Manchester United", 2021, 2022)],
        "goles": 895, "asistencias": 251, "tarjetas": 124, "partidos": 1225
    },
    "Benzema": {
        "carrera": [("Lyon", 2004, 2009), ("Real Madrid", 2009, 2023)],
        "goles": 472, "asistencias": 191, "tarjetas": 18, "partidos": 915
    },
    "Neymar": {
        "carrera": [("Barcelona", 2013, 2017), ("PSG", 2017, 2023)],
        "goles": 361, "asistencias": 224, "tarjetas": 139, "partidos": 612
    },
    "Mbappé": {
        "carrera": [("Monaco", 2015, 2017), ("PSG", 2017, 2024), ("Real Madrid", 2024, 2026)],
        "goles": 332, "asistencias": 128, "tarjetas": 32, "partidos": 448
    },
    "Sergio Ramos": {
        "carrera": [("Sevilla", 2003, 2005), ("Real Madrid", 2005, 2021), ("PSG", 2021, 2023), ("Sevilla", 2023, 2024)],
        "goles": 137, "asistencias": 40, "tarjetas": 265, "partidos": 985
    },
    "Modric": {
        "carrera": [("Tottenham", 2008, 2012), ("Real Madrid", 2012, 2026)],
        "goles": 115, "asistencias": 152, "tarjetas": 89, "partidos": 880
    },
    "Kroos": {
        "carrera": [("Bayern", 2007, 2014), ("Bayer Leverkusen", 2009, 2010), ("Real Madrid", 2014, 2024)],
        "goles": 79, "asistencias": 162, "tarjetas": 84, "partidos": 820
    },
    "Casemiro": {
        "carrera": [("Real Madrid", 2013, 2022), ("Porto", 2014, 2015), ("Manchester United", 2022, 2026)],
        "goles": 55, "asistencias": 48, "tarjetas": 147, "partidos": 650
    },
    "Varane": {
        "carrera": [("Real Madrid", 2011, 2021), ("Manchester United", 2021, 2024)],
        "goles": 21, "asistencias": 8, "tarjetas": 24, "partidos": 480
    },
    "Marcelo": {
        "carrera": [("Real Madrid", 2007, 2022), ("Olympiacos", 2022, 2023), ("Fluminense", 2023, 2025)],
        "goles": 48, "asistencias": 103, "tarjetas": 98, "partidos": 590
    },
    "Di María": {
        "carrera": [("Benfica", 2007, 2010), ("Real Madrid", 2010, 2014), ("Manchester United", 2014, 2015), ("PSG", 2015, 2022), ("Juventus", 2022, 2023), ("Benfica", 2023, 2025)],
        "goles": 178, "asistencias": 260, "tarjetas": 89, "partidos": 840
    },
    "Ibrahimovic": {
        "carrera": [("Ajax", 2001, 2004), ("Juventus", 2004, 2006), ("Inter", 2006, 2009), ("Barcelona", 2009, 2010), ("Milan", 2010, 2012), ("PSG", 2012, 2016), ("Manchester United", 2016, 2018), ("Milan", 2020, 2023)],
        "goles": 573, "asistencias": 210, "tarjetas": 152, "partidos": 988
    },
    "Cavani": {
        "carrera": [("Palermo", 2007, 2010), ("Napoli", 2010, 2013), ("PSG", 2013, 2020), ("Manchester United", 2020, 2022), ("Valencia", 2022, 2023)],
        "goles": 435, "asistencias": 85, "tarjetas": 110, "partidos": 780
    },
    "Thiago Silva": {
        "carrera": [("Milan", 2009, 2012), ("PSG", 2012, 2020), ("Chelsea", 2020, 2024)],
        "goles": 38, "asistencias": 21, "tarjetas": 94, "partidos": 765
    },
    "Marquinhos": {
        "carrera": [("Roma", 2012, 2013), ("PSG", 2013, 2026)],
        "goles": 38, "asistencias": 12, "tarjetas": 42, "partidos": 520
    },
    "Suárez": {
        "carrera": [("Ajax", 2007, 2011), ("Liverpool", 2011, 2014), ("Barcelona", 2014, 2020), ("Atletico", 2020, 2022), ("Inter Miami", 2024, 2026)],
        "goles": 560, "asistencias": 298, "tarjetas": 160, "partidos": 910
    },
    "Iniesta": {
        "carrera": [("Barcelona", 2002, 2018)],
        "goles": 88, "asistencias": 162, "tarjetas": 62, "partidos": 870
    },
    "Xavi": {
        "carrera": [("Barcelona", 1998, 2015)],
        "goles": 119, "asistencias": 212, "tarjetas": 75, "partidos": 940
    },
    "Busquets": {
        "carrera": [("Barcelona", 2008, 2023), ("Inter Miami", 2023, 2026)],
        "goles": 19, "asistencias": 45, "tarjetas": 178, "partidos": 885
    },
    "Jordi Alba": {
        "carrera": [("Valencia", 2009, 2012), ("Barcelona", 2012, 2023), ("Inter Miami", 2023, 2026)],
        "goles": 37, "asistencias": 105, "tarjetas": 115, "partidos": 660
    },
    "Piqué": {
        "carrera": [("Manchester United", 2004, 2008), ("Zaragoza", 2006, 2007), ("Barcelona", 2008, 2022)],
        "goles": 63, "asistencias": 15, "tarjetas": 162, "partidos": 769
    },
    "Puyol": {
        "carrera": [("Barcelona", 1999, 2014)],
        "goles": 20, "asistencias": 13, "tarjetas": 119, "partidos": 682
    },
    "Dani Alves": {
        "carrera": [("Sevilla", 2002, 2008), ("Barcelona", 2008, 2016), ("Juventus", 2016, 2017), ("PSG", 2017, 2019), ("Barcelona", 2021, 2022)],
        "goles": 61, "asistencias": 170, "tarjetas": 210, "partidos": 995
    },
    "Mascherano": {
        "carrera": [("West Ham", 2006, 2007), ("Liverpool", 2007, 2010), ("Barcelona", 2010, 2018)],
        "goles": 8, "asistencias": 24, "tarjetas": 182, "partidos": 715
    },
    "De Bruyne": {
        "carrera": [("Chelsea", 2012, 2014), ("Wolfsburg", 2014, 2015), ("Manchester City", 2015, 2026)],
        "goles": 149, "asistencias": 252, "tarjetas": 58, "partidos": 685
    },
    "Haaland": {
        "carrera": [("Salzburg", 2019, 2020), ("Dortmund", 2020, 2022), ("Manchester City", 2022, 2026)],
        "goles": 255, "asistencias": 48, "tarjetas": 22, "partidos": 312
    },
    "David Silva": {
        "carrera": [("Valencia", 2004, 2010), ("Manchester City", 2010, 2020), ("Real Sociedad", 2020, 2023)],
        "goles": 125, "asistencias": 204, "tarjetas": 92, "partidos": 810
    },
    "Agüero": {
        "carrera": [("Atletico", 2006, 2011), ("Manchester City", 2010, 2021), ("Barcelona", 2021, 2021)],
        "goles": 426, "asistencias": 140, "tarjetas": 72, "partidos": 786
    },
    "Yaya Touré": {
        "carrera": [("Monaco", 2006, 2007), ("Barcelona", 2007, 2010), ("Manchester City", 2010, 2018)],
        "goles": 103, "asistencias": 71, "tarjetas": 102, "partidos": 660
    },
    "Tévez": {
        "carrera": [("West Ham", 2006, 2007), ("Manchester United", 2007, 2009), ("Manchester City", 2009, 2013), ("Juventus", 2013, 2015)],
        "goles": 308, "asistencias": 122, "tarjetas": 98, "partidos": 745
    },
    "Rooney": {
        "carrera": [("Everton", 2002, 2004), ("Manchester United", 2004, 2017), ("Everton", 2017, 2018)],
        "goles": 366, "asistencias": 188, "tarjetas": 141, "partidos": 884
    },
    "Pogba": {
        "carrera": [("Manchester United", 2011, 2012), ("Juventus", 2012, 2016), ("Manchester United", 2016, 2022), ("Juventus", 2022, 2024)],
        "goles": 91, "asistencias": 111, "tarjetas": 82, "partidos": 482
    },
    "Rashford": {
        "carrera": [("Manchester United", 2015, 2026)],
        "goles": 131, "asistencias": 68, "tarjetas": 28, "partidos": 402
    },
    "De Gea": {
        "carrera": [("Atletico", 2009, 2011), ("Manchester United", 2011, 2023), ("Fiorentina", 2024, 2026)],
        "goles": 0, "asistencias": 0, "tarjetas": 15, "partidos": 665
    },
    "Lewandowski": {
        "carrera": [("Dortmund", 2010, 2014), ("Bayern", 2014, 2022), ("Barcelona", 2022, 2026)],
        "goles": 625, "asistencias": 145, "tarjetas": 81, "partidos": 892
    },
    "Müller": {
        "carrera": [("Bayern", 2008, 2026)],
        "goles": 242, "asistencias": 268, "tarjetas": 42, "partidos": 707
    },
    "Robben": {
        "carrera": [("Chelsea", 2004, 2007), ("Real Madrid", 2007, 2009), ("Bayern", 2009, 2019)],
        "goles": 209, "asistencias": 165, "tarjetas": 62, "partidos": 614
    },
    "Ribéry": {
        "carrera": [("Marseille", 2005, 2007), ("Bayern", 2007, 2019), ("Fiorentina", 2019, 2021)],
        "goles": 151, "asistencias": 224, "tarjetas": 88, "partidos": 710
    },
    "Alaba": {
        "carrera": [("Bayern", 2010, 2021), ("Hoffenheim", 2011, 2011), ("Real Madrid", 2021, 2026)],
        "goles": 45, "asistencias": 71, "tarjetas": 34, "partidos": 612
    },
    "Lahm": {
        "carrera": [("Bayern", 2001, 2017), ("Stuttgart", 2003, 2005)],
        "goles": 22, "asistencias": 78, "tarjetas": 48, "partidos": 712
    },
    "Schweinsteiger": {
        "carrera": [("Bayern", 2002, 2015), ("Manchester United", 2015, 2017)],
        "goles": 86, "asistencias": 112, "tarjetas": 115, "partidos": 687
    },
    "Thiago": {
        "carrera": [("Barcelona", 2009, 2013), ("Bayern", 2013, 2020), ("Liverpool", 2020, 2024)],
        "goles": 48, "asistencias": 65, "tarjetas": 71, "partidos": 485
    },
    "Hazard": {
        "carrera": [("Lille", 2007, 2012), ("Chelsea", 2012, 2019), ("Real Madrid", 2019, 2023)],
        "goles": 167, "asistencias": 150, "tarjetas": 42, "partidos": 620
    },
    "Lampard": {
        "carrera": [("Chelsea", 2001, 2014), ("Manchester City", 2014, 2015)],
        "goles": 274, "asistencias": 182, "tarjetas": 98, "partidos": 915
    },
    "Terry": {
        "carrera": [("Chelsea", 1998, 2017)],
        "goles": 67, "asistencias": 28, "tarjetas": 124, "partidos": 759
    },
    "Drogba": {
        "carrera": [("Marseille", 2003, 2004), ("Chelsea", 2004, 2012), ("Galatasaray", 2013, 2014), ("Chelsea", 2014, 2015)],
        "goles": 302, "asistencias": 118, "tarjetas": 110, "partidos": 685
    },
    "Čech": {
        "carrera": [("Rennes", 2002, 2004), ("Chelsea", 2004, 2015), ("Arsenal", 2015, 2019)],
        "goles": 0, "asistencias": 0, "tarjetas": 12, "partidos": 780
    },
    "Fàbregas": {
        "carrera": [("Arsenal", 2003, 2011), ("Barcelona", 2011, 2014), ("Chelsea", 2014, 2019), ("Monaco", 2019, 2022)],
        "goles": 125, "asistencias": 215, "tarjetas": 118, "partidos": 830
    },
    "Henry": {
        "carrera": [("Monaco", 1994, 1999), ("Juventus", 1999, 1999), ("Arsenal", 1999, 2007), ("Barcelona", 2007, 2010)],
        "goles": 360, "asistencias": 190, "tarjetas": 51, "partidos": 791
    },
    "Ronaldinho": {
        "carrera": [("PSG", 2001, 2003), ("Barcelona", 2003, 2008), ("Milan", 2008, 2011)],
        "goles": 197, "asistencias": 162, "tarjetas": 68, "partidos": 542
    },
    "Eto'o": {
        "carrera": [("Real Madrid", 1997, 2000), ("Mallorca", 2000, 2004), ("Barcelona", 2004, 2009), ("Inter", 2009, 2011), ("Chelsea", 2013, 2014), ("Everton", 2014, 2015)],
        "goles": 362, "asistencias": 116, "tarjetas": 81, "partidos": 724
    },
    "Griezmann": {
        "carrera": [("Real Sociedad", 2009, 2014), ("Atletico", 2014, 2019), ("Barcelona", 2019, 2021), ("Atletico", 2021, 2026)],
        "goles": 242, "asistencias": 105, "tarjetas": 89, "partidos": 662
    },
    "Falcao": {
        "carrera": [("Porto", 2009, 2011), ("Atletico", 2011, 2013), ("Monaco", 2013, 2019), ("Manchester United", 2014, 2015), ("Chelsea", 2015, 2016)],
        "goles": 307, "asistencias": 51, "tarjetas": 64, "partidos": 585
    },
    "Godín": {
        "carrera": [("Villarreal", 2007, 2010), ("Atletico", 2010, 2019), ("Inter", 2019, 2020)],
        "goles": 38, "asistencias": 18, "tarjetas": 152, "partidos": 720
    },
    "Oblak": {
        "carrera": [("Benfica", 2010, 2014), ("Atletico", 2014, 2026)],
        "goles": 0, "asistencias": 0, "tarjetas": 12, "partidos": 482
    },
    "Diego Costa": {
        "carrera": [("Atletico", 2010, 2014), ("Chelsea", 2014, 2017), ("Atletico", 2018, 2020)],
        "goles": 188, "asistencias": 71, "tarjetas": 131, "partidos": 495
    },
    "Joaquín": {
        "carrera": [("Real Betis", 2000, 2006), ("Valencia", 2006, 2011), ("Malaga", 2011, 2013), ("Fiorentina", 2013, 2015), ("Real Betis", 2015, 2023)],
        "goles": 112, "asistencias": 142, "tarjetas": 68, "partidos": 912
    },
    "Fekir": {
        "carrera": [("Lyon", 2013, 2019), ("Real Betis", 2019, 2024)],
        "goles": 105, "asistencias": 78, "tarjetas": 71, "partidos": 395
    },
    "Canales": {
        "carrera": [("Real Madrid", 2010, 2012), ("Valencia", 2011, 2014), ("Real Sociedad", 2014, 2018), ("Real Betis", 2018, 2023)],
        "goles": 68, "asistencias": 74, "tarjetas": 58, "partidos": 492
    },
    "Isco": {
        "carrera": [("Valencia", 2010, 2011), ("Malaga", 2011, 2013), ("Real Madrid", 2013, 2022), ("Sevilla", 2022, 2022), ("Real Betis", 2023, 2026)],
        "goles": 82, "asistencias": 79, "tarjetas": 54, "partidos": 520
    },
    "Bellerín": {
        "carrera": [("Arsenal", 2013, 2022), ("Real Betis", 2021, 2022), ("Barcelona", 2022, 2023), ("Real Betis", 2023, 2026)],
        "goles": 15, "asistencias": 42, "tarjetas": 41, "partidos": 380
    },
    "Jesús Navas": {
        "carrera": [("Sevilla", 2003, 2013), ("Manchester City", 2013, 2017), ("Sevilla", 2017, 2026)],
        "goles": 39, "asistencias": 160, "tarjetas": 89, "partidos": 890
    },
    "Rakitic": {
        "carrera": [("Schalke", 2007, 2011), ("Sevilla", 2011, 2014), ("Barcelona", 2014, 2020), ("Sevilla", 2020, 2024)],
        "goles": 121, "asistencias": 150, "tarjetas": 115, "partidos": 812
    },
    "Banega": {
        "carrera": [("Valencia", 2008, 2014), ("Atletico", 2008, 2009), ("Sevilla", 2014, 2016), ("Inter", 2016, 2017), ("Sevilla", 2017, 2020)],
        "goles": 48, "asistencias": 82, "tarjetas": 151, "partidos": 598
    },
    "Luuk de Jong": {
        "carrera": [("Monchengladbach", 2012, 2014), ("PSV", 2014, 2019), ("Sevilla", 2019, 2022), ("Barcelona", 2021, 2022), ("PSV", 2022, 2026)],
        "goles": 224, "asistencias": 78, "tarjetas": 42, "partidos": 580
    }
}


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


# --- CONTROL DE ALTERNANCIA DIARIA ---

def obtener_tipo_juego_hoy(fecha_juego):
    """Alterna el juego: días pares 'grid' (Cuadrícula), días impares 'ordenar'."""
    # toordinal() da un número único para cada día de la historia de la humanidad
    return "grid" if fecha_juego.toordinal() % 2 == 0 else "ordenar"


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
                # Comparamos la clave de carrera interna
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


# --- GENERADOR JUEGO 2: ORDENAR ---
def obtener_juego_ordenar(fecha_juego):
    hoy_str = fecha_juego.strftime('%Y%m%d')
    semilla = int(hoy_str)
    random.seed(semilla)
    
    # 1. Elegimos 10 jugadores aleatorios estables para hoy
    pool_jugadores = list(JUGADORES_DB.keys())
    jugadores_hoy = random.sample(pool_jugadores, 10)
    
    # 2. Elegimos la métrica al azar para hoy
    metricas = ["goles", "asistencias", "tarjetas", "partidos"]
    metrica_seleccionada = random.choice(metricas)
    
    # Mapeo para mostrar nombres bonitos en el HTML
    titulos_metrica = {
        "goles": "Goles en su Carrera ⚽",
        "asistencias": "Asistencias de Gol 🎯",
        "tarjetas": "Tarjetas Amarillas Recibidas 🟨",
        "partidos": "Partidos Oficiales Disputados 🏟️"
    }
    titulo_bonito = titulos_metrica[metrica_seleccionada]
    
    # 3. Solución correcta ordenada de MAYOR a MENOR basándose en la métrica
    solucion_ordenada = sorted(jugadores_hoy, key=lambda p: JUGADORES_DB[p][metrica_seleccionada], reverse=True)
    
    # 4. Mezclamos los jugadores para mostrárselos desordenados al usuario
    random.seed()
    jugadores_desordenados = list(jugadores_hoy)
    random.shuffle(jugadores_desordenados)
    
    return jugadores_desordenados, titulo_bonito, solucion_ordenada, metrica_seleccionada


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

    # Determinar qué minijuego toca hoy según alternancia diaria
    tipo_juego = obtener_tipo_juego_hoy(fecha_activa)

    if tipo_juego == "grid":
        # JUEGO 1: Cuadrícula de parejas
        jugadores_hoy, conexiones_hoy = obtener_juego_del_dia(fecha_activa)
        random.seed()
        jugadores_mezclados = list(jugadores_hoy)
        random.shuffle(jugadores_mezclados)
        return render_template('jugar.html', jugadores=jugadores_mezclados, conexiones=conexiones_hoy)
    else:
        # JUEGO 2: Ordenar jugadores
        jugadores_desordenados, titulo_bonito, solucion_ordenada, metrica = obtener_juego_ordenar(fecha_activa)
        
        # Guardamos en un diccionario el valor real de cada jugador para que JS pueda consultarlo si falla o acierta
        valores_reales = {p: JUGADORES_DB[p][metrica] for p in jugadores_desordenados}
        
        return render_template(
            'ordenar.html', 
            jugadores=jugadores_desordenados, 
            titulo_bonito=titulo_bonito, 
            solucion=solucion_ordenada,
            valores_reales=valores_reales
        )


@app.route('/guardar_puntuacion', methods=['POST'])
@login_required
def guardar_puntuacion():
    if current_user.username == 'admin':
        return jsonify({"status": "error", "message": "El admin no puntúa"}), 400

    fecha_activa = obtener_fecha_juego_actual()
    
    if current_user.ultimo_juego_fecha == fecha_activa:
        return jsonify({"status": "error", "message": "Ya has jugado este reto"}), 400

    datos = request.get_json()
    segundos = datos.get('segundos', 9999)
    completado = datos.get('completado', False)
    puntos_enviados = datos.get('puntos')  # Capturamos los puntos de precisión si existen

    if completado:
        # Si el juego de ordenar envía los puntos calculados por error, los usamos.
        # Si no, calculamos por tiempo (juego de cuadrícula).
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