// app/(dashboard)/bot/[id]/documents/page.tsx
'use client';
import { useParams } from 'next/navigation';
import DocumentUploader from '@/components/documents/DocumentUploader';
import DocumentList from '@/components/documents/DocumentList';
export default function DocumentsPage() {
  const params = useParams();
  const botId = params.id as string;
  return (
    <div className="space-y-6">

      <DocumentUploader botId={botId} />
      <DocumentList botId={botId} />
    </div>
  );
}
