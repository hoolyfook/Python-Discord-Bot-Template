import discord
from discord.ext import commands
from discord import Embed
from database.mongodb import MongoDB
from datetime import datetime
from utils.constants import CULTIVATION_LEVELS, LEVEL_REQUIREMENTS
import random

class Gamble(commands.Cog, name="Cờ bạc"):
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
        name="taixiu",
        description="Chơi tài xỉu với linh thạch"
    )
    async def taixiu(self, context: commands.Context, choice: str, bet: int) -> None:
        """
        Chơi tài xỉu với linh thạch
        choice: "tai" hoặc "xiu"
        bet: Số linh thạch muốn cược
        """
        # Validate choice
        choice = choice.lower()
        if choice not in ["tai", "xiu"]:
            await context.send("❌ Lựa chọn không hợp lệ! Chỉ được chọn 'tai' hoặc 'xiu'")
            return

        # Validate bet amount
        if bet <= 0:
            await context.send("❌ Số linh thạch cược phải lớn hơn 0!")
            return

        user_id = str(context.author.id)
        user = await self.mongodb.get_user(user_id)
        
        if not user:
            await context.send("❌ Bạn chưa có dữ liệu người chơi!")
            return

        spirit_stones = user.get("spirit_stones", 0)
        if spirit_stones < bet:
            await context.send(f"❌ Bạn không đủ linh thạch! Bạn có {spirit_stones} linh thạch <:linhthachydon:1366455607812427807>.")
            return

        # Roll 3 dice
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        dice3 = random.randint(1, 6)
        total = dice1 + dice2 + dice3

        # Determine result
        result = "tai" if total >= 11 else "xiu"
        
        # Calculate winnings
        if choice == result:
            winnings = bet
            new_spirit_stones = spirit_stones + winnings
            result_text = "🎉 Thắng"
        else:
            winnings = -bet
            new_spirit_stones = spirit_stones + winnings
            result_text = "❌ Thua"

        # Update user's spirit stones
        await self.mongodb.update_user(user_id, {
            "spirit_stones": new_spirit_stones
        })

        # Create embed
        embed = Embed(
            title="🎲 Kết Quả Tài Xỉu",
            color=0x00FF00 if choice == result else 0xFF0000
        )
        embed.add_field(name="Xúc xắc", value=f"🎲 {dice1} 🎲 {dice2} 🎲 {dice3}", inline=False)
        embed.add_field(name="Tổng", value=f"{total} ({result.upper()})", inline=False)
        embed.add_field(name="Lựa chọn", value=choice.upper(), inline=False)
        embed.add_field(name="Kết quả", value=result_text, inline=False)
        embed.add_field(name="Linh thạch", value=f"{winnings:+d} linh thạch", inline=False)
        embed.add_field(name="Linh thạch hiện tại", value=f"{new_spirit_stones} linh thạch <:linhthachydon:1366455607812427807>", inline=False)

        await context.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Gamble(bot)) 