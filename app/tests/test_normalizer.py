import unittest
from app.services.normalizer.data_normalizer import DataNormalizer

class TestDataNormalizer(unittest.TestCase):

    def setUp(self):
        self.normalizer = DataNormalizer()

    def test_normalize_menu(self):
        """메뉴 데이터가 성공적으로 정규화되는지 테스트합니다."""
        raw_data = [
            {"name": "아메리카노", "price": "4,500원", "description": "고소한 원두"},
            {"name": "카페라떼", "price": "5000원"},
            {"name": "카푸치노", "price": "5,000", "is_signature": True},
            {"name": "가격 정보 없음"},
            {}, # 비어 있는 데이터
            None, # None 데이터
        ]
        
        normalized_menu = self.normalizer.normalize_menu(raw_data)

        self.assertEqual(len(normalized_menu), 4)
        
        # 첫 번째 메뉴 검증
        self.assertEqual(normalized_menu[0].name, "아메리카노")
        self.assertEqual(normalized_menu[0].price, "4500")
        self.assertEqual(normalized_menu[0].description, "고소한 원두")
        self.assertFalse(normalized_menu[0].is_signature)

        # 두 번째 메뉴 검증
        self.assertEqual(normalized_menu[1].name, "카페라떼")
        self.assertEqual(normalized_menu[1].price, "5000")

        # 세 번째 메뉴 검증 (대표 메뉴)
        self.assertEqual(normalized_menu[2].name, "카푸치노")
        self.assertTrue(normalized_menu[2].is_signature)

        # 네 번째 메뉴 검증 (가격 없음)
        self.assertEqual(normalized_menu[3].name, "가격 정보 없음")
        self.assertEqual(normalized_menu[3].price, "0")

    def test_normalize_menu_with_empty_input(self):
        """비어 있거나 None인 입력에 대해 빈 리스트를 반환하는지 테스트합니다."""
        self.assertEqual(self.normalizer.normalize_menu([]), [])
        self.assertEqual(self.normalizer.normalize_menu(None), [])

if __name__ == '__main__':
    unittest.main(verbosity=2)
