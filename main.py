import discord
from discord.ext import commands
import random
import os
import datetime
import sqlite3

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Configuración de la base de datos
def init_db():
    conn = sqlite3.connect('green_hero.db')
    c = conn.cursor()
    # Tabla de usuarios con puntos
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, 
                  points INTEGER DEFAULT 0)''')
    # Tabla de insignias desbloqueadas
    c.execute('''CREATE TABLE IF NOT EXISTS badges
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  badge_name TEXT,
                  unlocked_date TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    conn.commit()
    conn.close()

# Inicializar la base de datos al iniciar el bot
init_db()

def get_user_points(user_id):
    conn = sqlite3.connect('green_hero.db')
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def update_user_points(user_id, points):
    conn = sqlite3.connect('green_hero.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, points) VALUES (?, 0)", (user_id,))
    c.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()
    
    # Obtener los nuevos puntos de manera segura
    c.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    
    # Asegurarse de que siempre devolvemos un número entero
    return result[0] if result else points  # Si no hay resultado, devolvemos los puntos recién añadidos

def check_and_award_badges(user_id, points):
    # Asegurarse de que points es un número entero
    if points is None:
        points = get_user_points(user_id)
    
    badges = []
    conn = sqlite3.connect('green_hero.db')
    c = conn.cursor()
    
    # Definir los requisitos para cada insignia (basado en puntos)
    badge_requirements = {
        "🌱 Semilla Verde": 50,
        "♻️ Reciclador Novato": 100,
        "🌿 Eco-Amistoso": 250,
        "🌍 Guardián del Planeta": 500,
        "🏆 Héroe Verde": 1000
    }
    
    for badge_name, requirement in badge_requirements.items():
        # Verificar si el usuario ya tiene esta insignia
        c.execute("SELECT * FROM badges WHERE user_id = ? AND badge_name = ?", (user_id, badge_name))
        if not c.fetchone() and points >= requirement:
            # Otorgar la insignia
            today = datetime.date.today().isoformat()
            c.execute("INSERT INTO badges (user_id, badge_name, unlocked_date) VALUES (?, ?, ?)",
                     (user_id, badge_name, today))
            badges.append(badge_name)
    
    conn.commit()
    conn.close()
    return badges

def get_user_badges(user_id):
    conn = sqlite3.connect('green_hero.db')
    c = conn.cursor()
    c.execute("SELECT badge_name, unlocked_date FROM badges WHERE user_id = ? ORDER BY unlocked_date", (user_id,))
    badges = c.fetchall()
    conn.close()
    return badges

preguntas = {
    "¿Cuál es el principal gas de efecto invernadero?": "CO2",
    "¿Qué energía es renovable? (carbón / solar)": "solar",
    "¿Qué océano está más afectado por el plástico?": "Pacífico",
    "¿Qué acción ayuda a reducir la huella de carbono? (andar en bici / usar más plástico)": "andar en bici",
    "¿Cuál de estos materiales tarda más en degradarse: vidrio, papel o cáscara de fruta?": "vidrio",
    "¿Qué significa la regla de las 3R en ecología?": "reducir, reutilizar, reciclar",
    "¿Cuál es la fuente principal de energía renovable más usada en el mundo?": "hidráulica",
    "¿Cuál de estos animales está en peligro por el deshielo del Ártico?": "oso polar",
}

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.command()
async def hola(ctx):
    await ctx.send("🌱 ¡Hola! Soy tu bot ecológico. Usa `!dato`, `!quiz` o mándame una imagen con `!clasificar`.")

@bot.command()
async def dato(ctx):
    datos = [
        "♻️ Cada año, 8 millones de toneladas de plástico terminan en el océano.",
        "🌍 Plantar un árbol puede absorber hasta 22 kg de CO2 al año.",
        "💧 Ahorrar un litro de agua embotellada ahorra 3 litros de agua en su producción.",
        "☀️ La energía solar es la fuente renovable que más crece en el mundo.",
        "🌊 Más del 70% de la superficie de la Tierra está cubierta de agua, pero solo el 3% es dulce.",
        "🐝 Las abejas son responsables de polinizar alrededor del 75% de los cultivos que consumimos.",
        "🪵 Reciclar una tonelada de papel ahorra 17 árboles y más de 25,000 litros de agua.",
        "🌡️ La última década ha sido la más caliente registrada en la historia.",
        "⚡ Una bombilla LED consume hasta un 80% menos energía que una incandescente.",
        "🚴‍♂️ Si todos usáramos la bicicleta en trayectos cortos, se reducirían millones de toneladas de CO₂ al año.",
        "🌳 Un árbol adulto puede absorber hasta 150 kg de CO₂ al año.",
    ]
    await ctx.send(random.choice(datos))

@bot.command()
async def quiz(ctx):
    pregunta, respuesta = random.choice(list(preguntas.items()))
    await ctx.send(f"❓ {pregunta}")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=20)
        if msg.content.strip().lower() == respuesta.lower():
            # Actualizar puntos y verificar insignias
            new_points = update_user_points(ctx.author.id, 5)
            new_badges = check_and_award_badges(ctx.author.id, new_points)
            
            message = "✅ ¡Correcto! Eres un verdadero guardián del planeta 🌍. ¡Ganaste 5 puntos!"
            if new_badges:
                message += "\n🎉 ¡Felicidades! Has desbloqueado nuevas insignias:\n"
                for badge in new_badges:
                    message += f"   - {badge}\n"
                message += "Usa `!insignias` para ver todas tus insignias."
                
            await ctx.send(message)
        else:
            await ctx.send(f"❌ Incorrecto. La respuesta correcta era: **{respuesta}**")
    except:
        await ctx.send("⌛ Se acabó el tiempo... intenta de nuevo con `!quiz`.")

