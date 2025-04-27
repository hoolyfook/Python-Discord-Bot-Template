import logging
import os
import platform
import random
import asyncio
from shutil import ExecError

import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv
import motor.motor_asyncio
from database.mongodb import mongodb

from database import DatabaseManager

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.members = True

class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# File handler
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(os.getenv("PREFIX")),
            intents=intents,
            help_command=None,
        )
        """
        This creates custom bot variables so that we can access these variables in cogs more easily.

        For example, The logger is available using the following code:
        - self.logger # In this class
        - bot.logger # In this file
        - self.bot.logger # In cogs
        """
        self.logger = logger
        self.database = None
        self.bot_prefix = os.getenv("PREFIX")
        self.invite_link = os.getenv("INVITE_LINK")
        self.worker_count = 4  # Số lượng worker mặc định
        self.workers = []  # Danh sách các worker

    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"✅ Đã load extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"❌ Không thể load extension {extension}\n{exception}"
                    )
        # Sync commands after loading all cogs
        try:
            synced = await self.tree.sync()
            self.logger.info(f"✅ Đã đồng bộ {len(synced)} lệnh")
            for cmd in synced:
                self.logger.info(f"  - {cmd.name}")
        except Exception as e:
            self.logger.error(f"❌ Không thể đồng bộ lệnh: {e}")

    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        """
        Setup the game status task of the bot.
        """
        statuses = ["Thiên đạo nhật nguyệt"]
        await self.change_presence(activity=discord.Game(random.choice(statuses)))

    @status_task.before_loop
    async def before_status_task(self) -> None:
        """
        Before starting the status changing task, we make sure the bot is ready
        """
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
        """
        This will just be executed when the bot starts the first time.
        """
        self.logger.info(f"Prefix: {self.bot_prefix}")
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        await self.load_cogs()
        self.status_task.start()
        self.database = DatabaseManager(
            connection=await aiosqlite.connect(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
            )
        )
        await self.start_workers()

    async def on_message(self, message: discord.Message) -> None:
        """
        The code in this event is executed every time someone sends a message, with or without the prefix

        :param message: The message that was sent.
        """
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_completion(self, context: Context) -> None:
        """
        The code in this event is executed every time a normal command has been *successfully* executed.

        :param context: The context of the command that has been executed.
        """
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if context.guild is not None:
            self.logger.info(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
            )
        else:
            self.logger.info(
                f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
            )

    async def on_command_error(self, context: Context, error) -> None:
        """
        The code in this event is executed every time a normal valid command catches an error.

        :param context: The context of the normal command that failed executing.
        :param error: The error that has been faced.
        """
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(
                description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                description="You are not the owner of the bot!", color=0xE02B2B
            )
            await context.send(embed=embed)
            if context.guild:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot."
                )
            else:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot."
                )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description="You are missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to execute this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="I am missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to fully perform this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error!",
                # We need to capitalize because the command arguments have no capital letter in the code and they are the first word in the error message.
                description=str(error).capitalize(),
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        else:
            raise error

    @commands.Cog.listener()
    async def on_ready(self):
        """
        The code in this event is executed when the bot is ready.
        """
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        self.logger.info("-------------------")
        await self.tree.sync()
        self.logger.info("Synced slash commands")
        self.logger.info(f"Bot đã sẵn sàng với {self.worker_count} worker")
        self.logger.info(f"Bot đang chạy với tên: {self.user.name}")
        self.logger.info(f"Bot ID: {self.user.id}")

    async def start_workers(self):
        """Khởi động các worker"""
        self.logger.info(f"Khởi động {self.worker_count} worker")
        for i in range(self.worker_count):
            worker = asyncio.create_task(self.worker_loop(i))
            self.workers.append(worker)

    async def worker_loop(self, worker_id: int):
        """Vòng lặp xử lý của worker"""
        self.logger.info(f"Worker {worker_id} đã khởi động")
        try:
            while True:
                # Xử lý các task trong queue
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.logger.info(f"Worker {worker_id} đã dừng")
        except Exception as e:
            self.logger.error(f"Lỗi trong worker {worker_id}: {str(e)}")

    async def scale_workers(self, new_count: int):
        """Scale số lượng worker"""
        if new_count < 1 or new_count > 10:
            raise ValueError("Số lượng worker phải từ 1 đến 10")

        # Dừng các worker cũ
        for worker in self.workers:
            try:
                await worker.cancel()
            except Exception:
                pass

        self.workers = []
        self.worker_count = new_count

        # Khởi động worker mới
        await self.start_workers()
        self.logger.info(f"Đã scale lên {new_count} worker")

    @commands.hybrid_command(
        name="diemdanh",
        description="Điểm danh hàng ngày để nhận Linh Thạch theo chức vụ"
    )
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def diemdanh(self, ctx: Context) -> None:
        if ctx.guild is None:
            await ctx.send("❌ Lệnh này chỉ dùng được trong server, không dùng được trong DM!")
            return
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        # ... phần còn lại giữ nguyên ...

bot = DiscordBot()

# Load biến môi trường
load_dotenv()

# Khởi tạo MongoDB client
mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URI"))
mongodb.db = mongodb_client[os.getenv("MONGODB_DB")]

bot.run(os.getenv("TOKEN"))
