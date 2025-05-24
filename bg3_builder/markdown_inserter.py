import re
from .utils import logger

def extract_build_info(content):
    """마크다운 내용에서 빌드 정보 추출"""
    info = {
        "build_name": "",
        "role": "",
        "key_stats": "",
        "race": "",
        "strength": "",
        "patch": ""
    }
    
    # 빌드명 추출 (제목에서)
    title_match = re.search(r"^#\s+(.+?)(?:\s+빌드|\s+가이드|\s+공략)?$", content, re.MULTILINE)
    if title_match:
        info["build_name"] = title_match.group(1).strip()
    
    # 역할 추출 - 주로 "~특화", "~중심", "~형" 등으로 표현됨
    role_patterns = [
        r"(힐링|버프|탱커|딜러|서포터|컨트롤|유틸리티|원딜|근딜)(?:\s*[/&,]\s*(?:힐링|버프|탱커|딜러|서포터|컨트롤|유틸리티|원딜|근딜))*\s*(?:특화|중심|형)",
        r"(?:파티|전투)에서\s*(?:주로)?\s*(.{2,10}?)(?:역할|담당)",
        r"(?:이\s*빌드는|이\s*클래스는)\s*(.{2,15}?)에\s*(?:특화|집중|좋은)"
    ]
    
    for pattern in role_patterns:
        match = re.search(pattern, content)
        if match:
            info["role"] = match.group(1).strip()
            break
    
    # 핵심 스탯 추출
    stat_match = re.search(r"(?:스탯|능력치).*?(?:STR|힘)\s*(\d+).*?(?:DEX|민첩)\s*(\d+).*?(?:CON|건강)\s*(\d+).*?(?:INT|지능)\s*(\d+).*?(?:WIS|지혜)\s*(\d+).*?(?:CHA|매력)\s*(\d+)", content, re.DOTALL | re.IGNORECASE)
    if stat_match:
        # 가장 높은 두 개의 스탯 찾기
        stats = {
            "WIS": int(stat_match.group(5)),
            "CON": int(stat_match.group(3)),
            "DEX": int(stat_match.group(2)),
            "STR": int(stat_match.group(1)),
            "CHA": int(stat_match.group(6)),
            "INT": int(stat_match.group(4))
        }
        
        # 가장 높은 두 개의 스탯
        top_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:2]
        info["key_stats"] = f"{top_stats[0][0]} {top_stats[0][1]} / {top_stats[1][0]} {top_stats[1][1]}"
    
    # 추천 종족 추출
    race_patterns = [
        r"(?:종족|레이스)[:\s]*[*_]?([가-힣\s]+(?:\([A-Za-z\s]+\))?)(?:[_*]|\s|$)",
        r"추천\s+(?:종족|레이스)[:\s]*[*_]?([가-힣\s]+(?:\([A-Za-z\s]+\))?)(?:[_*]|\s|$)",
        r"(?:종족|레이스)[은는이가]\s*([가-힣\s]+(?:\([A-Za-z\s]+\))?)"
    ]
    
    for pattern in race_patterns:
        match = re.search(pattern, content)
        if match:
            info["race"] = match.group(1).strip()
            break
    
    # 강점/장점 추출
    strength_patterns = [
        r"(?:강점|장점)[:\s]*(.{5,50}?)(?:[\n\.]|$)",
        r"(?:이\s*빌드의|클래스의)\s*(?:장점|강점|특징)[은는이가]\s*(.{5,50}?)(?:[\n\.]|$)"
    ]
    
    for pattern in strength_patterns:
        match = re.search(pattern, content)
        if match:
            info["strength"] = match.group(1).strip()
            break
    
    # 패치 기준 추출
    patch_patterns = [
        r"(?:패치|버전|업데이트)[:\s]*([0-9.]+)",
        r"(?:패치|버전|업데이트)[:\s]*(\d+년\s*\d+월(?:\s*\d+일)?)",
        r"(\d+년\s*\d+월(?:\s*\d+일)?)\s*(?:패치|버전|업데이트)"
    ]
    
    for pattern in patch_patterns:
        match = re.search(pattern, content)
        if match:
            info["patch"] = match.group(1).strip()
            break
    
    return info

