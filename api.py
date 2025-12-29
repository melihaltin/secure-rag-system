import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from nemoguardrails import LLMRails, RailsConfig
from dotenv import load_dotenv

# RAG motorunu içe aktar
from rag_chain import ask_rag

load_dotenv()


rails_app = None
SESSIONS_DIR = "sessions"  

def ensure_sessions_dir():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)


def get_session_file(session_id: str):
    safe_id = "".join([c for c in session_id if c.isalnum() or c in "-_"])
    return os.path.join(SESSIONS_DIR, f"{safe_id}.json")


def load_history(session_id: str):
    file_path = get_session_file(session_id)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")
            return []
    return []


def save_history(session_id: str, history: list):
    file_path = get_session_file(session_id)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Dosya yazma hatası: {e}")


# --- RAG Action ---
async def call_rag(query: str):
    print(f"⚡ RAG Çağrılıyor: {query}")
    return ask_rag(query)


# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global rails_app
    ensure_sessions_dir() 

    print("🚀 Sistem Başlatılıyor: Guardrails ve RAG yükleniyor...")
    config_path = "./config"
    config = RailsConfig.from_path(config_path)
    rails_app = LLMRails(config)
    rails_app.register_action(action=call_rag, name="call_rag")

    print("✅ Sistem Hazır! Hafıza modülü aktif.")
    yield
    print("🛑 Sistem Kapatılıyor...")


# --- FastAPI App ---
app = FastAPI(title="HR Guard API", version="1.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Modeller ---
class ChatRequest(BaseModel):
    message: str
    session_id: str  # Artık zorunlu, çünkü dosyayı buna göre açacağız


class ChatResponse(BaseModel):
    response: str
    session_id: str


# --- Endpointler ---


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    global rails_app

    if not rails_app:
        raise HTTPException(status_code=503, detail="Sistem hazır değil.")

    try:

        history = load_history(request.session_id)

        messages_to_send = history.copy() 
        messages_to_send.append(
            {"role": "user", "content": request.message}
        )  # Yeni mesaj


        response = await rails_app.generate_async(messages=messages_to_send)

        bot_reply = response.content

        if not bot_reply:
            bot_reply = "Üzgünüm, bir hata oluştu."

        history.append({"role": "user", "content": request.message})

        history.append({"role": "assistant", "content": bot_reply})

        save_history(request.session_id, history)

        return ChatResponse(response=bot_reply, session_id=request.session_id)

    except Exception as e:
        print(f"HATA: {e}")
        raise HTTPException(status_code=500, detail=str(e))
