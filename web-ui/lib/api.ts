import axios from "axios";
import type {
  ChatResponse,
  CreateSessionResponse,
  Message,
} from "@/types/chat";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const chatAPI = {
  // Yeni session oluştur
  createSession: async (): Promise<CreateSessionResponse> => {
    const response = await api.post("/session/create");
    return response.data;
  },

  // Mesaj gönder
  sendMessage: async (
    sessionId: string,
    message: string
  ): Promise<ChatResponse> => {
    const response = await api.post("/chat", {
      session_id: sessionId,
      message,
    });
    return response.data;
  },

  // Chat geçmişini getir
  getChatHistory: async (sessionId: string): Promise<Message[]> => {
    const response = await api.get(`/session/${sessionId}/history`);
    return response.data.messages;
  },

  // Session sil
  deleteSession: async (sessionId: string): Promise<void> => {
    await api.delete(`/session/${sessionId}`);
  },

  // Tüm session'ları listele
  listSessions: async (): Promise<string[]> => {
    const response = await api.get("/sessions");
    return response.data.sessions;
  },
};
