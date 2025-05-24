import re
import time
import requests
import urllib.parse
from bs4 import BeautifulSoup
from .utils import logger

# BG3 스킬/주문/아이템 데이터베이스 (정확도 향상을 위한 화이트리스트)
BG3_KNOWN_TERMS = {
    # 주문/스킬
    "spells": {
        "Magic Missile": "마법 화살",
        "Shield": "실드", 
        "Healing Word": "치유의 말",
        "Scorching Ray": "작열하는 광선",
        "Fireball": "화염구",
        "Lightning Bolt": "번개 화살",
        "Counterspell": "주문 반격",
        "Haste": "신속",
        "Misty Step": "안개 발걸음",
        "Thunderwave": "천둥파",
        "Burning Hands": "작열하는 손길",
        "Cure Wounds": "상처 치유",
        "Bless": "축복",
        "Divine Smite": "신성한 강타",
        "Action Surge": "행동 쇄도",
        "Sneak Attack": "은밀 공격",
        "Rage": "분노",
        "Wild Shape": "야생 변신",
        "Eldritch Blast": "엘드리치 블라스트",
        "Hex": "저주",
        "Hunter's Mark": "사냥꾼의 표식"
    },
    # 아이템/장비
    "items": {
        "Shortsword": "숏소드",
        "Longbow": "롱보우",
        "Shortbow": "숏보우", 
        "Studded Leather": "스터디드 레더",
        "Chain Mail": "체인 메일",
        "Scale Mail": "스케일 메일",
        "Plate Armor": "플레이트 아머",
        "Shield": "방패",
        "Helmet": "투구",
        "Gloves": "장갑",
        "Boots": "부츠",
        "Ring": "반지",
        "Amulet": "목걸이",
        "Cloak": "망토"
    },
    # 종족
    "races": {
        "Human": "휴먼",
        "Elf": "엘프",
        "Half-Elf": "하프엘프",
        "Dwarf": "드워프",
        "Halfling": "하플링",
        "Dragonborn": "드래곤본",
        "Tiefling": "티플링",
        "Gnome": "노움",
        "Half-Orc": "하프오크",
        "Githyanki": "기스양키"
    },
    # 클래스/서브클래스
    "classes": {
        "Fighter": "파이터",
        "Wizard": "위저드",
        "Rogue": "로그",
        "Ranger": "레인저",
        "Paladin": "팔라딘",
        "Barbarian": "바바리안",
        "Bard": "바드",
        "Cleric": "클레릭",
        "Druid": "드루이드",
        "Monk": "몽크",
        "Sorcerer": "소서러",
        "Warlock": "워록"
    }
}

# 제외할 일반적인 단어들 (확장된 블랙리스트)
EXCLUDED_WORDS = {
    "general": ["the", "and", "for", "item", "with", "this", "that", "from", "your", "when", "what", "where", 
               "build", "guide", "level", "damage", "attack", "spell", "cast", "turn", "round", "bonus", 
               "action", "reaction", "hit", "miss", "save", "roll", "dice", "modifier", "ability", "score",
               "armor", "class", "points", "health", "weapon", "range", "melee", "target", "enemy", "ally",
               "party", "character", "player", "game", "combat", "battle", "fight", "victory", "defeat"],
    "bg3_generic": ["BG3", "Baldur", "Gate", "Act", "Chapter", "Quest", "NPC", "Companion", "Camp", "Rest",
                   "Long", "Short", "Advantage", "Disadvantage", "Proficiency", "Inspiration", "Tadpole"]
}

def is_valid_bg3_term(term):
    """BG3 관련 유효한 용어인지 검증"""
    # 길이 체크
    if len(term) < 3 or len(term) > 30:
        return False
    
    # 블랙리스트 체크
    term_lower = term.lower()
    for category, words in EXCLUDED_WORDS.items():
        if term_lower in words:
            return False
    
    # 화이트리스트 체크 (확실한 BG3 용어들)
    for category, terms in BG3_KNOWN_TERMS.items():
        if term in terms:
            return True
    
    # 패턴 기반 검증
    # 1. 첫 글자가 대문자이고 나머지는 소문자/공백/하이픈으로 구성
    if re.match(r'^[A-Z][a-z\s\'-]+$', term):
        # 2. 연속된 대문자가 있는 경우 (Magic Missile, Divine Smite 등)
        if re.search(r'[A-Z][a-z]', term):
            return True
    
    # 3. 특수한 형태들 (숫자 포함, +1, +2 등)
    if re.match(r'^[A-Z][a-z\s\'-]*\s*\+?\d*$', term):
        return True
    
    return False

