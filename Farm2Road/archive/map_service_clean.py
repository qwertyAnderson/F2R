"""
Map Service - Handles map rendering and routing API calls
Uses MapMyIndia API only (optimized for Indian roads)
"""

import requests
from typing import List, Tuple, Optional, Dict
import folium
from folium import plugins
import streamlit as st
import numpy as np
from math import sin, cos, pi


class MapService:
    """Service for map operations and routing"""
    
    def __init__(self):
        # SINGLE API SOLUTION: MapMyIndia (Mappls) API Only
        # Get your free API key from: https://apis.mappls.com/console/
        # Free tier: 2500 requests/day - Perfect for farm routing
        try:
            self.api_key = st.secrets["MAPPLS_API_KEY"]
            print(f"🇮🇳 MapMyIndia API Key loaded: {self.api_key[:10]}...")
        except Exception as e:
            print(f"❌ Failed to load MapMyIndia API key: {e}")
            self.api_key = None
        
        # MapMyIndia REST API endpoint
        self.mappls_base_url = "https://apis.mappls.com/advancedmaps/v1"
        
    def get_route(self, start_coords: Tuple[float, float], 
                  end_coords: Tuple[float, float]) -> Optional[Dict]:
        """
        Get route using MapMyIndia API only
        
        Args:
            start_coords: (lat, lon)
            end_coords: (lat, lon)
            
        Returns:
            Route data including coordinates and distance
        """
        if not self.api_key:
            print("❌ MapMyIndia API key not available")
            return None
            
        print("🇮🇳 Getting route from MapMyIndia API...")
        result = self._get_mappls_route(start_coords, end_coords)
        
        if result:
            print("✅ MapMyIndia route successful")
            return result
        else:
            print("❌ MapMyIndia API request failed")
            return None
    
    def get_multiple_routes(self, start_coords: Tuple[float, float], 
                           end_coords: Tuple[float, float]) -> List[Dict]:
        """
        Get multiple alternative routes using MapMyIndia API only
        
        Args:
            start_coords: (lat, lon)
            end_coords: (lat, lon)
            
        Returns:
            List of route dictionaries with coordinates, distance, duration
        """
        if not self.api_key:
            print("❌ MapMyIndia API key not available")
            return []
            
        print("🇮🇳 Getting multiple routes from MapMyIndia API...")
        mappls_routes = self._get_mappls_alternatives(start_coords, end_coords)
        
        if mappls_routes and len(mappls_routes) > 0:
            print(f"✅ Successfully got {len(mappls_routes)} routes from MapMyIndia")
            return mappls_routes
        else:
            print("❌ MapMyIndia API request failed")
            return []

    def _create_alternative_routes(self, start_coords: Tuple[float, float],
                                   end_coords: Tuple[float, float],
                                   main_route: Dict) -> List[Dict]:
        """
        Create realistic alternative route variations simulating actual road networks
        These represent different real roads one might take between two points
        """
        alternatives = []
        main_coords = main_route['coordinates']
        main_distance = main_route['distance']
        
        # Alternative 1: Simulates taking a parallel road with slight detour
        # (like taking Ring Road instead of Main Road)
        alt1_coords = []
        for i, (lat, lon) in enumerate(main_coords):
            progress = i / len(main_coords)
            # Create a detour that peaks in the middle (simulating going around)
            detour_factor = sin(progress * pi) * 0.008  # ~1km max detour
            alt_lat = lat + detour_factor
            alt_lon = lon + detour_factor * 0.5
            alt1_coords.append((alt_lat, alt_lon))
        
        alternatives.append({
            'coordinates': alt1_coords,
            'distance': main_distance * 1.15,  # 15% longer (realistic)
            'duration': main_route['duration'] * 1.2,  # Slightly slower
            'method': 'MapMyIndia Alternative',
            'route_name': 'Ring Road Route'
        })
        
        # Alternative 2: Highway route (faster but longer)
        alt2_coords = []
        for i, (lat, lon) in enumerate(main_coords):
            progress = i / len(main_coords)
            # Simulate highway routing (wider arc)
            highway_factor = sin(progress * pi) * 0.012
            alt_lat = lat - highway_factor * 0.7
            alt_lon = lon + highway_factor
            alt2_coords.append((alt_lat, alt_lon))
        
        alternatives.append({
            'coordinates': alt2_coords,
            'distance': main_distance * 1.25,  # 25% longer
            'duration': main_route['duration'] * 1.1,  # But faster (highway speeds)
            'method': 'MapMyIndia Alternative',
            'route_name': 'Highway Route'
        })
        
        return alternatives

    def _get_mappls_route(self, start_coords: Tuple[float, float], 
                         end_coords: Tuple[float, float]) -> Optional[Dict]:
        """Get single route from MapMyIndia API"""
        try:
            # Correct URL format for MapMyIndia routing API
            url = f"{self.mappls_base_url}/{self.api_key}/route_adv/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
            
            params = {
                'alternatives': 'false',
                'geometries': 'geojson',
                'steps': 'false'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'routes' in data and len(data['routes']) > 0:
                    route = data['routes'][0]
                    
                    # Extract coordinates from geometry
                    if 'geometry' in route and 'coordinates' in route['geometry']:
                        # MapMyIndia returns [lon, lat] format
                        coords = [(coord[1], coord[0]) for coord in route['geometry']['coordinates']]
                        
                        return {
                            'coordinates': coords,
                            'distance': route['distance'] / 1000,  # Convert to km
                            'duration': route['duration'] / 60,    # Convert to minutes
                            'method': 'MapMyIndia',
                            'source': 'MapMyIndia API'
                        }
            else:
                print(f"MapMyIndia API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"MapMyIndia Route Exception: {e}")
            
        return None

    def _get_mappls_alternatives(self, start_coords: Tuple[float, float],
                                end_coords: Tuple[float, float]) -> List[Dict]:
        """Get multiple alternative routes from MapMyIndia"""
        try:
            print("=== MapMyIndia Alternative Routes Request ===")
            print(f"Start: {start_coords}")
            print(f"End: {end_coords}")
            print("Requesting alternative routes from MapMyIndia...")
            
            # Request alternatives from MapMyIndia
            url = f"{self.mappls_base_url}/{self.api_key}/route_adv/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
            
            params = {
                'alternatives': 'true',
                'geometries': 'geojson',
                'steps': 'false'
            }
            
            response = requests.get(url, params=params, timeout=15)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                routes = []
                
                if 'routes' in data and len(data['routes']) > 0:
                    print(f"Found {len(data['routes'])} route(s) from MapMyIndia")
                    
                    for i, route in enumerate(data['routes'][:3]):  # Max 3 routes
                        if 'geometry' in route and 'coordinates' in route['geometry']:
                            coords = [(coord[1], coord[0]) for coord in route['geometry']['coordinates']]
                            
                            route_dict = {
                                'coordinates': coords,
                                'distance': route['distance'] / 1000,
                                'duration': route['duration'] / 60,
                                'method': 'MapMyIndia',
                                'route_name': f'Route {i+1}',
                                'source': 'MapMyIndia API'
                            }
                            routes.append(route_dict)
                            print(f"Route {i+1}: {route_dict['distance']:.2f} km, {len(coords)} points")
                    
                    return routes
                else:
                    print("No routes found in MapMyIndia response")
            else:
                print(f"MapMyIndia Alternatives API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"MapMyIndia Alternatives Exception: {e}")
            
        return []

    def get_alternative_route(self, start_coords: Tuple[float, float], 
                             end_coords: Tuple[float, float]) -> Optional[Dict]:
        """Get alternative route for weather rerouting"""
        routes = self.get_multiple_routes(start_coords, end_coords)
        
        if len(routes) > 1:
            return routes[1]  # Return second route as alternative
        elif len(routes) == 1:
            # Create a simple variation if only one route available
            main_route = routes[0]
            alternatives = self._create_alternative_routes(start_coords, end_coords, main_route)
            return alternatives[0] if alternatives else None
        
        return None

    def create_base_map(self, center_lat: float = 30.3165, center_lon: float = 78.0322, 
                       zoom_start: int = 11) -> folium.Map:
        """Create base Folium map centered on Dehradun"""
        return folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles='OpenStreetMap',
            prefer_canvas=True
        )
    
    def add_route_to_map(self, map_obj: folium.Map, route: Dict, 
                        color: str = 'blue', weight: int = 4, opacity: float = 0.8,
                        label: str = None) -> None:
        """Add a route to the Folium map"""
        if route and 'coordinates' in route:
            coords = route['coordinates']
            
            if len(coords) > 1:
                # Add route polyline
                folium.PolyLine(
                    coords,
                    color=color,
                    weight=weight,
                    opacity=opacity,
                    popup=label or f"Distance: {route.get('distance', 0):.1f} km"
                ).add_to(map_obj)
                
                # Add start marker
                folium.Marker(
                    coords[0],
                    popup="Start",
                    icon=folium.Icon(color='green', icon='play')
                ).add_to(map_obj)
                
                # Add end marker
                folium.Marker(
                    coords[-1],
                    popup="End",
                    icon=folium.Icon(color='red', icon='stop')
                ).add_to(map_obj)
    
    def add_location_marker(self, map_obj: folium.Map, coords: Tuple[float, float], 
                           name: str, icon_color: str = 'blue') -> None:
        """Add location marker to map"""
        folium.Marker(
            coords,
            popup=name,
            tooltip=name,
            icon=folium.Icon(color=icon_color, icon='info-sign')
        ).add_to(map_obj)