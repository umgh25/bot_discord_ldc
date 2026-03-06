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
    "8e_finale_aller": {
        # Manche 1 sur 2 - Mar. 10/03
        1: ("Galatasaray", "Liverpool"),          # Mar. 10/03 18:45
        2: ("Newcastle", "Barcelone"),            # Mar. 10/03 21:00
        3: ("Atlético Madrid", "Tottenham"),      # Mar. 10/03 21:00
        4: ("Atalanta", "Bayern"),                # Mar. 10/03 21:00
        # Manche 1 sur 2 - Mer. 11/03
        5: ("Leverkusen", "Arsenal"),             # Mer. 11/03 18:45
        6: ("Paris-SG", "Chelsea"),               # Mer. 11/03 21:00
        7: ("Bodø/Glimt", "Sporting"),            # Mer. 11/03 21:00
        8: ("Real Madrid", "Manchester City"),    # Mer. 11/03 21:00
    }
}

# Pour les commandes actives, utiliser les 8èmes de finale aller
MATCHES = MATCHES_PHASES.get("8e_finale_aller", {})

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