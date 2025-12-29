from typing import Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel


class NeMoCompatibleGemini(ChatGoogleGenerativeAI):
    """
    Wrapper around Google Gemini with debugging for NeMo Guardrails
    """

    def _sanitize_kwargs(self, kwargs: Any) -> Any:
        """Fix max_tokens -> max_output_tokens"""
        if "max_tokens" in kwargs:
            val = kwargs.pop("max_tokens")
            if "max_output_tokens" not in kwargs:
                kwargs["max_output_tokens"] = val
        return kwargs

    async def _agenerate(self, messages: List[BaseMessage], **kwargs) -> Any:
        """Async version with debugging"""

        kwargs = self._sanitize_kwargs(kwargs)

        # DEBUG: Gemini'ye ne gönderildiğini gör
        message_content = messages[-1].content if messages else ""
        print(f"\n📤 GEMINI'YE GÖNDERİLEN:")
        print(f"   {message_content[:200]}...")

        try:
            result = await super()._agenerate(messages, **kwargs)
        except Exception as e:
            print(f"❌ GEMINI API HATASI: {e}")
            raise e

        # DEBUG: Gemini'nin cevabını gör
        if hasattr(result, "generations") and result.generations:
            raw_response = result.generations[0].message.content
            print(f"\n📥 GEMINI'NİN CEVABI:")
            print(f"   RAW: '{raw_response}'")

            # String formatına çevir
            if isinstance(raw_response, list):
                result.generations[0].message.content = "\n".join(
                    str(item) for item in raw_response
                )
            elif not isinstance(raw_response, str):
                result.generations[0].message.content = str(raw_response)

            # Temizlenmiş halini göster
            clean_response = result.generations[0].message.content.strip()
            print(f"   CLEAN: '{clean_response}'")

        return result
