import json
from database import init_database, save_vote

def migrate_votes():
    # Initialiser la base de données
    init_database()
    
    # Lire les votes depuis le fichier JSON
    try:
        with open('votes.json', 'r') as f:
            votes = json.load(f)
            
        # Migrer chaque vote vers la base de données
        for user_id, user_votes in votes.items():
            for match_id, team in user_votes.items():
                success = save_vote(user_id, match_id, team)
                if success:
                    print(f"Vote migré : Utilisateur {user_id}, Match {match_id}, Équipe {team}")
                else:
                    print(f"Erreur lors de la migration du vote : Utilisateur {user_id}, Match {match_id}")
                    
        print("\nMigration terminée avec succès!")
        
    except Exception as e:
        print(f"Erreur lors de la migration : {e}")

if __name__ == "__main__":
    migrate_votes() 