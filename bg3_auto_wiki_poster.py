#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Baldur's Gate 3 빌드 가이드 자동 생성 및 블로그 포스팅 도구
"""

import os
import re
import argparse
import time
from datetime import datetime

# bg3_builder 패키지 모듈 가져오기
from bg3_builder.utils import setup_logging, save_to_markdown
from bg3_builder.build_fetcher import get_build_info, create_korean_blog_post
from bg3_builder.wiki_image_parser import insert_images_to_markdown
from bg3_builder.youtube_fetcher import add_youtube_thumbnail_to_markdown
from bg3_builder.markdown_inserter import enhance_markdown_content
from bg3_builder.ghost_uploader import post_to_ghost_blog

# 로거 설정
logger = setup_logging(level='INFO')

def get_user_input():
    """사용자로부터 빌드명 입력 받기"""
    print("=" * 50)
    print("🔥 Baldur's Gate 3 빌드 공략 자동 생성기 🔥")
    print("=" * 50)
    print("원하는 빌드명을 입력해주세요. (예: Storm Sorcerer, 투척바바, 검바드)")
    print("-" * 50)
    
    build_name = input("빌드명: ").strip()
    
    if not build_name:
        build_name = "Storm Sorcerer"  # 기본값
        print(f"빌드명이 입력되지 않아 기본값 '{build_name}'으로 설정됩니다.")
    
    return build_name

def extract_title(content):
    """마크다운 내용에서 제목 추출"""
    title_match = re.search(r'^# (.*?)$', content, re.MULTILINE)
    return title_match.group(1) if title_match else None

def automate_build_guide(build_name, output_dir=None, post_to_blog=True, test_mode=False):
    """빌드 가이드 자동 생성 프로세스"""
    logger.info(f"🔥 BG3 {build_name} 빌드 공략 자동 생성기 시작!")
    start_time = time.time()
    result = {}
    
    try:
        # 1단계: 테스트 모드 확인
        if test_mode:
            logger.info("테스트 모드 활성화: API 호출 건너뛰기")
            build_info = "테스트 빌드 정보입니다. 실제 API 호출은 생략합니다."
            korean_blog_post = f"""
# 발더스 게이트 3 {build_name} 빌드 가이드

이 가이드는 테스트 모드에서 생성된 더미 데이터입니다.

## 스탯 배분
- **STR**: 16
- **DEX**: 12
- **CON**: 14
- **INT**: 10
- **WIS**: 8
- **CHA**: 16

## 추천 스킬
- **신성한 강타(Divine Smite)**: 강력한 추가 피해를 줍니다.
- **축복(Bless)**: 아군에게 버프를 제공합니다.
- **Healing Word**: 원거리에서 아군을 빠르게 치유합니다.
"""
        else:
            # 2단계: Perplexity API를 통해 빌드 정보 수집
            logger.info("🔍 빌드 정보 수집 단계 시작...")
            build_info = get_build_info(build_name)
            if not build_info:
                logger.error("빌드 정보 수집 실패. 프로그램을 종료합니다.")
                return None
            
            # 3단계: Grok API를 통해 한국어 블로그 포스트 생성
            logger.info("🌐 한글 번역 및 포스트 생성 단계 시작...")
            korean_blog_post = create_korean_blog_post(build_info, build_name)
            if not korean_blog_post:
                logger.error("블로그 포스트 생성 실패. 프로그램을 종료합니다.")
                return None
        
        # 4단계: 콘텐츠 강화 (요약 카드, 전투 루틴 추가)
        logger.info("💪 콘텐츠 강화 단계 시작...")
        enhanced_content = enhance_markdown_content(korean_blog_post, build_name)
        
        # 5단계: 이미지 삽입 (위키 이미지, 나무위키 헤더 등)
        logger.info("🖼️ 이미지 추가 단계 시작...")
        content_with_images = insert_images_to_markdown(enhanced_content)
        
        # 6단계: YouTube 썸네일 추가
        logger.info("📺 YouTube 썸네일 추가 단계 시작...")
        final_content = add_youtube_thumbnail_to_markdown(content_with_images, build_name)
        
        # 7단계: 마크다운 파일로 저장
        logger.info("💾 마크다운 파일 저장 단계 시작...")
        saved_file = save_to_markdown(final_content, build_name, output_dir)
        result["file"] = saved_file
        
        # 8단계: Ghost 블로그에 포스팅 (옵션)
        if post_to_blog:
            logger.info("📤 Ghost 블로그 포스팅 단계 시작...")
            # 제목 추출
            title = extract_title(final_content) or f"BG3 {build_name} 빌드 가이드"
            
            # 태그 생성
            tags = ["bg3", "공략", "빌드", build_name]
            
            # 포스팅
            post_url = post_to_ghost_blog(title, final_content, build_name, tags)
            if post_url:
                result["url"] = post_url
            else:
                logger.warning("블로그 포스팅에 실패했습니다.")
        
        # 실행 시간 계산
        execution_time = time.time() - start_time
        logger.info(f"✅ 총 실행 시간: {execution_time:.2f}초")
        
        # 성공 메시지
        if saved_file:
            logger.info(f"✅ '{saved_file}' 파일에 BG3 {build_name} 빌드 공략이 저장되었습니다.")
        if post_to_blog and result.get("url"):
            logger.info(f"✅ Ghost 블로그 포스팅 URL: {result['url']}")
        
        return result
    
    except Exception as e:
        logger.error(f"🔴 예상치 못한 오류 발생: {e}", exc_info=True)
        return None

def main():
    """커맨드 라인 인터페이스"""
    # 커맨드 라인 아규먼트 설정
    parser = argparse.ArgumentParser(description='Baldur\'s Gate 3 빌드 공략 자동 생성 및 블로그 포스팅 도구')
    parser.add_argument('--build', type=str, help='빌드 이름 (예: Storm Sorcerer, 투척바바, 검바드)')
    parser.add_argument('--output-dir', type=str, help='결과 마크다운 저장 디렉토리')
    parser.add_argument('--no-post', action='store_true', help='블로그 포스팅 건너뛰기')
    parser.add_argument('--debug', action='store_true', help='디버그 로그 출력')
    parser.add_argument('--test', action='store_true', help='테스트 모드 (API 호출 없이 더미 데이터 사용)')
    
    args = parser.parse_args()
    
    # 디버그 모드 설정
    if args.debug:
        setup_logging(level='DEBUG')
        logger.debug("디버그 모드 활성화")
    
    # 빌드 이름 설정 (커맨드 라인에서 가져오거나 사용자 입력 받기)
    build_name = args.build if args.build else get_user_input()
    
    # 메인 함수 호출
    result = automate_build_guide(
        build_name=build_name,
        output_dir=args.output_dir,
        post_to_blog=not args.no_post,
        test_mode=args.test
    )
    
    # 결과에 따른 종료 코드 설정
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 