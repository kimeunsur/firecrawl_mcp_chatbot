from typing import Dict, Any, Optional

from .placeid_extractor import extract_place_id
from .category_mapper import get_category
from .mobile_url_builder import generate_mobile_urls

class URLProcessor:
    """
    URL 및 관련 입력을 처리하기 위한 통합 인터페이스
    """
    def process(self, url_or_id: str, metadata: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        입력된 URL 또는 ID를 처리하여 placeId, category, mobile_urls를 반환합니다.

        Args:
            url_or_id: 처리할 URL 또는 placeId 문자열
            metadata: 카테고리 결정에 사용될 수 있는 추가 메타데이터

        Returns:
            처리 결과를 담은 딕셔너리. 실패 시 None.
            {
                "place_id": str,
                "category": str,
                "mobile_urls": { ... }
            }
        """
        # 1. placeId 추출
        place_id = extract_place_id(url_or_id)
        if not place_id:
            return None

        # 2. 카테고리 결정
        # url_or_id가 순수 ID일 경우, URL 정보가 없으므로 기본 카테고리를 사용하게 됨
        category = get_category(url_or_id, metadata)

        # 3. 모바일 URL 생성
        mobile_urls = generate_mobile_urls(place_id, category)

        return {
            "place_id": place_id,
            "category": category,
            "mobile_urls": mobile_urls,
        }

# 싱글턴 인스턴스 생성
url_processor = URLProcessor()
