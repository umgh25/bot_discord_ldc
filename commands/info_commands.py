import discord
from discord import app_commands
import logging
from discord.ext import commands

logger = logging.getLogger(__name__)

class InfoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="help_vote")
    async def help_vote(self, ctx):
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
            "-----------------------------------"
        ]
        
        await ctx.send("\n".join(help_message))

async def setup(bot):
    await bot.add_cog(InfoCommands(bot))

def setup(bot, matches):
    """Configure les commandes d'information pour le bot"""
    
    @bot.tree.command(name="help", description="Affiche l'aide sur les commandes disponibles")
    async def help_command(interaction: discord.Interaction):
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

`/all_votes`
└─ Voir les statistiques globales et tous les votes

**🏆 Commandes de points (Administrateurs) :**
`/point @utilisateur <numéro du match> <points>`
└─ Attribuer des points à un utilisateur
└─ Points : 1 = victoire, -1 = absence
└─ Exemple : `/point @Pierre 1 1`

`/reset_points @utilisateur`
└─ Réinitialiser les points d'un utilisateur
└─ Sans mention = réinitialise tous les points

`/classement`
└─ Voir le classement général des points
└─ Affiche le top 3 avec médailles 🥇🥈🥉

**📋 Liste des matchs disponibles :**"""

        # Ajouter la liste des matchs
        for match_id, match in matches.items():
            team1, team2 = match
            help_message += f"\n**Match {match_id}** : {team1} vs {team2}"

        help_message += "\n\n**⚠️ Rappels importants :**"
        help_message += "\n• Vous pouvez modifier vos votes à tout moment avant le début du match"
        help_message += "\n• Les votes non effectués avant le début du match entraînent une pénalité de -1 point"
        help_message += "\n• Utilisez les noms exacts des équipes (la casse n'est pas importante)"
        help_message += "\n• Seuls les administrateurs peuvent attribuer ou réinitialiser les points"

        await interaction.response.send_message(help_message, ephemeral=True)

    @bot.tree.command(name="programme", description="Affiche le programme des matchs et les règles du concours")
    async def programme(interaction: discord.Interaction):
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

🚀 Préparez-vous, la SARL reprend du service ! 🚀"""

        await interaction.response.send_message(message)

    @bot.tree.command(name="recap", description="Affiche un récapitulatif de vos votes")
    async def recap(interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        
        try:
            # Récupérer tous les votes de l'utilisateur depuis Supabase
            result = supabase.table("votes").select("*").eq("user_id", user_id).execute()
            user_votes = result.data
            
            if not user_votes:
                await interaction.response.send_message(
                    f"❌ {interaction.user.mention}, tu n'as pas encore voté pour aucun match.", 
                    ephemeral=True
                )
                return
                
            recap_message = f"**📊 Récapitulatif de vos votes {interaction.user.mention} :**\n\n"
            
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
                recap_message += f"\n💡 Utilisez `/help` pour voir la liste des matches disponibles."
            else:
                recap_message += f"\n✅ Vous avez voté pour tous les matches !"

            await interaction.response.send_message(recap_message, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur lors du récap: {str(e)}")
            await interaction.response.send_message(f"❌ Une erreur s'est produite lors de la récupération de vos votes.", ephemeral=True)

    @bot.tree.command(name="all_votes", description="Affiche les statistiques globales et tous les votes")
    async def all_votes(interaction: discord.Interaction):
        try:
            # Récupérer tous les votes depuis Supabase
            result = supabase.table("votes").select("*").execute()
            all_votes = result.data
            
            if not all_votes:
                await interaction.response.send_message("❌ Aucun vote n'a encore été enregistré.", ephemeral=True)
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
                await interaction.response.send_message(message)
            except discord.HTTPException:
                # Si le message est trop long, le diviser et l'envoyer en plusieurs fois
                await interaction.response.send_message("Récapitulatif des votes (suite dans les messages suivants)...")
                
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
                    await interaction.followup.send(msg)
                    
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage des votes: {str(e)}")
            await interaction.response.send_message(f"❌ Une erreur s'est produite lors de la récupération des votes.", ephemeral=True)

    @bot.tree.command(name="voir_votes", description="Voir les votes d'un autre utilisateur")
    @app_commands.describe(member="L'utilisateur dont vous souhaitez voir les votes")
    async def voir_votes(interaction: discord.Interaction, member: discord.Member):
        user_id = str(member.id)
        
        try:
            # Récupérer tous les votes de l'utilisateur depuis Supabase
            result = supabase.table("votes").select("*").eq("user_id", user_id).execute()
            user_votes = result.data
            
            if not user_votes:
                await interaction.response.send_message(f"❌ {member.mention} n'a pas encore voté pour aucun match.", ephemeral=True)
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

            await interaction.response.send_message(recap_message)
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des votes: {str(e)}")
            await interaction.response.send_message(f"❌ Une erreur s'est produite lors de la récupération des votes.", ephemeral=True)
        
    @bot.tree.command(name="classement", description="Affiche le classement général des points")
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
            
            # Créer le classement
            for index, entry in enumerate(leaderboard_data, 1):
                user_id = entry['user_id']
                points = entry['points']
                
                # Récupérer le nom d'utilisateur
                if user_id not in users_cache:
                    try:
                        user = await bot.fetch_user(int(user_id))
                        users_cache[user_id] = user.name
                    except:
                        users_cache[user_id] = f"Utilisateur_{user_id}"
                
                username = users_cache[user_id]
                
                # Ajouter les médailles pour le top 3
                if index == 1:
                    medal = "🥇"
                elif index == 2:
                    medal = "🥈"
                elif index == 3:
                    medal = "🥉"
                else:
                    medal = "👤"
                
                message += f"{medal} **{username}** : {points} point(s)\n"
            
             # Ajouter une ligne de séparation
        message += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # Ajouter des statistiques
        total_participants = len(leaderboard_data)
        total_points = sum(entry['points'] for entry in leaderboard_data)
        
        message += f"\n📊 **Statistiques**\n"
        message += f"└─ Participants : **{total_participants}**\n"
        message += f"└─ Total des points : **{total_points}**\n"
        
        if total_participants > 0:
            avg_points = total_points / total_participants
            message += f"└─ Moyenne : **{avg_points:.1f}** points par participant"
        
        await ctx.send(message)
        
    except Exception as e:
        print(f"Erreur dans la commande classement: {str(e)}")
        await ctx.send("❌ Une erreur s'est produite lors de la récupération du classement.")

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