#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from .utils import logger
from .wiki_image_parser import get_image_url_from_wiki

def extract_english_terms_simple(perplexity_content):
    """Perplexity에서 영어 용어를 아주 간단하게 추출"""
    logger.info("🔍 간단한 영어 용어 추출 시작")
    
    english_terms = set()
    
    # 1. 괄호 안의 영어 용어들 (가장 확실함)
    bracket_pattern = r'\(([A-Z][A-Za-z\s\'\-]+)\)'
    bracket_matches = re.findall(bracket_pattern, perplexity_content)
    
    for term in bracket_matches:
        term = term.strip()
        if len(term) > 3 and not re.search(r'[가-힣]', term):  # 한글 없고 3글자 이상
            english_terms.add(term)
            logger.info(f"괄호에서 발견: {term}")
    
    # 2. 콜론 뒤의 영어 용어들
    colon_pattern = r':\s*([A-Z][A-Za-z\s\'\-]+(?:\s+(?:Armor|Staff|Helm|Boots|Cloak|Ring|Amulet|Wounds|Word|Flame|Domain|Dwarf|Artisan|Caster))?)'
    colon_matches = re.findall(colon_pattern, perplexity_content)
    
    for term in colon_matches:
        term = term.strip()
        if len(term) > 3 and not re.search(r'[가-힣]', term):
            english_terms.add(term)
            logger.info(f"콜론에서 발견: {term}")
    
    # 3. 확실한 BG3 용어들 직접 찾기
    known_terms = [
        'Guidance', 'Resistance', 'Cure Wounds', 'Bless', 'Healing Word', 'Aid',
        'Spiritual Weapon', 'Sacred Flame', 'Spirit Guardians', 'Mass Healing Word',
        'Death Ward', 'Divine Strike', 'Mass Cure Wounds', 'Divine Intervention',
        'Heroes Feast', 'Life Domain', 'Shield Dwarf', 'Guild Artisan', 'War Caster',
        'Adamantine Splint Armor', 'Amulet of Greater Health', 'Helm of Brilliance',
        'Cloak of Protection', 'Ring of Regeneration', 'Preserve Life', 'Channel Divinity'
    ]
    
    for term in known_terms:
        if term in perplexity_content:
            english_terms.add(term)
            logger.info(f"확실한 용어 발견: {term}")
    
    final_terms = list(english_terms)
    logger.info(f"총 추출된 영어 용어: {len(final_terms)}개")
    
    return final_terms

def search_images_simple(terms):
    """용어들에 대해 간단하게 이미지 검색"""
    logger.info(f"🖼️ {len(terms)}개 용어 이미지 검색 시작")
    
    term_images = {}
    success_count = 0
    
    for i, term in enumerate(terms, 1):
        logger.info(f"[{i}/{len(terms)}] '{term}' 검색 중...")
        
        # 간단한 검색 전략들
        search_variants = [
            term,
            term.replace(' ', '_'),
            term.lower(),
            term.replace(' ', '')
        ]
        
        # 복합 단어는 마지막 단어도 시도
        if ' ' in term:
            last_word = term.split()[-1]
            if len(last_word) > 3:
                search_variants.append(last_word)
        
        image_url = None
        for variant in search_variants:
            image_url = get_image_url_from_wiki(variant)
            if image_url:
                logger.info(f"✅ 이미지 발견: {term} (검색어: {variant})")
                break
        
        if image_url:
            term_images[term] = image_url
            success_count += 1
        else:
            logger.info(f"❌ 이미지 없음: {term}")
    
    logger.info(f"이미지 검색 완료: {success_count}/{len(terms)} 성공")
    return term_images

