import re
import time
import requests
import urllib.parse
from bs4 import BeautifulSoup
from .utils import logger

def extract_skill_item_names(content):
    """마크다운 내용에서 스킬과 아이템 이름 추출"""
    # 정규식 패턴들
    patterns = [
        (r'\*\*(.*?) \((.*?)\)\*\*', "한글명 (영문명)"),  # **한글명 (영문명)**
        (r'([\w가-힣\s]+)\(([\w\s\'\-]+)\)', "한글명(영문명)"),  # 한글명(영문명)
        (r'\*\*([\w\s\'\-]+)\*\*', "영문명"),  # **영문명**
        (r'\(([\w\s\'\-]+)\)', "영문명괄호"),  # (영문명)
    ]
    
    # 결과 저장용 딕셔너리 {영문명: 한글명}
    item_dict = {}
    
    for pattern, pattern_name in patterns:
        matches = re.findall(pattern, content)
        logger.debug(f"{pattern_name} 패턴으로 {len(matches)}개 찾음")
        
        if pattern_name == "한글명 (영문명)":
            # (한글명, 영문명) 형태의 결과 처리
            for match in matches:
                korean_name, english_name = match
                # 영문명에 특수문자가 포함된 경우 제외
                if all(c.isalnum() or c.isspace() or c in "'-" for c in english_name):
                    if not any('\uAC00' <= c <= '\uD7A3' for c in english_name):  # 영문명에 한글이 없는지 확인
                        item_dict[english_name] = korean_name
                        logger.debug(f"추출: {english_name} (한글: {korean_name})")
        
        elif pattern_name == "한글명(영문명)":
            # 한글명(영문명) 형태의 결과 처리
            for match in matches:
                korean_name, english_name = match
                if all(c.isalnum() or c.isspace() or c in "'-" for c in english_name):
                    if not any('\uAC00' <= c <= '\uD7A3' for c in english_name):  # 영문명에 한글이 없는지 확인
                        item_dict[english_name] = korean_name
                        logger.debug(f"추출: {english_name} (한글: {korean_name})")
        
        else:
            # 영문명만 있는 패턴 처리
            for match in matches:
                if isinstance(match, tuple):  # 여러 그룹이 있는 경우
                    match = match[0]  # 첫 번째 그룹만 사용
                    
                # 이미 처리된 영문명이 아니고, 짧은 단어는 제외
                if (match not in item_dict.keys() and 
                    match not in item_dict.values() and 
                    len(match) > 3 and 
                    not match.lower() in ["the", "and", "for", "item", "with", "this", "that", "from", "your", "when"]):
                    # 영어 단어만 저장 (한글 포함된 경우 제외)
                    if all(c.isalnum() or c.isspace() or c in "'-" for c in match):
                        if not any('\uAC00' <= c <= '\uD7A3' for c in match):  # 영문명에 한글이 없는지 확인
                            item_dict[match] = match
                            logger.debug(f"추출: {match}")
    
    logger.info(f"추출된 스킬/아이템: {len(item_dict)}개")
    
    # 추출된 영문 아이템 목록 로깅
    if item_dict:
        logger.info(f"추출된 영문 아이템 목록: {', '.join(item_dict.keys())}")
    
    return item_dict

def get_image_url_from_wiki(item_name):
    """BG3 위키에서 아이템/스킬 이미지 URL 가져오기"""
    try:
        # 공백을 언더스코어로 대체하고 URL 인코딩
        encoded_name = urllib.parse.quote(item_name.replace(' ', '_'))
        wiki_url = f"https://bg3.wiki/wiki/{encoded_name}"
        
        logger.info(f"위키 페이지 요청: {wiki_url}")
        response = requests.get(wiki_url, timeout=30)
        
        if response.status_code != 200:
            logger.warning(f"위키 페이지를 찾을 수 없습니다: {wiki_url} (상태 코드: {response.status_code})")
            
            # 대체 검색 시도: 아이템 이름의 일부만 사용하여 검색
            terms = item_name.split()
            if len(terms) > 1:
                main_term = terms[0]
                encoded_main_term = urllib.parse.quote(main_term)
                alt_wiki_url = f"https://bg3.wiki/wiki/{encoded_main_term}"
                logger.info(f"대체 위키 페이지 요청: {alt_wiki_url}")
                
                response = requests.get(alt_wiki_url, timeout=30)
                if response.status_code != 200:
                    logger.warning(f"대체 위키 페이지도 찾을 수 없습니다: {alt_wiki_url}")
                    return None
            else:
                return None
        
        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. alt 속성에 item_name이 포함된 이미지 찾기 (가장 정확한 방법)
        img_with_alt = None
        for img in soup.find_all('img'):
            if img.get('alt') and (item_name.lower() in img.get('alt').lower()):
                img_with_alt = img
                logger.info(f"alt 속성으로 이미지 찾음: {img.get('src')}")
                break
        
        # 2. 클래스에 icon이 포함된 이미지 찾기
        img_with_icon_class = None
        for img in soup.find_all('img'):
            if img.get('class') and any('icon' in cls.lower() for cls in img.get('class')):
                img_with_icon_class = img
                logger.info(f"icon 클래스로 이미지 찾음: {img.get('src')}")
                break
        
        # 3. src에 icon 또는 spell이 포함된 이미지 찾기
        img_with_icon_src = None
        for img in soup.find_all('img'):
            if img.get('src') and ('icon' in img.get('src').lower() or 'spell' in img.get('src').lower()):
                img_with_icon_src = img
                logger.info(f"icon/spell src로 이미지 찾음: {img.get('src')}")
                break
        
        # 4. 일반 이미지 중 첫 번째 이미지 (최후의 방법)
        first_img = None
        for img in soup.find_all('img'):
            if img.get('src'):
                first_img = img
                break
        
        # 우선순위에 따라 이미지 선택
        selected_img = img_with_alt or img_with_icon_class or img_with_icon_src or first_img
        
        if selected_img:
            img_url = selected_img.get('src')
            # URL이 상대 경로인 경우 절대 경로로 변환
            if img_url:
                if img_url.startswith('//'):
                    img_url = f"https:{img_url}"
                elif img_url.startswith('/'):
                    img_url = f"https://bg3.wiki{img_url}"
                logger.info(f"선택된 이미지 URL: {img_url}")
                return img_url
        
        logger.warning(f"{item_name}의 이미지를 찾을 수 없습니다.")
        return None
    
    except Exception as e:
        logger.error(f"{item_name} 이미지 검색 중 오류 발생: {e}")
        return None

