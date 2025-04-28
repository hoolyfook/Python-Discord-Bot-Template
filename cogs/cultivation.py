import discord
from discord.ext import commands
from discord import Embed
from database.mongodb import mongodb
import random

class Cultivation(commands.Cog, name="Tu luyện"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.levels = {
            0: {"name": "Phàm Nhân", "points_required": 1000},
            1: {"name": "Luyện Khí", "points_required": 2000},
            2: {"name": "Trúc Cơ", "points_required": 5000},
            3: {"name": "Kim Đan", "points_required": 10000},
            4: {"name": "Nguyên Anh", "points_required": 20000},
            5: {"name": "Hóa Thần", "points_required": 50000},
            6: {"name": "Hợp Thể", "points_required": 100000},
            7: {"name": "Đại Thừa", "points_required": 200000},
            8: {"name": "Tiên Nhân", "points_required": 500000},
            9: {"name": "Kim Tiên", "points_required": 1000000},
            10: {"name": "Đại La Kim Tiên", "points_required": 2000000}
        }

    @commands.hybrid_command(
        name="dotpha",
        description="Thử đột phá lên cấp độ tu luyện cao hơn"
    )
    async def dotpha(self, context: commands.Context) -> None:
        """
        Thử đột phá lên cấp độ tu luyện cao hơn
        """
        user_id = str(context.author.id)
        user = await mongodb.get_user(user_id)
        
        if not user:
            await context.send("❌ Bạn chưa có dữ liệu tu luyện!")
            return
            
        current_level = user.get("cultivation_level", 0)
        current_points = user.get("cultivation_points", 0)
        
        if current_level >= max(self.levels.keys()):
            await context.send("❌ Bạn đã đạt đến cấp độ tối đa!")
            return
            
        next_level = current_level + 1
        required_points = self.levels[next_level]["points_required"]
        
        if current_points < required_points:
            await context.send(f"❌ Bạn cần {required_points} điểm tu vi để đột phá lên cấp {next_level}!")
            return
            
        # Tính tỷ lệ thành công
        success_rate = min(100, 30 + (current_points - required_points) / 100)
        if random.random() * 100 <= success_rate:
            # Đột phá thành công
            await mongodb.update_user(user_id, {
                "cultivation_level": next_level,
                "cultivation_points": 0
            })
            
            embed = Embed(
                title="🎉 Đột Phá Thành Công!",
                description=f"Chúc mừng {context.author.mention} đã đột phá thành công lên cấp độ {next_level} ({self.levels[next_level]['name']})!",
                color=0x00FF00
            )
            embed.add_field(name="Cấp độ mới", value=f"{next_level} ({self.levels[next_level]['name']})", inline=False)
            embed.add_field(name="Điểm tu vi", value="0 (đã reset)", inline=False)
            await context.send(embed=embed)
        else:
            # Đột phá thất bại
            await mongodb.update_user(user_id, {
                "cultivation_points": 0
            })
            
            embed = Embed(
                title="❌ Đột Phá Thất Bại!",
                description=f"Rất tiếc {context.author.mention}, bạn đã đột phá thất bại!",
                color=0xFF0000
            )
            embed.add_field(name="Điểm tu vi còn lại", value=f"{current_points - required_points}", inline=False)
            await context.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Cultivation(bot)) 