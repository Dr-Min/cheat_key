import requests
import time
import json
from .utils import logger, save_json_response, env_vars

# API 키 설정
PERPLEXITY_API_KEY = env_vars.get('PERPLEXITY_API_KEY')
GROK_API_KEY = env_vars.get('GROK_API_KEY')

# API 엔드포인트
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# 빌드 정보 수집 기본 프롬프트 템플릿
BUILD_INFO_PROMPT_TEMPLATE = """
Search across Reddit, YouTube, Fextralife wiki, Steam discussions, and expert-written build guides to find the most highly rated and popular {build_name} build in Baldur's Gate 3 as of the latest patch.

Return a **single, unified build** that is actually used and recommended in the community. Include:

1. Exact stat allocation at character creation (STR / DEX / CON / INT / WIS / CHA)
2. Recommended race and background with reasons
3. Spells to pick at each level from 1 to 12
4. Suggested subclass and multiclassing path (if any), with pros and cons
5. Best gear per Act (1–3), including weapons, armor, and accessories
6. Combo strategies, tactical tips, and overall gameplay style
7. The specific patch or game version this build is based on

If a Korean translation exists for spell or item names in the Korean version of Baldur's Gate 3, include that in parentheses.

+ If any gear (e.g. weapons, armor, accessories) is mentioned, include the original English name in parentheses immediately after the Korean name (e.g. "아다만틴 판금갑옷 (Adamantine Splint Armor)").

**Important**: Only return one fully-formed and coherent build. Do not mix different sources if they contradict each other. Avoid hallucinating or filling in gaps — only include details verified by actual guides.
"""

# 번역 프롬프트 템플릿
TRANSLATION_PROMPT_TEMPLATE = """
다음은 Baldur's Gate 3의 {build_name} 빌드에 대한 영어 공략 정보입니다. 이 내용을 기반으로 블로그용 한국어 공략글을 작성해주세요.

위 내용을 한국어 Baldur's Gate 3 유저들이 실제로 보기 편하게 다음과 같이 다시 써줘:

- 스펠, 장비, 특성 이름은 공식 한국어 번역 또는 유저들이 흔히 쓰는 번역으로 바꿔줘
- 번개/마법사 관련 용어는 위키식이 아닌 유저 중심의 표현으로 자연스럽게 표현
- 표보다는 제목 + 리스트로 가독성 높게
- 문체는 초보도 이해할 수 있게 하지만 음슴체를 사용 할 것. 문체는 아래 문체 칸에서 보고 참고할것.
- 영어 용어는 꼭 병기하지 않아도 돼 (필요할 경우만 괄호로)
- 중복되는 정보는 줄이고, 팁과 전략 중심으로 요약 정리해줘

조건:
- 스탯 분배를 정확한 숫자로
- 추천 종족과 배경, 그 이유 포함
- 레벨별 스펠 선택을 구체적으로 정리
- 멀티클래스가 있다면 조합 방식과 장단점
- 각 Act(1~3)별 추천 장비
- 전투 전략 및 콤보 팁
- 기반이 된 패치/버전 명시
- 절대 거짓 정보 넣지 말고, 영어 원문에 없는 내용 창작하지 말 것

형식:
- 서두에 이 빌드가 어떤 출처(Reddit, Fextralife, YouTube 등)를 기반으로 작성된 것인지 명시해주세요.
- 마크다운 블로그 스타일
- 제목 포함
- 각 섹션은 ##, ### 등의 헤딩으로 구분
- 유치하지 않은 말투로 정보는 전문가 수준으로 정확하게
- 너무 요약하지 말고 충분히 자세히 적어야 함
- 모든 문장을 마침표 기준으로 줄바꿈 해줘. 하지만 문단 구조는 유지하고 마크다운 문법이나 링크, 이미지 태그는 깨지 않게 해줘.
- 가독성 좋게 문단을 자주 나눠.

문체 무조건 반영할것:
알겠음 맞겠음 생각해봐야겠음 따져봐야겠음. 이런 문장은 알듯 맞을듯 생각해봐야할듯 따져봐야할듯 이런식으로 적어 
                     절대 할루시네이션을 일으키면 안돼

# 아래는 참고할 문체 예시임 (단어 말고 문체를 따라하셈):
스토리는 정말 잘 만든 중세 판타지 소설을 읽는 느낌이 들었음.
스토리 모르고 클리어하는 건 개인적으로 굉장한 손해라고 봄.
돈가스 정식 시키고 미니 우동은 남기고 가는 거임.
돈 내고 산 거니깐 미니 우동도 싹 비우고 가셈.
아무튼 간접적으로 스토리를 전해 듣기에 나 같은 킹반인 유저들은 게임 내에서 스토리를 구체적으로 알게 되는 것은 상당히 어렵다. (사실 불가능하다.)
그럼에도 불구하고 이 게임의 스토리는 직접 찾아서 읽어볼 만함.
하지만 이정도면 괜찮은듯

원문 정보:
{build_info}
"""

