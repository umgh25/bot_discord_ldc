import discord
from discord import app_commands
import asyncio
import logging

logger = logging.getLogger(__name__)

def setup(bot, matches, vote_locks):
    """Configure les commandes de vote pour le bot"""
    
    @bot.tree.command(name="vote", description="Voter pour une équipe dans un match spécifique")
    @app_commands.describe(
        match_id="Numéro du match (1-8)",
        equipe="Nom de l'équipe pour laquelle vous votez"
    )
    async def vote(interaction: discord.Interaction, match_id: int, equipe: str):
        # Vérifier si l'utilisateur a un vote en cours
        user_id = str(interaction.user.id)
        if user_id in vote_locks:
            await interaction.response.send_message("⚠️ Veuillez attendre que votre vote précédent soit terminé.", ephemeral=True)
            return
            
        vote_locks[user_id] = True
        try:
            logger.info(f"=== DÉBUT COMMANDE VOTE ===")
            logger.info(f"Match ID: {match_id}")
            logger.info(f"Team: {equipe}")
            
            # Vérifications habituelles...
            if match_id not in matches:
                await interaction.response.send_message(f"❌ Match {match_id} invalide. Les matchs disponibles sont de 1 à {len(matches)}.", ephemeral=True)
                return

            team1, team2 = matches[match_id]
            equipe = equipe.strip()
            
            if equipe.lower() not in [team1.lower(), team2.lower()]:
                await interaction.response.send_message(
                    f"❌ Équipe invalide. Pour le match {match_id}, vous pouvez seulement voter pour :\n- **{team1}**\n- **{team2}**", 
                    ephemeral=True
                )
                return
            
            equipe = team1 if equipe.lower() == team1.lower() else team2
            
            # Attendre un court instant pour éviter les doublons
            await asyncio.sleep(0.5)
            
            success = save_vote(user_id, match_id, equipe)
            
            if success:
                await interaction.response.send_message(
                    f"✅ {interaction.user.mention}, tu as voté pour **{equipe}** dans le match **{team1}** vs **{team2}**."
                )
            else:
                await interaction.response.send_message(
                    f"❌ {interaction.user.mention}, il y a eu une erreur lors de l'enregistrement de ton vote.", 
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Erreur lors du vote: {str(e)}")
            await interaction.response.send_message(f"❌ Une erreur s'est produite lors du vote.", ephemeral=True)
        finally:
            # Toujours libérer le verrou
            if user_id in vote_locks:
                del vote_locks[user_id]
        
        logger.info("=== FIN COMMANDE VOTE ===")

    @bot.tree.command(name="modifier_vote", description="Modifier un vote existant pour un match")
    @app_commands.describe(
        match_id="Numéro du match à modifier",
        equipe="Nouvelle équipe pour laquelle vous votez"
    )
    async def modifier_vote(interaction: discord.Interaction, match_id: int, equipe: str):
        user_id = str(interaction.user.id)
        
        try:
            # Vérifier si le match existe
            if match_id not in matches:
                await interaction.response.send_message(
                    f"❌ Match {match_id} invalide. Les matchs disponibles sont de 1 à {len(matches)}.", 
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

            team1, team2 = matches[match_id]
            ancien_vote = result.data[0]["choice"]

            # Normaliser le nom de l'équipe pour la comparaison
            equipe = equipe.strip()
            if equipe.lower() not in [team1.lower(), team2.lower()]:
                await interaction.response.send_message(
                    f"❌ Équipe invalide. Pour le match {match_id}, vous pouvez seulement voter pour :\n- **{team1}**\n- **{team2}**", 
                    ephemeral=True
                )
                return

            # Si l'utilisateur vote pour la même équipe
            if equipe.lower() == ancien_vote.lower():
                await interaction.response.send_message(
                    f"ℹ️ Vous avez déjà voté pour **{ancien_vote}** dans ce match.", 
                    ephemeral=True
                )
                return

            # Trouver le nom exact de l'équipe (pour garder la casse correcte)
            equipe = team1 if equipe.lower() == team1.lower() else team2

            # Modifier le vote dans Supabase
            supabase.table("votes").update({"choice": equipe}).eq("user_id", user_id).eq("match_id", match_id).execute()

            await interaction.response.send_message(
                f"✅ {interaction.user.mention}, votre vote a été modifié !\n"
                f"**Match {match_id}** : {team1} vs {team2}\n"
                f"└─ Ancien vote : **{ancien_vote}**\n"
                f"└─ Nouveau vote : **{equipe}** 🔄"
            )

        except Exception as e:
            logger.error(f"Erreur lors de la modification du vote: {str(e)}")
            await interaction.response.send_message(f"❌ Une erreur s'est produite lors de la modification du vote.", ephemeral=True)

    @bot.tree.command(name="supprimer_vote", description="Supprimer un vote existant")
    @app_commands.describe(match_id="Numéro du match dont vous voulez supprimer le vote")
    async def supprimer_vote(interaction: discord.Interaction, match_id: int):
        user_id = str(interaction.user.id)
        
        try:
            # Vérifier si le vote existe
            result = supabase.table("votes").select("*").eq("user_id", user_id).eq("match_id", match_id).execute()
            
            if not result.data:
                await interaction.response.send_message(
                    f"❌ {interaction.user.mention}, tu n'as pas encore voté pour le match {match_id}.", 
                    ephemeral=True
                )
                return
            
            # Suppression du vote
            supabase.table("votes").delete().eq("user_id", user_id).eq("match_id", match_id).execute()
            
            # Récupérer les équipes du match pour le message
            if match_id in matches:
                team1, team2 = matches[match_id]
                await interaction.response.send_message(
                    f"✅ {interaction.user.mention}, ton vote pour le match {match_id} ({team1} vs {team2}) a été supprimé !"
                )
            else:
                await interaction.response.send_message(
                    f"✅ {interaction.user.mention}, ton vote pour le match {match_id} a été supprimé !"
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du vote: {str(e)}")
            await interaction.response.send_message(f"❌ Une erreur s'est produite lors de la suppression du vote.", ephemeral=True)