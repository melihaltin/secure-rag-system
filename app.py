import os
import asyncio
from dotenv import load_dotenv
from nemoguardrails import LLMRails, RailsConfig

# RAG zincirini çağırıyoruz
from rag_chain import ask_rag

load_dotenv()


# --- Action Tanımlama ---
# NeMo Guardrails, Colang içindeki 'execute call_rag(...)' komutunu görünce
# Python tarafında bu fonksiyonu arayacak.
async def call_rag(query: str):
    """
    Colang tarafından çağrılan, LangChain RAG'a giden köprü fonksiyon.
    """
    # Senkron fonksiyonu asenkron içinde çalıştırmak için basit bir wrapper
    # (Gerçek prodüksiyonda async destekli RAG zinciri kullanmak daha iyidir)
    print(f"   Drafting RAG answer for: {query}...")  # Loglama, terminalde görmen için
    response = ask_rag(query)
    return response


def main():
    print("🛡️  HR Guard Sistemi Başlatılıyor...")

    # 1. Konfigürasyonu Yükle
    config = RailsConfig.from_path("./config")

    # 2. Guardrails Uygulamasını Başlat
    app = LLMRails(config)

    # 3. Action'ı (Fonksiyonu) Kaydet
    # Colang dosyasındaki 'call_rag' ismini Python'daki 'call_rag' fonksiyonuna bağlıyoruz.
    app.register_action(action=call_rag, name="call_rag")

    print("\n✅ SİSTEM HAZIR! (Çıkmak için 'exit' yazın)\n")
    print("-" * 50)

    # 4. Chat Döngüsü
    while True:
        try:
            user_input = input("\n👤 Çalışan: ")

            if user_input.lower() in ["exit", "q", "çıkış"]:
                print("👋 Güle güle!")
                break

            # Guardrails üzerinden cevabı al
            # Bu fonksiyon önce 'Input Rail' (topics.co) kontrolü yapar.
            # Yasaklıysa bloklar, değilse 'answer_general_hr' akışına girip RAG'ı çağırır.
            response = app.generate(messages=[{"role": "user", "content": user_input}])

            # Cevabı yazdır
            print(f"🤖 HR Guard: {response['content']}")

        except Exception as e:
            print(f"❌ Bir hata oluştu: {e}")


if __name__ == "__main__":
    main()