retos = [
    "🚶‍♂️ Camina al menos 15 minutos en vez de usar transporte.",
    "💧 Cierra el caño mientras te cepillas los dientes.",
    "♻️ Separa la basura de hoy en reciclables y no reciclables.",
    "📦 Reutiliza una caja de cartón para guardar algo en casa.",
    "🌳 Planta una semilla o cuida una planta de tu casa.",
    "🥤 Usa un vaso o botella reutilizable en vez de descartables.",
    "🔌 Desenchufa los aparatos que no uses durante el día.",
    "🛍️ Lleva tu propia bolsa de tela si vas a comprar.",
    "🌍 Habla con alguien sobre un hábito ecológico sencillo.",
    "🍎 No desperdicies comida: guarda o comparte lo que sobre."
]

ultimo_reto = {}

@bot.command()
async def reto(ctx):
    hoy = datetime.date.today()
    user = ctx.author.id

    if user in ultimo_reto and ultimo_reto[user]["fecha"] == hoy:
        await ctx.send("🌱 Ya tienes un reto para hoy. ¡Intenta cumplirlo antes de pedir otro mañana! 🌍")
        return

    reto = random.choice(retos)
    ultimo_reto[user] = {"fecha": hoy, "reto": reto, "cumplido": False}
    await ctx.send(f"✨ Tu reto ecológico de hoy es:\n**{reto}**")

@bot.command()
async def cumpli(ctx):
    user = ctx.author
    hoy = datetime.date.today()
    
    if user.id in ultimo_reto and ultimo_reto[user.id]["fecha"] == hoy and not ultimo_reto[user.id]["cumplido"]:
        # Actualizar puntos y verificar insignias
        new_points = update_user_points(user.id, 10)
        new_badges = check_and_award_badges(user.id, new_points)
        
        ultimo_reto[user.id]["cumplido"] = True
        
        # Construir mensaje de respuesta
        message = f"✅ {user.mention} cumplió el reto y ahora tiene {new_points} eco-puntos."
        
        if new_badges:
            message += "\n🎉 ¡Felicidades! Has desbloqueado nuevas insignias:\n"
            for badge in new_badges:
                message += f"   - {badge}\n"
            message += "Usa `!insignias` para ver todas tus insignias."
        
        await ctx.send(message)
    else:
        await ctx.send("❌ No tienes un reto pendiente para hoy. Usa `!reto` para obtener uno.")

@bot.command()
async def puntos(ctx):
    user_id = ctx.author.id
    points = get_user_points(user_id)
    await ctx.send(f"🏆 {ctx.author.mention}, tienes **{points} eco-puntos**.")

@bot.command()
async def insignias(ctx):
    user_id = ctx.author.id
    badges = get_user_badges(user_id)
    points = get_user_points(user_id)
    
    if not badges:
        await ctx.send(f"{ctx.author.mention}, aún no has obtenido ninguna insignia. ¡Gana más puntos para desbloquearlas!\nTienes {points} de 50 puntos necesarios para la primera insignia.")
        return
    
    message = f"🏅 **Insignias de {ctx.author.name}** 🏅\n"
    for badge_name, unlocked_date in badges:
        message += f"- {badge_name} (Obtenida el {unlocked_date})\n"
    
    # Mostrar progreso hacia la próxima insignia
    badge_milestones = [50, 100, 250, 500, 1000]
    next_milestone = next((m for m in badge_milestones if m > points), None)
    
    if next_milestone:
        progress = points / next_milestone * 100
        message += f"\n📈 Progreso hacia la próxima insignia: {progress:.1f}% ({points}/{next_milestone} puntos)"
    
    await ctx.send(message)

@bot.command()
async def ranking(ctx):
    conn = sqlite3.connect('green_hero.db')
    c = conn.cursor()
    c.execute("SELECT user_id, points FROM users ORDER BY points DESC LIMIT 10")
    top = c.fetchall()
    conn.close()
    
    if not top:
        await ctx.send("📊 Aún no hay eco-puntos registrados.")
        return

    mensaje = "🌟 **Ranking de Guardianes del Planeta** 🌟\n"
    for i, (user_id, points) in enumerate(top, start=1):
        user = await bot.fetch_user(user_id)
        mensaje += f"{i}. {user.name} → {points} puntos\n"

    await ctx.send(mensaje)
bot.run("BOT TOKEN")
