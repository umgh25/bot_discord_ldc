import os
from supabase import create_client
from functools import wraps
import sys
sys.path.append('../../config')
from config.settings import SUPABASE_URL, SUPABASE_KEY

# Configuration Supabase avec plus de logs
print("Initialisation de Supabase...")
print(f"URL configurée: {SUPABASE_URL[:30]}...") if SUPABASE_URL else print("URL non configurée")
print(f"Clé configurée: {SUPABASE_KEY[:20]}...") if SUPABASE_KEY else print("Clé non configurée")

# Initialisation du client Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
# Classe pour centraliser les logs de base de données
class DatabaseLogger:
    """Classe pour centraliser les logs de base de données"""
    
    @staticmethod
    def log_function_start(func_name: str):
        print(f"=== DÉBUT {func_name.upper()} ===")
    
    @staticmethod
    def log_function_end(func_name: str):
        print(f"=== FIN {func_name.upper()} ===")
    
    @staticmethod
    def log_error(func_name: str, error: Exception):
        print(f"!!! ERREUR DANS {func_name.upper()} !!!")
        print(f"Type d'erreur: {type(error)}")
        print(f"Message d'erreur: {str(error)}")
        print("=== FIN ERREUR ===")
    
    @staticmethod
    def log_data_received(user_id: str, match_id: int, **kwargs):
        print(f"User ID: {user_id}")
        print(f"Match ID: {match_id}")
        for key, value in kwargs.items():
            print(f"- {key}: {value}")
# Décorateur pour gérer les erreurs de base de données de manière uniforme
def handle_db_errors(default_return=None):
    """Décorateur pour gérer les erreurs de base de données de manière uniforme"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                DatabaseLogger.log_error(func.__name__, e)
                return default_return
        return wrapper
    return decorator
# Fonction pour insérer ou mettre à jour un enregistrement dans une table
def upsert_record(table: str, data: dict, conditions: dict):
    """Insère ou met à jour un enregistrement dans une table"""
    existing = supabase.table(table).select("*").eq(**conditions).execute()
    if existing.data:
        return supabase.table(table).update(data).eq(**conditions).execute()
    else:
        return supabase.table(table).insert(data).execute()
# Fonction pour compter les enregistrements dans une table avec conditions optionnelles
def count_records(table: str, conditions: dict = None):
    """Compte les enregistrements dans une table avec conditions optionnelles"""
    query = supabase.table(table).select("*", count="exact")
    if conditions:
        for key, value in conditions.items():
            query = query.eq(key, value)
    result = query.execute()
    return len(result.data) if result.data else 0 