def extract_skill_item_names(content):
    """마크다운 내용에서 스킬과 아이템 이름 추출 (개선된 버전)"""
    logger.info("BG3 스킬/아이템 이름 추출 시작 (개선된 정확도)")
    
    # 개선된 정규식 패턴들 (더 정확한 매칭)
    patterns = [
        # **한글명 (영문명)** 형태 - 가장 정확한 패턴
        (r'\*\*([가-힣\s]+)\s*\(([A-Za-z\s\'\-]+)\)\*\*', "한글명 (영문명)", True),
        # **영문명** 형태 - BG3 용어일 가능성이 높음  
        (r'\*\*([A-Z][A-Za-z\s\'\-]+)\*\*', "강조된 영문명", True),
        # (영문명) 형태 - 괄호 안의 영문명
        (r'\(([A-Z][A-Za-z\s\'\-]+)\)', "괄호 영문명", True),
        # 리스트 항목에서 찾기 - **항목명**: 설명
        (r'[-*]\s*\*\*([A-Z][A-Za-z\s\'\-]+)\*\*\s*[:：]', "리스트 항목", True),
        # 숫자 리스트에서 찾기 - 1. **항목명**: 설명
        (r'\d+\.\s*\*\*([A-Z][A-Za-z\s\'\-]+)\*\*\s*[:：]', "숫자 리스트", True)
    ]
    
    # 결과 저장용 딕셔너리 {영문명: 한글명}
    item_dict = {}
    extraction_stats = {}
    
    for pattern, pattern_name, is_high_confidence in patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        valid_matches = 0
        
        logger.debug(f"{pattern_name} 패턴으로 {len(matches)}개 후보 발견")
        
        if pattern_name == "한글명 (영문명)":
            # (한글명, 영문명) 형태 - 가장 신뢰도 높음
            for korean_name, english_name in matches:
                english_name = english_name.strip()
                korean_name = korean_name.strip()
                
                if is_valid_bg3_term(english_name):
                    item_dict[english_name] = korean_name
                    valid_matches += 1
                    logger.debug(f"✅ 확실한 매칭: {english_name} (한글: {korean_name})")
        
        else:
            # 영문명만 있는 패턴들
            for match in matches:
                if isinstance(match, tuple):
                    english_name = match[0].strip()
                else:
                    english_name = match.strip()
                
                # 이미 추가된 항목이면 건너뛰기
                if english_name in item_dict:
                    continue
                
                # BG3 용어 검증
                if is_valid_bg3_term(english_name):
                    # 고신뢰도 패턴이거나 화이트리스트에 있는 경우만 추가
                    if is_high_confidence or any(english_name in terms for terms in BG3_KNOWN_TERMS.values()):
                        item_dict[english_name] = english_name  # 한글명이 없으면 영문명 그대로
                        valid_matches += 1
                        logger.debug(f"✅ 유효한 용어: {english_name}")
                    else:
                        logger.debug(f"⚠️ 낮은 신뢰도: {english_name}")
        
        extraction_stats[pattern_name] = {"total": len(matches), "valid": valid_matches}
    
    # 추출 결과 통계 로깅
    total_extracted = len(item_dict)
    logger.info(f"스킬/아이템 추출 완료: {total_extracted}개 (검증된 용어만)")
    
    for pattern_name, stats in extraction_stats.items():
        logger.info(f"  - {pattern_name}: {stats['valid']}/{stats['total']} 유효")
    
    # 추출된 용어들 로깅 (디버그용)
    if item_dict:
        logger.info(f"추출된 BG3 용어들: {', '.join(sorted(item_dict.keys()))}")
    
    return item_dict

