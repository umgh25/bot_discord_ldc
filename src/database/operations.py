import sys
sys.path.append('../../config')
from config.settings import VOTES_TABLE, POINTS_TABLE, LEADERBOARD_TABLE, SETTINGS_TABLE
from .models import supabase, DatabaseLogger, handle_db_errors, upsert_record, count_records

# =============================================================================
# FONCTIONS DE BASE DE DONNÉES
# =============================================================================

@handle_db_errors()
def create_db():
    """Vérifier la connexion à Supabase"""
    # Cette fonction vérifie simplement la connexion
    # Les tables sont créées via l'interface Supabase ou avec des requêtes SQL
    supabase.table(VOTES_TABLE).select("*").limit(1).execute()
    print("Connexion à Supabase réussie")

@handle_db_errors(default_return=False)
def save_vote(user_id, match_id, choice):
    """Sauvegarde un vote en remplaçant l'ancien s'il existe"""
    DatabaseLogger.log_function_start("SAUVEGARDE VOTE")
    DatabaseLogger.log_data_received(user_id, match_id, Choice=choice)
    
    # 1. D'abord, supprimer tout vote existant pour cet utilisateur et ce match
    supabase.table(VOTES_TABLE).delete().eq("user_id", user_id).eq("match_id", match_id).execute()
    
    # 2. Ensuite, insérer le nouveau vote
    result = supabase.table(VOTES_TABLE).insert({
        "user_id": user_id,
        "match_id": match_id,
        "choice": choice
    }).execute()
    
    print(f"Vote enregistré avec succès")
    DatabaseLogger.log_function_end("SAUVEGARDE VOTE")
    return True

@handle_db_errors(default_return=[])
def get_votes(match_id):
    """Récupère les votes d'un match spécifique"""
    result = supabase.table(VOTES_TABLE).select("user_id, choice").eq("match_id", match_id).execute()
    # Convertir le résultat en format similaire à SQLite (liste de tuples)
    return [(item["user_id"], item["choice"]) for item in result.data]

@handle_db_errors(default_return=False)
def update_leaderboard(user_id: str) -> bool:
    """Met à jour le leaderboard pour un utilisateur"""
    DatabaseLogger.log_function_start(f"MISE À JOUR LEADERBOARD POUR {user_id}")
    
    # Calculer le total des points pour cet utilisateur
    points_result = supabase.table(POINTS_TABLE).select("points").eq("user_id", user_id).execute()
    total_points = sum(entry['points'] for entry in points_result.data) if points_result.data else 0
    
    print(f"Total des points calculé: {total_points}")
    
    # Insérer ou mettre à jour le leaderboard
    upsert_record(
        table=LEADERBOARD_TABLE,
        data={"points": total_points},
        conditions={"user_id": user_id}
    )
    
    print(f"Leaderboard mis à jour pour {user_id} avec {total_points} points")
    DatabaseLogger.log_function_end("MISE À JOUR LEADERBOARD")
    return True

@handle_db_errors(default_return=False)
def add_points(user_id: str, match_id: int, points: int) -> bool:
    """Ajoute ou met à jour les points d'un utilisateur pour un match"""
    DatabaseLogger.log_function_start("AJOUT POINTS DANS LA BDD")
    DatabaseLogger.log_data_received(user_id, match_id, Points=points)
    
    # Insérer ou mettre à jour les points
    upsert_record(
        table=POINTS_TABLE,
        data={
            "user_id": str(user_id),
            "match_id": int(match_id),
            "points": int(points)
        },
        conditions={"user_id": user_id, "match_id": match_id}
    )
    
    # Mettre à jour le leaderboard
    update_leaderboard(user_id)
    
    DatabaseLogger.log_function_end("AJOUT POINTS DANS LA BDD")
    return True

@handle_db_errors(default_return=[])
def get_leaderboard():
    """Récupère le classement général"""
    DatabaseLogger.log_function_start("RÉCUPÉRATION CLASSEMENT")
    
    # Récupérer directement depuis la table leaderboard, triée par points décroissants
    result = supabase.table(LEADERBOARD_TABLE).select("*").order("points", desc=True).execute()
    
    print(f"Résultat du classement: {result.data if hasattr(result, 'data') else result}")
    DatabaseLogger.log_function_end("RÉCUPÉRATION CLASSEMENT")
    return result.data if result.data else []

@handle_db_errors()
def set_channel(channel_id):
    """Enregistre l'ID du canal de votes"""
    # INSERT OR REPLACE équivalent dans Supabase
    supabase.table(SETTINGS_TABLE).upsert({"id": 1, "channel_id": channel_id}).execute()

@handle_db_errors(default_return=None)
def get_channel():
    """Récupère l'ID du canal de votes"""
    result = supabase.table(SETTINGS_TABLE).select("channel_id").eq("id", 1).execute()
    if result.data and len(result.data) > 0:
        return result.data[0]["channel_id"]
    return None

@handle_db_errors(default_return=(False, 0))
def reset_points(user_id: str = None) -> tuple[bool, int]:
    """Réinitialise les points d'un utilisateur ou de tous les utilisateurs"""
    DatabaseLogger.log_function_start("RESET POINTS")
    
    if user_id:
        print(f"Réinitialisation des points pour l'utilisateur: {user_id}")
        # Compter les points à supprimer
        points_count = count_records(POINTS_TABLE, {"user_id": user_id})
        
        if points_count == 0:
            print("Aucun point trouvé pour cet utilisateur")
            return True, 0
            
        # Supprimer les points
        supabase.table(POINTS_TABLE).delete().eq("user_id", user_id).execute()
        # Mettre à jour le leaderboard
        update_leaderboard(user_id)
        
        print(f"Nombre de points supprimés: {points_count}")
        
    else:
        print("Réinitialisation de tous les points")
        # Compter le total des points
        points_count = count_records(POINTS_TABLE)
        
        if points_count == 0:
            print("Aucun point trouvé dans la base de données")
            return True, 0
            
        # Supprimer tous les points
        supabase.table(POINTS_TABLE).delete().neq("user_id", "dummy").execute()
        # Vider le leaderboard
        supabase.table(LEADERBOARD_TABLE).delete().neq("user_id", "dummy").execute()
        
        print(f"Nombre total de points supprimés: {points_count}")
    
    DatabaseLogger.log_function_end("RESET POINTS")
    return True, points_count

# Vérification de la connexion au démarrage
create_db() 