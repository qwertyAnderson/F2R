# 🚜 Farm-to-Market Route Optimizer

Real-time route optimization for farmers with weather-aware rerouting and Dijkstra's algorithm.

## ✨ Features

- **Real-Time Map Interface**: Interactive map for selecting start and end locations
- **Dijkstra's Algorithm**: Optimal shortest path calculation
- **Weather-Aware Rerouting**: Automatic route adjustment based on current weather
- **Crop-Specific Optimization**: Route planning based on crop perishability and quantity
- **Clean Farmer-Friendly UI**: Minimal, mobile-friendly interface

## 📁 Project Structure

```
Dijkstra_Shortest_Path/
├── app_new.py                 # Main Streamlit application
├── services/
│   ├── __init__.py
│   ├── map_service.py         # Map API integration (OpenRouteService)
│   ├── weather_service.py     # Weather API integration (Open-Meteo)
│   └── route_service.py       # Dijkstra's algorithm implementation
├── components/
│   ├── __init__.py
│   └── map_picker.py          # Interactive map component
├── .streamlit/
│   └── secrets.toml           # API keys configuration
└── requirements_new.txt       # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Install dependencies**:
   ```powershell
   pip install -r requirements_new.txt
   ```

2. **Configure API Keys** (Optional):
   
   The app uses:
   - **OpenRouteService** for routing (free tier included)
   - **Open-Meteo** for weather (no key required)
   
   If you want to use your own OpenRouteService key:
   - Sign up at: https://openrouteservice.org/dev/#/signup
   - Edit `.streamlit/secrets.toml` and add your key

### Running the Application

```powershell
streamlit run app_new.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 How to Use

1. **Select Start Location**: Click on the map to set your farm location
2. **Select End Location**: Click again to set the market location
3. **Choose Crop Type**: Select from dropdown:
   - Highly Perishable
   - Moderately Perishable
   - Non-Perishable
   - Fragile
   - Bulk / Heavy
4. **Enter Quantity**: Input produce quantity in kg
5. **Calculate Route**: Click "Calculate Optimal Route" button
6. **Weather Check** (Optional): Click "Reroute Based on Weather" to get weather-safe alternative

## 🔧 API Services Used

### OpenRouteService (Free Tier)
- **Usage**: Road routing and directions
- **Rate Limit**: 2000 requests/day
- **No credit card required**
- **Fallback**: Direct line calculation if API fails

### Open-Meteo (Completely Free)
- **Usage**: Real-time weather data
- **Rate Limit**: Unlimited for non-commercial use
- **No API key required**
- **Coverage**: Global

## 🎨 UI Components

The final screen shows ONLY:

- ✅ Clean real-time interactive map
- ✅ Shortest path highlighted in green (Dijkstra's algorithm)
- ✅ Start marker (green) and end marker (red)
- ✅ Floating summary box with crop type, quantity, distance, and ETA
- ✅ Weather-safe alternative route (red) when weather is risky
- ✅ No debug info, no CSV uploads, no validation messages

## 🧪 Testing

To test the application:

1. Start the app
2. Click near Delhi for start location (28.6139, 77.2090)
3. Click near Jaipur for end location (26.9124, 75.7873)
4. Select "Highly Perishable"
5. Enter 500 kg
6. Calculate route
7. Test weather rerouting

## 🔐 Security Notes

- Never commit actual API keys to version control
- Use `.streamlit/secrets.toml` for sensitive data (gitignored by default)
- For production, use environment variables

## 📦 Dependencies

- **streamlit**: Web app framework
- **networkx**: Graph algorithms (Dijkstra)
- **folium**: Map visualization
- **streamlit-folium**: Streamlit-Folium integration
- **requests**: HTTP client for APIs
- **pandas/numpy**: Data processing

## 🐛 Troubleshooting

**Map not loading?**
- Check internet connection
- Verify API key in `.streamlit/secrets.toml`

**Route calculation failing?**
- App will fallback to direct line calculation
- Check coordinates are valid (lat: -90 to 90, lon: -180 to 180)

**Weather data not showing?**
- Open-Meteo is free and doesn't require authentication
- Check internet connection

## 📝 License

This project is for educational and non-commercial use.

## 🤝 Contributing

This is a demonstration project. Feel free to fork and customize for your needs.

## 📞 Support

For issues or questions, please check:
- OpenRouteService docs: https://openrouteservice.org/dev/#/api-docs
- Open-Meteo docs: https://open-meteo.com/en/docs
- Streamlit docs: https://docs.streamlit.io

---

**Built with ❤️ for farmers using Python, Streamlit, and open-source APIs**
