from discord.ext import commands
from discord.ext.commands import Context

class Template(commands.Cog, name="template"):
    def __init__(self, bot) -> None:
        self.bot = bot
        
    @commands.hybrid_command(
        name="testcommand",
        description="This is a testing command that does nothing.",
    )
    async def testcommand(self, context: Context) -> None:
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """
        pass

async def setup(bot) -> None:
    pass
    # await bot.add_cog(Template(bot))
