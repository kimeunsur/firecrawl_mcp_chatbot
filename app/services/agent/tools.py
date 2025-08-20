import subprocess
import json
import os
import shutil
import re
from langchain_core.tools import tool
from ...db.connection import get_database
from ...db.repositories.place_repository import PlaceRepository
from ..url_processor.mobile_url_builder import generate_mobile_urls

def _resolve_gemini_command() -> list[str]:
    """
    gemini 실행 경로를 해석.
    1) PATH에서 찾기
    2) 고정 경로(APPDATA\npm\gemini.cmd) 시도
    3) npx 대체 경로 사용
    """
    exe = shutil.which("gemini")
    if exe:
        return [exe]
    appdata = os.environ.get("APPDATA")
    if appdata:
        guess = os.path.join(appdata, "npm", "gemini.cmd")
        if os.path.exists(guess):
            return [guess]
    return ["npx", "-y", "@google/gemini-cli"]

@tool
def get_place_information(place_id: str) -> dict:
    """
    주어진 place_id에 해당하는 장소의 모든 정보를 데이터베이스에서 조회합니다.
    """
    try:
        db = get_database()
        repo = PlaceRepository(db)
        place_data = repo.get_by_id(place_id)
        
        if not place_data:
            return {"error": "해당 ID의 장소를 찾을 수 없습니다."}
        
        if '_id' in place_data:
            place_data['_id'] = str(place_data['_id'])
            
        return place_data
    except Exception as e:
        return {"error": f"데이터베이스 조회 중 오류 발생: {e}"}

@tool
def generate_llms_txt_for_place(place_id: str, category: str) -> dict:
    """
    주어진 place_id와 category로 네이버 모바일 지도 페이지를 크롤링하여 llms.txt를 생성하고,
    그 내용을 app/results/txt/{place_id}.txt 파일로 저장합니다.
    """
    try:
        urls = generate_mobile_urls(place_id, category)
        home_url = urls.get("home")
        if not home_url:
            return {"error": "해당 장소의 홈 URL을 생성할 수 없습니다."}

        prompt = f'firecrawl.generate_llmstxt(url="{home_url}", showFullText=True)'
        
        env = os.environ.copy()
        # -p 플래그를 제거하고, prompt를 stdin으로 전달하도록 변경
        cmd = _resolve_gemini_command() + [
            "--allowed-mcp-server-names", "firecrawl"
        ]

        print(f"Executing command: {" ".join(cmd)}")
        print(f"With stdin: {prompt}")
        
        # prompt를 'input' 인자로 전달
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
        
        stdout = result.stdout.strip()
        
        llms_txt_match = re.search(r'-- llms\.txt --\s*```\s*(.*?)\s*```', stdout, re.DOTALL)
        llms_full_txt_match = re.search(r'-- llms-full\.txt --\s*```\s*(.*?)\s*```', stdout, re.DOTALL)

        llms_txt_content = llms_txt_match.group(1).strip() if llms_txt_match else ""
        llms_full_txt_content = llms_full_txt_match.group(1).strip() if llms_full_txt_match else ""

        if not llms_txt_content and not llms_full_txt_content:
            return {"error": f"llms.txt 내용을 추출하지 못했습니다. 원본 출력: {stdout}"}

        full_content = f"-- llms.txt --\n{llms_txt_content}\n\n-- llms-full.txt --\n{llms_full_txt_content}"
        
        output_dir = os.path.join("app", "results", "txt")
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = os.path.join(output_dir, f"{place_id}.txt")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_content)
            
        return {
            "status": "success",
            "message": f"llms.txt 파일이 '{file_path}' 경로에 성공적으로 저장되었습니다.",
            "content": full_content
        }

    except subprocess.CalledProcessError as e:
        print("---" + " Subprocess Error" + "---")
        print(f"Exit Code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        print("------------------------")
        return {"error": f"llms.txt 생성 실패. STDERR: {e.stderr}"}
    except Exception as e:
        return {"error": f"llms.txt 생성 또는 저장 중 오류 발생: {e}"}