import discord
from discord.ext import commands
from discord import app_commands
import sys
sys.path.append('../../../config')
sys.path.append('../../database')
sys.path.append('../utils')

from config.settings import MATCHES, MATCHES_PHASES, ACTIVE_MATCH_PHASE
from src.database.operations import supabase
from ..utils.helpers import check_channel, format_match_list

PHASE_LABELS = {
    "8e_finale_aller": "8e de finale (aller)",
    "quart_finale_aller": "Quart de finale (aller)",
    "demi_finale": "Demi-finale",
    "finale": "Finale",
}


def format_phase_ids_help_message() -> str:
    """Message pour !matchs / !finale : IDs actifs + rappel des slash commands."""
    titre = PHASE_LABELS.get(ACTIVE_MATCH_PHASE, ACTIVE_MATCH_PHASE)
    lignes = [f"**{titre}** — matchs en cours\n"]

    if ACTIVE_MATCH_PHASE == "quart_finale_aller":
        lignes.append(
            "IDs en base : **8e** 1–8 · **quarts** 9–12 (pas de conflit avec les anciens votes).\n"
        )
    elif ACTIVE_MATCH_PHASE == "demi_finale":
        lignes.append("IDs en base : **8e** 1–8 · **quarts** 9–12 · **demis** 13–14.\n")
    elif ACTIVE_MATCH_PHASE == "finale":
        lignes.append(
            "IDs en base : **8e** 1–8 · **quarts** 9–12 · **demis** 13–14 · **finale** **15**.\n"
        )

    lignes.append("**Match(s) à voter :**")
    for mid in sorted(MATCHES.keys()):
        a, b = MATCHES[mid]
        lignes.append(f"• **{mid}** — {a} vs {b}")

    exemple_id = next(iter(sorted(MATCHES.keys())), 15)
    exemple_equipe = MATCHES[exemple_id][0]
    lignes.extend(
        [
            "",
            "**Voter (commandes slash `/`, pas `!`) :**",
            f"`/vote <id> <équipe>` — ex. `/vote {exemple_id} {exemple_equipe}`",
            "`/modifier_vote <id> <équipe>`",
            "`/supprimer_vote <id>`",
            "`/help_vote` — guide complet",
            "",
            "Le préfixe `!` sert aux commandes texte ; **le vote se fait avec `/`.**",
        ]
    )
    return "\n".join(lignes)


