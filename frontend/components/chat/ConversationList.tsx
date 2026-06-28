// components/chat/ConversationList.tsx
import { ConversationOut } from '@/types';
import { formatDistanceToNow } from 'date-fns';
export default function ConversationList({
  conversations,
  selectedId,
  onSelect,
  onDelete,
}: {
  conversations: ConversationOut[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}) {
  return (
    <div className="space-y-1">
      {conversations.map((conv) => (
        <div
          key={conv.id}
          className={`p-2 rounded cursor-pointer flex justify-between items-center ${
            selectedId === conv.id ? 'bg-blue-100' : 'hover:bg-gray-200'
          }`}
          onClick={() => onSelect(conv.id)}
        >
          <div className="truncate">
            <div className="text-sm font-medium truncate">{conv.title}</div>
            <div className="text-xs text-gray-500">
              {formatDistanceToNow(new Date(conv.updated_at), { addSuffix: true })}
            </div>
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(conv.id); }}
            className="text-red-400 hover:text-red-600 text-xs"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}
