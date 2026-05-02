import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot, User, Image as ImageIcon } from 'lucide-react';
import type { Message } from '../types';

interface ChatInterfaceProps {
  messages: Message[];
  loading: boolean;
  onSend: (content: string, imageData?: string) => void;
}

export default function ChatInterface({ messages, loading, onSend }: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const [imageData, setImageData] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSend(input.trim(), imageData || undefined);
      setInput('');
    }
  };

  const handleImageUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      setImageData(result.split(',')[1]);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg border">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <Bot className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="font-medium">Ask me about products!</p>
            <p className="text-sm text-gray-400 mt-1">
              Try: "What are the best headphones under 5000?"
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-200'
              }`}>
                {msg.role === 'user' ? (
                  <User className="w-5 h-5 text-white" />
                ) : (
                  <Bot className="w-5 h-5 text-gray-600" />
                )}
              </div>
              <div className={`flex-1 max-w-[80%] ${msg.role === 'user' ? 'text-right' : ''}`}>
                <div className={`inline-block p-3 rounded-lg ${
                  msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'
                }`}>
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <p className="text-xs text-gray-500 mt-1">
                    Sources: {msg.sources.join(', ')}
                  </p>
                )}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
              <Bot className="w-5 h-5 text-gray-600" />
            </div>
            <div className="bg-gray-100 p-3 rounded-lg">
              <Loader2 className="w-5 h-5 text-gray-600 animate-spin" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex gap-2">
          <label className="p-2 text-gray-500 hover:text-gray-700 cursor-pointer">
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleImageUpload(e.target.files[0])}
            />
            <ImageIcon className="w-5 h-5" />
          </label>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about products..."
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        {imageData && (
          <p className="text-xs text-green-600 mt-2">Image attached for visual search</p>
        )}
      </form>
    </div>
  );
}