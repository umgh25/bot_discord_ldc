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
            "-----------------"
        ]
        
        await ctx.send("\n".join(help_message))

async def setup(bot):
    await bot.add_cog(InfoCommands(bot))