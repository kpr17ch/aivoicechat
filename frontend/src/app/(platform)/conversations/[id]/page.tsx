import { notFound } from "next/navigation";
import { ConversationDetailView } from "@/components/conversations/conversation-detail";
import { getConversationDetail } from "@/lib/api";

export default async function ConversationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const conversationId = Number(id);

  if (isNaN(conversationId)) {
    notFound();
  }

  try {
    const detail = await getConversationDetail(conversationId);
    return <ConversationDetailView detail={detail} />;
  } catch (error) {
    console.error("Error loading conversation detail:", error);
    notFound();
  }
}

