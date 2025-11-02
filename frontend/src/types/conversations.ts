export interface ConversationSummary {
  id: number;
  stream_sid: string;
  state: string;
  started_at: string | null;
  ended_at: string | null;
  duration_seconds: number | null;
  turn_count: number;
  user_phone: string | null;
  latest_user_text: string | null;
  latest_assistant_text: string | null;
  transcript_available: boolean;
  created_at: string;
  updated_at: string;
}

export interface ConversationEntry {
  timestamp?: string | null;
  role?: string | null;
  text?: string | null;
  status?: string | null;
  sources?: string[] | null;
  normalized_text?: string | null;
  metadata?: Record<string, unknown> | null;
}

export interface ConversationDetail extends ConversationSummary {
  entries: ConversationEntry[];
  metadata?: Record<string, unknown> | null;
  transcript_json_path?: string | null;
  transcript_txt_path?: string | null;
}

export interface ConversationListResponse {
  total: number;
  items: ConversationSummary[];
}
