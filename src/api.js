// src/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: '/api', // Relative path for Vercel
  withCredentials: true,
});

// Function to call /predict endpoint
export const getWeatherPrediction = async (city) => {
  try {
    const response = await api.post('/predict', { city });
    return response.data;
  } catch (error) {
    if (error.response) {
      return { error: error.response.data.error };
    } else {
      return { error: 'Server not reachable' };
    }
  }
};

export default api;
