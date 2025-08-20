from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from googlenewsdecoder import new_decoderv1
from gnews import GNews
from newspaper import Article

llm = ChatOllama(model='exaone3.5:7.8b')

class NewsState(TypedDict):
    input: str # 입력 뉴스 기사,
    article_result: list # 검색 결과
    keyword_summary: str # 요약 결과
    fact_check: str # 팩트체크 결과
    verdict: str # 최종 판단
    reference: str # 출처
    

# 1. 키워드 추출
def extract_keyword(state: NewsState):
    text = state['input']
    prompt = ChatPromptTemplate([('system', '당신은 전문 키워드 추출가입니다.'),
    ('human', '''
        다음 문장에서 사람, 장소, 사건, 날짜 중심으로 핵심 키워드를 추출하세요.
        - 의미와 문맥을 보존하세요.
        - 관련 표현이나 다중 단어는 "_"로 연결하세요.
        - 날짜나 시간 표현도 하나의 단위로 묶으세요.
        - 키워드끼리는 공백으로 구분하세요.
        - 출력 예시는 다음과 같습니다:
        예: "도널드_트럼프 블라디미르_푸틴 알래스카_정상회담 2025년_8월"
        문장: {text}
    ''')])

    chain = prompt | llm | StrOutputParser()
    summary = chain.invoke({'text': text})
    state['keyword_summary'] = summary.strip()
    return state

# 2. 팩트체킹
def fact_check(state: NewsState):
    query = state['input']
    
     # 관련 기사 검색해서 검색 결과 가져오기
    def decode_url(url):

        interval_time = 5 # default interval is None, if not specified
        try:
            decoded_url = new_decoderv1(url, interval=interval_time)
            if decoded_url.get("status"):
                return decoded_url["decoded_url"]
            else:
                print("Error:", decoded_url["message"])
        except Exception as e:
            print(f"Error occurred: {e}")

    google_news = GNews(language='ko', country='KR', max_results=10)

    # 검색하고자 하는 주제입력
    resp = google_news.get_news(state['keyword_summary'])

    # 데이터 찾기
    article_list = []
    for item in resp:
        # 구글뉴스 url 디코딩하여 article 가져온다
        try:
            url = decode_url(item['url'])
            article = Article(url)
            article.download()
            article.parse()
            article_title = article.title
            article_content = article.text
            article_list.append({'title': article_title, 'article_content': article_content})
        except Exception as e:
            print(f'예상치 못한 에러 발생!, {e}')
    
    # 검색 결과 정리
    state['article_result'] = article_list

    # LLM 프롬프트
    prompt = ChatPromptTemplate([
        ('system','당신은 전문 팩트체커입니다.'),
        ('human', '''
            사용자 쿼리와 리스트로 주어진 뉴스 검색 결과를 기반으로 사실 여부를 판단하고 문장으로 서술하세요.

            쿼리: {query}
            뉴스 검색 결과: {article_result}

            지침:
            1. 뉴스 검색 결과를 먼저 요약한뒤, 근거로 판단하세요. 
            2. 뉴스 검색 결과 요약시에 관련 없는 군더더기 내용은 제거하세요.
            3. 추측이나 일반 지식에만 의존하지 마세요
            4. 과장, 출처 부족, 논리적 오류 등을 표시해주세요.
            5. 정치적 성향은 "보수, 진보, 중도, 알 수 없음" 중 선택하세요.
            6. 검색 결과를 가져온 것은, 사용자의 쿼리가 사실인지 확인하기 위해서 가져왔습니다. 활용하여서 쿼리가 사실이지 거짓인지 판별해주세요.
    ''')])

    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({'query': query, 'article_result': state['article_result'] })

    state['fact_check'] = result
    return state

# 3. 평가
def evaluate(state: NewsState):
    fact_result = state['fact_check']
    prompt = ChatPromptTemplate([
        ('system', '당신은 가짜 뉴스 탐지 전문가입니다.'),
        ('human', '''
        다음 팩트체크 결과를 기반으로 뉴스의 신뢰도를 평가하고, 각 항목 점수를 0.0~1.0 사이로 배점하세요.
        0점에 가까우면 진실이고, 1점에 가까우면 거짓입니다.

        팩트체크 결과: {fact_result}

        점수 항목:
        - 과장(Exaggeration)
        - 출처 부족(Lack of sources)
        - 논리적 오류(Logical errors)
        - 정치적 편향(Political bias)
        - 전체 허위 가능성(Overall fake probability)
''')])
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({'fact_result': fact_result})
    state['verdict'] = result
    return state


# Build Graph
def run_graph(input):
    builder = StateGraph(NewsState)
    builder.add_node('extract_keyword', extract_keyword)
    builder.add_node('FactCheck', fact_check)
    builder.add_node('evaluate', evaluate)

    builder.set_entry_point('extract_keyword') # 키워드 추출부터 시작
    builder.add_edge("extract_keyword", "FactCheck")
    builder.add_edge("FactCheck", "evaluate")
    builder.add_edge("evaluate", END)


    graph = builder.compile()
    return graph.invoke({'input': input})
    
    
    