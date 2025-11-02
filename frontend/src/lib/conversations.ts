import { getConversationSummaries } from '@/lib/api';
import type {
  ConversationDetail,
  ConversationListResponse,
  ConversationSummary,
} from '@/types/conversations';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface ConversationSummaryView {
  id: number;
  streamSid: string;
  state: string;
  startedAt: string | null;
  endedAt: string | null;
  durationSeconds: number | null;
  turnCount: number;
  userPhone: string | null;
  latestUserText: string | null;
  latestAssistantText: string | null;
  transcriptAvailable: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ConversationsListView {
  total: number;
  items: ConversationSummaryView[];
  raw: ConversationListResponse;
  fetchedAt: string;
}

export function buildConversationDownloadUrl(
  conversationId: number,
  format: 'json' | 'txt' = 'json'
): string {
  const url = new URL(
    `/conversations/${conversationId}/download`,
    API_BASE_URL
  );
  url.searchParams.set('format', format);
  return url.toString();
}

export function transformConversationSummary(
  summary: ConversationSummary
): ConversationSummaryView {
  return {
    id: summary.id,
    streamSid: summary.stream_sid,
    state: summary.state,
    startedAt: summary.started_at,
    endedAt: summary.ended_at,
    durationSeconds: summary.duration_seconds,
    turnCount: summary.turn_count,
    userPhone: summary.user_phone,
    latestUserText: summary.latest_user_text,
    latestAssistantText: summary.latest_assistant_text,
    transcriptAvailable: summary.transcript_available,
    createdAt: summary.created_at,
    updatedAt: summary.updated_at,
  };
}

export function transformConversationList(
  response: ConversationListResponse
): ConversationsListView {
  return {
    total: response.total,
    items: response.items.map(transformConversationSummary),
    raw: response,
    fetchedAt: new Date().toISOString(),
  };
}

export type { ConversationDetail };

export async function fetchConversationListView(
  options?: { page?: number; limit?: number }
): Promise<ConversationsListView> {
  const page = Math.max(1, options?.page ?? 1);
  const limit = Math.min(100, Math.max(1, options?.limit ?? 20));
  const offset = (page - 1) * limit;
  
  const response = await getConversationSummaries({ limit, offset, only_completed: true });
  return transformConversationList(response);
}
