import os
import logging
import re
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 로깅 설정
def setup_logging(log_file='bg3_automation.log', level=logging.INFO):
    """로깅 설정"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

# 기본 로거 설정
logger = setup_logging()

# 환경변수 로드
def load_env_vars():
    """환경변수(.env 파일) 로드"""
    # 방법 1: 현재 작업 디렉토리에서 .env 파일 찾기
    dotenv_path = os.path.join(os.getcwd(), '.env')
    
    # 방법 2: 기존 경로 계산 방식 (상위 디렉토리)
    alt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    
    # 두 경로 모두 확인
    if os.path.exists(dotenv_path):
        logger.info(f".env 파일 로드: {dotenv_path}")
        load_dotenv(dotenv_path, encoding="utf-8-sig")  # BOM 처리를 위한 encoding 추가
    elif os.path.exists(alt_path):
        logger.info(f".env 파일 로드: {alt_path}")
        load_dotenv(alt_path, encoding="utf-8-sig")  # BOM 처리를 위한 encoding 추가
    else:
        logger.warning(f".env 파일을 찾을 수 없습니다. 다음 경로에서 확인: {dotenv_path}, {alt_path}")
    
    # 필수 환경변수 체크
    required_vars = [
        'PERPLEXITY_API_KEY',
        'GROK_API_KEY',
        'GHOST_ADMIN_API_URL',
        'GHOST_API_KEY',
        'GHOST_INTEGRATION_ID'
    ]
    
    # 환경변수 값 디버깅
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logger.debug(f"환경변수 '{var}' 로드됨: {value[:5]}...")
        else:
            logger.warning(f"환경변수 '{var}'를 찾을 수 없습니다.")
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"다음 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
    
    return {var: os.getenv(var) for var in required_vars}

# 환경변수 로드 실행
env_vars = load_env_vars()

def save_json_response(data, prefix="api_response"):    """API 응답을 JSON 파일로 저장"""    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")    filename = f"{prefix}_{timestamp}.json"        with open(filename, "w", encoding="utf-8") as f:        json.dump(data, f, ensure_ascii=False, indent=2)        logger.info(f"API 응답이 '{filename}' 파일에 저장되었습니다.")    return filenamedef save_build_data(build_name, english_info, korean_info, extracted_terms=None):    """빌드 정보를 구조화된 형태로 저장"""    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")    filename = f"build_data_{build_name.replace(' ', '_')}_{timestamp}.json"        build_data = {        "build_name": build_name,        "timestamp": timestamp,        "english_build_info": english_info,        "korean_blog_post": korean_info,        "extracted_terms": extracted_terms or {},        "metadata": {            "source": "perplexity_api",             "translator": "grok_api",            "version": "2.0_with_term_extraction"        }    }        try:        with open(filename, 'w', encoding='utf-8') as f:            json.dump(build_data, f, ensure_ascii=False, indent=2)        logger.info(f"통합 빌드 데이터가 {filename}에 저장되었습니다.")        return filename    except Exception as e:        logger.error(f"빌드 데이터 저장 중 오류: {e}")        return None

def generate_filename(build_name, prefix="bg3", suffix="build", ext="md"):
    """빌드명으로 안전한 파일명 생성"""
    # 빌드명에서 공백 및 특수문자 제거 후 스네이크 케이스로 변환
    safe_build_name = build_name.lower().replace(" ", "_").replace("'", "").replace("-", "_")
    
    current_date = datetime.now().strftime("%Y%m%d")
    return f"{prefix}_{safe_build_name}_{suffix}_{current_date}.{ext}"

def save_to_markdown(content, build_name, output_dir=None):
    """생성된 블로그 포스트를 마크다운 파일로 저장"""
    # 문장 마침표 뒤에 줄바꿈 추가
    content = add_newlines_after_sentences(content)
    
    filename = generate_filename(build_name)
    
    # 출력 디렉토리가 지정된 경우
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
    else:
        filepath = filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"블로그 포스트가 '{filepath}' 파일로 저장되었습니다.")
    return filepath

def add_newlines_after_sentences(content):
    """문장 끝 마침표 뒤에 줄바꿈 추가 (숫자 사이 소수점 제외)"""
    logger.info("문장 끝 마침표 뒤에 줄바꿈 추가 중...")
    
    # 마크다운 코드 블록, 링크, 이미지 등 보존을 위한 임시 대체
    code_blocks = []
    links = []
    images = []
    
    # 코드 블록 임시 대체
    def replace_code_block(match):
        code_blocks.append(match.group(0))
        return f"CODE_BLOCK_{len(code_blocks)-1}"
    content = re.sub(r'```[\s\S]*?```', replace_code_block, content)
    
    # 링크 임시 대체
    def replace_link(match):
        links.append(match.group(0))
        return f"LINK_{len(links)-1}"
    content = re.sub(r'\[.*?\]\(.*?\)', replace_link, content)
    
    # 이미지 임시 대체
    def replace_image(match):
        images.append(match.group(0))
        return f"IMAGE_{len(images)-1}"
    content = re.sub(r'!\[.*?\]\(.*?\)', replace_image, content)
    
    # 테이블 행은 처리하지 않도록 표시
    table_rows = []
    def replace_table_row(match):
        table_rows.append(match.group(0))
        return f"TABLE_ROW_{len(table_rows)-1}"
    content = re.sub(r'\|.*\|', replace_table_row, content)
    
    # 1. 숫자 사이의 소수점은 임시 문자로 대체
    content = re.sub(r'(\d)\.(\d)', r'\1#DECIMAL#\2', content)
    
    # 2. 버전 번호 등 특수 패턴 보호
    content = re.sub(r'(v\d+)\.([\d]+)', r'\1#DECIMAL#\2', content)
    content = re.sub(r'(\[\d+)\.([\d]+\])', r'\1#DECIMAL#\2', content)
    
    # 3. 마크다운 헤더는 처리하지 않음
    def preserve_header(match):
        return match.group(0).replace('.', '#HEADER_DOT#')
    content = re.sub(r'#+\s+[^\n]*', preserve_header, content)
    
    # 4. 문장 끝 마침표 패턴 찾기 
    # - 마침표 + 공백 + 다음 글자 패턴
    # - 마침표 + 줄바꿈이 아닌 경우
    content = re.sub(r'\.(?= )', '.\n', content)
    
    # 5. 임시 문자들 복원
    content = content.replace('#DECIMAL#', '.')
    content = content.replace('#HEADER_DOT#', '.')
    
    # 코드 블록, 링크, 이미지 복원
    for i, block in enumerate(code_blocks):
        content = content.replace(f"CODE_BLOCK_{i}", block)
    for i, link in enumerate(links):
        content = content.replace(f"LINK_{i}", link)
    for i, image in enumerate(images):
        content = content.replace(f"IMAGE_{i}", image)
    for i, row in enumerate(table_rows):
        content = content.replace(f"TABLE_ROW_{i}", row)
    
    # 중복된 줄바꿈 제거 (최대 2개까지 허용)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    logger.info("문장 끝 마침표 뒤 줄바꿈 처리 완료")
    return content 