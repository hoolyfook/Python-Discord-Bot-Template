import discord
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime
from database.mongodb import mongodb
from discord.ext import app_commands

class Leaderboard(commands.Cog, name="leaderboard"):
    def __init__(self, bot) -> None:
        super().__init__(bot, register_context_menu=False)
        self.bot = bot
        self.cultivation_levels = [
            # (Tên, [Các kỳ nhỏ/tầng], Thọ nguyên, Màu sắc, Mô tả)
            ("Phàm Nhân", [], "70-100", 0xAAAAAA, "Người thường, chưa tu luyện."),
            ("Luyện Khí", [f"{i} tầng" for i in range(1, 10)], "120-150", 0xCCCCCC, "Bước đầu hấp thu linh khí."),
            ("Trúc Cơ", ["Sơ Kỳ", "Trung Kỳ", "Hậu Kỳ", "Viên Mãn"], "200-300", 0x00FF00, "Xây dựng nền tảng tu luyện."),
            ("Kim Đan", ["Sơ Kỳ", "Trung Kỳ", "Hậu Kỳ", "Viên Mãn"], "500-800", 0xFFD700, "Kết tinh linh lực thành kim đan."),
            ("Nguyên Anh", ["Sơ Kỳ", "Trung Kỳ", "Hậu Kỳ", "Viên Mãn"], "1000-1500", 0xFF4500, "Ngưng tụ nguyên anh."),
            ("Hóa Thần", ["Sơ Kỳ", "Trung Kỳ", "Hậu Kỳ", "Viên Mãn"], "2000-3000", 0x9932CC, "Hóa thần thành tiên."),
            ("Luyện Hư", ["Sơ Kỳ", "Trung Kỳ", "Hậu Kỳ", "Viên Mãn"], "4000-6000", 0x4169E1, "Luyện hư thành thực."),
            ("Hợp Thể", ["Sơ Kỳ", "Trung Kỳ", "Hậu Kỳ", "Viên Mãn"], "8000-10000", 0xFF0000, "Hợp nhất với thiên địa."),
            ("Đại Thừa", ["Sơ Kỳ", "Trung Kỳ", "Hậu Kỳ", "Viên Mãn"], "20000-30000", 0xFFFFFF, "Đạt đến cảnh giới tối cao."),
            ("Phi Thăng", ["Qua Kiếp Độ"], "", 0x00FFFF, "Độ kiếp phi thăng."),
            # Tiên Nhân trở lên
            ("Chân Tiên", [], "Vô hạn", 0xFFD700, "Bước vào hàng ngũ tiên nhân."),
            ("Huyền Tiên", [], "Vô hạn", 0xBEBEFE, "Cảnh giới cao hơn Chân Tiên."),
            ("Kim Tiên", [], "Vô hạn", 0xFFD700, "Cảnh giới Kim Tiên."),
            ("Thái Ất Chân Tiên", [], "Vô hạn", 0xFF00FF, "Cảnh giới Thái Ất Chân Tiên."),
            ("Đại La Kim Tiên", [], "Vô hạn", 0x00FF00, "Cảnh giới Đại La Kim Tiên."),
            ("Thánh Nhân", [], "Vô hạn", 0xFF0000, "Cảnh giới Thánh Nhân, tối thượng.")
        ]

    def get_cultivation_info(self, level: int) -> tuple:
        """Trả về thông tin về cảnh giới và giai đoạn tu luyện"""
        for realm, info in self.cultivation_levels.items():
            for stage, stage_level in info["levels"].items():
                if level == stage_level:
                    return realm, stage, info["color"]
        return "Không xác định", "Không xác định", 0x000000

    @commands.hybrid_command(
        name="tiemlongbang",
        aliases=["tlb"],
        description="Xem bảng xếp hạng top 10 tu sĩ"
    )
    async def leaderboard(self, ctx: Context) -> None:
        users = await mongodb.get_top_users(10)

        if not users:
            embed = discord.Embed(
                title="🏆 Tiềm Long Bảng 🏆",
                description="Chưa có ai trên bảng xếp hạng Tiềm Long!",
                color=0xFFD700
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        # Tạo danh sách các emoji cho top 3
        rank_emojis = {
            1: "🥇",
            2: "🥈",
            3: "🥉"
        }

        embed = discord.Embed(
            title="🏆 Tiềm Long Bảng 🏆",
            description="Xếp hạng các tu sĩ mạnh nhất!",
            color=0xFFD700
        )

        for i, user in enumerate(users, 1):
            realm, stage, color = self.get_cultivation_info(user["cultivation_level"])
            
            # Thêm emoji cho top 3
            rank_emoji = rank_emojis.get(i, f"#{i}")
            
            # Tạo thanh tiến trình tu vi
            progress = "█" * (user["cultivation_level"] % 4 + 1) + "░" * (3 - user["cultivation_level"] % 4)
            
            # Tạo giá trị hiển thị
            value = (
                f"**Cảnh Giới:** {realm}\n"
                f"**Giai Đoạn:** {stage}\n"
                f"**Tiến Trình:** [{progress}]\n"
                f"**Linh Thạch:** {user['spirit_stones']:,} 🪨"
            )
            
            embed.add_field(
                name=f"{rank_emoji} {user['username']}",
                value=value,
                inline=False
            )

        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="top10",
        description="Xem bảng xếp hạng top 10 tu sĩ"
    )
    async def top10(self, ctx: Context) -> None:
        users = await mongodb.get_top_users(10)

        if not users:
            embed = discord.Embed(
                title="🏆 Top 10 Tu Sĩ 🏆",
                description="Chưa có ai trên bảng xếp hạng!",
                color=0xFFD700
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        # Tạo danh sách các emoji cho top 3
        rank_emojis = {
            1: "👑",
            2: "🌟",
            3: "⭐"
        }

        embed = discord.Embed(
            title="🏆 Top 10 Tu Sĩ 🏆",
            description="Xếp hạng các tu sĩ mạnh nhất!",
            color=0xFFD700
        )

        for i, user in enumerate(users, 1):
            realm, stage, color = self.get_cultivation_info(user["cultivation_level"])
            
            # Thêm emoji cho top 3
            rank_emoji = rank_emojis.get(i, f"#{i}")
            
            # Tạo thanh tiến trình tu vi
            progress = "█" * (user["cultivation_level"] % 4 + 1) + "░" * (3 - user["cultivation_level"] % 4)
            
            # Tạo giá trị hiển thị
            value = (
                f"**Cảnh Giới:** {realm}\n"
                f"**Giai Đoạn:** {stage}\n"
                f"**Tiến Trình:** [{progress}]\n"
                f"**Linh Thạch:** {user['spirit_stones']:,} 🪨"
            )
            
            embed.add_field(
                name=f"{rank_emoji} {user['username']}",
                value=value,
                inline=False
            )

        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await ctx.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Leaderboard(bot)) 