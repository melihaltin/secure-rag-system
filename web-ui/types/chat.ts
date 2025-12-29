export interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface ChatSession {
  session_id: string;
  created_at: string;
  messages: Message[];
}

export interface ChatResponse {
  session_id: string;
  user_message: string;
  bot_response: string;
  timestamp: string;
}

export interface CreateSessionResponse {
  session_id: string;
  message: string;
}
