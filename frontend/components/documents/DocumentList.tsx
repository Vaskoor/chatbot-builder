// components/documents/DocumentList.tsx
'use client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiDelete } from '@/lib/api';
import { DocumentOut } from '@/types';
import { formatDistanceToNow } from 'date-fns';
export default function DocumentList({ botId }: { botId: string }) {
  const queryClient = useQueryClient();
  const { data: documents, isLoading } = useQuery<DocumentOut[]>({
    queryKey: ['documents', botId],
    queryFn: () => apiGet(`/api/bots/${botId}/documents`),
  });
  const deleteMutation = useMutation({
    mutationFn: (docId: string) => apiDelete(`/api/bots/${botId}/documents/${docId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', botId] });
    },
  });
  if (isLoading) return <div>Loading documents...</div>;
  return (
    <div>
      <h2 className="text-xl font-semibold mb-2">Uploaded Documents</h2>
      {documents?.length === 0 ? (
        <p className="text-gray-500">No documents uploaded.</p>
      ) : (
        <table className="w-full border">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-2 text-left">Name</th>
              <th className="p-2 text-left">Size</th>
              <th className="p-2 text-left">Status</th>
              <th className="p-2 text-left">Chunks</th>
              <th className="p-2 text-left">Version</th>
              <th className="p-2 text-left">Uploaded</th>
              <th className="p-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents?.map((doc) => (
              <tr key={doc.id} className="border-t">
                <td className="p-2">{doc.relative_path || doc.filename}</td>
                <td className="p-2">{(doc.size / 1024).toFixed(1)} KB</td>
                <td className="p-2">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    doc.status === 'done' ? 'bg-green-100 text-green-800' :
                    doc.status === 'failed' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>

                    {doc.status}
                  </span>
                </td>
                <td className="p-2">{doc.chunk_count}</td>
                <td className="p-2">{doc.version}</td>
                <td className="p-2 text-sm">
                  {formatDistanceToNow(new Date(doc.uploaded_at), { addSuffix: true })}
                </td>
                <td className="p-2">
                  <button
                    onClick={() => deleteMutation.mutate(doc.id)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
