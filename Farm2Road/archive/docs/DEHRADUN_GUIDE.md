# 🗺️ Dehradun Route Optimizer - Quick Reference

## ✅ **What's New**

### 1. Search-Based Location Selection
Instead of clicking on the map, you can now:
- Select **Start Location** from dropdown (15 predefined Dehradun locations)
- Select **End Location** from dropdown (same locations)
- Or still click on map if you prefer

### 2. Restricted to Dehradun Area Only
- Map is centered on Dehradun
- Cannot pan outside Dehradun boundaries
- Zoom levels: 11-18 (city level detail)
- Coordinates restricted to Dehradun region

### 3. Available Locations in Dehradun

| Location | Description | Coordinates |
|----------|-------------|-------------|
| **Clock Tower** | City Center | 30.3165°N, 78.0322°E |
| **Rajpur Road** | Main commercial area | 30.3459°N, 78.0561°E |
| **Sahastradhara Road** | Tourist & residential | 30.3255°N, 78.0644°E |
| **ISBT Dehradun** | Bus terminal | 30.3255°N, 78.0436°E |
| **Mussoorie Diversion** | Highway junction | 30.4598°N, 78.0644°E |
| **Rispana** | Agricultural area | 30.2833°N, 78.0167°E |
| **Clement Town** | Cantonment area | 30.2667°N, 78.0167°E |
| **Patel Nagar** | Market area | 30.3344°N, 78.0403°E |
| **Rajendra Nagar** | Residential | 30.3031°N, 78.0417°E |
| **Ballupur** | Near Mussoorie Road | 30.3511°N, 78.0736°E |
| **Raipur** | Industrial area | 30.2833°N, 78.0500°E |
| **Premnagar** | Outskirts | 30.3833°N, 78.1000°E |
| **Selaqui** | Western Dehradun | 30.3667°N, 77.8833°E |
| **Vikasnagar Road** | Highway area | 30.4667°N, 77.7667°E |
| **Doiwala** | Southern region | 30.1833°N, 78.1167°E |

## 🚀 How to Use

### Step 1: Select Locations
1. **Start Location dropdown**: Choose your farm location
2. **End Location dropdown**: Choose market destination
3. Or click map for custom locations within Dehradun

### Step 2: Configure Crop
- Choose crop type (Perishable/Non-Perishable/Fragile/Bulk)
- Enter quantity in kg

### Step 3: Calculate Route
- Click "🚀 Calculate Optimal Route"
- See green path on map (Dijkstra's shortest path)
- View summary: distance, ETA, crop info

### Step 4: Weather Check (Optional)
- Click "⛈️ Reroute Based on Weather"
- If risky weather detected: red alternative route shown
- If weather clear: confirmation message

## 🗺️ Map Features

### Restrictions
- **Area**: Dehradun only (cannot pan outside)
- **Bounds**: 30.1°N to 30.6°N, 77.7°E to 78.3°E
- **Zoom**: Min 11, Max 18 (city-level detail)

### Visual Elements
- 🟢 **Green marker** = Start location
- 🔴 **Red marker** = End location
- 🟢 **Green path** = Optimal route
- 🔴 **Red path** = Weather-safe alternative

## 📊 Example Routes

### Example 1: Farm to Market
- **Start**: Rispana (agricultural area)
- **End**: Patel Nagar (market)
- **Distance**: ~8-10 km
- **Use case**: Daily vegetable delivery

### Example 2: Long Distance
- **Start**: Selaqui (western farms)
- **End**: Mussoorie Diversion (highway market)
- **Distance**: ~25-30 km
- **Use case**: Wholesale transport

### Example 3: City Routes
- **Start**: Clement Town
- **End**: Clock Tower (city center)
- **Distance**: ~6-8 km
- **Use case**: Local distribution

## 💡 Tips

1. **Use Dropdowns**: Faster than clicking map
2. **Common Routes**: Clock Tower, ISBT, Rajpur Road are major markets
3. **Agricultural Areas**: Rispana, Doiwala, Selaqui are farm areas
4. **Check Weather**: Always check for routes > 15km
5. **Perishable Goods**: System will optimize for speed automatically

## 🎯 App Running At

**Local**: http://localhost:8504

## ✨ Features

✅ 15 predefined Dehradun locations  
✅ Dropdown search for quick selection  
✅ Map restricted to Dehradun only  
✅ Real-time routing with Dijkstra's algorithm  
✅ Weather-aware rerouting  
✅ Crop-specific optimization  
✅ Clean, farmer-friendly UI  

---

**Perfect for Dehradun farmers! 🚜🌾**
