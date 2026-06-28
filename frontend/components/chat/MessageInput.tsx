'use client';
import { useState } from 'react';

export default function MessageInput({
  onSend,
  disabled,
}: {
  onSend: (msg: string) => void;
  disabled?: boolean;
}) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    console.log("🔘 handleSend called, input:", input);
    if (input.trim()) {
      console.log("📤 Calling onSend with:", input.trim());
      onSend(input.trim());
      setInput('');
    }
  };

  return (
    <div className="flex gap-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            console.log("⌨️ Enter key pressed");
            handleSend();
          }
        }}
        placeholder="Type a message..."
        className="flex-1 border p-2 rounded"
        disabled={disabled}
      />
      <button
        onClick={() => {
          console.log("🖱️ Send button clicked");
          handleSend();
        }}
        disabled={disabled || !input.trim()}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        Send
      </button>
    </div>
  );
}