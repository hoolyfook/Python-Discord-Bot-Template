import time
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timedelta
import aiosqlite
import random

class YCoin(commands.Cog, name="ycoin"):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def ensure_user(self, user_id: str, username: str = None) -> None:
        # Ensure the user exists in the database, and update the username if necessary
        async with aiosqlite.connect("database/database.db") as db:
            # Check if the user exists in the database
            async with db.execute("SELECT user_id, username FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()

            if not row:
                # If the user doesn't exist, insert them into the database with the provided username
                await db.execute("INSERT INTO users (user_id, username, balance, last_daily) VALUES (?, ?, 0, ?)", 
                                (user_id, username, int(time.time())))
                await db.commit()
            else:
                # If the user exists but the username is different, update the username
                if row[1] != username:
                    await db.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
                    await db.commit()

    @commands.hybrid_command(
        name="xu",
        description="Xem số dư YCoin của bạn"
    )
    async def balance(self, ctx: Context) -> None:
        user_id = str(ctx.author.id)
        await self.ensure_user(user_id, username=ctx.author.name)

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
        await self.ensure_user(user_id, username=ctx.author.name)

        # Get the current time
        current_time = int(time.time())

        async with aiosqlite.connect("database/database.db") as db:
            # Fetch the last claim time of the user
            async with db.execute("SELECT last_daily FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()

            if row:
                last_daily_time = row[0]

                # Check if a full day (24 hours) has passed
                time_difference = current_time - last_daily_time
                if time_difference > 86400:
                    # If less than 24 hours, notify the user they need to wait
                    await ctx.send(f"⏳ Bạn đã nhận YCoin gần đây. Hãy quay lại sau {86400 - time_difference} giây nữa.")
                    return

                # Update the user's last claim timestamp and grant YCoin
                daily_reward = 100  # Amount of YCoin for daily claim
                await db.execute("UPDATE users SET balance = balance + ?, last_daily = ? WHERE user_id = ?", 
                                 (daily_reward, current_time, user_id))
                await db.commit()

                # Send the success message
                await ctx.send(f"🎉 Bạn đã nhận được **{daily_reward} YCoin**! Hẹn gặp lại ngày mai! 💰")
            else:
                # In case the user data doesn't exist (should not happen if `ensure_user` works properly)
                await ctx.send("⚠️ Lỗi khi truy xuất dữ liệu người dùng.")

    @commands.hybrid_command(
        name="chuyen",
        description="Chuyển YCoin cho người khác"
    )
    async def transfer(self, ctx: Context, member: commands.MemberConverter, amount: int) -> None:
        sender_id = str(ctx.author.id)
        receiver_id = str(member.id)

        # Ensure the user isn't transferring YCoins to themselves
        if member.id == ctx.author.id:
            await ctx.send("❌ Bạn không thể chuyển YCoin cho chính mình.")
            return

        # Ensure the amount is valid
        if amount <= 0:
            await ctx.send("❌ Số tiền phải lớn hơn 0.")
            return

        await self.ensure_user(sender_id, username=ctx.author.name)
        await self.ensure_user(receiver_id, username=member.name)

        async with aiosqlite.connect("database/database.db") as db:
            # Lấy số dư người gửi
            async with db.execute("SELECT balance FROM users WHERE user_id = ?", (sender_id,)) as cursor:
                row = await cursor.fetchone()
                sender_balance = row[0] if row else 0

            # Check if the sender has enough balance
            if sender_balance < amount:
                await ctx.send("❌ Bạn không có đủ YCoin để thực hiện giao dịch này.")
                return

            # Update the user's balance and usernames
            await db.execute("UPDATE users SET balance = balance - ?, username = ? WHERE user_id = ?", 
                            (amount, ctx.author.name, sender_id))
            await db.execute("UPDATE users SET balance = balance + ?, username = ? WHERE user_id = ?", 
                            (amount, member.name, receiver_id))
            await db.commit()

        # Send confirmation message
        await ctx.send(f"✅ Bạn đã chuyển **{amount} YCoin** cho {member.mention}!")

    @commands.command(
        name="rob",
        description="Trộm 5% YCoin từ 1 người ngẫu nhiên trong server"
    )
    async def rob(self, ctx: Context) -> None:
        robber_id = str(ctx.author.id)  # Get robber's ID (the user issuing the command)
        await self.ensure_user(robber_id, username=ctx.author.name)

        async with aiosqlite.connect("database/database.db") as db:
            # Fetch a random user from the database who has a positive balance and is not the robber
            async with db.execute(
                "SELECT user_id, balance FROM users WHERE balance > 0 AND user_id != ? ORDER BY RANDOM() LIMIT 1", 
                (robber_id,)
            ) as cursor:
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

                if target:
                    # Perform the robbery (update balances)
                    await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (steal_amount, target_user_id))
                    await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (steal_amount, robber_id))
                    await db.commit()

                    # Send the message about the robbery and mention the target
                    await ctx.send(f"🕵️‍♂️ Bạn đã trộm được **{steal_amount} YCoin** từ <@{target_user_id}>!")
                else:
                    # If the target is no longer in the server, find another target or notify the user
                    await ctx.send(f"😅 Người có ID {target_user_id} không còn trong server.")
                    # Optionally, you can repeat the query or inform the user there's no valid target.
            else:
                await ctx.send("😅 Không tìm thấy người có YCoin để trộm!")

async def setup(bot) -> None:
    await bot.add_cog(YCoin(bot))
