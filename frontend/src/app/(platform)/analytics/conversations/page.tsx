import type { Metadata } from 'next';

import { ConversationsDataProvider } from '@/components/conversations';
import { fetchConversationListView } from '@/lib/conversations';

export const metadata: Metadata = {
  title: 'Gespräche',
};

export default async function ConversationsPage() {
  const list = await fetchConversationListView();

  return (
    <ConversationsDataProvider initialData={list}>
      {/* Conversations UI will be implemented here */}
    </ConversationsDataProvider>
  );
}
