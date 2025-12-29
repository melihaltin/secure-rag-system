"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bot, User, Clock, ShieldAlert } from "lucide-react";
import type { Message } from "@/types/chat";

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const isSecurityBlock =
    message.content.includes("GÜVENLİK") ||
    message.content.includes("SECURITY") ||
    message.content.includes("🛡️") ||
    message.content.includes("⚠️");

  return (
    <div
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"} mb-4`}
    >
      {/* Avatar */}
      <Avatar
        className={`${
          isUser
            ? "bg-blue-500"
            : "bg-gradient-to-br from-purple-500 to-pink-500"
        } flex-shrink-0`}
      >
        <AvatarFallback className="text-white">
          {isUser ? <User size={20} /> : <Bot size={20} />}
        </AvatarFallback>
      </Avatar>

      {/* Mesaj Kartı */}
      <div
        className={`flex flex-col ${
          isUser ? "items-end" : "items-start"
        } max-w-[75%]`}
      >
        {/* İsim ve Zaman */}
        <div
          className={`flex items-center gap-2 mb-1 ${
            isUser ? "flex-row-reverse" : "flex-row"
          }`}
        >
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            {isUser ? "Siz" : "HR Guard"}
          </span>
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Clock size={12} />
            <span>
              {new Date(message.timestamp).toLocaleTimeString("tr-TR", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          </div>
        </div>

        {/* Mesaj İçeriği */}
        <Card
          className={`
          p-4 
          ${
            isUser
              ? "bg-blue-500 text-white border-blue-600"
              : isSecurityBlock
              ? "bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800"
              : "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700"
          }
          shadow-sm
        `}
        >
          {/* Güvenlik Uyarısı Badge */}
          {!isUser && isSecurityBlock && (
            <Badge variant="destructive" className="mb-2 gap-1">
              <ShieldAlert size={14} />
              Güvenlik Engeli
            </Badge>
          )}

          {/* Mesaj Metni */}
          <p
            className={`
            text-sm leading-relaxed whitespace-pre-wrap
            ${
              isUser
                ? "text-white"
                : isSecurityBlock
                ? "text-red-900 dark:text-red-100"
                : "text-gray-800 dark:text-gray-200"
            }
          `}
          >
            {message.content}
          </p>
        </Card>
      </div>
    </div>
  );
}
