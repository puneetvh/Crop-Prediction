import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import DarkModeToggle from "./DarkModeToggle";
import SearchBar from "./SearchBar";
import { getWeatherPrediction } from "../api";
import axios from "axios";
import "../styles.css";
import WeatherPrediction from "./WeatherPrediction";

const Dashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const name = location.state?.name;
  const [darkMode, setDarkMode] = useState(true); // Default to dark mode for new design
  const [city, setCity] = useState("Athens"); // Default city
  const [useCurrentLocation, setUseCurrentLocation] = useState(false);
  const [coordinates, setCoordinates] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [weatherData, setWeatherData] = useState(null);
  const [hourlyForecast, setHourlyForecast] = useState([]);
  const [dailyForecast, setDailyForecast] = useState([]);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [prediction, setPrediction] = useState(null);
  const apiKey = "d40b028769a50f27adc016fa18e36926";

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!name) {
      navigate("/"); // Redirect to login if name not available
    }
    document.body.classList.add("dark-theme"); // Apply dark theme by default
  }, [name, navigate]);

  useEffect(() => {
    if (useCurrentLocation && coordinates) {
      fetchWeatherByCoordinates(coordinates.lat, coordinates.lon);
    } else if (city) {
      fetchWeatherByCity(city);
    }
  }, [city, useCurrentLocation, coordinates]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.body.classList.toggle("dark-theme");
  };

  const handleSearch = (searchedCity) => {
    setUseCurrentLocation(false); // Reset current location flag
    setCoordinates(null); // Clear any saved coordinates
    setCity(searchedCity);
  };

  const handleCurrentLocation = () => {
    setIsLoading(true);

    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      setIsLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setCoordinates({ lat: latitude, lon: longitude });
        setUseCurrentLocation(true);
        setCity(""); // Clear city since we're using coordinates
        setIsLoading(false);
      },
      (error) => {
        alert("Failed to fetch location. Please allow location access.");
        console.error(error);
        setIsLoading(false);
      }
    );
  };

  const fetchWeatherByCity = async (cityName) => {
    try {
      setIsLoading(true);
      const weatherRes = await axios.get(
        `https://api.openweathermap.org/data/2.5/weather?q=${cityName}&units=metric&appid=${apiKey}`
      );
      const forecastRes = await axios.get(
        `https://api.openweathermap.org/data/2.5/forecast?q=${cityName}&units=metric&appid=${apiKey}`
      );

      setWeatherData(weatherRes.data);
      
      // Set hourly forecast (next 5 intervals)
      setHourlyForecast(forecastRes.data.list.slice(0, 5));
      
      // Set daily forecast (one forecast per day at noon)
      const dailyData = forecastRes.data.list.filter(item => 
        item.dt_txt.includes("12:00:00")
      );
      setDailyForecast(dailyData);

      try {
        // ML prediction via Flask API
        const predRes = await getWeatherPrediction(weatherRes.data.name);
        setPrediction(predRes);
      } catch (predErr) {
        console.warn("Prediction service unavailable:", predErr);
        setPrediction({ error: "Prediction service unavailable" });
      }

      setIsLoading(false);
    } catch (err) {
      console.error("Error fetching weather data:", err);
      setIsLoading(false);
      alert(err.response?.data?.message || "Failed to fetch weather data");
    }
  };

  const fetchWeatherByCoordinates = async (lat, lon) => {
    try {
      setIsLoading(true);
      const weatherRes = await axios.get(
        `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${apiKey}`
      );
      const forecastRes = await axios.get(
        `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&units=metric&appid=${apiKey}`
      );

      setWeatherData(weatherRes.data);
      
      // Set hourly forecast (next 5 intervals)
      setHourlyForecast(forecastRes.data.list.slice(0, 5));
      
      // Set daily forecast (one forecast per day at noon)
      const dailyData = forecastRes.data.list.filter(item => 
        item.dt_txt.includes("12:00:00")
      );
      setDailyForecast(dailyData);

      try {
        // ML prediction via Flask API
        const predRes = await getWeatherPrediction(weatherRes.data.name);
        setPrediction(predRes);
      } catch (predErr) {
        console.warn("Prediction service unavailable:", predErr);
        setPrediction({ error: "Prediction service unavailable" });
      }

      setCity(weatherRes.data.name);
      setIsLoading(false);
    } catch (err) {
      console.error("Error fetching weather data:", err);
      setIsLoading(false);
      alert("Failed to fetch weather data for your location");
    }
  };

  // Format time to HH:MM
  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Get day name from date
  const getDayName = (dateStr) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const date = new Date(dateStr);
    return days[date.getDay()];
  };

  if (isLoading || !weatherData) {
    return (
      <div className="dashboard-container">
        <div className="weather-loading">Loading weather data...</div>
      </div>
    );
  }

  return (
    <div className={`modern-dashboard ${darkMode ? "dark-theme" : ""}`}>
      {/* Top Navigation Bar */}
      <div className="modern-navbar">
        <div className="app-brand">WeatherInsight</div>
        <SearchBar onSearch={handleSearch} />
        <div className="navbar-actions">
          <button className="location-button" onClick={handleCurrentLocation}>
            <span className="location-icon">📍</span>
          </button>
          <DarkModeToggle darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
        </div>
      </div>
      
      {/* Main Content Grid */}
      <div className="modern-content">
        {/* Left Column */}
        <div className="left-panel">
          <div className="location-time-card">
            <h2>{weatherData.name}</h2>
            <div className="time-display">{formatTime(currentTime)}</div>
          </div>
          
          <div className="forecast-card">
            <h3>5-Day Forecast</h3>
            <div className="forecast-list">
              {dailyForecast.map((day, index) => (
                <div key={index} className="forecast-day-item">
                  <span className="day-name">{getDayName(day.dt_txt)}</span>
                  <span className="weather-icon">
                    <img
                      src={`http://openweathermap.org/img/wn/${day.weather[0].icon}.png`}
                      alt={day.weather[0].description}
                    />
                  </span>
                  <span className="day-temp">{Math.round(day.main.temp)}°C</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Right Column */}
        <div className="right-panel">
          <div className="weather-main-card">
            <div className="temp-display">
              <div className="current-temp">{Math.round(weatherData.main.temp)}°C</div>
              <div className="weather-state">
                <img 
                  src={`http://openweathermap.org/img/wn/${weatherData.weather[0].icon}@2x.png`} 
                  alt={weatherData.weather[0].description} 
                  className="weather-icon-large"
                />
                <span>{weatherData.weather[0].main}</span>
              </div>
            </div>
            
            <div className="weather-metrics">
              <div className="metric-item">
                <div className="metric-icon">💨</div>
                <div className="metric-label">Wind</div>
                <div className="metric-value">{weatherData.wind.speed} m/s</div>
              </div>
              <div className="metric-item">
                <div className="metric-icon">💧</div>
                <div className="metric-label">Humidity</div>
                <div className="metric-value">{weatherData.main.humidity}%</div>
              </div>
              <div className="metric-item">
                <div className="metric-icon">🌡️</div>
                <div className="metric-label">Pressure</div>
                <div className="metric-value">{weatherData.main.pressure} hPa</div>
              </div>
            </div>
          </div>
          
          <div className="hourly-forecast-card">
            <h3>Hourly Forecast</h3>
            <div className="hourly-list">
              {hourlyForecast.map((hour, index) => {
                const time = new Date(hour.dt * 1000).toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                });
                
                return (
                  <div key={index} className="hourly-item">
                    <div className="hour-time">{time}</div>
                    <img
                      src={`http://openweathermap.org/img/wn/${hour.weather[0].icon}.png`}
                      alt={hour.weather[0].description}
                      className="hour-icon"
                    />
                    <div className="hour-temp">{Math.round(hour.main.temp)}°</div>
                  </div>
                );
              })}
              <WeatherPrediction />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;