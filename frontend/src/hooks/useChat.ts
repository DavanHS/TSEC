import { useState, useCallback } from 'react';
import { queryProducts } from '../services/api';
import type { Message } from '../types';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = useCallback(async (content: string, imageData?: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content
    };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await queryProducts(content, imageData);
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        products: response.products.map(p => p.product)
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, loading, sendMessage, clearChat };
}