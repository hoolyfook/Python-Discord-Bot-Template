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
        aliases=["tuvi"],
        description="Xem hồ sơ tu luyện của bạn"
    )
    async def hoso(self, context: Context) -> None:
        """
        Xem hồ sơ tu luyện của bạn
        """
        user_id = str(context.author.id)
        await self.ensure_user(user_id, username=context.author.name)

        user = await mongodb.get_user(user_id)
        if not user:
            embed = discord.Embed(
                title="Lỗi Hồ Sơ",
                description="Không tìm thấy thông tin người dùng!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)
            return

        cultivation_level = user["cultivation_level"]
        cultivation_points = user["cultivation_points"]
        info = self.get_cultivation_info(cultivation_level)
        
        # Tính điểm cần thiết cho đột phá tiếp theo
        next_level_points = self.get_points_needed(cultivation_level + 1)
        
        embed = discord.Embed(
            title=f"Hồ Sơ Tu Luyện của {context.author.name}",
            description=f"**Cảnh Giới:** {info['realm']} {info['sublevel']}\n**Mô Tả:** {info['desc']}",
            color=info['color']
        )
        
        # Thêm avatar nếu có
        if context.author.avatar:
            embed.set_thumbnail(url=context.author.avatar.url)
        
        # Thêm thông tin điểm tu vi
        embed.add_field(
            name="Điểm Tu Vi",
            value=f"**{cultivation_points:,}** điểm",
            inline=True
        )
        
        # Thêm thông tin đột phá tiếp theo
        embed.add_field(
            name="Đột Phá Tiếp Theo",
            value=f"Cần **{next_level_points:,}** điểm tu vi",
            inline=True
        )
        
        # Thêm tỷ lệ thành công cho đột phá tiếp theo
        success_rate = 100 - (cultivation_level * 5)
        success_rate = max(10, success_rate)
        embed.add_field(
            name="Tỷ Lệ Thành Công",
            value=f"**{success_rate}%**",
            inline=True
        )

        embed.add_field(
            name="Linh thạch",
            value=f"**{user['spirit_stones']}**",
            inline=True
        )
        
        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await context.send(embed=embed)

    def get_cultivation_info(self, level: int):
        # Tính tổng số bậc nhỏ cho từng cảnh giới
        index = 0
        for name, sublevels, tho_nguyen, color, desc in self.cultivation_levels:
            num_sub = len(sublevels) if sublevels else 1
            if level < index + num_sub:
                sub = sublevels[level - index] if sublevels else ""
                return {
                    "realm": name,
                    "sublevel": sub,
                    "desc": desc,
                    "color": color,
                    "tho_nguyen": tho_nguyen,
                    "level_name": f"{name} {sub}" if sub else name
                }
            index += num_sub
        # Nếu vượt max, trả về cấp cuối cùng
        name, sublevels, tho_nguyen, color, desc = self.cultivation_levels[-1]
        return {
            "realm": name,
            "sublevel": "",
            "desc": desc,
            "color": color,
            "tho_nguyen": tho_nguyen,
            "level_name": name
        }

    def get_points_needed(self, level: int):
        # Ví dụ: mỗi cấp cần nhiều hơn 15% so với cấp trước
        base = 1000
        return int(base * (1.15 ** level))

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

    @commands.hybrid_command(
        name="tiemlongbang",
        aliases=["tlb","bxh","bangxephang","cuonggia"],
        description="Hiển thị bảng xếp hạng top 10 người mạnh nhất dựa theo cảnh giới"
    )
    async def tiemlongbang(self, context: Context) -> None:
        """
        Hiển thị bảng xếp hạng top 10 người mạnh nhất dựa theo cảnh giới
        """
        # Lấy top 10 người dùng có cảnh giới cao nhất
        top_users = await mongodb.get_top_users(10)
        
        if not top_users:
            embed = discord.Embed(
                title="Tiềm Long Bảng",
                description="Chưa có dữ liệu xếp hạng!",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)
            return

        embed = discord.Embed(
            title="🏆 Tiềm Long Bảng",
            description="Top 10 người mạnh nhất dựa theo cảnh giới",
            color=0xFFD700
        )

        for i, user in enumerate(top_users, 1):
            user_info = self.get_cultivation_info(user["cultivation_level"])
            level_name = user_info["level_name"]
            tho_nguyen = user_info["tho_nguyen"]
            
            # Thêm thông tin người dùng vào embed
            embed.add_field(
                name=f"{i}. {user['username']}",
                value=f"**Cảnh Giới:** {level_name}\n**Thọ Nguyên:** {tho_nguyen}\n**Tu Vi:** {user['cultivation_points']:,} điểm",
                inline=False
            )

        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
