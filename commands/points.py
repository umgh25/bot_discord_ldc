from discord.ext import commands
from database import add_points, reset_points, get_leaderboard

# Dictionnaire des matchs (à déplacer dans un fichier de configuration si nécessaire)
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

class PointsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="point")
    @commands.has_permissions(administrator=True)
    @commands.max_concurrency(1, per=commands.BucketType.user)
    async def point(self, ctx, member: commands.MemberConverter = None, match_id: int = None, point_value: int = None):
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
            
            await ctx.reply(message)
            
        except commands.MaxConcurrencyReached:
            await ctx.send("⚠️ Une commande est déjà en cours pour cet utilisateur.")
        except Exception as e:
            print(f"Erreur dans la commande point: {str(e)}")
            await ctx.send("❌ Une erreur s'est produite lors de l'attribution des points.")

    @commands.command(name="classement")
    async def classement(self, ctx):
        try:
            leaderboard_data = get_leaderboard()
            
            if not leaderboard_data:
                await ctx.send("❌ Aucun point n'a encore été attribué.")
                return
            
            message = "**🏆 CLASSEMENT GÉNÉRAL 🏆**\n\n"
            users_cache = {}
            
            for index, entry in enumerate(leaderboard_data, 1):
                user_id = entry['user_id']
                points = entry['points']
                
                if user_id not in users_cache:
                    try:
                        user = await self.bot.fetch_user(int(user_id))
                        users_cache[user_id] = user.name
                    except:
                        users_cache[user_id] = f"Utilisateur_{user_id}"
                
                username = users_cache[user_id]
                medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else "👤"
                
                message += f"{medal} **{username}** : {points} point(s)\n"
            
            message += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
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

    @commands.command(name="reset_points")
    @commands.has_permissions(administrator=True)
    async def reset_points(self, ctx, member: commands.MemberConverter = None):
        try:
            if member is None:
                confirmation_message = await ctx.send("⚠️ Voulez-vous vraiment réinitialiser **TOUS** les points ?\n"
                                                   "Cette action est irréversible !\n"
                                                   "✅ = Confirmer\n"
                                                   "❌ = Annuler")
                
                await confirmation_message.add_reaction("✅")
                await confirmation_message.add_reaction("❌")
                
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]
                
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                    
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

    @point.error
    @reset_points.error
    async def points_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Seuls les administrateurs peuvent gérer les points.")

async def setup(bot):
    await bot.add_cog(PointsCog(bot)) 