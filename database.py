import os
from supabase import create_client

# Configuration Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialisation du client Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_db():
    # Vérifier la connexion à Supabase
    try:
        # Cette fonction vérifie simplement la connexion
        # Les tables sont créées via l'interface Supabase ou avec des requêtes SQL
        supabase.table("votes").select("*").limit(1).execute()
        print("Connexion à Supabase réussie")
    except Exception as e:
        print(f"Erreur de connexion à Supabase: {e}")
        # Vous pouvez créer les tables ici si nécessaire avec des requêtes SQL
        # supabase.query("CREATE TABLE IF NOT EXISTS votes...")

def save_vote(user_id, match_id, choice):
    try:
        # INSERT OR REPLACE équivalent dans Supabase
        # Nous utilisons upsert qui fait INSERT si n'existe pas, UPDATE si existe
        supabase.table("votes").upsert({
            "user_id": user_id, 
            "match_id": match_id, 
            "choice": choice
        }).execute()
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du vote: {e}")

# Fonction pour récupérer les votes d'un match
def get_votes(match_id):
    try:
        result = supabase.table("votes").select("user_id, choice").eq("match_id", match_id).execute()
        # Convertir le résultat en format similaire à SQLite (liste de tuples)
        return [(item["user_id"], item["choice"]) for item in result.data]
    except Exception as e:
        print(f"Erreur lors de la récupération des votes: {e}")
        return []

# Fonction pour ajouter des points
def add_points(user_id, points):
    try:
        # Équivalent de ON CONFLICT DO UPDATE avec Supabase
        # D'abord, vérifier si l'utilisateur existe
        result = supabase.table("leaderboard").select("points").eq("user_id", user_id).execute()
        
        if result.data and len(result.data) > 0:
            # L'utilisateur existe, mettre à jour ses points
            current_points = result.data[0]["points"]
            supabase.table("leaderboard").update({"points": current_points + points}).eq("user_id", user_id).execute()
        else:
            # L'utilisateur n'existe pas, l'insérer
            supabase.table("leaderboard").insert({"user_id": user_id, "points": points}).execute()
    except Exception as e:
        print(f"Erreur lors de l'ajout des points: {e}")

# Fonction pour récupérer le classement
def get_leaderboard():
    try:
        result = supabase.table("leaderboard").select("user_id, points").order("points", desc=True).execute()
        # Convertir le résultat en format similaire à SQLite (liste de tuples)
        return [(item["user_id"], item["points"]) for item in result.data]
    except Exception as e:
        print(f"Erreur lors de la récupération du classement: {e}")
        return []

# Fonction pour enregistrer le canal de votes
def set_channel(channel_id):
    try:
        # INSERT OR REPLACE équivalent dans Supabase
        supabase.table("settings").upsert({"id": 1, "channel_id": channel_id}).execute()
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du canal: {e}")

# Fonction pour récupérer l'ID du canal de votes
def get_channel():
    try:
        result = supabase.table("settings").select("channel_id").eq("id", 1).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]["channel_id"]
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération du canal: {e}")
        return None

# Vérification de la connexion au démarrage
create_db()