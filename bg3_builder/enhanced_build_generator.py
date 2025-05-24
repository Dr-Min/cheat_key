#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from .build_fetcher import get_build_info, create_korean_blog_post
from .enhanced_perplexity_extractor import process_enhanced_perplexity_images
from .markdown_inserter import remove_existing_summary_cards
from .utils import logger

def create_build_with_enhanced_perplexity_system(build_name, perplexity_file_path):
    """
    완전 강화된 Perplexity 시스템으로 빌드 가이드 생성
    
    Args:
        build_name: 빌드명
        perplexity_file_path: Perplexity 원본 응답 JSON 파일 경로
        
    Returns:
        tuple: (성공여부, 한국어_포스트_내용, 추출_통계)
    """
    logger.info(f"🚀 완전 강화된 Perplexity 시스템으로 {build_name} 빌드 가이드 생성 시작")
    
    try:
        # 1. Perplexity 원본 응답 로드
        logger.info(f"1️⃣ Perplexity 원본 응답 로드: {perplexity_file_path}")
        with open(perplexity_file_path, 'r', encoding='utf-8') as f:
            perplexity_raw_response = json.load(f)
        
        # 원본 영어 콘텐츠 추출
        english_build_info = perplexity_raw_response['choices'][0]['message']['content']
        logger.info(f"원본 영어 콘텐츠 길이: {len(english_build_info):,} 문자")
        
        # 2. Grok으로 한국어 번역
        logger.info("2️⃣ Grok으로 한국어 번역...")
        korean_blog_post = create_korean_blog_post(english_build_info, build_name)
        if not korean_blog_post:
            logger.error("한국어 번역 실패")
            return False, None, None
        
        # 3. 요약 카드 제거
        logger.info("3️⃣ 요약 카드 제거...")
        clean_korean_post = remove_existing_summary_cards(korean_blog_post)
        
        # 4. 완전 강화된 Perplexity 이미지 시스템 적용
        logger.info("4️⃣ 완전 강화된 Perplexity 이미지 시스템으로 이미지 처리...")
        final_content = process_enhanced_perplexity_images(perplexity_raw_response, clean_korean_post)
        
        # 5. 완전한 빌드 데이터 저장
        logger.info("5️⃣ 완전한 빌드 데이터 저장...")
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_build_data_{build_name.replace(' ', '_')}_{timestamp}.json"
            
            # 이미지 삽입 통계 계산
            image_count = final_content.count('<img src=')
            content_length = len(final_content)
            
            build_data = {
                "build_name": build_name,
                "timestamp": timestamp,
                "source_file": perplexity_file_path,
                "english_build_info": english_build_info,
                "korean_blog_post": korean_blog_post,
                "clean_korean_post": clean_korean_post,
                "final_content_with_images": final_content,
                "perplexity_raw_response": perplexity_raw_response,
                "statistics": {
                    "images_inserted": image_count,
                    "content_length": content_length,
                    "enhancement_version": "6.0_enhanced_perplexity"
                },
                "metadata": {
                    "source": "perplexity_file", 
                    "translator": "grok_api",
                    "image_system": "enhanced_perplexity_extraction",
                    "version": "6.0_enhanced_system"
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(build_data, f, ensure_ascii=False, indent=2)
            logger.info(f"완전한 빌드 데이터가 {filename}에 저장되었습니다.")
            
            # 통계 로깅
            logger.info(f"📊 최종 통계:")
            logger.info(f"  - 이미지 삽입: {image_count}개")
            logger.info(f"  - 콘텐츠 길이: {content_length:,} 문자")
            
        except Exception as e:
            logger.warning(f"데이터 저장 중 오류 (처리는 계속): {e}")
        
        logger.info("🎯 완전 강화된 Perplexity 시스템으로 빌드 가이드 생성 완료!")
        return True, final_content, {"images": image_count, "length": content_length}
        
    except Exception as e:
        logger.error(f"빌드 가이드 생성 중 오류: {e}")
        return False, None, None 