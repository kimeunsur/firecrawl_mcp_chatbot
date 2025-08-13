from pymongo import MongoClient
from pymongo.database import Database
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDBConnection:
    _client = None
    _db = None

    @classmethod
    def get_client(cls) -> MongoClient:
        if cls._client is None:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ValueError("MONGO_URI 환경 변수가 설정되지 않았습니다.")
            cls._client = MongoClient(mongo_uri)
        return cls._client

    @classmethod
    def get_db(cls) -> Database:
        if cls._db is None:
            client = cls.get_client()
            # 데이터베이스 이름을 환경 변수에서 가져오거나 기본값을 사용
            db_name = os.getenv("MONGO_DB_NAME", "reservation")
            cls._db = client[db_name]
        return cls._db

def get_database() -> Database:
    """애플리케이션 전체에서 사용할 DB 인스턴스를 반환하는 의존성 주입용 함수"""
    return MongoDBConnection.get_db()

print(MongoDBConnection.get_db())