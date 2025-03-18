import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
from keep_alive import keep_alive
from database import *
import asyncio

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Obtenir le chemin absolu du fichier .env
env_path = Path('.') / '.env'

# Charger les variables d'environnement
load_dotenv(dotenv_path=env_path)

# Récupérer le token
TOKEN = os.getenv('DISCORD_TOKEN')
logger.info(f"Token trouvé : {'Oui' if TOKEN else 'Non'}")
logger.info(f"Longueur du token : {len(TOKEN) if TOKEN else 0}")
logger.info(f"Début du token : {TOKEN[:10]}... (pour vérification)")

if not TOKEN:
    raise ValueError("Le token Discord n'est pas configuré")

# Créer les intents nécessaires
intents = discord.Intents.default()
intents.message_content = True

# Créer l'instance du bot avec les intents
bot = commands.Bot(command_prefix="!", intents=intents)

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

# Verrous pour éviter les opérations simultanées
vote_locks = {}

@bot.event
async def on_ready():
    logger.info(f'{bot.user} est connecté et prêt !')
    try:
        # Synchroniser les commandes avec Discord
        synced = await bot.tree.sync()
        logger.info(f'Commandes slash synchronisées : {len(synced)}')
    except Exception as e:
        logger.error(f'Erreur lors de la synchronisation des commandes : {e}')

# Importer les commandes à partir d'autres fichiers
from commands.vote_commands import setup as setup_vote_commands
from commands.info_commands import setup as setup_info_commands
from commands.admin_commands import setup as setup_admin_commands

# Configurer les commandes
setup_vote_commands(bot, matches, vote_locks)
setup_info_commands(bot, matches)
setup_admin_commands(bot, matches)

keep_alive()

# Lancement du bot avec le token
bot.run(TOKEN)