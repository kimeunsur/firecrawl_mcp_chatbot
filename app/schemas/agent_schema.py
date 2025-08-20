from pydantic import BaseModel

class AgentQueryRequest(BaseModel):
    """AI 에이전트 질의 요청 스키마"""
    place_id: str
    category: str  # 장소의 카테고리 (e.g., 'restaurant', 'cafe')
    query: str

class AgentQueryResponse(BaseModel):
    """AI 에이전트 질의 응답 스키마"""
    place_id: str
    query: str
    answer: str
