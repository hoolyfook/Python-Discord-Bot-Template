import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from discord import Embed
import json
from datetime import datetime
import random

class Couple(commands.Cog, name="couple"):
    def __init__(self, bot) -> None:
        self.bot = bot

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
        aliases=["dl", "daoluluc", "tinhduyen"],
        description="Hiển thị bảng xếp hạng đạo lữ dựa trên độ thân mật"
    )
    async def daolu(self, context: Context) -> None:
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
            await self.update_relationship(user_id, partner_id, intimacy_gain)

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

async def setup(bot) -> None:
    await bot.add_cog(Couple(bot))
