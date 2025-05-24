import requests
import json
import datetime
import time
import jwt
import re
import markdown
from typing import Dict, Any, Optional, List, Union
from .utils import logger, env_vars

class GhostAPI:
    def __init__(self, api_url=None, admin_api_key=None, integration_id=None):
        """Ghost API 클래스 초기화"""
        # Ghost API 구성
        self.api_url = api_url or "https://ko.globexfeed.com" or env_vars.get('GHOST_ADMIN_API_URL')
        self.admin_api_key = admin_api_key or "6821c76cd1a15ea6851d6707:c76767c8b224d33ac08559b4e8adc25d2d4466747c2c3c6976bbc98513363907" or env_vars.get('GHOST_API_KEY')
        self.integration_id = integration_id or "6821c76cd1a15ea6851d6704" or env_vars.get('GHOST_INTEGRATION_ID')
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
    
    def _convert_markdown_to_html(self, markdown_content: str) -> str:
        """마크다운을 Ghost 친화적인 HTML로 변환"""
        # 먼저 문장 끝 마침표 뒤에 줄바꿈 추가
        from .utils import add_newlines_after_sentences
        content = add_newlines_after_sentences(markdown_content)
        
        # 리스트 항목을 정리 (마크다운 변환 전)
        
        # 요약 카드(인용구) 제거 패턴 - 강화된 버전
        summary_card_patterns = [
            # > **빌드명**: ... 형태의 요약 카드 (단일 라인)
            r'>\s*\*\*빌드명\*\*:.*?(?=\n[^>]|\n$|\Z)',
            # 연속된 인용구들 (여러 줄에 걸친 요약 카드) - 더 포괄적
            r'(?:>\s*\*\*(?:빌드명|주요\s*역할|핵심\s*스탯|추천\s*종족|강점|패치\s*기준)\*\*:.*?\n?)+',
            # 모든 빌드 요약 관련 인용구 블록
            r'>\s*\*\*빌드명\*\*:.*?(?:\n>\s*\*\*(?:주요\s*역할|핵심\s*스탯|추천\s*종족|강점|패치\s*기준)\*\*:.*?)*',
            # 빌드명으로 시작하는 모든 인용구 블록 (완전 제거)
            r'>\s*\*\*빌드명\*\*:.*?(?=\n(?:[^>]|$)|\Z)',
            # 여러 줄 인용구에서 빌드 정보 카드만 선별 제거
            r'(?:^>\s*\*\*(?:빌드명|주요\s*역할|핵심\s*스탯|추천\s*종족|강점|패치\s*기준)\*\*:.*?$\n?)+',
        ]
        
        # 요약 카드 제거 - 더 강력한 처리
        for pattern in summary_card_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
        
        # 추가: 빌드 관련 인용구 완전 제거
        content = re.sub(r'>\s*\*\*빌드명\*\*.*?(\n|$)', '', content, flags=re.MULTILINE)
        content = re.sub(r'>\s*\*\*주요\s*역할\*\*.*?(\n|$)', '', content, flags=re.MULTILINE)
        content = re.sub(r'>\s*\*\*핵심\s*스탯\*\*.*?(\n|$)', '', content, flags=re.MULTILINE)
        content = re.sub(r'>\s*\*\*추천\s*종족\*\*.*?(\n|$)', '', content, flags=re.MULTILINE)
        content = re.sub(r'>\s*\*\*강점\*\*.*?(\n|$)', '', content, flags=re.MULTILINE)
        content = re.sub(r'>\s*\*\*패치\s*기준\*\*.*?(\n|$)', '', content, flags=re.MULTILINE)
        
        # 빈 줄 정리
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # 텍스트를 줄 단위로 분리하여 처리 (줄바꿈 보존)
        lines = content.split('\n')
        processed_lines = []
        in_list = False
        
        for i, line in enumerate(lines):
            # 줄바꿈을 보존하기 위해 strip() 대신 좌측 공백만 제거하고 우측 공백은 보존
            stripped_line = line.lstrip()
            
            # 리스트 항목인지 확인
            if stripped_line.startswith('- ') or stripped_line.startswith('* '):
                # 리스트 시작 전에 빈 줄이 없으면 추가
                if not in_list and i > 0 and lines[i-1].lstrip() != '':
                    processed_lines.append('')
                
                # 하이픈을 별표로 변경
                if stripped_line.startswith('- '):
                    processed_lines.append(line.replace('- ', '* ', 1))
                else:
                    processed_lines.append(line)
                in_list = True
            else:
                # 리스트가 끝난 후 빈 줄이 없으면 추가
                if in_list and stripped_line != '':
                    processed_lines.append('')
                
                processed_lines.append(line)
                in_list = False
        
        content = '\n'.join(processed_lines)
        
        # 마크다운 확장 설정
        extensions = [
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.tables'
        ]
        
        try:
            # HTML로 변환
            html = markdown.markdown(content, extensions=extensions)
            
            # HTML에서도 요약 카드 제거 (혹시 변환된 것이 있다면) - 강화된 버전
            html = re.sub(r'<blockquote[^>]*>.*?빌드명.*?</blockquote>', '', html, flags=re.DOTALL)
            html = re.sub(r'<blockquote[^>]*>.*?<strong>빌드명</strong>.*?</blockquote>', '', html, flags=re.DOTALL)
            # 추가 HTML 요약 카드 제거 패턴들
            html = re.sub(r'<blockquote[^>]*>.*?<p>.*?<strong>빌드명</strong>.*?</p>.*?</blockquote>', '', html, flags=re.DOTALL)
            html = re.sub(r'<blockquote[^>]*>.*?주요\s*역할.*?</blockquote>', '', html, flags=re.DOTALL)
            html = re.sub(r'<blockquote[^>]*>.*?핵심\s*스탯.*?</blockquote>', '', html, flags=re.DOTALL)
            html = re.sub(r'<blockquote[^>]*>.*?추천\s*종족.*?</blockquote>', '', html, flags=re.DOTALL)
            html = re.sub(r'<blockquote[^>]*>.*?강점.*?</blockquote>', '', html, flags=re.DOTALL)
            html = re.sub(r'<blockquote[^>]*>.*?패치\s*기준.*?</blockquote>', '', html, flags=re.DOTALL)
            # 사용자가 보여준 정확한 패턴도 제거
            html = re.sub(r'<blockquote[^>]*>.*?<p><strong>빌드명</strong>:.*?<strong>패치\s*기준</strong>:.*?</p>.*?</blockquote>', '', html, flags=re.DOTALL)
            # 모든 빌드 정보 관련 blockquote 제거
            html = re.sub(r'<blockquote[^>]*style="[^"]*"[^>]*>.*?<p>.*?<strong>(?:빌드명|주요\s*역할|핵심\s*스탯|추천\s*종족|강점|패치\s*기준)</strong>.*?</p>.*?</blockquote>', '', html, flags=re.DOTALL)
            
            # Ghost에서 문제가 될 수 있는 요소들 정리
            # 이미지 태그 정리 (Ghost 형식에 맞게)
            html = re.sub(r'<img([^>]*?)width="100%"([^>]*?)>', r'<img\1\2 style="width: 100%;">', html)
            html = re.sub(r'<img([^>]*?)width="(\d+)"([^>]*?)>', r'<img\1\3 style="width: \2px;">', html)
            
            # YouTube 링크 처리 개선
            html = re.sub(
                r'\[!\[([^\]]*?)\]\(([^)]*?)\)\]\(([^)]*?)\)',
                r'<a href="\3" target="_blank"><img src="\2" alt="\1" style="width: 100%; max-width: 600px;"></a>',
                html
            )
            
            # 인용구 스타일 개선 (일반 인용구만, 요약 카드는 이미 제거됨)
            html = re.sub(r'<blockquote>', '<blockquote style="border-left: 4px solid #007acc; padding-left: 15px; margin: 20px 0;">', html)
            
            return html
        except Exception as e:
            logger.error(f"마크다운 변환 중 오류: {e}")
            # 변환 실패 시 원본 마크다운 반환
            return f"<pre>{markdown_content}</pre>"
    
    def _create_mobiledoc_from_html(self, html_content: str) -> dict:
        """HTML 콘텐츠로부터 Mobiledoc 생성"""
        return {
            "version": "0.3.1",
            "markups": [],
            "atoms": [],
            "cards": [["html", {"html": html_content}]],
            "sections": [[10, 0]]
        }
        
    def create_post(self, 
                   title: str, 
                   content: str, 
                   tags: Optional[List[Union[str, Dict[str, str]]]] = None, 
                   feature_image: Optional[str] = None,
                   meta_title: Optional[str] = None,
                   meta_description: Optional[str] = None,
                   custom_slug: Optional[str] = None,
                   status: str = "draft",
                   published_at: Optional[str] = None,
                   is_markdown: bool = True) -> Dict[str, Any]:
        """Ghost API를 사용하여 새 포스트를 생성합니다."""
        # Ghost Admin API 엔드포인트
        url = f"{self.api_url}/ghost/api/{self.version}/posts/"
        
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
            
        # 메타 제목도 길이 제한
        if len(meta_title) > 255:
            meta_title = meta_title[:252] + "..."
            
        # 발행 시간 설정
        if published_at:
            # 사용자가 지정한 시간 사용 (예약 발행)
            publish_time = published_at
            if status == "draft":
                status = "scheduled"  # 예약 발행으로 상태 변경
        else:
            # 기본 현재 시간 (UTC)
            publish_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # 슬러그 생성 (URL 경로)
        slug = custom_slug if custom_slug else self._generate_slug(title)
        
        # 콘텐츠를 HTML로 변환하여 Ghost에서 올바르게 렌더링되도록 함
        if is_markdown:
            # 마크다운을 HTML로 변환
            html_content = self._convert_markdown_to_html(content)
            mobiledoc = self._create_mobiledoc_from_html(html_content)
            logger.info("마크다운을 HTML로 변환하여 Ghost에 전송합니다.")
        else:
            # 이미 HTML인 경우 그대로 사용
            mobiledoc = self._create_mobiledoc_from_html(content)
            logger.info("HTML 콘텐츠를 Ghost에 전송합니다.")
        
        # 제목에서 HTML 태그 제거 (이미지 태그 등)
        title = re.sub(r'<[^>]+>', '', title)
        
        # 제목 길이 제한 (Ghost 255자 제한)
        if len(title) > 255:
            title = title[:252] + "..."
            logger.warning(f"제목이 255자를 초과하여 자릅니다: {title}")
        
        logger.info(f"최종 제목: {title} (길이: {len(title)}자)")
        
        # Ghost API 형식에 맞게 데이터 구조화
        data = {
            "posts": [{
                "title": title,
                "status": status,
                "featured": False,
                "tags": tag_objects,
                "slug": slug,
                "published_at": publish_time,
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

def post_to_ghost_blog(title, content, build_name, tags=None, published_at=None, status="draft"):
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
        
        # YouTube 썸네일 먼저 시도, 실패시 기본 BG3 이미지
        feature_image_url = None
        try:
            from .youtube_fetcher import get_build_thumbnail
            thumbnail_info = get_build_thumbnail(build_name)
            if thumbnail_info and thumbnail_info.get('thumbnail_url'):
                feature_image_url = thumbnail_info['thumbnail_url']
                logger.info(f"✅ YouTube 썸네일 사용: {feature_image_url}")
            else:
                logger.warning("❌ YouTube 썸네일을 찾지 못했습니다. 기본 BG3 이미지 사용")
        except Exception as e:
            logger.warning(f"YouTube 썸네일 검색 중 오류: {e}")
        
        # 기본 BG3 썸네일 이미지 URL (폴백)
        if not feature_image_url:
            feature_image_url = "https://i.namu.wiki/i/YJ42aHyMq-6Ol1p8xL7l1n3ExMbVJtX5UsTu-x2whwmfH-Ae8vEqsyUZHaQjw6pJx4gKv2wKfGj3BLQ4wtgBpye3pee0PX6I_472F0D6LOyQAJUhpqtWW02i6pRy5kRD__yO44e3ngLo5g.webp"
            logger.info("🔄 기본 BG3 썸네일 사용")
        
        # Ghost API로 포스트 생성
        result = ghost.create_post(
            title=title,
            content=content,
            tags=default_tags,
            feature_image=feature_image_url,  # 썸네일 이미지 추가
            meta_title=meta_title,
            meta_description=meta_description,
            status=status,
            published_at=published_at,  # 예약 발행 시간
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