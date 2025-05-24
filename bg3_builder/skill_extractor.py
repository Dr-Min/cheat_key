#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from typing import Dict, List, Set
from .utils import logger

def extract_bg3_terms_from_source(english_build_info: str) -> Dict[str, List[str]]:
    """
    Perplexity에서 받은 원본 영어 빌드 정보에서 정확한 BG3 용어들을 추출
    
    Args:
        english_build_info: Perplexity API로부터 받은 원본 영어 빌드 정보
        
    Returns:
        Dict: {category: [terms]} 형태로 추출된 용어들
    """
    logger.info("원본 영어 빌드 정보에서 BG3 용어 추출 시작")
    
    # 추출할 카테고리별 패턴들
    extraction_patterns = {
        "spells": [
            # 주문 이름 패턴들
            r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s*(?:\([^)]*\))?\s*(?:spell|cantrip)',
            r'spell:\s*([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'cast\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'learn\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'pick\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            # 특정 주문명 패턴
            r'\b(Magic Missile|Shield|Fireball|Lightning Bolt|Counterspell|Haste|Misty Step|Thunderwave|Healing Word|Cure Wounds|Bless|Divine Smite|Scorching Ray|Burning Hands|Eldritch Blast|Hunter\'s Mark|Hex|Wild Shape|Action Surge|Sneak Attack|Rage)\b'
        ],
        "weapons": [
            # 무기 이름 패턴들
            r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s*(?:\+\d+)?\s*(?:sword|bow|staff|mace|hammer|axe|dagger|crossbow|club|quarterstaff|scimitar|rapier|greatsword|longbow|shortbow|warhammer)',
            r'weapon:\s*([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'wield\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            # 특정 무기명
            r'\b(Shortsword|Longbow|Shortbow|Quarterstaff|Staff|Scimitar|Rapier|Greatsword|Crossbow|Dagger|Mace|Warhammer|Battleaxe)\b'
        ],
        "armor": [
            # 방어구 패턴들
            r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s*(?:Armor|Mail|Leather|Plate|Robe|Cloak)',
            r'armor:\s*([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'wear\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            # 특정 방어구명
            r'\b(Studded Leather|Chain Mail|Scale Mail|Plate Armor|Leather Armor|Hide Armor|Padded Armor|Ring Mail|Splint Armor|Half Plate)\b'
        ],
        "accessories": [
            # 액세서리 패턴들
            r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s*(?:Ring|Amulet|Necklace|Bracers|Gloves|Boots|Belt|Helmet|Crown|Circlet|Cloak|Cape)',
            r'\b(Ring|Amulet|Gloves|Boots|Helmet|Cloak|Belt|Bracers)\s+of\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            # 특정 액세서리명
            r'\b(Ring of Protection|Amulet of Health|Gloves of Dexterity|Boots of Speed|Helmet of Intellect|Cloak of Displacement)\b'
        ],
        "class_features": [
            # 클래스 특징 패턴들
            r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s*(?:Feature|Ability|Surge|Strike|Shot|Form)',
            r'gain\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'unlock\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            # 특정 클래스 특징명
            r'\b(Action Surge|Extra Attack|Sneak Attack|Arcane Shot|Wild Shape|Rage|Channel Divinity|Fighting Style|Spellcasting|Metamagic)\b'
        ],
        "races": [
            # 종족 패턴들
            r'race:\s*([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'racial\s+(?:trait|feature|ability):\s*([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            # 특정 종족명
            r'\b(Human|Elf|Half-Elf|Dwarf|Halfling|Dragonborn|Tiefling|Gnome|Half-Orc|Githyanki|Wood Elf|High Elf|Mountain Dwarf|Hill Dwarf|Lightfoot Halfling|Stout Halfling)\b'
        ]
    }
    
    extracted_terms = {}
    
    for category, patterns in extraction_patterns.items():
        category_terms = set()
        
        for pattern in patterns:
            matches = re.finditer(pattern, english_build_info, re.IGNORECASE)
            for match in matches:
                # 매치된 그룹들 중에서 실제 용어 추출
                for group in match.groups():
                    if group and len(group) > 2:
                        # 정리된 용어
                        clean_term = clean_extracted_term(group)
                        if clean_term and is_valid_bg3_term(clean_term):
                            category_terms.add(clean_term)
        
        # 리스트로 변환하고 정렬
        extracted_terms[category] = sorted(list(category_terms))
        logger.info(f"{category}: {len(extracted_terms[category])}개 용어 추출")
    
    # 추출된 용어들 로깅
    for category, terms in extracted_terms.items():
        if terms:
            logger.info(f"{category} 용어들: {', '.join(terms[:10])}{'...' if len(terms) > 10 else ''}")
    
    total_terms = sum(len(terms) for terms in extracted_terms.values())
    logger.info(f"총 {total_terms}개의 정확한 BG3 용어 추출 완료")
    
    return extracted_terms

def clean_extracted_term(term: str) -> str:
    """추출된 용어 정리"""
    # 앞뒤 공백 제거
    term = term.strip()
    
    # 특수문자 정리
    term = re.sub(r'^[^\w]', '', term)  # 앞의 특수문자 제거
    term = re.sub(r'[^\w\s\'-]$', '', term)  # 뒤의 특수문자 제거
    
    # 연속된 공백을 하나로
    term = re.sub(r'\s+', ' ', term)
    
    # 첫 글자 대문자화 (각 단어별로)
    term = ' '.join(word.capitalize() for word in term.split())
    
    return term

def is_valid_bg3_term(term: str) -> bool:
    """BG3 용어로 유효한지 검증"""
    # 길이 체크
    if len(term) < 3 or len(term) > 50:
        return False
    
    # 제외할 일반적인 단어들
    excluded_words = {
        'the', 'and', 'for', 'with', 'from', 'that', 'this', 'when', 'where', 'what',
        'level', 'build', 'guide', 'damage', 'attack', 'turn', 'round', 'point', 'bonus',
        'action', 'reaction', 'save', 'roll', 'hit', 'miss', 'target', 'enemy', 'ally',
        'character', 'player', 'game', 'combat', 'battle', 'fight', 'stat', 'ability'
    }
    
    if term.lower() in excluded_words:
        return False
    
    # 숫자만 있는 경우 제외
    if term.isdigit():
        return False
    
    # 영문자와 공백, 하이픈, 아포스트로피만 허용
    if not re.match(r"^[A-Za-z\s\'-]+$", term):
        return False
    
    return True

def create_term_mapping(extracted_terms: Dict[str, List[str]], korean_content: str) -> Dict[str, str]:
    """
    추출된 영어 용어들과 한국어 번역 내용을 매핑
    
    Args:
        extracted_terms: 원본에서 추출된 영어 용어들
        korean_content: 번역된 한국어 마크다운 내용
        
    Returns:
        Dict: {영어_용어: 한국어_용어} 매핑
    """
    logger.info("영어-한국어 용어 매핑 생성 중...")
    
    term_mapping = {}
    
    # 모든 카테고리의 용어들을 하나로 합침
    all_english_terms = []
    for terms in extracted_terms.values():
        all_english_terms.extend(terms)
    
    # 한국어 콘텐츠에서 영어 괄호 표기 찾기
    # 예: "마법 화살 (Magic Missile)" 패턴
    korean_english_pattern = r'([가-힣\s]+)\s*\(([A-Za-z\s\'\-]+)\)'
    matches = re.findall(korean_english_pattern, korean_content)
    
    for korean_term, english_term in matches:
        korean_term = korean_term.strip()
        english_term = english_term.strip()
        
        # 추출된 영어 용어와 매치되면 매핑에 추가
        if english_term in all_english_terms:
            term_mapping[english_term] = korean_term
            logger.debug(f"매핑 추가: {english_term} → {korean_term}")
    
    logger.info(f"총 {len(term_mapping)}개의 용어 매핑 생성 완료")
    
    return term_mapping

def get_image_search_terms(extracted_terms: Dict[str, List[str]]) -> List[str]:
    """
    이미지 검색에 사용할 우선순위 용어 리스트 생성
    
    Args:
        extracted_terms: 카테고리별 추출된 용어들
        
    Returns:
        List[str]: 우선순위 순으로 정렬된 검색 용어들
    """
    search_terms = []
    
    # 우선순위: spells > weapons > armor > accessories > class_features > races
    priority_order = ['spells', 'weapons', 'armor', 'accessories', 'class_features', 'races']
    
    for category in priority_order:
        if category in extracted_terms:
            search_terms.extend(extracted_terms[category])
    
    # 중복 제거하면서 순서 유지
    unique_terms = []
    seen = set()
    
    for term in search_terms:
        if term not in seen:
            unique_terms.append(term)
            seen.add(term)
    
    logger.info(f"이미지 검색용 {len(unique_terms)}개 용어 준비 완료")
    
    return unique_terms 