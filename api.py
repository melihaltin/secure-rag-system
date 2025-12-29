import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.actions import action

from config import MODEL_NAME, TEMP
from custom_llm import NeMoCompatibleGemini
from rag_chain import ask_rag
from session_manager import SessionManager
import re

load_dotenv()

# ============================================
# MODELS (Request/Response)
# ============================================


class CreateSessionResponse(BaseModel):
    session_id: str
    message: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    user_message: str
    bot_response: str
    timestamp: str


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]


class SessionListResponse(BaseModel):
    sessions: List[str]
    count: int


# ============================================
# ACTIONS (NeMo Guardrails)
# ============================================


@action(name="call_rag", is_system_action=True)
async def call_rag_action(context: dict = None) -> str:
    """RAG chain wrapper for NeMo Guardrails"""
    try:
        query = context.get("last_user_message", "")

        if not query:
            return "Sorunuzu anlayamadım."

        print(f"   📝 RAG Query: {query}")
        response = ask_rag(query)
        result = str(response).strip()

        if not result:
            result = "Bu soruya cevap bulamadım."

        print(f"   ✅ RAG Response: {result[:100]}...")
        return result

    except Exception as e:
        print(f"   ❌ RAG Action Error: {e}")
        return "Cevap oluştururken hata oluştu."


@action(name="check_input_for_salary", is_system_action=True)
async def check_input_for_salary_action(context: dict = None) -> bool:
    """Kullanıcı girişinde maaş araması var mı kontrol et"""
    try:
        text = context.get("last_user_message", "")

        if not text:
            return False

        text_lower = text.lower()

        salary_keywords = [
            "maaş",
            "maas",
            "salary",
            "ücret",
            "ucret",
            "kazanç",
            "kazanc",
            "gelir",
            "bordro",
            "payroll",
            "compensation",
            "zam",
            "prim",
            "bonus",
        ]

        for keyword in salary_keywords:
            if keyword in text_lower:
                print(f"   🚨 Maaş keyword tespit edildi: {keyword}")
                return True

        return False

    except Exception as e:
        print(f"   ❌ Input Check Error: {e}")
        return False


@action(name="check_salary_regex", is_system_action=True)
async def check_salary_regex_action(context: dict = None, text: str = None) -> bool:
    """Çıktıda maaş rakamı var mı kontrol et"""
    try:
        if text is None:
            text = context.get("bot_message", "")

        if not text:
            return False

        pattern = r"\d{2,}[\.,]?\d{3}\s*(TL|₺|lira|USD|\$)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            print(f"   🚨 Maaş verisi tespit edildi: {match.group()}")
            return True

        return False

    except Exception as e:
        print(f"   ❌ Regex Check Error: {e}")
        return False


# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="HR Guard API",
    description="TechFlow İK Asistanı - Session Yönetimli RAG Sistemi",
    version="1.0.0",
)

# CORS ayarları (Frontend için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da bunu değiştir!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NeMo Guardrails Instance (Global)
rails_app = None


@app.on_event("startup")
async def startup_event():
    """Sunucu başlatıldığında NeMo Guardrails'i yükle"""
    global rails_app

    print("\n" + "=" * 60)
    print("🚀 HR GUARD API BAŞLATILIYOR...")
    print("=" * 60 + "\n")

    try:
        # Config yükle
        config_path = "./config"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config klasörü bulunamadı: {config_path}")

        print(f"📂 Config yükleniyor: {config_path}")
        config = RailsConfig.from_path(config_path)

        # Custom LLM oluştur
        custom_llm = NeMoCompatibleGemini(
            model=MODEL_NAME, temperature=TEMP, max_output_tokens=256
        )

        # Rails başlat
        print("🔧 Rails başlatılıyor...")
        rails_app = LLMRails(config, llm=custom_llm)

        # Action'ları kaydet
        rails_app.register_action(call_rag_action, name="call_rag")
        rails_app.register_action(
            check_input_for_salary_action, name="check_input_for_salary"
        )
        rails_app.register_action(check_salary_regex_action, name="check_salary_regex")

        print("✅ Action'lar kaydedildi")
        print("\n" + "=" * 60)
        print("✅ HR GUARD API HAZIR!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ BAŞLATMA HATASI: {e}")
        import traceback

        traceback.print_exc()
        raise


# ============================================
# ENDPOINTS
# ============================================


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "HR Guard API",
        "version": "1.0.0",
        "endpoints": {
            "create_session": "POST /session/create",
            "chat": "POST /chat",
            "history": "GET /session/{session_id}/history",
            "delete_session": "DELETE /session/{session_id}",
            "list_sessions": "GET /sessions",
        },
    }


@app.post("/session/create", response_model=CreateSessionResponse)
async def create_session():
    """Yeni bir chat session oluşturur"""
    try:
        session_id = SessionManager.create_session()
        return CreateSessionResponse(
            session_id=session_id, message="Session başarıyla oluşturuldu"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session oluşturulamadı: {str(e)}",
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Kullanıcı mesajı gönderir ve bot cevabı alır"""
    global rails_app

    if not rails_app:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rails sistemi henüz hazır değil",
        )

    # Session kontrolü
    if not SessionManager.session_exists(request.session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session bulunamadı: {request.session_id}",
        )

    try:
        print(f"\n{'='*60}")
        print(f"📨 Yeni Mesaj - Session: {request.session_id}")
        print(f"👤 User: {request.message}")
        print(f"{'='*60}\n")

        # Kullanıcı mesajını kaydet
        SessionManager.save_message(request.session_id, "user", request.message)

        # NeMo Guardrails'e gönder
        response = rails_app.generate(
            messages=[{"role": "user", "content": request.message}]
        )

        # Response'u parse et
        if isinstance(response, dict):
            bot_response = response.get("content", "")
        elif isinstance(response, str):
            bot_response = response
        elif hasattr(response, "content"):
            bot_response = response.content
        else:
            bot_response = str(response)

        bot_response = bot_response.strip()

        if not bot_response:
            bot_response = "Üzgünüm, bir cevap oluşturamadım."

        print(f"🤖 Bot: {bot_response}\n")

        # Bot cevabını kaydet
        SessionManager.save_message(request.session_id, "assistant", bot_response)

        from datetime import datetime

        return ChatResponse(
            session_id=request.session_id,
            user_message=request.message,
            bot_response=bot_response,
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        print(f"❌ Chat Error: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mesaj işlenirken hata: {str(e)}",
        )


@app.get("/session/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """Session'ın tüm chat geçmişini döner"""
    if not SessionManager.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session bulunamadı: {session_id}",
        )

    messages = SessionManager.get_chat_history(session_id)
    return ChatHistoryResponse(session_id=session_id, messages=messages)


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Session'ı siler"""
    if not SessionManager.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session bulunamadı: {session_id}",
        )

    success = SessionManager.delete_session(session_id)

    if success:
        return {"message": f"Session silindi: {session_id}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session silinemedi",
        )


@app.get("/sessions", response_model=SessionListResponse)
async def list_sessions():
    """Tüm aktif session'ları listeler"""
    sessions = SessionManager.list_all_sessions()
    return SessionListResponse(sessions=sessions, count=len(sessions))


# ============================================
# RUN (Development)
# ============================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Development için
        log_level="info",
    )
