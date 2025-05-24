#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from .skill_extractor import extract_bg3_terms_from_source, create_term_mapping, get_image_search_terms
from .wiki_image_parser import get_image_url_from_wiki
from .utils import logger

def process_images_with_source_accuracy(english_build_info, korean_content):
    """
    Perplexity 원본 데이터를 기반으로 정확한 이미지 처리
    
    Args:
        english_build_info: Perplexity에서 받은 원본 영어 빌드 정보
        korean_content: 번역된 한국어 마크다운 내용
        
    Returns:
        str: 이미지가 삽입된 최종 마크다운 내용
    """
    logger.info("🔍 원본 소스 기반 정확한 이미지 처리 시작")
    
    # 1. 원본 영어 정보에서 정확한 BG3 용어들 추출
    logger.info("1️⃣ 원본 영어 빌드 정보에서 BG3 용어 추출...")
    extracted_terms = extract_bg3_terms_from_source(english_build_info)
    
    # 2. 영어-한국어 용어 매핑 생성
    logger.info("2️⃣ 영어-한국어 용어 매핑 생성...")
    term_mapping = create_term_mapping(extracted_terms, korean_content)
    
    # 3. 우선순위 기반 이미지 검색 용어 리스트 생성
    logger.info("3️⃣ 우선순위 기반 이미지 검색 용어 생성...")
    search_terms = get_image_search_terms(extracted_terms)
    
    # 4. 각 용어별 이미지 검색 및 수집
    logger.info("4️⃣ 정확한 영문명으로 이미지 검색 중...")
    image_collection = {}
    search_success = 0
    
    for term in search_terms[:20]:  # 상위 20개로 제한
        logger.info(f"'{term}' 이미지 검색 중...")
        
        img_url = get_image_url_from_wiki(term)
        if img_url:
            korean_name = term_mapping.get(term, term)  # 한국어명이 있으면 사용, 없으면 영어명
            
            image_collection[term] = {
                'url': img_url,
                'korean_name': korean_name,
                'search_confidence': 'high'  # 원본에서 추출했으므로 높은 신뢰도
            }
            search_success += 1
            logger.info(f"✅ {term}: 이미지 발견 (한국어: {korean_name})")
        else:
            logger.warning(f"❌ {term}: 이미지 찾지 못함")
        
        # API 요청 제한 준수
        time.sleep(0.8)
    
    search_rate = (search_success / len(search_terms[:20])) * 100 if search_terms else 0
    logger.info(f"이미지 검색 완료: {search_success}/{len(search_terms[:20])} 성공 ({search_rate:.1f}%)")
    
    # 5. 마크다운에 이미지 삽입
    logger.info("5️⃣ 마크다운에 이미지 삽입 중...")
    final_content = insert_images_to_korean_content(korean_content, image_collection, term_mapping)
    
    # 6. BG3 헤더 이미지 추가
    final_content = add_bg3_header_image(final_content)
    
    logger.info(f"🎯 정확도 개선 이미지 처리 완료 - {len(image_collection)}개 이미지 삽입")
    
    return final_content

def insert_images_to_korean_content(korean_content, image_collection, term_mapping):
    """
    한국어 콘텐츠에 정확한 이미지들을 삽입
    
    Args:
        korean_content: 한국어 마크다운 내용
        image_collection: 수집된 이미지 정보
        term_mapping: 영어-한국어 용어 매핑
        
    Returns:
        str: 이미지가 삽입된 마크다운 내용
    """
    import re
    
    lines = korean_content.split('\n')
    new_content = []
    inserted_images = set()
    
    # 역매핑 생성 (한국어 → 영어)
    reverse_mapping = {v: k for k, v in term_mapping.items()}
    
    for line in lines:
        line_modified = False
        
        # 한국어 용어들과 매치해서 이미지 삽입
        for korean_term, english_term in reverse_mapping.items():
            if english_term in image_collection and english_term not in inserted_images:
                # 한국어 용어가 라인에 포함되어 있고, 강조 표시되어 있는 경우
                if korean_term in line and ('**' in line or '*' in line):
                    img_info = image_collection[english_term]
                    
                    # 이미지 태그 생성
                    img_markdown = (
                        f"<img src=\"{img_info['url']}\" "
                        f"alt=\"{english_term}\" "
                        f"title=\"{korean_term}\" "
                        f"width=\"120\" "
                        f"style=\"margin-right: 10px; vertical-align: middle;\">"
                    )
                    
                    # 이미지를 라인 앞에 추가
                    new_content.append(img_markdown)
                    new_content.append(line)
                    
                    inserted_images.add(english_term)
                    line_modified = True
                    logger.debug(f"🖼️ 이미지 삽입: {korean_term} ({english_term})")
                    break
        
        # 영어 용어가 직접 나타나는 경우도 체크
        if not line_modified:
            for english_term in image_collection:
                if english_term in line and english_term not in inserted_images:
                    if '**' in line or '*' in line:
                        img_info = image_collection[english_term]
                        
                        img_markdown = (
                            f"<img src=\"{img_info['url']}\" "
                            f"alt=\"{english_term}\" "
                            f"title=\"{img_info['korean_name']}\" "
                            f"width=\"120\" "
                            f"style=\"margin-right: 10px; vertical-align: middle;\">"
                        )
                        
                        new_content.append(img_markdown)
                        new_content.append(line)
                        
                        inserted_images.add(english_term)
                        line_modified = True
                        logger.debug(f"🖼️ 이미지 삽입: {english_term}")
                        break
        
        # 이미지가 추가되지 않은 경우에만 원래 라인 추가
        if not line_modified:
            new_content.append(line)
    
    logger.info(f"이미지 삽입 완료: {len(inserted_images)}개 삽입됨")
    
    return '\n'.join(new_content)

def add_bg3_header_image(content):
    """BG3 헤더 이미지 추가"""
    header_image = "https://i.namu.wiki/i/IxWGCIu4G78HZv1d2AU_C5taEO8i-iT_aEbh5YbPAz73yIS3gFGB-Fj6EvL4Z-jmjcFIvWhr2XOxN0-sdmH31g.webp"
    header_markdown = f"<img src=\"{header_image}\" alt=\"BG3 헤더 이미지\" width=\"100%\" style=\"margin-bottom: 20px;\">\n\n"
    
    # 첫 번째 제목 찾아서 위에 헤더 이미지 삽입
    import re
    first_heading = re.search(r'^#\s+.*$', content, re.MULTILINE)
    if first_heading:
        heading_pos = first_heading.start()
        content = content[:heading_pos] + header_markdown + content[heading_pos:]
    else:
        content = header_markdown + content
    
    return content

def save_extraction_results(build_name, extracted_terms, image_collection):
    """추출 결과를 JSON으로 저장 (디버깅용)"""
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"extraction_results_{build_name.replace(' ', '_')}_{timestamp}.json"
    
    results = {
        "build_name": build_name,
        "timestamp": timestamp,
        "extracted_terms": extracted_terms,
        "image_collection": image_collection,
        "statistics": {
            "total_terms": sum(len(terms) for terms in extracted_terms.values()),
            "images_found": len(image_collection),
            "success_rate": len(image_collection) / sum(len(terms) for terms in extracted_terms.values()) * 100 if extracted_terms else 0
        }
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"추출 결과가 {filename}에 저장되었습니다.")
        return filename
    except Exception as e:
        logger.error(f"추출 결과 저장 중 오류: {e}")
        return None 