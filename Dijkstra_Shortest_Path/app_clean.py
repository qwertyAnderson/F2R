"""
Farm-to-Market Route Optimizer - Working Version
Complete routing application with real road geometry and weather integration
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import json
import math
from typing import List, Dict, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Farm Route Optimizer", 
    page_icon="T",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# CONFIGURATION
# ===============================

DEHRADUN_LOCATIONS = {
    "Clock Tower (City Center)": (30.32524771594182, 78.0412247750176),
    "ISBT Dehradun": (30.28949015941415, 77.997370426645),
    "Rajpur Road": (30.324786144964126, 78.04206627289855),
    "Sahastradhara Road": (30.358404480937825, 78.08800831001025),
    "Mussoorie Diversion": (30.371626982890795, 78.0774532247974),
    "Rispana": (30.29575309297316, 78.05628846682623),
    "Clement Town": (30.269080492236917, 78.00702082578448),
    "Patel Nagar": (30.310787064565137, 78.02028477928296),
    "Rajendra Nagar": (30.339703077426826, 78.02318300271952),
    "Ballupur": (30.33375980211612, 78.01142029317087),
    "Raipur": (30.30943210572888, 78.09293890340565),
    "Premnagar": (30.333775888326592, 77.9592646449722),
    "Selaqui": (30.368686788624988, 77.8640125033011),
    "Vikasnagar Road": (30.458511087625936, 77.76576582260995),
    "Doiwala": (30.17628822557042, 78.12184634139498)

}

CROP_TYPES = {
    "Highly Perishable": {"urgency": 1.5, "color": "#FF6B6B"},
    "Moderately Perishable": {"urgency": 1.2, "color": "#4ECDC4"},
    "Low Perishable": {"urgency": 1.0, "color": "#45B7D1"},
    "Non-Perishable": {"urgency": 0.8, "color": "#96CEB4"}
}

# Custom CSS
st.markdown("""
<style>
    .main-header { 
        text-align: center; 
        color: #2E8B57; 
        margin-bottom: 30px;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .route-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #2E8B57;
    }
    .metric-container {
        background: white;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# UTILITY FUNCTIONS
# ===============================

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return 6371 * c  # Earth's radius in kilometers

@st.cache_data(ttl=1800)  # Cache weather for 30 minutes
def get_weather_data(lat, lon):
    """Get weather data from Open-Meteo API"""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,precipitation,rain,wind_speed_10m,weather_code',
            'timezone': 'Asia/Kolkata'
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            current = data.get('current', {})
            return {
                'temperature': current.get('temperature_2m', 22),
                'precipitation': current.get('precipitation', 0),
                'wind_speed': current.get('wind_speed_10m', 5),
                'weather_code': current.get('weather_code', 1)
            }
    except Exception as e:
        st.warning(f"Weather API unavailable: {e}")
    
    # Fallback weather
    return {'temperature': 22, 'precipitation': 0, 'wind_speed': 5, 'weather_code': 1}

def decode_polyline(polyline_str):
    """Decode polyline string to coordinates"""
    try:
        import polyline
        return polyline.decode(polyline_str)
    except ImportError:
        # Manual polyline decoding if library not available
        return decode_polyline_manual(polyline_str)
    except:
        return []

def decode_polyline_manual(polyline_str):
    """Manual polyline decoding implementation"""
    try:
        coords = []
        index = 0
        lat = 0
        lng = 0
        
        while index < len(polyline_str):
            # Decode latitude
            shift = 0
            result = 0
            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if byte < 0x20:
                    break
            lat += ~(result >> 1) if result & 1 else result >> 1
            
            # Decode longitude
            shift = 0
            result = 0
            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if byte < 0x20:
                    break
            lng += ~(result >> 1) if result & 1 else result >> 1
            
            coords.append([lat / 1e5, lng / 1e5])
        
        return coords
    except:
        return []

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_real_road_route(start_coords, end_coords):
    """Get actual road routes using multiple routing services with enhanced validation"""
    
    # Validate coordinates
    if not start_coords or not end_coords:
        st.error("Invalid coordinates provided")
        return create_realistic_road_routes([30.3165, 78.0322], [30.3165, 78.0322])
    
    # Ensure coordinates are within reasonable bounds (Dehradun area)
    lat_min, lat_max = 30.1, 30.5
    lon_min, lon_max = 77.8, 78.3
    
    if not (lat_min <= start_coords[0] <= lat_max and lon_min <= start_coords[1] <= lon_max):
        st.warning("Start coordinates outside Dehradun area, using simulation")
        return create_realistic_road_routes(start_coords, end_coords)
    
    if not (lat_min <= end_coords[0] <= lat_max and lon_min <= end_coords[1] <= lon_max):
        st.warning("End coordinates outside Dehradun area, using simulation")
        return create_realistic_road_routes(start_coords, end_coords)
    
    # Try MapMyIndia API first - best for Indian roads
    try:
        st.info("Fetching real road routes from MapMyIndia...")
        api_key = "070c1c6ab4b3781b9f63b5b1b715d788"
        
        url = f"https://apis.mappls.com/advancedmaps/v1/{api_key}/route_adv/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
        
        params = {
            'alternatives': 'true',
            'geometries': 'polyline',
            'overview': 'full'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'routes' in data and data['routes']:
                routes = []
                for i, route in enumerate(data['routes'][:3]):
                    geometry = route.get('geometry', '')
                    if geometry:
                        coords = decode_polyline(geometry)
                        if coords:
                            routes.append({
                                'name': f'Route {i+1}' + (' (Shortest Real Road)' if i == 0 else ' (Alternative Real Road)'),
                                'coordinates': coords,
                                'distance': route.get('distance', 0) / 1000,
                                'duration': route.get('duration', 0) / 60,
                                'color': ['red', 'blue', 'green'][i],
                                'method': 'MapMyIndia Real Roads'
                            })
                
                if routes:
                    st.success(f"MapMyIndia: Found {len(routes)} real road routes with 35 km/h average speed!")
                    return routes
    
    except Exception as e:
        st.warning(f"MapMyIndia API error: {e}")
    
    # Fallback to OSRM (OpenStreetMap Routing Machine)
    try:
        st.info("Trying OpenStreetMap as backup...")
        
        # OSRM API endpoint  
        url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
        
        params = {
            'alternatives': 'true',
            'geometries': 'polyline',
            'overview': 'full',
            'annotations': 'true'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            routes = []
            
            for i, route in enumerate(data.get('routes', [])[:3]):
                # Get actual road geometry
                geometry = route.get('geometry', '')
                if geometry:
                    coords = decode_polyline(geometry)
                    if coords:
                        routes.append({
                            'name': f'Route {i+1}' + (' (Shortest Real Road)' if i == 0 else ' (Alternative Road)'),
                            'coordinates': coords,
                            'distance': route.get('distance', 0) / 1000,  # Convert to km
                            'duration': route.get('duration', 0) / 60,    # Convert to minutes
                            'color': ['red', 'blue', 'green'][i],
                            'method': 'OpenStreetMap Real Roads'
                        })
            
            if routes:
                st.success(f"OpenStreetMap: Found {len(routes)} real road routes!")
                return routes
    
    except Exception as e:
        st.warning(f"OpenStreetMap routing error: {e}")
    
    # Last resort: create realistic road-based simulation
    st.info("Using enhanced road simulation with 35 km/h average speed")
    return create_realistic_road_routes(start_coords, end_coords)

def create_curved_path(start_coords, end_coords, route_index):
    """Create a realistic road-like path between two points"""
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords
    
    points = []
    num_points = 40  # More points for smoother road-like curves
    
    # Calculate the bearing and distance
    bearing = math.atan2(lon2 - lon1, lat2 - lat1)
    
    for i in range(num_points + 1):
        t = i / num_points
        
        # Create more realistic road curves based on route index
        if route_index == 0:  # Direct route - slight road curves
            # Simulate natural road curves
            curve_lat = 0.001 * math.sin(t * 3 * math.pi) * math.cos(t * math.pi)
            curve_lon = 0.0008 * math.cos(t * 2 * math.pi) * math.sin(t * math.pi)
        elif route_index == 1:  # Alternative route - via different roads
            # Simulate going via intermediate points (like actual roads)
            mid_offset_lat = 0.015 if route_index == 1 else -0.01
            mid_offset_lon = 0.012 if route_index == 1 else -0.008
            
            # Create S-curve to simulate road network
            curve_lat = mid_offset_lat * math.sin(t * math.pi) + 0.002 * math.sin(t * 6 * math.pi)
            curve_lon = mid_offset_lon * math.sin(t * math.pi) + 0.0015 * math.cos(t * 4 * math.pi)
        else:  # Third route - different path
            # Another realistic road path
            curve_lat = -0.01 * math.sin(t * 1.5 * math.pi) + 0.003 * math.cos(t * 5 * math.pi)
            curve_lon = -0.008 * math.cos(t * 1.2 * math.pi) + 0.002 * math.sin(t * 7 * math.pi)
        
        # Apply curves perpendicular to the main direction
        perp_bearing = bearing + math.pi/2
        
        lat = lat1 + (lat2 - lat1) * t + curve_lat * math.cos(perp_bearing) + curve_lon * math.sin(perp_bearing)
        lon = lon1 + (lon2 - lon1) * t + curve_lat * math.sin(perp_bearing) + curve_lon * math.cos(perp_bearing)
        
        points.append([lat, lon])
    
    return points

def create_realistic_road_routes(start_coords, end_coords):
    """Create realistic road-based routes using road network patterns"""
    base_distance = calculate_distance(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
    
    routes = []
    
    # Route 1: Simulate main highway/arterial road
    highway_coords = create_highway_simulation(start_coords, end_coords)
    routes.append({
        'name': 'Main Road (Fastest)',
        'coordinates': highway_coords,
        'distance': base_distance * 1.05,  # Slightly longer but realistic
        'duration': (base_distance * 1.05) * 1.714,  # 35 km/h average
        'color': 'red',
        'method': 'Road Network Simulation'
    })
    
    # Route 2: Simulate local roads
    local_coords = create_local_road_simulation(start_coords, end_coords)
    routes.append({
        'name': 'Local Roads (Alternative)',
        'coordinates': local_coords,
        'distance': base_distance * 1.25,  # Longer local route
        'duration': (base_distance * 1.25) * 1.714,  # 35 km/h average
        'color': 'blue',
        'method': 'Road Network Simulation'
    })
    
    return routes

def create_highway_simulation(start_coords, end_coords):
    """Simulate a main highway route"""
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords
    
    points = []
    num_segments = 20
    
    for i in range(num_segments + 1):
        t = i / num_segments
        
        # Simulate highway with gentle curves and straight segments
        if 0.2 <= t <= 0.8:  # Straight highway segment in middle
            curve_offset_lat = 0.0005 * math.sin(t * 4 * math.pi)
            curve_offset_lon = 0.0003 * math.cos(t * 3 * math.pi)
        else:  # Approach and exit curves
            curve_offset_lat = 0.002 * math.sin(t * 6 * math.pi)
            curve_offset_lon = 0.0015 * math.cos(t * 8 * math.pi)
        
        lat = lat1 + (lat2 - lat1) * t + curve_offset_lat
        lon = lon1 + (lon2 - lon1) * t + curve_offset_lon
        
        points.append([lat, lon])
    
    return points

def create_local_road_simulation(start_coords, end_coords):
    """Simulate local roads with more turns"""
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords
    
    points = []
    num_segments = 30  # More segments for local roads
    
    for i in range(num_segments + 1):
        t = i / num_segments
        
        # Simulate local roads with more frequent turns
        curve_offset_lat = (
            0.003 * math.sin(t * 8 * math.pi) + 
            0.001 * math.cos(t * 12 * math.pi) +
            0.002 * math.sin(t * 4 * math.pi)
        )
        curve_offset_lon = (
            0.0025 * math.cos(t * 6 * math.pi) + 
            0.0008 * math.sin(t * 10 * math.pi) +
            0.0015 * math.cos(t * 3 * math.pi)
        )
        
        lat = lat1 + (lat2 - lat1) * t + curve_offset_lat
        lon = lon1 + (lon2 - lon1) * t + curve_offset_lon
        
        points.append([lat, lon])
    
    return points

def create_fallback_routes(start_coords, end_coords):
    """Legacy fallback function"""
    return create_realistic_road_routes(start_coords, end_coords)

# ===============================
# CHART FUNCTIONS
# ===============================

@st.cache_data
def create_route_comparison_chart(routes):
    """Create matplotlib chart comparing route distances only"""
    if not routes or len(routes) < 2:
        return None
    
    # Set style
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Data preparation
    route_names = [route['name'][:20] + '...' if len(route['name']) > 20 else route['name'] for route in routes]
    distances = [route['distance'] for route in routes]
    colors = [route['color'] for route in routes]
    
    # Distance comparison (horizontal bar chart)
    bars = ax.barh(route_names, distances, color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    ax.set_xlabel('Distance (km)', fontsize=12, fontweight='bold')
    ax.set_title('Route Distance Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    ax.set_xlim(0, max(distances) * 1.1)
    
    # Add value labels on bars
    for i, (bar, distance) in enumerate(zip(bars, distances)):
        ax.text(bar.get_width() + max(distances) * 0.01, bar.get_y() + bar.get_height()/2, 
                f'{distance:.1f} km', va='center', fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    return fig

def create_crop_suitability_chart(crop_type, routes):
    """Create chart showing crop suitability for different routes"""
    if not routes or crop_type not in CROP_TYPES:
        return None
    
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Calculate suitability scores
    crop_info = CROP_TYPES[crop_type]
    urgency_factor = crop_info['urgency']
    
    route_names = []
    suitability_scores = []
    colors = []
    
    for route in routes:
        # Advanced suitability calculation
        base_score = 100
        
        # Time penalty (more urgent crops penalized more for longer routes)
        time_penalty = (route['duration'] - 20) * urgency_factor  # 20 min baseline
        
        # Distance penalty
        distance_penalty = (route['distance'] - 10) * urgency_factor * 0.5  # 10 km baseline
        
        # Calculate final score
        suitability = max(0, min(100, base_score - time_penalty - distance_penalty))
        
        route_names.append(route['name'][:15] + '...' if len(route['name']) > 15 else route['name'])
        suitability_scores.append(suitability)
        colors.append(route['color'])
    
    # Create bar chart
    bars = ax.bar(route_names, suitability_scores, color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    ax.set_ylabel('Suitability Score (0-100)', fontsize=12, fontweight='bold')
    ax.set_title(f'🌾 Route Suitability for {crop_type} Crops', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)
    
    # Add score labels and grade
    for bar, score in zip(bars, suitability_scores):
        # Determine grade
        if score >= 80:
            grade = "A"
            grade_color = "green"
        elif score >= 60:
            grade = "B"
            grade_color = "orange"
        else:
            grade = "C"
            grade_color = "red"
        
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{score:.0f}\n({grade})', ha='center', fontweight='bold', 
                color=grade_color, fontsize=11)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

def create_weather_timeline_chart(weather_data):
    """Create weather timeline visualization"""
    plt.style.use('default')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8))
    
    hours = list(range(24))
    
    # Temperature (sample data - replace with real forecast)
    temps = [20 + 5 * math.sin((h - 6) * math.pi / 12) for h in hours]
    ax1.plot(hours, temps, color='red', linewidth=2, marker='o', markersize=4)
    ax1.set_ylabel('Temperature (°C)', fontweight='bold')
    ax1.set_title('🌡️ 24-Hour Weather Forecast', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 23)
    
    # Precipitation probability
    precip = [max(0, 30 + 20 * math.sin(h * math.pi / 8)) for h in hours]
    ax2.bar(hours, precip, color='blue', alpha=0.6)
    ax2.set_ylabel('Precipitation (%)', fontweight='bold')
    ax2.set_title('🌧️ Precipitation Probability', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(-0.5, 23.5)
    
    # Wind speed
    wind = [5 + 10 * abs(math.sin(h * math.pi / 12)) for h in hours]
    ax3.plot(hours, wind, color='green', linewidth=2, marker='s', markersize=4)
    ax3.set_ylabel('Wind Speed (km/h)', fontweight='bold')
    ax3.set_xlabel('Hour of Day', fontweight='bold')
    ax3.set_title('💨 Wind Speed Forecast', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, 23)
    
    plt.tight_layout()
    return fig

def calculate_weather_safety_score(route, weather_data):
    """Calculate safety score for a route based on weather conditions (0-100)"""
    score = 100.0
    
    # Precipitation penalty (max -40 points)
    if weather_data['precipitation'] > 10:
        score -= 40
    elif weather_data['precipitation'] > 5:
        score -= 25
    elif weather_data['precipitation'] > 2:
        score -= 10
    
    # Wind speed penalty (max -30 points)
    if weather_data['wind_speed'] > 35:
        score -= 30
    elif weather_data['wind_speed'] > 25:
        score -= 20
    elif weather_data['wind_speed'] > 15:
        score -= 10
    
    # Temperature penalty (max -30 points)
    temp = weather_data['temperature']
    if temp < 0 or temp > 40:
        score -= 30
    elif temp < 5 or temp > 35:
        score -= 20
    elif temp < 10 or temp > 30:
        score -= 10
    
    return max(0, score)

def prioritize_routes_by_weather(routes):
    """Reorder routes based on weather safety scores"""
    scored_routes = []
    
    for route in routes:
        # Get weather at start point
        start_lat, start_lon = route['coordinates'][0]
        weather = get_weather_data(start_lat, start_lon)
        
        # Calculate safety score
        safety_score = calculate_weather_safety_score(route, weather)
        
        # Store route with its scores
        route_copy = route.copy()
        route_copy['weather_safety_score'] = safety_score
        route_copy['weather_data'] = weather
        scored_routes.append(route_copy)
    
    # Sort by: 1) Safety score (higher is better), 2) Duration (lower is better)
    scored_routes.sort(key=lambda r: (-r['weather_safety_score'], r['duration']))
    
    return scored_routes

# ===============================
# MAIN APPLICATION
# ===============================

def main():
    # Header
    st.markdown('<h1 class="main-header">Farm-to-Market Route Optimizer</h1>', unsafe_allow_html=True)
    st.markdown("**Advanced route optimization with real-time weather integration and visual analytics**")
    
    # Initialize session state
    if 'routes' not in st.session_state:
        st.session_state.routes = []
    if 'weather_checked' not in st.session_state:
        st.session_state.weather_checked = False
    
    # Sidebar
    st.sidebar.header(" Route Configuration")
    
    # Location selection
    start_location = st.sidebar.selectbox(
        " Start Location (Farm)",
        options=list(DEHRADUN_LOCATIONS.keys()),
        index=0,
        help="Select your farm location"
    )
    
    end_location = st.sidebar.selectbox(
        " End Location (Market)", 
        options=list(DEHRADUN_LOCATIONS.keys()),
        index=4,
        help="Select your target market"
    )
    
    # Crop selection
    crop_type = st.sidebar.selectbox(
        "Crop Type",
        options=list(CROP_TYPES.keys()),
        index=1,
        help="Choose based on perishability"
    )
    
    quantity = st.sidebar.number_input(
        "Quantity (kg)",
        min_value=1,
        max_value=5000,
        value=100,
        step=25,
        help="Enter quantity in kilograms"
    )
    
    # Action buttons
    st.sidebar.markdown("---")
    st.sidebar.markdown("###  Actions")
    
    # Get routes button
    if st.sidebar.button("Get Shortest Path", type="primary", use_container_width=True):
        if start_location != end_location:
            start_coords = DEHRADUN_LOCATIONS[start_location]
            end_coords = DEHRADUN_LOCATIONS[end_location]
            
            with st.spinner(" Finding  road routes..."):
                routes = get_real_road_route(start_coords, end_coords)
                st.session_state.routes = routes
                st.session_state.weather_checked = False
            
            st.sidebar.success(f"Found {len(routes)} route(s)!")
        else:
            st.sidebar.error("Please select different locations!")
    
    # Weather check button
    if st.sidebar.button("🌦️ Reroute Based on Weather", use_container_width=True):
        if st.session_state.routes:
            with st.spinner("🌦️ Analyzing weather conditions and prioritizing routes..."):
                # Get weather for first route to check conditions
                route = st.session_state.routes[0]
                start_weather = get_weather_data(route['coordinates'][0][0], route['coordinates'][0][1])
                
                st.session_state.weather_checked = True
                
                # Weather assessment
                risk_factors = []
                if start_weather['precipitation'] > 5:
                    risk_factors.append("Heavy precipitation")
                if start_weather['wind_speed'] > 25:
                    risk_factors.append("Strong winds")
                if start_weather['temperature'] < 5 or start_weather['temperature'] > 35:
                    risk_factors.append("Extreme temperature")
                
                if risk_factors:
                    # Unfavorable weather - reprioritize routes
                    st.sidebar.warning(f"⚠️ Weather risks detected: {', '.join(risk_factors)}")
                    
                    # Reprioritize routes based on weather safety
                    reprioritized_routes = prioritize_routes_by_weather(st.session_state.routes)
                    
                    # Update routes in session state
                    original_best = st.session_state.routes[0]['name']
                    st.session_state.routes = reprioritized_routes
                    new_best = reprioritized_routes[0]['name']
                    
                    # Display weather safety scores
                    st.sidebar.markdown("### 🛡️ Weather Safety Analysis")
                    for i, r in enumerate(reprioritized_routes[:3]):
                        score = r.get('weather_safety_score', 0)
                        emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                        st.sidebar.markdown(f"{emoji} **{r['name']}**: Safety Score {score:.0f}/100")
                    
                    if original_best != new_best:
                        st.sidebar.success(f" Route reprioritized! New recommendation: {new_best}")
                        st.sidebar.info(" Routes reordered by weather safety. Check the map for the safest route (shown in red).")
                    else:
                        st.sidebar.info(" Current route is still the safest option despite weather risks")
                    
                    st.sidebar.warning(" Consider delaying travel if weather worsens")
                    
                else:
                    # Favorable weather
                    st.sidebar.success(" Weather conditions are favorable for travel!")
                    
                    # Still calculate and show safety scores
                    scored_routes = prioritize_routes_by_weather(st.session_state.routes)
                    st.session_state.routes = scored_routes
                    
                    st.sidebar.markdown("### 🛡️ Weather Safety Scores")
                    for i, r in enumerate(scored_routes[:3]):
                        score = r.get('weather_safety_score', 0)
                        st.sidebar.markdown(f"✅ **{r['name']}**: {score:.0f}/100")
        else:
            st.sidebar.warning("🔍 Please calculate routes first!")
    
    # Main content area
    if st.session_state.routes:
        # Create two columns for layout
        col1, col2 = st.columns([2.5, 1.5])
        
        with col1:
            # Map section
            st.markdown("### Interactive Route Map")
            
            # Create map
            center_coords = st.session_state.routes[0]['coordinates'][len(st.session_state.routes[0]['coordinates'])//2]
            m = folium.Map(location=center_coords, zoom_start=11, tiles='OpenStreetMap')
            
            # Add routes to map
            for i, route in enumerate(st.session_state.routes):
                # Build popup content
                popup_content = f"<b>{route['name']}</b><br>Distance: {route['distance']:.1f} km<br>Duration: {route['duration']:.0f} min"
                
                # Add weather safety info if available
                if 'weather_safety_score' in route:
                    score = route['weather_safety_score']
                    safety_emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                    popup_content += f"<br>{safety_emoji} Weather Safety: {score:.0f}/100"
                
                folium.PolyLine(
                    locations=route['coordinates'],
                    color=route['color'],
                    weight=6 if i == 0 else 4,
                    opacity=0.8,
                    popup=popup_content,
                    tooltip=f"{route['name']}: {route['distance']:.1f} km"
                ).add_to(m)
            
            # Add markers
            folium.Marker(
                st.session_state.routes[0]['coordinates'][0],
                popup=f"<b>{start_location}</b><br>Farm Location",
                tooltip=f"Start: {start_location}",
                icon=folium.Icon(color='green', icon='leaf')
            ).add_to(m)
            
            folium.Marker(
                st.session_state.routes[0]['coordinates'][-1],
                popup=f"<b>{end_location}</b><br>Market Location",
                tooltip=f"End: {end_location}",
                icon=folium.Icon(color='red', icon='shopping-cart')
            ).add_to(m)
            
            # Display map
            map_data = st_folium(m, width=900, height=450)
            
            # Charts section
            st.markdown("### 📊 Route Analytics Dashboard")
            
            # Route comparison chart
            if len(st.session_state.routes) > 1:
                comparison_fig = create_route_comparison_chart(st.session_state.routes)
                if comparison_fig:
                    st.pyplot(comparison_fig, use_container_width=True)
                    plt.close()
            else:
                st.info(" Multiple routes needed for comparison analysis")
        
        with col2:
            # Route details sidebar
            st.markdown("###  Route Details")
            
            # Summary metrics
            best_route = st.session_state.routes[0]
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(
                    label=" Best Distance", 
                    value=f"{best_route['distance']:.1f} km",
                    help="Shortest route distance"
                )
            with col_b:
                st.metric(
                    label="⏱ Best Time", 
                    value=f"{best_route['duration']:.0f} min",
                    help="Fastest route duration"
                )
            
            # Crop information
            st.markdown("###  Cargo Information")
            st.markdown(f"""
            <div class="metric-container">
                <strong>Crop Type:</strong> {crop_type}<br>
                <strong>Quantity:</strong> {quantity} kg
            </div>
            """, unsafe_allow_html=True)
            
            # Individual route details
            st.markdown("###  All Routes")
            
            for i, route in enumerate(st.session_state.routes):
                with st.expander(f" {route['name']}", expanded=(i==0)):
                    
                    # Route metrics
                    col_x, col_y = st.columns(2)
                    with col_x:
                        st.metric("Distance", f"{route['distance']:.1f} km")
                        st.metric("Color", route['color'].title())
                    with col_y:
                        st.metric("Duration", f"{route['duration']:.0f} min")
                        
                        # Calculate efficiency score
                        efficiency = (route['distance'] / route['duration']) * 60  # km/h
                        st.metric("Avg Speed", f"{efficiency:.1f} km/h")
                    
                    # Weather safety if available
                    if 'weather_safety_score' in route:
                        score = route['weather_safety_score']
                        col_w1, col_w2 = st.columns(2)
                        with col_w1:
                            st.metric("🛡️ Weather Safety", f"{score:.0f}/100")
                        with col_w2:
                            if score >= 80:
                                st.success("✅ Very Safe")
                            elif score >= 60:
                                st.warning("⚠️ Caution Advised")
                            else:
                                st.error("❌ High Risk")
                        
            
                    
                    # Route recommendation
                    if i == 0:
                        st.success(" Recommended route")
                    elif route['duration'] < best_route['duration'] * 1.2:
                        st.info(" Good alternative")
                    else:
                        st.warning("⚠️ Consider only if necessary. Might take longer time")
    
    else:
        # Welcome screen
        st.markdown("###  Getting Started")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Default map showing all locations
            st.markdown("####  Dehradun Farm & Market Locations")
            
            default_map = folium.Map(location=[30.3165, 78.0322], zoom_start=10, tiles='OpenStreetMap')
            
            # Add all locations as markers
            for name, coords in DEHRADUN_LOCATIONS.items():
                # Different icons for different location types
                if any(word in name.lower() for word in ['isbt', 'clock', 'market']):
                    icon_color = 'red'
                    icon = 'shopping-cart'
                else:
                    icon_color = 'green'
                    icon = 'leaf'
                
                folium.Marker(
                    coords,
                    popup=f"<b>{name}</b>",
                    tooltip=name,
                    icon=folium.Icon(color=icon_color, icon=icon)
                ).add_to(default_map)
            
            st_folium(default_map, width=700, height=400)
        
        with col2:
            st.markdown("####  Quick Start Guide")
            st.markdown("""
            **Step 1:**  Select your **farm location**
            
            **Step 2:**  Choose your **target market**
            
            **Step 3:**  Pick your **crop type** based on perishability
            
            **Step 4:**  Enter **quantity** in kilograms
            
            **Step 5:**  Click **"Get Shortest Path"**
            
            **Step 6:**  Check **weather conditions** for safety
            """)

if __name__ == "__main__":
    main()