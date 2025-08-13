from pydantic import BaseModel

class AgentQueryRequest(BaseModel):
    """AI 에이전트 질의 요청 스키마"""
    place_id: str
    query: str

class AgentQueryResponse(BaseModel):
    """AI 에이전트 질의 응답 스키마"""
    place_id: str
    query: str
    answer: str
