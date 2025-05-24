#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from .utils import logger
from .wiki_image_parser import get_image_url_from_wiki

class EnhancedPerplexityExtractor:
    """완전 개선된 Perplexity 기반 BG3 용어 추출 및 이미지 시스템"""
    
    def __init__(self):
        # 강화된 BG3 용어 추출 패턴들
        self.bg3_patterns = [
            # 1. 괄호 안의 영문명 (가장 정확한 패턴)
            r'[가-힣\s]+\s*\(([A-Z][A-Za-z\s\'\-&]+)\)',
            
            # 2. 콜론 뒤의 영문명들
            r':\s*([A-Z][A-Za-z\s\'\-&]+(?:\s*\([A-Z][A-Za-z\s]+\))?)',
            
            # 3. BG3 특화 장비명 패턴 (of, the 포함)
            r'\b((?:The\s+)?[A-Z][a-z]+(?:\s+of\s+[A-Z][a-z]+)+)\b',
            r'\b([A-Z][a-z]+\s+(?:Splint\s+)?Armor)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Staff|Helm|Boots|Cloak|Ring|Amulet))\b',
            
            # 4. BG3 주문명 패턴들 
            r'\b([A-Z][a-z]+\s+(?:Wounds|Word|Flame|Guardians|Ward|Strike|Intervention|Feast))\b',
            r'\b((?:Mass\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Word|Wounds))\b',
            r'\b([A-Z][a-z]+\s+(?:Domain|Dwarf|Artisan|Caster))\b',
            
            # 5. 일반 BG3 용어 (2-4 단어)
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b',
            
            # 6. 능력치 및 스킬
            r'\b(Guidance|Resistance|Bless|Aid)\b',
        ]
        
        # 제외할 단어들 (더 정교하게)
        self.excluded_terms = {
            'general': ['Game', 'Build', 'Guide', 'Level', 'Act', 'Patch', 'User', 'Community', 
                       'Expert', 'Best', 'Top', 'Main', 'New', 'Latest', 'Update', 'Version'],
            'korean': ['기준', '적용', '이유', '무료', '획득', '기반', '사용', '효과', '상황'],
            'numbers': ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA', 'AC', 'DC'],
            'common': ['This', 'That', 'With', 'From', 'When', 'Where', 'What', 'How', 'Why']
        }
        
        # BG3 확실한 용어들 (높은 우선순위)
        self.bg3_confirmed_terms = {
            'spells': ['Guidance', 'Resistance', 'Cure Wounds', 'Bless', 'Healing Word', 'Aid', 
                      'Spiritual Weapon', 'Sacred Flame', 'Spirit Guardians', 'Mass Healing Word',
                      'Death Ward', 'Storm Sphere', 'Divine Strike', 'Mass Cure Wounds', 
                      'Divine Intervention', 'Heroes Feast'],
            'equipment': ['Adamantine Splint Armor', 'Amulet of Greater Health', 'Staff of Arcane Blessing',
                         'Helm of Brilliance', 'Boots of Reactionary Defense', 'Cloak of Protection',
                         'Ring of Regeneration'],
            'classes': ['Life Domain', 'Shield Dwarf', 'Guild Artisan', 'War Caster'],
            'abilities': ['Preserve Life', 'Channel Divinity']
        }
    
    def extract_bg3_terms_from_perplexity(self, perplexity_content):
        """강화된 BG3 용어 추출"""
        logger.info("🔍 강화된 Perplexity BG3 용어 추출 시작")
        
        all_terms = set()
        priority_terms = set()
        extraction_stats = {}
        
        # 1. 확실한 BG3 용어들 먼저 찾기
        for category, terms in self.bg3_confirmed_terms.items():
            for term in terms:
                if term in perplexity_content:
                    priority_terms.add(term)
                    logger.info(f"✅ 확인된 BG3 용어 발견: {term}")
        
        # 2. 패턴 기반 추출
        for i, pattern in enumerate(self.bg3_patterns, 1):
            matches = re.findall(pattern, perplexity_content, re.MULTILINE | re.IGNORECASE)
            valid_matches = []
            
            for match in matches:
                if isinstance(match, tuple):
                    term = match[0] if match[0] else (match[1] if len(match) > 1 else '')
                else:
                    term = match
                
                term = term.strip()
                
                # 유효성 검증
                if self.is_valid_bg3_term(term):
                    all_terms.add(term)
                    valid_matches.append(term)
            
            extraction_stats[f"패턴_{i}"] = {
                "total": len(matches),
                "valid": len(valid_matches),
                "sample": valid_matches[:3]
            }
            
            logger.info(f"패턴 {i}: {len(valid_matches)}/{len(matches)} 유효")
        
        # 3. 우선순위 용어와 일반 용어 합치기
        final_terms = list(priority_terms) + [term for term in all_terms if term not in priority_terms]
        
        logger.info(f"총 추출된 BG3 용어: {len(final_terms)}개 (우선순위: {len(priority_terms)}개)")
        
        if final_terms:
            logger.info(f"샘플 용어들: {', '.join(final_terms[:10])}...")
        
        return final_terms, extraction_stats
    
    def is_valid_bg3_term(self, term):
        """개선된 BG3 용어 검증"""
        # 길이 체크
        if len(term) < 3 or len(term) > 50:
            return False
        
        # 제외 단어 체크
        for category, excluded in self.excluded_terms.items():
            if term in excluded:
                return False
        
        # 숫자만 있는 경우 제외
        if term.isdigit() or re.match(r'^\d+$', term):
            return False
        
        # 한글 포함 제외
        if re.search(r'[가-힣]', term):
            return False
        
        # 너무 많은 특수문자 제외
        special_chars = len(re.findall(r'[^A-Za-z\s\'\-&]', term))
        if special_chars > 2:
            return False
        
        # BG3 스러운 패턴들
        # 1. 확실한 BG3 용어
        for category, terms in self.bg3_confirmed_terms.items():
            if term in terms:
                return True
        
        # 2. 첫 글자 대문자 + 적절한 길이
        if re.match(r'^[A-Z][a-z]', term) and len(term) >= 4:
            return True
        
        # 3. "X of Y" 패턴
        if re.match(r'^[A-Z][a-z]+\s+of\s+[A-Z]', term):
            return True
        
        # 4. 복합 단어 (모든 단어가 대문자로 시작)
        words = term.split()
        if len(words) >= 2 and all(word[0].isupper() for word in words if len(word) > 0):
            return True
        
        return False
    
    def search_images_with_enhanced_strategy(self, terms):
        """강화된 다중 전략 이미지 검색"""
        logger.info(f"🖼️ {len(terms)}개 용어에 대한 강화된 이미지 검색 시작")
        
        term_image_mapping = {}
        successful_searches = 0
        
        for i, term in enumerate(terms, 1):
            logger.info(f"[{i}/{len(terms)}] '{term}' 이미지 검색 중...")
            
            # 확장된 검색 전략
            search_variants = [
                term,                               # 원본
                term.replace(' ', '_'),             # 공백 → 언더스코어
                term.replace(' ', ''),              # 공백 제거
                term.lower(),                       # 소문자
                term.title(),                       # 타이틀 케이스
                term.replace("'", ""),              # 어포스트로피 제거
                term.replace("-", " "),             # 하이픈 → 공백
                term.replace("&", "and"),           # & → and
            ]
            
            # 복합 단어 분해 전략
            words = term.split()
            if len(words) > 1:
                # 각 단어별로 시도
                for word in words:
                    if len(word) > 3:  # 의미있는 단어만
                        search_variants.append(word)
                
                # 마지막 단어 (보통 아이템 타입)
                if len(words[-1]) > 3:
                    search_variants.append(words[-1])
                
                # 첫 번째 + 마지막 단어 조합
                if len(words) > 2:
                    search_variants.append(f"{words[0]} {words[-1]}")
            
            # 중복 제거
            search_variants = list(dict.fromkeys(search_variants))
            
            image_url = None
            for variant in search_variants:
                if variant and len(variant) > 2:
                    image_url = get_image_url_from_wiki(variant)
                    if image_url:
                        logger.info(f"✅ 이미지 발견 ('{variant}'): {term}")
                        break
            
            if image_url:
                term_image_mapping[term] = image_url
                successful_searches += 1
            else:
                logger.info(f"❌ 이미지 없음: {term}")
        
        success_rate = (successful_searches / len(terms)) * 100 if terms else 0
        logger.info(f"이미지 검색 완료: {successful_searches}/{len(terms)} 성공 ({success_rate:.1f}%)")
        
        return term_image_mapping
    
    def insert_styled_images_into_markdown(self, korean_markdown, term_image_mapping):
        """일관된 스타일링으로 이미지 삽입"""
        logger.info("🖼️ 일관된 스타일링으로 마크다운에 이미지 삽입 시작")
        
        content = korean_markdown
        inserted_count = 0
        
        # 일관된 이미지 스타일
        def create_styled_image(image_url, term):
            return (
                f'<img src="{image_url}" '
                f'alt="{term}" '
                f'title="{term}" '
                f'style="width: 64px; height: 64px; '
                f'object-fit: cover; '
                f'border: 2px solid #8B4513; '
                f'border-radius: 8px; '
                f'margin: 0 8px 4px 0; '
                f'vertical-align: middle; '
                f'box-shadow: 0 2px 4px rgba(0,0,0,0.3);">'
            )
        
        for term, image_url in term_image_mapping.items():
            if not image_url:
                continue
            
            # 다양한 패턴으로 용어 찾기
            search_patterns = [
                # 괄호 안의 영문명
                rf'\(({re.escape(term)})\)',
                # 강조된 영문명 
                rf'\*\*{re.escape(term)}\*\*',
                # 일반 텍스트 (단어 경계 사용)
                rf'\b{re.escape(term)}\b',
                # 이탤릭
                rf'_{re.escape(term)}_',
                # 코드 블록
                rf'`{re.escape(term)}`',
                # 리스트 항목
                rf'[-*]\s*\*\*{re.escape(term)}\*\*'
            ]
            
            for pattern in search_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                match_found = False
                
                for match in matches:
                    # 첫 번째 매칭에만 이미지 삽입
                    styled_img = create_styled_image(image_url, term)
                    
                    # 매칭된 텍스트 앞에 이미지 삽입
                    start_pos = match.start()
                    content = content[:start_pos] + styled_img + '\n\n' + content[start_pos:]
                    inserted_count += 1
                    logger.info(f"✅ 스타일링된 이미지 삽입: {term}")
                    match_found = True
                    break
                
                if match_found:
                    break
        
        logger.info(f"총 {inserted_count}개 일관된 스타일의 이미지 삽입 완료")
        return content

