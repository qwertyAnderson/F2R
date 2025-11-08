# 🎯 VISUAL USAGE GUIDE

## Step-by-Step Guide with Screenshots

---

## 🚀 STEP 1: Launch the App

**Command**:
```powershell
python -m streamlit run app_new.py
```

**Result**: Browser opens to `http://localhost:8501`

**What You See**:
```
╔════════════════════════════════════════════════════════╗
║  🚜 Farm-to-Market Route Optimizer                     ║
╠════════════════════════════════════════════════════════╣
║                                                         ║
║  ┌────────────────────────┐  ┌──────────────────────┐ ║
║  │                        │  │  📍 Route Details    │ ║
║  │                        │  │                      │ ║
║  │      🗺️  MAP          │  │  How to use:         │ ║
║  │   (India Centered)     │  │  1. Click map for    │ ║
║  │                        │  │     Start            │ ║
║  │                        │  │  2. Click map for    │ ║
║  │     (Click to          │  │     End              │ ║
║  │      select)           │  │  3. Select crop      │ ║
║  │                        │  │  4. Calculate route  │ ║
║  │                        │  │                      │ ║
║  │                        │  │  Crop Type           │ ║
║  │                        │  │  [Moderately        ▼] ║
║  │                        │  │                      │ ║
║  │                        │  │  Produce Quantity    │ ║
║  │                        │  │  [_____100_____] kg  │ ║
║  │                        │  │                      │ ║
║  │                        │  │  👆 Click map for    │ ║
║  │                        │  │     start            │ ║
║  │                        │  │                      │ ║
║  └────────────────────────┘  └──────────────────────┘ ║
║                                                         ║
╚════════════════════════════════════════════════════════╝
```

---

## 📍 STEP 2: Select Start Location

**Action**: Click anywhere on the map (your farm location)

**What Happens**:
- Green marker appears
- Left panel shows: "✓ Start location selected"

**Visual**:
```
╔════════════════════════════════════════════════════════╗
║  🚜 Farm-to-Market Route Optimizer                     ║
╠════════════════════════════════════════════════════════╣
║                                                         ║
║  ┌────────────────────────┐  ┌──────────────────────┐ ║
║  │                        │  │  📍 Route Details    │ ║
║  │      🗺️  MAP          │  │                      │ ║
║  │                        │  │  ✅ Start location   │ ║
║  │        📍 ← GREEN      │  │     selected         │ ║
║  │     START MARKER       │  │                      │ ║
║  │                        │  │  👆 Click map for    │ ║
║  │                        │  │     end              │ ║
║  │                        │  │                      │ ║
║  │                        │  │  Crop Type           │ ║
║  │                        │  │  [Moderately        ▼] ║
║  │                        │  │                      │ ║
║  │                        │  │  Quantity: 100 kg    │ ║
║  └────────────────────────┘  └──────────────────────┘ ║
╚════════════════════════════════════════════════════════╝
```

---

## 📍 STEP 3: Select End Location

**Action**: Click another location on map (market location)

**What Happens**:
- Red marker appears
- Both locations now selected
- "Calculate" button activates

**Visual**:
```
╔════════════════════════════════════════════════════════╗
║  🚜 Farm-to-Market Route Optimizer                     ║
╠════════════════════════════════════════════════════════╣
║                                                         ║
║  ┌────────────────────────┐  ┌──────────────────────┐ ║
║  │      🗺️  MAP          │  │  📍 Route Details    │ ║
║  │                        │  │                      │ ║
║  │    📍 START (Green)    │  │  ✅ Start selected   │ ║
║  │          ↓             │  │  ✅ End selected     │ ║
║  │          ↓             │  │                      │ ║
║  │    📍 END (Red)        │  │  Crop Type           │ ║
║  │                        │  │  [Highly Perishable▼] ║
║  │                        │  │                      │ ║
║  │                        │  │  Quantity            │ ║
║  │                        │  │  [_____500_____] kg  │ ║
║  │                        │  │                      │ ║
║  │                        │  │  ──────────────────  │ ║
║  │                        │  │  [🚀 Calculate Route] │ ║
║  └────────────────────────┘  └──────────────────────┘ ║
╚════════════════════════════════════════════════════════╝
```

