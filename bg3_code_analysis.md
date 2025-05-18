# Baldur's Gate 3 빌드 생성기 코드 분석

## 프로젝트 개요

이 프로젝트는 Baldur's Gate 3 게임의 캐릭터 빌드(육성 가이드)에 대한 정보를 AI API를 사용하여 수집하고, 이를 한국어로 번역한 후 마크다운 파일로 저장하며 Ghost 블로그에 자동으로 포스팅하는 종합 시스템임.

## 폴더 구조

```
/
├── main.py                     # 메인 프로그램 진입점 (사용자 인터페이스)
├── bg3_auto_wiki_poster.py     # 전체 자동화 프로세스 관리
├── ghost_api.py                # Ghost 블로그 API 직접 구현
├── bg3_builder/                # 주요 기능 모듈 패키지
│   ├── __init__.py             # 패키지 정의
│   ├── build_fetcher.py        # 빌드 정보 수집 및 번역 모듈
│   ├── utils.py                # 유틸리티 함수 모음
│   ├── ghost_uploader.py       # Ghost 블로그 포스팅 기능
│   ├── markdown_inserter.py    # 마크다운 콘텐츠 강화 모듈
│   ├── youtube_fetcher.py      # YouTube 썸네일 검색/삽입 기능
│   └── wiki_image_parser.py    # 위키 이미지 검색/삽입 기능
```

## 핵심 컴포넌트 및 데이터 흐름

### 1. 메인 인터페이스 (main.py)

- 사용자 인터페이스 제공 (메뉴 시스템)
- 프로그램의 진입점 역할
- `bg3_auto_wiki_poster.py`의 기능 호출하여 전체 프로세스 실행
- **주요 기능**: 메뉴 시스템, 사용자 입력 처리, 워크플로우 실행

### 2. 자동화 프로세스 관리 (bg3_auto_wiki_poster.py)

- 전체 워크플로우를 통합 관리하는 핵심 컨트롤러
- `automate_build_guide` 함수가 중심 기능 수행
- **데이터 흐름**:
  1. 빌드 정보 수집 (`build_fetcher.py`)
  2. 한국어 블로그 포스트 생성 (`build_fetcher.py`)
  3. 콘텐츠 강화 (`markdown_inserter.py`)
  4. 이미지 추가 (`wiki_image_parser.py`)
  5. YouTube 썸네일 추가 (`youtube_fetcher.py`)
  6. 마크다운 파일 저장 (`utils.py`)
  7. Ghost 블로그 포스팅 (`ghost_uploader.py`)

### 3. 빌드 정보 수집/번역 (build_fetcher.py)

- AI API를 활용한 정보 수집 및 번역 담당
- **API 연동**:
  - Perplexity API(`sonar-reasoning-pro` 모델) - 빌드 정보 수집
  - Grok API(`grok-3-beta` 모델) - 한국어 번역(기본)
- **주요 함수**:
  - `get_build_info`: 빌드 정보 수집
  - `create_korean_blog_post`: 영어 빌드 정보를 한국어 블로그 포스트로 변환
  - `get_perplexity_response`/`get_grok_response`: API 호출 처리

### 4. 마크다운 콘텐츠 강화 (markdown_inserter.py)

- 기본 번역 콘텐츠를 확장/강화하는 모듈
- **주요 기능**:
  - 빌드 정보 추출 (`extract_build_info`)
  - 요약 카드 생성 (`create_summary_card`)
  - 주문/스킬 분석 (`extract_spells`)
  - 전투 루틴 섹션 자동 생성 (`create_combat_routine`)
  - 최종 마크다운 조합 (`enhance_markdown_content`)

### 5. 이미지 검색/삽입 (wiki_image_parser.py)

- BG3 위키 사이트에서 스킬/아이템 이미지 크롤링
- **주요 기능**:
  - 마크다운 내 스킬/아이템 이름 추출 (`extract_skill_item_names`)
  - 위키 사이트에서 이미지 URL 수집 (`get_image_url_from_wiki`)
  - 마크다운에 이미지 삽입 (`insert_images_to_markdown`)

### 6. YouTube 연동 (youtube_fetcher.py)

- YouTube에서 관련 영상 및 썸네일 검색
- **주요 기능**:
  - YouTube 비디오 검색 (`search_youtube_videos`)
  - 썸네일 URL 획득 (`get_youtube_thumbnail`)
  - 마크다운에 썸네일 추가 (`add_youtube_thumbnail_to_markdown`)

### 7. Ghost 블로그 포스팅 (ghost_uploader.py)

