#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BG3 빌드 예약 발행 시스템
사용자가 원하는 시간에 자동으로 포스팅되도록 스케줄링
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from bg3_batch_generator import BG3ScheduledBatchGenerator

def scheduled_batch_workflow():
    """스케줄링 배치 시스템 워크플로우"""
    print("\n" + "=" * 70)
    print("⏰ BG3 빌드 스케줄링 배치 자동 생성 시스템".center(70))
    print("=" * 70)
    print("📅 원하는 시간에 자동으로 포스팅되도록 예약 발행합니다")
    print("예: 처음 10개 → 1시간 간격, 24시간 후 → 다음 10개...")
    print("-" * 70)
    
    try:
        # 기본 설정 입력
        start_from = int(input("시작 인덱스 (0부터 시작, 기본값 0): ") or "0")
        max_builds_input = input("최대 빌드 수 (전체 처리하려면 엔터): ").strip()
        max_builds = int(max_builds_input) if max_builds_input else None
        
        # 스케줄링 설정
        print("\n📋 스케줄링 설정:")
        batch_size = int(input("배치당 빌드 수 (기본값 10): ") or "10")
        interval_hours = int(input("배치 내 포스팅 간격(시간, 기본값 1): ") or "1")
        break_hours = int(input("배치 간 휴식 시간(시간, 기본값 24): ") or "24")
        
        # 시작 시간 설정
        print("\n⏰ 시작 시간 설정:")
        print("1. 1시간 후 시작 (기본)")
        print("2. 내일 오전 9시")
        print("3. 사용자 지정")
        
        time_choice = input("선택 (1-3): ").strip() or "1"
        
        if time_choice == "2":
            # 내일 오전 9시 (UTC 기준 00:00)
            tomorrow = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            start_time = tomorrow
        elif time_choice == "3":
            # 사용자 지정
            date_str = input("날짜와 시간 (YYYY-MM-DD HH:MM): ").strip()
            try:
                start_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            except ValueError:
                print("잘못된 날짜 형식입니다. 기본값(1시간 후)을 사용합니다.")
                start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        else:
            # 기본: 1시간 후
            start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # 설정 확인
        print(f"\n📋 설정 확인:")
        print(f"  • 시작 인덱스: {start_from}")
        print(f"  • 최대 빌드 수: {max_builds or '전체'}")
        print(f"  • 배치 크기: {batch_size}개")
        print(f"  • 배치 내 간격: {interval_hours}시간")
        print(f"  • 배치 간 휴식: {break_hours}시간")
        print(f"  • 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # 스케줄 미리보기
        print(f"\n📅 스케줄 예시:")
        current_time = start_time
        for i in range(min(5, max_builds or 5)):
            batch_num = i // batch_size
            pos_in_batch = i % batch_size
            
            if pos_in_batch == 0 and batch_num > 0:
                current_time += timedelta(hours=break_hours)
            elif pos_in_batch > 0:
                current_time += timedelta(hours=interval_hours)
            
            print(f"  빌드 {i+1}: {current_time.strftime('%m/%d %H:%M')}")
        
        confirm = input("\n계속 진행하시겠습니까? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes', '예', 'ㅇ']:
            print("작업을 취소했습니다.")
            return None
        
        # 스케줄링 배치 생성기 실행
        print("\n🚀 스케줄링 배치 생성 시작!")
        generator = BG3ScheduledBatchGenerator(delay_between_builds=30)
        result = generator.run_scheduled_batch_generation(
            start_from=start_from,
            max_builds=max_builds,
            start_time=start_time,
            batch_size=batch_size,
            interval_hours=interval_hours,
            break_hours=break_hours
        )
        
        return result
        
    except (ValueError, KeyboardInterrupt):
        print("작업을 취소했습니다.")
        return None

def main():
    """메인 함수"""
    result = scheduled_batch_workflow()
    
    if result and result.get("success"):
        print(f"\n🎉 스케줄링 배치 완료!")
        print(f"성공률: {result['success_rate']:.1f}% ({result['completed']}/{result['total_builds']})")
        print(f"처리 시간: {result['total_time']/60:.1f}분")
        print(f"📋 리포트: {result['report_file']}")
    else:
        print("\n❌ 스케줄링 배치 실패")

if __name__ == "__main__":
    main() 