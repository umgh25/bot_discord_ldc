import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Configuration Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
ENV = os.getenv('ENV', 'prod').lower()

# Configuration Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Tables de la base de données
VOTES_TABLE = "votes"
POINTS_TABLE = "points"
LEADERBOARD_TABLE = "leaderboard"
SETTINGS_TABLE = "settings"

# Définir les phases de la compétition
MATCHES_PHASES = {
    "finale": {
        15: ("Club Bruges", "Aston Villa")
    }
}

# Pour les commandes actives, n'utiliser que les matchs actuels
MATCHES = MATCHES_PHASES.get("finale", {})

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