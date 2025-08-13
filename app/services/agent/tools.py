from langchain_core.tools import tool
from ...db.connection import get_database
from ...db.repositories.place_repository import PlaceRepository

@tool
def get_place_information(place_id: str) -> dict:
    """
    주어진 place_id에 해당하는 장소의 모든 정보를 데이터베이스에서 조회합니다.
    메뉴, 영업시간, 혼잡도 등 AI 에이전트가 답변에 필요한 모든 데이터를 포함합니다.
    """
    try:
        db = get_database()
        repo = PlaceRepository(db)
        place_data = repo.get_by_id(place_id)
        
        if not place_data:
            return {"error": "해당 ID의 장소를 찾을 수 없습니다."}
        
        # MongoDB의 ObjectId를 문자열로 변환
        if '_id' in place_data:
            place_data['_id'] = str(place_data['_id'])
            
        return place_data
    except Exception as e:
        return {"error": f"데이터베이스 조회 중 오류 발생: {e}"}
