// app/(dashboard)/layout.tsx
'use client';
import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/stores/authStore';
import { Bot, MessageSquare, FileText, Network, LogOut, Plus } from 'lucide-react';
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  useEffect(() => {
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);
  if (!user) return null;
  const navItems = [
    { href: '/dashboard', label: 'Bots', icon: Bot },
    { href: '/dashboard/create', label: 'New Bot', icon: Plus },
  ];
  return (
    <div className="flex h-screen">
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-4 text-xl font-bold">Chatbot Builder</div>
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}

                href={item.href}
                className={`flex items-center gap-3 p-2 rounded transition ${
                  active ? 'bg-gray-700' : 'hover:bg-gray-800'
                }`}
              >
                <item.icon size={20} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-gray-700">
          <div className="flex items-center justify-between">
            <span className="text-sm truncate">{user?.email}</span>
            <button
              onClick={() => { logout(); router.push('/login'); }}
              className="text-gray-400 hover:text-white"
            >
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
        {children}
      </main>
    </div>
  );
}
