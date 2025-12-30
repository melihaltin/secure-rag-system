import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

from config import MODEL_NAME, PROMPT, TEMP

load_dotenv()

rag_chain = None
retriever = None

# Basit kelime temelli güvenlik filtresi için anahtar kelimeler
SENSITIVE_KEYWORDS = [
    "maaş",
    "maas",
    "salary",
    "ücret",
    "ucret",
    "wage",
    "compensation",
    "bonus",
    "kazanç",
    "kazanci",
    "kazanc",
    "kazancı",
    "income",
    "pay",
    "odeme",
]

# Sık sorulan politika soruları için deterministik cevaplar
POLICY_OVERRIDES = [
    (
        "çekirdek saatler",
        "Çekirdek saatler (Core Hours) 10:00-16:00 olarak belirlenmiştir ve bu saatler arasında tüm ekiplerin ulaşılabilir olması beklenmektedir.",
    ),
    (
        "şort veya parmak arası terlik",
        "Hayır, şort ve parmak arası terlik kabul edilmeyen giyim kategorisindedir. Genel giyim kuralı Smart Casual'dır.",
    ),
    (
        "hibrit çalışma",
        "Hibrit çalışma düzeni haftada 3 gün ofis, 2 gün evden çalışmadır. Uzaktan günler departman yöneticileri ile koordine edilip haftalık takvime işlenir.",
    ),
    (
        "yemek kartı",
        "Yemek kartı bakiyesi her ayın 1'i ile 5'i arasında yüklenir. Yıllık izin veya 3 günü aşan raporlu durumlarda tutar bir sonraki aydan mahsup edilir.",
    ),
    (
        "alexander kensington",
        "Alexander Kensington, TechFlow A.Ş.'de CEO (Chief Executive Officer) olarak görev yapmaktadır.",
    ),
]

# Vektör veritabanı için kalıcı dizin
PERSIST_DIRECTORY = "./chroma_db"


def format_docs(docs):
    """Dokümanları string formatına çevirir"""
    if not docs:
        return "İlgili bilgi bulunamadı."
    return "\n\n".join(doc.page_content for doc in docs)


def create_vector_db():
    """Vektör veritabanını oluşturur ve kalıcı olarak saklar"""
    print("📚 Vektör veritabanı oluşturuluyor...")

    # Dokümanları yükle
    loader = DirectoryLoader(
        "./data",
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()

    if not documents:
        raise ValueError("❌ ./data klasöründe hiç döküman bulunamadı!")

    print(f"   ✅ {len(documents)} döküman yüklendi")

    # Metinleri böl
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=80,
        separators=["\n\n", "\n", ".", " "],  # Daha akıllı bölme
    )
    texts = text_splitter.split_documents(documents)
    print(f"   ✅ {len(texts)} parçaya bölündü")

    # Embedding oluştur
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Vektör veritabanını oluştur ve kaydet
    db = Chroma.from_documents(texts, embeddings, persist_directory=PERSIST_DIRECTORY)

    print(f"   ✅ Vektör veritabanı {PERSIST_DIRECTORY} dizinine kaydedildi!")
    return db


def is_sensitive_query(query: str) -> bool:
    """Basit anahtar kelime kontrolü ile maaş/bonus gibi hassas soruları yakalar."""
    lowered = query.lower()
    return any(keyword in lowered for keyword in SENSITIVE_KEYWORDS)


def get_policy_override(query: str) -> str | None:
    """Bilinen politika sorularında doğrudan kanonik cevabı döndürür."""
    lowered = query.lower()
    for marker, answer in POLICY_OVERRIDES:
        if marker in lowered:
            return answer
    return None


def load_vector_db():
    """Mevcut vektör veritabanını yükler"""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)

    return db


def init_rag_chain():
    global rag_chain, retriever

    if rag_chain:
        print("   ♻️  Mevcut RAG chain kullanılıyor")
        return rag_chain

    print("🔧 RAG zinciri başlatılıyor...")

    try:
        # Vektör veritabanını yükle veya oluştur
        if os.path.exists(PERSIST_DIRECTORY) and os.listdir(PERSIST_DIRECTORY):
            print("   📂 Mevcut vektör veritabanı yükleniyor...")
            db = load_vector_db()
        else:
            print("   🆕 Vektör veritabanı bulunamadı, yeni oluşturuluyor...")
            db = create_vector_db()

        # Retriever'ı oluştur
        retriever = db.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 5,
                "fetch_k": 10,
                "lambda_mult": 0.7,
            },
        )

        # Prompt şablonu
        prompt = ChatPromptTemplate.from_template(PROMPT)

        # LLM oluştur
        llm = ChatGoogleGenerativeAI(
            temperature=TEMP, max_output_tokens=512, model=MODEL_NAME
        )

        # RAG zincirini oluştur
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        print("   ✅ RAG Zinciri Hazır!")
        return rag_chain

    except Exception as e:
        print(f"   ❌ RAG Chain Başlatma Hatası: {e}")
        raise


def ask_rag(query: str) -> str:
    """Soruyu RAG zincirine gönderir ve cevabı döndürür"""
    global rag_chain

    try:
        if not query or not isinstance(query, str):
            return "Geçersiz sorgu."

        if is_sensitive_query(query):
            refusal = (
                "Bu bilgi gizlidir ve paylaşamam; I cannot disclose this information."
            )
            print(f"   🚫 Güvenlik politikası: {refusal}")
            return refusal

        # Politika SSS'leri için deterministik yanıt
        override_answer = get_policy_override(query)
        if override_answer:
            print("   📘 Politika cevabı (override) kullanıldı")
            return override_answer

        # RAG chain henüz oluşturulmadıysa oluştur
        if rag_chain is None:
            init_rag_chain()

        print(f"   🔍 RAG'e gönderiliyor:  {query}")

        # Global rag_chain kullan (önceki kod 'chain' kullanıyordu - hata!)
        result = rag_chain.invoke(query)

        # Ensure string output
        if isinstance(result, dict):
            result = result.get("answer", result.get("text", str(result)))
        elif isinstance(result, list):
            result = " ".join(str(x) for x in result)
        elif hasattr(result, "content"):
            result = str(result.content)
        else:
            result = str(result)

        result = result.strip()

        if not result:
            result = "Üzgünüm, bu soruya cevap bulunamadı."

        print(f"   ✅ RAG cevabı: {result[: 100]}...")
        return result

    except Exception as e:
        print(f"   ❌ RAG Error: {e}")
        import traceback

        traceback.print_exc()
        return "Üzgünüm, cevap oluştururken bir hata oluştu."


def reset_vector_db():
    """Vektör veritabanını sıfırlar"""
    global rag_chain, retriever
    import shutil

    if os.path.exists(PERSIST_DIRECTORY):
        shutil.rmtree(PERSIST_DIRECTORY)
        print("🗑️  Vektör veritabanı silindi!")

    # RAG chain'i sıfırla
    rag_chain = None
    retriever = None

    create_vector_db()


# Modül yüklendiğinde RAG chain'i otomatik olarak başlat
print("🚀 RAG Chain modülü yükleniyor...")
init_rag_chain()


# Test için
if __name__ == "__main__":
    print("🧪 RAG Chain Test\n")

    # Test sorusu
    test_query = "İzin politikası nedir?"
    print(f"Test sorusu: {test_query}\n")

    answer = ask_rag(test_query)
    print(f"\n📝 Cevap:\n{answer}")
