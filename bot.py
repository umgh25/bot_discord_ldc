import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from keep_alive import keep_alive
from database import *  # Importe toutes les fonctions de database.py
import asyncio

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
    1: ("Club Bruges", "Aston Villa"),
    2: ("Real Madrid", "Atlético Madrid"),
    3: ("PSV Eindhoven", "Arsenal"),
    4: ("Borussia Dortmund", "Lille"),
    5: ("Feyenoord", "Inter Milan"),
    6: ("Benfica", "FC Barcelone"),
    7: ("Bayern Munich", "Bayer Leverkusen"),
    8: ("Paris Saint-Germain", "Liverpool")
}

# Événement quand le bot est prêt
@bot.event
async def on_ready():
    print(f'{bot.user} est connecté et prêt !')
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des slash commands : {e}")

# Commande Slash pour l'aide sur le vote
@bot.tree.command(name="help_vote", description="Affiche l'aide pour les votes")
async def help_vote(interaction: discord.Interaction):
    try:
        help_message = [
            "**🎮 GUIDE DES COMMANDES 🎮**",
            "",
            "**📝 Commandes principales :**",
            "`!vote <numéro du match> <nom de l'équipe>`",
            "└─ Pour voter pour une équipe",
            "└─ Exemple : `!vote 1 Club Bruges`",
            "",
            "`!modifier_vote <numéro du match> <nom de l'équipe>`",
            "└─ Pour modifier un vote existant",
            "└─ Exemple : `!modifier_vote 1 Aston Villa`",
            "",
            "**📋 Liste des matchs disponibles :**"
        ]
        
        # Ajouter la liste des matchs
        for match_id, (team1, team2) in bot.matches.items():
            help_message.append(f"**Match {match_id}** : {team1} vs {team2}")
        
        help_message.append("\n-----------------")
        
        # Envoyer le message visible par tous (ephemeral=False)
        await interaction.response.send_message("\n".join(help_message), ephemeral=False)
        
    except Exception as e:
        print(f"Erreur dans la commande help_vote: {str(e)}")
        await interaction.response.send_message(
            "❌ Une erreur s'est produite lors de l'affichage de l'aide.",
            ephemeral=True  # Les messages d'erreur restent privés
        )

# Ajouter en haut du fichier
vote_locks = {}
point_locks = {}

@bot.command()
async def vote(ctx, match_id: int = None, *, team: str = None):
    # Vérifier si l'utilisateur a un vote en cours
    user_id = str(ctx.author.id)
    if user_id in vote_locks:
        await ctx.send("⚠️ Veuillez attendre que votre vote précédent soit terminé.")
        return
        
    vote_locks[user_id] = True
    try:
        print(f"=== DÉBUT COMMANDE VOTE ===")
        print(f"Match ID: {match_id}")
        print(f"Team: {team}")
        
        # Vérifications habituelles...
        if match_id is None or team is None:
            await ctx.send("❌ Format incorrect. Utilisez `!vote <numéro du match> <nom de l'équipe>`")
            return
        
        if match_id not in matches:
            await ctx.send(f"❌ Match {match_id} invalide. Les matchs disponibles sont de 1 à {len(matches)}.")
            return

        team1, team2 = matches[match_id]
        team = team.strip()
        
        if team.lower() not in [team1.lower(), team2.lower()]:
            await ctx.send(f"❌ Équipe invalide. Pour le match {match_id}, vous pouvez seulement voter pour :\n- **{team1}**\n- **{team2}**")
            return
        
        team = team1 if team.lower() == team1.lower() else team2
        
        # Attendre un court instant pour éviter les doublons
        await asyncio.sleep(0.5)
        
        success = save_vote(user_id, match_id, team)
        
        if success:
            await ctx.send(f"✅ {ctx.author.mention}, tu as voté pour **{team}** dans le match **{team1}** vs **{team2}**.")
        else:
            await ctx.send(f"❌ {ctx.author.mention}, il y a eu une erreur lors de l'enregistrement de ton vote.")
            
    except Exception as e:
        print(f"Erreur lors du vote: {str(e)}")
        await ctx.send(f"❌ Une erreur s'est produite lors du vote.")
    finally:
        # Toujours libérer le verrou
        if user_id in vote_locks:
            del vote_locks[user_id]
    
    print("=== FIN COMMANDE VOTE ===")

