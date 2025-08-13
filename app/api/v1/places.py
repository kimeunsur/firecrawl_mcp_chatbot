from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from ...services.sync.sync_pipeline import SyncPipeline
from ...services.url_processor import url_processor
from ...db.repositories.place_repository import PlaceRepository
from ...db.connection import get_database
from ...schemas.place_schema import PlaceSyncRequest, PlaceSyncResponse, PlaceResponse
from pymongo.database import Database

# 의존성 주입: SyncPipeline
def get_sync_pipeline(db: Database = Depends(get_database)) -> SyncPipeline:
    from ...services.crawler.client import FirecrawlClient
    from ...services.normalizer.data_normalizer import DataNormalizer
    from ...services.congestion.predictor import CongestionPredictor
    
    return SyncPipeline(
        place_repo=PlaceRepository(db),
        crawler=FirecrawlClient(),
        normalizer=DataNormalizer(),
        predictor=CongestionPredictor()
    )

# 의존성 주입: PlaceRepository
def get_place_repository(db: Database = Depends(get_database)) -> PlaceRepository:
    return PlaceRepository(db)

router = APIRouter()

@router.post("/places/sync", response_model=PlaceSyncResponse, status_code=202)
async def trigger_sync(
    request: PlaceSyncRequest,
    background_tasks: BackgroundTasks,
    pipeline: SyncPipeline = Depends(get_sync_pipeline)
):
    """
    Naver Place URL을 받아 해당 장소의 데이터 동기화를 비동기적으로 시작합니다.
    """
    try:
        processed_info = url_processor.process(str(request.url))
        place_id = processed_info["place_id"]
        category = processed_info["category"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"잘못된 URL입니다: {e}")

    background_tasks.add_task(pipeline.run_sync, place_id, category)

    return {"message": "데이터 동기화 작업이 시작되었습니다.", "place_id": place_id}

# app/api/v1/places.py
@router.get("/places/{place_id}", response_model=PlaceResponse)
def get_place_by_id(
    place_id: str,
    repo: PlaceRepository = Depends(get_place_repository)
):
    """
    DB에 저장된 특정 장소의 모든 정보를 조회합니다.
    """
    place_data = repo.get_by_id(place_id)
    if not place_data:
        raise HTTPException(status_code=404, detail="해당 ID의 장소를 찾을 수 없습니다.")
    
    # ObjectId를 str으로 변환하여 FastAPI 유효성 검사 오류를 해결
    if '_id' in place_data:
        place_data['_id'] = str(place_data['_id'])
        
    return place_data
