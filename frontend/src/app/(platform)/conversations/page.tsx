import type { Metadata } from 'next';

import { ConversationsDataProvider } from '@/components/conversations';
import { fetchConversationListView } from '@/lib/conversations';
import { ConversationsTable } from '@/components/conversations/conversations-table';

export const metadata: Metadata = {
  title: 'Gespräche',
};

export default async function ConversationsPage({
  searchParams,
}: {
  searchParams?: { page?: string; limit?: string };
}) {
  const page = Math.max(1, Number(searchParams?.page ?? 1));
  const limit = Math.min(100, Math.max(1, Number(searchParams?.limit ?? 20)));
  
  const list = await fetchConversationListView({ page, limit });

  return (
    <ConversationsDataProvider initialData={list}>
      <ConversationsTable initial={list} page={page} limit={limit} />
    </ConversationsDataProvider>
  );
}