def insert_images_to_markdown(content):
    """마크다운 내용에 이미지 URL 삽입"""
    logger.info("스킬 및 아이템 이미지 URL 추가 중...")
    
    # 스킬과 아이템 이름 추출
    skill_items = extract_skill_item_names(content)
    logger.info(f"{len(skill_items)}개의 스킬/아이템을 찾았습니다.")
    
    # 각 영문 이름에 대한 이미지 URL 검색
    item_image_urls = {}
    for english_name, korean_name in skill_items.items():
        # 영문 이름이 너무 짧거나 일반적인 단어면 건너뛰기
        if len(english_name) < 4 or english_name.lower() in ["the", "and", "for", "item", "with", "this", "that"]:
            continue
        
        # 한글 문자가 포함된 경우 검색하지 않음 (영어 이름만 검색)
        if any('\uAC00' <= c <= '\uD7A3' for c in english_name):
            continue
            
        logger.info(f"'{english_name}' 이미지 검색 중...")
        img_url = get_image_url_from_wiki(english_name)
        if img_url:
            item_image_urls[english_name] = img_url
        
        # 과도한 요청 방지를 위한 대기
        time.sleep(0.5)
    
    # 이미지 삽입을 위한 정규식 패턴
    patterns = [
        (fr'\*\*([\w\s\'\-]+)\*\*', lambda m: m.group(1)),  # **영문명** 패턴
        (fr'\(([\w\s\'\-]+)\)', lambda m: m.group(1))       # (영문명) 패턴
    ]
    
    # 마크다운 내용에 이미지 삽입
    lines = content.split('\n')
    new_content = []
    inserted_images = set()  # 중복 삽입 방지를 위한 집합
    
    for line in lines:
        new_content.append(line)
        
        # 현재 라인에서 패턴 매칭
        for pattern, extract_func in patterns:
            for match in re.finditer(pattern, line):
                term = extract_func(match)
                
                # 한글 문자가 포함된 경우 건너뛰기 (영어 이름만 처리)
                if any('\uAC00' <= c <= '\uD7A3' for c in term):
                    continue
                
                # 해당 단어가 이미지 URL 딕셔너리에 있고 아직 삽입되지 않았으면
                if term in item_image_urls and term not in inserted_images:
                    img_url = item_image_urls[term]
                    # 이미지 마크다운 추가
                    img_markdown = f"![{term} 아이콘]({img_url})"
                    new_content.append(img_markdown)
                    inserted_images.add(term)  # 삽입 완료 표시
                    break  # 한 줄에 하나의 이미지만 삽입
    
    logger.info(f"{len(inserted_images)}개의 이미지 URL을 추가했습니다.")
    
    # 최종 마크다운 생성
    final_content = '\n'.join(new_content)
    
    # 고정 이미지를 본문 최상단에 추가
    bg3_header_image = "https://i.namu.wiki/i/IxWGCIu4G78HZv1d2AU_C5taEO8i-iT_aEbh5YbPAz73yIS3gFGB-Fj6EvL4Z-jmjcFIvWhr2XOxN0-sdmH31g.webp"
    header_image_markdown = f"![BG3 헤더 이미지]({bg3_header_image})\n\n"
    
    # 마크다운 첫 번째 제목 줄 찾기
    first_heading_match = re.search(r'^#\s+.*$', final_content, re.MULTILINE)
    
    if first_heading_match:
        # 제목 바로 위에 이미지 삽입
        heading_pos = first_heading_match.start()
        final_content = final_content[:heading_pos] + header_image_markdown + final_content[heading_pos:]
    else:
        # 제목이 없으면 문서 맨 앞에 추가
        final_content = header_image_markdown + final_content
    
    return final_content 