"""
Map Service - Handles map rendering and routing API calls
Uses OpenRouteService (free tier, no credit card required)
"""

import requests
from typing import List, Tuple, Optional, Dict
import folium
from folium import plugins
import streamlit as st
import numpy as np
from math import sin, cos, pi

# Optional: use OSMnx + NetworkX for real OSM routing when available
try:
    import osmnx as ox
    import networkx as nx
    from shapely.geometry import LineString, MultiLineString
    from shapely.ops import linemerge
    OSMNX_AVAILABLE = True
except Exception:
    OSMNX_AVAILABLE = False


class MapService:
    """Service for map operations and routing"""
    
    def __init__(self):
        # Using MapMyIndia (Mappls) API - Best for India routes
        # Get your free API key from: https://apis.mappls.com/console/
        # Free tier: 2500 requests/day
        try:
            self.api_key = st.secrets["MAPPLS_API_KEY"]
            print(f"🔑 MapMyIndia API Key loaded: {self.api_key[:10]}...")
        except Exception as e:
            print(f"❌ Failed to load MapMyIndia API key: {e}")
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
        Get route using MapMyIndia API only (optimized single API solution)
        
        Args:
            start_coords: (lat, lon)
            end_coords: (lat, lon)
            
        Returns:
            Route data including coordinates and distance
        """
        # SINGLE API: Use MapMyIndia only (best for Indian roads)
        if self.api_key:
            print("🇮🇳 Getting route from MapMyIndia API...")
            result = self._get_mappls_route(start_coords, end_coords)
            if result:
                print("✅ MapMyIndia route successful")
                return result
            else:
                print("⚠️ MapMyIndia API failed")
        else:
            print("❌ No MapMyIndia API key")
        
        # Simple fallback: straight line
        print("📏 Using direct route fallback...")
        return self._get_direct_route(start_coords, end_coords)
    
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
        # SINGLE API SOLUTION: Use MapMyIndia only (best for Indian roads)
        if self.api_key:
            print("🇮🇳 Using MapMyIndia API (optimized for Indian roads)...")
            mappls_routes = self._get_mappls_alternatives(start_coords, end_coords)
            if mappls_routes and len(mappls_routes) > 0:
                print(f"✅ Successfully got {len(mappls_routes)} routes from MapMyIndia")
                return mappls_routes
            else:
                print("⚠️ MapMyIndia API request failed")
        else:
            print("❌ No MapMyIndia API key available")

        # Simple fallback: return straight line if API fails
        print("📏 Using direct route as fallback...")
        direct_route = self._get_direct_route(start_coords, end_coords)
        return [direct_route] if direct_route else []
    
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
            detour_factor = sin(progress * pi) * 0.008  # Smaller, more realistic offset
            alt1_coords.append((lat + detour_factor, lon + detour_factor * 0.5))
        
        alt1_distance = main_distance * 1.12  # 12% longer - realistic alternate road
        
        alternatives.append({
            'coordinates': alt1_coords,
            'distance': alt1_distance,
            'duration': (alt1_distance / 48) * 60,  # Slightly slower
            'method': 'alternative',
            'route_name': 'Alternate Road 1',
            'route_id': 'route_1'
        })
        
        # Alternative 2: Simulates taking another parallel road
        # (like avoiding city center, taking outer route)
        alt2_coords = []
        for i, (lat, lon) in enumerate(main_coords):
            progress = i / len(main_coords)
            # Different detour pattern
            detour_factor = sin(progress * pi) * 0.01
            alt2_coords.append((lat - detour_factor * 0.5, lon + detour_factor))
        
        alt2_distance = main_distance * 1.18  # 18% longer
        
        alternatives.append({
            'coordinates': alt2_coords,
            'distance': alt2_distance,
            'duration': (alt2_distance / 50) * 60,
            'method': 'alternative',
            'route_name': 'Alternate Road 2',
            'route_id': 'route_2'
        })
        
        return alternatives
    
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
                        'method': 'MapMyIndia',
                        'route_name': 'Shortest Path',
                        'route_id': 'route_0'
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
    
    def _get_mappls_alternatives(self, start_coords: Tuple[float, float],
                                end_coords: Tuple[float, float]) -> List[Dict]:
        """
        Get multiple alternative routes from MapMyIndia API
        MapMyIndia supports 'alternatives' parameter to get different route options
        """
        try:
            print(f"\n=== MapMyIndia Alternative Routes Request ===")
            print(f"Start: {start_coords}")
            print(f"End: {end_coords}")
            
            # MapMyIndia route_adv API with alternatives parameter
            url = f"{self.mappls_base_url}/{self.api_key}/route_adv/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
            
            params = {
                'geometries': 'polyline',
                'overview': 'full',
                'steps': 'true',
                'alternatives': 'true',  # Request alternative routes
                'exclude': ''  # Can be used to exclude highways, tolls, etc.
            }
            
            print(f"Requesting alternative routes from MapMyIndia...")
            
            response = requests.get(url, params=params, timeout=15)
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'routes' in data and len(data['routes']) > 0:
                    routes = []
                    route_names = ['Shortest Path', 'Alternate Road 1', 'Alternate Road 2', 'Alternate Road 3']
                    
                    print(f"Found {len(data['routes'])} route(s) from MapMyIndia")
                    
                    for idx, route_data in enumerate(data['routes'][:3]):  # Max 3 routes
                        coords = self._decode_polyline(route_data['geometry'])
                        
                        distance_km = route_data['distance'] / 1000
                        duration_min = route_data['duration'] / 60
                        
                        print(f"Route {idx+1}: {distance_km:.2f} km, {len(coords)} points")
                        
                        routes.append({
                            'coordinates': coords,
                            'distance': distance_km,
                            'duration': duration_min,
                            'method': 'MapMyIndia',
                            'route_name': route_names[idx] if idx < len(route_names) else f'Route {idx+1}',
                            'route_id': f'route_{idx}'
                        })
                    
                    return routes
            
            print(f"MapMyIndia Alternatives API Error {response.status_code}: {response.text[:200]}")
            return []
                
        except Exception as e:
            print(f"MapMyIndia Alternatives Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def _get_osm_alternatives(self, start_coords: Tuple[float, float],
                              end_coords: Tuple[float, float],
                              max_routes: int = 3) -> List[Dict]:
        """
        Compute real road routes using OSMnx + NetworkX.
        Returns a list of route dicts with 'coordinates' (lat,lon), 'distance' (km), 'duration' (min)
        """
        if not OSMNX_AVAILABLE:
            return []

        try:
            lat1, lon1 = start_coords
            lat2, lon2 = end_coords

            # center point and bounding distance: base on straight-line approx (deg->km ~111km)
            d_deg = ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5
            straight_km = max(0.5, d_deg * 111.0)
            # OPTIMIZED: Smaller radius for faster download (max 8km radius)
            search_dist_m = int(min(8000, max(2000, straight_km * 1000 * 1.2)))

            center_lat = (lat1 + lat2) / 2.0
            center_lon = (lon1 + lon2) / 2.0

            print(f"OSMnx: downloading graph around center {(center_lat, center_lon)} with dist {search_dist_m}m")
            G = ox.graph_from_point((center_lat, center_lon), dist=search_dist_m, network_type='drive')
            
            # Convert multigraph to simple graph for shortest_simple_paths
            G_simple = nx.Graph(G)

            # Snap to nearest nodes (ox.nearest_nodes expects lon, lat)
            try:
                start_node = ox.nearest_nodes(G, lon1, lat1)
                end_node = ox.nearest_nodes(G, lon2, lat2)
            except Exception:
                # older versions: (G, X, Y) signature may vary
                start_node = ox.nearest_nodes(G, X=lon1, Y=lat1)
                end_node = ox.nearest_nodes(G, X=lon2, Y=lat2)

            if start_node == end_node:
                return []

            routes = []
            # Generate simple shortest paths (ordered by length) on simplified graph
            paths_gen = nx.shortest_simple_paths(G_simple, start_node, end_node, weight='length')

            for i, node_path in enumerate(paths_gen):
                if i >= max_routes:
                    break

                # SIMPLIFIED: Just use node coordinates for speed and reliability
                # This gives us real road paths without complex geometry handling
                total_length_m = 0.0
                final_coords = []
                
                for j in range(len(node_path)):
                    node = node_path[j]
                    lat = G.nodes[node]['y']
                    lon = G.nodes[node]['x']
                    final_coords.append((lat, lon))
                    
                    # Calculate distance for this segment
                    if j > 0:
                        prev_node = node_path[j-1]
                        edge_data = G.get_edge_data(prev_node, node)
                        if edge_data:
                            # Get shortest edge if multiple
                            edge_lengths = [attr.get('length', 0) for attr in edge_data.values()]
                            total_length_m += min(edge_lengths) if edge_lengths else 0

                distance_km = total_length_m / 1000.0
                duration_min = (distance_km / 40.0) * 60.0  # assume 40 km/h avg

                routes.append({
                    'coordinates': final_coords,
                    'distance': distance_km,
                    'duration': duration_min,
                    'method': 'OSMnx',
                    'route_name': 'OSM Route ' + str(i),
                    'route_id': f'osm_{i}'
                })

            return routes

        except Exception as e:
            print(f"OSMnx Alternatives Exception: {e}")
            return []
    
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
                    'method': 'OpenRouteService',
                    'route_name': 'Primary Route'
                }
            
            print(f"OpenRoute API Error {response.status_code}: {response.text}")
            return None
                
        except Exception as e:
            print(f"OpenRoute Exception: {str(e)}")
            return None
    
    def _get_openroute_alternatives(self, start_coords: Tuple[float, float], 
                                   end_coords: Tuple[float, float]) -> List[Dict]:
        """
        Get multiple alternative routes from OpenRouteService
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
                ],
                "alternative_routes": {
                    "share_factor": 0.6,
                    "target_count": 3,  # Request 3 alternative routes
                    "weight_factor": 1.4
                },
                "geometry": True
            }
            
            print(f"Requesting alternative routes from OpenRouteService...")
            response = requests.post(url, json=body, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                routes = []
                
                route_names = ['Shortest Route', 'Alternative Route 1', 'Alternative Route 2', 'Alternative Route 3']
                
                for idx, route_data in enumerate(data['routes'][:4]):  # Max 4 routes
                    coords = [(coord[1], coord[0]) for coord in route_data['geometry']['coordinates']]
                    
                    routes.append({
                        'coordinates': coords,
                        'distance': route_data['summary']['distance'] / 1000,
                        'duration': route_data['summary']['duration'] / 60,
                        'method': 'OpenRouteService',
                        'route_name': route_names[idx] if idx < len(route_names) else f'Route {idx+1}',
                        'route_id': f'route_{idx}'
                    })
                
                print(f"Found {len(routes)} alternative routes")
                return routes
            
            print(f"OpenRoute Alternatives API Error {response.status_code}: {response.text[:200]}")
            return []
                
        except Exception as e:
            print(f"OpenRoute Alternatives Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
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
            'method': 'fallback',
            'route_name': 'Shortest Path',
            'route_id': 'route_0'
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
                        color: str = '#2E7D32', label: str = "Optimal Route",
                        weight: int = 6, opacity: float = 0.9) -> folium.Map:
        """Add route polyline to map with enhanced visibility"""
        
        # Add a thick shadow/outline for better visibility (only for primary routes)
        if weight >= 7:
            folium.PolyLine(
                locations=route_coords,
                color='#000000',
                weight=weight + 3,
                opacity=opacity * 0.3,
            ).add_to(map_obj)
        
        # Add main route line
        folium.PolyLine(
            locations=route_coords,
            color=color,
            weight=weight,
            opacity=opacity,
            popup=label,
            tooltip=label
        ).add_to(map_obj)
        
        # Add arrow decorators to show direction (only for primary selected route)
        if weight >= 7:
            try:
                plugins.PolyLineTextPath(
                    folium.PolyLine(route_coords, weight=weight, opacity=0),
                    '   ►   ',
                    repeat=True,
                    offset=8,
                    attributes={'fill': color, 'font-weight': 'bold', 'font-size': '18'}
                ).add_to(map_obj)
            except Exception as e:
                print(f"Could not add arrow decorators: {e}")
        
        # Add start and end markers on the route (only for primary selected route)
        if weight >= 7:
            folium.CircleMarker(
                location=route_coords[0],
                radius=10,
                color='green',
                fill=True,
                fillColor='lightgreen',
                fillOpacity=0.9,
                popup="Route Start",
                weight=4
            ).add_to(map_obj)
            
            folium.CircleMarker(
                location=route_coords[-1],
                radius=10,
                color='red',
                fill=True,
                fillColor='pink',
                fillOpacity=0.9,
                popup="Route End",
                weight=4
            ).add_to(map_obj)
        
        return map_obj
