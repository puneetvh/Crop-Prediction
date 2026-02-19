
import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import DarkModeToggle from "./DarkModeToggle";
import SearchBar from "./SearchBar";
import axios from "axios";
import "../styles.css";
import { FaLeaf, FaBiohazard, FaThermometerHalf, FaMagic } from "react-icons/fa";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const name = location.state?.name;
  const [darkMode, setDarkMode] = useState(true);
  const [city, setCity] = useState("Vellore");
  const [useCurrentLocation, setUseCurrentLocation] = useState(false);
  const [coordinates, setCoordinates] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [weatherData, setWeatherData] = useState(null);
  const [hourlyForecast, setHourlyForecast] = useState([]);
  const [dailyForecast, setDailyForecast] = useState([]);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Agent State
  const [agentLoading, setAgentLoading] = useState(false);
  const [agentData, setAgentData] = useState(null);
  const [agentError, setAgentError] = useState(null);

  const apiKey = "d40b028769a50f27adc016fa18e36926";

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    document.body.classList.add("dark-theme");
  }, [name, navigate]);

  useEffect(() => {
    fetchWeatherByCity(city);
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.body.classList.toggle("dark-theme");
  };

  const handleSearch = (searchedCity) => {
    setUseCurrentLocation(false);
    setCoordinates(null);
    setCity(searchedCity);
    fetchWeatherByCity(searchedCity);
    setAgentData(null);
    setAgentError(null);
  };

  const handleCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setCoordinates({ lat: latitude, lon: longitude });
        setUseCurrentLocation(true);
        fetchWeatherByCoordinates(latitude, longitude);
      },
      (error) => alert("Failed to fetch location.")
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
      setHourlyForecast(forecastRes.data.list.slice(0, 5));
      setDailyForecast(forecastRes.data.list.filter(item => item.dt_txt.includes("12:00:00")));
      setCity(weatherRes.data.name);
      setIsLoading(false);
    } catch (err) {
      console.error("Error fetching weather:", err);
      setIsLoading(false);
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
      setHourlyForecast(forecastRes.data.list.slice(0, 5));
      setDailyForecast(forecastRes.data.list.filter(item => item.dt_txt.includes("12:00:00")));
      setCity(weatherRes.data.name);
      setIsLoading(false);
    } catch (err) {
      console.error("Error fetching weather:", err);
      setIsLoading(false);
    }
  };

  const runAgentAnalysis = async () => {
    setAgentLoading(true);
    setAgentError(null);
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/workflow", { city: city });
      if (response.data.error) {
        setAgentError(response.data.error);
      } else {
        console.log("Agent Data:", response.data);
        setAgentData(response.data);
      }
    } catch (e) {
      console.error("Agent Workflow Error Details:", e);
      let errorMsg = "Failed to connect to AI Agents.";

      if (e.code === "ERR_NETWORK") {
        errorMsg = "Network Error: Cannot reach backend at http://127.0.0.1:5000. Is it running?";
      } else if (e.response) {
        errorMsg = `Server Error (${e.response.status}): ${e.response.data.error || e.response.statusText}`;
      } else if (e.message) {
        errorMsg = `Error: ${e.message}`;
      }

      setAgentError(errorMsg);
    } finally {
      setAgentLoading(false);
    }
  };

  const formatTime = (date) => date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const getDayName = (dateStr) => ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][new Date(dateStr).getDay()];

  if (isLoading || !weatherData) {
    return <div className="modern-dashboard"><div style={{ padding: '50px', color: 'white' }}>Loading...</div></div>;
  }

  // Format data for chart
  const getChartData = () => {
    if (!agentData || !agentData.weather.forecast.temperature_90_days) return [];
    return agentData.weather.forecast.temperature_90_days.map((temp, index) => ({
      day: `D${index + 1}`,
      temp: temp,
      humidity: agentData.weather.forecast.humidity_90_days[index]
    }));
  };

  const chartData = getChartData();

  return (
    <div className={`modern-dashboard ${darkMode ? "dark-theme" : ""}`}>
      <div className="modern-navbar">
        <div className="app-brand">WeatherInsight</div>
        <div style={{ flex: 1, maxWidth: '500px', margin: '0 20px' }}>
          <SearchBar onSearch={handleSearch} />
        </div>
        <div className="navbar-actions">
          <button className="location-button" onClick={handleCurrentLocation}>
            <span style={{ fontSize: '1.2rem' }}>📍</span>
          </button>
          <DarkModeToggle darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
        </div>
      </div>

      <div className="modern-content three-column">

        {/* COL 1: Basic Info & 5-Day */}
        <div className="left-panel">
          <div className="location-time-card">
            <div style={{ opacity: 0.7, fontSize: '0.9rem' }}>{weatherData.name}</div>
            <div className="time-display">{formatTime(currentTime)}</div>
          </div>
          <div className="forecast-card">
            <h3>5-Day Forecast</h3>
            <div className="forecast-list">
              {dailyForecast.map((day, index) => (
                <div key={index} className="forecast-day-item">
                  <span className="day-name">{getDayName(day.dt_txt)}</span>
                  <span className="weather-icon">
                    <img src={`http://openweathermap.org/img/wn/${day.weather[0].icon}.png`} alt="icon" />
                  </span>
                  <span className="day-temp">{Math.round(day.main.temp)}°C</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* COL 2: Current Status & Hourly */}
        <div className="middle-panel">
          <div className="weather-main-card">
            <div className="temp-display">
              <div><div className="current-temp">{Math.round(weatherData.main.temp)}°C</div></div>
              <div className="weather-state">
                <img src={`http://openweathermap.org/img/wn/${weatherData.weather[0].icon}@2x.png`} alt="icon" className="weather-icon-large" />
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
                const time = new Date(hour.dt * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                return (
                  <div key={index} className="hourly-item">
                    <div className="hour-time">{time}</div>
                    <img src={`http://openweathermap.org/img/wn/${hour.weather[0].icon}.png`} alt="icon" className="hour-icon" />
                    <div className="hour-temp">{Math.round(hour.main.temp)}°</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* COL 3: AI Analysis & Graph */}
        <div className="right-panel">
          <div className="prediction-card full-height">
            <div className="prediction-header">
              <h3><FaMagic style={{ marginRight: '10px' }} /> AI Prediction</h3>
              <button className="analyze-btn" onClick={runAgentAnalysis} disabled={agentLoading}>
                {agentLoading ? "Running Models..." : "Analyze"}
              </button>
            </div>

            {agentError && <div className="error-msg">{agentError}</div>}

            {agentData ? (
              <div className="agent-results">
                {/* 90 Day Graph */}
                <div className="chart-container">
                  <h4><FaThermometerHalf /> 3-Month Forecast Trend</h4>
                  <div style={{ width: '100%', height: '200px' }}>
                    <ResponsiveContainer>
                      <AreaChart data={chartData}>
                        <defs>
                          <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#4c8bf5" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="#4c8bf5" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <XAxis dataKey="day" hide />
                        <Tooltip
                          contentStyle={{ backgroundColor: '#2d2d2d', border: 'none', borderRadius: '8px' }}
                          itemStyle={{ color: '#fff' }}
                        />
                        <Area type="monotone" dataKey="temp" stroke="#4c8bf5" fillOpacity={1} fill="url(#colorTemp)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Analysis Results */}
                <div className="agent-summary">
                  <div className="summary-box">
                    <h4><FaLeaf /> Crop</h4>
                    <div className="highlight-text">{agentData.crop.recommended_crop}</div>
                    <div className="sub-text">{agentData.crop.confidence} Confidence</div>
                  </div>
                  <div className="summary-box">
                    <h4><FaBiohazard /> Disease</h4>
                    <div className={agentData.disease.status === 'Healthy' ? 'status-valid' : 'status-warning'}>
                      {agentData.disease.status}
                    </div>
                    {agentData.disease.diseases_detected && agentData.disease.diseases_detected.length > 0 &&
                      <div className="risk-list">{agentData.disease.diseases_detected.join(", ")}</div>
                    }
                  </div>
                </div>
              </div>
            ) : (
              <div className="placeholder-msg">
                Click "Analyze" to run the 90-day ML prediction models for Crop & Disease.
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;