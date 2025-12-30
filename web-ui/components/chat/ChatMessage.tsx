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
            ? "bg-gray-700"
            : "bg-gray-600"
        } flex-shrink-0`}
      >
        <AvatarFallback className="text-white">
          {isUser ? <User size={18} /> : <Bot size={18} />}
        </AvatarFallback>
      </Avatar>

      {/* Message Card */}
      <div
        className={`flex flex-col ${
          isUser ? "items-end" : "items-start"
        } max-w-[75%]`}
      >
        {/* Name and Time */}
        <div
          className={`flex items-center gap-2 mb-1 ${
            isUser ? "flex-row-reverse" : "flex-row"
          }`}
        >
          <span className="text-sm font-medium text-gray-300">
            {isUser ? "You" : "HR Guard"}
          </span>
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Clock size={12} />
            <span>
              {new Date(message.timestamp).toLocaleTimeString("en-US", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          </div>
        </div>

        {/* Message Content */}
        <Card
          className={`
          p-3 
          ${
            isUser
              ? "bg-gray-700 text-white border-gray-600"
              : isSecurityBlock
              ? "bg-red-950 border-red-800"
              : "bg-gray-800 border-gray-700"
          }
          shadow-sm
        `}
        >
          {/* Security Warning Badge */}
          {!isUser && isSecurityBlock && (
            <Badge variant="destructive" className="mb-2 gap-1 text-xs">
              <ShieldAlert size={12} />
              Security Block
            </Badge>
          )}

          {/* Message Text - with Markdown */}
          <div
            className={`
            prose prose-sm max-w-none
            ${
              isUser
                ? "prose-invert"
                : isSecurityBlock
                ? "prose-red prose-invert"
                : "prose-invert"
            }
          `}
          >
            <ReactMarkdown
              components={{
                // Paragraph styles
                p: ({ children }) => (
                  <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
                ),
                // Bold text
                strong: ({ children }) => (
                  <strong className="font-bold">{children}</strong>
                ),
                // Italic text
                em: ({ children }) => <em className="italic">{children}</em>,
                // Code blocks
                code: ({ node, children, ...props }: any) => {
                  const isInline = !node?.data?.meta;
                  return isInline ? (
                    <code className="px-1.5 py-0.5 rounded bg-gray-700 text-sm font-mono">
                      {children}
                    </code>
                  ) : (
                    <code className="block p-2 rounded bg-gray-900 text-sm font-mono overflow-x-auto">
                      {children}
                    </code>
                  );
                },
                // List styles
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
                // Link styles
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
