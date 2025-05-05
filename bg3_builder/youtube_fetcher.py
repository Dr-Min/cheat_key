import requests
import re
import time
from urllib.parse import quote_plus
from .utils import logger

def search_youtube_videos(query, max_results=3):
    """YouTube 비디오 검색 (YouTube API 대신 직접 검색)"""
    logger.info(f"YouTube 검색: '{query}'")
    
    search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        
        # 비디오 ID 추출
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
        
        # 중복 제거
        unique_video_ids = []
        for video_id in video_ids:
            if video_id not in unique_video_ids:
                unique_video_ids.append(video_id)
                if len(unique_video_ids) >= max_results:
                    break
        
        if not unique_video_ids:
            logger.warning(f"YouTube 검색 결과가 없습니다: '{query}'")
            return []
        
        logger.info(f"YouTube 검색 결과: {len(unique_video_ids)}개 비디오 찾음")
        return unique_video_ids
    
    except Exception as e:
        logger.error(f"YouTube 검색 중 오류 발생: {e}")
        return []

def get_youtube_thumbnail(video_id):
    """YouTube 비디오 썸네일 URL 가져오기"""
    # 고해상도 썸네일부터 시도
    thumbnail_urls = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",  # 최고 해상도
        f"https://img.youtube.com/vi/{video_id}/sddefault.jpg",       # 표준 해상도
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"        # 중간 해상도
    ]
    
    for url in thumbnail_urls:
        try:
            response = requests.head(url)
            if response.status_code == 200:
                logger.info(f"유효한 썸네일 발견: {url}")
                return url
        except Exception:
            pass
    
    # 기본 썸네일은 항상 존재하므로 최후의 수단으로 사용
    default_thumbnail = f"https://img.youtube.com/vi/{video_id}/default.jpg"
    logger.warning(f"고해상도 썸네일을 찾지 못했습니다. 기본 썸네일 사용: {default_thumbnail}")
    return default_thumbnail

def get_build_thumbnail(build_name):
    """빌드 이름으로 YouTube 검색하여 썸네일 가져오기"""
    logger.info(f"'{build_name}' 빌드 썸네일 검색 중...")
    
    # BG3와 build를 포함시켜 검색
    search_query = f"{build_name} BG3 build"
    video_ids = search_youtube_videos(search_query)
    
    if not video_ids:
        # 다른 검색어로 재시도
        search_query = f"Baldur's Gate 3 {build_name} guide"
        video_ids = search_youtube_videos(search_query)
    
    if video_ids:
        # 첫 번째 비디오의 썸네일 사용
        thumbnail_url = get_youtube_thumbnail(video_ids[0])
        
        # 비디오 URL도 함께 반환
        video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
        
        logger.info(f"빌드 썸네일 찾음: {thumbnail_url}")
        return {
            "thumbnail_url": thumbnail_url,
            "video_url": video_url,
            "video_id": video_ids[0]
        }
    
    logger.warning(f"'{build_name}' 빌드의 YouTube 썸네일을 찾지 못했습니다.")
    return None

def add_youtube_thumbnail_to_markdown(content, build_name):
    """마크다운 내용에 YouTube 썸네일 추가"""
    thumbnail_info = get_build_thumbnail(build_name)
    
    if not thumbnail_info:
        logger.warning("YouTube 썸네일을 추가하지 못했습니다.")
        return content
    
    # 썸네일 마크다운 생성
    thumbnail_markdown = (
        f"[![{build_name} 빌드 가이드]({thumbnail_info['thumbnail_url']})]({thumbnail_info['video_url']})\n"
        f"*이미지 클릭 시 YouTube 동영상으로 이동합니다*\n\n"
    )
    
    # 마크다운 첫 번째 제목 줄 찾기
    first_heading_match = re.search(r'^#\s+.*$', content, re.MULTILINE)
    
    if first_heading_match:
        # 제목 바로 아래에 썸네일 추가
        heading_end = first_heading_match.end()
        content = content[:heading_end] + "\n\n" + thumbnail_markdown + content[heading_end:]
    else:
        # 제목이 없으면 최상단에 추가
        content = thumbnail_markdown + content
    
    logger.info("YouTube 썸네일 추가 완료")
    return content 