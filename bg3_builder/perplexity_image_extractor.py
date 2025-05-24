#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from .utils import logger
from .wiki_image_parser import get_image_url_from_wiki

class PerplexityImageExtractor:
    """Perplexity 원본 응답에서 영어 BG3 용어를 추출하고 이미지를 가져오는 시스템"""
    
    def __init__(self):
        # Perplexity에서 자주 나오는 BG3 용어 패턴들
        self.bg3_patterns = [
            # 괄호 안의 영문명: 썬더웨이브(Thunderwave)
            r'[가-힣\s]+\(([A-Z][A-Za-z\s\'\-]+)\)',
            
            # 영문명 직접 언급: **Thunderwave**, Lightning Bolt 등
            r'\*\*([A-Z][A-Za-z\s\'\-]+)\*\*',
            
            # 콜론 후 영문명: **주문:** 썬더웨이브(Thunderwave)
            r':\s*[가-힣\s]*\(([A-Z][A-Za-z\s\'\-]+)\)',
            
            # 단독 영문명 (The Blood of Lathander 같은)
            r'\b(The\s+[A-Z][A-Za-z\s\'\-]+)\b',
            r'\b([A-Z][a-z]+\s+of\s+[A-Z][A-Za-z\s\'\-]+)\b',
            
            # 일반 BG3 용어 패턴
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b',
            
            # 특수 형태들
            r'([A-Z][A-Za-z\'\-]+(?:\s+[A-Z][A-Za-z\'\-]+)*)\s*\[?\d*\]?'
        ]
        
        # 제외할 일반적인 단어들
        self.excluded_words = {
            'general': ['Game', 'Build', 'Guide', 'Level', 'Act', 'Patch', 'Steam', 'Forum', 
                       'User', 'Community', 'Expert', 'Professional', 'Best', 'Top', 'Main'],
            'korean': ['기준', '적용', '이유', '무료', '획득', '민첩', '매력', '장점', '단점', 
                      '콤보', '강화', '활용', '우선순위', '최적화', '기반'],
            'numbers': ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA', 'AC', 'DC']
        }
    
    def extract_english_terms_from_perplexity(self, perplexity_content):
        """Perplexity 응답에서 영어 BG3 용어들을 추출"""
        logger.info("🔍 Perplexity 응답에서 영어 BG3 용어 추출 시작")
        
        all_terms = set()
        extraction_stats = {}
        
        for i, pattern in enumerate(self.bg3_patterns, 1):
            matches = re.findall(pattern, perplexity_content, re.MULTILINE)
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
                "terms": valid_matches[:5]  # 샘플만
            }
            
            logger.info(f"패턴 {i}: {len(valid_matches)}/{len(matches)} 유효")
        
        logger.info(f"총 추출된 영어 용어: {len(all_terms)}개")
        
        # 추출된 용어들 로깅
        if all_terms:
            sorted_terms = sorted(all_terms)
            logger.info(f"추출된 BG3 용어들: {', '.join(sorted_terms[:15])}...")
        
        return list(all_terms), extraction_stats
    
    def is_valid_bg3_term(self, term):
        """BG3 관련 유효한 용어인지 검증"""
        # 길이 체크
        if len(term) < 3 or len(term) > 40:
            return False
        
        # 제외 단어 체크
        term_words = term.split()
        for word in term_words:
            for category, excluded in self.excluded_words.items():
                if word in excluded:
                    return False
        
        # 숫자만 있는 경우 제외
        if term.isdigit():
            return False
        
        # 한글이 포함된 경우 제외 (영어만)
        if re.search(r'[가-힣]', term):
            return False
        
        # 특수문자 과다 제외
        special_chars = len(re.findall(r'[^A-Za-z\s\'\-]', term))
        if special_chars > 2:
            return False
        
        # BG3스러운 패턴 체크
        # 1. 첫 글자 대문자 + 적절한 길이
        if re.match(r'^[A-Z][a-z]', term) and len(term) > 4:
            return True
        
        # 2. "The X of Y" 패턴
        if re.match(r'^The\s+[A-Z][a-z]+\s+of\s+[A-Z]', term):
            return True
        
        # 3. 복합 단어 (Lightning Bolt, Magic Missile 등)
        if len(term_words) >= 2 and all(word[0].isupper() for word in term_words):
            return True
        
        return False
    
    def search_images_for_terms(self, terms):
        """추출된 용어들에 대해 이미지 검색"""
        logger.info(f"🖼️ {len(terms)}개 용어에 대한 이미지 검색 시작")
        
        term_image_mapping = {}
        successful_searches = 0
        
        for i, term in enumerate(terms, 1):
            logger.info(f"[{i}/{len(terms)}] '{term}' 이미지 검색 중...")
            
            # 다중 검색 전략
            search_variants = [
                term,  # 원본
                term.replace(' ', '_'),  # 공백을 언더스코어로
                term.lower(),  # 소문자
                term.title(),  # 타이틀 케이스
                term.replace("'", ""),  # 어포스트로피 제거
                term.replace("-", " "),  # 하이픈을 공백으로
            ]
            
            # 복합 단어인 경우 첫 번째 단어도 시도
            words = term.split()
            if len(words) > 1:
                search_variants.append(words[0])
                search_variants.append(words[-1])  # 마지막 단어도
            
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
    
    def insert_images_into_korean_markdown(self, korean_markdown, term_image_mapping):
        """한국어 마크다운에 영어 용어 기반 이미지 삽입"""
        logger.info("🖼️ 한국어 마크다운에 이미지 삽입 시작")
        
        content = korean_markdown
        inserted_count = 0
        
        for term, image_url in term_image_mapping.items():
            if not image_url:
                continue
            
            # 한국어 텍스트에서 영어 용어 찾기 (다양한 패턴)
            search_patterns = [
                # 괄호 안의 영문명
                rf'\(({re.escape(term)})\)',
                # 강조된 영문명
                rf'\*\*{re.escape(term)}\*\*',
                # 일반 텍스트
                rf'\b{re.escape(term)}\b',
                # 이탤릭
                rf'_{re.escape(term)}_',
                # 코드 블록
                rf'`{re.escape(term)}`'
            ]
            
            for pattern in search_patterns:
                if re.search(pattern, content):
                    # 이미지 마크다운 생성
                    img_markdown = f'<img src="{image_url}" alt="{term}" title="{term}" style="margin-right: 10px; vertical-align: middle;" style="width: 120px;">'
                    
                    # 첫 번째 매칭에만 이미지 삽입
                    content = re.sub(pattern, f'{img_markdown}\n\n\\g<0>', content, count=1)
                    inserted_count += 1
                    logger.info(f"✅ 이미지 삽입 완료: {term}")
                    break
        
        logger.info(f"총 {inserted_count}개 이미지 삽입 완료")
        return content

