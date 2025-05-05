#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Baldur's Gate 3 빌드 가이드 자동 생성기 - 메인 진입점
"""

import os
import sys
import time
from datetime import datetime
from bg3_auto_wiki_poster import automate_build_guide, get_user_input
from bg3_builder.utils import setup_logging

# 로거 설정
logger = setup_logging(level='INFO')

def show_header():
    """프로그램 헤더 표시"""
    print("\n" + "=" * 60)
    print("🔥 Baldur's Gate 3 빌드 가이드 자동 생성기 🔥".center(60))
    print("=" * 60)
    print("이 도구는 BG3 빌드 정보를 자동으로 수집하고 한글 가이드를 생성합니다.")
    print("사용한 AI API: Perplexity(수집), Grok(번역)")
    print("-" * 60)

def show_menu():
    """주 메뉴 표시"""
    print("\n메뉴를 선택하세요:")
    print("1. 빌드 가이드 생성")
    print("2. 빌드 가이드 생성 (블로그 포스팅 없이)")
    print("3. 테스트 모드 (API 호출 없음)")
    print("4. 프로그램 정보")
    print("0. 종료")
    print("-" * 30)
    
    try:
        choice = input("선택: ").strip()
        return choice
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        sys.exit(0)

def show_about():
    """프로그램 정보 표시"""
    print("\n" + "=" * 60)
    print("📖 프로그램 정보".center(60))
    print("=" * 60)
    print(" * 제작: Mins_coding_factory")
    print(" * 버전: 1.1.0")
    print(" * 빌드 날짜: 2025-05-04")
    print("\n기능:")
    print(" * BG3 빌드 정보 자동 수집 (Perplexity API)")
    print(" * 한글 빌드 가이드 생성 (Grok API)")
    print(" * 이미지 및 썸네일 자동 삽입")
    print(" * Ghost 블로그 자동 포스팅")
    print(" * 마크다운 파일 자동 저장")
    print("=" * 60)

def main():
    """메인 함수"""
    show_header()
    
    while True:
        choice = show_menu()
        
        if choice == "0":
            print("프로그램을 종료합니다. 감사합니다!")
            sys.exit(0)
        
        elif choice == "1":
            build_name = get_user_input()
            result = automate_build_guide(
                build_name=build_name,
                post_to_blog=True,
                test_mode=False
            )
            
            if result:
                print("\n✅ 작업이 완료되었습니다!")
                if "url" in result:
                    print(f"👉 블로그 URL: {result['url']}")
                print(f"👉 저장된 파일: {result['file']}")
            else:
                print("\n❌ 작업 중 오류가 발생했습니다.")
            
            input("\n계속하려면 Enter 키를 누르세요...")
        
        elif choice == "2":
            build_name = get_user_input()
            result = automate_build_guide(
                build_name=build_name,
                post_to_blog=False,
                test_mode=False
            )
            
            if result:
                print("\n✅ 작업이 완료되었습니다!")
                print(f"👉 저장된 파일: {result['file']}")
            else:
                print("\n❌ 작업 중 오류가 발생했습니다.")
            
            input("\n계속하려면 Enter 키를 누르세요...")
        
        elif choice == "3":
            build_name = get_user_input()
            result = automate_build_guide(
                build_name=build_name,
                post_to_blog=False,
                test_mode=True
            )
            
            if result:
                print("\n✅ 테스트가 완료되었습니다!")
                print(f"👉 저장된 파일: {result['file']}")
            else:
                print("\n❌ 테스트 중 오류가 발생했습니다.")
            
            input("\n계속하려면 Enter 키를 누르세요...")
        
        elif choice == "4":
            show_about()
            input("\n계속하려면 Enter 키를 누르세요...")
        
        else:
            print("올바른 메뉴를 선택해주세요.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}", exc_info=True)
        print(f"\n❌ 프로그램 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1) 