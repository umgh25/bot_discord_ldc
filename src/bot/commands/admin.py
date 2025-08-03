import discord
from discord.ext import commands
from discord import app_commands
import sys
sys.path.append('../../../config')
sys.path.append('../../database')
sys.path.append('../utils')

from config.settings import MATCHES
from src.database.operations import add_points, get_leaderboard, reset_points
from ..utils.helpers import check_channel

# Commandes d'administration
def setup_admin_commands(bot):
    """Configure toutes les commandes d'administration"""
    # Commande pour attribuer des points à un utilisateur
    @bot.tree.command(name="points", description="Attribuer des points à un utilisateur (admin seulement)")
    async def point_slash(interaction: discord.Interaction, membre: discord.Member, match_id: int, point_value: int):
        # Vérifier le canal
        if not check_channel(interaction):
            await interaction.response.send_message(
                f"❌ Cette commande ne peut être utilisée que dans le canal <#{interaction.channel_id}>",
                ephemeral=True
            )
            return
        # Vérifier les permissions administrateur
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Seuls les administrateurs peuvent attribuer des points.",
                ephemeral=True
            )
            return
        try:
            if match_id not in MATCHES:
                await interaction.response.send_message(
                    f"❌ Match {match_id} invalide. Les matchs disponibles sont :\n**Finale** : 15",
                    ephemeral=True
                )
                return
            if point_value not in [-1, 1]:
                await interaction.response.send_message(
                    "❌ Les points doivent être 1 (victoire) ou -1 (absence)",
                    ephemeral=True
                )
                return
            user_id = str(membre.id)
            success = add_points(user_id, match_id, point_value)
            if not success:
                await interaction.response.send_message(
                    "❌ Une erreur s'est produite lors de l'attribution des points.",
                    ephemeral=True
                )
                return
            team1, team2 = MATCHES[match_id]
            if point_value > 0:
                message = f"✅ {membre.mention} a gagné **{point_value}** point pour le match {match_id} !\n"
            else:
                message = f"❌ {membre.mention} a perdu **{abs(point_value)}** point pour le match {match_id} !\n"
            message += f"└─ Match : **{team1}** vs **{team2}**\n"
            message += f"└─ Points : **{point_value}**"
            await interaction.response.send_message(message)
        except Exception as e:
            print(f"Erreur dans la commande slash point: {str(e)}")
            await interaction.response.send_message(
                "❌ Une erreur s'est produite lors de l'attribution des points.",
                ephemeral=True
            )

    # Commande pour afficher le classement des points
    @bot.tree.command(name="classement", description="Affiche le classement des points.")
    async def classement(interaction: discord.Interaction):
        if not check_channel(interaction):
            await interaction.response.send_message(
                f"❌ Cette commande ne peut être utilisée que dans le canal <#{interaction.channel_id}>",
                ephemeral=True
            )
            return
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

    # Commande pour réinitialiser les points d'un utilisateur ou de tous les utilisateurs
    @bot.tree.command(name="reset_points", description="Réinitialise les points d'un utilisateur ou de tous les utilisateurs (admin seulement)")
    @app_commands.describe(membre="Utilisateur à réinitialiser (laisser vide pour tout réinitialiser)")
    async def reset_points_slash(interaction: discord.Interaction, membre: discord.Member = None):
        # Vérifier le canal
        if not check_channel(interaction):
            await interaction.response.send_message(
                f"❌ Cette commande ne peut être utilisée que dans le canal <#{interaction.channel_id}>",
                ephemeral=True
            )
            return
        # Vérifier les permissions administrateur
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Seuls les administrateurs peuvent réinitialiser les points.",
                ephemeral=True
            )
            return
        try:
            if membre is None:
                # Confirmation textuelle (pas de boutons natifs en slash, donc on demande une confirmation par message)
                await interaction.response.send_message(
                    "⚠️ Voulez-vous vraiment réinitialiser **TOUS** les points ?\n"\
                    "Cette action est irréversible !\n"\
                    "Répondez par `/confirm_reset_points` dans les 30 secondes pour confirmer.",
                    ephemeral=True
                )
                # Stocker l'ID de l'utilisateur qui a demandé la confirmation
                bot._reset_points_pending = {
                    "user_id": interaction.user.id,
                    "channel_id": interaction.channel_id,
                    "interaction_id": interaction.id
                }
                return
            else:
                # Réinitialiser les points d'un utilisateur spécifique
                user_id = str(membre.id)
                success, count = reset_points(user_id)
                if success:
                    if count > 0:
                        await interaction.response.send_message(f"✅ Les points de {membre.mention} ont été réinitialisés ! ({count} points supprimés)")
                    else:
                        await interaction.response.send_message(f"ℹ️ {membre.mention} n'avait pas de points enregistrés.")
                else:
                    await interaction.response.send_message(f"❌ Une erreur s'est produite lors de la réinitialisation des points de {membre.mention}.")
        except Exception as e:
            print(f"Erreur dans la commande reset_points (slash): {str(e)}")
            await interaction.response.send_message("❌ Une erreur s'est produite lors de la réinitialisation des points.")

    # Slash commande de confirmation pour la suppression totale (sécurité)
    @bot.tree.command(name="confirm_reset_points", description="Confirme la réinitialisation de tous les points (admin seulement)")
    async def confirm_reset_points(interaction: discord.Interaction):
        # Vérifier permissions et contexte
        pending = getattr(bot, '_reset_points_pending', None)
        if not pending or pending["user_id"] != interaction.user.id or pending["channel_id"] != interaction.channel_id:
            await interaction.response.send_message("❌ Aucune demande de confirmation en attente ou non autorisé.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Seuls les administrateurs peuvent confirmer cette action.", ephemeral=True)
            return
        try:
            success, count = reset_points()
            if success:
                if count > 0:
                    await interaction.response.send_message(f"✅ Tous les points ont été réinitialisés ! ({count} points supprimés)")
                else:
                    await interaction.response.send_message("ℹ️ Aucun point n'était enregistré dans la base de données.")
            else:
                await interaction.response.send_message("❌ Une erreur s'est produite lors de la réinitialisation des points.")
        except Exception as e:
            print(f"Erreur dans la commande confirm_reset_points: {str(e)}")
            await interaction.response.send_message("❌ Une erreur s'est produite lors de la réinitialisation des points.")
        finally:
            bot._reset_points_pending = None 