---

## 🌾 STEP 4: Configure Crop Details

**Actions**:
1. Select crop type from dropdown
2. Enter quantity in kg

**Options**:
- Highly Perishable (tomatoes, leafy greens)
- Moderately Perishable (fruits)
- Non-Perishable (grains, pulses)
- Fragile (eggs, glass jars)
- Bulk / Heavy (potatoes, rice bags)

---

## 🚀 STEP 5: Calculate Route

**Action**: Click "🚀 Calculate Optimal Route" button

**What Happens**:
1. Spinner shows "Calculating optimal route..."
2. Backend calls OpenRouteService API
3. Dijkstra's algorithm computes shortest path
4. Green route line appears on map
5. Summary box appears in top-right

**Visual After Calculation**:
```
╔════════════════════════════════════════════════════════╗
║  🚜 Farm-to-Market Route Optimizer                     ║
║                                    ┌────────────────┐  ║
║                                    │ 📦 Route       │  ║
║  ┌────────────────────────┐        │    Summary     │  ║
║  │      🗺️  MAP          │        │                │  ║
║  │                        │        │ Crop: Highly   │  ║
║  │    📍 START            │        │   Perishable   │  ║
║  │      ║  ← GREEN        │        │ Qty: 500 kg    │  ║
║  │      ║    ROUTE        │        │ Distance:      │  ║
║  │      ║    LINE         │        │   45.2 km      │  ║
║  │      ║                 │        │ ETA: 1h 20m    │  ║
║  │      ▼                 │        └────────────────┘  ║
║  │    📍 END              │  ┌──────────────────────┐ ║
║  │                        │  │  ──────────────────  │ ║
║  │  ✅ Optimal route      │  │  [⛈️ Reroute Based  │ ║
║  │     calculated!        │  │     on Weather]      │ ║
║  └────────────────────────┘  └──────────────────────┘ ║
╚════════════════════════════════════════════════════════╝
```

---

## ⛈️ STEP 6: Weather-Based Reroute (Optional)

**Action**: Click "⛈️ Reroute Based on Weather" button

**Scenario A - Good Weather**:
```
╔════════════════════════════════════════════════════════╗
║  ✅ Weather Clear                                       ║
║  Current route is optimal based on weather conditions. ║
╚════════════════════════════════════════════════════════╝
```

**Scenario B - Bad Weather**:
```
╔════════════════════════════════════════════════════════╗
║  ⚠️ Weather Alert                                       ║
║  Heavy rain detected. Alternative route shown in red.  ║
╚════════════════════════════════════════════════════════╝

  ┌────────────────────────┐
  │      🗺️  MAP          │
  │                        │
  │    📍 START            │
  │      ║  ← GREEN        │  Original route
  │      ║                 │
  │      ╬════════         │  ← RED alternative route
  │      ║                 │
  │      ▼                 │
  │    📍 END              │
  └────────────────────────┘
```

---

## 🔄 STEP 7: Reset (Optional)

**Action**: Click "🔄 Reset" button

**What Happens**:
- Clears all markers
- Resets selections
- Returns to initial state
- Ready for new route

---

## 📱 MOBILE VIEW

On mobile devices, the UI adapts:

```
┌──────────────────────┐
│  🚜 Route Optimizer  │
├──────────────────────┤
│                      │
│     🗺️ MAP          │
│      (Full Width)    │
│                      │
│    📍 Start          │
│      ║               │
│      ▼               │
│    📍 End            │
│                      │
├──────────────────────┤
│  📍 Route Details    │
│  Crop Type: [______▼]│
│  Quantity: [_____] kg│
│  [🚀 Calculate Route] │
│  [⛈️ Weather Reroute] │
│  [🔄 Reset]          │
└──────────────────────┘
    ┌──────────────┐
    │ 📦 Summary   │
    │ Fixed Bottom │
    └──────────────┘
```

---

## 🎨 COLOR CODING

### Markers
- 🟢 **Green** = Start location (farm)
- 🔴 **Red** = End location (market)

