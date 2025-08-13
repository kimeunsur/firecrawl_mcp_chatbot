from typing import Optional
from .pattern_analyzer import NAVER_PLACE_ID_PATTERNS

def extract_place_id(url_or_id: str) -> Optional[str]:
    """
    주어진 URL 또는 ID 문자열에서 네이버 플레이스 ID를 추출합니다.
    순수한 숫자 형식의 ID도 처리합니다.

    Args:
        url_or_id: 분석할 URL 또는 ID 문자열

    Returns:
        추출된 placeId 문자열 또는 찾지 못한 경우 None
    """
    if not isinstance(url_or_id, str):
        return None

    # 입력값이 순수한 숫자로만 이루어져 있는지 확인
    if url_or_id.isdigit():
        return url_or_id

    # URL에서 정규식으로 placeId 추출 시도
    for pattern in NAVER_PLACE_ID_PATTERNS:
        match = pattern.search(url_or_id)
        if match:
            return match.group(1)
    
    return None