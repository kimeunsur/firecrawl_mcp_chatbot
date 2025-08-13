from typing import Optional
from app.core.constants import NAVER_CATEGORY_MAP, DEFAULT_CATEGORY

def map_category_from_url(url: str) -> str:
    """
    URL에서 키워드를 찾아 내부 표준 카테고리로 매핑합니다.

    Args:
        url: 분석할 URL 문자열

    Returns:
        매핑된 표준 카테고리 문자열. 매핑되는 키워드가 없으면 기본값을 반환합니다.
    """
    if not isinstance(url, str):
        return DEFAULT_CATEGORY

    for keyword, category in NAVER_CATEGORY_MAP.items():
        if f"/{keyword}/" in url:
            return category
            
    return DEFAULT_CATEGORY

def get_category(url: str, metadata: Optional[dict] = None) -> str:
    """
    URL과 메타데이터를 기반으로 장소의 카테고리를 결정합니다.
    (현재는 URL 기반으로만 동작)

    Args:
        url: 분석할 URL 문자열
        metadata: 추가적인 메타데이터 (미사용)

    Returns:
        결정된 표준 카테고리 문자열
    """
    # 1. URL에서 카테고리 추론
    category = map_category_from_url(url)
    
    # 2. 메타데이터에서 카테고리 추론 (향후 확장)
    if metadata:
        pass # metadata를 활용한 로직 추가 가능

    return category
