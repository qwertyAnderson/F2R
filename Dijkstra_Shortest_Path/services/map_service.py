"""
Map Service - Handles map rendering and routing API calls
Uses OpenRouteService (free tier, no credit card required)
"""

import requests
from typing import List, Tuple, Optional, Dict
import folium
from folium import plugins
import streamlit as st


class MapService:
    """Service for map operations and routing"""
    
    def __init__(self):
        # Using MapMyIndia (Mappls) API - Best for India routes
        # Get your free API key from: https://apis.mappls.com/console/
        # Free tier: 2500 requests/day
        try:
            self.api_key = st.secrets["MAPPLS_API_KEY"]
        except:
            self.api_key = None
        
        # Mappls REST API endpoints - Correct format for routing API
        self.mappls_base_url = "https://apis.mappls.com/advancedmaps/v1"
        # Note: Mappls uses client_id and client_secret, not direct API key in URL
        
        # Fallback to OpenRouteService if Mappls key not available
        self.openroute_key = "5b3ce3597851110001cf6248a1b9c0b6d4d84e8db22b35a6f4c8b5b4"
        self.openroute_url = "https://api.openrouteservice.org/v2"
        
    def get_route(self, start_coords: Tuple[float, float], 
                  end_coords: Tuple[float, float]) -> Optional[Dict]:
        """
        Get route using MapMyIndia (Mappls) API first, fallback to OpenRouteService
        
        Args:
            start_coords: (lat, lon)
            end_coords: (lat, lon)
            
        Returns:
            Route data including coordinates and distance
        """
        # Try MapMyIndia first (best for India)
        if self.api_key:
            result = self._get_mappls_route(start_coords, end_coords)
            if result:
                return result
        
        # Fallback to OpenRouteService
        result = self._get_openroute_route(start_coords, end_coords)
        if result:
            return result
        
        # Final fallback: straight line
        return self._get_direct_route(start_coords, end_coords)
    
    def _get_mappls_route(self, start_coords: Tuple[float, float], 
                         end_coords: Tuple[float, float]) -> Optional[Dict]:
        """
        Get route from MapMyIndia (Mappls) API
        Best for Indian roads and rural areas
        """
        try:
            print(f"\n=== MapMyIndia Route Request ===")
            print(f"Start: {start_coords}")
            print(f"End: {end_coords}")
            
            # Correct Mappls API format: lon,lat (not lat,lon!)
            # API endpoint: https://apis.mappls.com/advancedmaps/v1/{api_key}/route_adv/driving/{coordinates}
            url = f"{self.mappls_base_url}/{self.api_key}/route_adv/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
            
            params = {
                'geometries': 'polyline',
                'overview': 'full',
                'steps': 'true'
            }
            
            print(f"Requesting route from Mappls...")
            
            response = requests.get(url, params=params, timeout=10)
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"Response data keys: {data.keys()}")
                
                if 'routes' in data and len(data['routes']) > 0:
                    route = data['routes'][0]
                    
                    print(f"Route found! Keys: {route.keys()}")
                    print(f"Distance: {route.get('distance', 0)} meters")
                    
                    # Decode polyline geometry
                    coords = self._decode_polyline(route['geometry'])
                    
                    print(f"Decoded {len(coords)} coordinate points")
                    print(f"First point: {coords[0]}")
                    print(f"Last point: {coords[-1]}")
                    
                    result = {
                        'coordinates': coords,
                        'distance': route['distance'] / 1000,  # Convert to km
                        'duration': route['duration'] / 60,  # Convert to minutes
                        'method': 'MapMyIndia'
                    }
                    
                    print(f"Returning route: {result['distance']:.2f} km")
                    return result
            
            print(f"MapMyIndia API Error {response.status_code}: {response.text[:200]}")
            return None
                
        except Exception as e:
            print(f"MapMyIndia Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_openroute_route(self, start_coords: Tuple[float, float], 
                            end_coords: Tuple[float, float]) -> Optional[Dict]:
        """
        Get route from OpenRouteService (fallback)
        """
        try:
            url = f"{self.openroute_url}/directions/driving-car"
            
            headers = {
                'Authorization': self.openroute_key,
                'Content-Type': 'application/json'
            }
            
            body = {
                "coordinates": [
                    [start_coords[1], start_coords[0]],  # [lon, lat]
                    [end_coords[1], end_coords[0]]
                ]
            }
            
            response = requests.post(url, json=body, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                route = data['routes'][0]
                
                coords = [(coord[1], coord[0]) for coord in route['geometry']['coordinates']]
                
                return {
                    'coordinates': coords,
                    'distance': route['summary']['distance'] / 1000,
                    'duration': route['summary']['duration'] / 60,
                    'method': 'OpenRouteService'
                }
            
            print(f"OpenRoute API Error {response.status_code}: {response.text}")
            return None
                
        except Exception as e:
            print(f"OpenRoute Exception: {str(e)}")
            return None
    
    def _decode_polyline(self, polyline_str: str) -> List[Tuple[float, float]]:
        """
        Decode Google-style polyline to list of coordinates
        """
        coords = []
        index = 0
        lat = 0
        lng = 0
        
        while index < len(polyline_str):
            # Decode latitude
            shift = 0
            result = 0
            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            dlat = ~(result >> 1) if (result & 1) else (result >> 1)
            lat += dlat
            
            # Decode longitude
            shift = 0
            result = 0
            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            dlng = ~(result >> 1) if (result & 1) else (result >> 1)
            lng += dlng
            
            coords.append((lat / 1e5, lng / 1e5))
        
        return coords
    
    def _get_direct_route(self, start_coords: Tuple[float, float], 
                          end_coords: Tuple[float, float]) -> Dict:
        """Fallback: direct line between points with intermediate points for better visualization"""
        from math import radians, sin, cos, sqrt, atan2
        
        # Calculate distance using Haversine formula
        lat1, lon1 = radians(start_coords[0]), radians(start_coords[1])
        lat2, lon2 = radians(end_coords[0]), radians(end_coords[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = 6371 * c  # Earth radius in km
        
        # Create intermediate points for smoother line visualization
        num_points = 20  # More points for smoother line
        coords = []
        for i in range(num_points + 1):
            fraction = i / num_points
            lat = start_coords[0] + (end_coords[0] - start_coords[0]) * fraction
            lon = start_coords[1] + (end_coords[1] - start_coords[1]) * fraction
            coords.append((lat, lon))
        
        print(f"Using fallback: straight-line distance = {distance:.2f} km with {len(coords)} interpolated points")
        
        return {
            'coordinates': coords,
            'distance': distance,
            'duration': distance / 50 * 60,  # Assume 50 km/h average
            'method': 'fallback'
        }
    
    def get_alternative_route(self, start_coords: Tuple[float, float], 
                             end_coords: Tuple[float, float]) -> Optional[Dict]:
        """Get alternative route (different from main route)"""
        try:
            url = f"{self.base_url}/directions/driving-car"
            
            headers = {
                'Authorization': self.api_key,
                'Content-Type': 'application/json'
            }
            
            body = {
                "coordinates": [
                    [start_coords[1], start_coords[0]],
                    [end_coords[1], end_coords[0]]
                ],
                "alternative_routes": {
                    "share_factor": 0.6,
                    "target_count": 2
                }
            }
            
            response = requests.post(url, json=body, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if len(data['routes']) > 1:
                    route = data['routes'][1]  # Get alternative route
                else:
                    route = data['routes'][0]
                
                coords = [(coord[1], coord[0]) for coord in route['geometry']['coordinates']]
                
                return {
                    'coordinates': coords,
                    'distance': route['summary']['distance'] / 1000,
                    'duration': route['summary']['duration'] / 60,
                }
            else:
                return None
                
        except Exception:
            return None
    
    def create_base_map(self, center: Tuple[float, float] = (30.3165, 78.0322), 
                       zoom: int = 12) -> folium.Map:
        """
        Create a base Folium map (Dehradun-centered by default)
        
        Args:
            center: (lat, lon) for map center
            zoom: Zoom level
            
        Returns:
            Folium Map object
        """
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap',
            control_scale=True,
            min_zoom=11,
            max_zoom=18
        )
        
        # Add click functionality
        m.add_child(folium.LatLngPopup())
        
        return m
    
    def add_markers(self, map_obj: folium.Map, 
                   start: Optional[Tuple[float, float]], 
                   end: Optional[Tuple[float, float]]) -> folium.Map:
        """Add start and end markers to map"""
        
        if start:
            folium.Marker(
                location=start,
                popup="Start Location",
                icon=folium.Icon(color='green', icon='play', prefix='fa'),
                tooltip="Start"
            ).add_to(map_obj)
        
        if end:
            folium.Marker(
                location=end,
                popup="End Location",
                icon=folium.Icon(color='red', icon='flag-checkered', prefix='fa'),
                tooltip="Destination"
            ).add_to(map_obj)
        
        return map_obj
    
    def add_route_to_map(self, map_obj: folium.Map, route_coords: List[Tuple[float, float]], 
                        color: str = '#2E7D32', label: str = "Optimal Route") -> folium.Map:
        """Add route polyline to map with enhanced visibility"""
        
        print(f"Adding route to map: {len(route_coords)} points")
        print(f"First point: {route_coords[0]}")
        print(f"Last point: {route_coords[-1]}")
        
        # Add a thick shadow/outline for better visibility
        folium.PolyLine(
            locations=route_coords,
            color='#000000',
            weight=8,
            opacity=0.5,
        ).add_to(map_obj)
        
        # Add main route line
        folium.PolyLine(
            locations=route_coords,
            color=color,
            weight=6,
            opacity=0.9,
            popup=label,
            tooltip=label
        ).add_to(map_obj)
        
        # Add arrow decorators to show direction
        try:
            plugins.PolyLineTextPath(
                folium.PolyLine(route_coords, weight=6, opacity=0),
                '   ►   ',
                repeat=True,
                offset=8,
                attributes={'fill': color, 'font-weight': 'bold', 'font-size': '18'}
            ).add_to(map_obj)
        except Exception as e:
            print(f"Could not add arrow decorators: {e}")
        
        # Add start and end markers on the route
        folium.CircleMarker(
            location=route_coords[0],
            radius=8,
            color='green',
            fill=True,
            fillColor='lightgreen',
            fillOpacity=0.8,
            popup="Route Start",
            weight=3
        ).add_to(map_obj)
        
        folium.CircleMarker(
            location=route_coords[-1],
            radius=8,
            color='red',
            fill=True,
            fillColor='pink',
            fillOpacity=0.8,
            popup="Route End",
            weight=3
        ).add_to(map_obj)
        
        return map_obj
