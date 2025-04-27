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
        self.love_potions = {
            "tieu-tinh-dan": {
                "name": "Tiểu Tình Đan",
                "price": 1000,
                "description": "Đan dược tình yêu cấp thấp, giúp tăng 100 điểm thân mật",
                "effect": 100,
                "cooldown": 3600  # 1 giờ
            },
            "dai-tinh-dan": {
                "name": "Đại Tình Đan",
                "price": 5000,
                "description": "Đan dược tình yêu cấp trung, giúp tăng 500 điểm thân mật",
                "effect": 500,
                "cooldown": 7200  # 2 giờ
            },
            "than-tinh-dan": {
                "name": "Thần Tình Đan",
                "price": 10000,
                "description": "Đan dược tình yêu cấp cao, giúp tăng 1000 điểm thân mật",
                "effect": 1000,
                "cooldown": 14400  # 4 giờ
            },
            "tien-tinh-dan": {
                "name": "Tiên Tình Đan",
                "price": 50000,
                "description": "Đan dược tình yêu cấp tiên, giúp tăng 5000 điểm thân mật",
                "effect": 5000,
                "cooldown": 28800  # 8 giờ
            }
        }

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

    @commands.hybrid_command(
        name="tinhdan",
        aliases=["td", "tinh-dan"],
        description="Hiển thị danh sách đan dược tình yêu"
    )
    async def tinhdan(self, context: Context) -> None:
        """Hiển thị danh sách đan dược tình yêu"""
        embed = discord.Embed(
            title="💝 Đan Dược Tình Yêu",
            description="Danh sách các loại đan dược tình yêu có thể sử dụng",
            color=0xFF69B4
        )
        
        for potion_id, potion in self.love_potions.items():
            embed.add_field(
                name=f"**{potion['name']}** - {potion['price']:,} Linh Thạch",
                value=f"{potion['description']}\n**Hiệu quả:** +{potion['effect']:,} điểm thân mật\n**Thời gian chờ:** {potion['cooldown']//3600} giờ",
                inline=False
            )
        
        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="sudung",
        aliases=["sd", "su-dung"],
        description="Sử dụng đan dược tình yêu"
    )
    @app_commands.describe(
        potion="Tên đan dược muốn sử dụng",
        partner="Người bạn muốn tặng đan dược"
    )
    async def sudung(self, context: Context, potion: str, partner: discord.Member) -> None:
        """Sử dụng đan dược tình yêu"""
        try:
            # Kiểm tra xem có phải là đạo lữ không
            with open("database/relationships.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            user_id = str(context.author.id)
            partner_id = str(partner.id)
            
            if user_id not in data["relationships"] or data["relationships"][user_id]["partner"] != partner_id:
                embed = discord.Embed(
                    title="Lỗi",
                    description="Bạn chỉ có thể sử dụng đan dược cho đạo lữ của mình!",
                    color=0xFF4500
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await context.send(embed=embed)
                return
            
            # Kiểm tra đan dược
            potion = potion.lower()
            if potion not in self.love_potions:
                embed = discord.Embed(
                    title="Lỗi",
                    description="Không tìm thấy đan dược này!",
                    color=0xFF4500
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await context.send(embed=embed)
                return
            
            potion_info = self.love_potions[potion]
            
            # Kiểm tra thời gian chờ
            last_use = data["relationships"][user_id].get("last_potion_use", 0)
            current_time = datetime.now().timestamp()
            
            if current_time - last_use < potion_info["cooldown"]:
                remaining_time = potion_info["cooldown"] - (current_time - last_use)
                hours = int(remaining_time // 3600)
                minutes = int((remaining_time % 3600) // 60)
                
                embed = discord.Embed(
                    title="Lỗi",
                    description=f"Bạn cần chờ thêm {hours} giờ {minutes} phút nữa mới có thể sử dụng đan dược!",
                    color=0xFF4500
                )
                embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await context.send(embed=embed)
                return
            
            # Cập nhật điểm thân mật
            await self.update_relationship(user_id, partner_id, potion_info["effect"])
            
            # Cập nhật thời gian sử dụng
            data["relationships"][user_id]["last_potion_use"] = current_time
            with open("database/relationships.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            
            # Hiển thị kết quả
            embed = discord.Embed(
                title="Sử Dụng Đan Dược Thành Công",
                description=f"{context.author.mention} đã sử dụng {potion_info['name']} cho {partner.mention}",
                color=0xFF69B4
            )
            embed.add_field(
                name="Hiệu quả",
                value=f"Độ thân mật tăng thêm {potion_info['effect']:,} điểm!",
                inline=False
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Lỗi trong lệnh sudung: {str(e)}")
            embed = discord.Embed(
                title="Lỗi",
                description=f"Có lỗi xảy ra khi sử dụng đan dược: {str(e)}",
                color=0xFF4500
            )
            embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await context.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Couple(bot))
