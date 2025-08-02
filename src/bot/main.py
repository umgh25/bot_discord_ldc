import discord
from discord.ext import commands
import sys
sys.path.append('../../config')
sys.path.append('../database')
sys.path.append('./commands')
sys.path.append('./utils')

from config.settings import DISCORD_TOKEN, CHANNEL_ID, validate_config, log_dev
from src.database.operations import supabase
from .commands.vote import setup_vote_commands
from .commands.info import setup_info_commands
from .commands.admin import setup_admin_commands

# Créer les intents nécessaires
intents = discord.Intents.default()
# Pour pouvoir lire le contenu des messages (important pour les commandes)
intents.message_content = True

# Créer l'instance du bot avec les intents
bot = commands.Bot(command_prefix="!", intents=intents)

def setup_bot():
    """Configure le bot avec toutes les commandes"""
    # Configurer les commandes
    setup_vote_commands(bot)
    setup_info_commands(bot)
    setup_admin_commands(bot)

# Événement quand le bot est prêt
@bot.event
async def on_ready():
    print(f'{bot.user} est connecté et prêt !')
    print(f'Canal restreint : {CHANNEL_ID}')
    try:
        channel = bot.get_channel(int(CHANNEL_ID))
        if channel:
            print(f"Canal trouvé : #{channel.name}")
        else:
            print("⚠️ ATTENTION : Le canal spécifié n'a pas été trouvé !")
        synced = await bot.tree.sync()
        print(f"Slash commands synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des slash commands : {e}")

# Pour les commandes normales, ajouter un event listener
@bot.event
async def on_command(ctx):
    if str(ctx.channel.id) != CHANNEL_ID:
        await ctx.send(f"❌ Cette commande ne peut être utilisée que dans le canal <#{CHANNEL_ID}>")
        raise commands.CommandError("Mauvais canal")

def run_bot():
    """Lance le bot avec la configuration appropriée"""
    # Valider la configuration
    validate_config()
    
    # Log en mode développement uniquement
    log_dev("✅ Token Discord chargé.")
    log_dev(f"Longueur : {len(DISCORD_TOKEN)}")
    log_dev(f"Début : {DISCORD_TOKEN[:10]}...")
    log_dev("✅ CHANNEL_ID chargé.")
    
    # Configurer le bot
    setup_bot()
    
    # Lancer le bot
    bot.run(DISCORD_TOKEN) 