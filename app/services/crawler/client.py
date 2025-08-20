import os
import aiohttp
from typing import Dict, Any, Optional

class FirecrawlException(Exception):
    """Firecrawl 클라이언트 관련 예외"""
    pass

class FirecrawlClient:

    BASE_URL = "https://api.firecrawl.dev"
    LLMSTXT_PATH = "/llmstxt"
    
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

    async def scrape_url(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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

    async def search(self, query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        주어진 쿼리로 Firecrawl 검색 API를 비동기적으로 호출합니다.
        """
        search_url = "https://api.firecrawl.dev/v0/search"
        payload = {"query": query}
        if params:
            payload.update(params)
            
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(search_url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise FirecrawlException(f"API 오류: {response.status} - {error_text}")
                    result = await response.json()
                    return result.get('data', {})
            except aiohttp.ClientError as e:
                raise FirecrawlException(f"네트워크 오류: {e}") from e

    async def generate_llms_txt(self, url: str, params: Optional[Dict[str, Any]] = None, output_dir: str = "app/results/txt") -> Dict[str, Any]:
        """
        주어진 URL로 Firecrawl llms.txt 생성 API를 비동기적으로 호출하고,
        결과를 파일로 저장합니다.
        """
        llms_txt_url = "https://api.firecrawl.dev/v0/llmstxt"
        payload = {"url": url}
        if params:
            payload.update(params)

        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(llms_txt_url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise FirecrawlException(f"API 오류: {response.status} - {error_text}")
                    
                    result = await response.json()
                    data = result.get('data', {})

                    if data:
                        # 디렉토리가 없으면 생성
                        os.makedirs(output_dir, exist_ok=True)

                        # llms.txt 파일 저장
                        llms_txt_content = data.get("llms.txt")
                        if llms_txt_content:
                            with open(os.path.join(output_dir, "llms.txt"), "w", encoding="utf-8") as f:
                                f.write(llms_txt_content)
                            print(f"'llms.txt' 파일이 {output_dir}에 저장되었습니다.")

                        # llms-full.txt 파일 저장
                        llms_full_txt_content = data.get("llms-full.txt")
                        if llms_full_txt_content:
                            with open(os.path.join(output_dir, "llms-full.txt"), "w", encoding="utf-8") as f:
                                f.write(llms_full_txt_content)
                            print(f"'llms-full.txt' 파일이 {output_dir}에 저장되었습니다.")
                    
                    return data
            except aiohttp.ClientError as e:
                raise FirecrawlException(f"네트워크 오류: {e}") from e
