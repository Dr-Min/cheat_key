#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BG3 배치 시스템 테스트
작은 규모로 테스트해보는 스크립트
"""

from bg3_batch_generator import BG3BatchGenerator

def test_batch_system():
    """배치 시스템 테스트"""
    print("🧪 BG3 배치 시스템 테스트")
    print("=" * 40)
    
    # 작은 규모로 테스트 (첫 3개 빌드만)
    generator = BG3BatchGenerator(delay_between_builds=10)  # 10초 대기
    
    print("📋 테스트 설정:")
    print("  • 시작 인덱스: 0")
    print("  • 최대 빌드 수: 3")
    print("  • 대기 시간: 10초")
    
    confirm = input("\n테스트를 시작하시겠습니까? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', '예', 'ㅇ']:
        print("테스트를 취소했습니다.")
        return
    
    # 테스트 실행
    result = generator.run_batch_generation(
        start_from=0,
        max_builds=3,
        auto_post=True
    )
    
    if result["success"]:
        print(f"\n🎉 테스트 완료!")
        print(f"성공률: {result['success_rate']:.1f}%")
        print(f"처리 시간: {result['total_time']/60:.1f}분")
    else:
        print(f"\n❌ 테스트 실패: {result.get('error')}")

if __name__ == "__main__":
    test_batch_system() 