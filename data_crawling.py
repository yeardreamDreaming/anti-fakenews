import bs4
import os
from urllib import parse, request
import json
from dotenv import load_dotenv, find_dotenv


def get_news(url):
    dotenv_file = find_dotenv()
    load_dotenv(dotenv_file)

    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')

    encText = parse.quote("대한민국 육상")

    url = "https://openapi.naver.com/v1/search/news.json?query=" + encText # JSON 결과

    req = request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)
    response = request.urlopen(req)
    rescode = response.getcode()

    if(rescode==200):
        response_body = response.read()
        data = response_body.decode('utf-8')
        contents = json.loads(data)
        print(f'{contents['display']}개만 추출합니다!')
        for content in contents['items']:
            print(f'뉴스 제목 : {content['title']}')
            print(f'뉴스 URL: {content['originallink']}')
            print(f'뉴스 내용 : {content['description']}')
            print(f'뉴스 업로드일자: {content['pubDate']}')
    else:
        print("Error Code:" + rescode)