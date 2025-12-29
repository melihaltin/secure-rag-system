"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Loader2 } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (message: string) => Promise<void>;
  disabled?: boolean;
}

export default function ChatInput({ onSendMessage, disabled }: ChatInputProps) {
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!message.trim() || disabled || isLoading) return;

    setIsLoading(true);
    try {
      await onSendMessage(message.trim());
      setMessage("");
    } catch (error) {
      console.error("Mesaj gönderme hatası:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Mesajınızı yazın... (örn: İzin politikası nedir?)"
        disabled={disabled || isLoading}
        className="flex-1"
        autoComplete="off"
      />
      <Button
        type="submit"
        disabled={!message.trim() || disabled || isLoading}
        size="icon"
        className="bg-blue-500 hover:bg-blue-600"
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Send className="h-4 w-4" />
        )}
      </Button>
    </form>
  );
}
