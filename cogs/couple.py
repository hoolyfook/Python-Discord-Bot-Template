import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from discord import Embed
import json
from datetime import datetime
import random
import asyncio
from database.mongodb import MongoDB
from utils.constants import CULTIVATION_LEVELS, LEVEL_REQUIREMENTS

class Couple(commands.Cog, name="couple"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = None
        self.mongodb = MongoDB()
        self.cultivation_levels = CULTIVATION_LEVELS
        self.level_requirements = LEVEL_REQUIREMENTS

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    async def cog_check(self, ctx):
        if ctx.command.name == "help":
            # Danh sách các lệnh và mô tả
            commands_list = [
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
            for cmd in commands_list:
                embed = discord.Embed(
                    title=cmd["name"],
                    description=cmd["description"],
                    color=cmd["color"]
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await ctx.send(embed=embed)
            
            return False
        
        return True

    async def update_relationship(self, user_id: str, partner_id: str, intimacy_change: int) -> None:
        """Cập nhật điểm thân mật cho cặp đôi"""
        try:
            with open("database/relationships.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if user_id in data["relationships"]:
                data["relationships"][user_id]["intimacy"] += intimacy_change
            if partner_id in data["relationships"]:
                data["relationships"][partner_id]["intimacy"] += intimacy_change
            
            with open("database/relationships.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.bot.logger.error(f"Lỗi khi cập nhật relationship: {str(e)}")
            raise

    @commands.hybrid_command(
        name="daolu",
        aliases=["dl", "status", "tinhduyen"],
        description="Xem tình trạng đạo lữ của bản thân"
    )
    async def daolu(self, context: Context) -> None:
        """
        Xem tình trạng đạo lữ của bản thân
        """
        try:
            if not context.guild:
                embed = discord.Embed(
                    title="❌ Không Thể Thực Hiện",
                    description="Chỉ có thể xem tình trạng đạo lữ trong môn phái!",
                    color=0xFF4500
                )
                await context.send(embed=embed)
                return

            # Đọc dữ liệu từ file relationships.json
            with open("database/relationships.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            user_id = str(context.author.id)

            # Kiểm tra xem người dùng có trong hệ thống không
            if user_id not in data["relationships"]:
                embed = discord.Embed(
                    title="💘 Tình Duyên Chưa Đến",
                    description="Ngươi vẫn chưa có đạo lữ.\nHãy tiếp tục tu luyện, chờ đợi lương duyên!",
                    color=0xFF69B4
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await context.send(embed=embed)
                return

            partner_id = data["relationships"][user_id]["partner"]
            
            if partner_id == "None":
                embed = discord.Embed(
                    title="💘 Tình Duyên Chưa Đến",
                    description="Ngươi vẫn chưa có đạo lữ.\nHãy tiếp tục tu luyện, chờ đợi lương duyên!",
                    color=0xFF69B4
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await context.send(embed=embed)
                return

            try:
                # Lấy thông tin đạo lữ
                partner = await context.guild.fetch_member(int(partner_id))
                if not partner:
                    embed = discord.Embed(
                        title="❌ Không Tìm Thấy",
                        description="Không tìm thấy đạo lữ của ngươi trong môn phái này!",
                        color=0xFF4500
                    )
                    await context.send(embed=embed)
                    return

                # Tính tổng điểm thân mật
                total_intimacy = data["relationships"][user_id]["intimacy"]
                if partner_id in data["relationships"]:
                    total_intimacy += data["relationships"][partner_id]["intimacy"]

                # Tính thời gian bên nhau
                since_date = datetime.fromisoformat(data["relationships"][user_id]["since"].replace("Z", "+00:00"))
                time_diff = datetime.now() - since_date
                days = time_diff.days

                # Xác định cấp độ quan hệ dựa trên điểm thân mật
                relationship_level = "Sơ Giao Chi Giao"  # Mặc định
                if total_intimacy >= 10000:
                    relationship_level = "Tiên Thê Tiên Phu"
                elif total_intimacy >= 5000:
                    relationship_level = "Đạo Lữ Song Tu"
                elif total_intimacy >= 2000:
                    relationship_level = "Tâm Ý Tương Thông"
                elif total_intimacy >= 1000:
                    relationship_level = "Tình Trường Lữ Đoạn"

                embed = discord.Embed(
                    title="💕 Tình Trạng Đạo Lữ",
                    description=f"**Đạo Lữ của {context.author.mention}**",
                    color=0xFF69B4
                )
                embed.add_field(
                    name="❤️ Đạo Lữ",
                    value=f"{partner.mention}",
                    inline=False
                )
                embed.add_field(
                    name="✨ Cấp Độ Quan Hệ",
                    value=relationship_level,
                    inline=True
                )
                embed.add_field(
                    name="💝 Điểm Thân Mật",
                    value=f"{total_intimacy:,} điểm",
                    inline=True
                )
                embed.add_field(
                    name="⏳ Thời Gian Bên Nhau",
                    value=f"{days} ngày",
                    inline=True
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                await context.send(embed=embed)

            except discord.NotFound:
                embed = discord.Embed(
                    title="❌ Không Tìm Thấy",
                    description="Không tìm thấy đạo lữ của ngươi trong môn phái này!",
                    color=0xFF4500
                )
                await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error(f"Lỗi trong lệnh daolu: {str(e)}")
            embed = discord.Embed(
                title="Lỗi",
                description=f"Có lỗi xảy ra khi xem tình trạng đạo lữ: {str(e)}",
                color=0xFF4500
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="daolubang",
        aliases=["dlb", "daoluluc", "tinhduyenbang"],
        description="Hiển thị bảng xếp hạng đạo lữ dựa trên độ thân mật"
    )
    async def daolubang(self, context: Context) -> None:
        """
        Hiển thị bảng xếp hạng đạo lữ dựa trên độ thân mật
        """
        try:
            # Kiểm tra xem lệnh có được thực hiện trong server không
            if not context.guild:
                embed = discord.Embed(
                    title="Lỗi",
                    description="Lệnh này chỉ có thể sử dụng trong server!",
                    color=0xFF4500
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await context.send(embed=embed)
                return

            # Đọc dữ liệu từ file relationships.json
            with open("database/relationships.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Lấy danh sách các cặp đôi và tính điểm thân mật
            couples = []
            processed_ids = set()
            
            for user_id, info in data["relationships"].items():
                if user_id in processed_ids:
                    continue
                    
                partner_id = info["partner"]
                if partner_id != "None":
                    # Tính tổng điểm thân mật của cả hai
                    total_intimacy = info["intimacy"]
                    if partner_id in data["relationships"]:
                        total_intimacy += data["relationships"][partner_id]["intimacy"]
                    
                    try:
                        # Lấy thông tin người dùng
                        user = await context.guild.fetch_member(int(user_id))
                        partner = await context.guild.fetch_member(int(partner_id))
                        
                        if user and partner:
                            couples.append({
                                "user1": user,
                                "user2": partner,
                                "intimacy": total_intimacy,
                                "since": info["since"]
                            })
                            processed_ids.add(user_id)
                            processed_ids.add(partner_id)
                    except discord.NotFound:
                        # Bỏ qua nếu không tìm thấy người dùng
                        continue
                    except discord.HTTPException as e:
                        self.bot.logger.error(f"Lỗi khi lấy thông tin người dùng: {str(e)}")
                        continue
            
            # Sắp xếp theo điểm thân mật giảm dần
            couples.sort(key=lambda x: x["intimacy"], reverse=True)
            
            if not couples:
                embed = discord.Embed(
                    title="Đạo Lữ Bảng",
                    description="Chưa có cặp đôi nào trong server!",
                    color=0xFF4500
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await context.send(embed=embed)
                return

            # Chia thành các trang, mỗi trang 10 cặp
            pages = []
            for i in range(0, len(couples), 10):
                page_couples = couples[i:i+10]
                embed = discord.Embed(
                    title="💕 Đạo Lữ Bảng",
                    description=f"Top {min(len(couples), 10)} cặp đôi có độ thân mật cao nhất (Trang {len(pages) + 1})",
                    color=0xFF69B4
                )
                
                for j, couple in enumerate(page_couples, i + 1):
                    # Chuyển đổi thời gian
                    since_date = datetime.fromisoformat(couple["since"].replace("Z", "+00:00"))
                    time_diff = datetime.now() - since_date
                    days = time_diff.days
                    
                    embed.add_field(
                        name=f"{j}. {couple['user1'].name} ❤️ {couple['user2'].name}",
                        value=f"**Độ Thân Mật:** {couple['intimacy']:,} điểm\n**Quen nhau:** {days} ngày",
                        inline=False
                    )
                
                embed.set_footer(text=f"SpiritStone Bot | Trang {len(pages) + 1}/{(len(couples) + 9) // 10} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                pages.append(embed)

            # Gửi trang đầu tiên
            await context.send(embed=pages[0])
            
        except Exception as e:
            self.bot.logger.error(f"Lỗi trong lệnh daolu: {str(e)}")
            embed = discord.Embed(
                title="Lỗi",
                description=f"Có lỗi xảy ra khi hiển thị đạo lữ bảng: {str(e)}",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="songtu",
        aliases=["st", "tangqua", "gift"],
        description="Tặng quà cho đạo lữ của bạn để tăng điểm thân mật"
    )
    @commands.cooldown(1, 43200, commands.BucketType.user)  # 12 tiếng cooldown
    async def songtu(self, context: Context) -> None:
        """
        Tặng quà cho đạo lữ để tăng điểm thân mật
        """
        try:
            if not context.guild:
                embed = discord.Embed(
                    title="Lỗi",
                    description="Lệnh này chỉ có thể sử dụng trong server!",
                    color=0xFF4500
                )
                await context.send(embed=embed)
                return

            # Đọc dữ liệu từ file relationships.json
            with open("database/relationships.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            user_id = str(context.author.id)

            # Kiểm tra xem người dùng có đạo lữ không
            if user_id not in data["relationships"] or \
               data["relationships"][user_id]["partner"] == "None":
                embed = discord.Embed(
                    title="Lỗi",
                    description="Bạn chưa có đạo lữ!",
                    color=0xFF4500
                )
                await context.send(embed=embed)
                return

            partner_id = data["relationships"][user_id]["partner"]
            
            try:
                # Lấy thông tin đạo lữ
                partner = await context.guild.fetch_member(int(partner_id))
                if not partner:
                    embed = discord.Embed(
                        title="Lỗi",
                        description="Không tìm thấy đạo lữ của bạn trong server này!",
                        color=0xFF4500
                    )
                    await context.send(embed=embed)
                    return
            except discord.NotFound:
                embed = discord.Embed(
                    title="Lỗi",
                    description="Không tìm thấy đạo lữ của bạn trong server này!",
                    color=0xFF4500
                )
                await context.send(embed=embed)
                return

            # Tính điểm thân mật ngẫu nhiên (500-1000)
            intimacy_gain = random.randint(500, 1000)
            
            # Cập nhật điểm thân mật
            await self.update_relationship(user_id, partner_id, intimacy_gain/2)

            # Tạo embed thông báo
            embed = discord.Embed(
                title="🎁 Tặng Quà",
                color=0xFF69B4
            )
            embed.add_field(name="Người Tặng", value=context.author.mention, inline=False)
            embed.add_field(name="Người Nhận", value=partner.mention, inline=False)
            embed.add_field(name="Điểm Thân Mật", value=f"+{intimacy_gain} ❤️", inline=False)
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error(f"Lỗi trong lệnh songtu: {str(e)}")
            embed = discord.Embed(
                title="Lỗi",
                description=f"Có lỗi xảy ra khi tặng quà: {str(e)}",
                color=0xFF4500
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="cauhon",
        aliases=["ch", "propose", "kethon"],
        description="Kết đạo hữu thành đạo lữ, cùng tu tiên luyện đạo"
    )
    @app_commands.describe(
        member="Đạo hữu mà ngươi muốn kết thành đạo lữ"
    )
    async def cauhon(self, context: Context, member: discord.Member) -> None:
        """
        Kết đạo hữu thành đạo lữ, cùng tu tiên luyện đạo
        
        Parameters
        ----------
        member: Đạo hữu được cầu hôn
        """
        try:
            if not context.guild:
                embed = discord.Embed(
                    title="❌ Không Thể Thực Hiện",
                    description="Nghi thức kết đạo lữ chỉ có thể thực hiện trong môn phái!",
                    color=0xFF4500
                )
                await context.send(embed=embed)
                return

            if member.id == context.author.id:
                embed = discord.Embed(
                    title="❌ Không Thể Thực Hiện",
                    description="Tự kết đạo lữ với chính mình? Đạo hữu điên rồi sao?",
                    color=0xFF4500
                )
                await context.send(embed=embed)
                return

            if member.bot:
                embed = discord.Embed(
                    title="❌ Không Thể Thực Hiện",
                    description="Ngươi không thể kết đạo lữ với một khôi lỗi!",
                    color=0xFF4500
                )
                await context.send(embed=embed)
                return

            # Đọc dữ liệu từ file relationships.json
            with open("database/relationships.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            user_id = str(context.author.id)
            target_id = str(member.id)

            # Kiểm tra xem người cầu hôn đã có đạo lữ chưa
            if user_id in data["relationships"] and data["relationships"][user_id]["partner"] != "None":
                embed = discord.Embed(
                    title="❌ Không Thể Thực Hiện",
                    description="Ngươi đã có đạo lữ, sao dám phụ lòng người ta?",
                    color=0xFF4500
                )
                await context.send(embed=embed)
                return

            # Kiểm tra xem người được cầu hôn đã có đạo lữ chưa
            if target_id in data["relationships"] and data["relationships"][target_id]["partner"] != "None":
                embed = discord.Embed(
                    title="❌ Không Thể Thực Hiện",
                    description=f"{member.mention} đã có đạo lữ, đừng phá hoại nhân duyên của người ta!",
                    color=0xFF4500
                )
                await context.send(embed=embed)
                return

            # Tạo embed thông báo cầu hôn
            embed = discord.Embed(
                title="💍 Thiên Định Lương Duyên",
                description=f"Hỡi {member.mention}!\n\n"
                          f"Ta {context.author.mention} thấy ngươi chính là có duyên với ta!\n"
                          f"Không biết ngươi có nguyện kết đạo lữ cùng ta, song tu luyện đạo?\n\n"
                          f"➤ Ấn ✅ để thuận theo thiên ý\n"
                          f"➤ Ấn ❌ để duyên phận lỡ làng",
                color=0xFF69B4
            )
            embed.set_footer(text="Thời hạn suy nghĩ: 60 giây | Duyên phận vô thường, xin đừng bỏ lỡ")

            # Gửi tin nhắn và thêm reactions
            message = await context.send(embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("❌")

            def check(reaction, user):
                return user.id == member.id and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == message.id

            try:
                # Chờ phản hồi trong 60 giây
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "✅":
                    # Tạo hoặc cập nhật dữ liệu cho cả hai người
                    current_time = datetime.now().isoformat()

                    if user_id not in data["relationships"]:
                        data["relationships"][user_id] = {"partner": "None", "intimacy": 0, "since": current_time}
                    if target_id not in data["relationships"]:
                        data["relationships"][target_id] = {"partner": "None", "intimacy": 0, "since": current_time}

                    # Cập nhật partner cho cả hai
                    data["relationships"][user_id]["partner"] = target_id
                    data["relationships"][user_id]["since"] = current_time
                    data["relationships"][user_id]["intimacy"] = 0

                    data["relationships"][target_id]["partner"] = user_id
                    data["relationships"][target_id]["since"] = current_time
                    data["relationships"][target_id]["intimacy"] = 0

                    # Lưu dữ liệu
                    with open("database/relationships.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)

                    success_embed = discord.Embed(
                        title="💕 Thiên Định Lương Duyên",
                        description=f"🎊 Chúc mừng! Một đôi đạo lữ mới đã được thiên địa chứng giám!\n\n"
                                  f"➤ {context.author.mention} và {member.mention} đã kết thành đạo lữ\n"
                                  f"➤ Từ nay về sau, hai người sẽ cùng nhau tu tiên, luyện đạo\n"
                                  f"➤ Mong rằng đôi đạo lữ sẽ sớm đạt tới đỉnh cao võ đạo!",
                        color=0xFF69B4
                    )
                    await message.edit(embed=success_embed)
                else:
                    reject_embed = discord.Embed(
                        title="💔 Duyên Phận Lỡ Làng",
                        description=f"Tiếc thay!\n\n"
                                  f"➤ {member.mention} đã từ chối lời cầu thân của {context.author.mention}\n"
                                  f"➤ Có lẽ duyên phận chưa đến, đừng quá buồn phiền\n"
                                  f"➤ Hãy tiếp tục tu luyện, chờ đợi lương duyên khác!",
                        color=0xFF4500
                    )
                    await message.edit(embed=reject_embed)

            except asyncio.TimeoutError:
                timeout_embed = discord.Embed(
                    title="⏰ Duyên Phận Trôi Qua",
                    description=f"Tiếc thay!\n\n"
                              f"➤ {member.mention} đã không đáp lại lời cầu thân của {context.author.mention}\n"
                              f"➤ Có lẽ thời cơ chưa đến\n"
                              f"➤ Hãy tiếp tục tu luyện, chờ đợi cơ duyên khác!",
                    color=0xFF4500
                )
                await message.edit(embed=timeout_embed)

        except Exception as e:
            self.bot.logger.error(f"Lỗi trong lệnh cauhon: {str(e)}")
            embed = discord.Embed(
                title="Lỗi",
                description=f"Có lỗi xảy ra trong nghi thức kết đạo lữ: {str(e)}",
                color=0xFF4500
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="lyhon",
        aliases=["lh", "chiatay", "doandao"],
        description="Đoạn tuyệt đạo lữ, từ nay mỗi người một phương trời tu luyện"
    )
    async def lyhon(self, context: Context) -> None:
        """
        Đoạn tuyệt đạo lữ, từ nay mỗi người một phương trời tu luyện
        """
        try:
            if not context.guild:
                embed = discord.Embed(
                    title="❌ Không Thể Thực Hiện",
                    description="Nghi thức đoạn tuyệt chỉ có thể thực hiện trong môn phái!",
                    color=0xFF4500
                )
                await context.send(embed=embed)
                return

            # Đọc dữ liệu từ file relationships.json
            with open("database/relationships.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            user_id = str(context.author.id)

            # Kiểm tra xem người dùng có đạo lữ không
            if user_id not in data["relationships"] or data["relationships"][user_id]["partner"] == "None":
                embed = discord.Embed(
                    title="❌ Không Thể Thực Hiện",
                    description="Ngươi làm gì có đạo lữ mà đòi đoạn tuyệt?",
                    color=0xFF4500
                )
                await context.send(embed=embed)
                return

            partner_id = data["relationships"][user_id]["partner"]
            
            try:
                # Lấy thông tin đạo lữ
                partner = await context.guild.fetch_member(int(partner_id))
                if not partner:
                    embed = discord.Embed(
                        title="❌ Không Thể Thực Hiện",
                        description="Không tìm thấy đạo lữ của ngươi trong môn phái này!",
                        color=0xFF4500
                    )
                    await context.send(embed=embed)
                    return
            except discord.NotFound:
                embed = discord.Embed(
                    title="❌ Không Thể Thực Hiện",
                    description="Không tìm thấy đạo lữ của ngươi trong môn phái này!",
                    color=0xFF4500
                )
                await context.send(embed=embed)
                return

            # Tạo embed xác nhận
            embed = discord.Embed(
                title="💔 Đoạn Tuyệt Chi Thư",
                description=f"Hỡi {partner.mention}!\n\n"
                          f"Ta {context.author.mention} xin gửi đến ngươi bức thư đoạn tuyệt này.\n"
                          f"Duyên phận đã hết, đường ai nấy tu.\n\n"
                          f"➤ Ấn ✅ để xác nhận đoạn tuyệt\n"
                          f"➤ Ấn ❌ để níu kéo duyên phận",
                color=0xFF4500
            )
            embed.set_footer(text="Thời hạn suy nghĩ: 60 giây | Một khi đoạn tuyệt, vạn kiếp không quay lại")

            # Gửi tin nhắn và thêm reactions
            message = await context.send(embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("❌")

            def check(reaction, user):
                return user.id == int(partner_id) and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == message.id

            try:
                # Chờ phản hồi trong 60 giây
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "✅":
                    # Xóa thông tin đạo lữ của cả hai
                    data["relationships"][user_id]["partner"] = "None"
                    data["relationships"][user_id]["intimacy"] = 0
                    data["relationships"][partner_id]["partner"] = "None"
                    data["relationships"][partner_id]["intimacy"] = 0

                    # Lưu dữ liệu
                    with open("database/relationships.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)

                    final_embed = discord.Embed(
                        title="💔 Duyên Tận",
                        description=f"Từ đây đường ai nấy đi!\n\n"
                                  f"➤ {context.author.mention} và {partner.mention} đã chính thức đoạn tuyệt\n"
                                  f"➤ Mong hai vị từ nay tinh tiến tu đạo\n"
                                  f"➤ Hữu duyên thiên lý năng tương ngộ, vô duyên đối diện bất tương phùng",
                        color=0xFF4500
                    )
                    await message.edit(embed=final_embed)
                else:
                    reject_embed = discord.Embed(
                        title="💕 Duyên Chưa Dứt",
                        description=f"Có duyên gặp lại!\n\n"
                                  f"➤ {partner.mention} đã không đồng ý đoạn tuyệt với {context.author.mention}\n"
                                  f"➤ Mong hai vị hãy cùng nhau hóa giải hiểm cảnh\n"
                                  f"➤ Đạo lữ đồng tâm, phương có thể đại đạo viên mãn",
                        color=0xFF69B4
                    )
                    await message.edit(embed=reject_embed)

            except asyncio.TimeoutError:
                timeout_embed = discord.Embed(
                    title="⏰ Thời Gian Trôi Qua",
                    description=f"Tiếc thay!\n\n"
                              f"➤ {partner.mention} đã không phản hồi thư đoạn tuyệt của {context.author.mention}\n"
                              f"➤ Có lẽ cần thêm thời gian để suy nghĩ\n"
                              f"➤ Hãy cùng nhau bình tâm, tĩnh trí!",
                    color=0xFF4500
                )
                await message.edit(embed=timeout_embed)

        except Exception as e:
            self.bot.logger.error(f"Lỗi trong lệnh lyhon: {str(e)}")
            embed = discord.Embed(
                title="Lỗi",
                description=f"Có lỗi xảy ra trong nghi thức đoạn tuyệt: {str(e)}",
                color=0xFF4500
            )
            await context.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Couple(bot))