- Ghost 블로그 API를 활용한 자동 포스팅
- **주요 기능**:
  - Ghost API 클래스 구현
  - JWT 토큰 인증 (`_create_jwt_token`)
  - 포스트 생성 및 업로드 (`create_post`, `post_to_ghost_blog`)

### 8. 유틸리티 기능 (utils.py)

- 공통 유틸리티 함수 모음
- **주요 기능**:
  - 환경변수 로드 (`load_env_vars`)
  - 로깅 설정 (`setup_logging`)
  - API 응답 저장 (`save_json_response`)
  - 마크다운 파일 저장 (`save_to_markdown`)
  - 문장 마침표 후 줄바꿈 추가 (`add_newlines_after_sentences`)

## 프롬프트 템플릿 상세

### 1. 빌드 정보 수집 프롬프트 (원문)

```
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
```

### 2. 번역 프롬프트 (원문)

```
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
```

## 코드 실행 흐름

### 메인 워크플로우 (automate_build_guide 함수)

1. **초기화 및 설정**

   - 프로그램 시작 로깅
   - 실행 시간 측정 시작

2. **빌드 정보 수집 단계**

   - `build_fetcher.py`의 `get_build_info` 함수 호출
   - Perplexity API를 통해 영문 빌드 정보 수집

3. **번역 단계**

   - `build_fetcher.py`의 `create_korean_blog_post` 함수 호출
   - Grok API (기본) 또는 Perplexity API (대체)를 통해 한국어 블로그 포스트 생성

4. **콘텐츠 강화 단계**

   - `markdown_inserter.py`의 `enhance_markdown_content` 함수 호출
   - 요약 카드, 전투 루틴 등 추가

5. **이미지 추가 단계**

   - `wiki_image_parser.py`의 `insert_images_to_markdown` 함수 호출
   - 위키 이미지 검색 및 삽입

6. **YouTube 썸네일 추가 단계**

   - `youtube_fetcher.py`의 `add_youtube_thumbnail_to_markdown` 함수 호출
   - 관련 YouTube 영상 검색 및 썸네일 삽입

7. **마크다운 저장 단계**

   - `utils.py`의 `save_to_markdown` 함수 호출
   - 생성된 최종 마크다운을 파일로 저장

8. **블로그 포스팅 단계 (선택적)**

   - `ghost_uploader.py`의 `post_to_ghost_blog` 함수 호출
   - Ghost 블로그에 자동으로 포스팅

9. **완료 및 결과 반환**
   - 실행 시간 측정 및 로깅
   - 성공 메시지와 함께 결과 반환

## 의존성 및 API 연동

1. **외부 라이브러리**

   - `requests`: HTTP 요청 처리
   - `beautifulsoup4`: HTML 파싱
   - `pyjwt`: JWT 토큰 생성 (Ghost API 인증)
   - `python-dotenv`: 환경변수 로드

2. **API 의존성**

   - **Perplexity API** (`sonar-reasoning-pro` 모델)

     - 엔드포인트: `https://api.perplexity.ai/chat/completions`
     - 용도: 빌드 정보 수집 및 보조 번역

   - **Grok API** (`grok-3-beta` 모델)

     - 엔드포인트: `https://api.x.ai/v1/chat/completions`
     - 용도: 한국어 번역 (주요)

   - **Ghost 블로그 API**
     - 인증 방식: JWT 토큰
     - 용도: 블로그 포스팅

3. **웹 크롤링**
   - BG3 위키 (`https://bg3.wiki/wiki/`) - 이미지 검색
   - YouTube - 관련 영상 및 썸네일 검색

## 에러 처리 및 로깅

- 모든 모듈에서 `utils.py`의 로거를 사용
- API 호출 실패 시 대체 방법 시도 (Grok API → Perplexity API)
- 이미지/썸네일 검색 실패 시 다양한 대체 전략 구현
- 자세한 에러 로깅 (API 응답 코드, 응답 내용 등)

## 확장성 및 모듈화

- 모듈식 설계로 각 기능 분리
- 패키지 구조로 코드 구성
- 테스트 모드 지원 (API 호출 없이 테스트)
- 커맨드 라인 인터페이스 지원

## 출력 결과

1. **마크다운 파일**

   - 이름 형식: `bg3_{빌드명}_{접미사}_{날짜}.md`
   - 예: `bg3_storm_sorcerer_build_20240504.md`

2. **Ghost 블로그 포스팅**

   - 타입: 드래프트 (자동)
   - 태그: BG3, 공략, 빌드, {빌드명} 등

3. **JSON 로그 파일**
   - API 응답을 타임스탬프와 함께 저장
   - 디버깅 및 분석용
