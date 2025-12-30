"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");
  
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

  // Create session on initial load if no session in URL
  useEffect(() => {
    if (!sessionId) {
      createNewSession();
    } else {
      setIsLoading(false);
    }
  }, []);

  const createNewSession = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await chatAPI.createSession();
      // Update URL with new session ID
      router.push(`?session=${response.session_id}`);
      setMessages([]);
      console.log("✅ New session created:", response.session_id);
    } catch (err) {
      setError(
        "Failed to create session. Please ensure the API server is running."
      );
      console.error("Session creation error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (messageText: string) => {
    if (!sessionId) {
      setError("Session not found. Please create a new session.");
      return;
    }

    // Add user message immediately (optimistic update)
    const userMessage: Message = {
      role: "user",
      content: messageText,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // Send to API
      const response = await chatAPI.sendMessage(sessionId, messageText);

      // Add bot response
      const botMessage: Message = {
        role: "assistant",
        content: response.bot_response,
        timestamp: response.timestamp,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError("Failed to send message. Please try again.");
      console.error("Message sending error:", err);

      // Remove user message on error
      setMessages((prev) => prev.filter((m) => m !== userMessage));
    }
  };

  const handleDeleteSession = async () => {
    if (!sessionId) return;

    try {
      await chatAPI.deleteSession(sessionId);
      console.log("🗑️ Session deleted:", sessionId);
      createNewSession();
    } catch (err) {
      setError("Failed to delete session.");
      console.error("Session deletion error:", err);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <Card className="w-full max-w-md p-8 bg-gray-800 border-gray-700">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-12 w-12 animate-spin text-gray-400" />
            <p className="text-lg font-medium text-gray-300">
              Initializing HR Guard...
            </p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <Card className="mb-4 bg-gray-800 border-gray-700">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gray-700">
                <Shield className="text-gray-300" size={24} />
              </div>
              <div>
                <CardTitle className="text-xl font-semibold text-gray-100">
                  HR Guard
                </CardTitle>
                <CardDescription className="text-gray-400">
                  TechFlow HR Policies & Benefits
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
          <Alert variant="destructive" className="mb-4 bg-red-950 border-red-800">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Chat Area */}
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-0">
            {/* Messages */}
            <ScrollArea className="h-[65vh] p-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <div className="p-4 rounded-full bg-gray-700 mb-4">
                    <Shield className="text-gray-400" size={40} />
                  </div>
                  <h3 className="text-lg font-medium text-gray-200 mb-2">
                    Welcome to HR Guard
                  </h3>
                  <p className="text-sm text-gray-400 max-w-md mb-6">
                    Ask me about policies, benefits, work guidelines, and more.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs max-w-lg">
                    <div className="p-3 bg-gray-700 rounded-lg text-left border border-gray-600">
                      <p className="font-medium text-gray-300 mb-2">
                        ✓ You can ask:
                      </p>
                      <ul className="text-gray-400 space-y-1">
                        <li>• Leave policy</li>
                        <li>• Remote work rules</li>
                        <li>• Meal card benefits</li>
                      </ul>
                    </div>
                    <div className="p-3 bg-gray-700 rounded-lg text-left border border-gray-600">
                      <p className="font-medium text-gray-300 mb-2">
                        ✗ Restricted topics:
                      </p>
                      <ul className="text-gray-400 space-y-1">
                        <li>• Salary information</li>
                        <li>• Compensation details</li>
                        <li>• Financial data</li>
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
            <div className="border-t border-gray-700 p-4">
              <ChatInput
                onSendMessage={handleSendMessage}
                disabled={!sessionId}
              />
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <p className="text-center text-xs text-gray-500 mt-4">
          🔒 Protected by NeMo Guardrails - All conversations are monitored for security
        </p>
      </div>
    </div>
  );
}
