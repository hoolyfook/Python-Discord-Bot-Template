import time
from discord.ext import commands
from discord.ext.commands import Context
import random
import uuid
import discord
from datetime import datetime
from database.mongodb import mongodb
import logging
import aiosqlite
from database.mongodb import MongoDB
from utils.constants import CULTIVATION_LEVELS, LEVEL_REQUIREMENTS

logger = logging.getLogger(__name__)

class SpiritStone(commands.Cog, name="Linh Thạch"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.cultivation_levels = CULTIVATION_LEVELS
        self.level_requirements = LEVEL_REQUIREMENTS
        self.default_role_reward = 100
        self.mongodb = MongoDB()

    async def ensure_user(self, user_id: str, username: str = None) -> None:
        """Đảm bảo người dùng tồn tại trong database"""
        try:
            user = await mongodb.get_user(user_id)
            if not user:
                # Khởi tạo người dùng mới
                user_data = {
                    "_id": user_id,
                    "username": username,
                    "spirit_stones": 0,
                    "cultivation_level": 0,
                    "failed_rob_attempts": 0,
                    "last_checkin": 0,
                    "inventory": {},
                    "cultivation_points": 0,
                }
                await mongodb.update_user(user_id, user_data)
                logger.info(f"✅ Đã khởi tạo người dùng mới: {username} ({user_id})")
            elif username and user["username"] != username:
                # Cập nhật username nếu thay đổi
                await mongodb.update_user(user_id, {"username": username})
                logger.info(f"✅ Đã cập nhật username: {username} ({user_id})")
        except Exception as e:
            logger.error(f"❌ Lỗi khi khởi tạo người dùng {user_id}: {str(e)}")
            raise

    @commands.hybrid_command(
        name="diemdanh",
        description="Điểm danh hàng ngày để nhận Linh Thạch theo chức vụ"
    )
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def diemdanh(self, ctx: Context) -> None:
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        await self.ensure_user(user_id, username=ctx.author.name)

        user = await mongodb.get_user(user_id)
        if not user:
            embed = discord.Embed(
                title="Lỗi Điểm Danh",
                description="Không tìm thấy thông tin người dùng!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        current_time = int(time.time())
        
        if user["last_checkin"] and current_time - user["last_checkin"] < 86400:
            embed = discord.Embed(
                title="Điểm Danh Thất Bại",
                description="Bạn đã điểm danh hôm nay! Hãy thử lại sau 24 giờ.",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        reward_amount = self.default_role_reward
        user_roles = [role.id for role in ctx.author.roles]
        if user_roles:
            role_rewards = await mongodb.get_role_rewards(guild_id)
            for reward in role_rewards:
                if reward["role_id"] in user_roles:
                    reward_amount = max(reward_amount, reward["reward_amount"])

        await mongodb.update_user(user_id, {
            "spirit_stones": user["spirit_stones"] + reward_amount,
            "last_checkin": current_time
        })

        role_status = "Tạp Vụ" if reward_amount == self.default_role_reward else "chức vụ cao hơn"
        embed = discord.Embed(
            title="Điểm Danh Thành Công",
            description=f"Bạn nhận được Linh Thạch dựa trên chức vụ của mình!",
            color=0x1E90FF
        )
        embed.add_field(name="Linh Thạch Nhận Được", value=f"**{reward_amount}**", inline=True)
        embed.add_field(name="Chức Vụ", value=f"**{role_status}**", inline=True)
        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="chuyen",
        description="Chuyển Linh Thạch cho người khác"
    )
    async def transfer(self, ctx: Context, member: commands.MemberConverter, amount: int) -> None:
        sender_id = str(ctx.author.id)
        receiver_id = str(member.id)

        if member.id == ctx.author.id:
            embed = discord.Embed(
                title="Lỗi Chuyển Linh Thạch",
                description="Không thể chuyển Linh Thạch cho chính mình!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        if amount <= 0:
            embed = discord.Embed(
                title="Lỗi Chuyển Linh Thạch",
                description="Số Linh Thạch phải lớn hơn 0!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        await self.ensure_user(sender_id, username=ctx.author.name)
        await self.ensure_user(receiver_id, username=member.name)

        sender = await mongodb.get_user(sender_id)
        if not sender:
            embed = discord.Embed(
                title="Lỗi Chuyển Linh Thạch",
                description="Không tìm thấy thông tin người gửi!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        if sender["spirit_stones"] < amount:
            embed = discord.Embed(
                title="Lỗi Chuyển Linh Thạch",
                description="Bạn không đủ Linh Thạch để chuyển!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        receiver = await mongodb.get_user(receiver_id)
        if not receiver:
            embed = discord.Embed(
                title="Lỗi Chuyển Linh Thạch",
                description="Không tìm thấy thông tin người nhận!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        await mongodb.update_user(sender_id, {
            "spirit_stones": sender["spirit_stones"] - amount
        })
        await mongodb.update_user(receiver_id, {
            "spirit_stones": receiver["spirit_stones"] + amount
        })

        embed = discord.Embed(
            title="Chuyển Linh Thạch Thành Công",
            description=f"Bạn đã chuyển Linh Thạch cho {member.mention}!",
            color=0x1E90FF
        )
        embed.add_field(name="Số Linh Thạch", value=f"**{amount}** 🪨", inline=True)
        embed.add_field(name="Người Nhận", value=member.mention, inline=True)
        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="cuop",
        description="Cướp Linh Thạch từ người khác"
    )
    @commands.cooldown(1, 10, commands.BucketType.user)  # 5 phút cooldown
    async def rob(self, ctx: Context) -> None:
        robber_id = str(ctx.author.id)
        await self.ensure_user(robber_id, username=ctx.author.name)

        # Lấy ngẫu nhiên một người chơi có Linh Thạch
        users = await mongodb.db.users.find({
            "spirit_stones": {"$gt": 0},
            "_id": {"$ne": robber_id}
        }).to_list(length=None)
        
        if not users:
            embed = discord.Embed(
                title="Lỗi Cướp",
                description="Không tìm thấy mục tiêu để cướp!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        target = random.choice(users)
        target_id = target["_id"]
        target_stones = target["spirit_stones"]
        target_level = target["cultivation_level"]

        robber = await mongodb.get_user(robber_id)
        if not robber:
            embed = discord.Embed(
                title="Lỗi Cướp",
                description="Không tìm thấy thông tin người cướp!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        robber_level = robber["cultivation_level"]
        failed_attempts = robber["failed_rob_attempts"]

        import math

        level_diff = robber_level - target_level

        if level_diff > 0:
            # Robber cấp cao hơn
            success_rate = min(1.0, 0.5 + 0.2 * level_diff)  # Base 50%, mỗi cấp hơn +10%, tối đa 100%
        elif level_diff < 0:
            # Robber cấp thấp hơn
            success_rate = math.exp(0.5 * level_diff)        # Hàm mũ tụt xuống
            success_rate = min(0.5, success_rate)            # Không quá 50%
        else:
            # Bằng cấp
            success_rate = 0.5
        
        if random.random() < success_rate:
            steal_amount = target_stones // 10
            if steal_amount <= 0:
                embed = discord.Embed(
                    title="Lỗi Cướp",
                    description="Mục tiêu quá nghèo, không cướp được gì!",
                    color=0xFF4500
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await ctx.send(embed=embed)
                return

            await mongodb.update_user(target_id, {
                "spirit_stones": target_stones - steal_amount
            })
            await mongodb.update_user(robber_id, {
                "spirit_stones": robber["spirit_stones"] + steal_amount,
                "failed_rob_attempts": 0
            })

            target_member = ctx.guild.get_member(int(target_id))
            if target_member:
                embed = discord.Embed(
                    title="Cướp Thành Công",
                    description=f"Bạn đã cướp được {steal_amount} Linh Thạch từ {target_member.mention}!",
                    color=0x1E90FF
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await ctx.send(embed=embed)
                try:
                    await target_member.send(f"❌ {ctx.author.mention} đã cướp {steal_amount} Linh Thạch của bạn!")
                except discord.Forbidden:
                    await ctx.send(f"❌ Không thể gửi tin nhắn cho {target_member.mention} (DM bị tắt).")
                except discord.HTTPException:
                    await ctx.send(f"❌ Lỗi khi gửi tin nhắn cho {target_member.mention}.")
            else:
                embed = discord.Embed(
                    title="Cướp Thành Công",
                    description=f"Bạn đã cướp được {steal_amount} Linh Thạch từ <@{target_id}>!",
                    color=0x1E90FF
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await ctx.send(embed=embed)
        else:
            failed_attempts += 1
            if failed_attempts >= 3:
                new_level = max(0, robber_level - 1)
                await mongodb.update_user(robber_id, {
                    "failed_rob_attempts": 0,
                    "cultivation_level": new_level
                })
                embed = discord.Embed(
                    title="Cướp Thất Bại",
                    description=f"Bạn bị phản phệ, tu vi giảm xuống **{self.cultivation_levels[new_level]}**!",
                    color=0xFF4500
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await ctx.send(embed=embed)
            else:
                await mongodb.update_user(robber_id, {
                    "failed_rob_attempts": failed_attempts
                })
                embed = discord.Embed(
                    title="Cướp Thất Bại",
                    description=f"Cướp thất bại!({failed_attempts}/3)! Yếu còn ra gió!",
                    color=0xFF4500
                )
                embed = discord.Embed(
                    description=f"Targer: <@{robber_id}>",
                    color=0xFF4500
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="hoso",
        aliases=["profile", "info","tuvi"],
        description="Xem hồ sơ tu luyện của bản thân"
    )
    async def hoso(self, context: commands.Context) -> None:
        """
        Hiển thị hồ sơ tu luyện của người dùng
        """
        user_id = str(context.author.id)
        await self.ensure_user(user_id, username=context.author.name)
        
        user = await mongodb.get_user(user_id)
        if not user:
            embed = discord.Embed(
                title="Lỗi",
                description="Không tìm thấy thông tin người dùng!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)
            return

        current_level = user.get("cultivation_level", 0)
        current_points = user.get("cultivation_points", 0)
        spirit_stones = user.get("spirit_stones", 0)
        mining_attempts = user.get("mining_attempts", 0)
        failed_rob_attempts = user.get("failed_rob_attempts", 0)

        # Lấy thông tin cấp độ hiện tại
        current_level_name = self.get_cultivation_info(current_level)
        
        # Tính điểm tu vi cần thiết cho cấp độ tiếp theo
        next_level = current_level + 1
        required_points = self.level_requirements.get(next_level, 0)
        points_needed = max(0, required_points - current_points)
        next_level_name = self.get_cultivation_info(next_level)

        embed = discord.Embed(
            title=f"Hồ Sơ Tu Luyện - {context.author.name}",
            description=f"**Cấp độ hiện tại:** {current_level_name}",
            color=0x1E90FF
        )

        embed.add_field(
            name="📊 Thông Tin Tu Luyện",
            value=f"**Điểm tu vi hiện tại:** {current_points:,}\n"
                  f"**Cấp độ tiếp theo:** {next_level_name}\n"
                  f"**Điểm tu vi cần thiết:** {required_points:,}\n"
                  f"**Còn thiếu:** {points_needed:,}",
            inline=False
        )

        embed.add_field(
            name="💰 Tài Nguyên",
            value=f"**Linh Thạch:** {spirit_stones:,} 🪨",
            inline=False
        )

        embed.add_field(
            name="📈 Thống Kê",
            value=f"**Số lần khai thác:** {mining_attempts:,}\n"
                  f"**Số lần cướp thất bại:** {failed_rob_attempts}/3",
            inline=False
        )

        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await context.send(embed=embed)

    def get_cultivation_info(self, level):
        level_info = self.cultivation_levels.get(level, {
            "name": "Unknown",
            "color": 0xAAAAAA,
            "description": "Cảnh giới không xác định",
            "tho_nguyen": "Unknown"
        })
        return level_info["name"]

async def setup(bot) -> None:
    await bot.add_cog(SpiritStone(bot))