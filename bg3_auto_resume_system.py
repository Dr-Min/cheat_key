#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BG3 빌드 배치 자동 재개 시스템
중간에 중단된 배치 작업을 자동으로 추적하고 재개
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
from bg3_builder.utils import setup_logging, load_env_vars

# 로거 설정
logger = setup_logging(level='INFO')

class BG3AutoResumeSystem:
    """BG3 배치 자동 재개 시스템"""
    
    def __init__(self):
        """초기화"""
        self.env_vars = load_env_vars()
        self.ghost_url = self.env_vars.get('GHOST_ADMIN_API_URL')
        self.ghost_key = self.env_vars.get('GHOST_API_KEY')
        
    def get_existing_posts(self) -> Set[str]:
        """Ghost 블로그에서 기존 포스트들의 제목을 가져오기"""
        existing_posts = set()
        
        if not self.ghost_url or not self.ghost_key:
            logger.warning("Ghost API 설정이 없어서 기존 포스트를 확인할 수 없습니다.")
            return existing_posts
        
        try:
            # Ghost Admin API로 포스트 목록 가져오기
            api_url = f"{self.ghost_url}/ghost/api/admin/posts/"
            headers = {
                'Authorization': f'Ghost {self.ghost_key}',
                'Content-Type': 'application/json'
            }
            
            page = 1
            while True:
                params = {
                    'limit': 50,  # 한 번에 50개씩
                    'page': page,
                    'fields': 'title,slug',
                    'filter': 'tag:배치생성'  # 배치생성 태그가 있는 포스트만
                }
                
                response = requests.get(api_url, headers=headers, params=params)
                
                if response.status_code != 200:
                    logger.warning(f"Ghost API 호출 실패: {response.status_code}")
                    break
                
                data = response.json()
                posts = data.get('posts', [])
                
                if not posts:
                    break
                
                # 포스트 제목에서 빌드명 추출
                for post in posts:
                    title = post.get('title', '')
                    # "[배치생성] Battle Master Fighter 빌드 가이드" -> "Battle Master Fighter"
                    if title.startswith('[배치생성]') and '빌드 가이드' in title:
                        build_name = title.replace('[배치생성]', '').replace('빌드 가이드', '').strip()
                        existing_posts.add(build_name)
                        logger.debug(f"기존 포스트 발견: {build_name}")
                
                # 다음 페이지가 있는지 확인
                meta = data.get('meta', {})
                pagination = meta.get('pagination', {})
                if page >= pagination.get('pages', 1):
                    break
                
                page += 1
            
            logger.info(f"기존 포스트 {len(existing_posts)}개 발견")
            return existing_posts
            
        except Exception as e:
            logger.error(f"기존 포스트 확인 중 오류: {e}")
            return existing_posts
    
    def load_build_list(self, build_list_file="bg3_build_list.txt") -> List[Tuple[str, str]]:
        """빌드 목록 로드"""
        builds = []
        current_category = "일반"
        
        if not os.path.exists(build_list_file):
            logger.error(f"빌드 목록 파일을 찾을 수 없습니다: {build_list_file}")
            return []
        
        with open(build_list_file, 'r', encoding='utf-8') as f:
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
        
        return builds
    
    def find_resume_point(self, builds: List[Tuple[str, str]], existing_posts: Set[str]) -> int:
        """재개 시작점 찾기"""
        for i, (build_name, category) in enumerate(builds):
            if build_name not in existing_posts:
                logger.info(f"재개 시작점 발견: {i}번째 빌드 '{build_name}'")
                return i
        
        # 모든 빌드가 완료된 경우
        logger.info("모든 빌드가 이미 완료되었습니다!")
        return len(builds)
    
    def get_resume_info(self) -> Dict:
        """자동 재개 정보 가져오기"""
        logger.info("🔍 배치 작업 재개 정보 확인 중...")
        
        # 빌드 목록 로드
        builds = self.load_build_list()
        if not builds:
            return {"error": "빌드 목록을 로드할 수 없습니다"}
        
        # 기존 포스트 확인
        existing_posts = self.get_existing_posts()
        
        # 재개 시작점 찾기
        resume_from = self.find_resume_point(builds, existing_posts)
        
        # 통계 계산
        total_builds = len(builds)
        completed_builds = len(existing_posts)
        remaining_builds = total_builds - resume_from
        
        result = {
            "total_builds": total_builds,
            "completed_builds": completed_builds,
            "resume_from": resume_from,
            "remaining_builds": remaining_builds,
            "completed_list": list(existing_posts),
            "next_build": builds[resume_from][0] if resume_from < total_builds else None
        }
        
        logger.info(f"📊 재개 정보:")
        logger.info(f"  • 전체 빌드: {total_builds}개")
        logger.info(f"  • 완료된 빌드: {completed_builds}개")
        logger.info(f"  • 재개 시작점: {resume_from}번째")
        logger.info(f"  • 남은 빌드: {remaining_builds}개")
        
        if result["next_build"]:
            logger.info(f"  • 다음 빌드: {result['next_build']}")
        
        return result

