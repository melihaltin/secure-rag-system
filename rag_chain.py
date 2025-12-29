import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

qa_chain = None


def init_rag_chain():

    global qa_chain

    if qa_chain:
        return qa_chain

    print("data is loading... and RAG chain is initializing...")

    loader = DirectoryLoader("./data", glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    db = Chroma.from_documents(texts, embeddings)

    retriever = db.as_retriever(search_kwargs={"k": 2})

    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(temperature=0), chain_type="stuff", retriever=retriever
    )

    print("RAG Chain is Ready!")
    return qa_chain


def ask_rag(query):
    chain = init_rag_chain()
    result = chain.invoke(query)
    return result["result"]
