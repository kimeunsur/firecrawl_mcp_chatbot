import unittest
from app.services.url_processor.placeid_extractor import extract_place_id
from app.services.url_processor.category_mapper import get_category
from app.services.url_processor.mobile_url_builder import generate_mobile_urls
from app.services.url_processor import url_processor # 통합 클래스 import

# 통일된 place_id
PLACE_ID = "1690334952"

class TestUrlProcessor(unittest.TestCase):

    def test_extract_place_id_from_various_urls(self):
        """다양한 네이버 지도 URL 형식에서 placeId가 정확히 추출되는지 테스트합니다."""
        urls_to_test = {
            f"https://map.naver.com/v5/entry/place/{PLACE_ID}?c=15,0,0,0,dh": PLACE_ID,
            f"https://m.place.naver.com/restaurant/{PLACE_ID}/home": PLACE_ID,
        }
        for url, expected_id in urls_to_test.items():
            with self.subTest(url=url):
                self.assertEqual(extract_place_id(url), expected_id)

    def test_extract_place_id_from_direct_id_string(self):
        """순수한 ID 문자열이 입력되었을 때 ID를 정확히 반환하는지 테스트합니다."""
        self.assertEqual(extract_place_id(PLACE_ID), PLACE_ID)

    def test_extract_place_id_with_invalid_inputs(self):
        """placeId가 없는 URL이나 잘못된 입력에 대해 None을 반환하는지 테스트합니다."""
        invalid_inputs = ["https://www.naver.com", "not a url", 12345]
        for url in invalid_inputs:
            with self.subTest(url=url):
                self.assertIsNone(extract_place_id(url))

    def test_get_category_from_url(self):
        """URL에 포함된 키워드를 기반으로 카테고리가 정확히 매핑되는지 테스트합니다."""
        urls_to_test = {
            f"https://m.place.naver.com/restaurant/{PLACE_ID}/home": "restaurant",
            f"https://m.place.naver.com/hairshop/{PLACE_ID}/home": "salon",
        }
        for url, expected_category in urls_to_test.items():
            with self.subTest(url=url):
                self.assertEqual(get_category(url), expected_category)

    def test_get_category_with_no_keyword(self):
        """URL에 카테고리 키워드가 없을 때 기본 카테고리를 반환하는지 테스트합니다."""
        url = f"https://map.naver.com/v5/entry/place/{PLACE_ID}"
        self.assertEqual(get_category(url), "restaurant")

    def test_generate_mobile_urls(self):
        """placeId와 카테고리로 모바일 URL이 정확히 생성되는지 테스트합니다."""
        # 식당 카테고리 테스트
        urls = generate_mobile_urls(PLACE_ID, "restaurant")
        self.assertEqual(urls["home"], f"https://m.place.naver.com/restaurant/{PLACE_ID}/home")
        self.assertIn("menu", urls)

        # 미용실 카테고리 테스트
        urls = generate_mobile_urls(PLACE_ID, "salon")
        self.assertEqual(urls["home"], f"https://m.place.naver.com/hairshop/{PLACE_ID}/home")
        self.assertNotIn("menu", urls)

    def test_url_processor_end_to_end(self):
        """URLProcessor 통합 클래스의 전체 처리 과정을 테스트합니다."""
        url = f"https://m.place.naver.com/restaurant/{PLACE_ID}/home"
        result = url_processor.process(url)

        self.assertIsNotNone(result)
        self.assertEqual(result["place_id"], PLACE_ID)
        self.assertEqual(result["category"], "restaurant")
        self.assertEqual(result["mobile_urls"]["home"], f"https://m.place.naver.com/restaurant/{PLACE_ID}/home")

    def test_url_processor_with_direct_id(self):
        """URLProcessor가 순수 ID 입력도 올바르게 처리하는지 테스트합니다."""
        result = url_processor.process(PLACE_ID)

        self.assertIsNotNone(result)
        self.assertEqual(result["place_id"], PLACE_ID)
        self.assertEqual(result["category"], "restaurant")
        self.assertEqual(result["mobile_urls"]["home"], f"https://m.place.naver.com/restaurant/{PLACE_ID}/home")

    def test_url_processor_with_invalid_input(self):
        """URLProcessor가 잘못된 입력에 대해 None을 반환하는지 테스트합니다."""
        self.assertIsNone(url_processor.process("invalid_input"))

if __name__ == '__main__':
    unittest.main()