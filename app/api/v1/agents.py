from fastapi import APIRouter, Depends, HTTPException
from ...schemas.agent_schema import AgentQueryRequest, AgentQueryResponse
from ...services.agent.graph import agent # LangGraph 에이전트 인스턴스 임포트

router = APIRouter()

@router.post("/agent/query", response_model=AgentQueryResponse)
def query_agent(
    request: AgentQueryRequest
):
    """
    사용자의 질문에 대해 LangGraph AI 에이전트가 답변을 생성합니다.
    """
    try:
        # LangGraph 에이전트 실행
        answer = agent.run(
            place_id=request.place_id,
            query=request.query
        )
        return AgentQueryResponse(
            place_id=request.place_id,
            query=request.query,
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"에이전트 실행 중 오류 발생: {e}")