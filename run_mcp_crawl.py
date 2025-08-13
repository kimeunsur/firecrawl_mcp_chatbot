import json, os, shutil, subprocess, sys
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def _ensure_path_for_gemini(env: dict) -> None:
    """PATH/PATHEXT에 필요한 값 주입 (Windows 대응)."""
    npm_bin = os.path.join(os.environ.get("APPDATA", ""), "npm")
    paths = env.get("PATH", "")
    if npm_bin and npm_bin not in paths:
        env["PATH"] = npm_bin + os.pathsep + paths

    # PATHEXT에 .CMD가 없다면 추가 (일부 런처/서비스 환경)
    pathext = env.get("PATHEXT", "")
    if ".CMD" not in pathext.upper():
        env["PATHEXT"] = pathext + (";" if pathext else "") + ".COM;.EXE;.BAT;.CMD"

def _resolve_gemini_command() -> list[str]:
    """
    gemini 실행 경로를 해석.
    1) PATH에서 찾기
    2) 고정 경로(APPDATA\\npm\\gemini.cmd) 시도
    3) npx 대체 경로 사용
    """
    exe = shutil.which("gemini")
    if exe:
        return [exe]

    # 직접 경로 지정 (Windows 전역 npm bin)
    appdata = os.environ.get("APPDATA")
    if appdata:
        guess = os.path.join(appdata, "npm", "gemini.cmd")
        if os.path.exists(guess):
            return [guess]

    # 최후의 수단: npx로 실행 (패키지 명시)
    return ["npx", "-y", "@google/gemini-cli"]

def run_mcp_crawl(url: str) -> Optional[dict]:
    """
    Gemini CLI로 firecrawl MCP의 scrape를 호출.
    - shell=False (따옴표 문제 방지)
    - PATH/PATHEXT 보정
    - stdout에서 JSON만 추출 시도
    """
    # ✅ scrape(이름 붙은 인자)로 호출 — crawl(params=...) 아님!
    prompt = f'''firecrawl.scrape(
  url="{url}",
  pageOptions={{"scrollDown": true, "waitFor": 1500, "waitForSelector": "ul[class*='menu_list'] li"}},
  extract={{"type":"json","selectors":[{{"name":"menuItems","selector":"div[class*='menu_list'] li, ul[class*='menu_list'] li",
           "fields":{{"name":".title, .menu_name","price":".price, .amount","description":".desc, .menu_desc",
                     "is_signature":{{"selector":".badge_popular","type":"boolean"}}}}}}]}}
)'''

    env = os.environ.copy()
    _ensure_path_for_gemini(env)

    cmd = _resolve_gemini_command() + [
        "-p", prompt,
        "--allowed-mcp-server-names", "firecrawl"
    ]

    try:
        print("\n[MCP] 실행 명령:", cmd)
        out = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
        stdout = (out.stdout or "").strip()
        if not stdout:
            print("[MCP] 출력이 비었습니다. --debug로 재시도해 보세요.")
            return None

        # Gemini가 안내문/로그를 섞어 출력하는 경우 JSON 시작점부터 파싱
        first_brace = stdout.find("{")
        if first_brace > 0:
            stdout = stdout[first_brace:]

        return json.loads(stdout)
    except subprocess.CalledProcessError as e:
        print("[MCP] 실행 실패")
        print("STDOUT:\n", e.stdout)
        print("STDERR:\n", e.stderr)
        return None
    except json.JSONDecodeError:
        print("[MCP] JSON 파싱 실패. RAW STDOUT:\n", stdout)
        return None

data = run_mcp_crawl("https://m.place.naver.com/restaurant/1690334952/menu")
if data and "data" in data:
    menu = data["data"].get("menuItems")
    print("menuItems:", menu)
else:
    print("크롤링 실패 또는 데이터 없음")
