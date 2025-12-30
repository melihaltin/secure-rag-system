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
    <Card className="p-3 bg-gray-800 border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CheckCircle2 className="text-green-500" size={20} />
          <div>
            <p className="text-sm font-medium text-gray-300">Active Session</p>
            {sessionId && (
              <p className="text-xs text-gray-500 font-mono">
                {sessionId.slice(0, 8)}...
              </p>
            )}
          </div>
          <Badge variant="secondary" className="ml-2 bg-gray-700 text-gray-300">
            {messageCount}
          </Badge>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={onNewSession}
            size="sm"
            variant="outline"
            className="gap-2 border-gray-700 hover:bg-gray-700"
          >
            <RefreshCw size={14} />
            New
          </Button>
          {sessionId && (
            <Button
              onClick={onDeleteSession}
              size="sm"
              variant="destructive"
              className="gap-2"
            >
              <Trash2 size={14} />
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}
