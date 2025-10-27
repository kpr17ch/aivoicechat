import { AssistantSettings, AssistantSettingsUpdate, InstructionTemplate, Voice } from '@/types/assistant';

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

