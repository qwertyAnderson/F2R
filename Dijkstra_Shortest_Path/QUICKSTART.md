# 🚀 QUICK START GUIDE

## Get Your App Running in 3 Steps

### Step 1: Install Dependencies

Open PowerShell in your project folder and run:

```powershell
pip install -r requirements_new.txt
```

Wait for all packages to install (~2 minutes).

### Step 2: Run the Application

```powershell
streamlit run app_new.py
```

### Step 3: Use the App

Your browser will open automatically to `http://localhost:8501`

1. **Click the map** to select start location (your farm)
2. **Click again** to select end location (market)
3. **Choose crop type** from dropdown
4. **Enter quantity** in kg
5. **Click "Calculate Optimal Route"** button
6. **Optional**: Click "Reroute Based on Weather" to check weather

---

## 📱 What You'll See

✅ **Clean interactive map** (no clutter)
✅ **Green marker** = Start location
✅ **Red marker** = End location  
✅ **Green path** = Optimal route (Dijkstra's algorithm)
✅ **Summary box** (top-right) with crop info and ETA
✅ **Red path** = Alternative route (if weather is bad)

---

## 🧪 Test Example

Try these coordinates:

**Start**: Click near Delhi area (center of map)
**End**: Click 200-300km away in any direction
**Crop**: Select "Highly Perishable"
**Quantity**: Enter 500 kg

Click "Calculate Optimal Route" and watch the magic happen! ✨

---

## ⚡ Features

- **No CSV uploads** - Everything is real-time
- **No validation messages** - Clean UI only
- **Live weather data** - Automatically checked
- **Mobile-friendly** - Works on phones
- **Dijkstra's algorithm** - Guaranteed shortest path

---

## 🆘 Troubleshooting

**Problem**: Map not loading?
**Solution**: Check your internet connection

**Problem**: "Calculate" button disabled?
**Solution**: Make sure you clicked BOTH start and end locations

**Problem**: Dependencies won't install?
**Solution**: Make sure you have Python 3.8 or higher:
```powershell
python --version
```

---

## 🎯 Next Steps

1. ✅ Run the app locally (you're here!)
2. 📝 Customize for your needs
3. 🚀 Deploy to Streamlit Cloud (see DEPLOYMENT.md)
4. 🌍 Share with farmers!

---

**Questions?** Check README_NEW.md for detailed docs.

**Ready to deploy?** Check DEPLOYMENT.md for cloud hosting.

---

**Enjoy your farmer-friendly route optimizer! 🚜**
