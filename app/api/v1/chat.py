from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# app/templates 디렉토리를 템플릿 폴더로 설정
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/chat", response_class=HTMLResponse)
async def read_chat(request: Request):
    """
    chat.html 템플릿을 렌더링하여 챗봇 UI 페이지를 반환합니다.
    """
    return templates.TemplateResponse("chat.html", {"request": request})
