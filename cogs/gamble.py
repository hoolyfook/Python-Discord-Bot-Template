import discord
from discord.ext import commands
from discord import Embed
from database.mongodb import MongoDB
from datetime import datetime
from utils.constants import CULTIVATION_LEVELS, LEVEL_REQUIREMENTS
import random
from typing import List, Tuple, Dict
import asyncio

class Gamble(commands.Cog, name="Cờ bạc"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.mongodb = MongoDB()
        self.cultivation_levels = CULTIVATION_LEVELS
        self.level_requirements = LEVEL_REQUIREMENTS
        self.active_games = {}  # Lưu trữ các game đang diễn ra

    def get_cultivation_info(self, level):
        level_info = self.cultivation_levels.get(level, {
            "name": "Unknown",
            "color": 0xAAAAAA,
            "description": "Cảnh giới không xác định",
            "tho_nguyen": "Unknown"
        })
        return level_info["name"]

    def create_deck(self) -> List[Tuple[str, str]]:
        """Tạo bộ bài 52 lá"""
        suits = ["♠️", "♥️", "♦️", "♣️"]
        values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        deck = [(value, suit) for suit in suits for value in values]
        random.shuffle(deck)
        return deck

    def evaluate_hand(self, hand: List[Tuple[str, str]]) -> Tuple[str, int, List[int]]:
        """Đánh giá bài và trả về tên hand, điểm và giá trị để so sánh"""
        values = [card[0] for card in hand]
        suits = [card[1] for card in hand]
        
        value_map = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, 
                    "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
        numeric_values = [value_map[v] for v in values]
        numeric_values.sort(reverse=True)

        # Kiểm tra các trường hợp và lưu giá trị để so sánh
        if len(set(suits)) == 1 and len(set(numeric_values)) == 5 and max(numeric_values) - min(numeric_values) == 4:
            return "Thùng phá sảnh", 9, [max(numeric_values)]
        
        if any(numeric_values.count(x) == 4 for x in numeric_values):
            quad_value = [x for x in numeric_values if numeric_values.count(x) == 4][0]
            kicker = [x for x in numeric_values if x != quad_value][0]
            return "Tứ quý", 8, [quad_value, kicker]
        
        if any(numeric_values.count(x) == 3 for x in numeric_values) and any(numeric_values.count(x) == 2 for x in numeric_values):
            triple_value = [x for x in numeric_values if numeric_values.count(x) == 3][0]
            pair_value = [x for x in numeric_values if numeric_values.count(x) == 2][0]
            return "Cù lũ", 7, [triple_value, pair_value]
        
        if len(set(suits)) == 1:
            return "Thùng", 6, sorted(numeric_values, reverse=True)
        
        if len(set(numeric_values)) == 5 and max(numeric_values) - min(numeric_values) == 4:
            return "Sảnh", 5, [max(numeric_values)]
        
        if any(numeric_values.count(x) == 3 for x in numeric_values):
            triple_value = [x for x in numeric_values if numeric_values.count(x) == 3][0]
            kickers = sorted([x for x in numeric_values if x != triple_value], reverse=True)
            return "Sám cô", 4, [triple_value] + kickers
        
        if len([x for x in numeric_values if numeric_values.count(x) == 2]) == 4:
            pairs = sorted([x for x in numeric_values if numeric_values.count(x) == 2], reverse=True)
            kicker = [x for x in numeric_values if x not in pairs][0]
            return "Hai đôi", 3, pairs + [kicker]
        
        if any(numeric_values.count(x) == 2 for x in numeric_values):
            pair_value = [x for x in numeric_values if numeric_values.count(x) == 2][0]
            kickers = sorted([x for x in numeric_values if x != pair_value], reverse=True)
            return "Một đôi", 2, [pair_value] + kickers
        
        return "Mậu thầu", 1, sorted(numeric_values, reverse=True)

    @commands.hybrid_command(
        name="poker",
        description="Chơi poker với linh thạch"
    )
    async def poker(self, context: commands.Context, bet: int) -> None:
        """
        Chơi poker với linh thạch
        bet: Số linh thạch muốn cược
        """
        if bet <= 0:
            await context.send("❌ Số linh thạch cược phải lớn hơn 0!")
            return

        user_id = str(context.author.id)
        user = await self.mongodb.get_user(user_id)
        
        if not user:
            await context.send("❌ Bạn chưa có dữ liệu người chơi!")
            return

        spirit_stones = user.get("spirit_stones", 0)
        if spirit_stones < bet:
            await context.send(f"❌ Bạn không đủ linh thạch! Bạn có {spirit_stones} linh thạch <:linhthachydon:1366455607812427807>.")
            return

        # Tạo bộ bài và chia bài
        deck = self.create_deck()
        player_hand = deck[:5]
        dealer_hand = deck[5:10]

        # Đánh giá bài
        player_hand_name, player_score, player_values = self.evaluate_hand(player_hand)
        dealer_hand_name, dealer_score, dealer_values = self.evaluate_hand(dealer_hand)

        # Hiển thị bài
        player_cards = " ".join([f"{card[0]}{card[1]}" for card in player_hand])
        dealer_cards = " ".join([f"{card[0]}{card[1]}" for card in dealer_hand])

        # Tính kết quả
        if player_score > dealer_score:
            result = "🎉 Thắng"
            winnings = bet
            new_spirit_stones = spirit_stones + winnings
        elif player_score < dealer_score:
            result = "❌ Thua"
            winnings = -bet
            new_spirit_stones = spirit_stones + winnings
        else:
            result = "🤝 Hòa"
            winnings = 0
            new_spirit_stones = spirit_stones

        # Cập nhật linh thạch
        await self.mongodb.update_user(user_id, {
            "spirit_stones": new_spirit_stones
        })

        # Tạo embed
        embed = Embed(
            title="🃏 Kết Quả Poker",
            color=0x00FF00 if winnings > 0 else 0xFF0000 if winnings < 0 else 0xFFFF00
        )
        
        embed.add_field(
            name="Bài của bạn",
            value=f"{player_cards}\n**{player_hand_name}**",
            inline=False
        )
        
        embed.add_field(
            name="Bài của nhà cái",
            value=f"{dealer_cards}\n**{dealer_hand_name}**",
            inline=False
        )
        
        embed.add_field(
            name="Kết quả",
            value=f"{result}\nLinh thạch: {winnings:+d}",
            inline=False
        )
        
        embed.add_field(
            name="Linh thạch hiện tại",
            value=f"{new_spirit_stones} linh thạch <:linhthachydon:1366455607812427807>",
            inline=False
        )

        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="taixiu",
        description="Chơi tài xỉu với linh thạch"
    )
    async def taixiu(self, context: commands.Context, choice: str, bet: int) -> None:
        """
        Chơi tài xỉu với linh thạch
        choice: "tai" hoặc "xiu"
        bet: Số linh thạch muốn cược
        """
        # Validate choice
        choice = choice.lower()
        if choice not in ["tai", "xiu"]:
            await context.send("❌ Lựa chọn không hợp lệ! Chỉ được chọn 'tai' hoặc 'xiu'")
            return

        # Validate bet amount
        if bet <= 0:
            await context.send("❌ Số linh thạch cược phải lớn hơn 0!")
            return

        user_id = str(context.author.id)
        user = await self.mongodb.get_user(user_id)
        
        if not user:
            await context.send("❌ Bạn chưa có dữ liệu người chơi!")
            return

        spirit_stones = user.get("spirit_stones", 0)
        if spirit_stones < bet:
            await context.send(f"❌ Bạn không đủ linh thạch! Bạn có {spirit_stones} linh thạch <:linhthachydon:1366455607812427807>.")
            return

        # Roll 3 dice
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        dice3 = random.randint(1, 6)
        total = dice1 + dice2 + dice3

        # Determine result
        result = "tai" if total >= 11 else "xiu"
        
        # Calculate winnings
        if choice == result:
            winnings = bet
            new_spirit_stones = spirit_stones + winnings
            result_text = "🎉 Thắng"
        else:
            winnings = -bet
            new_spirit_stones = spirit_stones + winnings
            result_text = "❌ Thua"

        # Update user's spirit stones
        await self.mongodb.update_user(user_id, {
            "spirit_stones": new_spirit_stones
        })

        # Create embed
        embed = Embed(
            title="🎲 Kết Quả Tài Xỉu",
            color=0x00FF00 if choice == result else 0xFF0000
        )
        embed.add_field(name="Xúc xắc", value=f"🎲 {dice1} 🎲 {dice2} 🎲 {dice3}", inline=False)
        embed.add_field(name="Tổng", value=f"{total} ({result.upper()})", inline=False)
        embed.add_field(name="Lựa chọn", value=choice.upper(), inline=False)
        embed.add_field(name="Kết quả", value=result_text, inline=False)
        embed.add_field(name="Linh thạch", value=f"{winnings:+d} linh thạch", inline=False)
        embed.add_field(name="Linh thạch hiện tại", value=f"{new_spirit_stones} linh thạch <:linhthachydon:1366455607812427807>", inline=False)

        await context.send(embed=embed)

    @commands.hybrid_command(
        name="pokersolo",
        description="Chơi poker 1v1 theo kiểu tố"
    )
    async def pokersolo(self, context: commands.Context, bet: int, target: discord.Member) -> None:
        """
        Chơi poker 1v1 theo kiểu tố
        bet: Số linh thạch muốn cược
        target: Người chơi muốn thách đấu
        """
        if bet <= 0:
            await context.send("❌ Số linh thạch cược phải lớn hơn 0!")
            return

        if target.bot:
            await context.send("❌ Không thể chơi với bot!")
            return

        if target.id == context.author.id:
            await context.send("❌ Không thể tự chơi với chính mình!")
            return

        # Kiểm tra linh thạch của cả hai người
        player1_id = str(context.author.id)
        player2_id = str(target.id)
        
        player1 = await self.mongodb.get_user(player1_id)
        player2 = await self.mongodb.get_user(player2_id)
        
        if not player1 or not player2:
            await context.send("❌ Một trong hai người chơi chưa có dữ liệu!")
            return

        player1_stones = player1.get("spirit_stones", 0)
        player2_stones = player2.get("spirit_stones", 0)
        
        if player1_stones < bet:
            await context.send(f"❌ Bạn không đủ linh thạch! Bạn có {player1_stones} linh thạch.")
            return
            
        if player2_stones < bet:
            await context.send(f"❌ {target.name} không đủ linh thạch! Họ có {player2_stones} linh thạch.")
            return

        # Tạo game mới
        game_id = f"{player1_id}_{player2_id}"
        if game_id in self.active_games:
            await context.send("❌ Đã có một game đang diễn ra giữa hai người!")
            return

        # Gửi lời mời
        embed = Embed(
            title="🎴 Lời Mời Chơi Poker",
            description=f"{context.author.mention} đã thách đấu {target.mention} chơi poker với số cược {bet:,} linh thạch!",
            color=0x00FF00
        )
        embed.add_field(
            name="Thời gian chờ",
            value="Bạn có 30 giây để chấp nhận lời mời!",
            inline=False
        )
        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        msg = await context.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        try:
            def check(reaction, user):
                return user == target and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == msg.id

            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            if str(reaction.emoji) == "❌":
                await context.send(f"❌ {target.mention} đã từ chối lời mời!")
                return
                
        except asyncio.TimeoutError:
            await context.send("❌ Đã hết thời gian chờ phản hồi!")
            return

        # Bắt đầu game
        self.active_games[game_id] = {
            "player1": player1_id,
            "player2": player2_id,
            "bet": bet,
            "pot": bet * 2,
            "deck": self.create_deck(),
            "community_cards": [],
            "current_player": player1_id,
            "last_bet": bet,
            "round": 0  # 0: Pre-flop, 1: Flop, 2: Turn, 3: River
        }

        # Chia bài
        game = self.active_games[game_id]
        game["player1_hand"] = game["deck"][:2]
        game["player2_hand"] = game["deck"][2:4]
        game["deck"] = game["deck"][4:]

        # Hiển thị bài
        await self.show_game_state(context, game_id)

    async def show_game_state(self, context: commands.Context, game_id: str) -> None:
        """Hiển thị trạng thái game"""
        game = self.active_games[game_id]
        player1 = self.bot.get_user(int(game["player1"]))
        player2 = self.bot.get_user(int(game["player2"]))

        # Gửi bài cho người chơi 1
        player1_cards = " ".join([f"{card[0]}{card[1]}" for card in game["player1_hand"]])
        await player1.send(embed=Embed(title="🎴 Bài của bạn", description=player1_cards, color=0x00FF00))

        # Gửi bài cho người chơi 2
        player2_cards = " ".join([f"{card[0]}{card[1]}" for card in game["player2_hand"]])
        await player2.send(embed=Embed(title="🎴 Bài của bạn", description=player2_cards, color=0x00FF00))

        # Hiển thị trạng thái game công khai
        embed = Embed(title="🎴 Poker 1v1", description=f"Ván bài đang diễn ra giữa {player1.mention} và {player2.mention}", color=0x00FF00)
        
        # Hiển thị bài chung
        community_cards = " ".join([f"{card[0]}{card[1]}" for card in game["community_cards"]]) if game["community_cards"] else "Chưa có bài chung"
        embed.add_field(name="Bài chung", value=community_cards, inline=False)

        # Hiển thị pot và lượt chơi hiện tại
        embed.add_field(name="Pot hiện tại", value=f"{game['pot']:,} linh thạch", inline=False)
        
        # Hiển thị số linh thạch tố gần nhất
        embed.add_field(
            name="Số linh thạch tố gần nhất",
            value=f"{game['last_bet']:,} linh thạch",
            inline=False
        )
        
        # Hiển thị lượt chơi và hướng dẫn
        current_player = self.bot.get_user(int(game["current_player"]))
        action_guide = (
            f"Đến lượt {current_player.mention}\n\n"
            "**Hướng dẫn:**\n"
            "📈 - Tố thêm (Raise): Tố thêm linh thạch vào pot\n"
            "👋 - Theo (Call/Check): Theo số linh thạch đã tố hoặc không tố thêm\n"
            "❌ - Bỏ bài (Fold): Bỏ bài và để đối thủ thắng pot"
        )
        embed.add_field(
            name="Lượt chơi",
            value=action_guide,
            inline=False
        )

        # Hiển thị vòng chơi hiện tại
        round_names = {
            0: "Pre-flop (Chưa có bài chung)",
            1: "Flop (3 lá bài chung đầu tiên)",
            2: "Turn (Lá bài chung thứ 4)",
            3: "River (Lá bài chung cuối cùng)"
        }
        embed.add_field(
            name="Vòng chơi hiện tại",
            value=round_names.get(game["round"], "Không xác định"),
            inline=False
        )
        
        # Thêm các nút hành động
        msg = await context.send(embed=embed)
        await msg.add_reaction("📈")  # Tố
        await msg.add_reaction("👋")  # Theo
        await msg.add_reaction("❌")  # Bỏ bài

        # Chờ người chơi hành động
        try:
            def check(reaction, user):
                return user.id == int(game["current_player"]) and str(reaction.emoji) in ["📈", "👋", "❌"] and reaction.message.id == msg.id

            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            
            if str(reaction.emoji) == "❌":
                # Xử lý bỏ bài
                winner_id = game["player2"] if game["current_player"] == game["player1"] else game["player1"]
                await self.end_game(context, game_id, winner_id)
                return
                
            elif str(reaction.emoji) == "📈":
                # Xử lý tố
                await self.handle_bet(context, game_id)
                
            elif str(reaction.emoji) == "👋":
                # Xử lý theo
                if game["last_bet"] > 0:
                    # Nếu có người tố trước đó, người chơi hiện tại phải theo số linh thạch đó
                    current_player_id = game["current_player"]
                    await self.mongodb.update_user(current_player_id, {
                        "spirit_stones": (await self.mongodb.get_user(current_player_id))["spirit_stones"] - game["last_bet"]
                    })
                    game["pot"] += game["last_bet"]
                
                game["current_player"] = game["player2"] if game["current_player"] == game["player1"] else game["player1"]
                
                # Nếu cả hai người đã theo, mới chuyển sang vòng tiếp theo
                if game.get("both_checked", False):
                    game["round"] += 1
                    game["both_checked"] = False
                    game["last_bet"] = 0  # Reset số linh thạch tố cho vòng mới
                    
                    if game["round"] > 3:
                        # Kết thúc ván bài
                        await self.showdown(context, game_id)
                    else:
                        # Chia bài chung mới
                        if game["round"] == 1:  # Flop
                            game["community_cards"] = game["deck"][:3]
                            game["deck"] = game["deck"][3:]
                        elif game["round"] in [2, 3]:  # Turn và River
                            game["community_cards"].append(game["deck"][0])
                            game["deck"] = game["deck"][1:]
                        
                        await self.show_game_state(context, game_id)
                else:
                    # Đánh dấu người chơi này đã theo
                    game["both_checked"] = True
                    # Hiển thị trạng thái mới và chờ người kia hành động
                    await self.show_game_state(context, game_id)
                
        except asyncio.TimeoutError:
            # Xử lý hết thời gian
            await context.send(f"❌ {player1.mention} đã hết thời gian hành động (60 giây)!")
            winner_id = game["player2"] if game["current_player"] == game["player1"] else game["player1"]
            await self.end_game(context, game_id, winner_id)

    async def handle_bet(self, context: commands.Context, game_id: str) -> None:
        """Xử lý hành động tố"""
        game = self.active_games[game_id]
        current_player = self.bot.get_user(int(game["current_player"]))
        
        # Lấy thông tin người chơi từ database
        current_player_data = await self.mongodb.get_user(str(current_player.id))
        current_spirit_stones = current_player_data.get("spirit_stones", 0)
        
        embed = Embed(
            title="📈 Tố thêm linh thạch",
            description=(
                f"{current_player.mention}, hãy nhập số linh thạch muốn tố\n\n"
                f"**Hướng dẫn:**\n"
                f"• Số linh thạch tố phải lớn hơn số tố gần nhất: {game['last_bet']:,}\n"
                f"• Linh thạch hiện có: {current_spirit_stones:,}\n"
                f"• Nhập số linh thạch trong vòng 30 giây"
            ),
            color=0x00FF00
        )
        await context.send(embed=embed)
        
        try:
            def check(m):
                return m.author.id == int(game["current_player"]) and m.channel == context.channel

            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            
            try:
                bet_amount = int(msg.content)
                
                # Kiểm tra số linh thạch tố
                if bet_amount <= game["last_bet"]:
                    await context.send(
                        f"❌ Số linh thạch tố ({bet_amount:,}) phải lớn hơn số tố gần nhất ({game['last_bet']:,})!"
                    )
                    await self.show_game_state(context, game_id)
                    return
                    
                if bet_amount > current_spirit_stones:
                    await context.send(
                        f"❌ Bạn không đủ linh thạch! Bạn chỉ có {current_spirit_stones:,} linh thạch."
                    )
                    await self.show_game_state(context, game_id)
                    return
                
                # Trừ linh thạch của người chơi
                await self.mongodb.update_user(str(current_player.id), {
                    "spirit_stones": current_spirit_stones - bet_amount
                })
                
                # Cập nhật pot và last_bet
                game["pot"] += bet_amount
                game["last_bet"] = bet_amount
                game["current_player"] = game["player2"] if game["current_player"] == game["player1"] else game["player1"]
                game["both_checked"] = False  # Reset trạng thái theo khi có người tố mới
                
                # Thông báo tố thành công
                await context.send(
                    f"✅ {current_player.mention} đã tố {bet_amount:,} linh thạch!"
                )
                
                await self.show_game_state(context, game_id)
                
            except ValueError:
                await context.send("❌ Vui lòng nhập một số nguyên hợp lệ!")
                await self.show_game_state(context, game_id)
                
        except asyncio.TimeoutError:
            await context.send(f"❌ {current_player.mention} đã hết thời gian tố!")
            await self.show_game_state(context, game_id)

    async def showdown(self, context: commands.Context, game_id: str) -> None:
        """So bài khi kết thúc ván"""
        game = self.active_games[game_id]
        
        # Tạo hand hoàn chỉnh cho mỗi người chơi
        player1_hand = game["player1_hand"] + game["community_cards"]
        player2_hand = game["player2_hand"] + game["community_cards"]
        
        # Đánh giá bài
        player1_hand_name, player1_score, player1_values = self.evaluate_hand(player1_hand)
        player2_hand_name, player2_score, player2_values = self.evaluate_hand(player2_hand)
        
        # Xác định người thắng
        if player1_score > player2_score:
            winner_id = game["player1"]
        elif player2_score > player1_score:
            winner_id = game["player2"]
        else:
            # Nếu cùng loại hand, so sánh giá trị
            for p1_val, p2_val in zip(player1_values, player2_values):
                if p1_val > p2_val:
                    winner_id = game["player1"]
                    break
                elif p2_val > p1_val:
                    winner_id = game["player2"]
                    break
            else:
                # Nếu tất cả giá trị đều bằng nhau
                winner_id = None
                
        await self.end_game(context, game_id, winner_id)

    async def end_game(self, context: commands.Context, game_id: str, winner_id: str = None) -> None:
        """Kết thúc game và trao thưởng"""
        game = self.active_games[game_id]
        player1 = self.bot.get_user(int(game["player1"]))
        player2 = self.bot.get_user(int(game["player2"]))
        
        embed = Embed(
            title="🎴 Kết Thúc Ván Bài",
            color=0x00FF00
        )
        
        if winner_id:
            winner = self.bot.get_user(int(winner_id))
            embed.description = f"🎉 {winner.mention} đã thắng {game['pot']:,} linh thạch!"
            
            # Cập nhật linh thạch
            if winner_id == game["player1"]:
                await self.mongodb.update_user(game["player1"], {
                    "spirit_stones": (await self.mongodb.get_user(game["player1"]))["spirit_stones"] + game["pot"]
                })
                await self.mongodb.update_user(game["player2"], {
                    "spirit_stones": (await self.mongodb.get_user(game["player2"]))["spirit_stones"] - game["bet"]
                })
            else:
                await self.mongodb.update_user(game["player2"], {
                    "spirit_stones": (await self.mongodb.get_user(game["player2"]))["spirit_stones"] + game["pot"]
                })
                await self.mongodb.update_user(game["player1"], {
                    "spirit_stones": (await self.mongodb.get_user(game["player1"]))["spirit_stones"] - game["bet"]
                })
        else:
            # Hòa, trả lại linh thạch
            embed.description = "🤝 Ván bài hòa! Mỗi người nhận lại số linh thạch đã cược."
            await self.mongodb.update_user(game["player1"], {
                "spirit_stones": (await self.mongodb.get_user(game["player1"]))["spirit_stones"] + game["bet"]
            })
            await self.mongodb.update_user(game["player2"], {
                "spirit_stones": (await self.mongodb.get_user(game["player2"]))["spirit_stones"] + game["bet"]
            })
        
        # Hiển thị bài của cả hai người
        player1_cards = " ".join([f"{card[0]}{card[1]}" for card in game["player1_hand"]])
        player2_cards = " ".join([f"{card[0]}{card[1]}" for card in game["player2_hand"]])
        community_cards = " ".join([f"{card[0]}{card[1]}" for card in game["community_cards"]])
        
        embed.add_field(
            name=f"Bài của {player1.name}",
            value=player1_cards,
            inline=False
        )
        embed.add_field(
            name=f"Bài của {player2.name}",
            value=player2_cards,
            inline=False
        )
        embed.add_field(
            name="Bài chung",
            value=community_cards,
            inline=False
        )
        
        embed.set_footer(text=f"SpiritStone Bot | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await context.send(embed=embed)
        
        # Xóa game khỏi active_games
        del self.active_games[game_id]

async def setup(bot) -> None:
    await bot.add_cog(Gamble(bot)) 