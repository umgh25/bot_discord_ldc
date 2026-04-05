import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Configuration Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
GUILD_ID = os.getenv('GUILD_ID')
ENV = os.getenv('ENV', 'prod').lower()

# Configuration Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Tables de la base de données
VOTES_TABLE = "votes"
POINTS_TABLE = "points"
LEADERBOARD_TABLE = "leaderboard"
SETTINGS_TABLE = "settings"

# Définir les phases de la compétition (phases passées conservées pour l'historique des votes)
MATCHES_PHASES = {
    "8e_finale_aller": {
        1: ("Galatasaray", "Liverpool"),
        2: ("Newcastle", "Barcelone"),
        3: ("Atlético Madrid", "Tottenham"),
        4: ("Atalanta", "Bayern"),
        5: ("Leverkusen", "Arsenal"),
        6: ("Paris-SG", "Chelsea"),
        7: ("Bodø/Glimt", "Sporting"),
        8: ("Real Madrid", "Manchester City"),
    },
    "quart_finale_aller": {
        # Manche 1 sur 2 — Mar. 07/04 & Mer. 08/04, 21:00
        9: ("Real Madrid", "Bayern"),
        10: ("Sporting", "Arsenal"),
        11: ("Barcelone", "Atlético Madrid"),
        12: ("Paris-SG", "Liverpool"),
    },
}

# Phase active pour les votes et la liste des matchs
ACTIVE_MATCH_PHASE = "quart_finale_aller"
MATCHES = MATCHES_PHASES.get(ACTIVE_MATCH_PHASE, {})

# Vérification des variables obligatoires
def validate_config():
    """Valide la configuration et lève une exception si des variables critiques sont manquantes"""
    if not DISCORD_TOKEN:
        raise ValueError("❌ Le token Discord n'est pas défini dans le fichier .env")
    # Vérification du channel_id
    if not CHANNEL_ID:
        raise ValueError("❌ Le CHANNEL_ID n'est pas défini dans le fichier .env")
    # Vérification des variables Supabase
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("❌ Les variables Supabase ne sont pas définies dans le fichier .env")

# Log en mode développement uniquement
def log_dev(message: str):
    """Affiche un message de log uniquement en mode développement"""
    if ENV == 'dev':
        print(f"[DEV LOG] {message}") 