import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import Embed
from database.mongodb import MongoDB
from datetime import datetime
from utils.constants import CULTIVATION_LEVELS, LEVEL_REQUIREMENTS

class Help(commands.Cog, name="Trợ giúp"):
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
        name="help",
        description="Hiển thị danh sách các lệnh bạn có thể sử dụng"
    )
    async def help(self, context: Context) -> None:
        """
        Hiển thị danh sách các lệnh bạn có thể sử dụng
        """
        try:
            self.bot.logger.info(f"Starting help command for user {context.author.name}")
            
            # Thông tin về prefix
            prefix = self.bot.bot_prefix
            prefix_embed = discord.Embed(
                title="ℹ️ Thông tin",
                description=f"Prefix: `{prefix}`\nBạn có thể sử dụng lệnh bằng cách:\n- Gõ `{prefix}lệnh`\n- Hoặc sử dụng slash command `/lệnh`",
                color=0xBEBEFE
            )
            await context.send(embed=prefix_embed)

            # Lặp qua tất cả các cog
            for cog_name in self.bot.cogs:
                self.bot.logger.info(f"Processing cog: {cog_name}")
                
                # Bỏ qua cog owner nếu người dùng không phải là owner
                if cog_name == "owner" and not (await self.bot.is_owner(context.author)):
                    self.bot.logger.info("Skipping owner cog - user is not owner")
                    continue
                
                cog = self.bot.get_cog(cog_name)
                if not cog:
                    self.bot.logger.warning(f"Cog {cog_name} not found")
                    continue
                
                commands = cog.get_commands()
                if not commands:
                    self.bot.logger.info(f"No commands found in cog {cog_name}")
                    continue

                # Xử lý riêng cho cog Couple
                if cog_name == "couple":
                    couple_commands = [
                        {
                            "name": "💍 /cauhon [@đạo_hữu]",
                            "description": "Kết đạo hữu thành đạo lữ, cùng tu tiên luyện đạo",
                            "color": 0xFF69B4
                        },
                        {
                            "name": "💔 /lyhon",
                            "description": "Đoạn tuyệt đạo lữ, từ nay mỗi người một phương trời tu luyện",
                            "color": 0xFF4500
                        },
                        {
                            "name": "❤️ /daolu",
                            "description": "Xem tình trạng đạo lữ của bản thân",
                            "color": 0xFF69B4
                        },
                        {
                            "name": "📊 /daolubang",
                            "description": "Hiển thị bảng xếp hạng đạo lữ dựa trên độ thân mật",
                            "color": 0xFF69B4
                        },
                        {
                            "name": "🎁 /songtu",
                            "description": "Tặng quà cho đạo lữ để tăng điểm thân mật",
                            "color": 0xFF69B4
                        }
                    ]

                    # Gửi từng lệnh trong một embed riêng
                    for cmd in couple_commands:
                        embed = discord.Embed(
                            title=cmd["name"],
                            description=cmd["description"],
                            color=cmd["color"]
                        )
                        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        await context.send(embed=embed)
                    continue

                # Xử lý các cog khác
                command_list = []
                for command in commands:
                    try:
                        # Kiểm tra quyền của người dùng
                        if not await command.can_run(context):
                            continue

                        # Lấy mô tả của lệnh
                        description = command.description or "Không có mô tả"
                        
                        # Lấy thông tin về cách sử dụng
                        usage = f"`{prefix}{command.name}"
                        if hasattr(command, 'signature') and command.signature:
                            usage += f" {command.signature}"
                        usage += "`"
                        
                        # Thêm thông tin về cooldown nếu có
                        cooldown = ""
                        if hasattr(command, '_buckets') and command._buckets:
                            cooldown_info = command._buckets._cooldown
                            if cooldown_info:
                                cooldown = f"\n⏱️ Cooldown: {cooldown_info.rate} lần/{cooldown_info.per}s"
                        
                        # Tạo thông tin lệnh với breakline
                        command_info = (
                            f"**{command.name}**\n"
                            f"{description}\n"
                            f"{usage}{cooldown}\n"
                            f"─────────────────────────\n"  # Breakline giữa các lệnh
                        )
                        command_list.append(command_info)
                        
                    except Exception as e:
                        self.bot.logger.error(f"Error processing command {command.name}: {str(e)}")
                        continue
                
                if command_list:
                    # Tạo embed riêng cho mỗi cog
                    embed = discord.Embed(
                        title=f"📁 {cog_name.capitalize()}",
                        description="\n".join(command_list),
                        color=0xBEBEFE
                    )
                    
                    if context.author.avatar:
                        embed.set_footer(text=f"Yêu cầu bởi {context.author.name}", icon_url=context.author.avatar.url)
                    else:
                        embed.set_footer(text=f"Yêu cầu bởi {context.author.name}")
                    
                    await context.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Error in help command: {str(e)}")
            error_embed = discord.Embed(
                title="❌ Lỗi",
                description=f"Đã có lỗi xảy ra khi hiển thị danh sách lệnh.\nLỗi: {str(e)}",
                color=0xFF0000
            )
            await context.send(embed=error_embed)

    @commands.hybrid_command(
        name="canhgioi",
        description="Hiển thị thông tin về các cảnh giới tu luyện"
    )
    async def canhgioi(self, context: Context) -> None:
        """
        Hiển thị thông tin về các cảnh giới tu luyện
        """
        embed = discord.Embed(
            title="🌌 Các Cảnh Giới Tu Luyện",
            description="Danh sách các cảnh giới tu luyện trong thế giới tu tiên",
            color=0x00FF00
        )

        realms = [
            "1️⃣ Phàm Nhân",
            "2️⃣ Luyện Khí (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)",
            "3️⃣ Trúc Cơ (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)",
            "4️⃣ Kim Đan (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)",
            "5️⃣ Nguyên Anh (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)",
            "6️⃣ Hóa Thần (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)",
            "7️⃣ Hợp Thể (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)",
            "8️⃣ Đại Thừa (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)",
            "9️⃣ Tiên Nhân (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)",
            "🔟 Kim Tiên (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)",
            "1️⃣1️⃣ Đại La Kim Tiên (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)",
            "1️⃣2️⃣ Tiên Vương (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)",
            "1️⃣3️⃣ Tiên Đế (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)",
            "1️⃣4️⃣ Đại Đế (Sơ Kỳ, Trung Kỳ, Hậu Kỳ, Đại Viên Mãn)"
        ]

        embed.add_field(
            name="📜 Các Cảnh Giới",
            value="\n".join(realms),
            inline=False
        )

        embed.add_field(
            name="ℹ️ Lưu ý",
            value="Mỗi cảnh giới (từ Luyện Khí trở đi) đều có 4 giai đoạn:\n- Sơ Kỳ\n- Trung Kỳ\n- Hậu Kỳ\n- Đại Viên Mãn",
            inline=False
        )

        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await context.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Help(bot)) 