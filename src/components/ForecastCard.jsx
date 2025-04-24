import React, { useEffect, useState } from "react";
import axios from "axios";

const ForecastCard = ({ city, useCurrentLocation, coordinates }) => {
  const [forecastData, setForecastData] = useState([]);
  const [loading, setLoading] = useState(true);
  const apiKey = "d40b028769a50f27adc016fa18e36926";

  useEffect(() => {
    if (useCurrentLocation && coordinates) {
      fetchForecastByCoordinates(coordinates.lat, coordinates.lon);
    } else if (city) {
      fetchForecastByCity(city);
    }
  }, [city, useCurrentLocation, coordinates]);

  const fetchForecastByCity = async (cityName) => {
    try {
      setLoading(true);
      const res = await axios.get(
        `https://api.openweathermap.org/data/2.5/forecast?q=${cityName}&units=metric&appid=${apiKey}`
      );
      // Filter to get one forecast per day (at noon)
      const dailyData = res.data.list.filter(item => 
        item.dt_txt.includes("12:00:00")
      );
      
      setForecastData(dailyData);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching forecast data:", err);
      setLoading(false);
    }
  };

  const fetchForecastByCoordinates = async (lat, lon) => {
    try {
      setLoading(true);
      const res = await axios.get(
        `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&units=metric&appid=${apiKey}`
      );
      // Filter to get one forecast per day (at noon)
      const dailyData = res.data.list.filter(item => 
        item.dt_txt.includes("12:00:00")
      );
      
      setForecastData(dailyData);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching forecast data:", err);
      setLoading(false);
    }
  };

  if (loading) return <div className="weather-loading">Loading forecast...</div>;
  if (forecastData.length === 0) return null;

  const getDayName = (dateStr) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const date = new Date(dateStr);
    return days[date.getDay()];
  };

  return (
    <div className="forecast-card">
      <h3>5-Day Forecast</h3>
      <div className="forecast-grid">
        {forecastData.map((day, index) => (
          <div key={index} className="forecast-item">
            <p>{getDayName(day.dt_txt)}</p>
            <img
              src={`http://openweathermap.org/img/wn/${day.weather[0].icon}.png`}
              alt={day.weather[0].description}
            />
            <p>{Math.round(day.main.temp)}°C</p>
            <p>{day.weather[0].main}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ForecastCard;
