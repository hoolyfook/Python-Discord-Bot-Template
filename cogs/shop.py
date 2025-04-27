import discord
from discord.ext import commands
from discord import Embed
from database.mongodb import mongodb
import random
import json
from datetime import datetime

class Shop(commands.Cog, name="shop"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.items = {
            "tieu-hoan-dan": {
                "name": "Tiểu Hoàn Đan",
                "price": 1000,
                "description": "Đan dược cấp thấp, giúp tăng 100 điểm tu vi",
                "effect": 1000,
                "type": "cultivation"
            },
            "dai-hoan-dan": {
                "name": "Đại Hoàn Đan",
                "price": 5000,
                "description": "Đan dược cấp trung, giúp tăng 500 điểm tu vi",
                "effect": 5000,
                "type": "cultivation"
            },
            "than-hoan-dan": {
                "name": "Thần Hoàn Đan",
                "price": 10000,
                "description": "Đan dược cấp cao, giúp tăng 1000 điểm tu vi",
                "effect": 10000,
                "type": "cultivation"
            },
            "tien-hoan-dan": {
                "name": "Tiên Hoàn Đan",
                "price": 50000,
                "description": "Đan dược cấp tiên, giúp tăng 5000 điểm tu vi",
                "effect": 50000,
                "type": "cultivation"
            },
            "kim-dan": {
                "name": "Kim Đan",
                "price": 100000,
                "description": "Đan dược cấp Kim Đan, giúp tăng 10000 điểm tu vi",
                "effect": 100000,
                "type": "cultivation"
            },
            "nguyen-anh-dan": {
                "name": "Nguyên Anh Đan",
                "price": 500000,
                "description": "Đan dược cấp Nguyên Anh, giúp tăng 50000 điểm tu vi",
                "effect": 500000,
                "type": "cultivation"
            },
            "hoa-than-dan": {
                "name": "Hóa Thần Đan",
                "price": 1000000,
                "description": "Đan dược cấp Hóa Thần, giúp tăng 100000 điểm tu vi",
                "effect": 1000000,
                "type": "cultivation"
            },
            "hop-the-dan": {
                "name": "Hợp Thể Đan",
                "price": 5000000,
                "description": "Đan dược cấp Hợp Thể, giúp tăng 500000 điểm tu vi",
                "effect": 5000000,
                "type": "cultivation"
            },
            "dai-thua-dan": {
                "name": "Đại Thừa Đan",
                "price": 10000000,
                "description": "Đan dược cấp Đại Thừa, giúp tăng 1000000 điểm tu vi",
                "effect": 10000000,
                "type": "cultivation"
            },
            "tieu-tien-dan": {
                "name": "Tiểu Tiên Đan",
                "price": 50000000,
                "description": "Đan dược cấp Tiểu Tiên, giúp tăng 5000000 điểm tu vi",
                "effect": 50000000,
                "type": "cultivation"
            },
            "dai-tien-dan": {
                "name": "Đại Tiên Đan",
                "price": 100000000,
                "description": "Đan dược cấp Đại Tiên, giúp tăng 10000000 điểm tu vi",
                "effect": 100000000,
                "type": "cultivation"
            },
            "tieu-than-dan": {
                "name": "Tiểu Thần Đan",
                "price": 500000000,
                "description": "Đan dược cấp Tiểu Thần, giúp tăng 50000000 điểm tu vi",
                "effect": 500000000,
                "type": "cultivation"
            },
            "dai-than-dan": {
                "name": "Đại Thần Đan",
                "price": 1000000000,
                "description": "Đan dược cấp Đại Thần, giúp tăng 100000000 điểm tu vi",
                "effect": 1000000000,
                "type": "cultivation"
            }
        }

    async def ensure_user(self, user_id: str, username: str = None) -> None:
        user = await mongodb.get_user(user_id)
        if not user:
            user_data = {
                "_id": user_id,
                "username": username,
                "spirit_stones": 0,
                "cultivation_level": 0,
                "failed_rob_attempts": 0,
                "last_checkin": 0,
                "inventory": {},
                "cultivation_points": 0
            }
            await mongodb.update_user(user_id, user_data)
        elif username and user.get("username") != username:
            await mongodb.update_user(user_id, {"username": username})

    @commands.hybrid_command(
        name="cuahang",
        aliases=["shop"],
        description="Hiển thị cửa hàng đan dược"
    )
    async def cuahang(self, context: commands.Context) -> None:
        """
        Hiển thị danh sách các đan dược có thể mua và hướng dẫn sử dụng
        """
        embed = Embed(
            title="🏪 Cửa Hàng Đan Dược",
            description="Dưới đây là danh sách các đan dược có sẵn:\n\n"
                      "**Hướng dẫn mua hàng:**\n"
                      "1. Xem danh sách đan dược bên dưới\n"
                      "2. Chọn đan dược muốn mua và ghi nhớ ID của nó\n"
                      "3. Sử dụng lệnh `/mua <id> [số_lượng]` để mua (số lượng là tuỳ chọn, mặc định là 1)\n"
                      "   Ví dụ: `/mua tieu-hoan-dan 3` (mua 3 viên), `/mua tieu-hoan-dan` (mua 1 viên)\n"
                      "4. Kiểm tra số Linh Thạch của bạn bằng lệnh `/tuitruvat`\n"
                      "5. Nếu đủ Linh Thạch, đan dược sẽ được thêm vào kho của bạn\n\n"
                      "**Hướng dẫn sử dụng:**\n"
                      "1. Xem kho đồ bằng lệnh `/tuitruvat`\n"
                      "2. Sử dụng đan dược bằng lệnh `/sudungdan <id> [số_lượng]`\n"
                      "3. Xem tu vi bằng lệnh `/tuvi`\n\n"
                      "**Danh sách đan dược:**",
            color=0x00FF00
        )

        for item_id, item in self.items.items():
            embed.add_field(
                name=f"💊 {item['name']} - {item['price']} Linh Thạch",
                value=f"{item['description']}\nID: `{item_id}`",
                inline=False
            )

        embed.set_footer(text="Sử dụng /mua <id> [số_lượng] để mua đan dược")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="mua",
        description="Mua đan dược từ cửa hàng"
    )
    async def mua(self, context: commands.Context, item_id: str, so_luong: int = 1) -> None:
        """
        Mua đan dược từ cửa hàng

        :param item_id: ID của đan dược muốn mua
        :param so_luong: Số lượng muốn mua (mặc định là 1)
        """
        if item_id not in self.items:
            await context.send("❌ Không tìm thấy đan dược này!")
            return

        if so_luong < 1:
            await context.send("❌ Số lượng phải lớn hơn 0!")
            return

        item = self.items[item_id]
        user_id = str(context.author.id)
        await self.ensure_user(user_id, username=context.author.name)
        user = await mongodb.get_user(user_id)
        spirit_stones = user.get("spirit_stones", 0)
        inventory = user.get("inventory", {})

        tong_gia = item['price'] * so_luong
        if spirit_stones < tong_gia:
            await context.send(f"❌ Bạn không đủ Linh Thạch để mua {so_luong} {item['name']}!")
            return

        # Trừ Linh Thạch và cập nhật kho
        new_spirit_stones = spirit_stones - tong_gia
        inventory[item_id] = inventory.get(item_id, 0) + so_luong

        await mongodb.update_user(user_id, {
            "spirit_stones": new_spirit_stones,
            "inventory": inventory
        })

        # Tạo embed thông báo mua hàng thành công
        embed = Embed(
            title="✅ Mua hàng thành công!",
            description=f"Bạn đã mua {so_luong} {item['name']} với giá {tong_gia} Linh Thạch",
            color=0x00FF00
        )
        embed.add_field(name="Linh Thạch còn lại", value=f"{new_spirit_stones} 🪨", inline=False)
        embed.add_field(name="Hiệu quả", value=f"+{item['effect']} điểm tu vi mỗi viên", inline=False)
        
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="tuitruvat",
        aliases=["inventory","tuido"],
        description="Xem kho đồ của bạn"
    )
    async def tuitruvat(self, context: commands.Context) -> None:
        """
        Hiển thị danh sách đan dược trong kho
        """
        user_id = str(context.author.id)
        await self.ensure_user(user_id, username=context.author.name)
        user = await mongodb.get_user(user_id)
        inventory = user.get("inventory", {})
        spirit_stones = user.get("spirit_stones", 0)

        embed = Embed(
            title="🎒 Túi Trữ Vật",
            description=f"Linh Thạch: **{spirit_stones}** 🪨",
            color=0x00FF00
        )

        if not inventory:
            embed.add_field(
                name="Kho Đồ",
                value="❌ Kho của bạn đang trống!",
                inline=False
            )
        else:
            embed.add_field(
                name="Kho Đồ",
                value="Danh sách đan dược trong kho của bạn:",
                inline=False
            )
            for item_id, quantity in inventory.items():
                if item_id in self.items:
                    item = self.items[item_id]
                    embed.add_field(
                        name=f"💊 {item['name']} x{quantity}",
                        value=f"Hiệu quả: +{item['effect']} điểm tu vi\nSử dụng: `/sudungdan {item_id} [số_lượng]`",
                        inline=False
                    )

        await context.send(embed=embed)

    @commands.hybrid_command(
        name="sudungdan",
        description="Sử dụng đan dược để tăng tu vi"
    )
    async def sudungdan(self, context: commands.Context, item_id: str, so_luong: int = 1) -> None:
        """
        Sử dụng đan dược để tăng tu vi

        :param item_id: ID của đan dược muốn sử dụng
        :param so_luong: Số lượng muốn sử dụng (mặc định là 1)
        """
        if item_id not in self.items:
            await context.send("❌ Không tìm thấy đan dược này!")
            return

        if so_luong < 1:
            await context.send("❌ Số lượng phải lớn hơn 0!")
            return

        item = self.items[item_id]
        user_id = str(context.author.id)
        await self.ensure_user(user_id, username=context.author.name)
        user = await mongodb.get_user(user_id)
        inventory = user.get("inventory", {})
        so_luong_trong_kho = inventory.get(item_id, 0)

        if so_luong_trong_kho < so_luong:
            await context.send(f"❌ Bạn không có đủ {item['name']} trong kho! (Chỉ còn {so_luong_trong_kho})")
            return

        # Giảm số lượng đan dược trong kho
        inventory[item_id] -= so_luong
        if inventory[item_id] <= 0:
            del inventory[item_id]

        diem_tuvi_tang = item['effect'] * so_luong
        await mongodb.update_user(user_id, {
            "inventory": inventory,
            "cultivation_points": user.get("cultivation_points", 0) + diem_tuvi_tang
        })

        # Tạo embed thông báo sử dụng thành công
        embed = Embed(
            title="✅ Sử dụng đan dược thành công!",
            description=f"Bạn đã sử dụng {so_luong} {item['name']}",
            color=0x00FF00
        )
        embed.add_field(name="Hiệu quả", value=f"+{diem_tuvi_tang} điểm tu vi", inline=False)
        embed.add_field(name="Số lượng còn lại", value=f"{inventory.get(item_id, 0)}", inline=False)
        
        await context.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Shop(bot)) 