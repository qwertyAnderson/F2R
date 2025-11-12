"""
Configuration file for Farm-to-Market Route Optimizer
Contains all settings, locations, and constants
"""

# Dehradun Locations (Farms and Markets)
DEHRADUN_LOCATIONS = {
    # Major Markets
    "Clock Tower (City Center)": (30.3165, 78.0322),
    "Rispana Market": (30.2833, 78.0167),
    "ISBT Dehradun": (30.3255, 78.0436),
    "Rajpur Road Market": (30.3459, 78.0561),
    
    # Farm Areas
    "Mussoorie Diversion": (30.4501, 78.0644),  # Fixed coordinates
    "Sahastradhara Road": (30.3255, 78.0644),
    "Clement Town": (30.2667, 78.0167),
    "Patel Nagar": (30.3344, 78.0403),
    "Rajendra Nagar": (30.3031, 78.0417),
    "Ballupur": (30.3511, 78.0736),
    "Raipur": (30.2833, 78.0500),
    "Premnagar": (30.3833, 78.1000),
    "Selaqui": (30.3667, 77.8833),
    "Vikasnagar Road": (30.4667, 77.7667),
    "Doiwala": (30.1833, 78.1167)
}

# Crop Types for Route Optimization
CROP_TYPES = {
    "Highly Perishable": {
        "examples": ["Leafy Greens", "Strawberries", "Mushrooms"],
        "time_factor": 1.5,  # Need faster routes
        "description": "Requires quickest delivery"
    },
    "Moderately Perishable": {
        "examples": ["Tomatoes", "Apples", "Potatoes"],
        "time_factor": 1.0,  # Standard routes
        "description": "Standard delivery time"
    },
    "Non-Perishable": {
        "examples": ["Grains", "Pulses", "Dried Fruits"],
        "time_factor": 0.8,  # Can take longer, cheaper routes
        "description": "Cost-optimized routes preferred"
    }
}

# API Configuration
API_CONFIG = {
    "mappls_base_url": "https://apis.mappls.com/advancedmaps/v1",
    "weather_base_url": "https://api.open-meteo.com/v1/forecast",
    "max_routes": 3,  # Maximum alternative routes to show
    "default_radius": 50  # Search radius in km
}

# Map Display Settings
MAP_CONFIG = {
    "center_lat": 30.3165,  # Dehradun center
    "center_lon": 78.0322,
    "default_zoom": 11,
    "route_colors": ["red", "blue", "green"],  # Order: shortest, alt1, alt2
    "route_weights": [4, 3, 3]  # Line thickness
}

# Chart Settings for Matplotlib
CHART_CONFIG = {
    "figure_size": (12, 5),
    "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"],  # Red, Teal, Blue
    "font_size": 10,
    "title_size": 12
}