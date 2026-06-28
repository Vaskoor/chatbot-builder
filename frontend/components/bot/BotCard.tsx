// components/bot/BotCard.tsx
import Link from 'next/link';
import { BotOut } from '@/types';
export function BotCard({ bot }: { bot: BotOut }) {
  return (
    <Link href={`/bot/${bot.id}`}>

      <div className="border rounded-lg p-4 hover:shadow-lg transition cursor-pointer">
        <h3 className="font-bold text-lg">{bot.name}</h3>
        <p className="text-sm text-gray-600">{bot.description || 'No description'}</p>
        <div className="mt-2 text-xs text-gray-400">
          Documents: {bot.document_count} | Chunks: {bot.chunk_count}
        </div>
        <div className="mt-1 text-xs text-gray-400">
          Created: {new Date(bot.created_at).toLocaleDateString()}
        </div>
      </div>
    </Link>
  );
}
