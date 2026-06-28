// frontend/types/index.ts
export interface User {
  id: string;
  email: string;
  full_name?: string;
  created_at: string;
}
export interface BotOut {
  id: string;
  name: string;
  description?: string;
  system_prompt?: string;
  created_at: string;
  updated_at: string;
  document_count: number;
  chunk_count: number;
}
export interface DocumentOut {
  id: string;
  filename: string;
  relative_path?: string;
  size: number;
  status: 'pending' | 'processing' | 'done' | 'failed' | 'superseded';
  chunk_count: number;
  version: number;
  is_latest: boolean;
  uploaded_at: string;
  error_message?: string;
}
export interface ConversationOut {

  id: string;
  bot_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}
export interface MessageOut {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: any[];
  created_at: string;
  map_data?: MapLocation[];   // new
}
export interface ConversationDetail extends ConversationOut {
  messages: MessageOut[];
}
// types/index.ts – add this interface
export interface GraphData {
  nodes: Array<{ id: string; name: string; type: string }>;
  edges: Array<{ source: string; target: string; relation: string; weight: number }>;
  node_count: number;
  edge_count: number;
}
// types/index.ts – add this export
export interface ChatResponse {
  answer: string;
  conversation_id: string;
  sources: any[];
  retrieval_strategy?: string;
}
export interface UserOut {
  id: string;
  email: string;
  full_name?: string;
  created_at: string;
}
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserOut;
}
export interface MapLocation {
  day: number;
  name: string;
  lat: number;
  lng: number;
  description?: string;
}
