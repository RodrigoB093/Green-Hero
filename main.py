import discord
from discord.ext import commands
import random
import os
import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

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
            await ctx.send("✅ ¡Correcto! Eres un verdadero guardián del planeta 🌍")
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
eco_puntos = {}  # 🔥 Cambiado de 'puntos' a 'eco_puntos'

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
    # 🔥 Usar el nuevo nombre del diccionario
    eco_puntos[user.id] = eco_puntos.get(user.id, 0) + 10
    await ctx.send(f"✅ {user.mention} cumplió el reto y ahora tiene {eco_puntos[user.id]} eco-puntos.")

@bot.command()
async def puntos(ctx):
    user = ctx.author.id
    # 🔥 Usar el nuevo nombre del diccionario
    total = eco_puntos.get(user, 0)
    await ctx.send(f"🏆 {ctx.author.mention}, tienes **{total} eco-puntos** acumulados.")

@bot.command()
async def ranking(ctx):
    # 🔥 Usar el nuevo nombre del diccionario
    if not eco_puntos:
        await ctx.send("📊 Aún no hay eco-puntos registrados.")
        return

    # 🔥 Usar el nuevo nombre del diccionario
    top = sorted(eco_puntos.items(), key=lambda x: x[1], reverse=True)
    mensaje = "🌟 **Ranking de Guardianes del Planeta** 🌟\n"
    for i, (user_id, score) in enumerate(top[:10], start=1):
        user = await bot.fetch_user(user_id)
        mensaje += f"{i}. {user.name} → {score} eco-puntos\n"

    await ctx.send(mensaje)
bot.run("BOT TOKEN")
