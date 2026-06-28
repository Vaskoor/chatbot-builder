'use client';
import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiPost, apiDelete } from '@/lib/api';
import { ConversationOut, ConversationDetail, ChatResponse } from '@/types';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import ConversationList from './ConversationList';

export default function ChatInterface({ botId }: { botId: string }) {
  const queryClient = useQueryClient();
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [isNewConversation, setIsNewConversation] = useState(false);

  // Fetch conversations
  const { data: conversations, isLoading: convLoading } = useQuery<ConversationOut[]>({
    queryKey: ['conversations', botId],
    queryFn: () => apiGet(`/api/bots/${botId}/conversations`),
  });

  // Fetch messages for selected conversation
  const { data: conversationDetail } = useQuery<ConversationDetail>({
    queryKey: ['conversation', selectedConversationId],
    queryFn: () => apiGet(`/api/bots/${botId}/conversations/${selectedConversationId}`),
    enabled: !!selectedConversationId,
  });

  // Send message
  const sendMutation = useMutation<ChatResponse, Error, string>({
    mutationFn: (message: string) =>
      apiPost(`/api/bots/${botId}/chat`, {
        message,
        conversation_id: selectedConversationId || undefined,
      }),
    onSuccess: (data) => {
      console.log("✅ Chat API response:", data);

      const newConversationId = data.conversation_id;
      if (!selectedConversationId) {
        // We were creating a new conversation
        setSelectedConversationId(newConversationId);
        setIsNewConversation(false);
      }

      const conversationId = selectedConversationId || newConversationId;
      if (conversationId) {
        // Add the new assistant message to the cache with map_data
        queryClient.setQueryData<ConversationDetail>(
          ['conversation', conversationId],
          (old) => {
            const newMessage = {
              id: 'temp-' + Date.now(),
              role: 'assistant',
              content: data.answer,
              sources: data.sources || [],
              created_at: new Date().toISOString(),
              map_data: data.map_data || [],
            };
            if (!old) {
              return {
                id: conversationId,
                bot_id: botId,
                title: "New Conversation",
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                messages: [newMessage],
              };
            }
            return {
              ...old,
              messages: [...old.messages, newMessage],
            };
          }
        );
      }

      // Refresh sidebar conversations
      queryClient.invalidateQueries({ queryKey: ['conversations', botId] });
    },
    onError: (error) => {
      console.error("❌ Chat API error:", error);
    },
  });

  // Delete conversation
  const deleteConv = useMutation<void, Error, string>({
    mutationFn: (convId: string) =>
      apiDelete(`/api/bots/${botId}/conversations/${convId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations', botId] });
      if (selectedConversationId) {
        setSelectedConversationId(null);
        setIsNewConversation(true); // stay in new conversation mode
      }
    },
  });

  // Auto-select first conversation only if we are not creating a new one
  useEffect(() => {
    if (!isNewConversation && !selectedConversationId && conversations && conversations.length > 0) {
      setSelectedConversationId(conversations[0].id);
    }
  }, [conversations, selectedConversationId, isNewConversation]);

  const handleNewConversation = () => {
    setSelectedConversationId(null);
    setIsNewConversation(true);
  };

  const messages = conversationDetail?.messages || [];

  return (
    <div className="flex h-[600px] border rounded-lg overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 border-r bg-gray-50 p-2 overflow-y-auto">
        <ConversationList
          conversations={conversations || []}
          selectedId={selectedConversationId}
          onSelect={(id) => {
            setSelectedConversationId(id);
            setIsNewConversation(false);
          }}
          onDelete={(id) => deleteConv.mutate(id)}
        />
        <button
          onClick={handleNewConversation}
          className="mt-2 w-full text-sm bg-blue-100 text-blue-700 p-2 rounded"
        >
          + New Conversation
        </button>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 && (
            <div className="text-gray-400 text-center mt-20">
              {isNewConversation ? "Start typing to begin a new conversation!" : "No messages yet. Start a conversation!"}
            </div>
          )}
          <MessageList messages={messages} />
          {sendMutation.isPending && (
            <div className="text-gray-400 text-sm">Thinking...</div>
          )}
        </div>
        <div className="border-t p-2">
          <MessageInput
            onSend={(msg) => sendMutation.mutate(msg)}
            disabled={sendMutation.isPending}
          />
        </div>
      </div>
    </div>
  );
}