# Commande !supprimer_vote


@bot.command(name="supprimer_vote")
async def supprimer_vote(ctx, match_id: int):
    user_id = str(ctx.author.id)
    
    try:
        # Vérifier si le vote existe
        result = supabase.table("votes").select("*").eq("user_id", user_id).eq("match_id", match_id).execute()
        
        if not result.data:
            await ctx.send(f"❌ {ctx.author.mention}, tu n'as pas encore voté pour le match {match_id}.")
            return
        
        # Suppression du vote
        supabase.table("votes").delete().eq("user_id", user_id).eq("match_id", match_id).execute()
        
        # Récupérer les équipes du match pour le message
        if match_id in matches:
            team1, team2 = matches[match_id]
            await ctx.send(f"✅ {ctx.author.mention}, ton vote pour le match {match_id} ({team1} vs {team2}) a été supprimé !")
        else:
            await ctx.send(f"✅ {ctx.author.mention}, ton vote pour le match {match_id} a été supprimé !")
            
    except Exception as e:
        print(f"Erreur lors de la suppression du vote: {str(e)}")
        await ctx.send(f"❌ Une erreur s'est produite lors de la suppression du vote.")

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
    user_id = str(ctx.author.id)
    
    try:
        # Récupérer tous les votes de l'utilisateur depuis Supabase
        result = supabase.table("votes").select("*").eq("user_id", user_id).execute()
        user_votes = result.data
        
        if not user_votes:
            await ctx.send(f"❌ {ctx.author.mention}, tu n'as pas encore voté pour aucun match.")
            return
            
        recap_message = f"**📊 Récapitulatif de vos votes {ctx.author.mention} :**\n\n"
        
        # Trier les votes par numéro de match
        user_votes.sort(key=lambda x: x['match_id'])
        
        for vote in user_votes:
            match_id = vote['match_id']
            voted_team = vote['choice']
            
            if match_id in matches:
                team1, team2 = matches[match_id]
                recap_message += f"**Match {match_id}** : {team1} vs {team2}\n"
                recap_message += f"➡️ Votre vote : **{voted_team}**\n\n"
        
        # Ajouter le nombre total de votes
        total_votes = len(user_votes)
        matches_restants = len(matches) - total_votes
        
        recap_message += f"**📈 Statistiques :**\n"
        recap_message += f"- Votes effectués : **{total_votes}/{len(matches)}**\n"
        
        if matches_restants > 0:
            recap_message += f"- Matches restants à voter : **{matches_restants}**\n"
            recap_message += f"\n💡 Utilisez `!help_vote` pour voir la liste des matches disponibles."
        else:
            recap_message += f"\n✅ Vous avez voté pour tous les matches !"

        await ctx.send(recap_message)
        
    except Exception as e:
        print(f"Erreur lors du récap: {str(e)}")
        await ctx.send(f"❌ Une erreur s'est produite lors de la récupération de vos votes.")

