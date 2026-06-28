// app/(dashboard)/bot/[id]/chat/page.tsx
'use client';
import { useParams } from 'next/navigation';
import ChatInterface from '@/components/chat/ChatInterface';
export default function ChatPage() {
  const params = useParams();
  const botId = params.id as string;
  return <ChatInterface botId={botId} />;
}
