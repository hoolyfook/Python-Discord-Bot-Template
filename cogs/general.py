import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from discord import Embed, Member
import aiosqlite
from datetime import datetime
from database.mongodb import mongodb

class General(commands.Cog, name="general"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.context_menu_user = app_commands.ContextMenu(
            name="Grab ID", callback=self.grab_id
        )
        self.bot.tree.add_command(self.context_menu_user)
        self.context_menu_message = app_commands.ContextMenu(
            name="Remove spoilers", callback=self.remove_spoilers
        )
        self.bot.tree.add_command(self.context_menu_message)
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
        self.level_requirements = [1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000]

    # Message context menu command
    async def remove_spoilers(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        """
        Removes the spoilers from the message. This command requires the MESSAGE_CONTENT intent to work properly.

        :param interaction: The application command interaction.
        :param message: The message that is being interacted with.
        """
        spoiler_attachment = None
        for attachment in message.attachments:
            if attachment.is_spoiler():
                spoiler_attachment = attachment
                break
        embed = discord.Embed(
            title="Message without spoilers",
            description=message.content.replace("||", ""),
            color=0xBEBEFE,
        )
        if spoiler_attachment is not None:
            embed.set_image(url=attachment.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # User context menu command
    async def grab_id(
        self, interaction: discord.Interaction, user: discord.User
    ) -> None:
        """
        Grabs the ID of the user.

        :param interaction: The application command interaction.
        :param user: The user that is being interacted with.
        """
        embed = discord.Embed(
            description=f"The ID of {user.mention} is `{user.id}`.",
            color=0xBEBEFE,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="hoso",
        description="Xem hồ sơ tu luyện của bạn"
    )
    async def hoso(self, ctx: Context) -> None:
        user_id = str(ctx.author.id)
        await self.ensure_user(user_id, username=ctx.author.name)

        user = await mongodb.get_user(user_id)
        if not user:
            embed = discord.Embed(
                title="Lỗi Hồ Sơ",
                description="Không tìm thấy thông tin người dùng!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            return

        level = user["cultivation_level"]
        stones = user["spirit_stones"]
        cultivation_points = user["cultivation_points"]

        # Lấy thông tin cảnh giới
        realm, stage, color = self.get_cultivation_info(level)
        
        # Tạo thanh tiến trình tu vi
        progress = "█" * (level % 4 + 1) + "░" * (3 - level % 4)

        embed = discord.Embed(
            title=f"Hồ Sơ Tu Luyện - {ctx.author.name}",
            description="Thông tin chi tiết về quá trình tu luyện của bạn",
            color=color
        )
        
        embed.add_field(
            name="Cảnh Giới",
            value=f"**{realm} {stage}**\nTiến Trình: [{progress}]",
            inline=False
        )
        
        embed.add_field(
            name="Tài Nguyên",
            value=f"**Linh Thạch:** {stones:,} 🪨\n**Điểm Tu Luyện:** {cultivation_points:,} ⭐",
            inline=False
        )
        
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        await ctx.send(embed=embed)

    def get_cultivation_info(self, level: int) -> tuple:
        """Trả về thông tin về cảnh giới và giai đoạn tu luyện"""
        for realm, info in self.cultivation_levels.items():
            for stage, stage_level in info["levels"].items():
                if level == stage_level:
                    return realm, stage, info["color"]
        return "Không xác định", "Không xác định", 0x000000

    @commands.hybrid_command(
        name="ping",
        description="Kiểm tra độ trễ của bot."
    )
    async def ping(self, context: Context) -> None:
        """
        Kiểm tra độ trễ của bot.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Độ trễ của bot là {round(self.bot.latency * 1000)}ms.",
            color=0xBEBEFE,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="serverinfo",
        description="Xem thông tin về máy chủ."
    )
    async def serverinfo(self, context: Context) -> None:
        """
        Xem thông tin về máy chủ.
        """
        roles = [role.name for role in context.guild.roles]
        num_roles = len(roles)
        if num_roles > 50:
            roles = roles[:50]
            roles.append(f">>>> Hiển thị [50/{num_roles}] Vai trò")
        roles = ", ".join(roles)

        embed = discord.Embed(
            title="**Tên máy chủ:**", description=f"{context.guild}", color=0xBEBEFE
        )
        if context.guild.icon is not None:
            embed.set_thumbnail(url=context.guild.icon.url)
        embed.add_field(name="ID máy chủ", value=context.guild.id)
        embed.add_field(name="Số thành viên", value=context.guild.member_count)
        embed.add_field(
            name="Kênh văn bản/Thoại", value=f"{len(context.guild.channels)}"
        )
        embed.add_field(name=f"Vai trò ({len(context.guild.roles)})", value=roles)
        await context.send(embed=embed)

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
            elif username and user["username"] != username:
                # Cập nhật username nếu thay đổi
                await mongodb.update_user(user_id, {"username": username})
        except Exception as e:
            print(f"Error ensuring user: {str(e)}")
            raise

async def setup(bot) -> None:
    await bot.add_cog(General(bot))
