// components/chat/MessageList.tsx
'use client';
import { MessageOut } from '@/types';
import ItineraryMap from './ItineraryMap';

export default function MessageList({ messages }: { messages: MessageOut[] }) {
  console.log("📨 Messages received in MessageList:", messages);

  return (
    <div className="space-y-4">
      {messages.map((msg) => {
        // Log each message to see if map_data exists
        if (msg.role === 'assistant') {
          console.log("🗺️ Assistant message map_data:", msg.map_data);
        }
        return (
          <div key={msg.id}>
            <div
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] p-3 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.content}</div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="text-xs opacity-70 mt-1">
                    Sources: {msg.sources.map((s: any) => s.source_file).join(', ')}
                  </div>
                )}
              </div>
            </div>
            {/* Render the map if map_data exists */}
            {msg.role === 'assistant' && msg.map_data && msg.map_data.length > 0 && (
              <div className="ml-12 mt-2">
                <ItineraryMap locations={msg.map_data} />
              </div>
            )}
            {/* TEMPORARY: show a green box if map_data exists but map doesn't render */}
            {msg.role === 'assistant' && msg.map_data && msg.map_data.length > 0 && (
              <div className="ml-12 mt-2 p-2 bg-green-200 text-green-800 rounded">
                ✅ Map should be here (map_data length: {msg.map_data.length})
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}