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

export default api;
