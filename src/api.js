// src/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000', // Flask API URL
  withCredentials: true, // For session handling if needed
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