# Commande pour voir le récapitulatif des votes
@bot.command(name="all_votes")
async def all_votes(ctx):
    try:
        # Récupérer tous les votes depuis Supabase
        result = supabase.table("votes").select("*").execute()
        all_votes = result.data
        
        if not all_votes:
            await ctx.send("❌ Aucun vote n'a encore été enregistré.")
            return
        
        # Créer un dictionnaire pour organiser les votes par match
        votes_par_match = {}
        for match_id in matches.keys():
            votes_par_match[match_id] = {"votes": {}}
        
        # Récupérer tous les utilisateurs une seule fois
        users_cache = {}
        
        # Organiser les votes par match
        for vote in all_votes:
            user_id = vote["user_id"]
            match_id = vote["match_id"]
            team = vote["choice"]
            
            # Récupérer le nom d'utilisateur si pas encore en cache
            if user_id not in users_cache:
                try:
                    user = await bot.fetch_user(int(user_id))
                    users_cache[user_id] = user.name
                except:
                    users_cache[user_id] = f"Utilisateur_{user_id}"
            
            if team not in votes_par_match[match_id]["votes"]:
                votes_par_match[match_id]["votes"][team] = []
            votes_par_match[match_id]["votes"][team].append(users_cache[user_id])
        
        # Créer le message de récapitulatif
        message = "**🌟 RÉCAPITULATIF GLOBAL DES VOTES 🌟**\n\n"
        
        for match_id in sorted(votes_par_match.keys()):
            team1, team2 = matches[match_id]
            message += f"**📌 Match {match_id}** : {team1} vs {team2}\n"
            message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            match_votes = votes_par_match[match_id]["votes"]
            if not match_votes:
                message += "❌ Aucun vote pour ce match\n"
            else:
                total_votes = sum(len(voters) for voters in match_votes.values())
                
                # Afficher les votes pour chaque équipe
                for team in [team1, team2]:
                    voters = match_votes.get(team, [])
                    percentage = (len(voters) / total_votes * 100) if total_votes > 0 else 0
                    
                    # Créer une barre de progression
                    progress_bar = "🟦" * int(percentage/10) + "⬜" * (10 - int(percentage/10))
                    
                    message += f"\n**{team}**\n"
                    message += f"└─ Votes : **{len(voters)}** ({percentage:.1f}%)\n"
                    message += f"└─ Progression : {progress_bar}\n"
                    if voters:
                        message += f"└─ 👥 Votants : {', '.join(sorted(voters))}\n"
            
            message += "\n"
        
        # Ajouter des statistiques globales
        total_users = len({vote["user_id"] for vote in all_votes})
        total_votes = len(all_votes)
        
        message += "**📊 STATISTIQUES GLOBALES 📊**\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"👥 **Participation**\n"
        message += f"└─ Nombre de participants : **{total_users}**\n"
        message += f"└─ Total des votes : **{total_votes}**\n"
        message += f"└─ Moyenne par utilisateur : **{total_votes/total_users:.1f}**\n\n"
        
        try:
            await ctx.send(message)
        except discord.HTTPException:
            # Si le message est trop long, on le divise
            messages = []
            current_message = ""
            for line in message.split('\n'):
                if len(current_message) + len(line) + 1 > 1900:
                    messages.append(current_message)
                    current_message = line
                else:
                    current_message += line + '\n'
            if current_message:
                messages.append(current_message)
            
            for msg in messages:
                await ctx.send(msg)
                
    except Exception as e:
        print(f"Erreur lors de l'affichage des votes: {str(e)}")
        await ctx.send(f"❌ Une erreur s'est produite lors de la récupération des votes.")

