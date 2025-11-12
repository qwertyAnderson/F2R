# How to Use Multiple Route Feature - Quick Guide

## Step-by-Step Instructions

### Step 1: Select Start and End Locations
1. In the right panel, use the dropdown menus:
   - **Start Location (Farm)**: Choose your starting point (e.g., "Clock Tower")
   - **End Location (Market)**: Choose your destination (e.g., "Mussoorie Diversion")
2. You'll see ✓ checkmarks when both are selected

### Step 2: Set Crop Parameters (Optional)
- **Crop Type**: Select from:
  - Highly Perishable (fastest routes)
  - Moderately Perishable
  - Non-Perishable
  - Fragile (slower, safer routes)
  - Bulk / Heavy
- **Quantity**: Enter produce weight in kg (1-10,000 kg)

### Step 3: Calculate Routes
1. Click the **"🚀 Calculate Optimal Route"** button
2. Wait 2-3 seconds for route calculation
3. The map will update showing multiple colored routes

### Step 4: View All Routes on Map
**What you'll see:**
- 🔴 **Red Route**: Shortest/Primary route (selected by default)
- 🟠 **Orange Route**: Alternative path 1
- 🟡 **Yellow Route**: Alternative path 2  
- 🟢 **Green Route**: Alternative path 3 (if available)

**Visual Indicators:**
- **Thick line** = Currently selected route
- **Thin line** = Available alternatives
- **Opacity**: Selected route is bright, others are semi-transparent

### Step 5: Compare Route Options
**Below the map, you'll find:**

```
┌─────────────────────────────────────────────────────────┐
│  🛣️ Available Routes - Click to Select                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [🔴 Direct Route (Shortest)]  [🟠 Via Eastern Path]    │
│  16.2 km • 0h 19m               18.7 km • 0h 22m         │
│  ✓ SELECTED                                              │
│                                                          │
│  [🟡 Via Western Path]          [🟢 Scenic Route]        │
│  19.5 km • 0h 23m               20.3 km • 0h 27m         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Step 6: Select a Different Route
1. **Click** on any route card (Orange, Yellow, or Green)
2. The map will instantly update:
   - Selected route becomes **thicker** and **brighter**
   - Previous route becomes **thinner** and **semi-transparent**
3. The route card shows **"✓ SELECTED"** badge

### Step 7: View Detailed Route Information

After selecting a route, scroll down to see:

**📊 Route Metrics:**
```
Distance: 18.7 km
Duration: 0h 22m
Data Source: Simulated
```

**🗺️ Route Path:**
- Total waypoints count
- **Expandable coordinate list**:
  - First 10 points (starting area)
  - Last 10 points (destination area)
  - Full lat/lon coordinates

**Example coordinate view:**
```
Start waypoints:
1. Lat: 30.316500, Lon: 78.032200
2. Lat: 30.323400, Lon: 78.038100
3. Lat: 30.330300, Lon: 78.044000
...

End waypoints:
19. Lat: 30.452700, Lon: 78.061300
20. Lat: 30.459800, Lon: 78.064400
```

## Understanding Route Types

### 🔴 Direct Route (Shortest)
- **Characteristics**: Most direct path
- **Best for**: Time-sensitive deliveries, perishable goods
- **Distance**: Baseline (shortest)
- **Speed**: Fastest

### 🟠 Via Eastern Path
- **Characteristics**: Curves eastward through route
- **Best for**: Avoiding western traffic/obstacles
- **Distance**: ~15% longer
- **Speed**: Moderate

### 🟡 Via Western Path  
- **Characteristics**: Curves westward through route
- **Best for**: Avoiding eastern congestion
- **Distance**: ~20% longer
- **Speed**: Moderate

### 🟢 Scenic Route
- **Characteristics**: More winding path
- **Best for**: Lower traffic, scenic drive
- **Distance**: ~25% longer
- **Speed**: Slower (more turns)

## Pro Tips

### ✨ Best Practices
1. **Compare distances** - Sometimes slightly longer routes save time
2. **Check duration** - Factor in road conditions (curves, turns)
3. **Consider crop type** - Match route to cargo:
   - Perishable → Shortest route
   - Fragile → Scenic route (fewer bumps)
   - Heavy → Direct route (efficiency)
4. **View waypoints** - Identify familiar landmarks along route
5. **Weather check** - Use "⛈️ Reroute Based on Weather" for safety

### 🎯 Quick Selection Guide
- **Fastest delivery?** → Use Red (Direct Route)
- **Avoid main roads?** → Try Orange or Yellow alternatives
- **Safer/calmer drive?** → Choose Green (Scenic Route)
- **Shortest distance?** → Always Red by default

## Troubleshooting

### Routes look similar?
- This is normal when API is unavailable
- Routes are algorithmically generated to show variations
- In production with real API, routes follow actual roads

### Can't see route differences?
- Zoom in on the map to see path variations
- Routes may overlap in certain areas
- Look at the waypoint coordinates for precise differences

### Route cards not updating?
- Ensure you clicked the button fully
- Check that both start/end locations are selected
- Try the "🔄 Reset" button and recalculate

## Example Use Case

**Scenario**: Transporting tomatoes from Clock Tower to Mussoorie Diversion

1. **Select Locations**:
   - Start: Clock Tower (City Center)
   - End: Mussoorie Diversion
   
2. **Set Parameters**:
   - Crop: Highly Perishable
   - Quantity: 500 kg
   
3. **Calculate & Compare**:
   - Red Route: 16.2 km, 19 min ← **CHOOSE THIS**
   - Orange: 18.7 km, 22 min
   - Yellow: 19.5 km, 23 min
   - Green: 20.3 km, 27 min
   
4. **Decision**: Select Red (shortest/fastest) for perishable cargo

---

## Summary

✅ **You now know how to:**
- Generate multiple route alternatives
- Compare routes visually on the map
- Select different routes by clicking
- View detailed path information
- Choose the best route for your needs

**Enjoy optimizing your farm-to-market transport! 🚜📦🗺️**
