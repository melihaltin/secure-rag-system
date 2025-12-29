import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

SESSIONS_DIR = Path("./sessions")
SESSIONS_DIR.mkdir(exist_ok=True)


class SessionManager:
    """Chat session'larını yönetir"""

    @staticmethod
    def create_session() -> str:
        """Yeni bir session oluşturur ve ID döner"""
        session_id = str(uuid.uuid4())
        session_file = SESSIONS_DIR / f"session_{session_id}.json"

        initial_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
        }

        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Yeni session oluşturuldu: {session_id}")
        return session_id

    @staticmethod
    def get_session_file(session_id: str) -> Path:
        """Session ID'ye göre dosya yolunu döner"""
        return SESSIONS_DIR / f"session_{session_id}.json"

    @staticmethod
    def session_exists(session_id: str) -> bool:
        """Session'ın var olup olmadığını kontrol eder"""
        return SessionManager.get_session_file(session_id).exists()

    @staticmethod
    def load_session(session_id: str) -> Optional[Dict]:
        """Session verisini yükler"""
        session_file = SessionManager.get_session_file(session_id)

        if not session_file.exists():
            print(f"⚠️  Session bulunamadı: {session_id}")
            return None

        try:
            with open(session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Session yükleme hatası: {e}")
            return None

    @staticmethod
    def save_message(session_id: str, role: str, content: str) -> bool:
        """Session'a yeni mesaj ekler"""
        session_data = SessionManager.load_session(session_id)

        if not session_data:
            return False

        message = {
            "role": role,  # "user" veya "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        session_data["messages"].append(message)

        try:
            session_file = SessionManager.get_session_file(session_id)
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ Mesaj kaydetme hatası: {e}")
            return False

    @staticmethod
    def get_chat_history(session_id: str) -> List[Dict]:
        """Session'ın chat geçmişini döner"""
        session_data = SessionManager.load_session(session_id)
        if session_data:
            return session_data.get("messages", [])
        return []

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Session'ı siler"""
        session_file = SessionManager.get_session_file(session_id)

        if session_file.exists():
            try:
                session_file.unlink()
                print(f"🗑️  Session silindi: {session_id}")
                return True
            except Exception as e:
                print(f"❌ Session silme hatası: {e}")
                return False
        return False

    @staticmethod
    def list_all_sessions() -> List[str]:
        """Tüm session ID'leri döner"""
        sessions = []
        for file in SESSIONS_DIR.glob("session_*.json"):
            session_id = file.stem.replace("session_", "")
            sessions.append(session_id)
        return sessions
