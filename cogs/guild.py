import discord
from discord.ext import commands
from discord import Embed

class Guild(commands.Cog, name="Guild"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="sotay",
        description="Hiển thị sổ tay hướng dẫn tân thủ"
    )
    async def sotay(self, context: commands.Context) -> None:
        """
        Hiển thị sổ tay hướng dẫn tân thủ
        """
        embed = Embed(
            title="📖 Sổ Tay Tân Thủ",
            description="Chào mừng bạn đến với thế giới tu luyện! Dưới đây là hướng dẫn cơ bản:",
            color=0x00FF00
        )

        # Phần 1: Hệ thống tu luyện
        embed.add_field(
            name="🎯 Hệ Thống Tu Luyện",
            value="```\n"
                  "1. Sử dụng lệnh /tuvi để xem thông tin tu luyện\n"
                  "2. Sử dụng lệnh /khaithach để khai thác linh thạch\n"
                  "3. Sử dụng lệnh /dotpha để đột phá lên cấp độ cao hơn\n"
                  "4. Sử dụng lệnh /cuahang để mua đan dược\n"
                  "5. Sử dụng lệnh /sudungdan để sử dụng đan dược\n"
                  "```",
            inline=False
        )

        # Phần 2: Cấp độ tu luyện
        embed.add_field(
            name="📈 Cấp Độ Tu Luyện",
            value="```\n"
                  "0. Phàm Nhân (1000 điểm)\n"
                  "1. Luyện Khí (2000 điểm)\n"
                  "2. Trúc Cơ (5000 điểm)\n"
                  "3. Kim Đan (10000 điểm)\n"
                  "4. Nguyên Anh (20000 điểm)\n"
                  "5. Hóa Thần (50000 điểm)\n"
                  "6. Hợp Thể (100000 điểm)\n"
                  "7. Đại Thừa (200000 điểm)\n"
                  "8. Tiên Nhân (500000 điểm)\n"
                  "9. Kim Tiên (1000000 điểm)\n"
                  "10. Đại La Kim Tiên (2000000 điểm)\n"
                  "```",
            inline=False
        )

        # Phần 3: Hệ thống đan dược
        embed.add_field(
            name="💊 Hệ Thống Đan Dược",
            value="```\n"
                  "1. Tiểu Hoàn Đan: +100 điểm tu vi\n"
                  "2. Đại Hoàn Đan: +500 điểm tu vi\n"
                  "3. Thần Hoàn Đan: +1000 điểm tu vi\n"
                  "4. Tiên Hoàn Đan: +5000 điểm tu vi\n"
                  "5. Kim Đan: +10000 điểm tu vi\n"
                  "6. Nguyên Anh Đan: +50000 điểm tu vi\n"
                  "7. Hóa Thần Đan: +100000 điểm tu vi\n"
                  "8. Hợp Thể Đan: +500000 điểm tu vi\n"
                  "9. Đại Thừa Đan: +1000000 điểm tu vi\n"
                  "10. Tiểu Tiên Đan: +5000000 điểm tu vi\n"
                  "11. Đại Tiên Đan: +10000000 điểm tu vi\n"
                  "12. Tiểu Thần Đan: +50000000 điểm tu vi\n"
                  "13. Đại Thần Đan: +100000000 điểm tu vi\n"
                  "```",
            inline=False
        )

        # Phần 4: Hệ thống đạo lữ
        embed.add_field(
            name="💑 Hệ Thống Đạo Lữ",
            value="```\n"
                  "1. Sử dụng lệnh /daolu để xem bảng xếp hạng đạo lữ\n"
                  "2. Sử dụng lệnh /tinhdan để xem danh sách tình đan\n"
                  "3. Sử dụng lệnh /sudung để sử dụng tình đan\n"
                  "```",
            inline=False
        )

        # Phần 5: Lưu ý quan trọng
        embed.add_field(
            name="⚠️ Lưu Ý Quan Trọng",
            value="```\n"
                  "1. Khi đột phá thành công, điểm tu vi sẽ reset về 0\n"
                  "2. Khi đột phá thất bại, điểm tu vi sẽ bị trừ\n"
                  "3. Tỷ lệ đột phá thành công phụ thuộc vào điểm tu vi dư thừa\n"
                  "4. Sử dụng đan dược để tăng điểm tu vi nhanh hơn\n"
                  "5. Tình đan có thể tăng độ thân mật với đạo lữ\n"
                  "```",
            inline=False
        )

        embed.set_footer(text="Chúc bạn tu luyện thành công!")
        await context.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Guild(bot)) 