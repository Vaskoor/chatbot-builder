// app/(dashboard)/bot/[id]/graph/page.tsx
'use client';
import { useParams } from 'next/navigation';
import GraphViewer from '@/components/graph/GraphViewer';
export default function GraphPage() {
  const params = useParams();
  const botId = params.id as string;
  return <GraphViewer botId={botId} />;
}
