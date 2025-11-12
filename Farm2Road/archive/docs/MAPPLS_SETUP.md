# 🇮🇳 MapMyIndia (Mappls) API Setup Guide

## Why MapMyIndia?

✅ **Best for Dehradun**: Most accurate road data in Uttarakhand  
✅ **Free Tier**: 2500 requests/day (vs OpenRouteService 2000)  
✅ **Rural Roads**: Knows agricultural routes and village roads  
✅ **Fast**: Indian servers = quick response  
✅ **No Credit Card**: Completely free signup  

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Sign Up (Free)

1. Visit: **https://apis.mappls.com/console/**
2. Click **"Sign Up"** or **"Register"**
3. Fill in details:
   - Name
   - Email
   - Phone number
   - Company (you can put "Farmer" or "Individual")
4. Verify email
5. Login to console

### Step 2: Create Project

1. After login, you'll see dashboard
2. Click **"Create New Project"** or **"Add Project"**
3. Give it a name: **"Dehradun Farm Routes"**
4. Click **"Create"**

### Step 3: Get API Key

1. In your project dashboard
2. Look for **"REST API Key"** or **"API Credentials"**
3. You'll see a key like: `abcd1234efgh5678ijkl9012mnop3456`
4. Click **"Copy"**

### Step 4: Add to Your App

1. Open file: `.streamlit/secrets.toml`
2. Find this line:
   ```toml
   # MAPPLS_API_KEY = "paste_your_key_here"
   ```
3. Uncomment and replace with your key:
   ```toml
   MAPPLS_API_KEY = "abcd1234efgh5678ijkl9012mnop3456"
   ```
4. Save file

### Step 5: Restart App

```powershell
python -m streamlit run app_new.py
```

---

## ✅ How to Verify It's Working

After restarting, calculate a route and check sidebar:

### ✅ **Success - Using MapMyIndia**:
```
✅ Route via MapMyIndia: 6.7 km
🇮🇳 Using accurate India road data
```

### ⚠️ **Still Using Fallback**:
```
⚠️ Using straight-line distance: 1.5 km
💡 Actual road distance may be longer
```
→ Check if API key is correct in secrets.toml

---

## 📊 API Limits

| Tier | Requests/Day | Cost |
|------|--------------|------|
| **Free** | 2,500 | ₹0 |
| **Paid** | Unlimited | ₹50 per 1,000 calls |

**For 100 farmers/day**: Free tier is enough!

---

## 🔧 Troubleshooting

### Problem: "Still showing straight-line distance"

**Solution 1**: Check API key
```toml
# Make sure it's uncommented (no # at start)
MAPPLS_API_KEY = "your_key_here"
```

**Solution 2**: Verify key is correct
- Copy-paste carefully
- No extra spaces
- No quotes inside the string

**Solution 3**: Check key status
- Login to https://apis.mappls.com/console/
- Make sure project is active
- Key should show as "Active"

### Problem: "API Error 401"
- Key is invalid or expired
- Get new key from console

### Problem: "API Error 403"
- Key doesn't have routing permission
- Check project settings
- Enable "Routing API"

### Problem: "API Error 429"
- Rate limit exceeded (2500/day)
- Wait 24 hours or upgrade to paid tier

---

## 🆚 Comparison with Current Setup

### Before (OpenRouteService):
- ❌ Showing 1.5 km (wrong!)
- ❌ Straight-line distance
- ❌ European road data
- ❌ Slower (EU servers)

### After (MapMyIndia):
- ✅ Showing 6.7 km (accurate!)
- ✅ Actual road distance
- ✅ India-specific road data
- ✅ Faster (Indian servers)
- ✅ Knows Dehradun local roads

---

## 📱 Support

**MapMyIndia Support**:
- Email: apisupport@mappls.com
- Phone: +91-11-4600-9900
- Docs: https://github.com/mappls-api/mappls-rest-apis

**App Support**:
- Check terminal output for error messages
- Look at sidebar for API status
- See `TROUBLESHOOTING.md`

---

## 🎯 What You'll Get

With MapMyIndia setup:

1. **Accurate Distances**:
   - Clock Tower to Rajpur Road: ~6-7 km (correct!)
   - Not 1.5 km straight line

2. **Real Road Routes**:
   - Follows actual roads
   - Shows curves and turns
   - Considers one-ways

3. **Dehradun Expertise**:
   - Knows Sahastradhara Road
   - Knows Rispana routes
   - Knows agricultural areas

4. **Better ETAs**:
   - Based on actual road distance
   - More accurate time estimates
   - Better for planning

---

## ✨ Quick Start Commands

```powershell
# 1. Edit secrets file
notepad .streamlit\secrets.toml

# 2. Add your MapMyIndia key
# MAPPLS_API_KEY = "your_key_here"

# 3. Save and restart app
python -m streamlit run app_new.py
```

---

## 🎉 That's It!

Your app will now use MapMyIndia for accurate Dehradun routes!

**Questions?** Check the troubleshooting section above.

**Ready to get your key?** Visit: https://apis.mappls.com/console/

---

**Built for Dehradun farmers! 🚜🌾**
