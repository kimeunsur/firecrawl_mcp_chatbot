import os
import aiohttp
from typing import Dict, Any, Optional

class FirecrawlException(Exception):
    """Firecrawl 클라이언트 관련 예외"""
    pass

class FirecrawlClient:
    """
    Firecrawl API를 직접 호출하는 HTTP 클라이언트.
    """
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.firecrawl.dev/v0/scrape"):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY가 .env 파일에 설정되지 않았습니다.")
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def crawl(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        주어진 URL과 파라미터로 Firecrawl 스크랩 API를 비동기적으로 호출합니다.
        """
        payload = {"url": url}
        if params:
            payload.update(params)
            
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(self.base_url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise FirecrawlException(f"API 오류: {response.status} - {error_text}")
                    result = await response.json()
                    # API 응답 형식에 따라 'data' 키를 반환
                    return result.get('data', {})
            except aiohttp.ClientError as e:
                raise FirecrawlException(f"네트워크 오류: {e}") from e
