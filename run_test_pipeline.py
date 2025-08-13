import os
import sys
import asyncio
from pprint import pprint
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.connection import get_database
from app.db.repositories.place_repository import PlaceRepository
from app.services.url_processor import url_processor
from app.services.crawler.client import FirecrawlClient
from app.services.normalizer.data_normalizer import DataNormalizer
from app.services.congestion.predictor import CongestionPredictor
from app.services.sync.sync_pipeline import SyncPipeline

load_dotenv()

async def main():
    """
    "삭제 후 검증" 방식으로 전체 동기화 파이프라인을 테스트합니다.
    """
    print("="*50)
    print("전체 동기화 파이프라인 통합 테스트 시작 (삭제 후 검증)")
    print("="*50)

    # --- 사전 준비 ---
    if not os.getenv("FIRECRAWL_API_KEY") or not os.getenv("MONGO_URI"):
        print(".env 파일에 FIRECRAWL_API_KEY와 MONGO_URI를 모두 설정해야 합니다.")
        return
        
    try:
        db = get_database()
        print(f"MongoDB 연결 성공: {db.client.server_info()['version']}")
        print(f"연결된 데이터베이스: '{db.name}'")
    except Exception as e:
        print(f"MongoDB 연결 실패: {e}")
        return

    place_repo = PlaceRepository(db)
    target_url = "https://map.naver.com/p/entry/place/2009222146"
    place_id = url_processor.process(target_url)["place_id"]
    category = url_processor.process(target_url)["category"]

    # --- 1. 테스트 데이터 삭제 ---
    print(f"\n[STEP 1] DB에서 기존 테스트 데이터 (place_id: {place_id}) 삭제 시도...")
    delete_result = place_repo.collection.delete_one({"source.placeId": place_id})
    if delete_result.deleted_count > 0:
        print(f"기존 문서 {delete_result.deleted_count}개 삭제 완료.")
    else:
        print("삭제할 기존 문서 없음.")

    # --- 2. 파이프라인 실행 ---
    print("\n[STEP 2] 전체 동기화 파이프라인 실행...")
    try:
        pipeline = SyncPipeline(
            place_repo=place_repo,
            crawler=FirecrawlClient(),
            normalizer=DataNormalizer(),
            predictor=CongestionPredictor()
        )
        result = await pipeline.run_sync(place_id, category)
        print("파이프라인 실행 완료.")
        pprint(result)

    except Exception as e:
        print(f"파이프라인 실행 중 오류 발생: {e}")
        return

    # --- 3. 최종 DB 데이터 확인 ---
    print("\n[STEP 3] DB에서 최종 데이터 조회 및 검증...")
    final_db_data = place_repo.get_by_id(place_id)
    
    print("--- DB에 저장된 최종 문서 ---")
    pprint(final_db_data)

    if final_db_data and final_db_data.get("restaurant") and final_db_data.get("restaurant").get("menu"):
        print("\n" + "="*50)
        print("검증 성공: DB에 데이터가 성공적으로 저장되었습니다.")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("검증 실패: DB에 데이터가 없거나 메뉴 정보가 누락되었습니다.")
        print("="*50)

if __name__ == "__main__":
    asyncio.run(main())