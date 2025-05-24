#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .build_fetcher import get_build_info, create_korean_blog_post
from .improved_image_system import process_images_with_source_accuracy
from .utils import logger
import json
from datetime import datetime

def create_build_with_accurate_images(build_name):
    """
    정확한 이미지 시스템을 사용하여 완전한 빌드 가이드 생성
    
    Args:
        build_name: 빌드명 (예: "Storm Sorcerer")
        
    Returns:
        tuple: (성공여부, 한국어_포스트_내용, 원본_영어_정보)
    """
    logger.info(f"🚀 정확한 이미지 시스템으로 {build_name} 빌드 가이드 생성 시작")
    
    try:
        # 1. Perplexity에서 원본 영어 빌드 정보 수집
        logger.info("1️⃣ Perplexity에서 원본 영어 빌드 정보 수집...")
        english_build_info = get_build_info(build_name)
        if not english_build_info:
            logger.error("영어 빌드 정보 수집 실패")
            return False, None, None
        
        # 2. Grok으로 한국어 번역
        logger.info("2️⃣ Grok으로 한국어 번역...")
        korean_blog_post = create_korean_blog_post(english_build_info, build_name)
        if not korean_blog_post:
            logger.error("한국어 번역 실패")
            return False, None, None
        
        # 3. 개선된 이미지 시스템 적용
        logger.info("3️⃣ 원본 기반 정확한 이미지 처리...")
        final_content = process_images_with_source_accuracy(english_build_info, korean_blog_post)
        
        # 4. 데이터 저장 (디버깅 및 추적용)
        logger.info("4️⃣ 완전한 빌드 데이터 저장...")
        save_accurate_build_data(build_name, english_build_info, korean_blog_post, final_content)
        
        logger.info("🎯 정확한 이미지 시스템으로 빌드 가이드 생성 완료!")
        return True, final_content, english_build_info
        
    except Exception as e:
        logger.error(f"빌드 가이드 생성 중 오류: {e}")
        return False, None, None

def save_accurate_build_data(build_name, english_info, korean_info, final_content):
    """빌드 정보를 완전한 형태로 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"accurate_build_data_{build_name.replace(' ', '_')}_{timestamp}.json"
    
    build_data = {
        "build_name": build_name,
        "timestamp": timestamp,
        "english_build_info": english_info,
        "korean_blog_post": korean_info,
        "final_content_with_images": final_content,
        "metadata": {
            "source": "perplexity_api", 
            "translator": "grok_api",
            "image_system": "accurate_source_based",
            "version": "3.0_accurate_images"
        }
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(build_data, f, ensure_ascii=False, indent=2)
        logger.info(f"완전한 빌드 데이터가 {filename}에 저장되었습니다.")
        return filename
    except Exception as e:
        logger.error(f"빌드 데이터 저장 중 오류: {e}")
        return None 