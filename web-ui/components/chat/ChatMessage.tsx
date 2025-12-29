"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bot, User, Clock, ShieldAlert } from "lucide-react";
import ReactMarkdown from "react-markdown";
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

          {/* Mesaj Metni - Markdown ile */}
          <div
            className={`
            prose prose-sm max-w-none
            ${
              isUser
                ? "prose-invert"
                : isSecurityBlock
                ? "prose-red dark:prose-invert"
                : "dark:prose-invert"
            }
          `}
          >
            <ReactMarkdown
              components={{
                // Paragraph stilleri
                p: ({ children }) => (
                  <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
                ),
                // Kalın metin
                strong: ({ children }) => (
                  <strong className="font-bold">{children}</strong>
                ),
                // İtalik metin
                em: ({ children }) => <em className="italic">{children}</em>,
                // Kod blokları
                code: ({ node, children, ...props }: any) => {
                  const isInline = !node?.data?.meta;
                  return isInline ? (
                    <code className="px-1.5 py-0.5 rounded bg-gray-200 dark:bg-gray-700 text-sm font-mono">
                      {children}
                    </code>
                  ) : (
                    <code className="block p-2 rounded bg-gray-100 dark:bg-gray-900 text-sm font-mono overflow-x-auto">
                      {children}
                    </code>
                  );
                },
                // Liste stilleri
                ul: ({ children }) => (
                  <ul className="list-disc list-inside space-y-1">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-inside space-y-1">
                    {children}
                  </ol>
                ),
                li: ({ children }) => <li className="ml-2">{children}</li>,
                // Link stilleri
                a: ({ children, href }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:no-underline"
                  >
                    {children}
                  </a>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        </Card>
      </div>
    </div>
  );
}