def process_perplexity_based_images(perplexity_raw_response, korean_markdown):
    """Perplexity 기반 동적 이미지 처리 시스템"""
    logger.info("🚀 Perplexity 기반 동적 이미지 시스템 시작")
    
    try:
        # 1. Perplexity 응답에서 컨텐츠 추출
        if isinstance(perplexity_raw_response, str):
            # JSON 문자열인 경우 파싱
            perplexity_data = json.loads(perplexity_raw_response)
        else:
            # 이미 딕셔너리인 경우
            perplexity_data = perplexity_raw_response
        
        # content 추출
        perplexity_content = perplexity_data['choices'][0]['message']['content']
        logger.info(f"Perplexity 응답 길이: {len(perplexity_content):,} 문자")
        
        # 2. 영어 용어 추출
        extractor = PerplexityImageExtractor()
        terms, stats = extractor.extract_english_terms_from_perplexity(perplexity_content)
        
        if not terms:
            logger.warning("추출된 BG3 용어가 없습니다")
            return korean_markdown
        
        # 3. 이미지 검색
        term_image_mapping = extractor.search_images_for_terms(terms)
        
        # 4. 한국어 마크다운에 이미지 삽입
        final_content = extractor.insert_images_into_korean_markdown(korean_markdown, term_image_mapping)
        
        logger.info("🎯 Perplexity 기반 동적 이미지 시스템 완료")
        return final_content
        
    except Exception as e:
        logger.error(f"Perplexity 기반 이미지 처리 중 오류: {e}")
        return korean_markdown 