# Commande pour voir les votes d'un utilisateur spécifique
@bot.command(name="voir_votes")
async def voir_votes(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("❌ Veuillez mentionner un utilisateur. Exemple : `!voir_votes @utilisateur`")
        return

    user_id = str(member.id)
    
    try:
        # Récupérer tous les votes de l'utilisateur depuis Supabase
        result = supabase.table("votes").select("*").eq("user_id", user_id).execute()
        user_votes = result.data
        
        if not user_votes:
            await ctx.send(f"❌ {member.mention} n'a pas encore voté pour aucun match.")
            return
            
        recap_message = f"**📊 Votes de {member.mention} :**\n\n"
        
        # Trier les votes par numéro de match
        user_votes.sort(key=lambda x: x['match_id'])
        
        for vote in user_votes:
            match_id = vote['match_id']
            voted_team = vote['choice']
            
            if match_id in matches:
                team1, team2 = matches[match_id]
                recap_message += f"**Match {match_id}** : {team1} vs {team2}\n"
                recap_message += f"➡️ Vote : **{voted_team}**\n\n"
        
        # Ajouter le nombre total de votes
        total_votes = len(user_votes)
        matches_restants = len(matches) - total_votes
        
        recap_message += f"**📈 Statistiques :**\n"
        recap_message += f"└─ Votes effectués : **{total_votes}/{len(matches)}**\n"
        recap_message += f"└─ Matches restants : **{matches_restants}**\n"

        if matches_restants > 0:
            recap_message += f"\n💡 Il reste encore {matches_restants} match(es) à voter !"
        else:
            recap_message += f"\n✅ A voté pour tous les matches !"

        await ctx.send(recap_message)
        
    except Exception as e:
        print(f"Erreur lors de la récupération des votes: {str(e)}")
        await ctx.send(f"❌ Une erreur s'est produite lors de la récupération des votes.")

# Commande pour modifier un vote existant
@bot.command(name="modifier_vote")
async def modifier_vote(ctx, match_id: int = None, *, team: str = None):
    user_id = str(ctx.author.id)
    
    try:
        # Vérifier si les paramètres sont fournis
        if match_id is None or team is None:
            await ctx.send("❌ Format incorrect. Utilisez `!modifier_vote <numéro du match> <nom de l'équipe>`")
            return

        # Vérifier si le match existe
        if match_id not in matches:
            await ctx.send(f"❌ Match {match_id} invalide. Les matchs disponibles sont de 1 à {len(matches)}.")
            return

        # Vérifier si l'utilisateur a déjà voté pour ce match
        result = supabase.table("votes").select("*").eq("user_id", user_id).eq("match_id", match_id).execute()
        
        if not result.data:
            await ctx.send(f"❌ Vous n'avez pas encore voté pour le match {match_id}. Utilisez `!vote` pour voter.")
            return

        team1, team2 = matches[match_id]
        ancien_vote = result.data[0]["choice"]

        # Normaliser le nom de l'équipe pour la comparaison
        team = team.strip()
        if team.lower() not in [team1.lower(), team2.lower()]:
            await ctx.send(f"❌ Équipe invalide. Pour le match {match_id}, vous pouvez seulement voter pour :\n- **{team1}**\n- **{team2}**")
            return

        # Si l'utilisateur vote pour la même équipe
        if team.lower() == ancien_vote.lower():
            await ctx.send(f"ℹ️ Vous avez déjà voté pour **{ancien_vote}** dans ce match.")
            return

        # Trouver le nom exact de l'équipe (pour garder la casse correcte)
        team = team1 if team.lower() == team1.lower() else team2

        # Modifier le vote dans Supabase
        supabase.table("votes").update({"choice": team}).eq("user_id", user_id).eq("match_id", match_id).execute()

        await ctx.send(f"✅ {ctx.author.mention}, votre vote a été modifié !\n"
                    f"**Match {match_id}** : {team1} vs {team2}\n"
                    f"└─ Ancien vote : **{ancien_vote}**\n"
                    f"└─ Nouveau vote : **{team}** 🔄")

    except Exception as e:
        print(f"Erreur lors de la modification du vote: {str(e)}")
        await ctx.send(f"❌ Une erreur s'est produite lors de la modification du vote.")

# Commande pour attribuer des points
@bot.command(name="point")
@commands.max_concurrency(1, per=commands.BucketType.user)  # Limite à une exécution à la fois par utilisateur
async def point(ctx, member: discord.Member = None, match_id: int = None, point_value: int = None):
    try:
        if None in (member, match_id, point_value):
            await ctx.send("❌ Format incorrect. Utilisez `!point @utilisateur 1 1`")
            return

        if match_id not in matches:
            await ctx.send(f"❌ Match {match_id} invalide. Les matchs disponibles sont de 1 à {len(matches)}.")
            return

        if point_value not in [-1, 1]:
            await ctx.send("❌ Les points doivent être 1 (victoire) ou -1 (absence)")
            return

        user_id = str(member.id)
        success = add_points(user_id, match_id, point_value)
        
        if not success:
            await ctx.send("❌ Une erreur s'est produite lors de l'attribution des points.")
            return
            
        team1, team2 = matches[match_id]
        
        if point_value > 0:
            message = f"✅ {member.mention} a gagné **{point_value}** point pour le match {match_id} !\n"
        else:
            message = f"❌ {member.mention} a perdu **{abs(point_value)}** point pour le match {match_id} !\n"
            
        message += f"└─ Match : **{team1}** vs **{team2}**\n"
        message += f"└─ Points : **{point_value}**"
        
        await ctx.reply(message)  # Utiliser reply au lieu de send
        
    except commands.MaxConcurrencyReached:
        await ctx.send("⚠️ Une commande est déjà en cours pour cet utilisateur.")
    except Exception as e:
        print(f"Erreur dans la commande point: {str(e)}")
        await ctx.send("❌ Une erreur s'est produite lors de l'attribution des points.")

@point.error
async def point_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Seuls les administrateurs peuvent attribuer des points.")

# Commande de classement en slash command
@bot.tree.command(name="classement", description="Affiche le classement des points.")
async def classement(interaction: discord.Interaction):
    try:
        # Récupérer le classement
        leaderboard_data = get_leaderboard()

        if not leaderboard_data:
            await interaction.response.send_message("❌ Aucun point n'a encore été attribué.", ephemeral=True)
            return

        # Créer le message de classement
        message = "**🏆 CLASSEMENT GÉNÉRAL 🏆**\n\n"

        # Cache pour stocker les noms d'utilisateurs
        users_cache = {}

        # Construire le classement
        for index, entry in enumerate(leaderboard_data, 1):
            user_id = entry["user_id"]
            points = entry["points"]

            # Récupérer le nom d'utilisateur
            if user_id not in users_cache:
                try:
                    user = await bot.fetch_user(int(user_id))
                    users_cache[user_id] = user.name
                except:
                    users_cache[user_id] = f"Utilisateur_{user_id}"

            username = users_cache[user_id]

            # Ajouter les médailles pour le top 3
            medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else "👤"
            message += f"{medal} **{username}** : {points} point(s)\n"

        # Ajouter une ligne de séparation
        message += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        # Ajouter des statistiques
        total_participants = len(leaderboard_data)
        total_points = sum(entry["points"] for entry in leaderboard_data)

        message += f"\n📊 **Statistiques**\n"
        message += f"└─ Participants : **{total_participants}**\n"
        message += f"└─ Total des points : **{total_points}**\n"

        if total_participants > 0:
            avg_points = total_points / total_participants
            message += f"└─ Moyenne : **{avg_points:.1f}** points par participant"

        await interaction.response.send_message(message)

    except Exception as e:
        print(f"Erreur dans la commande classement: {str(e)}")
        await interaction.response.send_message("❌ Une erreur s'est produite lors de la récupération du classement.", ephemeral=True)

# Commande pour réinitialiser les points
@bot.command(name="reset_points")
@commands.has_permissions(administrator=True)
async def reset_points_cmd(ctx, member: discord.Member = None):
    try:
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
                    success, count = reset_points()
                    if success:
                        if count > 0:
                            await ctx.send(f"✅ Tous les points ont été réinitialisés ! ({count} points supprimés)")
                        else:
                            await ctx.send("ℹ️ Aucun point n'était enregistré dans la base de données.")
                    else:
                        await ctx.send("❌ Une erreur s'est produite lors de la réinitialisation des points.")
                else:
                    await ctx.send("❌ Réinitialisation annulée.")
                    
            except TimeoutError:
                await ctx.send("❌ Temps écoulé. Réinitialisation annulée.")
                
        else:
            # Réinitialiser les points d'un utilisateur spécifique
            user_id = str(member.id)
            success, count = reset_points(user_id)
            
            if success:
                if count > 0:
                    await ctx.send(f"✅ Les points de {member.mention} ont été réinitialisés ! ({count} points supprimés)")
                else:
                    await ctx.send(f"ℹ️ {member.mention} n'avait pas de points enregistrés.")
            else:
                await ctx.send(f"❌ Une erreur s'est produite lors de la réinitialisation des points de {member.mention}.")
                
    except Exception as e:
        print(f"Erreur dans la commande reset_points: {str(e)}")
        await ctx.send("❌ Une erreur s'est produite lors de la réinitialisation des points.")

@reset_points_cmd.error
async def reset_points_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Seuls les administrateurs peuvent réinitialiser les points.")

keep_alive()

# Lancement du bot avec le token
bot.run(TOKEN)

