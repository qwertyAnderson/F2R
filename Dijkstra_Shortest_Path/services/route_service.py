"""
Route Service - Implements Dijkstra's algorithm for shortest path
"""

import networkx as nx
from typing import List, Tuple, Dict, Optional
import numpy as np


class RouteService:
    """Service for route calculation using Dijkstra's algorithm"""
    
    def __init__(self):
        self.graph = nx.Graph()
    
    def create_graph_from_coords(self, start_coords: Tuple[float, float], 
                                end_coords: Tuple[float, float],
                                route_coords: List[Tuple[float, float]]) -> nx.Graph:
        """
        Create a graph from route coordinates for Dijkstra's algorithm
        
        Args:
            start_coords: Start location (lat, lon)
            end_coords: End location (lat, lon)
            route_coords: List of coordinates along the route
            
        Returns:
            NetworkX Graph
        """
        G = nx.Graph()
        
        # Add edges between consecutive points with calculated distances
        for i in range(len(route_coords) - 1):
            point_a = route_coords[i]
            point_b = route_coords[i + 1]
            
            # Calculate distance between points
            distance = self._calculate_distance(point_a, point_b)
            
            # Add edge with distance as weight
            G.add_edge(
                f"node_{i}",
                f"node_{i+1}",
                weight=distance,
                coords_a=point_a,
                coords_b=point_b
            )
        
        self.graph = G
        return G
    
    def _calculate_distance(self, coord1: Tuple[float, float], 
                           coord2: Tuple[float, float]) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Args:
            coord1: (lat, lon)
            coord2: (lat, lon)
            
        Returns:
            Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return 6371 * c  # Earth radius in km
    
    def find_shortest_path(self, start_node: str, end_node: str) -> Tuple[List[str], float]:
        """
        Find shortest path using Dijkstra's algorithm
        
        Args:
            start_node: Starting node identifier
            end_node: Ending node identifier
            
        Returns:
            Tuple of (path as list of nodes, total distance)
        """
        try:
            if not self.graph.has_node(start_node) or not self.graph.has_node(end_node):
                return [], 0.0
            
            # Use NetworkX's Dijkstra implementation
            path = nx.dijkstra_path(self.graph, start_node, end_node, weight='weight')
            distance = nx.dijkstra_path_length(self.graph, start_node, end_node, weight='weight')
            
            return path, distance
            
        except nx.NetworkXNoPath:
            return [], 0.0
        except Exception:
            return [], 0.0
    
    def get_path_coordinates(self, node_path: List[str]) -> List[Tuple[float, float]]:
        """
        Convert node path to coordinates
        
        Args:
            node_path: List of node identifiers
            
        Returns:
            List of coordinates
        """
        coords = []
        
        for i in range(len(node_path) - 1):
            edge_data = self.graph.get_edge_data(node_path[i], node_path[i + 1])
            if edge_data:
                coords.append(edge_data['coords_a'])
        
        # Add last coordinate
        if node_path:
            last_edge = self.graph.get_edge_data(node_path[-2], node_path[-1])
            if last_edge:
                coords.append(last_edge['coords_b'])
        
        return coords
    
    def optimize_route_for_crop(self, distance: float, crop_type: str, 
                               quantity: float) -> Dict:
        """
        Calculate route optimization based on crop characteristics
        
        Args:
            distance: Route distance in km
            crop_type: Type of crop being transported
            quantity: Quantity in kg
            
        Returns:
            Dictionary with optimization recommendations
        """
        # Speed adjustments based on crop type
        speed_factors = {
            "Highly Perishable": 0.85,  # Need to go faster, less stops
            "Moderately Perishable": 1.0,  # Normal speed
            "Non-Perishable": 1.1,  # Can take slower, more economical route
            "Fragile": 0.7,  # Need to go slower for safety
            "Bulk / Heavy": 0.8,  # Heavier load, slower speed
        }
        
        base_speed = 50  # km/h
        factor = speed_factors.get(crop_type, 1.0)
        adjusted_speed = base_speed * factor
        
        # Calculate estimated time
        eta_minutes = (distance / adjusted_speed) * 60
        
        # Calculate recommended stops based on crop type and distance
        stops = 0
        if crop_type in ["Highly Perishable", "Fragile"]:
            stops = max(0, int((distance / 100)))  # Stop every 100km
        else:
            stops = max(0, int((distance / 150)))  # Stop every 150km
        
        return {
            'adjusted_speed': adjusted_speed,
            'eta_minutes': eta_minutes,
            'recommended_stops': stops,
            'priority': 'high' if crop_type == "Highly Perishable" else 'medium'
        }
