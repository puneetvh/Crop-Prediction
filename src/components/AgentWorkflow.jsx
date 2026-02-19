import React, { useState } from 'react';
import axios from 'axios';
import '../styles.css';

const AgentWorkflow = () => {
    const [city, setCity] = useState('');
    const [status, setStatus] = useState('idle'); // idle, loading, complete, error
    const [activeAgent, setActiveAgent] = useState(null); // weather, crop, disease
    const [data, setData] = useState(null);
    const [logs, setLogs] = useState([]);

    const addLog = (message) => {
        setLogs((prev) => [...prev, { time: new Date().toLocaleTimeString(), message }]);
    };

    const runWorkflow = async () => {
        if (!city) return;

        setStatus('loading');
        setLogs([]);
        setData(null);
        setActiveAgent('weather');
        addLog(`🚀 Starting workflow for ${city}...`);

        try {
            // Simulate visual delay for "Thinking" effect
            await new Promise(r => setTimeout(r, 800));
            addLog("🌍 Weather Agent: Analyzing climate data...");

            const res = await axios.post('/api/workflow', { city });
            const result = res.data;

            // WEATHER STEP
            setTimeout(() => {
                addLog(`✅ Weather Agent: Temp ${result.weather.current.current_temp}°C, Humidity ${result.weather.current.humidity}%`);
                setActiveAgent('crop');
            }, 1500);

            // CROP STEP
            setTimeout(() => {
                addLog(`🌱 Crop Agent: Analyzing soil & climate match...`);
                addLog(`✅ Crop Agent: Recommended ${result.crop.recommended_crop} (${result.crop.confidence} Match)`);
                setActiveAgent('disease');
            }, 3500);

            // DISEASE STEP
            setTimeout(() => {
                addLog(`🦠 Disease Agent: Scanning for potential risks...`);
                if (result.disease.status === 'Warning') {
                    addLog(`⚠️ Disease Agent: Alert! ${result.disease.message}`);
                } else {
                    addLog(`✅ Disease Agent: ${result.disease.message}`);
                }
                setActiveAgent(null);
                setData(result);
                setStatus('complete');
            }, 5500);

        } catch (err) {
            console.error(err);
            setStatus('error');
            addLog("❌ Error: Workflow failed. Server not reachable or internal error.");
        }
    };

    return (
        <div className="workflow-container">
            <h2>🤖 Multi-Agent AI Prediction System</h2>

            <div className="input-group">
                <input
                    type="text"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="Enter city (e.g., Vellore)"
                />
                <button onClick={runWorkflow} disabled={status === 'loading'}>
                    {status === 'loading' ? 'Running Agents...' : 'Start Workflow'}
                </button>
            </div>

            <div className="agents-grid">
                <div className={`agent-card ${activeAgent === 'weather' ? 'active' : ''} ${data ? 'done' : ''}`}>
                    <div className="icon">🌍</div>
                    <h3>Weather Agent</h3>
                    <p>Predicts climate conditions</p>
                </div>
                <div className="arrow">→</div>
                <div className={`agent-card ${activeAgent === 'crop' ? 'active' : ''} ${data ? 'done' : ''}`}>
                    <div className="icon">🌱</div>
                    <h3>Crop Agent</h3>
                    <p>Recommends optimal crops</p>
                </div>
                <div className="arrow">→</div>
                <div className={`agent-card ${activeAgent === 'disease' ? 'active' : ''} ${data ? 'done' : ''}`}>
                    <div className="icon">🦠</div>
                    <h3>Disease Agent</h3>
                    <p>Predicts disease risks</p>
                </div>
            </div>

            {/* Live Logs Console */}
            <div className="console-log">
                <div className="console-header">🖥️ Agent Interaction Log</div>
                <div className="console-body">
                    {logs.map((log, i) => (
                        <div key={i} className="log-entry">
                            <span className="timestamp">[{log.time}]</span> {log.message}
                        </div>
                    ))}
                    {status === 'loading' && <div className="typing-cursor">_</div>}
                </div>
            </div>

            {/* Final Results Display */}
            {status === 'complete' && data && (
                <div className="results-panel">
                    <h3>📊 Final AI Report</h3>

                    <div className="report-grid">
                        <div className="report-card weather">
                            <h4>Weather Forecast</h4>
                            <p><strong>Temp:</strong> {data.weather.current.current_temp}°C</p>
                            <p><strong>Humidity:</strong> {data.weather.current.humidity}%</p>
                            <p><strong>Rain Probability:</strong> {data.weather.will_rain ? "High" : "Low"}</p>
                        </div>

                        <div className="report-card crop">
                            <h4>Crop Recommendation</h4>
                            <p className="highlight">{data.crop.recommended_crop}</p>
                            <p><small>{data.crop.reasoning}</small></p>
                        </div>

                        <div className="report-card disease">
                            <h4>Disease Analysis</h4>
                            <p className={data.disease.status === 'Warning' ? 'danger' : 'safe'}>
                                {data.disease.status}
                            </p>
                            <p>{data.disease.message}</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AgentWorkflow;
