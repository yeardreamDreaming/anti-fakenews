import re
import html
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.docstore.document import Document

def loader(data_dir):
    loader = DirectoryLoader(data_dir, glob='**/*.txt', loader_cls=TextLoader)
    
    return loader.load()

def preprocessing(text: str):
    # 전처리 함수입니다.
    
    text = html.unescape(text)
    text = re.sub(r"http[s]?://\S+|www\.\S+", "", text) # url 제거
    text = re.sub(r"\s+", " ", text).strip() # 여러 공백을 공백 하나로 줄임
    
    return text

def text_preprocessing_for_rag(data_dir):
    
    docs = loader(data_dir)
    
    # 전처리 및 분할
    processed_docs = [Document(
        page_content=preprocessing(doc.page_content),
        metadata=doc.metadata
    ) for doc in docs]
    
    # splitter 구현
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700, # 뉴스 기사 평균에 맞게
        chunk_overlap=100, # 문맥 유지
        separators=['\n', '.', ' ', '']
    )
    chunks = splitter.split_documents(processed_docs)
    print(f'총 분할된 청크 수 : {len(chunks)}')
    return chunks

    
    




