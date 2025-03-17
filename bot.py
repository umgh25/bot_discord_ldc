import discord
from discord import app_commands
from database import *  # Importe toutes les fonctions de database.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
TOKEN = os.getenv('DISCORD_TOKEN')

# Configuration des intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Liste des matchs
matches = {
    1: ("Club Bruges", "Aston Villa"),
    2: ("Real Madrid", "Atlético Madrid"),
    3: ("PSV Eindhoven", "Arsenal"),
    4: ("Borussia Dortmund", "Lille"),
    5: ("Feyenoord", "Inter Milan"),
    6: ("Benfica", "FC Barcelone"),
    7: ("Bayern Munich", "Bayer Leverkusen"),
    8: ("Paris Saint-Germain", "Liverpool")
}

# Création du client
class ChampionsBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

client = ChampionsBot()

@client.event
async def on_ready():
    print(f'Bot connecté en tant que {client.user}')
    try:
        print("Synchronisation des commandes...")
        await client.tree.sync()
        print("Commandes synchronisées avec succès!")
    except Exception as e:
        print(f"Erreur lors de la synchronisation: {e}")

@client.tree.command(
    name="classement",
    description="Affiche le classement des points"
)
async def classement(interaction: discord.Interaction):
    print(f"Commande classement appelée par {interaction.user}")
    try:
        leaderboard_data = get_leaderboard()
        
        if not leaderboard_data:
            await interaction.response.send_message("❌ Aucun point n'a encore été attribué.")
            return
        
        message = "**🏆 CLASSEMENT GÉNÉRAL 🏆**\n\n"
        
        for index, entry in enumerate(leaderboard_data, 1):
            user_id = entry['user_id']
            points = entry['points']
            
            try:
                user = await client.fetch_user(int(user_id))
                username = user.name
            except:
                username = f"Utilisateur_{user_id}"
            
            medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else "👤"
            message += f"{medal} **{username}** : {points} point(s)\n"
        
        await interaction.response.send_message(message)
        
    except Exception as e:
        print(f"Erreur dans la commande classement: {e}")
        await interaction.response.send_message(
            "❌ Une erreur s'est produite lors de la récupération du classement.",
            ephemeral=True
        )

@client.tree.command(
    name="help_vote",
    description="Affiche l'aide pour les votes"
)
async def help_vote(interaction: discord.Interaction):
    help_message = """**🎮 GUIDE DES COMMANDES 🎮**

**📝 Commandes principales :**
`/vote <numéro du match> <nom de l'équipe>`
└─ Pour voter pour une équipe
└─ Exemple : `/vote 1 Club Bruges`

`/modifier_vote <numéro du match> <nom de l'équipe>`
└─ Pour modifier un vote existant
└─ Exemple : `/modifier_vote 1 Aston Villa`

`/supprimer_vote <numéro du match>`
└─ Pour supprimer un de vos votes
└─ Exemple : `/supprimer_vote 1`

**📊 Commandes de consultation :**
`/recap`
└─ Voir tous vos votes

`/voir_votes @utilisateur`
└─ Voir les votes d'un autre utilisateur
└─ Exemple : `/voir_votes @Pierre`

`/classement`
└─ Voir le classement général des points

**📋 Liste des matchs disponibles :**"""

    # Ajouter la liste des matchs
    for match_id, match in matches.items():
        team1, team2 = match
        help_message += f"\n**Match {match_id}** : {team1} vs {team2}"

    await interaction.response.send_message(help_message)

# Lancement du bot
if __name__ == "__main__":
    print("Démarrage du bot...")
    client.run(TOKEN)

