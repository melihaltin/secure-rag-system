"use client";

import { useState, useEffect, useRef } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, AlertCircle, Shield } from "lucide-react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import SessionInfo from "./SessionInfo";
import { chatAPI } from "@/lib/api";
import type { Message } from "@/types/chat";

export default function ChatInterface() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // İlk yüklemede session oluştur
  useEffect(() => {
    createNewSession();
  }, []);

  const createNewSession = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await chatAPI.createSession();
      setSessionId(response.session_id);
      setMessages([]);
      console.log("✅ Yeni session oluşturuldu:", response.session_id);
    } catch (err) {
      setError(
        "Session oluşturulamadı. Lütfen API sunucusunun çalıştığından emin olun."
      );
      console.error("Session oluşturma hatası:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (messageText: string) => {
    if (!sessionId) {
      setError("Session bulunamadı. Lütfen yeni bir session oluşturun.");
      return;
    }

    // Kullanıcı mesajını hemen ekle (optimistic update)
    const userMessage: Message = {
      role: "user",
      content: messageText,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // API'ye gönder
      const response = await chatAPI.sendMessage(sessionId, messageText);

      // Bot cevabını ekle
      const botMessage: Message = {
        role: "assistant",
        content: response.bot_response,
        timestamp: response.timestamp,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError("Mesaj gönderilemedi. Lütfen tekrar deneyin.");
      console.error("Mesaj gönderme hatası:", err);

      // Hata durumunda kullanıcı mesajını geri al
      setMessages((prev) => prev.filter((m) => m !== userMessage));
    }
  };

  const handleDeleteSession = async () => {
    if (!sessionId) return;

    try {
      await chatAPI.deleteSession(sessionId);
      console.log("🗑️ Session silindi:", sessionId);
      createNewSession();
    } catch (err) {
      setError("Session silinemedi.");
      console.error("Session silme hatası:", err);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-purple-50 to-pink-50 dark:from-gray-900 dark:to-gray-800">
        <Card className="w-full max-w-md p-8">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-12 w-12 animate-spin text-purple-500" />
            <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">
              HR Guard Başlatılıyor...
            </p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <Card className="mb-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-purple-200 dark:border-purple-800">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500">
                <Shield className="text-white" size={28} />
              </div>
              <div>
                <CardTitle className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  HR Guard Asistan
                </CardTitle>
                <CardDescription>
                  TechFlow İK Politikaları ve Yan Haklar
                </CardDescription>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Session Info */}
        {sessionId && (
          <div className="mb-4">
            <SessionInfo
              sessionId={sessionId}
              messageCount={messages.length}
              onNewSession={createNewSession}
              onDeleteSession={handleDeleteSession}
            />
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Chat Area */}
        <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
          <CardContent className="p-0">
            {/* Messages */}
            <ScrollArea className="h-[60vh] p-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <div className="p-4 rounded-full bg-purple-100 dark:bg-purple-900 mb-4">
                    <Shield className="text-purple-500" size={48} />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Merhaba! 👋
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 max-w-md">
                    Ben HR Guard asistanıyım. Size izinler, ofis kuralları, yan
                    haklar ve çalışma politikaları hakkında yardımcı olabilirim.
                  </p>
                  <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                    <div className="p-3 bg-blue-50 dark:bg-blue-950 rounded-lg text-left">
                      <p className="font-semibold text-blue-700 dark:text-blue-300 mb-1">
                        ✅ Sorabilirsiniz:
                      </p>
                      <ul className="text-gray-600 dark:text-gray-400 space-y-1">
                        <li>• İzin politikası nedir?</li>
                        <li>• Uzaktan çalışma kuralları</li>
                        <li>• Yemek kartı bilgileri</li>
                      </ul>
                    </div>
                    <div className="p-3 bg-red-50 dark:bg-red-950 rounded-lg text-left">
                      <p className="font-semibold text-red-700 dark:text-red-300 mb-1">
                        🚫 Sorulamaz:
                      </p>
                      <ul className="text-gray-600 dark:text-gray-400 space-y-1">
                        <li>• Maaş bilgileri</li>
                        <li>• Tazminat detayları</li>
                        <li>• Finansal veriler</li>
                      </ul>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((msg, idx) => (
                    <ChatMessage key={idx} message={msg} />
                  ))}
                  <div ref={scrollRef} />
                </>
              )}
            </ScrollArea>

            {/* Input */}
            <div className="border-t border-gray-200 dark:border-gray-700 p-4">
              <ChatInput
                onSendMessage={handleSendMessage}
                disabled={!sessionId}
              />
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <p className="text-center text-xs text-gray-500 dark:text-gray-400 mt-4">
          🔒 Bu sistem NeMo Guardrails ile korunmaktadır. Tüm konuşmalar
          güvenlik kontrolünden geçer.
        </p>
      </div>
    </div>
  );
}
