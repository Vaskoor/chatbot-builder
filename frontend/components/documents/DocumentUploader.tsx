// components/documents/DocumentUploader.tsx
'use client';
import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiUpload } from '@/lib/api';
export default function DocumentUploader({ botId }: { botId: string }) {
  const queryClient = useQueryClient();
  const [uploading, setUploading] = useState(false);
  const mutation = useMutation({
    mutationFn: async (formData: FormData) => {
      const result = await apiUpload(`/api/bots/${botId}/documents/upload`, formData);
      return result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', botId] });
      setUploading(false);
    },
    onError: (err) => {
      alert('Upload failed: ' + err.message);
      setUploading(false);
    },
  });
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    const formData = new FormData();
    // For each file, append to 'files'
    acceptedFiles.forEach((file) => {
      formData.append('files', file);

    });
    // Optionally, we could extract relative paths if using folder upload, but for now we just use filename.
    setUploading(true);
    mutation.mutate(formData);
  }, [mutation]);
  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    multiple: true,
  });
  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition">
      <div {...getRootProps()}>
        <input {...getInputProps()} />
        {uploading ? (
          <p>Uploading...</p>
        ) : (
          <p>Drag & drop files here, or click to select</p>
        )}
        <p className="text-sm text-gray-500">(PDF, DOCX, CSV, Excel, TXT, Images)</p>
      </div>
    </div>
  );
}
