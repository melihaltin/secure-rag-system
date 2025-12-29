from typing import Any, List, Optional, Dict
import requests
import aiohttp
from pydantic import Field

from langchain_core.language_models import BaseLanguageModel as LLM
from langchain_core.callbacks.manager import (
    CallbackManagerForLLMRun,
    AsyncCallbackManagerForLLMRun,
)


class NeMoCompatiblePerplexity(LLM):
    """
    NeMo Guardrails uyumlu Perplexity (Sonar) LLM.
    Response'ların string formatında olmasını garanti eder.
    """

    api_key: str
    model: str = "sonar-pro"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)

    # API endpoint
    api_url: str = "https://api.perplexity.ai/chat/completions"

    # Timeout ayarları
    request_timeout: int = 60

    class Config:
        """Pydantic config"""

        extra = "allow"

    @property
    def _llm_type(self) -> str:
        """LLM tipini döndür"""
        return "perplexity"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """LLM'i tanımlayan parametreler"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }

    def _ensure_string_content(self, content: Any) -> str:
        """
        Content'in string olmasını garanti eder.
        NeMo Guardrails string parsing için gerekli.
        """
        if isinstance(content, list):
            # Liste ise string'e çevir
            return "\n".join(str(item) for item in content)
        elif isinstance(content, dict):
            # Dict ise text alanını çıkar veya string'e çevir
            if "text" in content:
                return str(content["text"])
            return str(content)
        elif not isinstance(content, str):
            return str(content)
        return content

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Perplexity API'sine istek gönder

        Args:
            prompt: Gönderilecek prompt
            stop: Durma token'ları
            run_manager: Callback manager
            **kwargs:  Ekstra parametreler

        Returns:
            LLM'den dönen cevap (string olarak garantili)
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }

        if stop:
            payload["stop"] = stop

        payload.update(kwargs)

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.request_timeout,
            )
            response.raise_for_status()

            data = response.json()

            if "choices" not in data or len(data["choices"]) == 0:
                raise ValueError("API'den geçerli bir cevap alınamadı")

            content = data["choices"][0]["message"]["content"]

            # NeMo uyumluluğu için string'e çevir
            text = self._ensure_string_content(content)

            # Stop token kontrolü
            if stop:
                for token in stop:
                    if token in text:
                        text = text.split(token)[0]
                        break

            return text.strip()

        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Perplexity API isteği {self. request_timeout}s içinde yanıt vermedi"
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Perplexity API hatası:  {str(e)}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"API yanıtı parse edilemedi:  {str(e)}")

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Async Perplexity API çağrısı.
        NeMo Guardrails async akışları için optimize edilmiş.
        """

        print("🧠 Perplexity'ye giden mesaj uzunluğu (char):", len(str(prompt)))

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }

        if stop:
            payload["stop"] = stop

        payload.update(kwargs)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.request_timeout),
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

            if "choices" not in data or len(data["choices"]) == 0:
                raise ValueError("API'den geçerli bir cevap alınamadı")

            content = data["choices"][0]["message"]["content"]

            # NeMo uyumluluğu için string'e çevir
            text = self._ensure_string_content(content)

            # Stop token kontrolü
            if stop:
                for token in stop:
                    if token in text:
                        text = text.split(token)[0]
                        break

            return text.strip()

        except aiohttp.ClientTimeout:
            raise TimeoutError(
                f"Perplexity API isteği {self.request_timeout}s içinde yanıt vermedi"
            )
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Perplexity API hatası: {str(e)}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"API yanıtı parse edilemedi: {str(e)}")


# Eski isim için alias (geriye uyumluluk)
PerplexityLLM = NeMoCompatiblePerplexity


# NeMo Guardrails için provider'ı kaydet
def register_perplexity_provider():
    """Perplexity'yi NeMo Guardrails'e kaydet"""
    try:
        from nemoguardrails.llm.providers import register_llm_provider

        register_llm_provider("perplexity", NeMoCompatiblePerplexity)
        print("✅ Perplexity provider kaydedildi")
    except ImportError:
        print("⚠️  nemoguardrails bulunamadı, provider kaydedilmedi")


# Test için
if __name__ == "__main__":
    import os
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("❌ PERPLEXITY_API_KEY bulunamadı!")
    else:
        llm = NeMoCompatiblePerplexity(
            api_key=api_key, model="sonar-pro", temperature=0.7
        )

        print("🧪 NeMo Uyumlu Perplexity LLM Test\n")

        test_prompt = "Python'da list comprehension nedir? Kısa açıkla."
        print(f"Prompt: {test_prompt}\n")

        # Sync test
        print("📍 Sync Test:")
        response = llm(test_prompt)
        print(f"Cevap:\n{response}\n")

        # Async test
        print("📍 Async Test:")

        async def async_test():
            response = await llm._acall(test_prompt)
            print(f"Cevap:\n{response}")

        asyncio.run(async_test())
