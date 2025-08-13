from pymongo.database import Database
from typing import Dict, Any
from datetime import datetime
from ...models.place import Place

class PlaceRepository:
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db["places"]

    def get_by_id(self, place_id: str) -> Dict[str, Any]:
        """ID로 장소 정보를 조회합니다."""
        return self.collection.find_one({"source.placeId": place_id})

    def create_or_update_place(self, place_id: str, category: str) -> Dict[str, Any]:
        """
        초기 동기화를 위해 장소 문서를 생성하거나, 이미 존재하면 업데이트하지 않습니다.
        """
        place_doc = {
            "source": {
                "platform": "naver",
                "placeId": place_id,
                "lastFetchedAt": datetime.utcnow()
            },
            "profile": {
                "category": [category]
            }
        }
        # $setOnInsert는 문서가 새로 생성될 때만 값을 설정합니다.
        self.collection.update_one(
            {"source.placeId": place_id},
            {"$setOnInsert": place_doc},
            upsert=True
        )
        return self.get_by_id(place_id)

    def update_synced_data(self, place_id: str, update_data: Dict[str, Any]) -> int:
        """
        동기화 파이프라인을 통해 수집된 정규화된 데이터로 장소 문서를 업데이트합니다.
        """
        # 마지막 fetch 시간을 현재로 갱신
        update_data["source.lastFetchedAt"] = datetime.utcnow()

        result = self.collection.update_one(
            {"source.placeId": place_id},
            {"$set": update_data}
        )
        return result.modified_count