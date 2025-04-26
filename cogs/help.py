import discord
from discord.ext import commands
from discord.ext.commands import Context

class Help(commands.Cog, name="help"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="help",
        description="Hiển thị danh sách tất cả các lệnh của bot."
    )
    async def help(self, context: Context) -> None:
        """
        Hiển thị danh sách tất cả các lệnh của bot.
        """
        try:
            self.bot.logger.info("Starting help command")
            embed = discord.Embed(
                title="📚 Danh sách lệnh",
                description="Dưới đây là danh sách tất cả các lệnh có sẵn:",
                color=0xBEBEFE
            )
            
            # Thêm thông tin về prefix
            prefix = self.bot.bot_prefix
            embed.add_field(
                name="ℹ️ Thông tin",
                value=f"Prefix: `{prefix}`\nBạn có thể sử dụng lệnh bằng cách:\n- Gõ `{prefix}lệnh`\n- Hoặc sử dụng slash command `/lệnh`",
                inline=False
            )

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
                
                command_list = []
                for command in commands:
                    try:
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
                    # Thêm breakline trước mỗi nhóm lệnh
                    embed.add_field(
                        name="\u200b",
                        value="════════════════════════════════",
                        inline=False
                    )
                    
                    # Thêm nhóm lệnh
                    embed.add_field(
                        name=f"📁 {cog_name.capitalize()}",
                        value="\n".join(command_list),
                        inline=False
                    )
                    
                    # Thêm breakline sau mỗi nhóm lệnh
                    embed.add_field(
                        name="\u200b",
                        value="════════════════════════════════",
                        inline=False
                    )
            
            # Thêm footer
            if context.author.avatar:
                embed.set_footer(text=f"Yêu cầu bởi {context.author.name}", icon_url=context.author.avatar.url)
            else:
                embed.set_footer(text=f"Yêu cầu bởi {context.author.name}")
            
            self.bot.logger.info("Sending help embed")
            await context.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Error in help command: {str(e)}")
            error_embed = discord.Embed(
                title="❌ Lỗi",
                description=f"Đã có lỗi xảy ra khi hiển thị danh sách lệnh.\nLỗi: {str(e)}",
                color=0xFF0000
            )
            await context.send(embed=error_embed)

async def setup(bot) -> None:
    await bot.add_cog(Help(bot)) 