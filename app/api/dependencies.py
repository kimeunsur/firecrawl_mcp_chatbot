from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.connection import get_database
from app.db.repositories.policy_repository import PolicyRepository

def get_policy_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> PolicyRepository:
    return PolicyRepository(db)
