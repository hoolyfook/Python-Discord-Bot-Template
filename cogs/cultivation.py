import discord
from discord.ext import commands
from discord import Embed
from database.mongodb import mongodb
import random

class Cultivation(commands.Cog, name="Tu luyện"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.levels = {
            # Luyện Khí
            0: {"name": "Luyện Khí tầng 1 ", "points_required": 1000},
            1: {"name": "Luyện Khí tầng 2 ", "points_required": 1322},
            2: {"name": "Luyện Khí tầng 3 ", "points_required": 1748},
            3: {"name": "Luyện Khí tầng 4 ", "points_required": 2311},
            4: {"name": "Luyện Khí tầng 5 ", "points_required": 3056},
            5: {"name": "Luyện Khí tầng 6 ", "points_required": 4040},
            6: {"name": "Luyện Khí tầng 7 ", "points_required": 5341},
            7: {"name": "Luyện Khí tầng 8 ", "points_required": 7061},
            8: {"name": "Luyện Khí tầng 9 ", "points_required": 9336},
            9: {"name": "Luyện Khí tầng 10 ", "points_required": 12342},
            
            # Trúc Cơ
            10: {"name": "Trúc Cơ Sơ Kỳ", "points_required": 16316},
            11: {"name": "Trúc Cơ Trung Kỳ", "points_required": 21570},
            12: {"name": "Trúc Cơ Hậu Kỳ", "points_required": 28516},
            13: {"name": "Trúc Cơ Đại Viên Mãn", "points_required": 37698},
            
            # Kim Đan
            14: {"name": "Kim Đan Sơ Kỳ", "points_required": 49837},
            15: {"name": "Kim Đan Trung Kỳ", "points_required": 65884},
            16: {"name": "Kim Đan Hậu Kỳ", "points_required": 87100},
            17: {"name": "Kim Đan Đại Viên Mãn", "points_required": 115139},
            
            # Nguyên Anh
            18: {"name": "Nguyên Anh Sơ Kỳ", "points_required": 152216},
            19: {"name": "Nguyên Anh Trung Kỳ", "points_required": 201230},
            20: {"name": "Nguyên Anh Hậu Kỳ", "points_required": 266026},
            21: {"name": "Nguyên Anh Đại Viên Mãn", "points_required": 351686},
            
            # Hóa Thần
            22: {"name": "Hóa Thần Sơ Kỳ", "points_required": 464929},
            23: {"name": "Hóa Thần Trung Kỳ", "points_required": 614657},
            24: {"name": "Hóa Thần Hậu Kỳ", "points_required": 812617},
            25: {"name": "Hóa Thần Đại Viên Mãn", "points_required": 1074386},
            
            # Luyện Hư
            26: {"name": "Luyện Hư Sơ Kỳ", "points_required": 1420328},
            27: {"name": "Luyện Hư Trung Kỳ", "points_required": 1877774},
            28: {"name": "Luyện Hư Hậu Kỳ", "points_required": 2482517},
            29: {"name": "Luyện Hư Đại Viên Mãn", "points_required": 3282117},
            
            # Hợp Thể
            30: {"name": "Hợp Thể Sơ Kỳ", "points_required": 4338959},
            31: {"name": "Hợp Thể Trung Kỳ", "points_required": 5736319},
            32: {"name": "Hợp Thể Hậu Kỳ", "points_required": 7583529},
            33: {"name": "Hợp Thể Đại Viên Mãn", "points_required": 10025938},
            
            # Đại Thừa
            34: {"name": "Đại Thừa Sơ Kỳ", "points_required": 13254290},
            35: {"name": "Đại Thừa Trung Kỳ", "points_required": 17523171},
            36: {"name": "Đại Thừa Hậu Kỳ", "points_required": 23165632},
            37: {"name": "Đại Thừa Đại Viên Mãn", "points_required": 30627010},
            
            # Bán Đế
            38: {"name": "Bán Đế Sơ Kỳ", "points_required": 40489026},
            39: {"name": "Bán Đế Trung Kỳ", "points_required": 53526534},
            40: {"name": "Bán Đế Hậu Kỳ", "points_required": 70760085},
            41: {"name": "Bán Đế Đại Viên Mãn", "points_required": 93544892},
            
            # Đại Đế
            42: {"name": "Đại Đế Sơ Kỳ", "points_required": 123664275},
            43: {"name": "Đại Đế Trung Kỳ", "points_required": 163484171},
            44: {"name": "Đại Đế Hậu Kỳ", "points_required": 216125674},
            45: {"name": "Đại Đế Đại Viên Mãn", "points_required": 285718142}
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
            await context.send(f"❌ Bạn cần {required_points:,} điểm tu vi để đột phá lên cấp {next_level} ({self.levels[next_level]['name']})!")
            return
            
        # Tính tỷ lệ thành công dựa trên tỷ lệ điểm tu vi
        success_rate = min(100, (current_points / required_points) * 100)
        
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
            embed.add_field(name="Điểm tu vi còn lại", value=f"{current_points - required_points:,}", inline=False)
            embed.add_field(name="Lời khuyên", value="Hãy tích lũy thêm điểm tu vi và thử lại sau!", inline=False)
            await context.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Cultivation(bot)) 