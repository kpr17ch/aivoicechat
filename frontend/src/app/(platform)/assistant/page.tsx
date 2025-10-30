'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import {
  getAssistantSettings,
  updateAssistantSettings,
  getInstructionTemplates,
  getAvailableVoices
} from '@/lib/api';
import type { AssistantSettings, InstructionTemplate, Voice } from '@/types/assistant';

export default function AssistantPage() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [settings, setSettings] = useState<AssistantSettings | null>(null);
  const [templates, setTemplates] = useState<InstructionTemplate[]>([]);
  const [voices, setVoices] = useState<Voice[]>([]);

  const [selectedVoice, setSelectedVoice] = useState('sage');
  const [selectedTemplate, setSelectedTemplate] = useState('allgemein');
  const [instructions, setInstructions] = useState('');
  const [templateInstructions, setTemplateInstructions] = useState<Record<string, string>>({});
  const [useGreeting, setUseGreeting] = useState(false);
  const [greetingMessage, setGreetingMessage] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [settingsData, templatesData, voicesData] = await Promise.all([
        getAssistantSettings(),
        getInstructionTemplates(),
        getAvailableVoices(),
      ]);

      setSettings(settingsData);
      setTemplates(templatesData);
      setVoices(voicesData);

      setSelectedVoice(settingsData.voice);
      setSelectedTemplate(settingsData.template_name);
      setInstructions(settingsData.system_instructions);

      const initialTemplateState: Record<string, string> = {};
      templatesData.forEach((template) => {
        if (template.name === settingsData.template_name) {
          initialTemplateState[template.name] = settingsData.system_instructions;
        } else {
          initialTemplateState[template.name] = template.default_instructions;
        }
      });
      setTemplateInstructions(initialTemplateState);

      setUseGreeting(!!settingsData.greeting_message);
      setGreetingMessage(settingsData.greeting_message || '');
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Fehler',
        description: 'Einstellungen konnten nicht geladen werden.',
      });
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateChange = (templateName: string) => {
    setTemplateInstructions((prev) => ({
      ...prev,
      [selectedTemplate]: instructions,
    }));

    setSelectedTemplate(templateName);
    const savedInstructions = templateInstructions[templateName];
    if (savedInstructions) {
      setInstructions(savedInstructions);
    } else {
      const template = templates.find((t) => t.name === templateName);
      if (template) {
        setInstructions(template.default_instructions);
      }
    }
  };

  const handleInstructionsChange = (value: string) => {
    setInstructions(value);
    setTemplateInstructions((prev) => ({
      ...prev,
      [selectedTemplate]: value,
    }));
  };

  const handleResetToTemplate = () => {
    const template = templates.find((t) => t.name === selectedTemplate);
    if (template) {
      const defaultInstructions = template.default_instructions;
      setInstructions(defaultInstructions);
      setTemplateInstructions((prev) => ({
        ...prev,
        [selectedTemplate]: defaultInstructions,
      }));
      toast({
        title: 'Zurückgesetzt',
        description: 'Instructions wurden auf das Template zurückgesetzt.',
      });
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await updateAssistantSettings({
        voice: selectedVoice,
        template_name: selectedTemplate,
        system_instructions: instructions,
        greeting_message: useGreeting ? greetingMessage : null,
      });

      toast({
        title: 'Gespeichert',
        description: 'Einstellungen wurden erfolgreich gespeichert.',
      });

      await loadData();
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Fehler',
        description: 'Einstellungen konnten nicht gespeichert werden.',
      });
      console.error('Error saving settings:', error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-muted-foreground">Lade Einstellungen...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Assistant Konfiguration</h1>
        <p className="text-muted-foreground">
          Passe deinen Voice Assistant an deine Bedürfnisse an.
        </p>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Voice Auswahl</CardTitle>
            <CardDescription>
              Wähle die Stimme für deinen AI Assistant
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Label htmlFor="voice">OpenAI Realtime Voice</Label>
              <Select value={selectedVoice} onValueChange={setSelectedVoice}>
                <SelectTrigger id="voice">
                  <SelectValue placeholder="Voice auswählen" />
                </SelectTrigger>
                <SelectContent>
                  {voices.map((voice) => (
                    <SelectItem key={voice.id} value={voice.id}>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{voice.name}</span>
                        <span className="text-sm text-muted-foreground">
                          {voice.description}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Instructions</CardTitle>
            <CardDescription>
              Wähle ein Template oder passe die Instructions individuell an
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="template">Template</Label>
              <div className="flex gap-2">
                <Select value={selectedTemplate} onValueChange={handleTemplateChange}>
                  <SelectTrigger id="template">
                    <SelectValue placeholder="Template auswählen">
                      {selectedTemplate && (
                        <span>
                          {selectedTemplate.charAt(0).toUpperCase() + selectedTemplate.slice(1)}
                        </span>
                      )}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {templates.map((template) => (
                      <SelectItem key={template.name} value={template.name}>
                        <div className="flex flex-col gap-1">
                          <span className="font-medium">
                            {template.name.charAt(0).toUpperCase() + template.name.slice(1)}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {template.description}
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  variant="outline"
                  onClick={handleResetToTemplate}
                  type="button"
                >
                  Zurücksetzen
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="instructions">Instructions</Label>
              <Textarea
                id="instructions"
                value={instructions}
                onChange={(e) => handleInstructionsChange(e.target.value)}
                rows={8}
                className="font-mono text-sm"
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Begrüßungsnachricht</CardTitle>
            <CardDescription>
              Optional: Definiere eine eigene Begrüßungsnachricht für den Assistant
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-2">
              <Switch
                id="use-greeting"
                checked={useGreeting}
                onCheckedChange={setUseGreeting}
              />
              <Label htmlFor="use-greeting">
                Eigene Begrüßungsnachricht verwenden
              </Label>
            </div>

            {useGreeting && (
              <div className="space-y-2">
                <Label htmlFor="greeting">Begrüßungstext</Label>
                <Textarea
                  id="greeting"
                  value={greetingMessage}
                  onChange={(e) => setGreetingMessage(e.target.value)}
                  placeholder="z.B. Hallo, willkommen bei unserem Service. Wie kann ich Ihnen heute helfen?"
                  rows={3}
                />
              </div>
            )}
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4">
          <Button variant="outline" onClick={loadData} disabled={saving}>
            Zurücksetzen
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? 'Speichere...' : 'Einstellungen speichern'}
          </Button>
        </div>
      </div>
    </div>
  );
}

