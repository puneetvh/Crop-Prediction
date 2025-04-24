import React, { useEffect, useState } from "react";
import axios from "axios";
import "../styles.css";

const WeatherCard = ({ city, useCurrentLocation, coordinates }) => {
  const [currentWeather, setCurrentWeather] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const apiKey = "d40b028769a50f27adc016fa18e36926";

  useEffect(() => {
    if (useCurrentLocation && coordinates) {
      fetchWeatherByCoordinates(coordinates.lat, coordinates.lon);
    } else if (city) {
      fetchWeatherByCity(city);
    }
  }, [city, useCurrentLocation, coordinates]);

  const fetchWeatherByCity = async (cityName) => {
    try {
      setLoading(true);
      const weatherRes = await axios.get(
        `https://api.openweathermap.org/data/2.5/weather?q=${cityName}&units=metric&appid=${apiKey}`
      );
      const forecastRes = await axios.get(
        `https://api.openweathermap.org/data/2.5/forecast?q=${cityName}&units=metric&appid=${apiKey}`
      );

      setCurrentWeather(weatherRes.data);

      const dailyForecast = forecastRes.data.list.filter((item) =>
        item.dt_txt.includes("12:00:00")
      );
      setForecast(dailyForecast);

      try {
        // ML prediction via Flask API
        const predRes = await axios.post(""https://b468-34-126-65-19.ngrok-free.app/predict"", { 
          city: weatherRes.data.name 
        });
        setPrediction(predRes.data);
      } catch (predErr) {
        console.warn("Prediction service unavailable:", predErr);
        setPrediction({ error: "Prediction service unavailable" });
      }

      setLoading(false);
    } catch (err) {
      console.error("Error fetching weather data:", err);
      setLoading(false);
      alert(err.response?.data?.message || "Failed to fetch weather data");
    }
  };

  const fetchWeatherByCoordinates = async (lat, lon) => {
    try {
      setLoading(true);
      const weatherRes = await axios.get(
        `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${apiKey}`
      );
      const forecastRes = await axios.get(
        `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&units=metric&appid=${apiKey}`
      );

      setCurrentWeather(weatherRes.data);

      const dailyForecast = forecastRes.data.list.filter((item) =>
        item.dt_txt.includes("12:00:00")
      );
      setForecast(dailyForecast);

      try {
        // ML prediction via Flask API
        const predRes = await axios.post("http://localhost:5000/predict", { 
          city: weatherRes.data.name 
        });
        setPrediction(predRes.data);
      } catch (predErr) {
        console.warn("Prediction service unavailable:", predErr);
        setPrediction({ error: "Prediction service unavailable" });
      }

      setLoading(false);
    } catch (err) {
      console.error("Error fetching weather data:", err);
      setLoading(false);
      alert("Failed to fetch weather data for your location");
    }
  };

  if (loading) return <div className="weather-loading">🔄 Loading weather...</div>;
  if (!currentWeather) return <div className="weather-error">⚠️ Could not load weather data.</div>;

  return (
    <div className="weather-card">
      <h2>📍 {currentWeather.name}</h2>
      <div className="weather-info">
        <p><strong>🌡 Temp:</strong> {currentWeather.main.temp} °C</p>
        <p><strong>🤔 Feels Like:</strong> {currentWeather.main.feels_like} °C</p>
        <p><strong>💧 Humidity:</strong> {currentWeather.main.humidity} %</p>
        <p><strong>💨 Wind:</strong> {currentWeather.wind.speed} m/s</p>
        <p><strong>🌥️ Condition:</strong> {currentWeather.weather[0].main} - {currentWeather.weather[0].description}</p>
        <img
          src={`http://openweathermap.org/img/wn/${currentWeather.weather[0].icon}@2x.png`}
          alt="weather-icon"
        />
      </div>

      <h3>📅 5-Day Forecast</h3>
      <div className="forecast-grid">
        {forecast.map((day, index) => (
          <div key={index} className="forecast-item">
            <p>{new Date(day.dt_txt).toLocaleDateString()}</p>
            <img
              src={`http://openweathermap.org/img/wn/${day.weather[0].icon}.png`}
              alt="icon"
            />
            <p>{day.main.temp} °C</p>
            <p>{day.weather[0].main}</p>
          </div>
        ))}
      </div>

      {prediction && !prediction.error && (
        <div className="prediction-card">
          <h3>🌦️ ML-Based Weather Predictions</h3>
          <p><strong>City:</strong> {prediction.city}</p>
          <p><strong>Will it rain?</strong> {prediction.predicted_rain ? "Yes 🌧️" : "No ☀️"}</p>
          <p><strong>Predicted Temp:</strong> {prediction.predicted_temperature} °C</p>
          <p><strong>Predicted Humidity:</strong> {prediction.predicted_humidity} %</p>
        </div>
      )}
      
      {prediction?.error && (
        <div className="prediction-error">
          ⚠️ Prediction Error: {prediction.error}
        </div>
      )}
    </div>
  );
};

export default WeatherCard;
