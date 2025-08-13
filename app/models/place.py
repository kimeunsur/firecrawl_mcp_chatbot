from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

# Pydantic 모델 정의
class Source(BaseModel):
    platform: str = "naver"
    placeId: str
    lastFetchedAt: datetime = Field(default_factory=datetime.utcnow)
    sourceUrl: Optional[HttpUrl] = None

class Coordinates(BaseModel):
    lat: float
    lng: float

class Address(BaseModel):
    road: Optional[str] = None
    lot: Optional[str] = None
    coords: Optional[Coordinates] = None

class Profile(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    category: List[str] = []
    address: Optional[Address] = None

class Hour(BaseModel):
    day: str
    open: str
    close: str
    break_time: Optional[str] = Field(alias="break", default=None)
    last_order: Optional[str] = None

class PopularTimeNow(BaseModel):
    label: Optional[str] = None
    score: Optional[int] = None
    source: str = "absent"
    confidence: float = 0.0

class PopularTime(BaseModel):
    now: PopularTimeNow = Field(default_factory=PopularTimeNow)
    hourly: List[Dict[str, Any]] = []
    sources: Dict[str, bool] = {"naver_text": False, "inference": False}
    lastComputedAt: Optional[datetime] = None

class MenuItem(BaseModel):
    name: str
    price: str
    description: Optional[str] = None
    is_signature: bool = False

class Restaurant(BaseModel):
    menu: List[MenuItem] = []

class Place(BaseModel):
    id: str = Field(alias="_id")
    source: Source
    profile: Profile = Field(default_factory=Profile)
    hours: List[Hour] = []
    popularTimes: PopularTime = Field(default_factory=PopularTime)
    restaurant: Optional[Restaurant] = None
    # 다른 카테고리 모델 추가 가능 (e.g., salon: Optional[Salon] = None)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "place_1690334952",
                "source": {
                    "platform": "naver",
                    "placeId": "1690334952",
                    "lastFetchedAt": "2025-08-12T12:00:00Z",
                    "sourceUrl": "https://m.place.naver.com/restaurant/1690334952/home"
                },
                "profile": {
                    "name": "파이브가이즈 강남",
                    "phone": "1544-3955",
                    "category": ["음식점", "햄버거"],
                    "address": {
                        "road": "서울 서초구 강남대로 435",
                        "lot": "서초동 1305-5",
                        "coords": {"lat": 37.4982, "lng": 127.0265}
                    }
                }
            }
        }
