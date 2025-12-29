import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader

# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

rag_chain = None
retriever = None


def format_docs(docs):
    """Dokümanları string formatına çevirir"""
    return "\n\n".join(doc.page_content for doc in docs)


def init_rag_chain():
    global rag_chain, retriever

    if rag_chain:
        return rag_chain

    print("Veriler yükleniyor ve RAG zinciri başlatılıyor...")

    # Dokümanları yükle
    loader = DirectoryLoader("./data", glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()

    # Metinleri böl
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    # Embedding ve vektör veritabanı oluştur
    embeddings = GoogleGenerativeAIEmbeddings()
    db = Chroma.from_documents(texts, embeddings)

    # Retriever'ı global değişkene ata
    retriever = db.as_retriever(search_kwargs={"k": 2})

    # Prompt şablonu oluştur
    prompt = ChatPromptTemplate.from_template(
        """Aşağıdaki bağlama göre soruyu cevapla. 
        Eğer cevabı bağlamda bulamazsan, "Bu sorunun cevabını verilen dokümanlarda bulamadım" de.
        
Bağlam:
{context}

Soru: {question}

Cevap:"""
    )

    # LLM oluştur
    llm = ChatGoogleGenerativeAI(
        temperature=0, max_output_tokens=512, model="gemini-flash-latest"
    )

    # RAG zincirini oluştur (yeni LCEL syntax)
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("RAG Zinciri Hazır!")
    return rag_chain


def ask_rag(query):
    """Soruyu RAG zincirine gönderir ve cevabı döndürür"""
    chain = init_rag_chain()
    result = chain.invoke(query)
    return result


# Test için örnek kullanım
if __name__ == "__main__":
    # Örnek soru
    answer = ask_rag("Benim sorum nedir?")
    print(f"\nCevap: {answer}")
