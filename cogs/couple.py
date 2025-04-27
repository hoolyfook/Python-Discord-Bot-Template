import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from discord import Embed
import json
from datetime import datetime

class Couple(commands.Cog, name="couple"):
    def __init__(self, bot) -> None:
        self.bot = bot

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
            
            embed = discord.Embed(
                title="💕 Đạo Lữ Bảng",
                description="Top 10 cặp đôi có độ thân mật cao nhất",
                color=0xFF69B4
            )
            
            for i, couple in enumerate(couples[:10], 1):
                # Chuyển đổi thời gian
                since_date = datetime.fromisoformat(couple["since"].replace("Z", "+00:00"))
                time_diff = datetime.now() - since_date
                days = time_diff.days
                
                embed.add_field(
                    name=f"{i}. {couple['user1'].name} ❤️ {couple['user2'].name}",
                    value=f"**Độ Thân Mật:** {couple['intimacy']:,} điểm\n**Quen nhau:** {days} ngày",
                    inline=False
                )
            
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Lỗi trong lệnh daolu: {str(e)}")
            embed = discord.Embed(
                title="Lỗi",
                description=f"Có lỗi xảy ra khi hiển thị đạo lữ bảng: {str(e)}",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Couple(bot))
