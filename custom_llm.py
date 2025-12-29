from typing import Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel


class NeMoCompatibleGemini(ChatGoogleGenerativeAI):
    """
    Wrapper around Google Gemini that ensures responses are
    compatible with NeMo Guardrails string parsing.
    """

    def _generate(self, messages: List[BaseMessage], **kwargs) -> Any:
        """Override to ensure string output"""
        result = super()._generate(messages, **kwargs)

        # Extract text content and ensure it's a string
        if hasattr(result, "generations"):
            for generation in result.generations:
                if hasattr(generation, "message"):
                    if isinstance(generation.message.content, list):
                        # Convert list to string
                        generation.message.content = "\n".join(
                            str(item) for item in generation.message.content
                        )
                    elif not isinstance(generation.message.content, str):
                        generation.message.content = str(generation.message.content)

        return result

    async def _agenerate(self, messages: List[BaseMessage], **kwargs) -> Any:
        """Async version"""

        print("🧠 Gemini'ye giden mesaj uzunluğu (char):", len(str(messages)))

        result = await super()._agenerate(messages, **kwargs)

        if hasattr(result, "generations"):
            for generation in result.generations:
                if hasattr(generation, "message"):
                    if isinstance(generation.message.content, list):
                        generation.message.content = "\n".join(
                            str(item) for item in generation.message.content
                        )
                    elif not isinstance(generation.message.content, str):
                        generation.message.content = str(generation.message.content)

        return result
