from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.policy import Policy
from typing import Dict, Any

class PolicyRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db["polices"]

    async def create_policy(self, policy: Policy) -> str:
        """
        새로운 정책 문서를 MongoDB에 삽입합니다.
        """
        policy_dict = policy.model_dump(by_alias=True)
        result = await self.collection.insert_one(policy_dict)
        return str(result.inserted_id)

    async def get_policy_by_id(self, policy_id: str) -> Dict[str, Any]:
        """
        ID로 정책 문서를 조회합니다.
        """
        from bson import ObjectId
        policy = await self.collection.find_one({"_id": ObjectId(policy_id)})
        return policy
