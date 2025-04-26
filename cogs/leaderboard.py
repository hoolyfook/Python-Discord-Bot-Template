import discord
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime
from database.mongodb import mongodb

class Leaderboard(commands.Cog, name="leaderboard"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.cultivation_levels = {
            "Luyện Khí": {
                "levels": {
                    "Sơ Kỳ": 0,
                    "Trung Kỳ": 1,
                    "Hậu Kỳ": 2,
                    "Đại Viên Mãn": 3
                },
                "color": 0x00FF00
            },
            "Trúc Cơ": {
                "levels": {
                    "Sơ Kỳ": 4,
                    "Trung Kỳ": 5,
                    "Hậu Kỳ": 6,
                    "Đại Viên Mãn": 7
                },
                "color": 0x00FFFF
            },
            "Kim Đan": {
                "levels": {
                    "Sơ Kỳ": 8,
                    "Trung Kỳ": 9,
                    "Hậu Kỳ": 10,
                    "Đại Viên Mãn": 11
                },
                "color": 0xFFD700
            },
            "Nguyên Anh": {
                "levels": {
                    "Sơ Kỳ": 12,
                    "Trung Kỳ": 13,
                    "Hậu Kỳ": 14,
                    "Đại Viên Mãn": 15
                },
                "color": 0xFF4500
            },
            "Hóa Thần": {
                "levels": {
                    "Sơ Kỳ": 16,
                    "Trung Kỳ": 17,
                    "Hậu Kỳ": 18,
                    "Đại Viên Mãn": 19
                },
                "color": 0x9932CC
            },
            "Luyện Hư": {
                "levels": {
                    "Sơ Kỳ": 20,
                    "Trung Kỳ": 21,
                    "Hậu Kỳ": 22,
                    "Đại Viên Mãn": 23
                },
                "color": 0x4169E1
            },
            "Hợp Thể": {
                "levels": {
                    "Sơ Kỳ": 24,
                    "Trung Kỳ": 25,
                    "Hậu Kỳ": 26,
                    "Đại Viên Mãn": 27
                },
                "color": 0xFF0000
            },
            "Đại Thừa": {
                "levels": {
                    "Sơ Kỳ": 28,
                    "Trung Kỳ": 29,
                    "Hậu Kỳ": 30,
                    "Đại Viên Mãn": 31
                },
                "color": 0xFFFFFF
            },
            "Bán Đế": {
                "levels": {
                    "Sơ Kỳ": 32,
                    "Trung Kỳ": 33,
                    "Hậu Kỳ": 34,
                    "Đại Viên Mãn": 35
                },
                "color": 0xFF00FF
            },
            "Đại Đế": {
                "levels": {
                    "Sơ Kỳ": 36,
                    "Trung Kỳ": 37,
                    "Hậu Kỳ": 38,
                    "Đại Viên Mãn": 39
                },
                "color": 0x000000
            }
        }

    def get_cultivation_info(self, level: int) -> tuple:
        """Trả về thông tin về cảnh giới và giai đoạn tu luyện"""
        for realm, info in self.cultivation_levels.items():
            for stage, stage_level in info["levels"].items():
                if level == stage_level:
                    return realm, stage, info["color"]
        return "Không xác định", "Không xác định", 0x000000

    @commands.hybrid_command(
        name="tiemlongbang",
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