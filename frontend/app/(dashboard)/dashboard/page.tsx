// app/(dashboard)/dashboard/page.tsx
'use client';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { apiGet } from '@/lib/api';
import { BotCard } from '@/components/bot/BotCard';
import { BotOut } from '@/types';
export default function DashboardPage() {
  const { data: bots, isLoading, error } = useQuery<BotOut[]>({
    queryKey: ['bots'],
    queryFn: () => apiGet('/api/bots'),
  });
  if (isLoading) return <div>Loading bots...</div>;
  if (error) return <div>Error loading bots: {(error as Error).message}</div>;
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Your Bots</h1>

        <Link href="/dashboard/create" className="bg-blue-600 text-white px-4 py-2 rounded">
          + New Bot
        </Link>
      </div>
      {bots?.length === 0 ? (
        <p className="text-gray-500">No bots yet. Create one!</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {bots?.map((bot) => (
            <BotCard key={bot.id} bot={bot} />
          ))}
        </div>
      )}
    </div>
  );
}
