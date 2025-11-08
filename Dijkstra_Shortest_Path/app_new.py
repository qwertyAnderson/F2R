"""
Farm-to-Market Route Optimizer
Real-time route optimization with weather-aware rerouting
"""

import streamlit as st
from streamlit_folium import st_folium
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
if 'alternative_route' not in st.session_state:
    st.session_state.alternative_route = None
if 'weather_checked' not in st.session_state:
    st.session_state.weather_checked = False
if 'crop_type' not in st.session_state:
    st.session_state.crop_type = "Moderately Perishable"
if 'quantity' not in st.session_state:
    st.session_state.quantity = 100.0


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
        
        # Predefined Dehradun locations
        dehradun_locations = {
            "Clock Tower (City Center)": (30.3165, 78.0322),
            "Rajpur Road": (30.3459, 78.0561),
            "Sahastradhara Road": (30.3255, 78.0644),
            "ISBT Dehradun": (30.3255, 78.0436),
            "Mussoorie Diversion": (30.4598, 78.0644),
            "Rispana": (30.2833, 78.0167),
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
        route_coords = st.session_state.current_route['coordinates']
        
        # Debug info
        st.sidebar.success(f"🗺️ Route Display Active!")
        st.sidebar.info(f"📍 Route has {len(route_coords)} points")
        st.sidebar.info(f"📏 Distance: {st.session_state.current_route.get('distance', 0):.1f} km")
        st.sidebar.info(f"🎯 Start: ({route_coords[0][0]:.4f}, {route_coords[0][1]:.4f})")
        st.sidebar.info(f"🏁 End: ({route_coords[-1][0]:.4f}, {route_coords[-1][1]:.4f})")
        
        # Add the route with bright, visible color
        map_obj = services['map'].add_route_to_map(
            map_obj,
            route_coords,
            color='#FF0000',  # Bright red for visibility
            label='Optimal Route'
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
    """Calculate optimal route using route service"""
    
    with st.spinner("Calculating optimal route..."):
        try:
            # Get route from map service
            route = services['map'].get_route(
                st.session_state.start_location,
                st.session_state.end_location
            )
            
            if route:
                # Apply Dijkstra's algorithm
                route_coords = route['coordinates']
                
                # Create graph and find shortest path
                services['route'].create_graph_from_coords(
                    st.session_state.start_location,
                    st.session_state.end_location,
                    route_coords
                )
                
                # Get shortest path (Dijkstra)
                start_node = "node_0"
                end_node = f"node_{len(route_coords) - 1}"
                path, distance = services['route'].find_shortest_path(start_node, end_node)
                
                # Store route
                st.session_state.current_route = route
                st.session_state.route_calculated = True
                st.session_state.weather_checked = False
                st.session_state.alternative_route = None
                
                # Increment map counter to force re-render
                if 'map_counter' not in st.session_state:
                    st.session_state.map_counter = 0
                st.session_state.map_counter += 1
                
                # Show success message with method used
                method = route.get('method', 'unknown')
                if method == 'fallback':
                    st.sidebar.warning(f"⚠️ Using straight-line distance: {route['distance']:.1f} km")
                    st.sidebar.info("💡 Actual road distance may be longer. API may be unavailable.")
                elif method == 'MapMyIndia':
                    st.sidebar.success(f"✅ Route via MapMyIndia: {route['distance']:.1f} km")
                    st.sidebar.info("🇮🇳 Using accurate India road data")
                elif method == 'OpenRouteService':
                    st.sidebar.success(f"✅ Route via OpenRouteService: {route['distance']:.1f} km")
                    st.sidebar.info("🌍 Using global road data")
                else:
                    st.sidebar.success(f"✅ Route calculated: {route['distance']:.1f} km")
                
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
