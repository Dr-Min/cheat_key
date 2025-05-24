#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bg3_builder.simple_build_generator import create_build_simple_system
from bg3_builder.ghost_uploader import post_to_ghost_blog

def test_simple_system():
    """간단한 Perplexity 이미지 시스템 테스트"""
    print("🚀 간단한 PERPLEXITY 이미지 시스템 테스트!")
    print("=" * 60)
    
    # 테스트할 빌드명과 Perplexity 파일
    build_name = "Life Domain Cleric"
    perplexity_file = "perplexity_raw_response_20250524_172433.json"
    
    print(f"📋 테스트 빌드: {build_name}")
    print(f"📁 Perplexity 파일: {perplexity_file}")
    print()
    print(f"🎯 간단한 접근법:")
    print(f"  1️⃣ 괄호 안의 영어 용어 추출")
    print(f"  2️⃣ 콜론 뒤의 영어 용어 추출")
    print(f"  3️⃣ 확실한 BG3 용어들 직접 찾기")
    print(f"  4️⃣ 간단한 이미지 검색 (4가지 변형)")
    print(f"  5️⃣ 간단한 이미지 삽입")
    print()
    
    # Perplexity 파일 존재 확인
    if not os.path.exists(perplexity_file):
        print(f"❌ Perplexity 파일이 없습니다: {perplexity_file}")
        return
    
    # 간단한 시스템으로 빌드 생성
    print("🔄 간단한 시스템으로 빌드 생성 시작...")
    success, final_content, stats = create_build_simple_system(
        build_name, perplexity_file
    )
    
    if not success:
        print("❌ 빌드 생성 실패!")
        return
    
    print("✅ 빌드 생성 성공!")
    print(f"📊 최종 통계:")
    print(f"  - 콘텐츠 길이: {stats['length']:,} 문자")
    print(f"  - 삽입된 이미지: {stats['images']}개")
    
    # Ghost 블로그에 포스팅
    print("\n🔄 Ghost 블로그에 포스팅 중...")
    
    post_url = post_to_ghost_blog(
        title=f"[SIMPLE] {build_name} 빌드 가이드 - 간단한 이미지 시스템",
        content=final_content,
        build_name=build_name,
        tags=["간단시스템", "동적이미지", "Life Domain Cleric", "실용적"]
    )
    
    if post_url:
        print("🎯 간단한 시스템 테스트 완료!")
        print(f"🔗 포스트 URL: {post_url}")
        print()
        print("🔍 확인할 핵심사항:")
        print("  ✓ 괄호 안의 영어 용어들이 정확히 추출되었는지")
        print("  ✓ BG3 확실한 용어들(Guidance, Bless 등)이 발견되었는지")
        print("  ✓ 이미지가 실제로 삽입되었는지")
        print("  ✓ 64x64 크기, 갈색 테두리 스타일이 적용되었는지")
        print()
        print("📈 성과 측정:")
        print(f"  🎯 이미지 개수: {stats['images']}개")
        print(f"  🚀 복잡도: 기존 복잡함 → 신규 아주 간단함")
        print(f"  🔥 성공률: 실제 작동 여부 확인")
    else:
        print("❌ Ghost 포스팅 실패")

if __name__ == "__main__":
    test_simple_system() 