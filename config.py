# config.py
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Değişkenleri al
MODEL_NAME = os.getenv("LLM_MODEL")
TEMP = float(os.getenv("LLM_TEMP", 0))

PROMPT = """ Sen bir HR asistanısın. Aşağıdaki bağlama göre soruyu cevapla. 
Kullanıcı genel bir soru sorsa bile (örn: "kadın olarak", "erkek olarak"), 
bağlamdaki ilgili kurallara göre cevap ver. 
Eğer bağlamda cinsiyet belirtilmemişse, genel kuralları paylaş.

Bağlam: 
{context}

Soru:  {question}

Cevap: """
