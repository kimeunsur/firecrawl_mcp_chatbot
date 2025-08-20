from datetime import datetime
from ...db.repositories.place_repository import PlaceRepository
from ..crawler.client import FirecrawlClient
from ..normalizer.data_normalizer import DataNormalizer
from ..congestion.predictor import CongestionPredictor
from ..url_processor import mobile_url_builder
from ...models.place import Place, Source, Profile

class SyncPipeline:
    def __init__(
        self,
        place_repo: PlaceRepository,
        crawler: FirecrawlClient,
        normalizer: DataNormalizer,
        predictor: CongestionPredictor,
    ):
        self.place_repo = place_repo
        self.crawler = crawler
        self.normalizer = normalizer
        self.predictor = predictor

    async def run_sync(self, place_id: str, category: str):
        """
        지정된 장소에 대한 전체 동기화 파이프라인을 실행합니다.
        """
        # 1. DB에 기본 문서 생성 또는 확인
        self.place_repo.create_or_update_place(place_id, category)

        # 2. 모든 소스 페이지 크롤링
        urls = mobile_url_builder.generate_mobile_urls(place_id, category)
        home_content = (await self.crawler.scrape_url(urls.get("home"))).get("content")
        menu_content = (await self.crawler.scrape_url(urls.get("menu"))).get("content")
        # info 페이지는 home과 내용이 중복될 수 있으므로 home_content 재사용
        info_content = home_content 

        # 3. 데이터 정규화
        normalized_menu = self.normalizer.normalize_menu(menu_content)
        normalized_hours = self.normalizer.normalize_hours(info_content)

        # 4. 혼잡도 예측
        place_for_prediction = Place(
            _id=f"place_{place_id}",
            source=Source(placeId=place_id),
            profile=Profile(category=[category])
        )
        predicted_congestion = self.predictor.predict(home_content, place_for_prediction)

        # 5. DB 업데이트를 위한 데이터 구조화
        update_data = {
            "restaurant.menu": [item.dict() for item in normalized_menu],
            "hours": [hour.dict() for hour in normalized_hours],
            "popularTimes.now": predicted_congestion.dict()
        }

        # 6. DB에 최종 데이터 업데이트
        modified_count = self.place_repo.update_synced_data(place_id, update_data)
        
        return {
            "place_id": place_id,
            "modified_count": modified_count,
            "synced_data": update_data
        }
