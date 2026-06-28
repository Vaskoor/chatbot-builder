// app/(dashboard)/bot/[id]/settings/page.tsx
'use client';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiPatch, apiDelete } from '@/lib/api';
import { useState } from 'react';
import { BotOut } from '@/types';
export default function SettingsPage() {
  const params = useParams();
  const router = useRouter();
  const botId = params.id as string;
  const queryClient = useQueryClient();
  const { data: bot, isLoading } = useQuery<BotOut>({
    queryKey: ['bot', botId],
    queryFn: () => apiGet(`/api/bots/${botId}`),
  });
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  // Update when bot loaded
  if (bot && name === '' && description === '') {
    setName(bot.name);
    setDescription(bot.description || '');
    setSystemPrompt(bot.system_prompt || '');
  }
  const updateMutation = useMutation({
    mutationFn: (data: any) => apiPatch(`/api/bots/${botId}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bot', botId] });
      alert('Updated successfully');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => apiDelete(`/api/bots/${botId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bots'] });
      router.push('/dashboard');
    },
  });
  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate({ name, description, system_prompt: systemPrompt || undefined });
  };
  if (isLoading) return <div>Loading...</div>;
  return (
    <div className="max-w-lg">
      <h2 className="text-xl font-bold mb-4">Bot Settings</h2>
      <form onSubmit={handleUpdate} className="space-y-4">
        <div>
          <label className="block text-sm font-medium">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full border p-2 rounded"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full border p-2 rounded"
            rows={3}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">System Prompt</label>
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            className="w-full border p-2 rounded"
            rows={4}
          />
        </div>
        <button
          type="submit"
          disabled={updateMutation.isPending}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {updateMutation.isPending ? 'Saving...' : 'Save'}
        </button>
      </form>
      <div className="mt-8 border-t pt-4">
        <button
          onClick={() => {
            if (confirm('Delete this bot permanently?')) {

              deleteMutation.mutate();
            }
          }}
          className="bg-red-600 text-white px-4 py-2 rounded"
        >
          Delete Bot
        </button>
      </div>
    </div>
  );
}
