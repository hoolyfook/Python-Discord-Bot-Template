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

logger = logging.getLogger(__name__)

class SpiritStone(commands.Cog, name="spiritstone"):
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
                "description": "Giai đoạn đầu của tu luyện, luyện khí thành linh lực",
                "color": 0x00FF00
            },
            "Trúc Cơ": {
                "levels": {
                    "Sơ Kỳ": 4,
                    "Trung Kỳ": 5,
                    "Hậu Kỳ": 6,
                    "Đại Viên Mãn": 7
                },
                "description": "Xây dựng nền tảng tu luyện vững chắc",
                "color": 0x00FFFF
            },
            "Kim Đan": {
                "levels": {
                    "Sơ Kỳ": 8,
                    "Trung Kỳ": 9,
                    "Hậu Kỳ": 10,
                    "Đại Viên Mãn": 11
                },
                "description": "Kết tinh linh lực thành kim đan",
                "color": 0xFFD700
            },
            "Nguyên Anh": {
                "levels": {
                    "Sơ Kỳ": 12,
                    "Trung Kỳ": 13,
                    "Hậu Kỳ": 14,
                    "Đại Viên Mãn": 15
                },
                "description": "Nuôi dưỡng nguyên thần, hình thành nguyên anh",
                "color": 0xFF4500
            },
            "Hóa Thần": {
                "levels": {
                    "Sơ Kỳ": 16,
                    "Trung Kỳ": 17,
                    "Hậu Kỳ": 18,
                    "Đại Viên Mãn": 19
                },
                "description": "Hóa thần thành tiên, đạt đến cảnh giới cao hơn",
                "color": 0x9932CC
            },
            "Luyện Hư": {
                "levels": {
                    "Sơ Kỳ": 20,
                    "Trung Kỳ": 21,
                    "Hậu Kỳ": 22,
                    "Đại Viên Mãn": 23
                },
                "description": "Luyện hư thành thực, đạt đến cảnh giới tiên nhân",
                "color": 0x4169E1
            },
            "Hợp Thể": {
                "levels": {
                    "Sơ Kỳ": 24,
                    "Trung Kỳ": 25,
                    "Hậu Kỳ": 26,
                    "Đại Viên Mãn": 27
                },
                "description": "Hợp nhất với thiên địa, đạt đến cảnh giới đại năng",
                "color": 0xFF0000
            },
            "Đại Thừa": {
                "levels": {
                    "Sơ Kỳ": 28,
                    "Trung Kỳ": 29,
                    "Hậu Kỳ": 30,
                    "Đại Viên Mãn": 31
                },
                "description": "Đạt đến cảnh giới tối cao, một bước thành tiên",
                "color": 0xFFFFFF
            },
            "Bán Đế": {
                "levels": {
                    "Sơ Kỳ": 32,
                    "Trung Kỳ": 33,
                    "Hậu Kỳ": 34,
                    "Đại Viên Mãn": 35
                },
                "description": "Đạt đến cảnh giới bán đế, một chân đã bước vào thế giới đế giới",
                "color": 0xFF00FF
            },
            "Đại Đế": {
                "levels": {
                    "Sơ Kỳ": 36,
                    "Trung Kỳ": 37,
                    "Hậu Kỳ": 38,
                    "Đại Viên Mãn": 39
                },
                "description": "Đạt đến cảnh giới đại đế, chân chính bước vào thế giới đế giới",
                "color": 0x000000
            }
        }
        self.level_requirements = {
            0: 1000,    # Luyện Khí Sơ Kỳ
            1: 2000,    # Luyện Khí Trung Kỳ
            2: 4000,    # Luyện Khí Hậu Kỳ
            3: 8000,    # Luyện Khí Đại Viên Mãn
            4: 16000,   # Trúc Cơ Sơ Kỳ
            5: 32000,   # Trúc Cơ Trung Kỳ
            6: 64000,   # Trúc Cơ Hậu Kỳ
            7: 128000,  # Trúc Cơ Đại Viên Mãn
            8: 256000,  # Kim Đan Sơ Kỳ
            9: 512000,  # Kim Đan Trung Kỳ
            10: 1024000, # Kim Đan Hậu Kỳ
            11: 2048000, # Kim Đan Đại Viên Mãn
            12: 4096000, # Nguyên Anh Sơ Kỳ
            13: 8192000, # Nguyên Anh Trung Kỳ
            14: 16384000, # Nguyên Anh Hậu Kỳ
            15: 32768000, # Nguyên Anh Đại Viên Mãn
            16: 65536000, # Hóa Thần Sơ Kỳ
            17: 131072000, # Hóa Thần Trung Kỳ
            18: 262144000, # Hóa Thần Hậu Kỳ
            19: 524288000, # Hóa Thần Đại Viên Mãn
            20: 1048576000, # Luyện Hư Sơ Kỳ
            21: 2097152000, # Luyện Hư Trung Kỳ
            22: 4194304000, # Luyện Hư Hậu Kỳ
            23: 8388608000, # Luyện Hư Đại Viên Mãn
            24: 16777216000, # Hợp Thể Sơ Kỳ
            25: 33554432000, # Hợp Thể Trung Kỳ
            26: 67108864000, # Hợp Thể Hậu Kỳ
            27: 134217728000, # Hợp Thể Đại Viên Mãn
            28: 268435456000, # Đại Thừa Sơ Kỳ
            29: 536870912000, # Đại Thừa Trung Kỳ
            30: 1073741824000, # Đại Thừa Hậu Kỳ
            31: 2147483648000, # Đại Thừa Đại Viên Mãn
            32: 4294967296000, # Bán Đế Sơ Kỳ
            33: 8589934592000, # Bán Đế Trung Kỳ
            34: 17179869184000, # Bán Đế Hậu Kỳ
            35: 34359738368000, # Bán Đế Đại Viên Mãn
            36: 68719476736000, # Đại Đế Sơ Kỳ
            37: 137438953472000, # Đại Đế Trung Kỳ
            38: 274877906944000, # Đại Đế Hậu Kỳ
            39: 549755813888000  # Đại Đế Đại Viên Mãn
        }
        self.default_role_reward = 100

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
                    "balance": 0
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
        name="setup_role_rewards",
        description="Thiết lập Linh Thạch thưởng cho các vai trò (admin only)"
    )
    @commands.has_permissions(administrator=True)
    async def setup_role_rewards(self, ctx: Context, role: discord.Role, reward_amount: int) -> None:
        if reward_amount <= 0:
            embed = discord.Embed(
                title="Lỗi Thiết Lập",
                description="Số Linh Thạch thưởng phải lớn hơn 0!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        guild_id = str(ctx.guild.id)
        role_id = str(role.id)

        await mongodb.update_role_reward(guild_id, role_id, reward_amount)

        embed = discord.Embed(
            title="Thiết Lập Thành Công",
            description=f"Đã thiết lập thưởng cho vai trò {role.mention}!",
            color=0x1E90FF
        )
        embed.add_field(name="Vai Trò", value=role.mention, inline=True)
        embed.add_field(name="Linh Thạch Thưởng", value=f"**{reward_amount}**", inline=True)
        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="khaikhoang",
        description="Khai thác để nhận Linh Thạch (số lượng tăng theo tu vi)"
    )
    async def khaikhoang(self, ctx: Context) -> None:
        user_id = str(ctx.author.id)
        await self.ensure_user(user_id, username=ctx.author.name)
        
        user = await mongodb.get_user(user_id)
        if not user:
            embed = discord.Embed(
                title="Lỗi Khai Khoáng",
                description="Không tìm thấy thông tin người dùng!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        spirit_stones = user.get("spirit_stones", 0)
        cultivation_level = user.get("cultivation_level", 0)

        # Tính toán số Linh Thạch nhận được dựa trên tu vi
        base_reward = {
            "Luyện Khí": 5000,
            "Trúc Cơ": 10000,
            "Kim Đan": 20000,
            "Nguyên Anh": 40000,
            "Hóa Thần": 80000,
            "Luyện Hư": 160000,
            "Hợp Thể": 320000,
            "Đại Thừa": 640000,
            "Bán Đế": 1280000,
            "Đại Đế": 2560000
        }

        # Lấy thông tin cảnh giới hiện tại
        realm, stage, _, _ = self.get_cultivation_info(cultivation_level)
        
        # Lấy phần thưởng cơ bản theo cảnh giới
        base = base_reward.get(realm, 5000)
        
        # Tính hệ số theo giai đoạn (Sơ Kỳ: x1, Trung Kỳ: x1.2, Hậu Kỳ: x1.5, Đại Viên Mãn: x2)
        stage_multiplier = {
            "Sơ Kỳ": 1,
            "Trung Kỳ": 1.2,
            "Hậu Kỳ": 1.5,
            "Đại Viên Mãn": 2
        }
        
        multiplier = stage_multiplier.get(stage, 1)
        
        # Tính số Linh Thạch nhận được
        mining_reward = int(base * multiplier)

        # Thêm yếu tố ngẫu nhiên (90% - 110% phần thưởng)
        random_factor = random.uniform(0.9, 1.1)
        mining_reward = int(mining_reward * random_factor)

        # Cập nhật số Linh Thạch mới
        new_spirit_stones = spirit_stones + mining_reward
        
        await mongodb.update_user(user_id, {
            "spirit_stones": new_spirit_stones
        })

        embed = discord.Embed(
            title="⛏️ Khai Khoáng Thành Công",
            description=f"Bạn đã khai thác được Linh Thạch tại mỏ khoáng!",
            color=0x1E90FF
        )
        embed.add_field(
            name="Cảnh Giới",
            value=f"**{realm} {stage}**",
            inline=True
        )
        embed.add_field(
            name="Phần Thưởng Cơ Bản",
            value=f"**{base:,}** 🪨",
            inline=True
        )
        embed.add_field(
            name="Hệ Số Giai Đoạn",
            value=f"**x{multiplier:.1f}**",
            inline=True
        )
        embed.add_field(
            name="Yếu Tố May Mắn",
            value=f"**x{random_factor:.2f}**",
            inline=True
        )
        embed.add_field(
            name="Tổng Nhận Được",
            value=f"**{mining_reward:,}** 🪨",
            inline=True
        )
        embed.add_field(
            name="Linh Thạch Hiện Tại",
            value=f"**{new_spirit_stones:,}** 🪨",
            inline=True
        )
        
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

        level_diff = robber_level - target_level
        success_rate = min(0.8, max(0.2, 0.5 + (level_diff * 0.1)))
        
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
                    description=f"Cướp thất bại! ({failed_attempts}/3)",
                    color=0xFF4500
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="dotpha",
        description="Sử dụng điểm tu vi để đột phá cảnh giới"
    )
    async def dotpha(self, context: Context) -> None:
        user_id = str(context.author.id)
        await self.ensure_user(user_id, username=context.author.name)

        user = await mongodb.get_user(user_id)
        if not user:
            embed = discord.Embed(
                title="Lỗi Đột Phá",
                description="Không tìm thấy thông tin người dùng!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)
            return

        cultivation_points = user.get("cultivation_points", 0)
        current_level = user.get("cultivation_level", 0)

        # Tính toán điểm cần thiết cho đột phá
        points_needed = (current_level + 1) * 1000

        if cultivation_points < points_needed:
            embed = discord.Embed(
                title="Đột Phá Thất Bại",
                description=f"Bạn cần {points_needed:,} điểm tu vi để đột phá!\nHiện tại bạn có: {cultivation_points:,} điểm tu vi",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)
            return

        # Tính tỷ lệ thành công
        success_rate = 100 - (current_level * 5)  # Giảm 5% mỗi level
        success_rate = max(10, success_rate)

        # Thực hiện đột phá
        if random.randint(1, 100) <= success_rate:
            # Đột phá thành công
            new_level = current_level + 1
            new_points = cultivation_points - points_needed

            await mongodb.update_user(user_id, {
                "cultivation_level": new_level,
                "cultivation_points": new_points
            })

            # Lấy thông tin cảnh giới mới
            realm, stage, _, color = self.get_cultivation_info(new_level)

            embed = discord.Embed(
                title="Đột Phá Thành Công!",
                description=f"Chúc mừng bạn đã đột phá thành công lên **{realm} {stage}**!",
                color=color
            )
            embed.add_field(
                name="Thông tin đột phá",
                value=f"Điểm tu vi đã sử dụng: {points_needed:,}\nĐiểm tu vi còn lại: {new_points:,}",
                inline=False
            )
            embed.add_field(
                name="Tỷ lệ thành công",
                value=f"{success_rate}%",
                inline=False
            )
        else:
            # Đột phá thất bại
            new_points = cultivation_points - (points_needed // 2)  # Mất 50% điểm cần thiết

            await mongodb.update_user(user_id, {
                "cultivation_points": new_points
            })

            embed = discord.Embed(
                title="Đột Phá Thất Bại",
                description="Đột phá thất bại! Bạn đã mất một nửa số điểm tu vi cần thiết.",
                color=0xFF4500
            )
            embed.add_field(
                name="Thông tin đột phá",
                value=f"Điểm tu vi đã mất: {points_needed // 2:,}\nĐiểm tu vi còn lại: {new_points:,}",
                inline=False
            )
            embed.add_field(
                name="Tỷ lệ thành công",
                value=f"{success_rate}%",
                inline=False
            )

        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await context.send(embed=embed)

    def get_cultivation_info(self, level: int) -> tuple:
        """Trả về thông tin về cảnh giới và giai đoạn tu luyện"""
        for realm, info in self.cultivation_levels.items():
            for stage, stage_level in info["levels"].items():
                if level == stage_level:
                    return realm, stage, info["description"], info["color"]
        return "Không xác định", "Không xác định", "Không có mô tả", 0x000000

async def setup(bot) -> None:
    await bot.add_cog(SpiritStone(bot))