
CREATE TABLE users (id SERIAL PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, name TEXT, created_at TIMESTAMP DEFAULT NOW());
CREATE TABLE chatbots (id SERIAL PRIMARY KEY, user_id INT REFERENCES users(id) ON DELETE CASCADE, name TEXT NOT NULL, system_prompt TEXT, model TEXT DEFAULT 'gpt-4o', temperature REAL DEFAULT 0.7, status TEXT DEFAULT 'active', created_at TIMESTAMP DEFAULT NOW());
CREATE TABLE conversations (id SERIAL PRIMARY KEY, chatbot_id INT REFERENCES chatbots(id) ON DELETE CASCADE, session_id TEXT, created_at TIMESTAMP DEFAULT NOW());
CREATE TABLE messages (id SERIAL PRIMARY KEY, conversation_id INT REFERENCES conversations(id) ON DELETE CASCADE, role TEXT NOT NULL CHECK (role IN ('user','assistant','system')), content TEXT NOT NULL, tokens INT, created_at TIMESTAMP DEFAULT NOW());
CREATE TABLE api_keys (id SERIAL PRIMARY KEY, chatbot_id INT REFERENCES chatbots(id) ON DELETE CASCADE, key_hash TEXT UNIQUE NOT NULL, active BOOLEAN DEFAULT true, created_at TIMESTAMP DEFAULT NOW());
CREATE INDEX idx_conversations_chatbot ON conversations(chatbot_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
