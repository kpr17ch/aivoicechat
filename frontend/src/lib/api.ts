import { AssistantSettings, AssistantSettingsUpdate, InstructionTemplate, Voice } from '@/types/assistant';
import {
  ConversationDetail,
  ConversationListResponse,
} from '@/types/conversations';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function getAssistantSettings(): Promise<AssistantSettings> {
  return fetchAPI<AssistantSettings>('/assistant/settings');
}

export async function updateAssistantSettings(
  data: AssistantSettingsUpdate
): Promise<AssistantSettings> {
  return fetchAPI<AssistantSettings>('/assistant/settings', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function getInstructionTemplates(): Promise<InstructionTemplate[]> {
  return fetchAPI<InstructionTemplate[]>('/assistant/templates');
}

export async function getAvailableVoices(): Promise<Voice[]> {
  return fetchAPI<Voice[]>('/assistant/voices');
}

export interface ConversationListQuery {
  limit?: number;
  offset?: number;
}

export async function getConversationSummaries(
  params: ConversationListQuery = {}
): Promise<ConversationListResponse> {
  const search = new URLSearchParams();
  if (typeof params.limit === 'number') {
    search.set('limit', String(params.limit));
  }
  if (typeof params.offset === 'number') {
    search.set('offset', String(params.offset));
  }

  const query = search.toString();
  const endpoint = query ? `/conversations?${query}` : '/conversations';
  return fetchAPI<ConversationListResponse>(endpoint, { cache: 'no-store' });
}

export async function getConversationDetail(
  conversationId: number
): Promise<ConversationDetail> {
  return fetchAPI<ConversationDetail>(`/conversations/${conversationId}`, {
    cache: 'no-store',
  });
}
