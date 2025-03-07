import sqlite3
import json
import os

# Définir le chemin de la base de données
DB_PATH = os.path.join(os.getenv('RENDER_DB_PATH', '.'), 'bot_database.db')
VOTES_FILE = 'votes.json'

def migrate_json_to_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Charger les votes depuis le fichier JSON
        print("Lecture du fichier votes.json...")
        with open(VOTES_FILE, 'r', encoding='utf-8') as f:
            votes_data = json.load(f)
            print(f"Nombre d'utilisateurs trouvés : {len(votes_data)}")

        # Pour chaque utilisateur et ses votes
        for user_id, user_votes in votes_data.items():
            print(f"Migration des votes pour l'utilisateur {user_id}")
            for match_id, choice in user_votes.items():
                # Insérer dans la base de données
                c.execute('''INSERT OR REPLACE INTO votes (user_id, match_id, choice) 
                           VALUES (?, ?, ?)''', (user_id, match_id, choice))
                print(f"Vote migré : Match {match_id}, Choix {choice}")

        conn.commit()
        print("Migration terminée avec succès!")
        
        # Vérifier les données migrées
        c.execute('''SELECT COUNT(*) FROM votes''')
        count = c.fetchone()[0]
        print(f"Nombre total de votes dans la base de données : {count}")
        
    except Exception as e:
        print(f"Erreur pendant la migration : {e}")
        conn.rollback()
        print("Rollback effectué - Aucune donnée n'a été perdue")
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("Début de la migration des votes JSON vers SQLite...")
    migrate_json_to_db() 