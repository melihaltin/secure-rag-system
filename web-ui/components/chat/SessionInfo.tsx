"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RefreshCw, Trash2, CheckCircle2 } from "lucide-react";

interface SessionInfoProps {
  sessionId: string | null;
  messageCount: number;
  onNewSession: () => void;
  onDeleteSession: () => void;
}

export default function SessionInfo({
  sessionId,
  messageCount,
  onNewSession,
  onDeleteSession,
}: SessionInfoProps) {
  return (
    <Card className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950 border-purple-200 dark:border-purple-800">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CheckCircle2 className="text-green-500" size={24} />
          <div>
            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              Aktif Session
            </p>
            {sessionId && (
              <p className="text-xs text-gray-500 font-mono">
                ID: {sessionId.slice(0, 8)}...
              </p>
            )}
          </div>
          <Badge variant="secondary" className="ml-2">
            {messageCount} mesaj
          </Badge>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={onNewSession}
            size="sm"
            variant="outline"
            className="gap-2"
          >
            <RefreshCw size={16} />
            Yeni Session
          </Button>
          {sessionId && (
            <Button
              onClick={onDeleteSession}
              size="sm"
              variant="destructive"
              className="gap-2"
            >
              <Trash2 size={16} />
              Sil
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}
