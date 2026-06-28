// app/(dashboard)/dashboard/create/page.tsx
'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiPost } from '@/lib/api';
export default function CreateBotPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [error, setError] = useState('');
  const mutation = useMutation({
    mutationFn: (data: any) => apiPost('/api/bots', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bots'] });
      router.push('/dashboard');
    },
    onError: (err: any) => setError(err.message),
  });
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({ name, description, system_prompt: systemPrompt || undefined });
  };
  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-4">Create New Bot</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium">Bot Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}

            className="w-full border p-2 rounded"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Description (optional)</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full border p-2 rounded"
            rows={3}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">System Prompt (optional)</label>
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            className="w-full border p-2 rounded"
            rows={4}
            placeholder="e.g., You are a helpful travel assistant..."
          />
        </div>
        {error && <div className="text-red-500 text-sm">{error}</div>}
        <button
          type="submit"
          disabled={mutation.isPending}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {mutation.isPending ? 'Creating...' : 'Create Bot'}
        </button>
      </form>
    </div>
  );
}
