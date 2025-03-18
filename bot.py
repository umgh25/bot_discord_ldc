import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from database import *

# Configuration
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Liste des matchs
matches = {
    1: ("Club Bruges", "Aston Villa"),
    2: ("Real Madrid", "Atlético Madrid"),
    3: ("PSV Eindhoven", "Arsenal"),
    4: ("Borussia Dortmund", "Lille"),
    5: ("Feyenoord", "Inter Milan"),
    6: ("Benfica", "FC Barcelone"),
    7: ("Bayern Munich", "Bayer Leverkusen"),
    8: ("Paris Saint-Germain", "Liverpool")
}

# Création du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Stockage des matches comme variable globale du bot
bot.matches = matches

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté et prêt !')

# Chargement des commandes
async def load_extensions():
    try:
        await bot.load_extension("commands.info_commands")
        await bot.load_extension("commands.admin_commands")
        print("Extensions chargées avec succès")
    except Exception as e:
        print(f"Erreur lors du chargement des extensions: {e}")

# Lancement du bot
async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())