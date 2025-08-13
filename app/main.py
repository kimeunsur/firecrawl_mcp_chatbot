from fastapi import FastAPI
from .api.v1 import agents, places, chat
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="AI Agent Service",
    description="가게 정보를 수집하고 고객 문의에 응답하는 AI 에이전트 API",
    version="1.0.0"
)

# API V1 라우터 포함
app.include_router(places.router, prefix="/api/v1", tags=["Places"])
app.include_router(agents.router, prefix="/api/v1", tags=["AI Agent"])
app.include_router(chat.router, tags=["Chat UI"]) # chat 라우터 추가
app.mount("/static",     StaticFiles(directory=os.path.join("app", "static")), name="static")

@app.get("/", tags=["Root"])
def read_root():
    """API 서버의 루트 경로입니다."""
    return {"message": "AI Agent Service is running."}