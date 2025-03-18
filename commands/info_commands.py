from discord.ext import commands

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
            "**📋 Liste des matchs disponibles :**"
        ]

        # Ajouter la liste des matchs
        for match_id, (team1, team2) in self.bot.matches.items():
            help_message.append(f"**Match {match_id}** : {team1} vs {team2}")
        
        help_message.append("\n-----------------")
        
        await ctx.send("\n".join(help_message))

async def setup(bot):
    await bot.add_cog(InfoCommands(bot))