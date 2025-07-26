import streamlit as st
from langchain.schema import Document
from langchain_core.runnables import Runnable
from typing import List, Dict
from agent import run_graph

# 봇 만들기
st.set_page_config(page_title="🕵️ 가짜뉴스 탐지 챗봇", page_icon="🧠", layout="wide")

st.title("🕵️ 가짜뉴스 탐지 챗봇")
st.markdown("뉴스 내용이나 의심되는 정보를 입력하면 AI가 팩트체크를 도와줍니다.")

query = st.text_area("📝 뉴스 내용 입력", height=150, placeholder="예: '2025년에 대한민국이 핵무장을 완료했다'...")

if st.button("🔍 확인하기") and query.strip():
    with st.spinner("분석 중..."):
        result = run_graph(query)

    st.success("✅ 분석 완료")

    st.markdown("### 🤖 챗봇의 응답")
    st.write(result["answer"])

    st.markdown("### 📄 근거 문서")
    for i, doc in enumerate(result["sources"]):
        st.markdown(f"**문서 {i+1}**")
        st.info(doc.page_content)

    st.markdown("### 📊 신뢰도 점수")
    st.progress(result["score"])
    st.write(f"Score: **{round(result['score']*100, 2)}%**")

else:
    st.warning("뉴스 문장을 입력하고 버튼을 눌러주세요.")
