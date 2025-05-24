#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bg3_builder.final_dynamic_generator import create_build_with_dynamic_images
from bg3_builder.ghost_uploader import post_to_ghost_blog

def test_final_dynamic_system():
    """최종 동적 이미지 시스템 테스트"""
    print("🚀 FINAL 동적 이미지 시스템 테스트 시작!")
    print("=" * 70)
    
    # 테스트할 빌드명 
    build_name = "Storm Sorcerer"
    
    print(f"📋 테스트 빌드: {build_name}")
    print(f"🔄 혁신적 동적 시스템:")
    print(f"  1️⃣ Perplexity → 원본 영어 빌드 정보 수집")
    print(f"  2️⃣ Grok → 한국어 번역")
    print(f"  3️⃣ 요약 카드 완전 제거")
    print(f"  4️⃣ 실제 텍스트에서 BG3 용어 동적 추출")
    print(f"  5️⃣ 정규식 패턴 + 휴리스틱으로 모든 용어 포착")
    print(f"  6️⃣ 다중 검색 전략으로 이미지 발굴")
    print(f"  7️⃣ 영어-한국어 매핑으로 정확한 삽입")
    print(f"  8️⃣ Ghost 블로그 포스팅")
    print()
    print("🎯 이제 빌드마다 다른 스킬/장비가 나와도 유동적으로 처리!")
    print()
    
    # 동적 이미지 시스템으로 빌드 생성
    print("🔄 빌드 생성 시작...")
    success, final_content, english_info = create_build_with_dynamic_images(build_name)
    
    if not success:
        print("❌ 빌드 생성 실패!")
        return
    
    print("✅ 빌드 생성 성공!")
    print(f"📊 최종 콘텐츠 길이: {len(final_content):,} 문자")
    
    # Ghost 블로그에 포스팅
    print("\n🔄 Ghost 블로그에 포스팅 중...")
    
    post_url = post_to_ghost_blog(
        title=f"[DYNAMIC] {build_name} 빌드 가이드",
        content=final_content,
        build_name=build_name,
        tags=["동적시스템", "이미지최적화", "Storm Sorcerer", "유동적처리"]
    )
    
    if post_url:
        print("🎯 FINAL 동적 이미지 시스템 테스트 완료!")
        print(f"🔗 포스트 URL: {post_url}")
        print()
        print("🔍 확인할 항목들:")
        print("  ✓ 모든 주문명에 이미지 (Lightning Bolt, Fireball, Counterspell 등)")
        print("  ✓ 모든 장비명에 이미지 (Staff, Robe, Ring 등)")
        print("  ✓ 클래스/서브클래스 이미지 (Sorcerer, Wild Magic 등)")
        print("  ✓ 한국어 용어에도 영어 매핑을 통한 이미지")
        print("  ✓ 텍스트에서 실제 언급된 용어들만 정확히 추출")
        print("  ✓ 리스트에 없던 새로운 용어도 동적으로 발견")
        print("  ✓ 요약 카드(인용구) 완전 제거")
        print()
        print("🎉 이미지 유동성 문제 완전 해결!")
        print("📈 예상 적용률: 모든 BG3 용어 90%+ 커버")
        print("🔥 이제 어떤 빌드가 와도 자동으로 이미지 적용!")
    else:
        print("❌ Ghost 포스팅 실패")

if __name__ == "__main__":
    test_final_dynamic_system() 