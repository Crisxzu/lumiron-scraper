import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5100/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchPerson = async (firstName, lastName, company, forceRefresh = false) => {
  try {
    const response = await api.post('/search', {
      first_name: firstName,
      last_name: lastName,
      company: company,
      force_refresh: forceRefresh,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Network error occurred' };
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Recherche avec streaming SSE pour suivre la progression en temps réel
 * @param {string} firstName
 * @param {string} lastName
 * @param {string} company
 * @param {boolean} forceRefresh
 * @param {function} onProgress - Callback (percent, message, step)
 * @param {function} onComplete - Callback (result)
 * @param {function} onError - Callback (error)
 * @returns {function} cleanup function pour annuler la requête
 */
export const searchPersonStream = (firstName, lastName, company, forceRefresh = false, onProgress, onComplete, onError) => {
  let aborted = false;

  const executeStream = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/search-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          company: company,
          force_refresh: forceRefresh,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (!aborted) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            if (data.type === 'progress') {
              onProgress?.(data.percent, data.message, data.step);
            } else if (data.type === 'complete') {
              onComplete?.({
                success: true,
                data: data.data,
                cached: data.cached || false,
                cache_age_seconds: data.cache_age_seconds,
              });
              break;
            } else if (data.type === 'error') {
              onError?.(data.message);
              break;
            }
          }
        }
      }
    } catch (error) {
      if (!aborted) {
        onError?.(error.message || 'Erreur de connexion');
      }
    }
  };

  executeStream();

  // Retourner une fonction de cleanup
  return () => {
    aborted = true;
  };
};

export default api;
