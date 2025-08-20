from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from googlenewsdecoder import new_decoderv1
from gnews import GNews


llm = ChatOllama(model='exaone3.5:7.8b')

class NewsState(TypedDict):
    input: str # 입력 뉴스 기사,
    article_result: str # 검색 결과
    keyword_summary: str # 요약 결과
    fact_check: str # 팩트체크 결과
    verdict: str # 최종 판단
    reference: str # 출처
    

# 1. 키워드 추출
def extract_keyword(state: NewsState):
    text = state['input']
    prompt = ChatPromptTemplate([('system', 'You are a professional keyword extractor.'),
                                 ('human', '''Extract the core keywords from the following sentence:
                                        - Preserve the meaning and context of the sentence.
                                        - Focus on people, locations, and events.
                                        - Connect related expressions as much as possible.
                                        - Output the result as a space-separated string of keywords in Korean.

                                        Sentence: {text}''')])
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
        url = decode_url(item['url'])
        article = google_news.get_full_article(url).title + '\n' + google_news.get_full_article(url).text
        article_list.append(article)
    
    # 검색 결과 정리
    article_result = '\n'.join(map(str, article_list))
    state['article_result'] = article_result


    # LLM 프롬프트
    prompt = ChatPromptTemplate(
        [
            ('system','You are a professional fact-checker.'),
            ('human','''Here is User's query to ask whether it is true or not :
             {query}
        
        Here are recent related news search results:
        {article_result}

        Task:
        1. Summarize the news articles concisely.
        2. Extract the core claims and distinguish them from factual information.
        3. Highlight any signs of misinformation: exaggeration, lack of source, or logical fallacies.
        4. Identify the inputs and infer its political orientation (e.g., conservative, liberal, centrist, unknown).
        
        Please write all outputs in Korean.
        ''')])

    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({'query': query, 'article_result': article_result})

    state['fact_check'] = result
    return state

# 3. 평가
def evaluate(state: NewsState):
    fact_result = state['fact_check']
    prompt = ChatPromptTemplate([
        ('system', 'You are a fake news detection expert.'),
        ('human', 'Based on the following fact-checking result, determine if the original news is likely real or fake. Provide a short explanation in Korean:\n{fact_result}')
    ])
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
    
    
    