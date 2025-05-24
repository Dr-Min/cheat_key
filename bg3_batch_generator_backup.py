#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BG3 빌드 가이드 배치 자동 생성기
여러 빌드를 순차적으로 자동 생성하는 시스템
"""

import os
import time
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from bg3_builder.utils import setup_logging
from bg3_builder.simple_build_generator import create_build_simple_system
from bg3_builder.ghost_uploader import post_to_ghost_blog

# 로거 설정
logger = setup_logging(level='INFO')

class BG3BatchGenerator:
    """BG3 빌드 배치 생성기"""
    
    def __init__(self, build_list_file="bg3_build_list.txt", delay_between_builds=30):
        """
        초기화
        
        Args:
            build_list_file: 빌드 목록 파일 경로
            delay_between_builds: 빌드 간 대기 시간 (초)
        """
        self.build_list_file = build_list_file
        self.delay_between_builds = delay_between_builds
        self.results = []
        self.total_builds = 0
        self.completed_builds = 0
        self.failed_builds = 0
        
    def load_build_list(self) -> List[Tuple[str, str]]:
        """빌드 목록 파일에서 빌드 리스트 로드"""
        builds = []
        current_category = "일반"
        
        if not os.path.exists(self.build_list_file):
            logger.error(f"빌드 목록 파일을 찾을 수 없습니다: {self.build_list_file}")
            return []
        
        with open(self.build_list_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # 카테고리 헤더 처리
                if line.startswith("##"):
                    current_category = line.replace("##", "").strip()
                    continue
                
                # 빈 줄이나 주석 건너뛰기
                if not line or line.startswith("#"):
                    continue
                
                # 빌드명 추가
                builds.append((line, current_category))
        
        logger.info(f"총 {len(builds)}개의 빌드 로드 완료")
        return builds
    
    def get_latest_perplexity_file(self) -> Optional[str]:
        """가장 최근의 Perplexity 파일 찾기"""
        import glob
        
        perplexity_files = glob.glob("perplexity_raw_response_*.json")
        if not perplexity_files:
            logger.warning("Perplexity 파일을 찾을 수 없습니다.")
            return None
        
        # 파일명의 타임스탬프 기준으로 정렬하여 가장 최근 파일 반환
        perplexity_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        latest_file = perplexity_files[0]
        logger.info(f"최신 Perplexity 파일 사용: {latest_file}")
        return latest_file
    
    def process_single_build(self, build_name: str, category: str, perplexity_file: str) -> Dict:
        """단일 빌드 처리"""
        logger.info(f"🔄 [{category}] {build_name} 빌드 생성 시작...")
        start_time = time.time()
        
        try:
            # 빌드 생성
            success, final_content, stats = create_build_simple_system(build_name, perplexity_file)
            
            if not success:
                logger.error(f"❌ {build_name} 빌드 생성 실패")
                return {
                    "build_name": build_name,
                    "category": category,
                    "success": False,
                    "error": "빌드 생성 실패",
                    "execution_time": time.time() - start_time
                }
            
                                    # Ghost 블로그 포스팅            logger.info(f"📤 {build_name} Ghost 블로그 포스팅...")            post_url = post_to_ghost_blog(                title=f"[배치생성] {build_name} 빌드 가이드",                content=final_content,                build_name=build_name,                tags=["발더스게이트3", "배치생성", category.replace(" ", ""), build_name.replace(" ", "")]            )
            
            execution_time = time.time() - start_time
            
            result = {
                "build_name": build_name,
                "category": category,
                "success": True,
                "post_url": post_url,
                "stats": stats,
                "execution_time": execution_time
            }
            
            if post_url:
                logger.info(f"✅ {build_name} 완료! ({execution_time:.1f}초)")
                logger.info(f"🔗 URL: {post_url}")
            else:
                logger.warning(f"⚠️ {build_name} 생성 성공, 포스팅 실패")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {build_name} 처리 중 오류: {e}")
            return {
                "build_name": build_name,
                "category": category,
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    def run_batch_generation(self, start_from: int = 0, max_builds: Optional[int] = None, auto_post: bool = True) -> Dict:
        """배치 생성 실행"""
        logger.info("🚀 BG3 빌드 배치 자동 생성 시작!")
        logger.info("=" * 70)
        
        # 빌드 목록 로드
        builds = self.load_build_list()
        if not builds:
            logger.error("빌드 목록이 비어있습니다.")
            return {"success": False, "error": "빌드 목록 없음"}
        
        # 최신 Perplexity 파일 찾기
        perplexity_file = self.get_latest_perplexity_file()
        if not perplexity_file:
            logger.error("Perplexity 파일을 찾을 수 없습니다.")
            return {"success": False, "error": "Perplexity 파일 없음"}
        
        # 처리할 빌드 범위 설정
        if max_builds:
            builds = builds[start_from:start_from + max_builds]
        else:
            builds = builds[start_from:]
        
        self.total_builds = len(builds)
        logger.info(f"📊 처리할 빌드: {self.total_builds}개 (시작: {start_from})")
        logger.info(f"⏱️ 예상 소요 시간: {(self.total_builds * 2):.0f}분 (빌드당 약 2분)")
        logger.info("-" * 70)
        
        batch_start_time = time.time()
        
        # 각 빌드 순차 처리
        for i, (build_name, category) in enumerate(builds, 1):
            logger.info(f"\n[{i}/{self.total_builds}] 🎯 현재 진행률: {(i-1)/self.total_builds*100:.1f}%")
            
            # 빌드 처리
            result = self.process_single_build(build_name, category, perplexity_file)
            self.results.append(result)
            
            # 통계 업데이트
            if result["success"]:
                self.completed_builds += 1
            else:
                self.failed_builds += 1
            
            # 진행 상황 출력
            logger.info(f"📈 진행 상황: 완료 {self.completed_builds}, 실패 {self.failed_builds}")
            
            # 마지막 빌드가 아니면 대기
            if i < len(builds):
                logger.info(f"⏳ {self.delay_between_builds}초 대기 중...")
                time.sleep(self.delay_between_builds)
        
        # 최종 결과 저장 및 리포트 생성
        total_time = time.time() - batch_start_time
        final_result = self.generate_final_report(total_time)
        
        return final_result
    
    def generate_final_report(self, total_time: float) -> Dict:
        """최종 결과 리포트 생성"""
        logger.info("\n" + "=" * 70)
        logger.info("🏁 배치 처리 완료!")
        logger.info("=" * 70)
        
        # 통계 계산
        success_rate = (self.completed_builds / self.total_builds * 100) if self.total_builds > 0 else 0
        avg_time_per_build = total_time / self.total_builds if self.total_builds > 0 else 0
        
        # 결과 출력
        logger.info(f"📊 전체 통계:")
        logger.info(f"  • 총 빌드: {self.total_builds}개")
        logger.info(f"  • 성공: {self.completed_builds}개")
        logger.info(f"  • 실패: {self.failed_builds}개")
        logger.info(f"  • 성공률: {success_rate:.1f}%")
        logger.info(f"  • 총 소요 시간: {total_time/60:.1f}분")
        logger.info(f"  • 빌드당 평균 시간: {avg_time_per_build:.1f}초")
        
        # 실패한 빌드 목록
        failed_builds = [r for r in self.results if not r["success"]]
        if failed_builds:
            logger.warning(f"\n❌ 실패한 빌드 ({len(failed_builds)}개):")
            for result in failed_builds:
                logger.warning(f"  • {result['build_name']}: {result.get('error', '알 수 없는 오류')}")
        
        # 성공한 빌드 목록
        successful_builds = [r for r in self.results if r["success"]]
        if successful_builds:
            logger.info(f"\n✅ 성공한 빌드 ({len(successful_builds)}개):")
            for result in successful_builds:
                url = result.get('post_url', '포스팅 실패')
                logger.info(f"  • {result['build_name']}: {url}")
        
        # 결과를 JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"batch_generation_report_{timestamp}.json"
        
        report_data = {
            "batch_info": {
                "timestamp": timestamp,
                "total_builds": self.total_builds,
                "completed_builds": self.completed_builds,
                "failed_builds": self.failed_builds,
                "success_rate": success_rate,
                "total_time_minutes": total_time / 60,
                "avg_time_per_build_seconds": avg_time_per_build
            },
            "results": self.results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n📄 상세 리포트 저장: {report_file}")
        logger.info("=" * 70)
        
        return {
            "success": True,
            "total_builds": self.total_builds,
            "completed": self.completed_builds,
            "failed": self.failed_builds,
            "success_rate": success_rate,
            "total_time": total_time,
            "report_file": report_file,
            "results": self.results
        }

def main():
    """메인 함수"""
    print("🔥 BG3 빌드 배치 자동 생성기 🔥")
    print("=" * 50)
    
    # 사용자 설정
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
            return
        
    except KeyboardInterrupt:
        print("\n작업을 취소했습니다.")
        return
    except ValueError:
        print("잘못된 입력입니다.")
        return
    
    # 배치 생성기 실행
    generator = BG3BatchGenerator(delay_between_builds=delay)
    result = generator.run_batch_generation(
        start_from=start_from,
        max_builds=max_builds,
        auto_post=True
    )
    
    if result["success"]:
        print(f"\n🎉 배치 처리 완료!")
        print(f"성공률: {result['success_rate']:.1f}% ({result['completed']}/{result['total_builds']})")
    else:
        print(f"\n❌ 배치 처리 실패: {result.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    main() 