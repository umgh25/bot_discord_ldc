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
        print(f"Données reçues:")
        print(f"- User ID: {user_id}")
        print(f"- Match ID: {match_id}")
        print(f"- Points: {points}")
        
        # Vérifier si des points existent déjà pour cet utilisateur et ce match
        existing = supabase.table("points").select("*").eq("user_id", user_id).eq("match_id", match_id).execute()
        
        if existing.data:
            # Si des points existent déjà, on les met à jour
            print("Points existants trouvés, mise à jour...")
            result = supabase.table("points").update({
                "points": int(points)
            }).eq("user_id", user_id).eq("match_id", match_id).execute()
        else:
            # Si pas de points existants, on en crée
            print("Pas de points existants, création...")
            result = supabase.table("points").insert({
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

# Fonction pour réinitialiser les points
def reset_points(user_id: str = None) -> tuple[bool, int]:
    try:
        print(f"=== DÉBUT RESET POINTS ===")
        
        if user_id:
            print(f"Réinitialisation des points pour l'utilisateur: {user_id}")
            # D'abord, compter combien de points vont être supprimés
            count_result = supabase.table("points").select("*", count="exact").eq("user_id", user_id).execute()
            points_count = len(count_result.data) if count_result.data else 0
            
            if points_count == 0:
                print("Aucun point trouvé pour cet utilisateur")
                return True, 0
                
            # Supprimer les points
            result = supabase.table("points").delete().eq("user_id", user_id).execute()
            print(f"Nombre de points supprimés: {points_count}")
            
        else:
            print("Réinitialisation de tous les points")
            # Compter d'abord le total des points
            count_result = supabase.table("points").select("*", count="exact").execute()
            points_count = len(count_result.data) if count_result.data else 0
            
            if points_count == 0:
                print("Aucun point trouvé dans la base de données")
                return True, 0
                
            # Supprimer tous les points
            result = supabase.table("points").delete().neq("user_id", "dummy").execute()
            print(f"Nombre total de points supprimés: {points_count}")
        
        print("=== FIN RESET POINTS ===")
        return True, points_count
        
    except Exception as e:
        print(f"!!! ERREUR DANS RESET_POINTS !!!")
        print(f"Type d'erreur: {type(e)}")
        print(f"Message d'erreur: {str(e)}")
        print("=== FIN ERREUR ===")
        return False, 0

# Vérification de la connexion au démarrage
create_db()