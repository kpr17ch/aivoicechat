import { getConversationSummaries } from '@/lib/api';
import type {
  ConversationDetail,
  ConversationEntry,
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

export interface ConversationEntryView {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'other';
  text: string;
  timestamp: string | null;
  formattedTime: string | null;
  status: string | null;
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

function normalizeRole(role: string | null | undefined): 'user' | 'assistant' | 'system' | 'other' {
  if (!role) return 'other';
  const normalized = role.toLowerCase().trim();
  if (normalized === 'user') return 'user';
  if (normalized === 'assistant') return 'assistant';
  if (normalized === 'system') return 'system';
  return 'other';
}

function formatTimestamp(timestamp: string | null | undefined): string | null {
  if (!timestamp) return null;
  try {
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return null;
    return new Intl.DateTimeFormat('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(date);
  } catch {
    return null;
  }
}

function isPromptInstruction(text: string): boolean {
  const lowerText = text.toLowerCase().trim();
  return (
    lowerText.startsWith('greet the user') ||
    lowerText.startsWith('greet the user with') ||
    lowerText.includes('greet the user with') ||
    lowerText.startsWith('relevante begriffe') ||
    lowerText.startsWith('erkenne begriffe')
  );
}

export function buildConversationEntries(
  detail: ConversationDetail
): ConversationEntryView[] {
  const entries = detail.entries
    .filter((entry) => {
      const hasText = entry.text && entry.text.trim().length > 0;
      const isNotPending = entry.status !== 'pending';
      const isNotPrompt = !isPromptInstruction(entry.text || '');
      return hasText && isNotPending && isNotPrompt;
    })
    .map((entry, index) => ({
      id: entry.timestamp || `entry-${index}`,
      role: normalizeRole(entry.role),
      text: entry.text || '',
      timestamp: entry.timestamp || null,
      formattedTime: formatTimestamp(entry.timestamp),
      status: entry.status || null,
    }))
    .sort((a, b) => {
      if (!a.timestamp && !b.timestamp) return 0;
      if (!a.timestamp) return 1;
      if (!b.timestamp) return -1;
      return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
    });

  return entries;
}

export async function fetchConversationListView(
  options?: { page?: number; limit?: number }
): Promise<ConversationsListView> {
  const page = Math.max(1, options?.page ?? 1);
  const limit = Math.min(100, Math.max(1, options?.limit ?? 20));
  const offset = (page - 1) * limit;
  
  const response = await getConversationSummaries({ limit, offset, only_completed: true });
  return transformConversationList(response);
}