def process_enhanced_perplexity_images(perplexity_raw_response, korean_markdown):
    """완전 강화된 Perplexity 기반 이미지 처리 시스템"""
    logger.info("🚀 완전 강화된 Perplexity 이미지 시스템 시작")
    
    try:
        # 1. Perplexity 응답에서 컨텐츠 추출
        if isinstance(perplexity_raw_response, str):
            perplexity_data = json.loads(perplexity_raw_response)
        else:
            perplexity_data = perplexity_raw_response
        
        perplexity_content = perplexity_data['choices'][0]['message']['content']
        logger.info(f"Perplexity 응답 길이: {len(perplexity_content):,} 문자")
        
        # 2. 강화된 영어 용어 추출
        extractor = EnhancedPerplexityExtractor()
        terms, stats = extractor.extract_bg3_terms_from_perplexity(perplexity_content)
        
        if not terms:
            logger.warning("추출된 BG3 용어가 없습니다")
            return korean_markdown
        
        # 3. 강화된 이미지 검색
        term_image_mapping = extractor.search_images_with_enhanced_strategy(terms)
        
        # 4. 일관된 스타일로 이미지 삽입
        final_content = extractor.insert_styled_images_into_markdown(korean_markdown, term_image_mapping)
        
        logger.info("🎯 완전 강화된 Perplexity 이미지 시스템 완료")
        return final_content
        
    except Exception as e:
        logger.error(f"강화된 Perplexity 이미지 처리 중 오류: {e}")
        return korean_markdown 