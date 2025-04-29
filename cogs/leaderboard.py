import discord
from discord.ext import commands
from discord import Embed
from database.mongodb import MongoDB
from datetime import datetime
from utils.constants import CULTIVATION_LEVELS, LEVEL_REQUIREMENTS

class Leaderboard(commands.Cog, name="Bảng xếp hạng"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.mongodb = MongoDB()
        self.cultivation_levels = CULTIVATION_LEVELS
        self.level_requirements = LEVEL_REQUIREMENTS

    def get_cultivation_info(self, level):
        level_info = self.cultivation_levels.get(level, {
            "name": "Unknown",
            "color": 0xAAAAAA,
            "description": "Cảnh giới không xác định",
            "tho_nguyen": "Unknown"
        })
        return level_info["name"]

    @commands.hybrid_command(
        name="diachubang",
        aliases=["dcb", "cocc"],
        description="Hiển thị top 10 người giàu nhất"
    )
    async def topgiau(self, context: commands.Context) -> None:
        """
        Hiển thị top 10 người giàu nhất dựa trên số linh thạch
        """
        # Lấy top 10 người dùng có nhiều linh thạch nhất
        top_users = await self.mongodb.get_top_users(10, sort_by="spirit_stones")
        
        if not top_users:
            embed = discord.Embed(
                title="Top Người Giàu",
                description="Chưa có dữ liệu xếp hạng!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)
            return

        embed = discord.Embed(
            title="💰 Top 10 Người Giàu Nhất",
            description="Dựa trên số lượng Linh Thạch sở hữu",
            color=0xFFD700
        )

        for i, user in enumerate(top_users, 1):
            embed.add_field(
                name=f"{i}. {user.get('username', 'Unknown')}",
                value=f"**Linh Thạch:** {user.get('spirit_stones', 0):,} 🪨",
                inline=False
            )

        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="topkhaithac",
        aliases=["topmining", "khaithacnhat"],
        description="Hiển thị top 10 người khai thác nhiều nhất"
    )
    async def topkhaithac(self, context: commands.Context) -> None:
        """
        Hiển thị top 10 người khai thác nhiều nhất
        """
        # Lấy top 10 người dùng có số lần khai thác nhiều nhất
        top_users = await self.mongodb.get_top_users(10, sort_by="mining_attempts")
        
        if not top_users:
            embed = discord.Embed(
                title="Top Khai Thác",
                description="Chưa có dữ liệu xếp hạng!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)
            return

        embed = discord.Embed(
            title="⛏️ Top 10 Người Khai Thác Nhiều Nhất",
            description="Dựa trên số lần khai thác",
            color=0x1E90FF
        )

        for i, user in enumerate(top_users, 1):
            embed.add_field(
                name=f"{i}. {user.get('username', 'Unknown')}",
                value=f"**Số lần khai thác:** {user.get('mining_attempts', 0):,}",
                inline=False
            )

        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="topdotpha",
        aliases=["topbreakthrough", "dotphanhat"],
        description="Hiển thị top 10 người đột phá nhiều nhất"
    )
    async def topdotpha(self, context: commands.Context) -> None:
        """
        Hiển thị top 10 người có cấp độ tu luyện cao nhất
        """
        # Lấy top 10 người dùng có cấp độ tu luyện cao nhất
        top_users = await self.mongodb.get_top_users(10, sort_by="cultivation_level")
        
        if not top_users:
            embed = discord.Embed(
                title="Top Đột Phá",
                description="Chưa có dữ liệu xếp hạng!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)
            return

        embed = discord.Embed(
            title="🌟 Top 10 Người Đột Phá Nhiều Nhất",
            description="Dựa trên cấp độ tu luyện",
            color=0x9932CC
        )

        for i, user in enumerate(top_users, 1):
            embed.add_field(
                name=f"{i}. {user.get('username', 'Unknown')}",
                value=f"**Cấp độ:** {user.get('cultivation_level', 0)}\n**Điểm tu vi:** {user.get('cultivation_points', 0):,}",
                inline=False
            )

        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await context.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Leaderboard(bot)) 