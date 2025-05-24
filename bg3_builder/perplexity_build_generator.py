#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from .build_fetcher import get_build_info, create_korean_blog_post
from .perplexity_image_extractor import process_perplexity_based_images
from .markdown_inserter import remove_existing_summary_cards
from .utils import logger

def create_build_with_perplexity_images(build_name):
    """
    Perplexity 원본 응답 기반 혁신적 이미지 시스템으로 빌드 가이드 생성
    
    Args:
        build_name: 빌드명 (예: "Storm Sorcerer", "Life Domain Cleric")
        
    Returns:
        tuple: (성공여부, 한국어_포스트_내용, Perplexity_원본_응답)
    """
    logger.info(f"🚀 Perplexity 기반 혁신적 이미지 시스템으로 {build_name} 빌드 가이드 생성 시작")
    
    try:
        # 1. Perplexity에서 원본 영어 빌드 정보 수집 및 원본 응답 저장
        logger.info("1️⃣ Perplexity에서 원본 영어 빌드 정보 수집...")
        
        # build_fetcher.py를 수정해서 원본 응답도 반환하도록 해야 함
        # 일단 현재는 기존 방식으로 진행
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
        
        # 3. 요약 카드 제거
        logger.info("3️⃣ 요약 카드 제거...")
        clean_korean_post = remove_existing_summary_cards(korean_blog_post)
        
        # 4. Perplexity 원본 응답이 있다면 로드 (테스트용)
        perplexity_raw_response = None
        try:
            with open('perplexity_raw_response_20250524_171613.json', 'r', encoding='utf-8') as f:
                perplexity_raw_response = json.load(f)
            logger.info("테스트용 Perplexity 원본 응답 로드 성공")
        except Exception as e:
            logger.warning(f"Perplexity 원본 응답 로드 실패: {e}")
            # 원본 응답이 없으면 영어 빌드 정보를 대신 사용
            perplexity_raw_response = {
                'choices': [{'message': {'content': english_build_info}}]
            }
        
        # 5. Perplexity 기반 동적 이미지 시스템 적용
        logger.info("5️⃣ Perplexity 기반 혁신적 이미지 시스템으로 이미지 처리...")
        final_content = process_perplexity_based_images(perplexity_raw_response, clean_korean_post)
        
        # 6. 완전한 빌드 데이터 저장 (디버깅 및 추적용)
        logger.info("6️⃣ 완전한 빌드 데이터 저장...")
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"perplexity_build_data_{build_name.replace(' ', '_')}_{timestamp}.json"
            
            build_data = {
                "build_name": build_name,
                "timestamp": timestamp,
                "english_build_info": english_build_info,
                "korean_blog_post": korean_blog_post,
                "clean_korean_post": clean_korean_post,
                "final_content_with_images": final_content,
                "perplexity_raw_response": perplexity_raw_response,
                "metadata": {
                    "source": "perplexity_api",
                    "translator": "grok_api", 
                    "image_system": "perplexity_based_extraction",
                    "version": "5.0_perplexity_images"
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(build_data, f, ensure_ascii=False, indent=2)
            logger.info(f"완전한 빌드 데이터가 {filename}에 저장되었습니다.")
        except Exception as e:
            logger.warning(f"데이터 저장 중 오류 (처리는 계속): {e}")
        
        logger.info("🎯 Perplexity 기반 혁신적 이미지 시스템으로 빌드 가이드 생성 완료!")
        return True, final_content, perplexity_raw_response
        
    except Exception as e:
        logger.error(f"빌드 가이드 생성 중 오류: {e}")
        return False, None, None

def create_build_with_existing_perplexity_response(build_name, perplexity_file_path):
    """
    기존 Perplexity 응답 파일을 사용하여 빌드 가이드 생성
    
    Args:
        build_name: 빌드명
        perplexity_file_path: Perplexity 원본 응답 JSON 파일 경로
        
    Returns:
        tuple: (성공여부, 한국어_포스트_내용, Perplexity_원본_응답)
    """
    logger.info(f"🚀 기존 Perplexity 응답으로 {build_name} 빌드 가이드 생성 시작")
    
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
        
        # 4. Perplexity 기반 동적 이미지 시스템 적용
        logger.info("4️⃣ Perplexity 기반 혁신적 이미지 시스템으로 이미지 처리...")
        final_content = process_perplexity_based_images(perplexity_raw_response, clean_korean_post)
        
        # 5. 완전한 빌드 데이터 저장
        logger.info("5️⃣ 완전한 빌드 데이터 저장...")
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"perplexity_build_data_{build_name.replace(' ', '_')}_{timestamp}.json"
            
            build_data = {
                "build_name": build_name,
                "timestamp": timestamp,
                "source_file": perplexity_file_path,
                "english_build_info": english_build_info,
                "korean_blog_post": korean_blog_post,
                "clean_korean_post": clean_korean_post,
                "final_content_with_images": final_content,
                "perplexity_raw_response": perplexity_raw_response,
                "metadata": {
                    "source": "perplexity_file",
                    "translator": "grok_api", 
                    "image_system": "perplexity_based_extraction",
                    "version": "5.0_perplexity_images"
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(build_data, f, ensure_ascii=False, indent=2)
            logger.info(f"완전한 빌드 데이터가 {filename}에 저장되었습니다.")
        except Exception as e:
            logger.warning(f"데이터 저장 중 오류 (처리는 계속): {e}")
        
        logger.info("🎯 기존 Perplexity 응답 기반 빌드 가이드 생성 완료!")
        return True, final_content, perplexity_raw_response
        
    except Exception as e:
        logger.error(f"빌드 가이드 생성 중 오류: {e}")
        return False, None, None 