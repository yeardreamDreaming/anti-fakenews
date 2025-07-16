from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors.embeddings_filter import EmbeddingsFilter
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from preprocessing import text_preprocessing_for_rag
from langchain.document_loaders import DirectoryLoader, TextLoader
import os
import yaml

def store_or_load_Vectordb(text, embeddings, save_path='./vectordb'):    
    # 저장 경로에 vectordb 저장
    if os.path.exists(os.path.join(save_path, 'index.faiss')):
        return FAISS.load_local(save_path, embeddings)
    else:
        # 벡터스토어 생성
        texts = text_preprocessing_for_rag(text)
        vectordb = FAISS.from_documents(texts, embeddings)
        
        # 로컬에 저장
        os.makedirs(f'{save_path}', exist_ok=True)
        vectordb.save_local(f'{save_path}')
        print(f"FAISS 인덱스가 f'{os.path.abspath(save_path)}' 경로에 저장되었습니다.")
        
        return vectordb
    

def rag(config_path, state):
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # 모델 로드
    model_name = config['model_name']
    embeddings = HuggingFaceEmbeddings(model=config['embedding_model'])
    query = state['query']
    
    # text 데이터 불러와서 전처리
    docs = text_preprocessing_for_rag(config['data_dir'])

    # vectordb
    vectordb = store_or_load_Vectordb(docs, embeddings)
    
    prompt = '''
        [System role]
        You are a professional AI journalist and fact-checking analyst. Your goal is to evaluate a given news article or claim and assess its reliability.

        [Instructions]
        For the input article, do the following:
        1. Summarize the article in 3 paragraphs or fewer.
        2. Identify the media outlet and infer its political orientation (e.g., conservative, liberal, centrist, unknown).
        3. Extract the core claims and distinguish them from factual information.
        4. Fact-check each key claim using general knowledge and plausible reasoning.
        5. Highlight any signs of misinformation: exaggeration, lack of source, or logical fallacies.
        6. Conclude whether the article is:
        - Fact-based
        - Contains exaggeration or misleading framing
        - Fake or highly unreliable

        [Output format]
        - Summary:
        - Media Outlet and Political Bias:
        - Core Claims:
        - Factual Information:
        - Fact-Check Analysis:
        - Final Assessment: [Fact-based / Misleading / Fake News]

        [Input Article]
        <<< INSERT ARTICLE TEXT HERE >>>
        '''

    