from discord.ext import commands
from discord import Embed
import aiosqlite
import time

class BaseCog(commands.Cog):
    def __init__(self, bot, category: str = None):
        self.bot = bot
        self.category = category  # Thêm category để nhóm các lệnh

    # Đảm bảo người dùng tồn tại trong cơ sở dữ liệu
    async def ensure_user(self, user_id: str, username: str = None) -> None:
        async with aiosqlite.connect("database/database.db") as db:
            async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
            if not row:
                await db.execute("INSERT INTO users (user_id, username, balance, last_daily) VALUES (?, ?, 0, ?)",
                                 (user_id, username, int(time.time())))
                await db.commit()

    # Xử lý lỗi của các lệnh
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Lệnh bạn nhập không tồn tại. Dùng `/help` để xem các lệnh có sẵn.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⚠️ Bạn đang thiếu một hoặc nhiều đối số. Hãy kiểm tra lại lệnh của mình.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ Đối số bạn nhập không hợp lệ.")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("❌ Có lỗi xảy ra khi thực thi lệnh.")
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
