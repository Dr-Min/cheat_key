import requests
import json
import datetime
import time
import jwt
import re
from typing import Dict, Any, Optional, List, Union
from .utils import logger

class GhostAPI:
    def __init__(self, api_url=None, admin_api_key=None, integration_id=None):
        """Ghost API 클래스 초기화"""
        # Ghost API 구성
        self.api_url = api_url or "https://globexfeed.com/ghost"
        self.admin_api_key = admin_api_key or "67deb866ce5a16c2cac23f08:a785936c8fb3ef3a1c87eb513f5763afe4baf242b1f02feab6f5940a09fe76d6"
        self.integration_id = integration_id or "67deb866ce5a16c2cac23f05"
        self.version = "admin"
        
        # API 키 분리
        self.id, self.secret = self.admin_api_key.split(':')
        
    def _create_jwt_token(self) -> str:
        """Ghost Admin API 인증을 위한 JWT 토큰 생성"""
        # 현재 시간과 만료 시간 설정 (5분)
        iat = int(time.time())
        exp = iat + 5 * 60
        
        # JWT 페이로드
        payload = {
            'iat': iat,
            'exp': exp,
            'aud': '/admin/'
        }
        
        # JWT 토큰 생성
        token = jwt.encode(
            payload,
            bytes.fromhex(self.secret),
            algorithm='HS256',
            headers={'kid': self.id, 'alg': 'HS256'}
        )
        
        # PyJWT 버전에 따라 bytes로 리턴될 수 있음 → 문자열로 변환
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        logger.info(f"JWT 토큰 생성 완료: {token[:20]}...")
        return token
    
    def _generate_slug(self, title: str) -> str:
        """한글 제목에서 URL 슬러그 생성"""
        # 특수문자 제거
        slug = re.sub(r'[^\w\s가-힣]', '', title)
        # 띄어쓰기를 하이픈으로 변경
        slug = re.sub(r'\s+', '-', slug)
        # 최대 길이 제한
        if len(slug) > 60:
            slug = slug[:60]
        return slug
        
    def create_post(self, 
                   title: str, 
                   content: str, 
                   tags: Optional[List[Union[str, Dict[str, str]]]] = None, 
                   feature_image: Optional[str] = None,
                   meta_title: Optional[str] = None,
                   meta_description: Optional[str] = None,
                   custom_slug: Optional[str] = None,
                   status: str = "draft",
                   is_markdown: bool = True) -> Dict[str, Any]:
        """Ghost API를 사용하여 새 포스트를 생성합니다."""
        # Ghost Admin API 엔드포인트
        url = f"{self.api_url}/api/{self.version}/posts/"
        
        # JWT 토큰 생성
        token = self._create_jwt_token()
        
        # API 요청 헤더
        headers = {
            'Authorization': f'Ghost {token}',
            'Content-Type': 'application/json'
        }
        
        # 기본 태그 설정
        if tags is None:
            tags = ["BG3", "발더스 게이트 3", "빌드 가이드"]
            
        # 태그를 Ghost API에 맞는 형식으로 변환
        tag_objects = []
        for tag in tags:
            if isinstance(tag, dict):
                tag_objects.append(tag)
            else:
                tag_objects.append({"name": tag})
        
        # 메타 데이터 설정
        if not meta_title:
            meta_title = title
            
        # UTC 시간 설정
        now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # 슬러그 생성 (URL 경로)
        slug = custom_slug if custom_slug else self._generate_slug(title)
        
        # mobiledoc 생성 (마크다운 또는 HTML)
        card_type = "markdown" if is_markdown else "html"
        card_content = {"markdown": content} if is_markdown else {"html": content}
        
        mobiledoc = {
            "version": "0.3.1",
            "markups": [],
            "atoms": [],
            "cards": [[card_type, card_content]],
            "sections": [[10, 0]]
        }
        
        # Ghost API 형식에 맞게 데이터 구조화
        data = {
            "posts": [{
                "title": title,
                "status": status,
                "featured": False,
                "tags": tag_objects,
                "slug": slug,
                "published_at": now_utc,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "mobiledoc": json.dumps(mobiledoc)
            }]
        }
        
        # 대표 이미지가 있는 경우 추가
        if feature_image:
            data["posts"][0]["feature_image"] = feature_image
        
        try:
            logger.info(f"Ghost API 요청 URL: {url}")
            logger.debug(f"요청 데이터 구조: {json.dumps(data, ensure_ascii=False)[:100]}...")
            
            # API 요청 전송
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            # 응답 결과 로깅
            logger.info(f"응답 코드: {response.status_code}")
            
            # 응답 내용 확인
            if response.text:
                logger.debug(f"응답 내용 미리보기: {response.text[:200]}...")
                
            # 성공 여부 확인 (201 = Created)
            if response.status_code == 201:
                result = response.json()
                logger.info(f"Ghost 블로그 포스트가 성공적으로 생성되었습니다.")
                post_url = result.get("posts", [{}])[0].get("url", "")
                if post_url:
                    logger.info(f"포스트 URL: {post_url}")
                return result
            else:
                logger.error(f"Ghost 블로그 포스트 생성 실패: {response.status_code}")
                logger.error(f"응답 내용: {response.text}")
                return {}
            
        except requests.RequestException as e:
            logger.error(f"Ghost 블로그 포스트 생성 중 오류 발생: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"응답 코드: {e.response.status_code}")
                logger.error(f"응답 내용: {e.response.text}")
            return {}

def post_to_ghost_blog(title, content, build_name, tags=None):
    """Ghost 블로그에 포스팅"""
    logger.info("Ghost 블로그에 포스팅 중...")
    
    try:
        # GhostAPI 인스턴스 생성
        ghost = GhostAPI()
        
        # 태그 준비
        default_tags = ["bg3", "공략", "빌드"]
        if build_name and build_name.strip():
            default_tags.append(build_name.strip())
            
        # 사용자 지정 태그가 있으면 추가
        if tags:
            for tag in tags:
                if tag not in default_tags:
                    default_tags.append(tag)
        
        # 메타 정보
        meta_title = f"BG3 {build_name} 빌드 가이드"
        meta_description = f"Baldur's Gate 3 {build_name} 빌드 공략 가이드"
        
        # Ghost API로 포스트 생성
        result = ghost.create_post(
            title=title,
            content=content,
            tags=default_tags,
            meta_title=meta_title,
            meta_description=meta_description,
            status="draft",
            is_markdown=True  # 마크다운 형식 사용
        )
        
        if result and "posts" in result and len(result["posts"]) > 0:
            post_url = result["posts"][0].get("url", "")
            logger.info(f"Ghost 블로그에 성공적으로 포스팅되었습니다: {post_url}")
            return post_url
        else:
            logger.error("Ghost 블로그 포스팅 결과가 유효하지 않습니다.")
            return None
    
    except Exception as e:
        logger.error(f"Ghost 블로그 포스팅 중 오류 발생: {e}")
        return None

# 테스트 코드
if __name__ == "__main__":
    # 로깅 설정
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 테스트 마크다운
    test_markdown = """
    # Ghost API 연결 테스트 - JWT 인증
    
    이 글은 Ghost API JWT 인증 방식으로 작성된 테스트 글입니다.
    
    * 이제 성공적으로 Ghost 블로그에 포스팅할 수 있습니다!
    * 마크다운 형식으로 작성했습니다.
    """
    
    # 포스팅 테스트
    post_url = post_to_ghost_blog(
        title="Ghost API 테스트",
        content=test_markdown,
        build_name="테스트 빌드",
        tags=["테스트", "API"]
    )
    
    if post_url:
        print(f"테스트 성공! 포스트 URL: {post_url}")
    else:
        print("테스트 실패") 