### Routes
- 🟢 **Green Line** = Optimal route (Dijkstra's algorithm)
- 🔴 **Red Line** = Weather-safe alternative route

### Messages
- ✅ **Green Box** = Success / Good weather
- ⚠️ **Yellow Box** = Weather warning
- ℹ️ **Blue Box** = Information

---

## 🎯 UI ELEMENTS EXPLAINED

### Summary Box (Top-Right)
```
┌─────────────────┐
│ 📦 Route Summary│  ← Title
├─────────────────┤
│ Crop: Type      │  ← Your selection
│ Quantity: XX kg │  ← Amount entered
│ Distance: XX km │  ← Calculated by API
│ ETA: Xh XXm     │  ← Crop-optimized time
└─────────────────┘
```

### Input Panel (Right Sidebar)
```
┌──────────────────────┐
│ 📍 Route Details     │
├──────────────────────┤
│ How to use:          │  ← Instructions
│ 1. Click for start   │
│ 2. Click for end     │
│ 3. Select crop       │
│ 4. Calculate         │
├──────────────────────┤
│ Crop Type            │
│ [Dropdown      ▼]    │  ← 5 options
├──────────────────────┤
│ Produce Quantity     │
│ [_____100_____] kg   │  ← Number input
├──────────────────────┤
│ ✅ Start selected    │  ← Status
│ ✅ End selected      │
├──────────────────────┤
│ [🚀 Calculate Route] │  ← Main action
├──────────────────────┤
│ [⛈️ Weather Reroute] │  ← Optional
├──────────────────────┤
│ [🔄 Reset]           │  ← Start over
└──────────────────────┘
```

---

## 💡 PRO TIPS

### Tip 1: Zoom Controls
- **+** button = Zoom in
- **-** button = Zoom out
- **Mouse scroll** = Quick zoom
- **Drag** = Pan around map

### Tip 2: Selecting Locations
- Click once = Start location
- Click twice = End location
- Want to change? Click "Reset"

### Tip 3: Crop Selection
- **Highly Perishable** → Fastest route, higher speed
- **Fragile** → Safer route, lower speed
- **Bulk/Heavy** → Adjusted for weight

### Tip 4: Weather Check
- Always check weather for long distances
- Red route = Safer alternative
- Green toast = Current route is safe

---

## ⚡ KEYBOARD SHORTCUTS

- **F11** = Fullscreen mode
- **Ctrl + R** = Refresh app
- **Esc** = Exit fullscreen

---

## 🎬 EXAMPLE WORKFLOW

### Real Example: Delhi to Jaipur

1. **Launch**: `python -m streamlit run app_new.py`

2. **Start**: Click near Delhi (28.6°N, 77.2°E)
   - Green marker appears

3. **End**: Click near Jaipur (26.9°N, 75.8°E)
   - Red marker appears

4. **Configure**:
   - Crop: "Highly Perishable"
   - Quantity: 500 kg

5. **Calculate**: Click button
   - Route appears in ~2 seconds
   - Distance: ~280 km
   - ETA: ~4h 30m

6. **Weather**: Click weather button
   - Checks real-time weather
   - Shows result

7. **Success**: Route ready for farmer!

---

## ✨ WHAT MAKES IT SPECIAL

### 1. No Training Required
- Farmers can use immediately
- Intuitive map interaction
- Clear visual feedback

### 2. Real-Time Data
- Live routing from OpenRouteService
- Current weather from Open-Meteo
- Dynamic calculations

### 3. Smart Optimization
- Dijkstra's algorithm (proven optimal)
- Crop-specific adjustments
- Weather-aware decisions

### 4. Production Ready
- Error handling (fallbacks)
- Clean code structure
- Scalable architecture

---

## 🎉 YOU'RE READY!

Now you know:
- ✅ How to launch the app
- ✅ How to select locations
- ✅ How to configure crop details
- ✅ How to calculate routes
- ✅ How to check weather
- ✅ What each UI element does

**Go ahead and try it!** 🚜✨

---

**Questions?** Check QUICKSTART.md  
**Need more?** Check README_NEW.md  
**Want to deploy?** Check DEPLOYMENT.md
