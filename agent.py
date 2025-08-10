from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os


llm = ChatOllama(model='exaone3.5:7.8b')

class NewsState(TypedDict):
    input: str # 입력 뉴스 기사,
    summary: str # 요약 결과
    fact_check: str # 팩트체크 결과
    verdict: str # 최종 판단
    score: Optional[float] # 신뢰도 점수
    url: str # 출처
    

# 뉴스 긁어오기
def get_news(state: NewsState):
    keyword = state['input']
    
    

# 1. 뉴스 요약
def summarize(state: NewsState):
    text = state['input']
    prompt = PromptTemplate.from_template('Please summarize the following news article concisely:\n{text}')
    chain = prompt | llm | StrOutputParser()
    summary = chain.invoke({'text': text})
    state['summary'] = summary
    return state

# 2. 팩트체킹
def fact_check(state: NewsState):
    summary = state['summary']
    prompt = ChatPromptTemplate(
        [
        SystemMessage(content="You are a professional fact-checker."),
        HumanMessage(content=f"Please assess the factual accuracy of the following summary based on known facts or reliable external sources:\n{summary}")
        ]
    )
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({'summary': summary})
    state['fact_check'] = result
    return state

# 3. 분류
def classify_news(state: NewsState):
    fact_result = state['fact_check']
    prompt = ChatPromptTemplate([
        SystemMessage(content="You are a fake news detection expert."),
        HumanMessage(content=f"Based on the following fact-checking result, determine if the original news is likely real or fake. Provide a short explanation:\n{fact_result}")
    ])
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({'fact_result': fact_result})
    state['verdict'] = result
    return state

# 4. Output node
def output_node(state: NewsState):
    print("\n📰 Input News:\n", state['input'])
    print("\n📝 Summary:\n", state['summary'])
    print("\n🔍 Fact-checking:\n", state['fact_check'])
    print("\n📢 Final Verdict:\n", state['verdict'])
    return state

# Build Graph
def run_graph(input):
    builder = StateGraph(NewsState)
    builder.add_node('Summarize', summarize)
    builder.add_node('FactCheck', fact_check)
    builder.add_node('Classify', classify_news)
    builder.add_node('Output', output_node)

    builder.set_entry_point('Summarize') # 요약부터 시작
    builder.add_edge('Summarize', 'FactCheck')
    builder.add_edge("FactCheck", "Classify")
    builder.add_edge("Classify", "Output")
    builder.add_edge("Output", END)

    graph = builder.compile()
    return graph.invoke({'input': input})
    
    
    