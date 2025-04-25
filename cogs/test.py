from discord.ext import commands
from .base import BaseCog

class MyCommandCog(BaseCog):
    def __init__(self, bot):
        # Chỉ định category là "MyCategory"
        super().__init__(bot, category="MyCategory")
        
    @commands.hybrid_command(
        name="mycommand",
        description="This is an example command.",
    )
    async def mycommand(self, ctx):
        # Logic for your command here
        pass

async def setup(bot) -> None:
    await bot.add_cog(MyCommandCog(bot))