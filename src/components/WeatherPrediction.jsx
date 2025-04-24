import React, { useState } from 'react';
import { getWeatherPrediction } from '../api'; // Assuming you have api.js in the same folder

const WeatherPrediction = () => {
  const [city, setCity] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGetPrediction = async () => {
    if (!city) {
      setError("City name is required.");
      return;
    }
    setLoading(true);
    setError('');

    try {
      const result = await getWeatherPrediction(city);

      if (result.error) {
        setError(result.error);
        setWeatherData(null);
      } else {
        setWeatherData(result);
      }
    } catch (err) {
      console.error('Error fetching prediction:', err);
      setError('Failed to fetch weather data');
      setWeatherData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Weather Prediction</h2>

      <input
        type="text"
        placeholder="Enter city"
        value={city}
        onChange={(e) => setCity(e.target.value)}
      />
      <button onClick={handleGetPrediction} disabled={loading}>
        {loading ? 'Loading...' : 'Get Prediction'}
      </button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {weatherData && (
        <div style={{ marginTop: '1rem' }}>
          <p><strong>City:</strong> {weatherData.city}</p>
          <p><strong>Country:</strong> {weatherData.country}</p>
          <p><strong>Current Temperature:</strong> {weatherData.current_temp}°C</p>
          <p><strong>Humidity:</strong> {weatherData.humidity}%</p>
          <p><strong>Weather Condition:</strong> {weatherData.description}</p>
          <p><strong>Pressure:</strong> {weatherData.pressure} hPa</p>

          {/* Display Predicted Values */}
          <div style={{ marginTop: '1rem' }}>
            <p><strong>Predicted Temperatures (Next 7 Days):</strong></p>
            <ul>
              {weatherData.predicted_temperatures.map((temp, idx) => (
                <li key={idx}>{temp.toFixed(1)}°C</li>
              ))}
            </ul>

            <p><strong>Predicted Humidity (Next 7 Days):</strong></p>
            <ul>
              {weatherData.predicted_humidity.map((hum, idx) => (
                <li key={idx}>{hum.toFixed(1)}%</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default WeatherPrediction;
