import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import sys
sys.path.append('../../../config')
sys.path.append('../../database')
sys.path.append('../utils')

from config.settings import MATCHES
from src.database.operations import save_vote, supabase
from ..utils.helpers import check_channel, validate_team, format_match_list

# Dictionnaire pour gérer les verrous des votes
vote_locks = {}

def setup_vote_commands(bot):
    """Configure toutes les commandes de vote"""
    
    @bot.tree.command(name="vote", description="Voter pour une équipe dans un match spécifique")
    @app_commands.describe(
        match_id="Numéro du match (ex: 15 pour la finale)",
        team="Nom de l'équipe pour laquelle voter"
    )
    async def vote_slash(interaction: discord.Interaction, match_id: int, team: str):
        if not check_channel(interaction):
            await interaction.response.send_message(
                f"❌ Cette commande ne peut être utilisée que dans le canal <#{interaction.channel_id}>",
                ephemeral=True
            )
            return
            
        # Vérifier si l'utilisateur a un vote en cours
        user_id = str(interaction.user.id)
        if user_id in vote_locks:
            await interaction.response.send_message(
                "⚠️ Veuillez attendre que votre vote précédent soit terminé.",
                ephemeral=True
            )
            return
            
        vote_locks[user_id] = True
        try:
            print(f"=== DÉBUT COMMANDE VOTE SLASH ===")
            print(f"Match ID: {match_id}")
            print(f"Team: {team}")
            
            # Vérifications habituelles...
            if match_id is None or team is None:
                await interaction.response.send_message(
                    "❌ Format incorrect. Utilisez `/vote <numéro du match> <nom de l'équipe>`",
                    ephemeral=True
                )
                return
            
            # Mise à jour de la vérification pour inclure les nouveaux matchs
            if match_id not in MATCHES:
                await interaction.response.send_message(
                    f"❌ Match {match_id} invalide. Les matchs disponibles sont :\n"
                    "**Finale** : 15",
                    ephemeral=True
                )
                return

            # Valider l'équipe
            is_valid, team1, team2, exact_team = validate_team(match_id, team)
            if not is_valid:
                await interaction.response.send_message(
                    f"❌ Équipe invalide. Pour le match {match_id}, vous pouvez seulement voter pour :\n"
                    f"- **{team1}**\n"
                    f"- **{team2}**",
                    ephemeral=True
                )
                return
            
            # Attendre un court instant pour éviter les doublons
            await asyncio.sleep(0.5)
            
            success = save_vote(user_id, match_id, exact_team)
            
            if success:
                await interaction.response.send_message(
                    f"✅ {interaction.user.mention}, tu as voté pour **{exact_team}** dans le match **{team1}** vs **{team2}**."
                )
            else:
                await interaction.response.send_message(
                    f"❌ {interaction.user.mention}, il y a eu une erreur lors de l'enregistrement de ton vote.",
                    ephemeral=True
                )
                
        except Exception as e:
            print(f"Erreur lors du vote (slash): {str(e)}")
            await interaction.response.send_message(
                f"❌ Une erreur s'est produite lors du vote.",
                ephemeral=True
            )
        finally:
            # Toujours libérer le verrou
            if user_id in vote_locks:
                del vote_locks[user_id]
        
        print("=== FIN COMMANDE VOTE SLASH ===")

    @bot.tree.command(name="supprimer_vote", description="Supprime votre vote pour un match spécifique.")
    async def supprimer_vote(interaction: discord.Interaction, match_id: int):
        if not check_channel(interaction):
            await interaction.response.send_message(
                f"❌ Cette commande ne peut être utilisée que dans le canal <#{interaction.channel_id}>",
                ephemeral=True
            )
            return
        user_id = str(interaction.user.id)
        
        try:
            # Vérifier si le vote existe
            result = supabase.table("votes").select("*").eq("user_id", user_id).eq("match_id", match_id).execute()
            
            if not result.data:
                await interaction.response.send_message(f"❌ {interaction.user.mention}, tu n'as pas encore voté pour le match {match_id}.")
                return
            
            # Suppression du vote
            supabase.table("votes").delete().eq("user_id", user_id).eq("match_id", match_id).execute()
            
            # Récupérer les équipes du match pour le message
            if match_id in MATCHES:
                team1, team2 = MATCHES[match_id]
                await interaction.response.send_message(f"✅ {interaction.user.mention}, ton vote pour le match {match_id} ({team1} vs {team2}) a été supprimé !")
            else:
                await interaction.response.send_message(f"✅ {interaction.user.mention}, ton vote pour le match {match_id} a été supprimé !")
                
        except Exception as e:
            print(f"Erreur lors de la suppression du vote: {str(e)}")
            await interaction.response.send_message(f"❌ Une erreur s'est produite lors de la suppression du vote.")

    @bot.tree.command(name="modifier_vote", description="Modifie votre vote pour un match spécifique.")
    async def modifier_vote_slash(interaction: discord.Interaction, match_id: int, team: str):
        if not check_channel(interaction):
            await interaction.response.send_message(
                f"❌ Cette commande ne peut être utilisée que dans le canal <#{interaction.channel_id}>",
                ephemeral=True
            )
            return
        user_id = str(interaction.user.id)
        
        try:
            # Vérifier si le match existe
            if match_id not in MATCHES:
                await interaction.response.send_message(
                    f"❌ Match {match_id} invalide. Les matchs disponibles sont :\n**Finale** : 15",
                    ephemeral=True
                )
                return

            # Vérifier si l'utilisateur a déjà voté pour ce match
            result = supabase.table("votes").select("*").eq("user_id", user_id).eq("match_id", match_id).execute()
            
            if not result.data:
                await interaction.response.send_message(
                    f"❌ Vous n'avez pas encore voté pour le match {match_id}. Utilisez `/vote` pour voter.",
                    ephemeral=True
                )
                return

            # Valider l'équipe
            is_valid, team1, team2, exact_team = validate_team(match_id, team)
            if not is_valid:
                await interaction.response.send_message(
                    f"❌ Équipe invalide. Pour le match {match_id}, vous pouvez seulement voter pour :\n- **{team1}**\n- **{team2}**",
                    ephemeral=True
                )
                return

            ancien_vote = result.data[0]["choice"]

            # Si l'utilisateur vote pour la même équipe
            if exact_team.lower() == ancien_vote.lower():
                await interaction.response.send_message(
                    f"ℹ️ Vous avez déjà voté pour **{ancien_vote}** dans ce match.",
                    ephemeral=True
                )
                return

            # Modifier le vote dans Supabase
            supabase.table("votes").update({"choice": exact_team}).eq("user_id", user_id).eq("match_id", match_id).execute()

            await interaction.response.send_message(
                f"✅ {interaction.user.mention}, votre vote a été modifié !\n"
                f"**Match {match_id}** : {team1} vs {team2}\n"
                f"└─ Ancien vote : **{ancien_vote}**\n"
                f"└─ Nouveau vote : **{exact_team}** 🔄"
            )

        except Exception as e:
            print(f"Erreur lors de la modification du vote: {str(e)}")
            await interaction.response.send_message(
                f"❌ Une erreur s'est produite lors de la modification du vote.",
                ephemeral=True
            ) 