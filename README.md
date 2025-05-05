# 🎮 발더스 게이트 3 (BG3) 빌드 가이드 자동 생성기

발더스 게이트 3(Baldur's Gate 3)의 빌드 가이드를 자동으로 생성하고 블로그에 포스팅하는 도구입니다.

![BG3 헤더 이미지](https://i.namu.wiki/i/IxWGCIu4G78HZv1d2AU_C5taEO8i-iT_aEbh5YbPAz73yIS3gFGB-Fj6EvL4Z-jmjcFIvWhr2XOxN0-sdmH31g.webp)

## 📋 주요 기능

- **빌드 정보 자동 수집**: Perplexity API를 사용하여 영어로 된 빌드 정보를 수집합니다.
- **한글 번역 및 가이드 작성**: Grok API를 사용하여 한국어로 번역하고 가이드를 작성합니다.
- **이미지 향상**: BG3 위키에서 관련 스킬/아이템 이미지를 자동으로 추가합니다.
- **YouTube 썸네일**: 관련 YouTube 영상의 썸네일을 가이드에 추가합니다.
- **콘텐츠 강화**: 빌드 요약 카드와 전투 루틴 템플릿을 자동으로 생성합니다.
- **Ghost 블로그 포스팅**: JWT 인증 방식으로 Ghost 블로그에 자동 포스팅합니다.

## 🛠️ 설치 방법

1. 요구사항:

   - Python 3.8 이상
   - pip (Python 패키지 관리자)

2. 저장소 클론:

   ```bash
   git clone https://github.com/yourusername/bg3-build-guide-generator.git
   cd bg3-build-guide-generator
   ```

3. 필요한 패키지 설치:

   ```bash
   pip install -r requirements.txt
   ```

4. API 키 설정:
   - `bg3_builder/build_fetcher.py` 파일에서 Perplexity와 Grok API 키를 설정하세요.
   - `bg3_builder/ghost_uploader.py` 파일에서 Ghost 블로그 API 키를 설정하세요.

## 📝 사용 방법

1. 메인 스크립트 실행:

   ```bash
   python main.py
   ```

2. 메뉴에서 원하는 옵션 선택:

   - 1: 빌드 가이드 생성 (블로그 포스팅 포함)
   - 2: 빌드 가이드 생성 (블로그 포스팅 없이)
   - 3: 테스트 모드 (API 호출 없음)
   - 4: 프로그램 정보
   - 0: 종료

3. 빌드 이름 입력:

   - 원하는 빌드 이름을 입력하세요. (예: "Storm Sorcerer", "투척바바", "검바드")

4. 결과 확인:
   - 마크다운 파일이 생성됩니다.
   - 블로그 포스팅을 선택한 경우, Ghost 블로그에 자동으로 게시됩니다.

## 💻 명령줄 옵션

`bg3_auto_wiki_poster.py` 스크립트는 다음 명령줄 옵션을 지원합니다:

```bash
python bg3_auto_wiki_poster.py --build "Storm Sorcerer" --output-dir "./output" --debug
```

- `--build`: 빌드 이름 (예: "Storm Sorcerer", "투척바바")
- `--output-dir`: 결과 마크다운 저장 디렉토리
- `--no-post`: 블로그 포스팅 건너뛰기
- `--debug`: 디버그 로그 출력
- `--test`: 테스트 모드 (API 호출 없이 더미 데이터 사용)

## 📁 프로젝트 구조

```
bg3-build-guide-generator/
├── bg3_builder/               # 모듈화된 코드
│   ├── __init__.py            # 패키지 정의
│   ├── utils.py               # 공통 유틸리티 함수
│   ├── build_fetcher.py       # API 통신 모듈
│   ├── wiki_image_parser.py   # 이미지 추출/검색 모듈
│   ├── youtube_fetcher.py     # YouTube 썸네일 모듈
│   ├── markdown_inserter.py   # 콘텐츠 강화 모듈
│   └── ghost_uploader.py      # 블로그 포스팅 모듈
├── main.py                    # 메인 진입점
├── bg3_auto_wiki_poster.py    # 주요 실행 스크립트
├── README.md                  # 프로젝트 설명서
└── requirements.txt           # 필요한 패키지 목록
```

## ⚠️ 주의사항

- API 키는 외부에 노출되지 않도록 주의하세요.
- API 사용량에 따라 요금이 발생할 수 있습니다.
- Ghost 블로그 인증 정보를 안전하게 관리하세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 문의

문제나 제안사항이 있으시면 이슈를 등록하거나 다음 이메일로 문의해주세요: your.email@example.com
