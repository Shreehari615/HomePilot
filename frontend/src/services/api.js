import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for LLM calls
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.error || error.message || 'Network error';
    console.error(`[API Error] ${message}`);
    return Promise.reject(error);
  }
);

/**
 * Send a chat message to the agent.
 * @param {string} message - User's natural language message
 * @param {string|null} conversationId - Optional conversation ID for context
 * @returns {Promise<object>} Chat response with properties and explanations
 */
export const sendChatMessage = async (message, conversationId = null) => {
  const { data } = await api.post('/api/chat', {
    message,
    conversation_id: conversationId,
  });
  return data;
};

/**
 * Search properties with filters (non-agent).
 */
export const searchProperties = async (filters) => {
  const { data } = await api.post('/api/search', filters);
  return data;
};

/**
 * Get all properties for browsing.
 */
export const getAllProperties = async () => {
  const { data } = await api.get('/api/properties');
  return data;
};

/**
 * Get full details for a single property.
 */
export const getPropertyDetail = async (propertyId) => {
  const { data } = await api.get(`/api/property/${propertyId}`);
  return data;
};

/**
 * Get price history for a property.
 */
export const getPropertyHistory = async (propertyId) => {
  const { data } = await api.get(`/api/history/${propertyId}`);
  return data;
};

/**
 * Re-rank properties with custom weights.
 */
export const rankProperties = async (propertyIds, weights = null) => {
  const { data } = await api.post('/api/rank', {
    property_ids: propertyIds,
    weights,
  });
  return data;
};

/**
 * Get conversation history.
 */
export const getConversation = async (conversationId) => {
  const { data } = await api.get(`/api/conversation?conversation_id=${conversationId}`);
  return data;
};

/**
 * Health check.
 */
export const healthCheck = async () => {
  const { data } = await api.get('/api/health');
  return data;
};

export default api;
