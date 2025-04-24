import React, { useEffect, useState } from "react";
import axios from "axios";

const HourlyForecastCard = ({ city, useCurrentLocation, coordinates }) => {
  const [hourlyData, setHourlyData] = useState([]);
  const [loading, setLoading] = useState(true);
  const apiKey = "d40b028769a50f27adc016fa18e36926";

  useEffect(() => {
    if (useCurrentLocation && coordinates) {
      fetchHourlyByCoordinates(coordinates.lat, coordinates.lon);
    } else if (city) {
      fetchHourlyByCity(city);
    }
  }, [city, useCurrentLocation, coordinates]);

  const fetchHourlyByCity = async (cityName) => {
    try {
      setLoading(true);
      const res = await axios.get(
        `https://api.openweathermap.org/data/2.5/forecast?q=${cityName}&units=metric&appid=${apiKey}`
      );
      // Get first 5 forecasts (hourly data)
      setHourlyData(res.data.list.slice(0, 5));
      setLoading(false);
    } catch (err) {
      console.error("Error fetching hourly data:", err);
      setLoading(false);
    }
  };

  const fetchHourlyByCoordinates = async (lat, lon) => {
    try {
      setLoading(true);
      const res = await axios.get(
        `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&units=metric&appid=${apiKey}`
      );
      // Get first 5 forecasts (hourly data)
      setHourlyData(res.data.list.slice(0, 5));
      setLoading(false);
    } catch (err) {
      console.error("Error fetching hourly data:", err);
      setLoading(false);
    }
  };

  if (loading) return <div className="weather-loading">Loading hourly forecast...</div>;
  if (hourlyData.length === 0) return null;

  return (
    <div className="hourly-forecast-card">
      <h3>Hourly Forecast</h3>
      <div className="hourly-items">
        {hourlyData.map((hour, index) => {
          const time = new Date(hour.dt * 1000).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          });
          
          return (
            <div key={index} className="hourly-item">
              <p className="hour-time">{time}</p>
              <img
                src={`http://openweathermap.org/img/wn/${hour.weather[0].icon}.png`}
                alt={hour.weather[0].description}
                className="hour-icon"
              />
              <p className="hour-temp">{Math.round(hour.main.temp)}°C</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default HourlyForecastCard;
