from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from app.models.place import Place # DB 모델을 직접 재사용하거나 API용 모델을 따로 정의할 수 있습니다.

class PlaceSyncRequest(BaseModel):
    """장소 데이터 동기화 요청 스키마"""
    url: HttpUrl

class PlaceSyncResponse(BaseModel):
    """장소 데이터 동기화 응답 스키마"""
    message: str
    place_id: str

class PlaceResponse(Place):
    """
    장소 데이터 조회 응답 스키마.
    DB 모델인 Place를 그대로 상속받아 사용합니다.
    """
    class Config:
        orm_mode = True # Pydantic V1 스타일, V2에서는 from_attributes = True
        allow_population_by_field_name = True
