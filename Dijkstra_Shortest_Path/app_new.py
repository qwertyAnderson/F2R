"""
Farm-to-Market Route Optimizer
Real-time route optimization with weather-aware rerouting
Multi-route support with visual color differentiation
"""

import streamlit as st
from streamlit_folium import st_folium
import folium
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from services.map_service import MapService
from services.weather_service import WeatherService
from services.route_service import RouteService
from components.map_picker import MapPicker
from typing import Optional, Tuple
import time


# Page configuration
st.set_page_config(
    page_title="Farm-to-Market Route Optimizer",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for minimal, clean UI
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Clean header */
    .main-header {
        font-size: 2rem;
        color: #1a5f1a;
        text-align: center;
        padding: 1rem 0;
        font-weight: 600;
    }
    
    /* Summary box */
    .summary-box {
        position: fixed;
        top: 80px;
        right: 20px;
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        min-width: 220px;
        border-left: 4px solid #1a5f1a;
    }
    
    .summary-title {
        font-weight: 600;
        color: #1a5f1a;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    .summary-item {
        margin: 0.5rem 0;
        font-size: 0.95rem;
        color: #333;
    }
    
    .summary-label {
        font-weight: 500;
        color: #666;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background-color: #1a5f1a;
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1rem;
        font-weight: 500;
        border-radius: 8px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #145014;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Input fields */
    .stSelectbox, .stNumberInput {
        margin-bottom: 1rem;
    }
    
    /* Toast messages */
    .toast-success {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .toast-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    
    /* Map container */
    .map-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Instructions */
    .instructions {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #495057;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def get_services():
    return {
        'map': MapService(),
        'weather': WeatherService(),
        'route': RouteService()
    }

services = get_services()

# Initialize session state
if 'start_location' not in st.session_state:
    st.session_state.start_location = None
if 'end_location' not in st.session_state:
    st.session_state.end_location = None
if 'route_calculated' not in st.session_state:
    st.session_state.route_calculated = False
if 'current_route' not in st.session_state:
    st.session_state.current_route = None
if 'all_routes' not in st.session_state:
    st.session_state.all_routes = []
if 'selected_route_idx' not in st.session_state:
    st.session_state.selected_route_idx = 0
if 'alternative_route' not in st.session_state:
    st.session_state.alternative_route = None
if 'weather_checked' not in st.session_state:
    st.session_state.weather_checked = False
if 'crop_type' not in st.session_state:
    st.session_state.crop_type = "Moderately Perishable"
if 'quantity' not in st.session_state:
    st.session_state.quantity = 100.0

# Predefined Dehradun locations
dehradun_locations = {
    "Clock Tower (City Center)": (30.324323, 78.041863),
    "Rajpur Road": (30.384070, 78.090270),
    "Sahastradhara Road": (30.342614, 78.072927),
    "ISBT Dehradun": (30.287929, 77.998488),
    "Mussoorie Diversion": (30.459909, 78.066399),
    "Rispana": (30.294711, 78.057143),
    "Clement Town": (30.254394, 78.057341),
    "Patel Nagar": (30.337707, 78.052461),
    "Rajendra Nagar": (30.292117, 77.997876),
    "Ballupur": (30.368175, 78.072166),
    "Raipur": (30.316700, 78.099998),
    "Premnagar": (30.333092, 77.961016),
    "Selaqui": (30.368159, 77.865313),
    "Vikasnagar Road": (30.475025, 77.765235),
    "Doiwala": (30.176670, 78.116590)
}

def main():
    # Header
    st.markdown('<h1 class="main-header">🚜 Farm-to-Market Route Optimizer - Dehradun</h1>', unsafe_allow_html=True)
    
    # Layout
    col_main, col_inputs = st.columns([3, 1])
    
    with col_inputs:
        st.markdown("### 📍 Route Details")
        
        # Instructions
        st.markdown("""
        <div class="instructions">
        <strong>How to use:</strong><br>
        1. Select Start location<br>
        2. Select End location<br>
        3. Choose crop type<br>
        4. Calculate route
        </div>
        """, unsafe_allow_html=True)
        
        # Location search options for Dehradun
        st.markdown("### 📍 Select Locations")
        
        # Start location search
        start_search = st.selectbox(
            "🟢 Start Location (Farm)",
            ["Select from map..."] + list(dehradun_locations.keys()),
            key="start_search"
        )
        
        if start_search != "Select from map..." and start_search:
            st.session_state.start_location = dehradun_locations[start_search]
            st.success(f"✓ Start: {start_search}")
        
        # End location search
        end_search = st.selectbox(
            "🔴 End Location (Market)",
            ["Select from map..."] + list(dehradun_locations.keys()),
            key="end_search"
        )
        
        if end_search != "Select from map..." and end_search:
            st.session_state.end_location = dehradun_locations[end_search]
            st.success(f"✓ End: {end_search}")
        
        st.markdown("---")
        
        # Crop type selection
        crop_type = st.selectbox(
            "Crop Type",
            ["Highly Perishable", "Moderately Perishable", "Non-Perishable", "Fragile", "Bulk / Heavy"],
            index=1,
            key="crop_type_select"
        )
        st.session_state.crop_type = crop_type
        
        # Quantity input
        quantity = st.number_input(
            "Produce Quantity (kg)",
            min_value=1.0,
            max_value=10000.0,
            value=100.0,
            step=10.0,
            key="quantity_input"
        )
        st.session_state.quantity = quantity
        
        st.markdown("---")
        
        # Show current selections
        if st.session_state.start_location:
            st.success("✓ Start location set")
        else:
            st.info("👆 Select start location")
        
        if st.session_state.end_location:
            st.success("✓ End location set")
        else:
            st.info("👆 Select end location")
        
        # Calculate route button
        st.markdown("---")
        can_calculate = st.session_state.start_location and st.session_state.end_location
        
        if st.button("🚀 Calculate Optimal Route", disabled=not can_calculate):
            calculate_route()
        
        # Weather reroute button (only show after route is calculated)
        if st.session_state.route_calculated:
            st.markdown("---")
            if st.button("⛈️ Reroute Based on Weather"):
                check_weather_and_reroute()
        
        # Reset button
        if st.session_state.start_location or st.session_state.end_location:
            st.markdown("---")
            if st.button("🔄 Reset"):
                reset_all()
    
    with col_main:
        # Render map
        render_map()
        
        # Show route selection if multiple routes available
        if st.session_state.route_calculated and len(st.session_state.all_routes) > 1:
            display_route_options()
        elif st.session_state.route_calculated and len(st.session_state.all_routes) == 1:
            # Show single route details
            display_single_route_details()
        
        # Show summary box if route calculated
        if st.session_state.route_calculated and st.session_state.current_route:
            display_summary_box()


def render_map():
    """Render the interactive map"""
    
    # Add container for map visibility
    st.markdown("### 🗺️ Route Map")
    
    # Determine map center and zoom
    if st.session_state.start_location and st.session_state.end_location:
        # Center between start and end
        center_lat = (st.session_state.start_location[0] + st.session_state.end_location[0]) / 2
        center_lon = (st.session_state.start_location[1] + st.session_state.end_location[1]) / 2
        center = (center_lat, center_lon)
        zoom = 12
    elif st.session_state.start_location:
        center = st.session_state.start_location
        zoom = 13
    else:
        # Default: Dehradun, Uttarakhand
        center = (30.3165, 78.0322)
        zoom = 12
    
    # Create base map
    map_obj = services['map'].create_base_map(center=center, zoom=zoom)
    
    # Show map status
    if st.session_state.route_calculated:
        st.success(f"✅ Route displayed on map below - Distance: {st.session_state.current_route.get('distance', 0):.1f} km")
    else:
        st.info("👆 Select start and end locations from the right panel, then click Calculate")
    
    # Add markers
    map_obj = services['map'].add_markers(
        map_obj,
        st.session_state.start_location,
        st.session_state.end_location
    )
    
    # Add route if calculated
    if st.session_state.route_calculated and st.session_state.current_route:
        # Display all available routes
        if st.session_state.all_routes and len(st.session_state.all_routes) > 0:
            st.sidebar.success(f"🗺️ {len(st.session_state.all_routes)} Route(s) Found!")
            
            # Draw all routes with VERY distinct colors and visual separation
            # Use highly contrasting colors and add spatial offset for visibility
            colors = ['#FF0000', '#0000FF', '#00AA00']  # Bright Red, Blue, Green
            
            for idx, route in enumerate(st.session_state.all_routes):
                route_coords = route['coordinates']
                is_selected = (idx == st.session_state.selected_route_idx)
                is_shortest = (idx == 0)  # First route is always shortest
                
                # For better visibility when routes overlap, apply slight visual offset
                # This makes multiple routes visible even when they follow the same roads
                if idx > 0 and len(st.session_state.all_routes) > 1:
                    # Add tiny offset to alternative routes for visual separation
                    offset = 0.0002 * idx  # Very small offset
                    route_coords = [(lat + offset, lon + offset) for lat, lon in route_coords]
                
                # Differentiate routes clearly
                if is_shortest and is_selected:
                    # Shortest and selected - MAXIMUM prominence
                    map_obj = services['map'].add_route_to_map(
                        map_obj,
                        route_coords,
                        color=colors[idx % len(colors)],
                        label=f"{route.get('route_name', f'Route {idx+1}')} ⭐ - {route['distance']:.1f}km",
                        weight=14,  # Very thick
                        opacity=1.0  # Full opacity
                    )
                elif is_shortest:
                    # Shortest but not selected - still very prominent
                    map_obj = services['map'].add_route_to_map(
                        map_obj,
                        route_coords,
                        color=colors[idx % len(colors)],
                        label=f"{route.get('route_name', f'Route {idx+1}')} - {route['distance']:.1f}km",
                        weight=12,
                        opacity=0.8
                    )
                elif is_selected:
                    # Alternative but selected - thick and visible
                    map_obj = services['map'].add_route_to_map(
                        map_obj,
                        route_coords,
                        color=colors[idx % len(colors)],
                        label=f"{route.get('route_name', f'Route {idx+1}')} - {route['distance']:.1f}km",
                        weight=14,
                        opacity=1.0
                    )
                else:
                    # Alternative and not selected - still clearly visible with offset
                    map_obj = services['map'].add_route_to_map(
                        map_obj,
                        route_coords,
                        color=colors[idx % len(colors)],
                        label=f"{route.get('route_name', f'Route {idx+1}')} - {route['distance']:.1f}km",
                        weight=8,
                        opacity=0.7
                    )
            
            # Add bounds to ensure all routes are visible
            all_coords = []
            for route in st.session_state.all_routes:
                all_coords.extend(route['coordinates'])
            if len(all_coords) > 0:
                map_obj.fit_bounds(all_coords)
            
            # Add legend to map
            if len(st.session_state.all_routes) > 1:
                legend_html = '''
                <div style="position: fixed; 
                     top: 10px; left: 10px; width: 200px; height: auto; 
                     background-color: white; z-index:9999; font-size:14px;
                     border:2px solid grey; border-radius: 5px; padding: 10px">
                     <p style="margin:0; font-weight: bold;">Route Legend:</p>
                '''
                route_colors = ['🔴 Red', '🔵 Blue', '🟢 Green']
                for idx, route in enumerate(st.session_state.all_routes[:3]):
                    route_name = route.get('route_name', f'Route {idx+1}')
                    distance = route['distance']
                    is_shortest = ' ⭐' if idx == 0 else ''
                    legend_html += f'<p style="margin:2px 0;">{route_colors[idx]}: {route_name}{is_shortest}<br><small>{distance:.1f} km</small></p>'
                legend_html += '</div>'
                map_obj.get_root().html.add_child(folium.Element(legend_html))
        else:
            route_coords = st.session_state.current_route['coordinates']
            
            # Debug info
            st.sidebar.success(f"🗺️ Route Display Active!")
            st.sidebar.info(f"📍 Route has {len(route_coords)} points")
            st.sidebar.info(f"📏 Distance: {st.session_state.current_route.get('distance', 0):.1f} km")
            
            # Add the route with bright, visible color
            map_obj = services['map'].add_route_to_map(
                map_obj,
                route_coords,
                color='#FF0000',  # Bright red for visibility
                label='Optimal Route',
                weight=6,
                opacity=0.9
            )
            
            # Add bounds to ensure route is visible
            if len(route_coords) > 0:
                map_obj.fit_bounds(route_coords)
    
    # Add alternative route if weather-based rerouting was done
    if st.session_state.alternative_route:
        alt_coords = st.session_state.alternative_route['coordinates']
        map_obj = services['map'].add_route_to_map(
            map_obj,
            alt_coords,
            color='#ff6b6b',
            label='Weather-Safe Alternative'
        )
    
    # Render map using components.html for better reliability
    import streamlit.components.v1 as components
    import tempfile
    import os
    
    # Save map to temp HTML file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        map_obj.save(f.name)
        temp_file = f.name
    
    # Read HTML content
    with open(temp_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Clean up temp file
    try:
        os.unlink(temp_file)
    except:
        pass
    
    # Render using components.html (more reliable than st_folium for complex maps)
    components.html(html_content, height=700, scrolling=False)
    
    # Note: Using dropdown selection instead of map clicks since components.html doesn't support click events


def calculate_route():
    """Calculate optimal route and find alternatives using route service"""
    
    with st.spinner("🔍 Finding all available routes..."):
        try:
            # Get multiple alternative routes from map service
            all_routes = services['map'].get_multiple_routes(
                st.session_state.start_location,
                st.session_state.end_location
            )
            
            if all_routes and len(all_routes) > 0:
                # Store all routes
                st.session_state.all_routes = all_routes
                st.session_state.current_route = all_routes[0]  # Shortest route by default
                st.session_state.selected_route_idx = 0
                st.session_state.route_calculated = True
                st.session_state.weather_checked = False
                st.session_state.alternative_route = None
                
                # Increment map counter to force re-render
                if 'map_counter' not in st.session_state:
                    st.session_state.map_counter = 0
                st.session_state.map_counter += 1
                
                # Show success message
                method = all_routes[0].get('method', 'unknown')
                if method == 'fallback':
                    st.sidebar.info(f"📍 Found {len(all_routes)} route(s)")
                    st.sidebar.info(f"⭐ Shortest: {all_routes[0]['distance']:.1f} km")
                elif method == 'alternative':
                    st.sidebar.success(f"✅ {len(all_routes)} route(s) available")
                    st.sidebar.info(f"⭐ Shortest: {all_routes[0]['distance']:.1f} km")
                elif method == 'MapMyIndia':
                    st.sidebar.success(f"✅ {len(all_routes)} route(s) via MapMyIndia")
                    st.sidebar.info("🇮🇳 Using accurate India road data")
                    st.sidebar.info(f"⭐ Shortest: {all_routes[0]['distance']:.1f} km")
                elif method == 'OpenRouteService':
                    st.sidebar.success(f"✅ {len(all_routes)} route(s) via OpenRouteService")
                    st.sidebar.info("🌍 Using global road data")
                    st.sidebar.info(f"⭐ Shortest: {all_routes[0]['distance']:.1f} km")
                else:
                    st.sidebar.success(f"✅ Found {len(all_routes)} route(s)")
                    st.sidebar.info(f"⭐ Shortest: {all_routes[0]['distance']:.1f} km")
                
                # Force rerun to update map
                st.rerun()
            else:
                st.error("❌ Could not calculate route. Please try different locations.")
        except Exception as e:
            st.error(f"❌ Error calculating route: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def check_weather_and_reroute():
    """Check weather and suggest reroute if needed"""
    
    with st.spinner("Checking weather conditions..."):
        # Evaluate weather along current route
        weather_eval = services['weather'].evaluate_route_weather(
            st.session_state.start_location,
            st.session_state.end_location
        )
        
        st.session_state.weather_checked = True
        
        if weather_eval['is_risky']:
            # Get alternative route
            alt_route = services['map'].get_alternative_route(
                st.session_state.start_location,
                st.session_state.end_location
            )
            
            if alt_route:
                st.session_state.alternative_route = alt_route
                
                # Show warning
                st.markdown(f"""
                <div class="toast-warning">
                    <strong>⚠️ Weather Alert</strong><br>
                    {weather_eval['recommendation']}<br>
                    Alternative route shown in red.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="toast-warning">
                    <strong>⚠️ Weather Alert</strong><br>
                    Unfavorable weather detected. No alternative route available. 
                    Consider delaying travel or proceeding with caution.
                </div>
                """, unsafe_allow_html=True)
        else:
            # Weather is good
            st.markdown("""
            <div class="toast-success">
                <strong>✅ Weather Clear</strong><br>
                Current route is optimal based on weather conditions.
            </div>
            """, unsafe_allow_html=True)
        
        time.sleep(2)
        st.rerun()


def display_single_route_details():
    """Display details when only one route is available"""
    
    st.markdown("---")
    st.markdown("### 📍 Route Information")
    
    route = st.session_state.all_routes[0]
    
    st.info("ℹ️ **Showing the optimal route.** Alternative routes are not available from the routing API for this route.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Distance", f"{route['distance']:.2f} km")
    
    with col2:
        duration = route['duration']
        eta_h = int(duration // 60)
        eta_m = int(duration % 60)
        st.metric("Duration", f"{eta_h}h {eta_m}m")
    
    with col3:
        method = route.get('method', 'Unknown')
        st.metric("Data Source", method)
    
    # Show path waypoints
    coords = route['coordinates']
    st.markdown(f"**Route waypoints:** {len(coords)} coordinate points")
    
    with st.expander("View Path Coordinates"):
        st.markdown("**Starting waypoints:**")
        for i in range(min(10, len(coords))):
            st.text(f"{i+1}. Lat: {coords[i][0]:.6f}, Lon: {coords[i][1]:.6f}")
        
        if len(coords) > 20:
            st.markdown(f"... ({len(coords) - 20} intermediate waypoints)")
        
        if len(coords) > 10:
            st.markdown("**Ending waypoints:**")
            start_idx = max(10, len(coords) - 10)
            for i in range(start_idx, len(coords)):
                st.text(f"{i+1}. Lat: {coords[i][0]:.6f}, Lon: {coords[i][1]:.6f}")


def create_route_comparison_chart(routes):
    """Create matplotlib chart comparing route distances and times"""
    if len(routes) < 2:
        return None
    
    # Set matplotlib style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Prepare data
    route_names = [f"Route {i+1}" for i in range(len(routes))]
    distances = [route.get('distance', 0) for route in routes]
    durations = [route.get('duration', 0) for route in routes]
    colors = ['#FF4B4B', '#1f77b4', '#2ca02c', '#ff7f0e'][:len(routes)]
    
    # Create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('📊 Route Comparison Analysis', fontsize=16, fontweight='bold')
    
    # Distance comparison (left chart)
    bars1 = ax1.bar(route_names, distances, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax1.set_title('🛣️ Distance Comparison', fontsize=14, pad=20)
    ax1.set_ylabel('Distance (km)', fontsize=12)
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim(0, max(distances) * 1.1)
    
    # Add value labels on bars
    for bar, distance in zip(bars1, distances):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(distances)*0.01,
                f'{distance:.1f} km', ha='center', va='bottom', fontweight='bold')
    
    # Duration comparison (right chart)
    bars2 = ax2.bar(route_names, durations, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax2.set_title('⏱️ Time Comparison', fontsize=14, pad=20)
    ax2.set_ylabel('Duration (minutes)', fontsize=12)
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_ylim(0, max(durations) * 1.1)
    
    # Add value labels on bars
    for bar, duration in zip(bars2, durations):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + max(durations)*0.01,
                f'{duration:.0f} min', ha='center', va='bottom', fontweight='bold')
    
    # Highlight shortest route
    shortest_idx = distances.index(min(distances))
    bars1[shortest_idx].set_edgecolor('gold')
    bars1[shortest_idx].set_linewidth(3)
    bars2[shortest_idx].set_edgecolor('gold')
    bars2[shortest_idx].set_linewidth(3)
    
    plt.tight_layout()
    return fig


def create_route_efficiency_chart(routes):
    """Create efficiency analysis chart"""
    if len(routes) < 2:
        return None
    
    # Calculate efficiency metrics
    distances = [route.get('distance', 0) for route in routes]
    durations = [route.get('duration', 0) for route in routes]
    
    # Speed calculation (km/h)
    speeds = [d / (t/60) if t > 0 else 0 for d, t in zip(distances, durations)]
    route_names = [f"Route {i+1}" for i in range(len(routes))]
    colors = ['#FF4B4B', '#1f77b4', '#2ca02c', '#ff7f0e'][:len(routes)]
    
    # Create efficiency radar chart
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Normalize metrics for comparison (0-100 scale)
    max_distance = max(distances)
    max_duration = max(durations)
    max_speed = max(speeds)
    
    distance_scores = [100 - (d/max_distance)*100 for d in distances]  # Lower distance = higher score
    time_scores = [100 - (t/max_duration)*100 for t in durations]    # Lower time = higher score
    speed_scores = [(s/max_speed)*100 for s in speeds]              # Higher speed = higher score
    
    x = np.arange(len(route_names))
    width = 0.25
    
    bars1 = ax.bar(x - width, distance_scores, width, label='Distance Efficiency', color=colors[0], alpha=0.8)
    bars2 = ax.bar(x, time_scores, width, label='Time Efficiency', color=colors[1], alpha=0.8)
    bars3 = ax.bar(x + width, speed_scores, width, label='Speed Efficiency', color=colors[2], alpha=0.8)
    
    ax.set_xlabel('Routes', fontsize=12)
    ax.set_ylabel('Efficiency Score (0-100)', fontsize=12)
    ax.set_title('🎯 Route Efficiency Analysis', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(route_names)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 105)
    
    plt.tight_layout()
    return fig


def display_route_options():
    """Display clickable alternative routes below the map"""
    
    st.markdown("---")
    st.markdown("### 🛣️ Available Routes")
    
    # Info about routes and how they're displayed
    if st.session_state.all_routes:
        if len(st.session_state.all_routes) > 1:
            st.info("ℹ️ **Multiple routes found!** Routes are color-coded: 🔴 Red (shortest), 🔵 Blue, � Green. "
                   "Each route is slightly offset on the map for better visibility when they share roads.")
    
    # Create columns for route options (max 3 routes to keep it practical)
    num_routes = min(len(st.session_state.all_routes), 3)
    cols = st.columns(num_routes)
    
    for idx in range(num_routes):
        route = st.session_state.all_routes[idx]
        with cols[idx]:
            # Route card
            is_selected = (idx == st.session_state.selected_route_idx)
            is_shortest = (idx == 0)
            
            # Color indicator - matching map colors
            colors = ['🔴', '🔵', '🟢']  # Red, Blue, Green
            color_indicator = colors[idx]
            
            # Route details
            route_name = route.get('route_name', f'Route {idx+1}')
            distance = route.get('distance', 0)
            duration = route.get('duration', 0)
            
            # Calculate ETA
            eta_hours = int(duration // 60)
            eta_mins = int(duration % 60)
            
            # Add badge for shortest
            if is_shortest:
                route_label = f"⭐ {route_name}\n(SHORTEST)"
            else:
                route_label = route_name
            
            # Create button with route info
            button_label = f"{color_indicator} {route_label}\n{distance:.1f} km • {eta_hours}h {eta_mins}m"
            
            if is_selected:
                if is_shortest:
                    st.success(f"**✓ ACTIVE**\n\n{button_label}")
                else:
                    st.info(f"**✓ SELECTED**\n\n{button_label}")
            else:
                if st.button(button_label, key=f"route_btn_{idx}", use_container_width=True):
                    # Select this route
                    st.session_state.selected_route_idx = idx
                    st.session_state.current_route = st.session_state.all_routes[idx]
                    st.rerun()
    
    # Show detailed route comparison
    st.markdown("---")
    st.markdown("### 📊 Route Comparison")
    
    # Create comparison table
    comparison_cols = st.columns([3, 2, 2])
    
    with comparison_cols[0]:
        st.markdown("**Route**")
    with comparison_cols[1]:
        st.markdown("**Distance**")
    with comparison_cols[2]:
        st.markdown("**Time**")
    
    for idx in range(num_routes):
        route = st.session_state.all_routes[idx]
        is_selected = (idx == st.session_state.selected_route_idx)
        is_shortest = (idx == 0)
        
        route_name = route.get('route_name', f'Route {idx+1}')
        distance = route.get('distance', 0)
        duration = route.get('duration', 0)
        eta_h = int(duration // 60)
        eta_m = int(duration % 60)
        
        cols = st.columns([3, 2, 2])
        
        with cols[0]:
            if is_shortest:
                st.markdown(f"⭐ **{route_name}** {'✓' if is_selected else ''}")
            else:
                st.markdown(f"{route_name} {'✓' if is_selected else ''}")
        with cols[1]:
            st.markdown(f"{distance:.2f} km")
        with cols[2]:
            st.markdown(f"{eta_h}h {eta_m}m")
    
    # Show detailed path description for selected route
    st.markdown("---")
    st.markdown("### � Selected Route Details")
    
    selected_route = st.session_state.all_routes[st.session_state.selected_route_idx]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Distance", f"{selected_route['distance']:.2f} km")
    
    with col2:
        duration = selected_route['duration']
        eta_h = int(duration // 60)
        eta_m = int(duration % 60)
        st.metric("Duration", f"{eta_h}h {eta_m}m")
    
    with col3:
        is_shortest = (st.session_state.selected_route_idx == 0)
        st.metric("Type", "Shortest ⭐" if is_shortest else "Alternate")
    
    # Show path waypoints
    coords = selected_route['coordinates']
    st.markdown(f"**Route waypoints:** {len(coords)} coordinates")
    
    with st.expander("View Path Coordinates"):
        # Show first 10 and last 10 coordinates
        st.markdown("**Starting waypoints:**")
        for i in range(min(10, len(coords))):
            st.text(f"{i+1}. Lat: {coords[i][0]:.6f}, Lon: {coords[i][1]:.6f}")
        
        if len(coords) > 20:
            st.markdown(f"... ({len(coords) - 20} intermediate waypoints)")
        
        if len(coords) > 10:
            st.markdown("**Ending waypoints:**")
            start_idx = max(10, len(coords) - 10)
            for i in range(start_idx, len(coords)):
                st.text(f"{i+1}. Lat: {coords[i][0]:.6f}, Lon: {coords[i][1]:.6f}")


def display_summary_box():
    """Display floating summary box with crop and route info"""
    
    route = st.session_state.current_route
    
    # Get route optimization
    optimization = services['route'].optimize_route_for_crop(
        route['distance'],
        st.session_state.crop_type,
        st.session_state.quantity
    )
    
    eta_hours = int(optimization['eta_minutes'] // 60)
    eta_mins = int(optimization['eta_minutes'] % 60)
    
    summary_html = f"""
    <div class="summary-box">
        <div class="summary-title">📦 Route Summary</div>
        <div class="summary-item">
            <span class="summary-label">Crop:</span> {st.session_state.crop_type}
        </div>
        <div class="summary-item">
            <span class="summary-label">Quantity:</span> {st.session_state.quantity:.0f} kg
        </div>
        <div class="summary-item">
            <span class="summary-label">Distance:</span> {route['distance']:.1f} km
        </div>
        <div class="summary-item">
            <span class="summary-label">ETA:</span> {eta_hours}h {eta_mins}m
        </div>
    </div>
    """
    
    st.markdown(summary_html, unsafe_allow_html=True)


def reset_all():
    """Reset all selections"""
    st.session_state.start_location = None
    st.session_state.end_location = None
    st.session_state.route_calculated = False
    st.session_state.current_route = None
    st.session_state.alternative_route = None
    st.session_state.weather_checked = False
    st.rerun()


if __name__ == "__main__":
    main()
