import { useState, useCallback, useRef, useEffect } from 'react';
import { sendChatMessage } from '../services/api';

/**
 * Custom hook for managing chat state and communication with the agent.
 */
export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [error, setError] = useState(null);
  const [properties, setProperties] = useState([]);
  const [toolsCalled, setToolsCalled] = useState([]);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(text.trim(), conversationId);

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.reply || 'I processed your request.',
        timestamp: new Date().toISOString(),
        properties: response.properties || [],
        explanations: response.explanations || [],
        toolsCalled: response.tools_called || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (response.properties?.length) {
        setProperties(response.properties);
      }
      if (response.tools_called) {
        setToolsCalled(response.tools_called);
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Something went wrong';
      setError(errorMessage);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
          timestamp: new Date().toISOString(),
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [conversationId, isLoading]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setProperties([]);
    setToolsCalled([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    conversationId,
    error,
    properties,
    toolsCalled,
    sendMessage,
    clearChat,
    messagesEndRef,
  };
}
