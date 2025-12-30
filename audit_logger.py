"""
Audit Logger for Security Events
Logs all blocked/suspicious activities for security monitoring
"""

import json
import os
from datetime import datetime
from typing import Optional


class AuditLogger:
    """Logs security events and blocked attempts"""

    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = log_dir
        self.ensure_log_directory()

    def ensure_log_directory(self):
        """Create logs directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"✅ Audit log directory created: {self.log_dir}")

    def get_log_file_path(self) -> str:
        """Get current log file path (one file per day)"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"audit_{date_str}.log")

    def log_blocked_attempt(
        self,
        session_id: str,
        user_message: str,
        block_reason: str,
        blocked_by: str,
        additional_info: Optional[dict] = None,
    ):
        """
        Log a blocked security event

        Args:
            session_id: Session identifier
            user_message: The user's message that was blocked
            block_reason: Why it was blocked
            blocked_by: Which security control blocked it (input/output)
            additional_info: Additional context (e.g., detected keywords)
        """
        try:
            timestamp = datetime.now().isoformat()

            log_entry = {
                "timestamp": timestamp,
                "event_type": "SECURITY_BLOCK",
                "session_id": session_id,
                "user_message": user_message,
                "block_reason": block_reason,
                "blocked_by": blocked_by,
                "additional_info": additional_info or {},
            }

            # Write to daily log file
            log_file = self.get_log_file_path()
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            # Console output
            print(f"\n{'='*60}")
            print(f"🚨 SECURITY EVENT LOGGED")
            print(f"{'='*60}")
            print(f"Time: {timestamp}")
            print(f"Session: {session_id}")
            print(f"Blocked by: {blocked_by}")
            print(f"Reason: {block_reason}")
            print(f"Message: {user_message[:100]}...")
            print(f"Log file: {log_file}")
            print(f"{'='*60}\n")

        except Exception as e:
            print(f"❌ Failed to write audit log: {e}")

    def log_suspicious_pattern(
        self,
        session_id: str,
        user_message: str,
        pattern_type: str,
        detected_keywords: list,
    ):
        """Log suspicious patterns detected (not necessarily blocked)"""
        try:
            timestamp = datetime.now().isoformat()

            log_entry = {
                "timestamp": timestamp,
                "event_type": "SUSPICIOUS_PATTERN",
                "session_id": session_id,
                "user_message": user_message,
                "pattern_type": pattern_type,
                "detected_keywords": detected_keywords,
            }

            log_file = self.get_log_file_path()
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            print(f"⚠️  Suspicious pattern logged: {pattern_type}")

        except Exception as e:
            print(f"❌ Failed to write suspicious pattern log: {e}")

    def get_recent_logs(self, limit: int = 50) -> list:
        """Retrieve recent audit logs"""
        try:
            log_file = self.get_log_file_path()
            if not os.path.exists(log_file):
                return []

            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Get last N lines
            recent_lines = lines[-limit:]
            return [json.loads(line) for line in recent_lines if line.strip()]

        except Exception as e:
            print(f"❌ Failed to read audit logs: {e}")
            return []


# Global singleton instance
audit_logger = AuditLogger()
