from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timedelta
import aiosqlite
import random

class YCoin(commands.Cog, name="ycoin"):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def ensure_user(self, user_id: str):
        async with aiosqlite.connect("database/database.db") as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, balance, last_daily) VALUES (?, 0, ?)",
                (user_id, "2000-01-01T00:00:00")
            )
            await db.commit()

    @commands.hybrid_command(
        name="xu",
        description="Xem số dư YCoin của bạn"
    )
    async def balance(self, ctx: Context) -> None:
        user_id = str(ctx.author.id)
        await self.ensure_user(user_id)

        async with aiosqlite.connect("database/database.db") as db:
            async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                balance = row[0] if row else 0

        await ctx.send(f"💰 Số dư YCoin của bạn là: **{balance} YCoin**")

    @commands.hybrid_command(
        name="diemdanh",
        description="Nhận YCoin mỗi ngày"
    )
    async def daily(self, ctx: Context) -> None:
        user_id = str(ctx.author.id)
        await self.ensure_user(user_id)

        now = datetime.utcnow()
        async with aiosqlite.connect("database/database.db") as db:
            async with db.execute("SELECT last_daily FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                last_daily = datetime.fromisoformat(row[0]) if row else datetime.min

            if 1==0:
            # if now - last_daily < timedelta(hours=24):
                next_claim = last_daily + timedelta(hours=24)
                remaining = next_claim - now
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes = remainder // 60
                await ctx.send(f"⏳ Bạn cần chờ {remaining.days} ngày, {hours} giờ và {minutes} phút nữa để nhận daily.")
                return

            reward = random.randint(100, 500)
            await db.execute(
                "UPDATE users SET balance = balance + ?, last_daily = ? WHERE user_id = ?",
                (reward, now.isoformat(), user_id)
            )
            await db.commit()

        await ctx.send(f"🎉 Bạn đã nhận được **{reward} YCoin** hôm nay!")


    @commands.hybrid_command(
        name="chuyentien",
        description="Chuyển YCoin cho người khác"
    )
    async def transfer(self, ctx: Context, member: commands.MemberConverter, amount: int) -> None:
        sender_id = str(ctx.author.id)
        receiver_id = str(member.id)

        if member.id == ctx.author.id:
            await ctx.send("❌ Bạn không thể chuyển YCoin cho chính mình.")
            return

        if amount <= 0:
            await ctx.send("❌ Số tiền phải lớn hơn 0.")
            return

        await self.ensure_user(sender_id)
        await self.ensure_user(receiver_id)

        async with aiosqlite.connect("database/database.db") as db:
            # Lấy số dư người gửi
            async with db.execute("SELECT balance FROM users WHERE user_id = ?", (sender_id,)) as cursor:
                row = await cursor.fetchone()
                sender_balance = row[0] if row else 0

            if sender_balance < amount:
                await ctx.send("❌ Bạn không có đủ YCoin để thực hiện giao dịch này.")
                return

            # Cập nhật số dư
            await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, sender_id))
            await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, receiver_id))
            await db.commit()

        await ctx.send(f"✅ Bạn đã chuyển **{amount} YCoin** cho {member.mention}!")

    @commands.command(
        name="rob",
        help="Trộm 5% YCoin từ 1 người ngẫu nhiên trong server"
    )
    async def rob(self, ctx):
        robber_id = str(ctx.author.id)  # Get robber's ID (the user issuing the command)
        await self.ensure_user(robber_id)

        async with aiosqlite.connect("database/database.db") as db:
            # Fetch a random user from the database who has a positive balance and is not the robber
            async with db.execute("SELECT user_id, balance FROM users WHERE balance > 0 AND user_id != ? ORDER BY RANDOM() LIMIT 1", (robber_id,)) as cursor:
                row = await cursor.fetchone()

            if row:
                target_user_id, balance = row
                steal_amount = balance // 20  # 5%

                if steal_amount <= 0:
                    await ctx.send(f"🤷 Người có ID {target_user_id} nghèo quá, không trộm được gì.")
                    return

                # Ensure the robber isn't the target
                if robber_id == target_user_id:
                    await ctx.send("🤔 Bạn không thể trộm chính mình!")
                    return

                # Get the target Discord user object
                target = ctx.guild.get_member(int(target_user_id))

                # Perform the robbery (update balances)
                await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (steal_amount, target_user_id))
                await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (steal_amount, robber_id))
                await db.commit()

                # Send the message about the robbery and mention the target
                if target:
                    await ctx.send(f"🕵️‍♂️ Bạn đã trộm được **{steal_amount} YCoin** từ **{target.mention}**! Đừng để bị bắt nhé 😉")
                else:
                    await ctx.send(f"🕵️‍♂️ Bạn đã trộm được **{steal_amount} YCoin** từ người có ID **{target_user_id}**! Đừng để bị bắt nhé 😉")
            else:
                await ctx.send("😅 Không tìm thấy người có YCoin để trộm!")

async def setup(bot) -> None:
    await bot.add_cog(YCoin(bot))
