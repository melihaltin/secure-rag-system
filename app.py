import os
import re
from dotenv import load_dotenv
from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.actions import action
from config import MODEL_NAME, TEMP
from custom_llm import NeMoCompatibleGemini
from rag_chain import ask_rag

load_dotenv()


@action(name="call_rag", is_system_action=True)
async def call_rag_action(context: dict = None, query: str = None) -> str:
    """RAG chain wrapper for NeMo Guardrails"""
    try:
        # Extract query from context if not provided directly
        if query is None and context:
            query = context.get("user_message", context.get("last_user_message", ""))

        if not query:
            print("   ⚠️  Query bulunamadı!")
            return "Üzgünüm, sorunuzu anlayamadım."

        print(f"   📝 RAG Query: {query}")

        # Call the RAG chain
        response = ask_rag(query)

        # Ensure string output
        result = str(response).strip()

        if not result:
            result = "Üzgünüm, bu soruya cevap bulunamadı."

        print(f"   ✅ RAG Response: {result[:100]}...")

        # Update context
        if context:
            context["rag_response"] = result

        return result

    except Exception as e:
        print(f"   ❌ RAG Action Error: {e}")
        import traceback

        traceback.print_exc()
        return "Üzgünüm, cevap oluştururken bir hata oluştu."


@action(name="check_salary_regex", is_system_action=True)
async def check_salary_regex_action(context: dict = None, text: str = None) -> bool:
    """Check for salary information patterns"""
    try:
        # Get text from context if not provided
        if text is None and context:
            text = context.get("bot_message", context.get("last_bot_message", ""))

        if not text or not isinstance(text, str):
            return False

        pattern = r"\d{2,3}[\.,]\d{3}\s*TL"
        match = re.search(pattern, text)

        if match:
            print(f"   🚨 Salary data detected: {match.group()}")
            if context:
                context["contains_salary"] = True

        return bool(match)

    except Exception as e:
        print(f"   ❌ Regex Check Error: {e}")
        return False


@action(name="check_input_for_salary", is_system_action=True)
async def check_input_for_salary_action(context: dict = None, text: str = None) -> bool:
    """Check if input contains salary-related keywords"""
    try:
        if text is None and context:
            text = context.get("last_user_message", context.get("user_message", ""))

        if not text or not isinstance(text, str):
            return False

        text_lower = text.lower()

        # Maaş ile ilgili anahtar kelimeler (Türkçe ve İngilizce)
        salary_keywords = [
            # İngilizce
            "salary",
            "salaries",
            "wage",
            "wages",
            "income",
            "earn",
            "earning",
            "payroll",
            "compensation",
            "pay rate",
            "pay scale",
            "bonus",
            "net income",
            "gross income",
            "financial",
            "money",
            "paid",
            # Türkçe
            "maaş",
            "maas",
            "ücret",
            "ucret",
            "gelir",
            "kazanç",
            "kazanc",
            "ödeme",
            "odeme",
            "bordro",
            "prim",
            "zam",
            "net gelir",
            "brüt",
            # CEO/Yönetici spesifik
            "executive",
            "manager salary",
            "director salary",
            "yönetici maaş",
            "müdür maaş",
            "patron",
        ]

        for keyword in salary_keywords:
            if keyword in text_lower:
                print(f"   🚨 Salary keyword detected in input: {keyword}")
                return True

        # Regex pattern for salary amounts
        import re

        salary_pattern = r"\d{2,3}[\.,]\d{3}\s*(TL|tl|₺|lira)"
        if re.search(salary_pattern, text):
            print(f"   🚨 Salary amount pattern detected in input")
            return True

        return False

    except Exception as e:
        print(f"   ❌ Input Check Error: {e}")
        return False


def main():
    print("🛡️  HR Guard Sistemi Başlatılıyor...\n")

    try:
        # Load base config
        config_path = "./config"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"❌ Config klasörü bulunamadı: {config_path}")

        print(f"📂 Config yükleniyor: {config_path}")
        config = RailsConfig.from_path(config_path)

        # Create custom LLM instance
        custom_llm = NeMoCompatibleGemini(
            model=MODEL_NAME, temperature=TEMP, max_output_tokens=256
        )

        # Initialize rails with custom LLM
        print("🔧 Rails başlatılıyor...")
        app = LLMRails(config, llm=custom_llm)

        # Register actions
        app.register_action(call_rag_action, name="call_rag")
        app.register_action(check_salary_regex_action, name="check_salary_regex")
        app.register_action(
            check_input_for_salary_action, name="check_input_for_salary"
        )

        print("✅ Action'lar kaydedildi")

        print("\n" + "=" * 50)
        print("✅ SİSTEM HAZIR! (Çıkmak için 'exit' yazın)")
        print("=" * 50 + "\n")

        # Chat loop
        while True:
            try:
                user_input = input("\n👤 Çalışan: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "q", "çıkış", "quit"]:
                    print("\n👋 Güle güle!")
                    break

                print(f"\n🔄 İşleniyor...")

                # Generate response
                response = app.generate(
                    messages=[{"role": "user", "content": user_input}]
                )

                # Extract content safely
                if isinstance(response, dict):
                    content = response.get("content", "")
                elif isinstance(response, str):
                    content = response
                elif hasattr(response, "content"):
                    content = response.content
                else:
                    content = str(response)

                if content and content.strip():
                    print(f"\n🤖 HR Guard: {content}")
                else:
                    print("\n🤖 HR Guard: Üzgünüm, bir cevap oluşturamadım.")

            except KeyboardInterrupt:
                print("\n\n👋 Güle güle!")
                break
            except Exception as e:
                print(f"\n❌ İşlem Hatası: {e}")
                import traceback

                traceback.print_exc()

    except Exception as e:
        print(f"\n❌ Başlatma Hatası: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
