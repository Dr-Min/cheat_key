import os
from pathlib import Path

# utils.py에 있는 경로 계산 방식
current_file = __file__
print(f"Current file: {current_file}")

file_dir = os.path.dirname(current_file)
print(f"File directory: {file_dir}")

parent_dir = os.path.dirname(file_dir)
print(f"Parent directory: {parent_dir}")

dotenv_path = os.path.join(parent_dir, '.env')
print(f"Expected .env path: {dotenv_path}")

# .env 파일이 존재하는지 확인
exists = os.path.exists(dotenv_path)
print(f"Does .env file exist at this path? {exists}")

# 현재 작업 디렉토리 확인
cwd = os.getcwd()
print(f"Current working directory: {cwd}")

# 현재 디렉토리에 .env가 있는지 확인
alt_path = os.path.join(cwd, '.env')
print(f"Alternative .env path: {alt_path}")
print(f"Does .env file exist at alternative path? {os.path.exists(alt_path)}")

# 파일 내용 출력 시도
if os.path.exists(dotenv_path):
    print("Content of .env file:")
    with open(dotenv_path, 'r') as f:
        print(f.read())
elif os.path.exists(alt_path):
    print("Content of alternative .env file:")
    with open(alt_path, 'r') as f:
        print(f.read()) 