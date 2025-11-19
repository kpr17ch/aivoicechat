"use client";

import { MessageSquare } from "lucide-react";
import { IconFileCode, IconFileText } from "@tabler/icons-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Conversation,
  ConversationContent,
  ConversationEmptyState,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import { Message, MessageContent, MessageResponse } from "@/components/ai-elements/message";
import type { ConversationDetail } from "@/types/conversations";
import { buildConversationEntries, buildConversationDownloadUrl } from "@/lib/conversations";

function formatDuration(seconds: number | null): string {
  if (!seconds) return "-";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  }
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function formatDateTime(dateString: string | null): string {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("de-DE", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

interface ConversationDetailViewProps {
  detail: ConversationDetail;
}

export function ConversationDetailView({ detail }: ConversationDetailViewProps) {
  const entries = buildConversationEntries(detail);
  const hasTranscript = detail.transcript_available || detail.transcript_json_path || detail.transcript_txt_path || entries.length > 0;

  return (
    <div className="flex w-full flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Gespräch #{detail.id}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div className="flex flex-col gap-1">
              <span className="text-muted-foreground text-xs font-medium">Start</span>
              <span className="text-sm">{formatDateTime(detail.started_at)}</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-muted-foreground text-xs font-medium">Ende</span>
              <span className="text-sm">{formatDateTime(detail.ended_at)}</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-muted-foreground text-xs font-medium">Dauer</span>
              <span className="text-sm font-mono">{formatDuration(detail.duration_seconds)}</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-muted-foreground text-xs font-medium">Züge</span>
              <span className="text-sm">{detail.turn_count}</span>
            </div>
            {detail.user_phone && (
              <div className="flex flex-col gap-1">
                <span className="text-muted-foreground text-xs font-medium">Telefon</span>
                <span className="text-sm font-mono">{detail.user_phone}</span>
              </div>
            )}
            {hasTranscript && (
              <div className="flex flex-col gap-2">
                <span className="text-muted-foreground text-xs font-medium">Downloads</span>
                <div className="flex gap-2">
                  {detail.transcript_json_path && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const url = buildConversationDownloadUrl(detail.id, "json");
                        window.open(url, "_blank");
                      }}
                    >
                      <IconFileCode className="mr-2 size-4" />
                      JSON
                    </Button>
                  )}
                  {detail.transcript_txt_path && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const url = buildConversationDownloadUrl(detail.id, "txt");
                        window.open(url, "_blank");
                      }}
                    >
                      <IconFileText className="mr-2 size-4" />
                      TXT
                    </Button>
                  )}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle>Gesprächsverlauf</CardTitle>
        </CardHeader>
        <CardContent>
          {!hasTranscript || entries.length === 0 ? (
            <div className="h-[600px]">
              <ConversationEmptyState
                icon={<MessageSquare className="size-12" />}
                title="Kein Gesprächsverlauf verfügbar"
                description={
                  !hasTranscript
                    ? "Für dieses Gespräch ist kein Transcript verfügbar."
                    : "Dieses Gespräch enthält keine Nachrichten."
                }
              />
            </div>
          ) : (
            <div className="relative w-full rounded-lg border h-[600px] overflow-hidden">
              <Conversation className="h-full">
                <ConversationContent>
                  {entries.map((entry) => (
                    <Message key={entry.id} from={entry.role}>
                      <MessageContent>
                        <MessageResponse from={entry.role}>{entry.text}</MessageResponse>
                        {entry.formattedTime && (
                          <span className="text-muted-foreground text-xs mt-1 px-1">
                            {entry.formattedTime}
                          </span>
                        )}
                      </MessageContent>
                    </Message>
                  ))}
                </ConversationContent>
                <ConversationScrollButton />
              </Conversation>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

