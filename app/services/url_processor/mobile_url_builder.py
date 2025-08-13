from typing import Dict
from app.core.constants import NAVER_CATEGORY_MAP

def generate_mobile_urls(place_id: str, category: str) -> Dict[str, str]:
    """
    placeId와 카테고리를 기반으로 표준화된 네이버 모바일 플레이스 URL들을 생성합니다.

    Args:
        place_id: 네이버 플레이스 ID
        category: 내부 표준 카테고리 (e.g., 'restaurant', 'salon')

    Returns:
        'home', 'menu', 'info' 등 각 세부 페이지의 URL을 담은 딕셔너리
    """
    # 내부 표준 카테고리를 네이버 URL에 사용되는 키워드로 변환
    # NAVER_CATEGORY_MAP의 key-value를 뒤집어서 사용
    naver_url_keyword = next((k for k, v in NAVER_CATEGORY_MAP.items() if v == category), category)

    base_url = f"https://m.place.naver.com/{naver_url_keyword}/{place_id}"

    # 카테고리별로 다른 URL 구조를 가질 수 있음을 고려하여 확장 가능하게 설계
    # 예를 들어, 'hospital'은 'menu' 대신 'directions'가 있을 수 있음
    url_map = {
        "home": f"{base_url}/home",
        "info": f"{base_url}/info",
        "review": f"{base_url}/review/visitor",
    }

    if category in ["restaurant", "cafe"]:
        url_map["menu"] = f"{base_url}/menu"
    
    # 다른 카테고리에 대한 특별한 URL 규칙 추가 가능

    return url_map
