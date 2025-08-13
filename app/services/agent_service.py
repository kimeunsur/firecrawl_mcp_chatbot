from ..db.repositories.place_repository import PlaceRepository
from ..models.place import Place

class AgentService:
    def __init__(self, place_repo: PlaceRepository):
        self.place_repo = place_repo

    def generate_response(self, place_id: str, query: str) -> str:
        """
        DB에서 장소 정보를 조회하고, 사용자의 질문에 대한 답변을 생성합니다.
        (초기 버전: 간단한 규칙 기반 응답)
        """
        place_data = self.place_repo.get_by_id(place_id)
        if not place_data:
            return "해당 장소 정보를 찾을 수 없습니다."

        # Pydantic 모델로 변환하여 데이터에 쉽게 접근
        place = Place.parse_obj(place_data)

        if "영업시간" in query or "언제 열어" in query:
            if not place.hours:
                return "죄송합니다, 영업시간 정보가 등록되어 있지 않습니다."
            
            response_lines = ["영업시간 정보입니다:"]
            for h in place.hours:
                day_str = h.day
                time_str = f"{h.open} - {h.close}"
                if h.break_time:
                    time_str += f" (브레이크타임: {h.break_time})")
                response_lines.append(f"- {day_str}: {time_str}")
            return "\n".join(response_lines)

        elif "메뉴" in query or "가격" in query:
            if not place.restaurant or not place.restaurant.menu:
                return "죄송합니다, 메뉴 정보가 등록되어 있지 않습니다."
            
            response_lines = ["메뉴 정보입니다:"]
            for item in place.restaurant.menu:
                price = f"{int(item.price):,}원" # 가격 포맷팅
                response_lines.append(f"- {item.name}: {price}")
            return "\n".join(response_lines)
        
        elif "혼잡" in query or "사람 많아" in query:
            now_popularity = place.popularTimes.now
            if now_popularity.source == 'absent':
                return "죄송합니다, 현재 혼잡도 정보가 없습니다."
            
            return f"현재 혼잡도는 '{now_popularity.label}' 상태입니다. (점수: {now_popularity.score}/100, 출처: {now_popularity.source})"

        else:
            return "죄송합니다, 아직 답변할 수 없는 질문입니다. (영업시간, 메뉴, 혼잡도에 대해 질문해주세요)"
