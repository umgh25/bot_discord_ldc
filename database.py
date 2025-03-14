import os
from supabase import create_client

# Configuration Supabase avec plus de logs
print("Initialisation de Supabase...")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
print(f"URL configurée: {SUPABASE_URL[:30]}...") # Affiche le début de l'URL pour vérification
print(f"Clé configurée: {SUPABASE_KEY[:20]}...") # Affiche le début de la clé pour vérification

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
        print(f"=== DÉBUT SAUVEGARDE VOTE ===")
        print(f"User ID: {user_id}")
        print(f"Match ID: {match_id}")
        print(f"Choice: {choice}")
        
        # 1. D'abord, supprimer tout vote existant pour cet utilisateur et ce match
        supabase.table("votes").delete().eq("user_id", user_id).eq("match_id", match_id).execute()
        
        # 2. Ensuite, insérer le nouveau vote
        result = supabase.table("votes").insert({
            "user_id": user_id,
            "match_id": match_id,
            "choice": choice
        }).execute()
        
        print(f"Vote enregistré avec succès")
        print("=== FIN SAUVEGARDE VOTE ===")
        return True
        
    except Exception as e:
        print(f"!!! ERREUR SAUVEGARDE VOTE !!!")
        print(f"Type d'erreur: {type(e)}")
        print(f"Message d'erreur: {str(e)}")
        print("=== FIN ERREUR ===")
        return False

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
def add_points(user_id: str, match_id: int, points: int) -> bool:
    try:
        print(f"=== DÉBUT AJOUT POINTS DANS LA BDD ===")
        
        # Supprimer d'abord tout enregistrement existant
        supabase.table("points") \
            .delete() \
            .eq("user_id", str(user_id)) \
            .eq("match_id", int(match_id)) \
            .execute()
        
        # Puis insérer le nouveau
        result = supabase.table("points") \
            .insert({
                "user_id": str(user_id),
                "match_id": int(match_id),
                "points": int(points)
            }).execute()
        
        print(f"Résultat de l'opération: {result.data if hasattr(result, 'data') else result}")
        print("=== FIN AJOUT POINTS DANS LA BDD ===")
        return True
        
    except Exception as e:
        print(f"!!! ERREUR DANS ADD_POINTS !!!")
        print(f"Type d'erreur: {type(e)}")
        print(f"Message d'erreur: {str(e)}")
        print("=== FIN ERREUR ===")
        return False

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