def insert_images_simple(korean_markdown, term_images):
    """한국어 마크다운에 간단하게 이미지 삽입"""
    logger.info("🖼️ 이미지 삽입 시작")
    
    content = korean_markdown
    inserted_count = 0
    
    # 한국어 마크다운에서 괄호 안의 영어 용어들 찾기
    bracket_pattern = r'\(([A-Z][A-Za-z\s\'\-]+)\)'
    bracket_matches = re.findall(bracket_pattern, content)
    
    logger.info(f"한국어 마크다운에서 발견된 괄호 안 용어들: {bracket_matches[:5]}...")
    
    for term, image_url in term_images.items():
        # 한국어 마크다운에서 이 용어가 괄호 안에 있는지 확인
        for bracket_term in bracket_matches:
            if term.lower() == bracket_term.lower() or term == bracket_term:
                # 간단한 이미지 스타일 (더 작게)
                img_tag = f'<img src="{image_url}" alt="{term}" title="{term}" style="width: 48px; height: 48px; border: 2px solid #8B4513; border-radius: 6px; margin-left: 8px; vertical-align: middle; display: inline-block;">'
                
                # 괄호 안의 용어 뒤에 이미지 삽입 (줄바꿈 없이)
                pattern = rf'\({re.escape(bracket_term)}\)'
                if re.search(pattern, content, re.IGNORECASE):
                    content = re.sub(pattern, f'({bracket_term}) {img_tag}', content, count=1, flags=re.IGNORECASE)
                    inserted_count += 1
                    logger.info(f"✅ 이미지 삽입: {term} (괄호: {bracket_term})")
                    break
    
    # 추가: 한국어 용어와 매칭 시도
    korean_mappings = {
        'Guidance': ['가이던스', '지도'],
        'Bless': ['축복'],
        'Cure Wounds': ['상처', '치유'],
        'Healing Word': ['치유', '회복'],
        'Sacred Flame': ['성스러운', '화염'],
        'Spirit Guardians': ['영혼', '수호자'],
        'Life Domain': ['생명', '영역'],
        'Shield Dwarf': ['방패', '드워프'],
        'War Caster': ['전쟁', '술사']
    }
    
    for term, image_url in term_images.items():
        if term in korean_mappings:
            for korean_word in korean_mappings[term]:
                if korean_word in content and term not in content:
                    img_tag = f'<img src="{image_url}" alt="{term}" title="{term}" style="width: 32px; height: 32px; border: 2px solid #8B4513; border-radius: 4px; margin-left: 6px; vertical-align: middle; display: inline-block;">'
                    
                    # 한국어 단어 뒤에 이미지 삽입 (줄바꿈 없이)
                    content = re.sub(f'({korean_word})', f'\\1 {img_tag}', content, count=1)
                    inserted_count += 1
                    logger.info(f"✅ 한국어 매칭 이미지 삽입: {term} -> {korean_word}")
                    break
    
    logger.info(f"총 {inserted_count}개 이미지 삽입 완료")
    return content

def process_simple_perplexity_images(korean_markdown, perplexity_file_path):
    """
    Perplexity 파일을 사용해서 한국어 마크다운에 이미지를 삽입하는 완전한 워크플로우
    
    Args:
        korean_markdown: 한국어 마크다운 내용
        perplexity_file_path: Perplexity 원본 응답 JSON 파일 경로
        
    Returns:
        str: 이미지가 삽입된 한국어 마크다운
    """
    logger.info("🚀 새로운 간단한 Perplexity 이미지 시스템 시작!")
    
    try:
        # 1. Perplexity 원본 응답 로드
        with open(perplexity_file_path, 'r', encoding='utf-8') as f:
            perplexity_data = json.load(f)
        
        perplexity_content = perplexity_data['choices'][0]['message']['content']
        logger.info("✅ Perplexity 원본 응답 로드 완료")
        
        # 2. 영어 용어 추출
        english_terms = extract_english_terms_simple(perplexity_content)
        logger.info(f"✅ 영어 용어 추출 완료: {len(english_terms)}개")
        
        # 3. 이미지 검색
        term_images = search_images_simple(english_terms)
        logger.info(f"✅ 이미지 검색 완료: {len(term_images)}개")
        
        # 4. 이미지 삽입
        final_markdown = insert_images_simple(korean_markdown, term_images)
        logger.info("✅ 이미지 삽입 완료")
        
        return final_markdown
        
    except Exception as e:
        logger.error(f"❌ 간단한 이미지 시스템 오류: {e}")
        return korean_markdown 