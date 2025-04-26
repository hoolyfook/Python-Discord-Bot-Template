import discord
from discord.ext import commands
from discord import Embed
import aiosqlite
import random

class Shop(commands.Cog, name="shop"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.items = {
            "tieu-hoan-dan": {
                "name": "Tiểu Hoàn Đan",
                "price": 1000,
                "description": "Đan dược cấp thấp, giúp tăng 100 điểm tu vi",
                "effect": 100
            },
            "dai-hoan-dan": {
                "name": "Đại Hoàn Đan",
                "price": 5000,
                "description": "Đan dược cấp trung, giúp tăng 500 điểm tu vi",
                "effect": 500
            },
            "than-hoan-dan": {
                "name": "Thần Hoàn Đan",
                "price": 10000,
                "description": "Đan dược cấp cao, giúp tăng 1000 điểm tu vi",
                "effect": 1000
            },
            "tien-hoan-dan": {
                "name": "Tiên Hoàn Đan",
                "price": 50000,
                "description": "Đan dược cấp tiên, giúp tăng 5000 điểm tu vi",
                "effect": 5000
            }
        }

    async def ensure_user(self, user_id: str) -> None:
        async with aiosqlite.connect("database/database.db") as db:
            async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
            if not row:
                await db.execute("INSERT INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
                await db.commit()

    @commands.hybrid_command(
        name="cuahang",
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
                      "3. Sử dụng lệnh `/mua <id>` để mua\n"
                      "   Ví dụ: `/mua tieu-hoan-dan`\n"
                      "4. Kiểm tra số Linh Thạch của bạn bằng lệnh `/tuitruvat`\n"
                      "5. Nếu đủ Linh Thạch, đan dược sẽ được thêm vào kho của bạn\n\n"
                      "**Hướng dẫn sử dụng:**\n"
                      "1. Xem kho đồ bằng lệnh `/tuitruvat`\n"
                      "2. Sử dụng đan dược bằng lệnh `/sudungdan <id>`\n"
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

        embed.set_footer(text="Sử dụng /mua <id> để mua đan dược")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="mua",
        description="Mua đan dược từ cửa hàng"
    )
    async def mua(self, context: commands.Context, item_id: str) -> None:
        """
        Mua đan dược từ cửa hàng

        :param item_id: ID của đan dược muốn mua
        """
        # Kiểm tra đan dược có tồn tại không
        if item_id not in self.items:
            await context.send("❌ Không tìm thấy đan dược này!")
            return

        item = self.items[item_id]
        user_id = str(context.author.id)

        # Đảm bảo người dùng tồn tại trong database
        await self.ensure_user(user_id)

        # Kiểm tra số dư Linh Thạch
        async with aiosqlite.connect("database/database.db") as db:
            async with db.execute("SELECT spirit_stones FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                spirit_stones = row[0] if row else 0

            if spirit_stones < item['price']:
                await context.send(f"❌ Bạn không đủ Linh Thạch để mua {item['name']}!")
                return

            # Trừ Linh Thạch và cập nhật kho
            new_spirit_stones = spirit_stones - item['price']
            await db.execute("UPDATE users SET spirit_stones = ? WHERE user_id = ?", (new_spirit_stones, user_id))
            
            # Cập nhật kho đồ
            async with db.execute("SELECT inventory FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                inventory = row[0] if row else "{}"
                inventory = eval(inventory) if inventory else {}
                
                # Thêm đan dược vào kho
                if item_id in inventory:
                    inventory[item_id] += 1
                else:
                    inventory[item_id] = 1
                    
                await db.execute("UPDATE users SET inventory = ? WHERE user_id = ?", (str(inventory), user_id))
            await db.commit()

        # Tạo embed thông báo mua hàng thành công
        embed = Embed(
            title="✅ Mua hàng thành công!",
            description=f"Bạn đã mua {item['name']} với giá {item['price']} Linh Thạch",
            color=0x00FF00
        )
        embed.add_field(name="Linh Thạch còn lại", value=f"{new_spirit_stones} 🪨", inline=False)
        embed.add_field(name="Hiệu quả", value=f"+{item['effect']} điểm tu vi", inline=False)
        
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="tuitruvat",
        description="Xem kho đồ của bạn"
    )
    async def tuitruvat(self, context: commands.Context) -> None:
        """
        Hiển thị danh sách đan dược trong kho
        """
        user_id = str(context.author.id)
        
        async with aiosqlite.connect("database/database.db") as db:
            async with db.execute("SELECT inventory, spirit_stones FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                inventory = row[0] if row else "{}"
                inventory = eval(inventory) if inventory else {}
                spirit_stones = row[1] if row else 0

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
                        value=f"Hiệu quả: +{item['effect']} điểm tu vi\nSử dụng: `/sudungdan {item_id}`",
                        inline=False
                    )

        await context.send(embed=embed)

    @commands.hybrid_command(
        name="sudungdan",
        description="Sử dụng đan dược để tăng tu vi"
    )
    async def sudungdan(self, context: commands.Context, item_id: str) -> None:
        """
        Sử dụng đan dược để tăng tu vi

        :param item_id: ID của đan dược muốn sử dụng
        """
        # Kiểm tra đan dược có tồn tại không
        if item_id not in self.items:
            await context.send("❌ Không tìm thấy đan dược này!")
            return

        item = self.items[item_id]
        user_id = str(context.author.id)

        # Kiểm tra xem người dùng có đan dược này không
        async with aiosqlite.connect("database/database.db") as db:
            async with db.execute("SELECT inventory FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                inventory = row[0] if row else "{}"
                inventory = eval(inventory) if inventory else {}

            if item_id not in inventory or inventory[item_id] <= 0:
                await context.send(f"❌ Bạn không có {item['name']} trong kho!")
                return

            # Giảm số lượng đan dược trong kho
            inventory[item_id] -= 1
            if inventory[item_id] == 0:
                del inventory[item_id]

            # Cập nhật tu vi
            await db.execute("UPDATE users SET cultivation_points = cultivation_points + ? WHERE user_id = ?", 
                           (item['effect'], user_id))
            await db.execute("UPDATE users SET inventory = ? WHERE user_id = ?", 
                           (str(inventory), user_id))
            await db.commit()

        # Tạo embed thông báo sử dụng thành công
        embed = Embed(
            title="✅ Sử dụng đan dược thành công!",
            description=f"Bạn đã sử dụng {item['name']}",
            color=0x00FF00
        )
        embed.add_field(name="Hiệu quả", value=f"+{item['effect']} điểm tu vi", inline=False)
        embed.add_field(name="Số lượng còn lại", value=f"{inventory.get(item_id, 0)}", inline=False)
        
        await context.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Shop(bot)) 