from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class MongoDB:
    def __init__(self):
        # Lấy MongoDB URI từ biến môi trường
        uri = os.getenv("MONGODB_URI")
        if not uri:
            logger.error("❌ Không tìm thấy MONGODB_URI trong biến môi trường")
            raise ValueError("MONGODB_URI is required")

        try:
            logger.info("🔄 Đang kết nối đến MongoDB...")
            self.client = AsyncIOMotorClient(uri)
            self.db = self.client.spiritstone  # Sử dụng database spiritstone
            
            # Kiểm tra kết nối đơn giản
            self.client.server_info()
            
            logger.info(f"✅ Đã kết nối thành công đến MongoDB Atlas - Database: spiritstone")
        except Exception as e:
            logger.error(f"❌ Lỗi kết nối MongoDB: {str(e)}")
            raise
        
    async def get_user(self, user_id: str):
        return await self.db.users.find_one({"_id": user_id})
    
    async def update_user(self, user_id: str, data: dict):
        await self.db.users.update_one(
            {"_id": user_id},
            {"$set": data},
            upsert=True
        )
    
    async def get_top_users(self, limit: int = 10, sort_by: str = "cultivation_level"):
        """
        Lấy danh sách người dùng được sắp xếp theo tiêu chí
        
        :param limit: Số lượng người dùng cần lấy
        :param sort_by: Tiêu chí sắp xếp (cultivation_level, spirit_stones, mining_attempts)
        :return: Danh sách người dùng
        """
        sort_field = sort_by
        if sort_by == "cultivation_level":
            cursor = self.db.users.find().sort([
                ("cultivation_level", -1),
                ("cultivation_points", -1)
            ]).limit(limit)
        else:
            cursor = self.db.users.find().sort(sort_field, -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_role_rewards(self, guild_id: str):
        return await self.db.role_rewards.find({"guild_id": guild_id}).to_list(length=None)
    
    async def update_role_reward(self, guild_id: str, role_id: str, reward_amount: int):
        await self.db.role_rewards.update_one(
            {"guild_id": guild_id, "role_id": role_id},
            {"$set": {"reward_amount": reward_amount}},
            upsert=True
        )

mongodb = MongoDB() 