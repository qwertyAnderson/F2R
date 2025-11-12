"""
Chart Service - Matplotlib visualizations for route analysis
Provides clean charts for route comparison and analytics
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st
from config import CHART_CONFIG
import numpy as np

class ChartService:
    """Service for creating matplotlib charts"""
    
    def __init__(self):
        # Set matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
        
    def create_route_comparison_chart(self, routes):
        """
        Create side-by-side comparison chart for multiple routes
        
        Args:
            routes: List of route dictionaries with distance, duration, etc.
        """
        if not routes or len(routes) == 0:
            return None
            
        # Prepare data
        route_names = [f"Route {i+1}" for i in range(len(routes))]
        distances = [route.get('distance', 0) for route in routes]
        durations = [route.get('duration', 0) for route in routes]
        colors = CHART_CONFIG['colors'][:len(routes)]
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=CHART_CONFIG['figure_size'])
        
        # Distance comparison (horizontal bar chart)
        bars1 = ax1.barh(route_names, distances, color=colors)
        ax1.set_xlabel('Distance (km)', fontsize=CHART_CONFIG['font_size'])
        ax1.set_title('Route Distance Comparison', fontsize=CHART_CONFIG['title_size'], fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Add distance labels on bars
        for i, (bar, distance) in enumerate(zip(bars1, distances)):
            ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{distance:.1f} km', va='center', fontsize=9)
        
        # Duration comparison (vertical bar chart)
        bars2 = ax2.bar(route_names, durations, color=colors)
        ax2.set_ylabel('Duration (minutes)', fontsize=CHART_CONFIG['font_size'])
        ax2.set_title('Route Time Comparison', fontsize=CHART_CONFIG['title_size'], fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add duration labels on bars
        for i, (bar, duration) in enumerate(zip(bars2, durations)):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{duration:.0f} min', ha='center', fontsize=9)
        
        # Rotate x-axis labels for better readability
        ax2.tick_params(axis='x', rotation=45)
        
        # Tight layout and return
        plt.tight_layout()
        return fig
    
    def create_route_efficiency_chart(self, routes):
        """
        Create efficiency analysis chart (Speed vs Distance)
        """
        if not routes or len(routes) < 2:
            return None
            
        # Calculate efficiency metrics
        distances = [route.get('distance', 0) for route in routes]
        durations = [route.get('duration', 0) for route in routes]
        speeds = [d / (t/60) if t > 0 else 0 for d, t in zip(distances, durations)]
        
        route_names = [f"Route {i+1}" for i in range(len(routes))]
        colors = CHART_CONFIG['colors'][:len(routes)]
        
        # Create scatter plot
        fig, ax = plt.subplots(figsize=(8, 6))
        
        scatter = ax.scatter(distances, speeds, c=colors, s=200, alpha=0.7, edgecolors='black')
        
        # Add route labels
        for i, (d, s, name) in enumerate(zip(distances, speeds, route_names)):
            ax.annotate(name, (d, s), xytext=(5, 5), textcoords='offset points', 
                       fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Distance (km)', fontsize=CHART_CONFIG['font_size'])
        ax.set_ylabel('Average Speed (km/h)', fontsize=CHART_CONFIG['font_size'])
        ax.set_title('Route Efficiency Analysis', fontsize=CHART_CONFIG['title_size'], fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_weather_timeline_chart(self, weather_data):
        """
        Create weather forecast timeline chart
        
        Args:
            weather_data: Dictionary with hourly weather forecast
        """
        if not weather_data:
            return None
            
        # Sample weather timeline (you'd replace with real data)
        hours = list(range(6, 22))  # 6 AM to 10 PM
        temperatures = [18, 20, 23, 26, 28, 30, 32, 31, 29, 27, 25, 23, 21, 19, 17, 16]
        rain_probability = [10, 5, 15, 25, 40, 60, 80, 70, 50, 30, 20, 15, 10, 5, 0, 0]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
        
        # Temperature timeline
        ax1.plot(hours, temperatures, color='#FF6B6B', linewidth=3, marker='o')
        ax1.set_ylabel('Temperature (°C)', fontsize=CHART_CONFIG['font_size'])
        ax1.set_title('Weather Forecast Timeline', fontsize=CHART_CONFIG['title_size'], fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.fill_between(hours, temperatures, alpha=0.3, color='#FF6B6B')
        
        # Rain probability
        ax2.bar(hours, rain_probability, color='#4ECDC4', alpha=0.7)
        ax2.set_ylabel('Rain Probability (%)', fontsize=CHART_CONFIG['font_size'])
        ax2.set_xlabel('Time (24h)', fontsize=CHART_CONFIG['font_size'])
        ax2.grid(True, alpha=0.3)
        
        # Highlight risky times (rain > 50%)
        risky_hours = [h for h, r in zip(hours, rain_probability) if r > 50]
        for hour in risky_hours:
            ax2.axvline(x=hour, color='red', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
    
    def create_crop_optimization_chart(self, crop_type, routes):
        """
        Create crop-specific route optimization chart
        """
        if not routes:
            return None
            
        route_names = [f"Route {i+1}" for i in range(len(routes))]
        distances = [route.get('distance', 0) for route in routes]
        durations = [route.get('duration', 0) for route in routes]
        
        # Calculate crop-specific scores (lower is better)
        if crop_type == "Highly Perishable":
            scores = durations  # Time is most critical
            score_label = "Time Priority Score"
        elif crop_type == "Non-Perishable":
            scores = distances  # Distance/fuel cost is most critical
            score_label = "Cost Priority Score"
        else:
            scores = [(d + t/10) for d, t in zip(distances, durations)]  # Balanced
            score_label = "Balanced Score"
        
        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = CHART_CONFIG['colors'][:len(routes)]
        bars = ax.barh(route_names, scores, color=colors)
        
        # Highlight best route
        best_idx = scores.index(min(scores))
        bars[best_idx].set_color('#FFD700')  # Gold color for best route
        
        ax.set_xlabel(score_label, fontsize=CHART_CONFIG['font_size'])
        ax.set_title(f'Route Optimization for {crop_type} Crops', 
                    fontsize=CHART_CONFIG['title_size'], fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Add score labels
        for i, (bar, score) in enumerate(zip(bars, scores)):
            label = "⭐ BEST" if i == best_idx else f"{score:.1f}"
            ax.text(bar.get_width() + max(scores)*0.01, bar.get_y() + bar.get_height()/2, 
                   label, va='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        return fig

# Convenience function for Streamlit
def display_chart(fig):
    """Display matplotlib figure in Streamlit"""
    if fig:
        st.pyplot(fig)
        plt.close(fig)  # Prevent memory leaks
    else:
        st.error("Unable to generate chart")