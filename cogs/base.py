from discord.ext import commands
from discord import Embed
import aiosqlite
import time

class BaseCog(commands.Cog):
    def __init__(self, bot, category: str = None):
        self.bot = bot
        self.category = category  # Thêm category để nhóm các lệnh

    # Xử lý lỗi của các lệnh
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Lệnh bạn nhập không tồn tại. Dùng `/help` để xem các lệnh có sẵn.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⚠️ Bạn đang thiếu một hoặc nhiều đối số. Hãy kiểm tra lại lệnh của mình.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ Đối số bạn nhập không hợp lệ.")
        else:
            await ctx.send("⚠️ Lỗi không xác định đã xảy ra.")
    
    # Hàm gửi thông báo lỗi nếu lệnh không có
    async def send_error_message(self, ctx, message: str):
        embed = Embed(
            title="❌ Lỗi",
            description=message,
            color=0xFF0000
        )
        await ctx.send(embed=embed)

# Cài đặt Cog vào bot và chỉ định category
async def setup(bot) -> None:
    # Dùng category để nhóm các lệnh trong phần help
    await bot.add_cog(BaseCog(bot, category="General"))
