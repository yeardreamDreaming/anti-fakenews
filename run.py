import subprocess
import time
import sys
import os


def run():
    # ollama pull -> ollama run -> streamlit run app.py
    print('모델 다운로드 중...')
    subprocess.run(['ollama', 'pull', 'exaone3.5:7.8b'], check=True)
    
    print('모델 불러오는 중...')
    ollama_proc = subprocess.Popen(['ollama', 'run', 'exaone3.5:7.8b'])
    
    # 서버 실행을 위한 잠시 대기
    time.sleep(3)
    
    # 스트림릿 앱 실행
    print('스트림릿 앱 실행중...')
    try:
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    finally:
        ollama_proc.terminate()
    
if __name__ == '__main__':
    run()
    
    
    
    