# --- BASE DE DATOS ESTADÍSTICA DE TRAYECTORIAS Y MÉTRICAS (64 JUGADORES) ---
# Métricas incluidas: goles, asistencias, tarjetas, partidos, europa, mundial, internacional

JUGADORES_DB = {
    # Real Madrid / Barcelona / PSG
    "Messi": {
        "carrera": [("Barcelona", 2004, 2021), ("PSG", 2021, 2023), ("Inter Miami", 2023, 2026)],
        "goles": 835, "asistencias": 372, "tarjetas": 15, "partidos": 1062, "europa": 149, "mundial": 26, "internacional": 180
    },
    "C. Ronaldo": {
        "carrera": [("Manchester United", 2003, 2009), ("Real Madrid", 2009, 2018), ("Juventus", 2018, 2021), ("Manchester United", 2021, 2022)],
        "goles": 895, "asistencias": 251, "tarjetas": 124, "partidos": 1225, "europa": 197, "mundial": 22, "internacional": 206
    },
    "Benzema": {
        "carrera": [("Lyon", 2004, 2009), ("Real Madrid", 2009, 2023)],
        "goles": 472, "asistencias": 191, "tarjetas": 18, "partidos": 915, "europa": 152, "mundial": 5, "internacional": 97
    },
    "Neymar": {
        "carrera": [("Barcelona", 2013, 2017), ("PSG", 2017, 2023)],
        "goles": 361, "asistencias": 224, "tarjetas": 139, "partidos": 612, "europa": 81, "mundial": 13, "internacional": 128
    },
    "Mbappé": {
        "carrera": [("Monaco", 2015, 2017), ("PSG", 2017, 2024), ("Real Madrid", 2024, 2026)],
        "goles": 332, "asistencias": 128, "tarjetas": 32, "partidos": 448, "europa": 73, "mundial": 14, "internacional": 80
    },
    "Sergio Ramos": {
        "carrera": [("Sevilla", 2003, 2005), ("Real Madrid", 2005, 2021), ("PSG", 2021, 2023), ("Sevilla", 2023, 2024)],
        "goles": 137, "asistencias": 40, "tarjetas": 265, "partidos": 985, "europa": 142, "mundial": 17, "internacional": 180
    },
    "Modric": {
        "carrera": [("Tottenham", 2008, 2012), ("Real Madrid", 2012, 2026)],
        "goles": 115, "asistencias": 152, "tarjetas": 89, "partidos": 880, "europa": 141, "mundial": 19, "internacional": 175
    },
    "Kroos": {
        "carrera": [("Bayern", 2007, 2014), ("Bayer Leverkusen", 2009, 2010), ("Real Madrid", 2014, 2024)],
        "goles": 79, "asistencias": 162, "tarjetas": 84, "partidos": 820, "europa": 150, "mundial": 14, "internacional": 108
    },
    "Casemiro": {
        "carrera": [("Real Madrid", 2013, 2022), ("Porto", 2014, 2015), ("Manchester United", 2022, 2026)],
        "goles": 55, "asistencias": 48, "tarjetas": 147, "partidos": 650, "europa": 95, "mundial": 9, "internacional": 75
    },
    "Varane": {
        "carrera": [("Real Madrid", 2011, 2021), ("Manchester United", 2021, 2024)],
        "goles": 21, "asistencias": 8, "tarjetas": 24, "partidos": 480, "europa": 93, "mundial": 18, "internacional": 93
    },
    "Marcelo": {
        "carrera": [("Real Madrid", 2007, 2022), ("Olympiacos", 2022, 2023), ("Fluminense", 2023, 2025)],
        "goles": 48, "asistencias": 103, "tarjetas": 98, "partidos": 590, "europa": 102, "mundial": 10, "internacional": 58
    },
    "Di María": {
        "carrera": [("Benfica", 2007, 2010), ("Real Madrid", 2010, 2014), ("Manchester United", 2014, 2015), ("PSG", 2015, 2022), ("Juventus", 2022, 2023), ("Benfica", 2023, 2025)],
        "goles": 178, "asistencias": 260, "tarjetas": 89, "partidos": 840, "europa": 124, "mundial": 18, "internacional": 140
    },
    "Ibrahimovic": {
        "carrera": [("Ajax", 2001, 2004), ("Juventus", 2004, 2006), ("Inter", 2006, 2009), ("Barcelona", 2009, 2010), ("Milan", 2010, 2012), ("PSG", 2012, 2016), ("Manchester United", 2016, 2018), ("Milan", 2020, 2023)],
        "goles": 573, "asistencias": 210, "tarjetas": 152, "partidos": 988, "europa": 141, "mundial": 5, "internacional": 122
    },
    "Cavani": {
        "carrera": [("Palermo", 2007, 2010), ("Napoli", 2010, 2013), ("PSG", 2013, 2020), ("Manchester United", 2020, 2022), ("Valencia", 2022, 2023)],
        "goles": 435, "asistencias": 85, "tarjetas": 110, "partidos": 780, "europa": 92, "mundial": 17, "internacional": 136
    },
    "Thiago Silva": {
        "carrera": [("Milan", 2009, 2012), ("PSG", 2012, 2020), ("Chelsea", 2020, 2024)],
        "goles": 38, "asistencias": 21, "tarjetas": 94, "partidos": 765, "europa": 105, "mundial": 15, "internacional": 113
    },
    "Marquinhos": {
        "carrera": [("Roma", 2012, 2013), ("PSG", 2013, 2026)],
        "goles": 38, "asistencias": 12, "tarjetas": 42, "partidos": 520, "europa": 91, "mundial": 6, "internacional": 84
    },
    "Suárez": {
        "carrera": [("Ajax", 2007, 2011), ("Liverpool", 2011, 2014), ("Barcelona", 2014, 2020), ("Atletico", 2020, 2022), ("Inter Miami", 2024, 2026)],
        "goles": 560, "asistencias": 298, "tarjetas": 160, "partidos": 910, "europa": 79, "mundial": 16, "internacional": 138
    },
    "Iniesta": {
        "carrera": [("Barcelona", 2002, 2018)],
        "goles": 88, "asistencias": 162, "tarjetas": 62, "partidos": 870, "europa": 138, "mundial": 16, "internacional": 131
    },
    "Xavi": {
        "carrera": [("Barcelona", 1998, 2015)],
        "goles": 119, "asistencias": 212, "tarjetas": 75, "partidos": 940, "europa": 157, "mundial": 15, "internacional": 133
    },
    "Busquets": {
        "carrera": [("Barcelona", 2008, 2023), ("Inter Miami", 2023, 2026)],
        "goles": 19, "asistencias": 45, "tarjetas": 178, "partidos": 885, "europa": 136, "mundial": 17, "internacional": 143
    },
    "Jordi Alba": {
        "carrera": [("Valencia", 2009, 2012), ("Barcelona", 2012, 2023), ("Inter Miami", 2023, 2026)],
        "goles": 37, "asistencias": 105, "tarjetas": 115, "partidos": 660, "europa": 92, "mundial": 13, "internacional": 93
    },
    "Piqué": {
        "carrera": [("Manchester United", 2004, 2008), ("Zaragoza", 2006, 2007), ("Barcelona", 2008, 2022)],
        "goles": 63, "asistencias": 15, "tarjetas": 162, "partidos": 769, "europa": 128, "mundial": 12, "internacional": 102
    },
    "Puyol": {
        "carrera": [("Barcelona", 1999, 2014)],
        "goles": 20, "asistencias": 13, "tarjetas": 119, "partidos": 682, "europa": 120, "mundial": 14, "internacional": 100
    },
    "Dani Alves": {
        "carrera": [("Sevilla", 2002, 2008), ("Barcelona", 2008, 2016), ("Juventus", 2016, 2017), ("PSG", 2017, 2019), ("Barcelona", 2021, 2022)],
        "goles": 61, "asistencias": 170, "tarjetas": 210, "partidos": 995, "europa": 143, "mundial": 9, "internacional": 126
    },
    "Mascherano": {
        "carrera": [("West Ham", 2006, 2007), ("Liverpool", 2007, 2010), ("Barcelona", 2010, 2018)],
        "goles": 8, "asistencias": 24, "tarjetas": 182, "partidos": 715, "europa": 110, "mundial": 20, "internacional": 147
    },
    "De Bruyne": {
        "carrera": [("Chelsea", 2012, 2014), ("Wolfsburg", 2014, 2015), ("Manchester City", 2015, 2026)],
        "goles": 149, "asistencias": 252, "tarjetas": 58, "partidos": 685, "europa": 78, "mundial": 10, "internacional": 105
    },
    "Haaland": {
        "carrera": [("Salzburg", 2019, 2020), ("Dortmund", 2020, 2022), ("Manchester City", 2022, 2026)],
        "goles": 255, "asistencias": 48, "tarjetas": 22, "partidos": 312, "europa": 41, "mundial": 0, "internacional": 33
    },
    "David Silva": {
        "carrera": [("Valencia", 2004, 2010), ("Manchester City", 2010, 2020), ("Real Sociedad", 2020, 2023)],
        "goles": 125, "asistencias": 204, "tarjetas": 92, "partidos": 810, "europa": 108, "mundial": 11, "internacional": 125
    },
    "Agüero": {
        "carrera": [("Atletico", 2006, 2011), ("Manchester City", 2010, 2021), ("Barcelona", 2021, 2021)],
        "goles": 426, "asistencias": 140, "tarjetas": 72, "partidos": 786, "europa": 109, "mundial": 12, "internacional": 101
    },
    "Yaya Touré": {
        "carrera": [("Monaco", 2006, 2007), ("Barcelona", 2007, 2010), ("Manchester City", 2010, 2018)],
        "goles": 103, "asistencias": 71, "tarjetas": 102, "partidos": 660, "europa": 84, "mundial": 9, "internacional": 101
    },
    "Tévez": {
        "carrera": [("West Ham", 2006, 2007), ("Manchester United", 2007, 2009), ("Manchester City", 2009, 2013), ("Juventus", 2013, 2015)],
        "goles": 308, "asistencias": 122, "tarjetas": 98, "partidos": 745, "europa": 56, "mundial": 8, "internacional": 76
    },
    "Rooney": {
        "carrera": [("Everton", 2002, 2004), ("Manchester United", 2004, 2017), ("Everton", 2017, 2018)],
        "goles": 366, "asistencias": 188, "tarjetas": 141, "partidos": 884, "europa": 98, "mundial": 11, "internacional": 120
    },
    "Pogba": {
        "carrera": [("Manchester United", 2011, 2012), ("Juventus", 2012, 2016), ("Manchester United", 2016, 2022), ("Juventus", 2022, 2024)],
        "goles": 91, "asistencias": 111, "tarjetas": 82, "partidos": 482, "europa": 78, "mundial": 12, "internacional": 91
    },
    "Rashford": {
        "carrera": [("Manchester United", 2015, 2026)],
        "goles": 131, "asistencias": 68, "tarjetas": 28, "partidos": 402, "europa": 69, "mundial": 7, "internacional": 60
    },
    "De Gea": {
        "carrera": [("Atletico", 2009, 2011), ("Manchester United", 2011, 2023), ("Fiorentina", 2024, 2026)],
        "goles": 0, "asistencias": 0, "tarjetas": 15, "partidos": 665, "europa": 111, "mundial": 5, "internacional": 45
    },
    "Lewandowski": {
        "carrera": [("Dortmund", 2010, 2014), ("Bayern", 2014, 2022), ("Barcelona", 2022, 2026)],
        "goles": 625, "asistencias": 145, "tarjetas": 81, "partidos": 892, "europa": 143, "mundial": 7, "internacional": 150
    },
    "Müller": {
        "carrera": [("Bayern", 2008, 2026)],
        "goles": 242, "asistencias": 268, "tarjetas": 42, "partidos": 707, "europa": 153, "mundial": 19, "internacional": 131
    },
    "Robben": {
        "carrera": [("Chelsea", 2004, 2007), ("Real Madrid", 2007, 2009), ("Bayern", 2009, 2019)],
        "goles": 209, "asistencias": 165, "tarjetas": 62, "partidos": 614, "europa": 112, "mundial": 15, "internacional": 96
    },
    "Ribéry": {
        "carrera": [("Marseille", 2005, 2007), ("Bayern", 2007, 2019), ("Fiorentina", 2019, 2021)],
        "goles": 151, "asistencias": 224, "tarjetas": 88, "partidos": 710, "europa": 120, "mundial": 11, "internacional": 81
    },
    "Alaba": {
        "carrera": [("Bayern", 2010, 2021), ("Hoffenheim", 2011, 2011), ("Real Madrid", 2021, 2026)],
        "goles": 45, "asistencias": 71, "tarjetas": 34, "partidos": 612, "europa": 114, "mundial": 0, "internacional": 105
    },
    "Lahm": {
        "carrera": [("Bayern", 2001, 2017), ("Stuttgart", 2003, 2005)],
        "goles": 22, "asistencias": 78, "tarjetas": 48, "partidos": 712, "europa": 117, "mundial": 20, "internacional": 113
    },
    "Schweinsteiger": {
        "carrera": [("Bayern", 2002, 2015), ("Manchester United", 2015, 2017)],
        "goles": 86, "asistencias": 112, "tarjetas": 115, "partidos": 687, "europa": 102, "mundial": 18, "internacional": 121
    },
    "Thiago": {
        "carrera": [("Barcelona", 2009, 2013), ("Bayern", 2013, 2020), ("Liverpool", 2020, 2024)],
        "goles": 48, "asistencias": 65, "tarjetas": 71, "partidos": 485, "europa": 78, "mundial": 5, "internacional": 46
    },
    "Hazard": {
        "carrera": [("Lille", 2007, 2012), ("Chelsea", 2012, 2019), ("Real Madrid", 2019, 2023)],
        "goles": 167, "asistencias": 150, "tarjetas": 42, "partidos": 620, "europa": 94, "mundial": 11, "internacional": 126
    },
    "Lampard": {
        "carrera": [("Chelsea", 2001, 2014), ("Manchester City", 2014, 2015)],
        "goles": 274, "asistencias": 182, "tarjetas": 98, "partidos": 915, "europa": 132, "mundial": 10, "internacional": 106
    },
    "Terry": {
        "carrera": [("Chelsea", 1998, 2017)],
        "goles": 67, "asistencias": 28, "tarjetas": 124, "partidos": 759, "europa": 124, "mundial": 8, "internacional": 78
    },
    "Drogba": {
        "carrera": [("Marseille", 2003, 2004), ("Chelsea", 2004, 2012), ("Galatasaray", 2013, 2014), ("Chelsea", 2014, 2015)],
        "goles": 302, "asistencias": 118, "tarjetas": 110, "partidos": 685, "europa": 102, "mundial": 8, "internacional": 105
    },
    "Čech": {
        "carrera": [("Rennes", 2002, 2004), ("Chelsea", 2004, 2015), ("Arsenal", 2015, 2019)],
        "goles": 0, "asistencias": 0, "tarjetas": 12, "partidos": 780, "europa": 124, "mundial": 4, "internacional": 124
    },
    "Fàbregas": {
        "carrera": [("Arsenal", 2003, 2011), ("Barcelona", 2011, 2014), ("Chelsea", 2014, 2019), ("Monaco", 2019, 2022)],
        "goles": 125, "asistencias": 215, "tarjetas": 118, "partidos": 830, "europa": 110, "mundial": 10, "internacional": 110
    },
    "Henry": {
        "carrera": [("Monaco", 1994, 1999), ("Juventus", 1999, 1999), ("Arsenal", 1999, 2007), ("Barcelona", 2007, 2010)],
        "goles": 360, "asistencias": 190, "tarjetas": 51, "partidos": 791, "europa": 139, "mundial": 17, "internacional": 123
    },
    "Ronaldinho": {
        "carrera": [("PSG", 2001, 2003), ("Barcelona", 2003, 2008), ("Milan", 2008, 2011)],
        "goles": 197, "asistencias": 162, "tarjetas": 68, "partidos": 542, "europa": 48, "mundial": 10, "internacional": 97
    },
    "Eto'o": {
        "carrera": [("Real Madrid", 1997, 2000), ("Mallorca", 2000, 2004), ("Barcelona", 2004, 2009), ("Inter", 2009, 2011), ("Chelsea", 2013, 2014), ("Everton", 2014, 2015)],
        "goles": 362, "asistencias": 116, "tarjetas": 81, "partidos": 724, "europa": 113, "mundial": 8, "internacional": 118
    },
    "Griezmann": {
        "carrera": [("Real Sociedad", 2009, 2014), ("Atletico", 2014, 2019), ("Barcelona", 2019, 2021), ("Atletico", 2021, 2026)],
        "goles": 242, "asistencias": 105, "tarjetas": 89, "partidos": 662, "europa": 95, "mundial": 19, "internacional": 137
    },
    "Falcao": {
        "carrera": [("Porto", 2009, 2011), ("Atletico", 2011, 2013), ("Monaco", 2013, 2019), ("Manchester United", 2014, 2015), ("Chelsea", 2015, 2016)],
        "goles": 307, "asistencias": 51, "tarjetas": 64, "partidos": 585, "europa": 68, "mundial": 4, "internacional": 104
    },
    "Godín": {
        "carrera": [("Villarreal", 2007, 2010), ("Atletico", 2010, 2019), ("Inter", 2019, 2020)],
        "goles": 38, "asistencias": 18, "tarjetas": 152, "partidos": 720, "europa": 112, "mundial": 14, "internacional": 161
    },
    "Oblak": {
        "carrera": [("Benfica", 2010, 2014), ("Atletico", 2014, 2026)],
        "goles": 0, "asistencias": 0, "tarjetas": 12, "partidos": 482, "europa": 90, "mundial": 4, "internacional": 72
    },
    "Diego Costa": {
        "carrera": [("Atletico", 2010, 2014), ("Chelsea", 2014, 2017), ("Atletico", 2018, 2020)],
        "goles": 188, "asistencias": 71, "tarjetas": 131, "partidos": 495, "europa": 65, "mundial": 5, "internacional": 26
    },
    "Joaquín": {
        "carrera": [("Real Betis", 2000, 2006), ("Valencia", 2006, 2011), ("Malaga", 2011, 2013), ("Fiorentina", 2013, 2015), ("Real Betis", 2015, 2023)],
        "goles": 112, "asistencias": 142, "tarjetas": 68, "partidos": 912, "europa": 84, "mundial": 5, "internacional": 51
    },
    "Fekir": {
        "carrera": [("Lyon", 2013, 2019), ("Real Betis", 2019, 2024)],
        "goles": 105, "asistencias": 78, "tarjetas": 71, "partidos": 395, "europa": 54, "mundial": 6, "internacional": 25
    },
    "Canales": {
        "carrera": [("Real Madrid", 2010, 2012), ("Valencia", 2011, 2014), ("Real Sociedad", 2014, 2018), ("Real Betis", 2018, 2023)],
        "goles": 68, "asistencias": 74, "tarjetas": 58, "partidos": 492, "europa": 42, "mundial": 0, "internacional": 11
    },
    "Isco": {
        "carrera": [("Valencia", 2010, 2011), ("Malaga", 2011, 2013), ("Real Madrid", 2013, 2022), ("Sevilla", 2022, 2022), ("Real Betis", 2023, 2026)],
        "goles": 82, "asistencias": 79, "tarjetas": 54, "partidos": 520, "europa": 82, "mundial": 4, "internacional": 38
    },
    "Bellerín": {
        "carrera": [("Arsenal", 2013, 2022), ("Real Betis", 2021, 2022), ("Barcelona", 2022, 2023), ("Real Betis", 2023, 2026)],
        "goles": 15, "asistencias": 42, "tarjetas": 41, "partidos": 380, "europa": 43, "mundial": 0, "internacional": 4
    },
    "Jesús Navas": {
        "carrera": [("Sevilla", 2003, 2013), ("Manchester City", 2013, 2017), ("Sevilla", 2017, 2026)],
        "goles": 39, "asistencias": 160, "tarjetas": 89, "partidos": 890, "europa": 115, "mundial": 3, "internacional": 56
    },
    "Rakitic": {
        "carrera": [("Schalke", 2007, 2011), ("Sevilla", 2011, 2014), ("Barcelona", 2014, 2020), ("Sevilla", 2020, 2024)],
        "goles": 121, "asistencias": 150, "tarjetas": 115, "partidos": 812, "europa": 139, "mundial": 19, "internacional": 106
    },
    "Banega": {
        "carrera": [("Valencia", 2008, 2014), ("Atletico", 2008, 2009), ("Sevilla", 2014, 2016), ("Inter", 2016, 2017), ("Sevilla", 2017, 2020)],
        "goles": 48, "asistencias": 82, "tarjetas": 151, "partidos": 598, "europa": 81, "mundial": 3, "internacional": 65
    },
    "Luuk de Jong": {
        "carrera": [("Monchengladbach", 2012, 2014), ("PSV", 2014, 2019), ("Sevilla", 2019, 2022), ("Barcelona", 2021, 2022), ("PSV", 2022, 2026)],
        "goles": 224, "asistencias": 78, "tarjetas": 42, "partidos": 580, "europa": 95, "mundial": 5, "internacional": 39
    }
}