# 요약 카드 생성 함수 제거됨 - 사용자 요청에 따라 완전 삭제

def extract_spells(content):
    """마크다운 내용에서 주문/스킬 추출"""
    spells = []
    
    # 주문/스킬 추출 패턴
    patterns = [
        r"\*\*([^*]+?)\*\*\s*(?:\(([^)]+)\))?\s*[:：]\s*(.+?)(?:[\.。]|$)",  # **주문명**(영문명): 설명
        r"- \*\*([^*]+?)\*\*\s*(?:\(([^)]+)\))?\s*[:：]\s*(.+?)(?:[\.。]|$)",  # - **주문명**(영문명): 설명
        r"[0-9]+\.\s*\*\*([^*]+?)\*\*\s*(?:\(([^)]+)\))?\s*[:：]\s*(.+?)(?:[\.。]|$)"  # 1. **주문명**(영문명): 설명
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        for match in matches:
            spell_name = match[0].strip()
            english_name = match[1].strip() if match[1] else ""
            description = match[2].strip() if len(match) > 2 else ""
            
            if spell_name and len(spell_name) > 1:
                spells.append({
                    "name": spell_name,
                    "english_name": english_name,
                    "description": description
                })
    
    # 중복 제거
    unique_spells = []
    seen_names = set()
    
    for spell in spells:
        spell_key = spell["name"].lower()
        if spell_key not in seen_names:
            seen_names.add(spell_key)
            unique_spells.append(spell)
    
    logger.info(f"{len(unique_spells)}개의 주문/스킬 추출됨")
    return unique_spells

def create_combat_routine(content):
    """전투 루틴 섹션 생성"""
    spells = extract_spells(content)
    
    # 추출된 주문이 없으면 기본 템플릿 사용
    if not spells or len(spells) < 3:
        return """
## 전투 루틴 예시
1. 전투 시작 → 버프 주문 선사용
2. 주요 공격 주문 사용 → 보조 주문으로 연계
3. 대상 상태에 따라 CC/서포트 주문 적절히 활용
"""
    
    # 주문 타입 분류 (추출된 설명을 바탕으로)
    buff_spells = []
    attack_spells = []
    utility_spells = []
    
    for spell in spells:
        desc = spell["description"].lower()
        name = spell["name"]
        
        # 버프/디버프 주문
        if any(keyword in desc for keyword in ["버프", "강화", "증가", "보너스", "이점", "방어", "보호", "치유", "회복"]):
            buff_spells.append(name)
        # 공격 주문
        elif any(keyword in desc for keyword in ["피해", "공격", "데미지", "타격", "벙", "대미지"]):
            attack_spells.append(name)
        # 유틸리티 주문
        else:
            utility_spells.append(name)
    
    # 분류가 비어있으면 첫 번째 스펠 넣기
    if not buff_spells and spells:
        buff_spells.append(spells[0]["name"])
    if not attack_spells and len(spells) > 1:
        attack_spells.append(spells[1]["name"])
    if not utility_spells and len(spells) > 2:
        utility_spells.append(spells[2]["name"])
    
    # 전투 루틴 생성
    combat_routine = """
## 전투 루틴 예시
"""
    
    # 버프 주문이 있으면 첫 번째 단계로
    if buff_spells:
        combat_routine += f"1. **전투 준비** → {buff_spells[0]}"
        if len(buff_spells) > 1:
            combat_routine += f" + {buff_spells[1]}"
        combat_routine += "\n"
    else:
        combat_routine += "1. **전투 준비** → 유리한 위치 선점\n"
    
    # 공격 주문이 있으면 두 번째 단계로
    if attack_spells:
        combat_routine += f"2. **공격 페이즈** → {attack_spells[0]}"
        if len(attack_spells) > 1:
            combat_routine += f" → {attack_spells[1]} 연계"
        combat_routine += "\n"
    else:
        combat_routine += "2. **공격 페이즈** → 주요 공격 스킬 활용\n"
    
    # 유틸리티 주문이 있으면 세 번째 단계로
    if utility_spells:
        combat_routine += f"3. **대응 페이즈** → 상황에 따라 {utility_spells[0]}"
        if len(utility_spells) > 1:
            combat_routine += f" 또는 {utility_spells[1]}"
        combat_routine += " 사용\n"
    else:
        combat_routine += "3. **대응 페이즈** → 상황에 맞는 유틸리티 스킬 활용\n"
    
    # 추가 팁
    combat_routine += "4. **위기 상황** → 보유한 포션 및 스크롤 적극 활용\n"
    
    logger.info("전투 루틴 섹션 생성 완료")
    return combat_routine

def remove_existing_summary_cards(content):
    """기존 마크다운에서 요약 카드(인용구) 제거"""
    # 인용구 형태의 요약 카드 패턴 제거
    patterns = [
        # > **빌드명**: ... 형태의 요약 카드
        r'>\s*\*\*빌드명\*\*:.*?(?=\n[^>]|\n$|\Z)',
        # 연속된 인용구들 (여러 줄에 걸친 요약 카드)
        r'(?:>\s*\*\*(?:빌드명|주요\s*역할|핵심\s*스탯|추천\s*종족|강점|패치\s*기준)\*\*:.*?\n)+',
        # blockquote 태그로 된 요약 카드 (HTML 변환 후)
        r'<blockquote[^>]*>.*?빌드명.*?</blockquote>',
        # HTML에서 변환된 형태도 제거
        r'<blockquote[^>]*>.*?<strong>빌드명</strong>.*?</blockquote>'
    ]
    
    for pattern in patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
    
    # 빈 줄 정리 (연속된 빈 줄을 하나로)
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    logger.info("기존 요약 카드 제거 완료")
    return content

def enhance_markdown_content(content, build_name):
    """마크다운 내용 강화 (전투 루틴 추가만 수행, 요약 카드는 제거)"""
    logger.info("마크다운 콘텐츠 강화 작업 시작")
    
    # 기존 요약 카드가 있다면 제거
    content = remove_existing_summary_cards(content)
    
    # 요약 카드 생성 부분 제거 (사용자 요청에 따라)
    # summary_card = create_summary_card(content)
    
    # 전투 루틴 섹션 생성
    combat_routine = create_combat_routine(content)
    
    # 제목 찾기 (요약 카드 삽입 부분 제거)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    
    # 요약 카드 삽입 로직 제거
    # if title_match:
    #     # 제목 바로 아래에 요약 카드 삽입
    #     title_end = title_match.end()
    #     content = content[:title_end] + "\n\n" + summary_card + content[title_end:]
    # else:
    #     # 제목이 없으면 문서 상단에 빌드명으로 제목 생성 후 요약 카드 삽입
    #     title = f"# {build_name} 빌드 가이드\n\n"
    #     content = title + summary_card + content
    
    # 제목이 없는 경우에만 제목 추가 (요약 카드 없이)
    if not title_match:
        title = f"# {build_name} 빌드 가이드\n\n"
        content = title + content
    
    # 전투 루틴 섹션이 이미 있는지 확인
    if not re.search(r"^#+\s+(?:전투|컴뱃|콤보|루틴)", content, re.MULTILINE | re.IGNORECASE):
        # 마지막 섹션 뒤에 전투 루틴 추가
        content += "\n\n" + combat_routine
    
    logger.info("마크다운 콘텐츠 강화 완료 (요약 카드 제외)")
    return content 