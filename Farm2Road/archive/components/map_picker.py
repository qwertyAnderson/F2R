"""
Map Picker Component - Interactive map for selecting locations
"""

import streamlit as st
from streamlit_folium import st_folium
from typing import Optional, Tuple
import folium


class MapPicker:
    """Component for interactive map-based location picking"""
    
    @staticmethod
    def render(map_obj: folium.Map, height: int = 500) -> Optional[Tuple[float, float]]:
        """
        Render interactive map and return clicked coordinates
        
        Args:
            map_obj: Folium map object
            height: Map height in pixels
            
        Returns:
            Clicked coordinates (lat, lon) or None
        """
        # Render map with st_folium
        map_data = st_folium(
            map_obj,
            height=height,
            width=None,
            returned_objects=["last_clicked"],
            key="map"
        )
        
        # Extract clicked coordinates
        if map_data and map_data.get("last_clicked"):
            clicked = map_data["last_clicked"]
            lat = clicked.get("lat")
            lon = clicked.get("lng")
            
            if lat is not None and lon is not None:
                return (lat, lon)
        
        return None
    
    @staticmethod
    def display_coordinates(coords: Optional[Tuple[float, float]], label: str):
        """Display coordinates in a clean format (for debugging only)"""
        if coords:
            # Internal validation only - not shown to user
            pass