def get_image_url_from_wiki(item_name, retry_count=0):
    """BG3 위키에서 아이템/스킬 이미지 URL 가져오기 (개선된 검색 로직)"""
    try:
        # 기본 검색 URL 생성
        encoded_name = urllib.parse.quote(item_name.replace(' ', '_'))
        wiki_url = f"https://bg3.wiki/wiki/{encoded_name}"
        
        logger.info(f"위키 검색 [{retry_count + 1}/3]: {wiki_url}")
        
        # User-Agent 헤더 추가 (크롤링 차단 방지)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(wiki_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            logger.warning(f"위키 페이지를 찾을 수 없음: {wiki_url} (코드: {response.status_code})")
            
            # 대체 검색 전략들
            alternative_searches = [
                # 1. 첫 번째 단어만 사용
                item_name.split()[0] if ' ' in item_name else None,
                # 2. 복수형을 단수형으로 (예: Gloves → Glove)
                item_name.rstrip('s') if item_name.endswith('s') and len(item_name) > 4 else None,
                # 3. 일반적인 변형들
                item_name.replace(' ', '_'),
                # 4. 소문자 변형
                item_name.lower()
            ]
            
            for alt_term in alternative_searches:
                if alt_term and alt_term != item_name and retry_count < 2:
                    logger.info(f"대체 검색 시도: {alt_term}")
                    result = get_image_url_from_wiki(alt_term, retry_count + 1)
                    if result:
                        return result
            
            return None
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 개선된 이미지 검색 전략 (우선순위 순)
        search_strategies = [
            # 1. 정확한 alt 텍스트 매칭
            lambda: find_image_by_alt_exact(soup, item_name),
            # 2. alt 텍스트 부분 매칭  
            lambda: find_image_by_alt_partial(soup, item_name),
            # 3. 테이블 내 아이콘 이미지
            lambda: find_image_in_table(soup, item_name),
            # 4. 클래스 기반 아이콘 검색
            lambda: find_image_by_class(soup),
            # 5. src 경로 기반 검색
            lambda: find_image_by_src_pattern(soup),
            # 6. 최후의 수단: 첫 번째 이미지
            lambda: find_first_content_image(soup)
        ]
        
        for i, strategy in enumerate(search_strategies, 1):
            img_url = strategy()
            if img_url:
                logger.info(f"이미지 발견 (전략 {i}): {img_url}")
                return validate_and_format_url(img_url)
        
        logger.warning(f"{item_name}의 적절한 이미지를 찾을 수 없습니다.")
        return None
        
    except Exception as e:
        logger.error(f"{item_name} 이미지 검색 중 오류: {e}")
        return None

def find_image_by_alt_exact(soup, item_name):
    """정확한 alt 텍스트로 이미지 찾기"""
    for img in soup.find_all('img'):
        if img.get('alt') and img.get('alt').lower().strip() == item_name.lower().strip():
            return img.get('src')
    return None

def find_image_by_alt_partial(soup, item_name):
    """부분 alt 텍스트로 이미지 찾기"""
    for img in soup.find_all('img'):
        alt_text = img.get('alt', '').lower()
        if alt_text and item_name.lower() in alt_text:
            # 노이즈 이미지 제외 (로고, 배너 등)
            if not any(noise in alt_text for noise in ['logo', 'banner', 'icon-', 'edit', 'external']):
                return img.get('src')
    return None

def find_image_in_table(soup, item_name):
    """테이블 내에서 관련 이미지 찾기"""
    # 테이블에서 아이템명과 함께 있는 이미지 찾기
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            row_text = row.get_text().lower()
            if item_name.lower() in row_text:
                img = row.find('img')
                if img and img.get('src'):
                    return img.get('src')
    return None

def find_image_by_class(soup):
    """클래스명으로 아이콘 이미지 찾기"""
    icon_classes = ['icon', 'item-icon', 'spell-icon', 'ability-icon']
    for class_name in icon_classes:
        for img in soup.find_all('img', class_=lambda x: x and any(cls in ' '.join(x) for cls in [class_name])):
            if img.get('src'):
                return img.get('src')
    return None

def find_image_by_src_pattern(soup):
    """src 경로 패턴으로 이미지 찾기"""
    patterns = ['icon', 'spell', 'item', 'ability', 'equipment']
    for img in soup.find_all('img'):
        src = img.get('src', '').lower()
        if any(pattern in src for pattern in patterns):
            # 썸네일이나 작은 이미지 우선
            if 'thumb' in src or '64px' in src or '32px' in src:
                return img.get('src')
    return None

def find_first_content_image(soup):
    """첫 번째 콘텐츠 이미지 찾기 (최후의 수단)"""
    # 메인 콘텐츠 영역에서 첫 번째 이미지
    content_areas = ['#mw-content-text', '.mw-parser-output', '#content']
    for selector in content_areas:
        content = soup.select_one(selector)
        if content:
            img = content.find('img')
            if img and img.get('src'):
                # 로고나 네비게이션 이미지 제외
                src = img.get('src', '').lower()
                if not any(exclude in src for exclude in ['logo', 'wiki', 'nav', 'menu']):
                    return img.get('src')
    return None

def validate_and_format_url(img_url):
    """이미지 URL 검증 및 포맷팅"""
    if not img_url:
        return None
    
    # 상대 경로를 절대 경로로 변환
    if img_url.startswith('//'):
        img_url = f"https:{img_url}"
    elif img_url.startswith('/'):
        img_url = f"https://bg3.wiki{img_url}"
    
    # URL 유효성 간단 검증
    if not img_url.startswith('http'):
        return None
    
    return img_url

