export interface AssistantSettings {
  id: number;
  voice: string;
  system_instructions: string;
  greeting_message: string | null;
  template_name: string;
  phone_number: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssistantSettingsUpdate {
  voice?: string;
  system_instructions?: string;
  greeting_message?: string | null;
  template_name?: string;
  phone_number?: string | null;
}

export interface InstructionTemplate {
  id: number;
  name: string;
  description: string;
  default_instructions: string;
  category: string;
}

export interface Voice {
  id: string;
  name: string;
  description: string;
}

