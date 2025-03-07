import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from keep_alive import keep_alive
from database import save_vote, get_votes, get_leaderboard, add_points
import sqlite3

# Obtenir le chemin absolu du fichier .env
env_path = Path('.') / '.env'

# Charger les variables d'environnement
load_dotenv(dotenv_path=env_path)

# Récupérer le token
TOKEN = os.getenv('DISCORD_TOKEN')
print(f"Token trouvé : {'Oui' if TOKEN else 'Non'}")
print(f"Longueur du token : {len(TOKEN) if TOKEN else 0}")
print(f"Début du token : {TOKEN[:10]}... (pour vérification)")

if not TOKEN:
    raise ValueError("Le token Discord n'est pas configuré")

# Fichier où stocker les votes
VOTES_FILE = "votes.json"

# Structure pour stocker les points
POINTS_FILE = "points.json"

# Charger les votes depuis le fichier (s'il existe)


def charger_votes():
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Sauvegarder les votes dans le fichier JSON


def sauvegarder_votes():
    with open(VOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(votes, f, indent=4)

# Charger les points depuis le fichier (s'il existe)


def charger_points():
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Sauvegarder les points dans le fichier JSON


def sauvegarder_points():
    with open(POINTS_FILE, "w", encoding="utf-8") as f:
        json.dump(points, f, indent=4)


# Charger les votes au démarrage
votes = charger_votes()

# Charger les points au démarrage
points = charger_points()

# Créer les intents nécessaires
intents = discord.Intents.default()
# Pour pouvoir lire le contenu des messages (important pour les commandes)
intents.message_content = True

# Créer l'instance du bot avec les intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Liste des matchs
matches = {
    1: {"teams": ("Club Bruges", "Aston Villa")},
    2: {"teams": ("Real Madrid", "Atlético Madrid")},
    3: {"teams": ("PSV Eindhoven", "Arsenal")},
    4: {"teams": ("Borussia Dortmund", "Lille")},
    5: {"teams": ("Feyenoord", "Inter Milan")},
    6: {"teams": ("Benfica", "FC Barcelone")},
    7: {"teams": ("Bayern Munich", "Bayer Leverkusen")},
    8: {"teams": ("Paris Saint-Germain", "Liverpool")},
}

# Événement quand le bot est prêt
@bot.event
async def on_ready():
    print(f'{bot.user} est connecté et prêt !')

# Commande d'aide pour le vote
@bot.command(name="help_vote")
async def help_vote(ctx):
    help_message = """**🎮 GUIDE DES COMMANDES 🎮**

**📝 Commandes principales :**
`!vote <numéro du match> <nom de l'équipe>`
└─ Pour voter pour une équipe
└─ Exemple : `!vote 1 Club Bruges`

`!modifier_vote <numéro du match> <nom de l'équipe>`
└─ Pour modifier un vote existant
└─ Exemple : `!modifier_vote 1 Aston Villa`

`!supprimer_vote <numéro du match>`
└─ Pour supprimer un de vos votes
└─ Exemple : `!supprimer_vote 1`

**📊 Commandes de consultation :**
`!recap`
└─ Voir tous vos votes

`!voir_votes @utilisateur`
└─ Voir les votes d'un autre utilisateur
└─ Exemple : `!voir_votes @Pierre`

`!all_votes`
└─ Voir les statistiques globales et tous les votes

**🏆 Commandes de points (Administrateurs) :**
`!point @utilisateur <numéro du match> <points>`
└─ Attribuer des points à un utilisateur
└─ Points : 1 = victoire, -1 = absence
└─ Exemple : `!point @Pierre 1 1`

`!reset_points @utilisateur`
└─ Réinitialiser les points d'un utilisateur
└─ Sans mention = réinitialise tous les points

`!classement`
└─ Voir le classement général des points
└─ Affiche le top 3 avec médailles 🥇🥈🥉

**📋 Liste des matchs disponibles :**"""

    # Ajouter la liste des matchs
    for match_id, match in matches.items():
        team1, team2 = match["teams"]
        help_message += f"\n**Match {match_id}** : {team1} vs {team2}"

    help_message += "\n\n**⚠️ Rappels importants :**"
    help_message += "\n• Vous pouvez modifier vos votes à tout moment avant le début du match"
    help_message += "\n• Les votes non effectués avant le début du match entraînent une pénalité de -1 point"
    help_message += "\n• Utilisez les noms exacts des équipes (la casse n'est pas importante)"
    help_message += "\n• Seuls les administrateurs peuvent attribuer ou réinitialiser les points"

    await ctx.send(help_message)

# Commande !vote
@bot.command(name="vote")
async def vote(ctx, match_id: str, choice: str):
    try:
        print(f"Vote reçu de {ctx.author.id} pour match {match_id}: {choice}")
        
        db_path = os.path.join(os.getenv('RENDER_DB_PATH', '.'), 'bot_database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insérer ou mettre à jour le vote
        cursor.execute('''INSERT OR REPLACE INTO votes (user_id, match_id, choice)
                         VALUES (?, ?, ?)''', (ctx.author.id, match_id, choice))
        
        conn.commit()
        print(f"Vote enregistré avec succès")
        await ctx.send(f"Vote enregistré pour le match {match_id}: {choice}")
        
    except Exception as e:
        print(f"Erreur dans vote: {str(e)}")
        await ctx.send("Une erreur s'est produite lors de l'enregistrement de votre vote.")
    finally:
        if 'conn' in locals():
            conn.close()

# Commande !supprimer_vote


@bot.command(name="supprimer_vote")
async def supprimer_vote(ctx, match_id: int):
    user_id = str(ctx.author.id)

    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    # Vérifier si le vote existe
    cursor.execute('SELECT choice FROM votes WHERE user_id = ? AND match_id = ?', 
                  (user_id, str(match_id)))
    result = cursor.fetchone()
    
    if not result:
        await ctx.send(f"❌ {ctx.author.mention}, tu n'as pas encore voté pour ce match `{match_id}`.")
        conn.close()
        return

    # Suppression du vote
    cursor.execute('DELETE FROM votes WHERE user_id = ? AND match_id = ?', 
                  (user_id, str(match_id)))
    conn.commit()
    conn.close()

    await ctx.send(f"✅ {ctx.author.mention}, ton vote pour le match `{match_id}` a été supprimé !")

# Commande !programme (Annonce du quiz)


@bot.command()
async def programme(ctx):
    message = """**Oyé, Oyé,
⚽ La Ligue des Champions reprend demain avec les huitièmes de finale ! ⚽
🔥 Les meilleurs clubs d'Europe s'affrontent pour une place en quarts de finale ! 🔥

La SARL organise son grand jeu "Road to Munich", avec des récompenses à la clé ! 🎁🏆

Trêve de bavardages, voyons ce qui nous attend !

💰 Les récompenses
Vainqueur des huitièmes et quarts de finale : Carte cadeau de 5€ 🏅
Vainqueur des demi-finales et de la finale : Carte cadeau de 5€ 🏆

Note : Les huitièmes et quarts de finale constituent une première phase, suivie des demi-finales et de la finale en seconde phase.

---

🔴 Matchs des huitièmes de finale 🔴
Aller :
Mardi 4 mars 2025 :
🕕 18h45 : Club Bruges 🇧🇪 vs. Aston Villa 🏴󠁧󠁢󠁥󠁮󠁧󠁿
🕘 21h00 : Real Madrid 🇪🇸 vs. Atlético Madrid 🇪🇸
🕘 21h00 : PSV Eindhoven 🇳🇱 vs. Arsenal 🏴󠁧󠁢󠁥󠁮󠁧󠁿
🕘 21h00 : Borussia Dortmund 🇩🇪 vs. Lille 🇫🇷

Mercredi 5 mars 2025 :
🕕 18h45 : Feyenoord 🇳🇱 vs. Inter Milan 🇮🇹
🕘 21h00 : Benfica 🇵🇹 vs. FC Barcelone 🇪🇸
🕘 21h00 : Bayern Munich 🇩🇪 vs. Bayer Leverkusen 🇩🇪
🕘 21h00 : Paris Saint-Germain 🇫🇷 vs. Liverpool 🏴󠁧󠁢󠁥󠁮󠁧󠁿

Retour :
Mardi 11 mars 2025 :
🕕 18h45 : FC Barcelone 🇪🇸 vs. Benfica 🇵🇹
🕘 21h00 : Inter Milan 🇮🇹 vs. Feyenoord 🇳🇱
🕘 21h00 : Bayer Leverkusen 🇩🇪 vs. Bayern Munich 🇩🇪
🕘 21h00 : Liverpool 🏴󠁧󠁢󠁥󠁮󠁧󠁿 vs. Paris Saint-Germain 🇫🇷

Mercredi 12 mars 2025 :
🕕 18h45 : Lille 🇫🇷 vs. Borussia Dortmund 🇩🇪
🕘 21h00 : Atlético Madrid 🇪🇸 vs. Real Madrid 🇪🇸
🕘 21h00 : Arsenal 🏴󠁧󠁢󠁥󠁮󠁧󠁿 vs. PSV Eindhoven 🇳🇱
🕘 21h00 : Aston Villa 🏴󠁧󠁢󠁥󠁮󠁧󠁿 vs. Club Bruges 🇧🇪

---
📜 Règlement du concours
Prédictions : Vous avez jusqu'au coup d'envoi du premier match de chaque confrontation pour poster vos pronostics.
Pénalité : Chaque match non pronostiqué à temps entraîne une pénalité de -1 point.

---

🚀 Préparez-vous, la SARL reprend du service ! 🚀**"""

    await ctx.send(message)

# Commande pour voir le récapitulatif des votes
@bot.command(name="recap")
async def recap(ctx):
    try:
        print(f"Commande recap appelée par {ctx.author.id}")
        
        # Utiliser le chemin correct de la base de données
        db_path = os.path.join(os.getenv('RENDER_DB_PATH', '.'), 'bot_database.db')
        print(f"Chemin de la base de données: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la table votes existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='votes'")
        if not cursor.fetchone():
            print("La table 'votes' n'existe pas!")
            await ctx.send("Erreur: La table des votes n'existe pas.")
            return
        
        # Récupérer tous les votes de l'utilisateur
        cursor.execute('SELECT match_id, choice FROM votes WHERE user_id = ?', (ctx.author.id,))
        votes = cursor.fetchall()
        print(f"Votes trouvés pour {ctx.author.id}: {votes}")
        
        if not votes:
            await ctx.send("Vous n'avez pas encore voté pour un match.")
            return
            
        recap_message = "Voici vos votes :\n"
        for match_id, choice in votes:
            recap_message += f"Match {match_id}: {choice}\n"
        
        await ctx.send(recap_message)
        
    except Exception as e:
        print(f"Erreur dans recap: {str(e)}")
        await ctx.send("Une erreur s'est produite lors de la récupération de vos votes.")
    finally:
        if 'conn' in locals():
            conn.close()

# Commande pour voir les votes d'un utilisateur spécifique
@bot.command(name="voir_votes")
async def voir_votes(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("❌ Veuillez mentionner un utilisateur. Exemple : `!voir_votes @utilisateur`")
        return

    user_id = str(member.id)
    
    # Récupérer les votes depuis la base de données
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT match_id, choice FROM votes WHERE user_id = ?', (user_id,))
    user_votes = cursor.fetchall()
    conn.close()
    
    if not user_votes:
        await ctx.send(f"❌ {member.mention} n'a pas encore voté pour aucun match.")
        return
        
    recap_message = f"**📊 Votes de {member.mention} :**\n\n"
    
    # Trier les votes par numéro de match
    sorted_votes = sorted(user_votes, key=lambda x: int(x[0]))
    
    for match_id, voted_team in sorted_votes:
        match = matches[int(match_id)]
        team1, team2 = match["teams"]
        recap_message += f"**Match {match_id}** : {team1} vs {team2}\n"
        recap_message += f"└─ Vote : **{voted_team}** ⚽\n\n"
    
    total_votes = len(user_votes)
    matches_restants = len(matches) - total_votes
    
    recap_message += f"**📈 Statistiques :**\n"
    recap_message += f"└─ Votes effectués : **{total_votes}/{len(matches)}**\n"
    recap_message += f"└─ Matches restants : **{matches_restants}**\n"

    await ctx.send(recap_message)

# Commande pour modifier un vote existant
@bot.command(name="modifier_vote")
async def modifier_vote(ctx, match_id: int = None, *, team: str = None):
    if match_id is None or team is None:
        await ctx.send("❌ Format incorrect. Utilisez `!modifier_vote <numéro du match> <nom de l'équipe>`")
        return

    user_id = str(ctx.author.id)
    
    # Vérifier si l'utilisateur a déjà voté pour ce match
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT choice FROM votes WHERE user_id = ? AND match_id = ?', (user_id, str(match_id)))
    result = cursor.fetchone()
    
    if not result:
        await ctx.send(f"❌ Vous n'avez pas encore voté pour le match {match_id}. Utilisez `!vote` pour voter.")
        conn.close()
        return

    ancien_vote = result[0]
    
    # Vérifier si le match existe
    if match_id < 1 or match_id > len(matches):
        await ctx.send(f"❌ Match {match_id} invalide. Les matchs disponibles sont de 1 à {len(matches)}.")
        conn.close()
        return

    match = matches[match_id]
    team1, team2 = match["teams"]

    # Normaliser le nom de l'équipe
    team = team.strip()
    
    if team.lower() not in [team1.lower(), team2.lower()]:
        await ctx.send(f"❌ Équipe invalide. Pour le match {match_id}, vous pouvez seulement voter pour :\n- **{team1}**\n- **{team2}**")
        conn.close()
        return

    # Si l'utilisateur vote pour la même équipe
    if team.lower() == ancien_vote.lower():
        await ctx.send(f"ℹ️ Vous avez déjà voté pour **{ancien_vote}** dans ce match.")
        conn.close()
        return

    # Trouver le nom exact de l'équipe
    if team.lower() == team1.lower():
        team = team1
    else:
        team = team2

    # Modifier le vote
    cursor.execute('UPDATE votes SET choice = ? WHERE user_id = ? AND match_id = ?', 
                  (team, user_id, str(match_id)))
    conn.commit()
    conn.close()

    await ctx.send(f"✅ {ctx.author.mention}, votre vote a été modifié !\n"
                  f"**Match {match_id}** : {team1} vs {team2}\n"
                  f"└─ Ancien vote : **{ancien_vote}**\n"
                  f"└─ Nouveau vote : **{team}**")

# Commande pour attribuer des points
@bot.command(name="point")
@commands.has_permissions(administrator=True)
async def point(ctx, member: discord.Member = None, match_id: int = None, point_value: int = None):
    if None in (member, match_id, point_value):
        await ctx.send("❌ Format incorrect. Utilisez `!point @utilisateur 1 1` (premier chiffre = numéro du match, deuxième chiffre = points)")
        return

    if match_id < 1 or match_id > len(matches):
        await ctx.send(f"❌ Match {match_id} invalide. Les matchs disponibles sont de 1 à {len(matches)}.")
        return

    if point_value not in [-1, 1]:
        await ctx.send("❌ Les points doivent être 1 (victoire) ou -1 (absence)")
        return

    user_id = str(member.id)
    
    # Ajouter les points dans la base de données
    add_points(user_id, point_value)
    
    # Récupérer le vote de l'utilisateur pour ce match
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT choice FROM votes WHERE user_id = ? AND match_id = ?', (user_id, str(match_id)))
    result = cursor.fetchone()
    user_vote = result[0] if result else "N'a pas voté"
    conn.close()
    
    # Récupérer les informations du match
    match = matches[match_id]
    team1, team2 = match["teams"]
    
    # Créer le message de confirmation
    if point_value > 0:
        emoji = "✅"
        message = f"a gagné **{point_value}** point"
    else:
        emoji = "❌"
        message = f"a perdu **{abs(point_value)}** point"
    
    confirmation = f"{emoji} {member.mention} {message} pour le match {match_id} !\n"
    confirmation += f"└─ Match : **{team1}** vs **{team2}**\n"
    confirmation += f"└─ Vote : **{user_vote}**\n"
    confirmation += f"└─ Points : **{point_value}**"
    
    await ctx.send(confirmation)

# Commande pour voir le classement
@bot.command(name="classement")
async def classement(ctx):
    # Récupérer le classement depuis la base de données
    leaderboard = get_leaderboard()
    
    if not leaderboard:
        await ctx.send("❌ Aucun point n'a encore été attribué.")
        return
    
    message = "**🏆 CLASSEMENT GÉNÉRAL 🏆**\n\n"
    
    for i, (user_id, points) in enumerate(leaderboard, 1):
        try:
            user = await bot.fetch_user(int(user_id))
            username = user.name
        except:
            username = f"Utilisateur_{user_id}"
            
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
        message += f"{medal} **{username}** : {points} point(s)\n"
    
    await ctx.send(message)

# Commande pour réinitialiser les points
@bot.command(name="reset_points")
@commands.has_permissions(administrator=True)
async def reset_points(ctx, member: discord.Member = None):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    if member is None:
        # Demander confirmation pour réinitialiser tous les points
        confirmation_message = await ctx.send("⚠️ Voulez-vous vraiment réinitialiser **TOUS** les points ?\n"
                                            "Cette action est irréversible !\n"
                                            "✅ = Confirmer\n"
                                            "❌ = Annuler")
        
        await confirmation_message.add_reaction("✅")
        await confirmation_message.add_reaction("❌")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]
        
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            if str(reaction.emoji) == "✅":
                cursor.execute('DELETE FROM leaderboard')
                conn.commit()
                await ctx.send("✅ Tous les points ont été réinitialisés !")
            else:
                await ctx.send("❌ Réinitialisation annulée.")
                
        except TimeoutError:
            await ctx.send("❌ Temps écoulé. Réinitialisation annulée.")
            
    else:
        # Réinitialiser les points d'un utilisateur spécifique
        user_id = str(member.id)
        cursor.execute('DELETE FROM leaderboard WHERE user_id = ?', (user_id,))
        conn.commit()
        await ctx.send(f"✅ Les points de {member.mention} ont été réinitialisés !")
    
    conn.close()

@reset_points.error
async def reset_points_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Seuls les administrateurs peuvent réinitialiser les points.")

keep_alive()

# Lancement du bot avec le token
bot.run(TOKEN)

