import re
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.place import Place, PopularTimeNow

class CongestionPredictor:
    """
    크롤링된 데이터로부터 혼잡도를 추출하거나, 정보가 없을 경우 추론합니다.
    """

    def extract_from_content(self, content: str) -> Optional[PopularTimeNow]:
        """
        네이버에서 제공하는 실제 혼잡도 텍스트를 content에서 추출합니다.
        """
        if not content:
            return None

        keywords = {
            '여유': 25,
            '보통': 50,
            '혼잡': 80,
            '붐빔': 90
        }

        # **실시간 인기 토픽** 또는 유사한 섹션에서 혼잡도 키워드 검색
        popularity_section_match = re.search(r'\*\*실시간 인기 토픽\*\*(.*?)(?=\*\*|$)', content, re.DOTALL)
        search_area = popularity_section_match.group(1) if popularity_section_match else content

        for label, score in keywords.items():
            if label in search_area:
                return PopularTimeNow(
                    label=label,
                    score=score,
                    source='naver',
                    confidence=0.9
                )
        
        return None

    def infer_popularity(self, place_data: Place, current_time: Optional[datetime] = None) -> PopularTimeNow:
        """
        업종, 요일, 시간대 등 가용한 정보를 바탕으로 혼잡도를 추론합니다.
        """
        if not current_time:
            current_time = datetime.now()

        # 업종 확인
        categories = place_data.profile.category
        is_restaurant = any('음식' in cat for cat in categories)
        
        # 요일 및 시간
        weekday = current_time.weekday()  # 0=월요일, 6=일요일
        hour = current_time.hour
        
        prior_score = 30  # 기본값

        if is_restaurant:
            if 12 <= hour < 14: # 점심 피크
                prior_score = 80
            elif 18 <= hour < 21: # 저녁 피크
                prior_score = 75
            else:
                prior_score = 40
        
        # TODO: 다른 업종(미용실 등)에 대한 추론 로직 추가

        # 내부 신호 보정 (현재는 기본값 사용)
        signal_score = 50
        final_score = int(0.6 * prior_score + 0.4 * signal_score)

        # 점수에 따른 라벨 매핑
        if final_score < 30:
            label = '여유'
        elif final_score < 60:
            label = '보통'
        elif final_score < 85:
            label = '혼잡'
        else:
            label = '붐빔'

        return PopularTimeNow(
            label=label,
            score=final_score,
            source='inference',
            confidence=0.5
        )

    def predict(self, content: str, place_data: Place) -> PopularTimeNow:
        """
        메인 예측 함수. 실제 데이터 추출을 먼저 시도하고, 실패 시 추론을 실행합니다.
        """
        extracted = self.extract_from_content(content)
        if extracted:
            return extracted
        
        return self.infer_popularity(place_data)
