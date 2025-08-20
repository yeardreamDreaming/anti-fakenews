# FakeGuard
FakeGuard 뉴스 리터러시 팩트체크


## 사용 방법
먼저, git clone을 활용하여 레포지토리를 clone 해옵니다
```bash 
git clone https://github.com/yeardreamDreaming/fakeguard.git
```

이 프로젝트를 사용하시기 위해서는 기본적으로 파이썬과 ollama 설치가 필수적입니다.

우선, 다음과 같은 명령어로 파이썬 가상 환경을 먼저 만듭니다.
```bash 
python -m venv .venv
```

이후 다음 명령어로 파이썬 필수 패키지들을 설치합니다.
```bash
pip install -r requirements.txt
```

ollama를 설치하시고, 윈도우 파워쉘(또는 cmd)나 터미널(리눅스, 맥) 창에서 ollama pull exaone3.5:7.8b 명령어로 ollama 모델을 설치합니다.
이후, 터미널 혹은 커맨드 창에서 python run.py를 통하여 실행하시면 자동으로 모델이 설치되며, 스트림릿 앱이 구동됩니다.
스트림릿에서는 귀동냥으로 들은 카더라 통신이나, 뉴스 내용을 복사 혹은 요약해서 입력으로 넣으시고 분석을 진행하시면 다음과 같이 분석이 진행됩니다.

종료하실때는 터미널/파워쉘 창을 닫으시면 자동으로 종료됩니다.

## 분석 예(이미지)
[!분석 이미지 1](./examples/ab1.png)
[!분석 이미지 2](./examples/ab2.png)