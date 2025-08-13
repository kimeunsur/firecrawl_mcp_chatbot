import re

# 네이버 지도 URL에서 placeId를 추출하기 위한 정규식 패턴
# 1. /entry/place/11571379
# 2. /place/11571379
# 3. ?id=11571379
# 4. /place/11571379/
# 5. /restaurant/11571379
# 6. /hairshop/11571379/review/visitor
NAVER_PLACE_ID_PATTERNS = [
    re.compile(r'/entry/place/(\d+)'),
    re.compile(r'/place/(\d+)'),
    re.compile(r'\?id=(\d+)'),
    re.compile(r'/(?:restaurant|hairshop|cafe)/(\d+)'),
]
