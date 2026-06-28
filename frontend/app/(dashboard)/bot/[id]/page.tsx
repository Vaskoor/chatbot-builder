// app/(dashboard)/bot/[id]/page.tsx
'use client';
import { useParams, usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { apiGet } from '@/lib/api';
import { BotOut } from '@/types';
export default function BotLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const botId = params.id as string;
  const pathname = usePathname();
  const { data: bot, isLoading } = useQuery<BotOut>({
    queryKey: ['bot', botId],
    queryFn: () => apiGet(`/api/bots/${botId}`),
  });
  const tabs = [
    { href: `/bot/${botId}/chat`, label: 'Chat' },
    { href: `/bot/${botId}/documents`, label: 'Documents' },
    { href: `/bot/${botId}/graph`, label: 'Graph' },
    { href: `/bot/${botId}/settings`, label: 'Settings' },
  ];
  if (isLoading) return <div>Loading bot...</div>;
  if (!bot) return <div>Bot not found</div>;
  return (
    <div>
      <div className="flex items-center gap-4 mb-4">
        <Link href="/dashboard" className="text-blue-600 hover:underline">
          ← Back
        </Link>
        <h1 className="text-2xl font-bold">{bot.name}</h1>
        <span className="text-sm text-gray-500">{bot.description}</span>
      </div>
      <div className="border-b border-gray-200 mb-4">
        <div className="flex gap-4">
          {tabs.map((tab) => (
            <Link

              key={tab.href}
              href={tab.href}
              className={`px-4 py-2 border-b-2 transition ${
                pathname === tab.href
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
            </Link>
          ))}
        </div>
      </div>
      <div>{children}</div>
    </div>
  );
}