def auto_resume_batch_generation():
    """자동 재개 배치 생성"""
    from bg3_batch_generator import BG3BatchGenerator
    
    print("🔄 BG3 빌드 배치 자동 재개 시스템")
    print("=" * 50)
    
    # 재개 정보 확인
    resume_system = BG3AutoResumeSystem()
    resume_info = resume_system.get_resume_info()
    
    if "error" in resume_info:
        print(f"❌ {resume_info['error']}")
        return None
    
    # 재개 정보 출력
    total = resume_info["total_builds"]
    completed = resume_info["completed_builds"]
    remaining = resume_info["remaining_builds"]
    resume_from = resume_info["resume_from"]
    next_build = resume_info["next_build"]
    
    print(f"\n📊 현재 상태:")
    print(f"  • 전체 빌드: {total}개")
    print(f"  • 완료된 빌드: {completed}개 ({completed/total*100:.1f}%)")
    print(f"  • 남은 빌드: {remaining}개")
    
    if remaining == 0:
        print("\n🎉 모든 빌드가 이미 완료되었습니다!")
        return {"success": True, "message": "모든 빌드 완료"}
    
    print(f"\n🎯 다음 시작 빌드: {next_build}")
    print(f"📍 시작 인덱스: {resume_from}")
    
    # 사용자 확인
    confirm = input(f"\n{remaining}개 빌드를 {resume_from}번째부터 계속 진행하시겠습니까? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', '예', 'ㅇ']:
        print("작업을 취소했습니다.")
        return None
    
    # 대기 시간 설정
    try:
        delay = int(input("빌드 간 대기 시간(초, 기본값 30): ") or "30")
    except ValueError:
        delay = 30
    
    print(f"\n🚀 배치 생성 재개 시작!")
    print(f"시작점: {resume_from}, 남은 빌드: {remaining}개, 대기시간: {delay}초")
    
    # 배치 생성기 실행
    generator = BG3BatchGenerator(delay_between_builds=delay)
    result = generator.run_batch_generation(
        start_from=resume_from,
        max_builds=None,  # 끝까지 실행
        auto_post=True
    )
    
    return result

def show_resume_status():
    """재개 상태만 확인 (실행하지 않음)"""
    resume_system = BG3AutoResumeSystem()
    resume_info = resume_system.get_resume_info()
    
    if "error" in resume_info:
        print(f"❌ {resume_info['error']}")
        return
    
    print("\n" + "=" * 60)
    print("📊 BG3 배치 생성 진행 상황".center(60))
    print("=" * 60)
    
    total = resume_info["total_builds"]
    completed = resume_info["completed_builds"]
    remaining = resume_info["remaining_builds"]
    
    # 진행률 바 생성
    progress = completed / total
    bar_length = 40
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    print(f"\n진행률: [{bar}] {progress*100:.1f}%")
    print(f"완료: {completed}/{total}개 빌드")
    
    if remaining > 0:
        print(f"\n🎯 다음 시작: {resume_info['next_build']}")
        print(f"📍 시작 인덱스: {resume_info['resume_from']}")
        print(f"⏱️ 예상 소요 시간: {remaining * 2:.0f}분")
    else:
        print(f"\n🎉 모든 빌드 완료!")
    
    print("=" * 60)

def main():
    """메인 함수"""
    print("🔄 BG3 배치 자동 재개 시스템")
    print("=" * 40)
    print("1. 진행 상황 확인만")
    print("2. 자동 재개 실행")
    print("0. 종료")
    
    choice = input("\n선택: ").strip()
    
    if choice == "1":
        show_resume_status()
    elif choice == "2":
        result = auto_resume_batch_generation()
        if result and result.get("success"):
            print(f"\n🎉 자동 재개 완료!")
            print(f"성공률: {result['success_rate']:.1f}%")
    elif choice == "0":
        print("종료합니다.")
    else:
        print("올바른 선택을 해주세요.")

if __name__ == "__main__":
    main() 