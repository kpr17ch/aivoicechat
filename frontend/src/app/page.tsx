"use client";

import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { apiBaseUrl } from "@/lib/config";

interface AssistantSettings {
  id: number;
  voice: string;
  system_instructions: string;
  greeting_message: string | null;
  template_name: string;
  phone_number: string | null;
  created_at: string;
  updated_at: string;
}

interface AssistantTemplate {
  id: number;
  name: string;
  description: string;
  default_instructions: string;
  category: string;
}

interface AssistantVoice {
  id: string;
  name: string;
  description: string;
}

interface FormState {
  voice: string;
  template_name: string;
  system_instructions: string;
  use_custom_greeting: boolean;
  greeting_message: string;
}

const INITIAL_ERROR = "Einstellungen konnten nicht geladen werden.";

export default function Home() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [settings, setSettings] = useState<AssistantSettings | null>(null);
  const [templates, setTemplates] = useState<AssistantTemplate[]>([]);
  const [voices, setVoices] = useState<AssistantVoice[]>([]);
  const [form, setForm] = useState<FormState | null>(null);

  const selectedTemplate = useMemo(() => {
    if (!form) return null;
    return templates.find((tpl) => tpl.name === form.template_name) ?? null;
  }, [form, templates]);

  useEffect(() => {
    void loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [settingsRes, templatesRes, voicesRes] = await Promise.all([
        fetch(`${apiBaseUrl}/assistant/settings`, { cache: "no-store" }),
        fetch(`${apiBaseUrl}/assistant/templates`, { cache: "no-store" }),
        fetch(`${apiBaseUrl}/assistant/voices`, { cache: "no-store" }),
      ]);

      if (!settingsRes.ok) {
        throw new Error(`Settings request failed (${settingsRes.status})`);
      }
      if (!templatesRes.ok) {
        throw new Error(`Templates request failed (${templatesRes.status})`);
      }
      if (!voicesRes.ok) {
        throw new Error(`Voices request failed (${voicesRes.status})`);
      }

      const settingsData = (await settingsRes.json()) as AssistantSettings;
      const templateData = (await templatesRes.json()) as AssistantTemplate[];
      const voiceData = (await voicesRes.json()) as AssistantVoice[];

      setSettings(settingsData);
      setTemplates(templateData);
      setVoices(voiceData);
      setForm({
        voice: settingsData.voice,
        template_name: settingsData.template_name,
        system_instructions: settingsData.system_instructions,
        use_custom_greeting: Boolean(settingsData.greeting_message),
        greeting_message: settingsData.greeting_message ?? "",
      });
      setSuccess(null);
    } catch (err) {
      console.error("Failed to load assistant configuration", err);
      setError(INITIAL_ERROR);
    } finally {
      setLoading(false);
    }
  }

  const hasChanges = useMemo(() => {
    if (!settings || !form) return false;
    const greeting = form.use_custom_greeting ? form.greeting_message : "";
    return (
      settings.voice !== form.voice ||
      settings.template_name !== form.template_name ||
      settings.system_instructions !== form.system_instructions ||
      (settings.greeting_message ?? "") !== greeting
    );
  }, [settings, form]);

  const handleReset = () => {
    if (!settings) return;
    setForm({
      voice: settings.voice,
      template_name: settings.template_name,
      system_instructions: settings.system_instructions,
      use_custom_greeting: Boolean(settings.greeting_message),
      greeting_message: settings.greeting_message ?? "",
    });
    setSuccess(null);
    setError(null);
  };

  const handleTemplateReset = () => {
    if (!selectedTemplate || !form) return;
    setForm({
      ...form,
      system_instructions: selectedTemplate.default_instructions,
    });
  };

  async function handleSave() {
    if (!form || !settings) return;
    setSaving(true);
    setError(null);
    setSuccess(null);

    const payload = {
      voice: form.voice,
      template_name: form.template_name,
      system_instructions: form.system_instructions,
      greeting_message: form.use_custom_greeting ? form.greeting_message || null : null,
    };

    try {
      const response = await fetch(`${apiBaseUrl}/assistant/settings`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Save failed (${response.status})`);
      }

      const updated = (await response.json()) as AssistantSettings;
      setSettings(updated);
      setForm({
        voice: updated.voice,
        template_name: updated.template_name,
        system_instructions: updated.system_instructions,
        use_custom_greeting: Boolean(updated.greeting_message),
        greeting_message: updated.greeting_message ?? "",
      });
      setSuccess("Einstellungen gespeichert.");
    } catch (err) {
      console.error("Failed to save assistant configuration", err);
      setError("Einstellungen konnten nicht gespeichert werden.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="px-6 py-8">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-muted-foreground">
          Voice Studio
        </p>
        <h1 className="mt-2 text-2xl font-bold">AI Assistant Console</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          Passe deinen Voice Assistant an, indem du Stimme, System Instructions und Begrüßung
          definierst. Änderungen gelten für alle eingehenden Anrufe.
        </p>
      </header>

      <main className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-6 pb-16">
        <Card>
          <CardHeader>
            <CardTitle>Voice Auswahl</CardTitle>
            <CardDescription>Wähle die Stimme für deinen AI Assistant.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Label htmlFor="voice">OpenAI Realtime Voice</Label>
            <Select
              value={form?.voice ?? ""}
              onValueChange={(value) =>
                setForm((prev) => (prev ? { ...prev, voice: value } : prev))
              }
              disabled={loading || !form}
            >
              <SelectTrigger id="voice">
                <SelectValue placeholder="Stimme auswählen" />
              </SelectTrigger>
              <SelectContent>
                {voices.map((voice) => (
                  <SelectItem key={voice.id} value={voice.id}>
                    <div className="flex flex-col">
                      <span className="font-medium">{voice.name}</span>
                      <span className="text-xs text-muted-foreground">
                        {voice.description}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Instructions</CardTitle>
            <CardDescription>
              Wähle ein Template oder passe die Instructions individuell an.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="template">Template</Label>
              <Select
                value={form?.template_name ?? ""}
                onValueChange={(value) =>
                  setForm((prev) =>
                    prev
                      ? {
                          ...prev,
                          template_name: value,
                          system_instructions:
                            templates.find((tpl) => tpl.name === value)?.default_instructions ??
                            prev.system_instructions,
                        }
                      : prev,
                  )
                }
                disabled={loading || !form}
              >
                <SelectTrigger id="template">
                  <SelectValue placeholder="Template auswählen" />
                </SelectTrigger>
                <SelectContent>
                  {templates.map((template) => (
                    <SelectItem key={template.id} value={template.name}>
                      <div className="flex flex-col">
                        <span className="font-medium">{template.name}</span>
                        <span className="text-xs text-muted-foreground">
                          {template.description}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="instructions">Instructions</Label>
                <Button variant="outline" size="sm" onClick={handleTemplateReset}>
                  Auf Template zurücksetzen
                </Button>
              </div>
              <Textarea
                id="instructions"
                rows={6}
                value={form?.system_instructions ?? ""}
                onChange={(event) =>
                  setForm((prev) =>
                    prev ? { ...prev, system_instructions: event.target.value } : prev,
                  )
                }
                disabled={loading || !form}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Begrüßungsnachricht</CardTitle>
            <CardDescription>
              Optional: Definiere eine eigene Begrüßungsnachricht für den Assistant.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <label className="flex items-center gap-3 text-sm font-medium">
              <input
                type="checkbox"
                className="h-4 w-4"
                checked={Boolean(form?.use_custom_greeting)}
                onChange={(event) =>
                  setForm((prev) =>
                    prev
                      ? {
                          ...prev,
                          use_custom_greeting: event.target.checked,
                          greeting_message: event.target.checked ? prev.greeting_message : "",
                        }
                      : prev,
                  )
                }
                disabled={loading || !form}
              />
              Eigene Begrüßungsnachricht verwenden
            </label>
            <Textarea
              rows={3}
              placeholder="Optionaler Begrüßungstext"
              value={form?.greeting_message ?? ""}
              onChange={(event) =>
                setForm((prev) =>
                  prev ? { ...prev, greeting_message: event.target.value } : prev,
                )
              }
              disabled={loading || !form || !form.use_custom_greeting}
            />
          </CardContent>
        </Card>

        <div className="flex flex-wrap items-center justify-end gap-3">
          <Button variant="outline" onClick={handleReset} disabled={!hasChanges || saving}>
            Zurücksetzen
          </Button>
          <Button onClick={handleSave} disabled={!hasChanges || saving || !form}>
            {saving ? "Speichern..." : "Einstellungen speichern"}
          </Button>
        </div>

        {success && (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
            {success}
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800">
            {error}
          </div>
        )}

        {loading && (
          <div className="rounded-lg border border-dashed px-4 py-6 text-center text-sm text-muted-foreground">
            Einstellungen werden geladen...
          </div>
        )}
      </main>
    </div>
  );
}
