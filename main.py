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
from bg3_builder.simple_build_generator import create_build_simple_system
from bg3_builder.ghost_uploader import post_to_ghost_blog

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
    print("1. 빌드 가이드 생성 (기존 시스템)")
    print("2. 빌드 가이드 생성 (블로그 포스팅 없이)")
    print("3. 🔥 NEW! 간단한 이미지 시스템 (Perplexity 파일 사용)")
    print("4. 🚀 NEW! 배치 자동 생성 시스템 (여러 빌드 한 번에)")
    print("5. 🔄 NEW! 자동 재개 시스템 (중단된 작업 이어서)")
    print("6. ⏰ NEW! 스케줄링 배치 시스템 (예약 발행)")
    print("7. 🧪 배치 시스템 테스트 (3개 빌드만)")
    print("8. 테스트 모드 (API 호출 없음)")
    print("9. 프로그램 정보")
    print("0. 종료")
    print("-" * 30)
    
    try:
        choice = input("선택: ").strip()
        return choice
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        sys.exit(0)

def batch_system_workflow():
    """배치 시스템 워크플로우"""
    print("\n" + "=" * 60)
    print("🚀 BG3 빌드 배치 자동 생성 시스템".center(60))
    print("=" * 60)
    
    from bg3_batch_generator import BG3BatchGenerator
    
    print("설정을 입력해주세요:")
    try:
        start_from = int(input("시작 인덱스 (0부터 시작, 기본값 0): ") or "0")
        max_builds_input = input("최대 빌드 수 (전체 처리하려면 엔터): ").strip()
        max_builds = int(max_builds_input) if max_builds_input else None
        delay = int(input("빌드 간 대기 시간(초, 기본값 30): ") or "30")
        
        print(f"\n📋 설정 확인:")
        print(f"  • 시작 인덱스: {start_from}")
        print(f"  • 최대 빌드 수: {max_builds or '전체'}")
        print(f"  • 대기 시간: {delay}초")
        
        confirm = input("\n계속 진행하시겠습니까? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes', '예', 'ㅇ']:
            print("작업을 취소했습니다.")
            return None
        
        # 배치 생성기 실행
        generator = BG3BatchGenerator(delay_between_builds=delay)
        result = generator.run_batch_generation(
            start_from=start_from,
            max_builds=max_builds,
            auto_post=True
        )
        
        return result
        
    except (ValueError, KeyboardInterrupt):
        print("작업을 취소했습니다.")
        return None

def batch_test_workflow():
    """배치 시스템 테스트 워크플로우"""
    print("\n" + "=" * 50)
    print("🧪 배치 시스템 테스트 (3개 빌드)".center(50))
    print("=" * 50)
    
    from bg3_batch_generator import BG3BatchGenerator
    
    confirm = input("\n첫 3개 빌드로 테스트를 시작하시겠습니까? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', '예', 'ㅇ']:
        print("테스트를 취소했습니다.")
        return None
    
    # 테스트 실행
    generator = BG3BatchGenerator(delay_between_builds=10)
    result = generator.run_batch_generation(
        start_from=0,
        max_builds=3,
        auto_post=True
    )
    
    return result

# 기존 함수들은 그대로 유지...
def get_perplexity_file():
    """Perplexity 파일 선택"""
    print("\n사용 가능한 Perplexity 파일:")
    perplexity_files = [f for f in os.listdir('.') if f.startswith('perplexity_raw_response_') and f.endswith('.json')]
    
    if not perplexity_files:
        print("❌ Perplexity 파일이 없습니다.")
        return None
    
    for i, file in enumerate(perplexity_files, 1):
        file_time = file.replace('perplexity_raw_response_', '').replace('.json', '')
        print(f"{i}. {file} ({file_time})")
    
    try:
        choice = int(input(f"\n파일 선택 (1-{len(perplexity_files)}): "))
        if 1 <= choice <= len(perplexity_files):
            return perplexity_files[choice - 1]
        else:
            print("올바른 번호를 선택해주세요.")
            return None
    except (ValueError, KeyboardInterrupt):
        print("올바른 번호를 입력해주세요.")
        return None

def simple_system_workflow():
    """간단한 시스템 워크플로우"""
    print("\n" + "=" * 50)
    print("🚀 간단한 Perplexity 이미지 시스템".center(50))
    print("=" * 50)
    
    # 빌드명 입력
    build_name = input("빌드명을 입력하세요: ").strip()
    if not build_name:
        print("❌ 빌드명을 입력해주세요.")
        return None
    
    # Perplexity 파일 선택
    perplexity_file = get_perplexity_file()
    if not perplexity_file:
        return None
    
    print(f"\n🔄 {build_name} 빌드 생성 중...")
    print(f"📁 사용 파일: {perplexity_file}")
    
    # 간단한 시스템으로 빌드 생성
    success, final_content, stats = create_build_simple_system(build_name, perplexity_file)
    
    if not success:
        print("❌ 빌드 생성 실패!")
        return None
    
    print("✅ 빌드 생성 성공!")
    print(f"📊 통계: 이미지 {stats['images']}개, 길이 {stats['length']:,}자")
    
    # Ghost 블로그 포스팅 여부 선택
    post_choice = input("\nGhost 블로그에 포스팅하시겠습니까? (y/n): ").strip().lower()
    
    if post_choice in ['y', 'yes', '예', 'ㅇ']:
        print("🔄 Ghost 블로그에 포스팅 중...")
        post_url = post_to_ghost_blog(
            title=f"[간단시스템] {build_name} 빌드 가이드",
            content=final_content,
            build_name=build_name,
            tags=["발더스게이트3", "간단시스템", "Perplexity", build_name.replace(" ", "")]
        )
        
        if post_url:
            print(f"🎯 포스팅 완료!")
            print(f"🔗 URL: {post_url}")
            return {"url": post_url, "stats": stats}
        else:
            print("❌ 포스팅 실패")
    
    return {"stats": stats}

def show_about():
    """프로그램 정보 표시"""
    print("\n" + "=" * 60)
    print("📖 프로그램 정보".center(60))
    print("=" * 60)
    print(" * 제작: Mins_coding_factory")
    print(" * 버전: 3.0.0 (배치 자동 생성 시스템 추가)")
    print(" * 빌드 날짜: 2025-05-24")
    print("\n기능:")
    print(" * BG3 빌드 정보 자동 수집 (Perplexity API)")
    print(" * 한글 빌드 가이드 생성 (Grok API)")
    print(" * 🔥 NEW! 간단한 이미지 시스템 (Perplexity 파일 기반)")
    print(" * 🚀 NEW! 배치 자동 생성 시스템 (90+ 빌드 자동 처리)")
    print(" * 이미지 및 썸네일 자동 삽입")
    print(" * Ghost 블로그 자동 포스팅")
    print(" * 마크다운 파일 자동 저장")
    print(" * 진행률 추적 및 에러 처리")
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
            result = simple_system_workflow()
            
            if result:
                print("\n✅ 간단한 시스템 작업 완료!")
                if "url" in result:
                    print(f"👉 블로그 URL: {result['url']}")
                print(f"👉 이미지: {result['stats']['images']}개")
            else:
                print("\n❌ 작업 중 오류가 발생했습니다.")
            
            input("\n계속하려면 Enter 키를 누르세요...")
        
        elif choice == "4":
            result = batch_system_workflow()
            
            if result and result["success"]:
                print(f"\n🎉 배치 처리 완료!")
                print(f"성공률: {result['success_rate']:.1f}% ({result['completed']}/{result['total_builds']})")
                print(f"처리 시간: {result['total_time']/60:.1f}분")
            else:
                print("\n❌ 배치 처리 실패")
            
            input("\n계속하려면 Enter 키를 누르세요...")
        
        elif choice == "5":
            # 자동 재개 시스템
            from bg3_auto_resume_system import auto_resume_batch_generation
            result = auto_resume_batch_generation()
            
            if result and result.get("success"):
                print(f"\n🎉 자동 재개 완료!")
                print(f"성공률: {result['success_rate']:.1f}% ({result['completed']}/{result['total_builds']})")
                print(f"처리 시간: {result['total_time']/60:.1f}분")
            else:
                print("\n❌ 자동 재개 실패")
            
            input("\n계속하려면 Enter 키를 누르세요...")
        
        elif choice == "6":
            # 스케줄링 배치 시스템
            from bg3_scheduled_system import scheduled_batch_workflow
            result = scheduled_batch_workflow()
            
            if result and result.get("success"):
                print(f"\n🎉 스케줄링 배치 완료!")
                print(f"성공률: {result['success_rate']:.1f}% ({result['completed']}/{result['total_builds']})")
                print(f"처리 시간: {result['total_time']/60:.1f}분")
                print(f"📋 리포트: {result['report_file']}")
            else:
                print("\n❌ 스케줄링 배치 실패")
            
            input("\n계속하려면 Enter 키를 누르세요...")
        
        elif choice == "7":
            result = batch_test_workflow()
            
            if result and result["success"]:
                print(f"\n🎉 테스트 완료!")
                print(f"성공률: {result['success_rate']:.1f}%")
                print(f"처리 시간: {result['total_time']/60:.1f}분")
            else:
                print("\n❌ 테스트 실패")
            
            input("\n계속하려면 Enter 키를 누르세요...")
        
        elif choice == "8":
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
        
        elif choice == "9":
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