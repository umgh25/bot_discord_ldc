import json
import os
from database import init_database, save_vote, create_connection

def migrate_votes():
    # Initialiser la base de données
    init_database()
    
    # Lire les votes depuis le fichier JSON
    try:
        with open('votes.json', 'r') as f:
            votes = json.load(f)
            
        # Vérifier si on est sur Render
        db_path = '/data/bot_database.db' if os.path.exists('/data') else 'bot_database.db'
        print(f"Utilisation de la base de données : {db_path}")
            
        # Migrer chaque vote vers la base de données
        for user_id, user_votes in votes.items():
            print(f"\nMigration des votes pour l'utilisateur {user_id}")
            for match_id, team in user_votes.items():
                success = save_vote(user_id, match_id, team)
                if success:
                    print(f"✅ Vote migré : Match {match_id}, Équipe {team}")
                else:
                    print(f"❌ Erreur : Match {match_id}, Équipe {team}")
                    
        print("\nMigration terminée!")
        
        # Vérifier le contenu après migration
        conn = create_connection()
        if conn:
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM votes')
            count = c.fetchone()[0]
            print(f"\nNombre total de votes dans la base : {count}")
            conn.close()
        
    except Exception as e:
        print(f"Erreur lors de la migration : {e}")

if __name__ == "__main__":
    migrate_votes() 