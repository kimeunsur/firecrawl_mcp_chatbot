import unittest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

# `google.generativeai` 모듈을 모의 처리합니다.
# 이 코드는 테스트 파일의 다른 import 문보다 먼저 실행되어야 합니다.
mock_genai = MagicMock()
with patch.dict('sys.modules', {'google.generativeai': mock_genai}):
    from app.services.crawler.client import FirecrawlClient, FirecrawlException
    from app.services.crawler.menu_crawler import crawl_menu
    from app.services.crawler.hours_crawler import crawl_hours
    from app.services.crawler.congestion_crawler import crawl_congestion
    from app.services.crawler.unified_crawler import UnifiedCrawler

# 통일된 place_id
PLACE_ID = "1690334952"

# 비동기 테스트를 위한 데코레이터
def async_test(f):
    def wrapper(*args, **kwargs):
        asyncio.run(f(*args, **kwargs))
    return wrapper

class TestCrawler(unittest.TestCase):

    def setUp(self):
        """각 테스트 전에 `FirecrawlClient` 인스턴스를 생성하고 `crawl` 메서드를 모의 처리합니다."""
        # `genai.configure`와 `genai.GenerativeModel`이 호출될 때 아무 작업도 수행하지 않도록 설정합니다.
        mock_genai.configure = MagicMock()
        mock_model = MagicMock()
        # `crawl` 메서드를 AsyncMock으로 설정하여 비동기 호출을 시뮬레이션합니다.
        mock_model.crawl = AsyncMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # 이제 FirecrawlClient를 안전하게 인스턴스화할 수 있습니다.
        self.client = FirecrawlClient(api_key="fake_key")
        # 테스트에서 모의 처리된 crawl 메서드를 쉽게 사용할 수 있도록 self에 할당합니다.
        self.mock_crawl = mock_model.crawl

    @async_test
    async def test_crawl_menu_success(self):
        """메뉴 크롤링 함수가 성공적으로 데이터를 반환하는지 테스트합니다."""
        self.mock_crawl.return_value = {"data": {"llm_extraction": [{"name": "아메리카노"}]}}
        result = await crawl_menu(self.client, PLACE_ID, "cafe")
        self.assertEqual(result[0]["name"], "아메리카노")

    @async_test
    async def test_crawl_hours_success(self):
        """영업시간 크롤링 함수가 성공적으로 데이터를 반환하는지 테스트합니다."""
        self.mock_crawl.return_value = {"data": {"llm_extraction": {"holidays": "매주 일요일"}}}
        result = await crawl_hours(self.client, PLACE_ID, "restaurant")
        self.assertEqual(result["holidays"], "매주 일요일")

    @async_test
    async def test_crawl_congestion_success(self):
        """혼잡도 크롤링 함수가 성공적으로 데이터를 반환하는지 테스트합니다."""
        self.mock_crawl.return_value = {"data": {"llm_extraction": {"realtime_status": "여유"}}}
        result = await crawl_congestion(self.client, PLACE_ID, "restaurant")
        self.assertEqual(result["realtime_status"], "여유")

    @async_test
    @patch('app.services.crawler.unified_crawler.crawl_menu', new_callable=AsyncMock)
    @patch('app.services.crawler.unified_crawler.crawl_hours', new_callable=AsyncMock)
    @patch('app.services.crawler.unified_crawler.crawl_congestion', new_callable=AsyncMock)
    async def test_unified_crawler_success(self, mock_crawl_congestion, mock_crawl_hours, mock_crawl_menu):
        """UnifiedCrawler가 모든 정보를 성공적으로 크롤링하고 통합하는지 테스트합니다."""
        mock_crawl_menu.return_value = [{"name": "아메리카노"}]
        mock_crawl_hours.return_value = {"holidays": "매주 일요일"}
        mock_crawl_congestion.return_value = {"realtime_status": "여유"}
        
        unified_crawler = UnifiedCrawler(self.client)
        result = await unified_crawler.crawl_all(PLACE_ID, "cafe")
        
        self.assertEqual(result["menu"][0]["name"], "아메리카노")
        self.assertEqual(result["hours"]["holidays"], "매주 일요일")
        self.assertEqual(result["congestion"]["realtime_status"], "여유")

if __name__ == '__main__':
    unittest.main()
