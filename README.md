# AgriGenius: AI-Powered Smart Agriculture System

AgriGenius is a comprehensive ML-based crop recommendation and disease prediction system tailored for farmers in Tamil Nadu. The system leverages an AI Agent orchestration pipeline to seamlessly connect localized weather prediction, crop suitability recommendations, and disease risk analysis.

## Features

- **Agentic Pipeline**: Utilizes an orchestrated flow of AI agents to sequentially process inputs and output predictions without human intervention.
- **Weather Prediction**: Predicts temperature, humidity, and rainfall based on district using trained ML models (XGBoost/Scikit-Learn).
- **Crop Recommendation**: Analyzes N, P, K, pH levels, soil color, and predicted weather to recommend the most suitable crop.
- **Disease Prediction**: Assesses the recommended crop against historical disease models to predict potential threats.
- **Interactive Dashboard**: A dynamic React-based frontend dashboard presenting analytics, metrics, and actionable recommendations.

## Tech Stack & Tools

### Frontend
- **React 19 & Vite**: Fast, modern frontend framework and build tool.
- **React Router DOM**: Handling seamless page navigation.
- **Recharts**: Data visualization for displaying weather trends and metrics.
- **Axios**: HTTP client for communicating with the Python backend.

### Backend & Machine Learning
- **Python & Flask**: Lightweight WSGI web application framework serving as the API backend.
- **Scikit-Learn**: Machine learning library used for data preprocessing (Label Encoders) and building baseline predictive models.
- **XGBoost**: High-performance gradient boosting library used for robust weather prediction modeling.
- **Joblib**: Efficient serialization of trained ML models (`.pkl` and `.json` model files).
- **NumPy & Pandas**: Essential libraries for data manipulation and mathematical operations.

## Project Structure

```
├── api/                  # Python Flask Backend & ML Pipeline
│   ├── agents/           # Orchestration logic for the AI Agents
│   ├── models/           # Pre-trained ML models (.pkl, .json)
│   ├── index.py          # Main Flask application entry point
│   └── requirements.txt  # Python dependencies
├── src/                  # React Frontend Source
│   ├── components/       # Reusable UI components (Dashboard, etc.)
│   ├── api.js            # API utility functions
│   └── main.jsx          # React entry point
├── package.json          # Node.js dependencies
└── start_app.bat         # Windows script to launch both servers
```

## Running the Application Locally

1. **Install Frontend Dependencies:**
   ```bash
   npm install
   ```

2. **Install Backend Dependencies:**
   ```bash
   pip install -r api/requirements.txt
   ```

3. **Start the Application:**
   On Windows, you can simply run the provided batch script which starts both the React frontend and Flask backend simultaneously:
   ```cmd
   start_app.bat
   ```

   *Alternatively, run them manually in separate terminals:*
   - Backend: `python api/index.py` (Runs on http://localhost:5000)
   - Frontend: `npm run dev` (Runs on http://localhost:5173)

## Deployment

The application is configured for deployment with standard platform-as-a-service providers. The repository includes `vercel.json` for frontend and serverless backend deployments on Vercel, as well as Firebase configurations (`firebase.json`).