def setup_info_commands(bot):
    """Configure toutes les commandes d'information"""
    # Commande d'aide pour les commandes de vote
    @bot.tree.command(name="help_vote", description="Affiche le guide des commandes de vote.")
    async def help_vote(interaction: discord.Interaction):
        """
        Commande d'aide qui affiche le guide complet des commandes disponibles.
        Inclut toutes les commandes de vote, consultation et administration.
        """
        # Vérifier que la commande est utilisée dans le bon canal
        if not check_channel(interaction):
            await interaction.response.send_message(
                f"❌ Cette commande ne peut être utilisée que dans le canal <#{interaction.channel_id}>",
                ephemeral=True
            )
            return
        
        # Construire le message d'aide avec toutes les commandes
        help_message = """**🎮 GUIDE DES COMMANDES 🎮**

**📝 Commandes principales :**
`/vote <numéro du match> <nom de l'équipe>`
└─ Pour voter pour une équipe
└─ Exemple : `/vote 15 Paris-SG`

`/modifier_vote <numéro du match> <nom de l'équipe>`
└─ Pour modifier un vote existant
└─ Exemple : `/modifier_vote 15 Arsenal`

`/supprimer_vote <numéro du match>`
└─ Pour supprimer un de vos votes
└─ Exemple : `/supprimer_vote 15`

**📊 Commandes de consultation :**
`/recap`
└─ Voir tous vos votes

`/voir_votes @utilisateur`
└─ Voir les votes d'un autre utilisateur
└─ Exemple : `/voir_votes @Pierre`

`/all_votes`
└─ Voir les statistiques globales et tous les votes

**🏆 Commandes de points (Administrateurs) :**
`/points @utilisateur <numéro du match> <points>`
└─ Attribuer des points à un utilisateur
└─ Points : 1 = victoire, -1 = absence
└─ Exemple : `/points @Pierre 15 1`

`/reset_points @utilisateur`
└─ Réinitialiser les points d'un utilisateur
└─ Sans mention = réinitialise tous les points

`/classement`
└─ Voir le classement général des points
└─ Affiche le top 3 avec médailles 🥇🥈🥉

**📋 Liste des matchs disponibles :**"""

        # Ajouter dynamiquement la liste des matchs disponibles
        help_message += format_match_list()

        help_message += "\n\n**💬 Rappel texte :** tape `!finale` ou `!matchs` pour revoir le numéro du match et les commandes slash."

        # Ajouter les rappels importants
        help_message += "\n\n**⚠️ Rappels importants :**"
        help_message += "\n• Vous pouvez modifier vos votes à tout moment avant le début du match"
        help_message += "\n• Les votes non effectués avant le début du match entraînent une pénalité de -1 point"
        help_message += "\n• Utilisez les noms exacts des équipes (la casse n'est pas importante)"
        help_message += "\n• Seuls les administrateurs peuvent attribuer ou réinitialiser les points"

        # Envoyer le message d'aide (visible par tout le monde)
        await interaction.response.send_message(help_message)

    # Commande pour afficher le programme des matchs et les règles du concours
    @bot.tree.command(name="programme", description="Affiche le programme des matchs et les règles du concours.")
    async def programme(interaction: discord.Interaction):
        if not check_channel(interaction):
            await interaction.response.send_message(
                f"❌ Cette commande ne peut être utilisée que dans le canal <#{interaction.channel_id}>",
                ephemeral=True
            )
            return
        message = """**Oyé, Oyé,
⚽ La Ligue des Champions — **FINALE** ! ⚽
🔥 Paris-SG et Arsenal s'affrontent pour soulever la coupe ! 🔥

La SARL organise son grand jeu "Road to Munich", avec des récompenses à la clé ! 🎁🏆

Trêve de bavardages, voyons ce qui nous attend !

💰 Les récompenses
Vainqueur de la finale : Carte cadeau de 5€ 🏆

---

🏆 **Finale** — match unique 🏆
**Paris-SG 🇫🇷 vs. Arsenal 🏴󠁧󠁢󠁥󠁮󠁧󠁿**

Pour voter : `/vote 15 Paris-SG` ou `/vote 15 Arsenal`
Rappel : `!finale` ou `!matchs` pour revoir le numéro de match.

---
📜 Règlement du concours
Prédictions : Vous avez jusqu'au coup d'envoi du premier match de chaque confrontation pour poster vos pronostics.
Pénalité : Chaque match non pronostiqué à temps entraîne une pénalité de -1 point.

---

🚀 Préparez-vous, la SARL reprend du service ! 🚀"""

        await interaction.response.send_message(
            f"@everyone\n{message}",
            allowed_mentions=discord.AllowedMentions(everyone=True)
        )

    # Commande pour afficher le récapitulatif de vos votes dans le channel
    @bot.tree.command(name="recap", description="Affiche un récapitulatif de vos votes dans le channel.")
    async def recap(interaction: discord.Interaction):
        if not check_channel(interaction):
            await interaction.response.send_message(
                f"❌ Cette commande ne peut être utilisée que dans le canal <#{interaction.channel_id}>",
                ephemeral=True
            )
            return
            
        user_id = str(interaction.user.id)
        
        try:
            result = supabase.table("votes").select("*").eq("user_id", user_id).execute()
            user_votes = result.data
            
            if not user_votes:
                await interaction.response.send_message(
                    f"❌ {interaction.user.mention}, tu n'as pas encore voté pour aucun match.",
                    ephemeral=False
                )
                return
                
            recap_message = f"**📊 Récapitulatif des votes de {interaction.user.mention} :**\n\n"
            
            # Trier les votes par numéro de match
            user_votes.sort(key=lambda x: x['match_id'])
            
            for vote in user_votes:
                match_id = vote['match_id']
                voted_team = vote['choice']
                
                match_found = False
                if match_id in MATCHES:
                    team1, team2 = MATCHES[match_id]
                    phase_name = PHASE_LABELS.get(ACTIVE_MATCH_PHASE, ACTIVE_MATCH_PHASE)
                    recap_message += f"**Match {match_id}** ({phase_name}) : {team1} vs {team2}\n"
                    recap_message += f"➡️ Son vote : **{voted_team}**\n\n"
                    match_found = True
                else:
                    for phase, phase_matches in MATCHES_PHASES.items():
                        if phase == ACTIVE_MATCH_PHASE:
                            continue
                        if match_id in phase_matches:
                            team1, team2 = phase_matches[match_id]
                            phase_name = PHASE_LABELS.get(phase, phase)
                            recap_message += f"**Match {match_id}** ({phase_name}) : {team1} vs {team2}\n"
                            recap_message += f"➡️ Son vote : **{voted_team}**\n\n"
                            match_found = True
                            break
                
                if not match_found:
                    recap_message += f"**Match {match_id}** : Vote pour **{voted_team}**\n\n"
            
            votes_phase_actuelle = sum(1 for v in user_votes if v["match_id"] in MATCHES)
            matches_restants = len(MATCHES) - votes_phase_actuelle

            recap_message += f"**📈 Statistiques (matchs en cours) :**\n"
            recap_message += f"- Votes effectués : **{votes_phase_actuelle}/{len(MATCHES)}**\n"

            if matches_restants > 0:
                recap_message += f"- Matches restants à voter : **{matches_restants}**\n"
                recap_message += f"\n💡 `/help_vote` ou `!finale` pour le numéro de match."
            else:
                recap_message += f"\n✅ {interaction.user.mention} a voté pour tous les matches en cours !"

            await interaction.response.send_message(recap_message)
            
        except Exception as e:
            print(f"Erreur lors du récap: {str(e)}")
            await interaction.response.send_message(
                f"❌ Une erreur s'est produite lors de la récupération des votes.",
                ephemeral=False
            )

    # Commande pour afficher un résumé global des votes avec les votants
    @bot.tree.command(name="all_votes", description="Affiche un résumé global des votes avec les votants")
    async def all_votes(interaction: discord.Interaction):
        if not check_channel(interaction):
            await interaction.response.send_message(
                f"❌ Cette commande ne peut être utilisée que dans le canal <#{interaction.channel_id}>",
                ephemeral=True
            )
            return
        try:
            # Récupérer tous les votes depuis Supabase
            result = supabase.table("votes").select("*").execute()
            all_votes = result.data
            
            if not all_votes:
                await interaction.response.send_message("❌ Aucun vote enregistré.", ephemeral=False)
                return

            votes_par_match = {match_id: {"votes": {}, "votants": {}} for match_id in MATCHES.keys()}
            users_cache = {}

            for vote in all_votes:
                user_id = vote["user_id"]
                match_id = vote["match_id"]
                team = vote["choice"]

                if match_id not in votes_par_match:
                    continue

                if user_id not in users_cache:
                    try:
                        user = await bot.fetch_user(int(user_id))
                        users_cache[user_id] = user.name
                    except:
                        users_cache[user_id] = f"User_{user_id}"

                username = users_cache[user_id]
                votes_par_match[match_id]["votes"].setdefault(team, []).append(username)
                votes_par_match[match_id]["votants"][username] = team  # Stocker le choix par utilisateur

            message = "**📊 Votes Résumés 📊**\n"
            
            for match_id in sorted(votes_par_match.keys()):
                team1, team2 = MATCHES[match_id]
                match_votes = votes_par_match[match_id]["votes"]
                match_votants = votes_par_match[match_id]["votants"]
                total_votes = sum(len(voters) for voters in match_votes.values())

                message += f"\n📌 **{team1} vs {team2}**\n"

                if not match_votes:
                    message += "❌ Aucun vote\n"
                else:
                    for team in [team1, team2]:
                        voters = match_votes.get(team, [])
                        percentage = (len(voters) / total_votes * 100) if total_votes > 0 else 0
                        message += f"🏆 **{team}** - {len(voters)} votes ({percentage:.1f}%)\n"

                # Ajouter les votants pour ce match
                message += "\n👥 **Votants :**\n"
                for voter, vote_choice in match_votants.items():
                    message += f"🔹 {voter} → {vote_choice}\n"

            votes_affiches = [v for v in all_votes if v["match_id"] in MATCHES]
            total_users = len({v["user_id"] for v in votes_affiches})
            total_votes_phase = len(votes_affiches)

            message += f"\n👥 **{total_users} participants** | 🗳️ **{total_votes_phase} votes** (phase en cours)"

            await interaction.response.send_message(message[:2000])  # Discord limite à 2000 caractères

        except Exception as e:
            print(f"Erreur: {e}")
            await interaction.response.send_message("❌ Erreur lors de la récupération des votes.", ephemeral=True)

    # Commande pour afficher les votes d'un utilisateur spécifique
    @bot.tree.command(name="voir_votes", description="Affiche les votes d'un utilisateur spécifique.")
    async def voir_votes(interaction: discord.Interaction, member: discord.Member):
        if not check_channel(interaction):
            await interaction.response.send_message(
                f"❌ Cette commande ne peut être utilisée que dans le canal <#{interaction.channel_id}>",
                ephemeral=True
            )
            return
        
        user_id = str(member.id)
        
        try:
            # Récupérer tous les votes de l'utilisateur depuis Supabase
            result = supabase.table("votes").select("*").eq("user_id", user_id).execute()
            user_votes = result.data
            
            if not user_votes:
                await interaction.response.send_message(f"❌ {member.mention} n'a pas encore voté pour aucun match.")
                return
                
            recap_message = f"**📊 Votes de {member.mention} :**\n\n"
            
            # Trier les votes par numéro de match
            user_votes.sort(key=lambda x: x['match_id'])
            
            for vote in user_votes:
                match_id = vote['match_id']
                voted_team = vote['choice']
                
                if match_id in MATCHES:
                    team1, team2 = MATCHES[match_id]
                    recap_message += f"**Match {match_id}** : {team1} vs {team2}\n"
                    recap_message += f"➡️ Vote : **{voted_team}**\n\n"
            
            votes_actuels = sum(1 for v in user_votes if v["match_id"] in MATCHES)
            matches_restants = len(MATCHES) - votes_actuels

            recap_message += f"**📈 Statistiques (phase en cours) :**\n"
            recap_message += f"└─ Votes effectués : **{votes_actuels}/{len(MATCHES)}**\n"
            recap_message += f"└─ Matches restants : **{matches_restants}**\n"

            if matches_restants > 0:
                recap_message += f"\n💡 Il reste encore {matches_restants} match(es) à voter !"
            else:
                recap_message += f"\n✅ A voté pour tous les matches !"

            await interaction.response.send_message(recap_message)
            
        except Exception as e:
            print(f"Erreur lors de la récupération des votes: {str(e)}")
            await interaction.response.send_message(f"❌ Une erreur s'est produite lors de la récupération des votes.")

    @bot.command(
        name="matchs",
        aliases=["finale", "quarts", "matchs_quarts", "ids_matchs"],
        help="Affiche les numéros de match de la phase en cours et comment voter",
    )
    async def matchs_prefix(ctx: commands.Context):
        """Commande préfixe !matchs / !finale — filtré par on_command dans main.py."""
        await ctx.send(format_phase_ids_help_message())