def insert_images_to_markdown(content):
    """마크다운 내용에 이미지 URL 삽입 (개선된 정확도)"""
    logger.info("스킬 및 아이템 이미지 삽입 시작 (개선된 시스템)")
    
    # 스킬과 아이템 이름 추출 (개선된 함수 사용)
    skill_items = extract_skill_item_names(content)
    total_found = len(skill_items)
    logger.info(f"검증된 BG3 용어 {total_found}개 발견")
    
    # 이미지 검색 및 수집
    item_image_urls = {}
    search_success = 0
    
    for english_name, korean_name in skill_items.items():
        logger.info(f"'{english_name}' 이미지 검색 중...")
        
        # 우선순위: 정확한 영문명 > 첫 번째 단어 > 변형된 이름
        search_terms = [english_name]
        
        # 공백이 있는 경우 첫 번째 단어도 시도
        if ' ' in english_name:
            first_word = english_name.split()[0]
            if len(first_word) > 3:  # 너무 짧은 단어는 제외
                search_terms.append(first_word)
        
        img_url = None
        for search_term in search_terms:
            img_url = get_image_url_from_wiki(search_term)
            if img_url:
                break
        
        if img_url:
            item_image_urls[english_name] = {
                'url': img_url,
                'korean_name': korean_name,
                'confidence': 'high' if english_name in search_terms[0] else 'medium'
            }
            search_success += 1
            logger.info(f"✅ {english_name}: 이미지 발견")
        else:
            logger.warning(f"❌ {english_name}: 이미지 찾지 못함")
        
        # 과도한 요청 방지
        time.sleep(0.8)
    
    logger.info(f"이미지 검색 완료: {search_success}/{total_found} 성공 ({search_success/total_found*100:.1f}%)")
    
    # 마크다운에 이미지 삽입
    lines = content.split('\n')
    new_content = []
    inserted_images = set()
    
    # 이미지 삽입을 위한 개선된 패턴들
    insertion_patterns = [
        (fr'\*\*({"|".join(re.escape(name) for name in item_image_urls.keys())})\*\*', "bold_pattern"),
        (fr'\(({"|".join(re.escape(name) for name in item_image_urls.keys())})\)', "paren_pattern")
    ]
    
    for line in lines:
        line_modified = False
        
        # 각 패턴에 대해 체크
        for pattern, pattern_type in insertion_patterns:
            if line_modified:
                break
                
            match = re.search(pattern, line)
            if match:
                term = match.group(1)
                
                if term in item_image_urls and term not in inserted_images:
                    img_info = item_image_urls[term]
                    
                    # 신뢰도에 따라 다른 크기 적용
                    width = "120" if img_info['confidence'] == 'high' else "100"
                    
                    # 개선된 이미지 태그 생성
                    img_markdown = (
                        f"<img src=\"{img_info['url']}\" "
                        f"alt=\"{term}\" "
                        f"title=\"{img_info['korean_name']}\" "
                        f"width=\"{width}\" "
                        f"style=\"margin-right: 10px; vertical-align: middle;\">"
                    )
                    
                    # 이미지를 라인 앞에 추가
                    new_content.append(img_markdown)
                    new_content.append(line)
                    
                    inserted_images.add(term)
                    line_modified = True
                    logger.debug(f"🖼️ 이미지 삽입: {term}")
        
        # 이미지가 추가되지 않은 경우에만 원래 라인 추가
        if not line_modified:
            new_content.append(line)
    
    logger.info(f"이미지 삽입 완료: {len(inserted_images)}개 삽입됨")
    
    # 최종 콘텐츠 생성
    final_content = '\n'.join(new_content)
    
    # BG3 헤더 이미지 추가
    header_image = "https://i.namu.wiki/i/IxWGCIu4G78HZv1d2AU_C5taEO8i-iT_aEbh5YbPAz73yIS3gFGB-Fj6EvL4Z-jmjcFIvWhr2XOxN0-sdmH31g.webp"
    header_markdown = f"<img src=\"{header_image}\" alt=\"BG3 헤더 이미지\" width=\"100%\" style=\"margin-bottom: 20px;\">\n\n"
    
    # 첫 번째 제목 찾아서 위에 헤더 이미지 삽입
    first_heading = re.search(r'^#\s+.*$', final_content, re.MULTILINE)
    if first_heading:
        heading_pos = first_heading.start()
        final_content = final_content[:heading_pos] + header_markdown + final_content[heading_pos:]
    else:
        final_content = header_markdown + final_content
    
    # 최종 통계 로깅
    logger.info(f"🎯 이미지 처리 완료 - 총 {len(inserted_images)}개 이미지 삽입 완료")
    
    return final_content 