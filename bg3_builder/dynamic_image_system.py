#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
from bs4 import BeautifulSoup
from .utils import logger
from .wiki_image_parser import get_image_url_from_wiki

class DynamicImageExtractor:
    """실제 텍스트에서 BG3 용어를 동적으로 추출하고 이미지를 찾는 시스템"""
    
    def __init__(self):
        # BG3 위키에서 가져올 수 있는 용어 패턴들
        self.bg3_patterns = [
            # 주문 패턴 (더 광범위하게)
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Word|Bolt|Wave|Strike|Guard|Shield|Heal|Cure|Bless|Ward|Light|Fire|Ice|Lightning|Thunder|Magic|Divine|Sacred|Holy|Spirit|Soul|Death|Life|Healing|Mass|Greater|Lesser)))\b',
            
            # 장비 패턴
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Armor|Sword|Blade|Axe|Mace|Staff|Wand|Bow|Shield|Helmet|Gauntlets|Boots|Ring|Amulet|Necklace|Cloak|Robe|Mail|Plate|Leather|Chain|Splint|Scale)))\b',
            
            # 클래스/서브클래스 패턴
            r'\b(Fighter|Wizard|Rogue|Ranger|Paladin|Barbarian|Bard|Cleric|Druid|Monk|Sorcerer|Warlock)\b',
            r'\b([A-Z][a-z]+\s+(?:Domain|Circle|Patron|School|Path|Way|College|Oath))\b',
            
            # 특성/피트 패턴
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Master|Expert|Adept|Caster|Fighter|Attacker|Defender|Healer)))\b',
            
            # 종족 패턴
            r'\b(Human|Elf|Dwarf|Halfling|Dragonborn|Tiefling|Half-orc|Half-elf|Gnome|Githyanki|Githzerai|Drow)\b',
            r'\b(High\s+Elf|Wood\s+Elf|Drow|Hill\s+Dwarf|Mountain\s+Dwarf|Lightfoot\s+Halfling|Strongheart\s+Halfling)\b',
            
            # 액션/특수능력 패턴
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Channel|Divinity|Smite|Rage|Sneak|Attack|Strike|Shot|Spell|Cantrip|Ritual)))\b',
        ]
        
        # 한국어-영어 매핑 (일반적인 것들)
        self.korean_to_english = {
            "치유의 말": "Healing Word",
            "치유의 단어": "Healing Word", 
            "천둥파": "Thunderwave",
            "번개 화살": "Lightning Bolt",
            "마법 화살": "Magic Missile",
            "방호": "Sanctuary",
            "축복": "Bless",
            "영적 무기": "Spiritual Weapon",
            "영혼의 수호자": "Spirit Guardians",
            "집단 치료": "Mass Cure Wounds",
            "죽음으로부터의 구원": "Death Ward",
            "아다만틴 판금갑옷": "Adamantine Splint Armor",
            "생명권역": "Life Domain",
            "클레릭": "Cleric",
            "마법사": "Wizard",
            "전사": "Fighter",
            "도적": "Rogue",
            "팔라딘": "Paladin",
            "바바리안": "Barbarian",
            "음유시인": "Bard",
            "드루이드": "Druid",
            "몽크": "Monk",
            "소서러": "Sorcerer",
            "워록": "Warlock",
            "레인저": "Ranger"
        }
    
    def extract_bg3_terms_from_text(self, english_text, korean_text):
        """영어와 한국어 텍스트에서 BG3 용어를 동적으로 추출"""
        logger.info("🔍 동적 BG3 용어 추출 시작")
        
        all_terms = set()
        english_terms = set()
        korean_terms = set()
        
        # 1. 영어 텍스트에서 패턴 매칭으로 추출
        for pattern in self.bg3_patterns:
            matches = re.findall(pattern, english_text, re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    term = match[0] if match[0] else match[1] if len(match) > 1 else ''
                else:
                    term = match
                
                if term and len(term) > 2:  # 너무 짧은 건 제외
                    english_terms.add(term.strip())
                    all_terms.add(term.strip())
        
        # 2. 한국어 텍스트에서 매핑 가능한 용어 찾기
        for korean, english in self.korean_to_english.items():
            if korean in korean_text:
                korean_terms.add(korean)
                all_terms.add(english)  # 영어로 변환해서 추가
                logger.info(f"매핑 발견: {korean} → {english}")
        
        # 3. 추가 휴리스틱: 대문자로 시작하는 연속된 단어들 (게임 용어 가능성)
        additional_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b', english_text)
        for term in additional_terms:
            if len(term) > 4 and not any(word in term.lower() for word in ['the', 'and', 'for', 'with', 'this', 'that', 'from']):
                all_terms.add(term)
        
        logger.info(f"추출된 영어 용어: {len(english_terms)}개")
        logger.info(f"추출된 한국어 매핑: {len(korean_terms)}개") 
        logger.info(f"총 추출된 용어: {len(all_terms)}개")
        
        if len(all_terms) > 0:
            sample_terms = list(all_terms)[:10]
            logger.info(f"샘플 용어들: {', '.join(sample_terms)}")
        
        return list(all_terms), dict(zip(korean_terms, [self.korean_to_english[k] for k in korean_terms if k in self.korean_to_english]))
    
    def search_and_validate_image(self, term):
        """용어에 대한 이미지를 찾고 검증"""
        try:
            # 기본 검색
            image_url = get_image_url_from_wiki(term)
            if image_url:
                return image_url
            
            # 대체 검색 전략들
            search_variants = [
                term.replace(" ", "_"),
                term.lower(),
                term.title(),
                term.replace("'", ""),
                term.replace("-", " "),
                term.replace("_", " ")
            ]
            
            for variant in search_variants:
                if variant != term:
                    image_url = get_image_url_from_wiki(variant)
                    if image_url:
                        return image_url
            
            # 부분 매칭 시도
            words = term.split()
            if len(words) > 1:
                for word in words:
                    if len(word) > 3:  # 의미있는 단어만
                        image_url = get_image_url_from_wiki(word)
                        if image_url:
                            return image_url
            
            return None
            
        except Exception as e:
            logger.warning(f"이미지 검색 중 오류 ({term}): {e}")
            return None
    
    def insert_images_into_markdown(self, markdown_content, term_image_mapping, korean_mapping):
        """마크다운에 이미지를 동적으로 삽입"""
        logger.info("🖼️ 마크다운에 이미지 삽입 시작")
        
        content = markdown_content
        inserted_count = 0
        
        # 영어 용어들 먼저 처리
        for term, image_url in term_image_mapping.items():
            if not image_url:
                continue
                
            # 다양한 패턴으로 용어 찾기
            patterns = [
                rf'\b{re.escape(term)}\b',
                rf'\*\*{re.escape(term)}\*\*',
                rf'_{re.escape(term)}_',
                rf'`{re.escape(term)}`'
            ]
            
            for pattern in patterns:
                if re.search(pattern, content):
                    # 이미지 마크다운 생성
                    img_markdown = f'<img src="{image_url}" alt="{term}" title="{term}" style="margin-right: 10px; vertical-align: middle;" style="width: 120px;">'
                    
                    # 첫 번째 매칭에만 이미지 삽입
                    content = re.sub(pattern, f'{img_markdown}\n\n\\g<0>', content, count=1)
                    inserted_count += 1
                    logger.info(f"✅ 이미지 삽입: {term}")
                    break
        
        # 한국어 매핑된 용어들 처리
        for korean, english in korean_mapping.items():
            if english in term_image_mapping and term_image_mapping[english]:
                image_url = term_image_mapping[english]
                
                # 한국어 용어에 이미지 삽입
                if korean in content:
                    img_markdown = f'<img src="{image_url}" alt="{english}" title="{english}" style="margin-right: 10px; vertical-align: middle;" style="width: 120px;">'
                    content = content.replace(korean, f'{img_markdown}\n\n{korean}', 1)
                    inserted_count += 1
                    logger.info(f"✅ 한국어 이미지 삽입: {korean} ({english})")
        
        logger.info(f"총 {inserted_count}개 이미지 삽입 완료")
        return content

def process_dynamic_images(english_build_info, korean_markdown):
    """동적 이미지 시스템으로 이미지 처리"""
    logger.info("🚀 동적 이미지 시스템 시작")
    
    extractor = DynamicImageExtractor()
    
    # 1. 용어 추출
    terms, korean_mapping = extractor.extract_bg3_terms_from_text(english_build_info, korean_markdown)
    
    if not terms:
        logger.warning("추출된 용어가 없습니다")
        return korean_markdown
    
    # 2. 이미지 검색
    logger.info(f"🔍 {len(terms)}개 용어에 대한 이미지 검색 시작")
    term_image_mapping = {}
    successful_searches = 0
    
    for i, term in enumerate(terms[:30], 1):  # 최대 30개까지만 처리 (성능상)
        logger.info(f"[{i}/{min(len(terms), 30)}] '{term}' 이미지 검색 중...")
        
        image_url = extractor.search_and_validate_image(term)
        term_image_mapping[term] = image_url
        
        if image_url:
            successful_searches += 1
            logger.info(f"✅ {term}: 이미지 발견")
        else:
            logger.info(f"❌ {term}: 이미지 없음")
    
    logger.info(f"이미지 검색 완료: {successful_searches}/{len(terms[:30])} 성공 ({successful_searches/min(len(terms), 30)*100:.1f}%)")
    
    # 3. 이미지 삽입
    final_content = extractor.insert_images_into_markdown(korean_markdown, term_image_mapping, korean_mapping)
    
    logger.info("🎯 동적 이미지 시스템 처리 완료")
    return final_content 