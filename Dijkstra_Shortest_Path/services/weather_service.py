"""
Weather Service - Checks weather conditions along route
Uses Open-Meteo (free, no API key required)
"""

import requests
from typing import Tuple, Dict, Optional
from datetime import datetime


class WeatherService:
    """Service for weather-based route decisions"""
    
    def __init__(self):
        # Open-Meteo is completely free, no API key needed
        self.base_url = "https://api.open-meteo.com/v1/forecast"
    
    def check_weather(self, lat: float, lon: float) -> Dict:
        """
        Check current weather at a location
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Weather data dictionary
        """
        try:
            params = {
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,precipitation,rain,weathercode,windspeed_10m',
                'timezone': 'Asia/Kolkata'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current']
                
                return {
                    'temperature': current.get('temperature_2m', 0),
                    'precipitation': current.get('precipitation', 0),
                    'rain': current.get('rain', 0),
                    'weather_code': current.get('weathercode', 0),
                    'wind_speed': current.get('windspeed_10m', 0),
                    'is_risky': self._is_weather_risky(current)
                }
            else:
                return self._default_weather()
                
        except Exception:
            return self._default_weather()
    
    def _is_weather_risky(self, weather_data: Dict) -> bool:
        """
        Determine if weather is risky for transport
        
        Weather codes (WMO):
        - 0: Clear
        - 1-3: Partly cloudy
        - 45-48: Fog
        - 51-67: Rain/Drizzle
        - 71-86: Snow
        - 95-99: Thunderstorm
        """
        code = weather_data.get('weathercode', 0)
        precipitation = weather_data.get('precipitation', 0)
        rain = weather_data.get('rain', 0)
        wind_speed = weather_data.get('windspeed_10m', 0)
        
        # Risky conditions
        if code >= 45 and code <= 48:  # Fog
            return True
        if code >= 51 and code <= 67:  # Rain
            return True
        if code >= 71 and code <= 86:  # Snow
            return True
        if code >= 95:  # Thunderstorm
            return True
        if precipitation > 5:  # Heavy precipitation
            return True
        if rain > 5:  # Heavy rain
            return True
        if wind_speed > 40:  # Strong winds
            return True
        
        return False
    
    def _default_weather(self) -> Dict:
        """Return default safe weather when API fails"""
        return {
            'temperature': 25,
            'precipitation': 0,
            'rain': 0,
            'weather_code': 0,
            'wind_speed': 10,
            'is_risky': False
        }
    
    def get_weather_description(self, weather_code: int) -> str:
        """Get human-readable weather description"""
        codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Dense fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
            99: "Heavy thunderstorm"
        }
        return codes.get(weather_code, "Unknown")
    
    def evaluate_route_weather(self, start_coords: Tuple[float, float], 
                              end_coords: Tuple[float, float]) -> Dict:
        """
        Evaluate weather along route (check start, end, and midpoint)
        
        Returns:
            Dictionary with weather assessment
        """
        # Check weather at key points
        start_weather = self.check_weather(start_coords[0], start_coords[1])
        end_weather = self.check_weather(end_coords[0], end_coords[1])
        
        # Check midpoint
        mid_lat = (start_coords[0] + end_coords[0]) / 2
        mid_lon = (start_coords[1] + end_coords[1]) / 2
        mid_weather = self.check_weather(mid_lat, mid_lon)
        
        # Determine if any point has risky weather
        is_risky = any([
            start_weather['is_risky'],
            end_weather['is_risky'],
            mid_weather['is_risky']
        ])
        
        # Find worst condition
        worst_weather = start_weather
        if end_weather['is_risky']:
            worst_weather = end_weather
        if mid_weather['is_risky']:
            worst_weather = mid_weather
        
        return {
            'is_risky': is_risky,
            'start_weather': start_weather,
            'end_weather': end_weather,
            'mid_weather': mid_weather,
            'worst_condition': worst_weather,
            'recommendation': self._get_recommendation(is_risky, worst_weather)
        }
    
    def _get_recommendation(self, is_risky: bool, weather: Dict) -> str:
        """Get recommendation based on weather"""
        if not is_risky:
            return "Current route is optimal based on weather conditions."
        
        code = weather['weather_code']
        desc = self.get_weather_description(code)
        
        return f"Weather Alert: {desc} detected. Alternative route recommended for safety."
