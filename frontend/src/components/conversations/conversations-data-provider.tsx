'use client';

import { createContext, useContext } from 'react';
import type { ConversationsListView } from '@/lib/conversations';

type ConversationsDataContextValue = ConversationsListView | null;

const ConversationsDataContext =
  createContext<ConversationsDataContextValue>(null);

interface ConversationsDataProviderProps {
  initialData: ConversationsListView;
  children?: React.ReactNode;
}

export function ConversationsDataProvider({
  initialData,
  children,
}: ConversationsDataProviderProps) {
  return (
    <ConversationsDataContext.Provider value={initialData}>
      {children ?? null}
    </ConversationsDataContext.Provider>
  );
}

export function useConversationsData(): ConversationsListView {
  const context = useContext(ConversationsDataContext);
  if (!context) {
    throw new Error(
      'useConversationsData must be used within a ConversationsDataProvider'
    );
  }
  return context;
}
