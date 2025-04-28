import discord
from discord.ext import commands
from discord import Embed
from database.mongodb import mongodb
import random
import json
from datetime import datetime

class Mining(commands.Cog, name="Khai thác thạch"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.mining_rates = {
            0: {"success_rate": 0.05, "attempts": 3, "cooldown": 3600},  # Thường dân
            1: {"success_rate": 0.10, "attempts": 4, "cooldown": 2700},  # Luyện Khí
            2: {"success_rate": 0.15, "attempts": 5, "cooldown": 1800},  # Trúc Cơ
            3: {"success_rate": 0.20, "attempts": 6, "cooldown": 1500},  # Kim Đan
            4: {"success_rate": 0.25, "attempts": 7, "cooldown": 1200},  # Nguyên Anh
            5: {"success_rate": 0.30, "attempts": 8, "cooldown": 900},   # Hóa Thần
            6: {"success_rate": 0.35, "attempts": 9, "cooldown": 600},   # Hợp Thể
            7: {"success_rate": 0.40, "attempts": 10, "cooldown": 300},  # Đại Thừa
            8: {"success_rate": 0.50, "attempts": 12, "cooldown": 60}    # Tiên Nhân
        }
        
        self.spirit_stones = {
            0: {"min": 100, "max": 500},    # Hạ Phẩm (Thường dân)
            1: {"min": 500, "max": 1000},   # Hạ Phẩm (Luyện Khí)
            2: {"min": 1000, "max": 5000},  # Trung Phẩm (Trúc Cơ)
            3: {"min": 5000, "max": 10000}, # Trung Phẩm (Kim Đan)
            4: {"min": 10000, "max": 50000},# Thượng Phẩm (Nguyên Anh)
            5: {"min": 50000, "max": 100000},# Thượng Phẩm (Hóa Thần)
            6: {"min": 100000, "max": 500000},# Cực Phẩm (Hợp Thể)
            7: {"min": 500000, "max": 1000000},# Cực Phẩm (Đại Thừa)
            8: {"min": 1000000, "max": 5000000} # Thần Phẩm (Tiên Nhân)
        }

    async def ensure_user(self, user_id: str, username: str = None) -> None:
        user = await mongodb.get_user(user_id)
        if not user:
            user_data = {
                "_id": user_id,
                "username": username,
                "spirit_stones": 0,
                "cultivation_level": 0,
                "failed_rob_attempts": 0,
                "last_checkin": 0,
                "inventory": {},
                "cultivation_points": 0,
                "mining_attempts": 0,
                "last_mining": 0
            }
            await mongodb.update_user(user_id, user_data)
        elif username and user.get("username") != username:
            await mongodb.update_user(user_id, {"username": username})

    @commands.hybrid_command(
        name="khaithac",
        description="Khai thác Linh Thạch <:linhthachydon:1366455607812427807>"
    )
    async def khaithac(self, ctx: commands.Context) -> None:
        """
        Khai thác Linh Thạch
        """
        user_id = str(ctx.author.id)
        await self.ensure_user(user_id, username=ctx.author.name)
        user = await mongodb.get_user(user_id)
        
        # Kiểm tra thời gian chờ
        current_time = datetime.now().timestamp()
        last_mining = user.get("last_mining", 0)
        mining_attempts = user.get("mining_attempts", 0)
        
        if mining_attempts >= 1000:
            await ctx.send("❌ Bạn đã sử dụng hết số lần khai thác hôm nay!")
            return
            
        if current_time - last_mining < 1:
            remaining_time = 1 - (current_time - last_mining)
            seconds = int(remaining_time)
            await ctx.send(f"❌ Bạn cần chờ thêm {seconds} giây nữa mới có thể khai thác!")
            return
            
        # Kiểm tra tỷ lệ thành công
        if random.random() > 0.5:
            await mongodb.update_user(user_id, {
                "mining_attempts": mining_attempts + 1,
                "last_mining": current_time
            })
            await ctx.send("❌ Khai thác thất bại! Không tìm thấy Linh Thạch.")
            return
            
        # Tính toán số Linh Thạch nhận được
        spirit_stones_found = random.randint(100, 500)
        
        # Cập nhật dữ liệu người dùng
        await mongodb.update_user(user_id, {
            "spirit_stones": user.get("spirit_stones", 0) + spirit_stones_found,
            "mining_attempts": mining_attempts + 1,
            "last_mining": current_time
        })
        
        # Tạo embed thông báo
        embed = discord.Embed(
            title="Khai thác thành công!",
            description=f"Bạn đã tìm thấy {spirit_stones_found} Linh Thạch <:linhthachydon:1366455607812427807>",
            color=0x00FF00
        )
        embed.add_field(name="Số lần còn lại", value=f"{1000 - (mining_attempts + 1)}", inline=True)
        await ctx.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Mining(bot)) 