def get_perplexity_response(prompt, model="sonar-reasoning-pro"):
    """Perplexity API를 사용하여 응답 가져오기"""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}"
    }
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        logger.info(f"Perplexity API 요청 중... (모델: {model})")
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # 원본 응답 데이터를 로그 파일에 저장
        save_json_response(result, "perplexity_raw_response")
        
        content = result["choices"][0]["message"]["content"]
        logger.info("Perplexity API 응답 성공")
        return content
    except requests.RequestException as e:
        logger.error(f"Perplexity API 오류: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"응답 코드: {e.response.status_code}")
            logger.error(f"응답 내용: {e.response.text}")
        return None

def get_grok_response(prompt):
    """Grok API를 사용하여 응답 가져오기"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROK_API_KEY}"
    }
    
    data = {
        "model": "grok-3-beta",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 4000
    }
    
    try:
        logger.info("Grok API 요청 중...")
        response = requests.post(GROK_API_URL, headers=headers, json=data, timeout=180)  # 3분 타임아웃
        response.raise_for_status()
        
        result = response.json()
        
        # 원본 응답 데이터를 로그 파일에 저장
        save_json_response(result, "grok_raw_response")
        
        # 디버깅 정보
        logger.info(f"Grok API 응답 상태 코드: {response.status_code}")
        logger.info(f"Grok API 응답 구조 키: {list(result.keys())}")
        
        # 응답에서 content 추출 시도
        if "choices" in result and len(result["choices"]) > 0:
            if "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
                return result["choices"][0]["message"]["content"]
        
        logger.error(f"응답 구조를 찾지 못했습니다. 전체 응답: {json.dumps(result, indent=2)}")
        return None
    except requests.RequestException as e:
        logger.error(f"Grok API 호출 중 오류 발생: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"응답 코드: {e.response.status_code}")
            logger.error(f"응답 내용: {e.response.text}")
        return None

def get_build_info(build_name):
    """특정 빌드 정보 수집"""
    logger.info(f"Perplexity API를 통해 {build_name} 빌드 정보 수집 중...")
    
    # 빌드명을 프롬프트에 삽입
    build_prompt = BUILD_INFO_PROMPT_TEMPLATE.format(build_name=build_name)
    
    build_info = get_perplexity_response(build_prompt)
    
    if build_info:
        logger.info("빌드 정보 성공적으로 수집 완료!")
        return build_info
    else:
        logger.error("빌드 정보 수집 실패.")
        return None

def create_korean_blog_post(build_info, build_name):
    """영어 빌드 정보를 한국어 블로그 포스트로 변환"""
    logger.info(f"Grok API를 통해 {build_name} 한국어 블로그 포스트 생성 중...")
    
    # 빌드명을 프롬프트에 삽입
    translation_prompt = TRANSLATION_PROMPT_TEMPLATE.format(
        build_name=build_name,
        build_info=build_info
    )
    
    # 먼저 Grok API를 시도
    logger.info("Grok API로 한국어 번역 시도...")
    korean_blog_post = get_grok_response(translation_prompt)
    
    # Grok API 실패 시 Perplexity API로 대체
    if not korean_blog_post:
        logger.warning("Grok API 실패, Perplexity API로 대체...")
        korean_blog_post = get_perplexity_response(translation_prompt)
    
    if korean_blog_post:
        logger.info("한국어 블로그 포스트 생성 완료!")
        return korean_blog_post
    else:
        logger.error("한국어 블로그 포스트 생성 실패.")
        return None 