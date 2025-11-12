# 🚀 Deployment Guide

## Running Locally

### Quick Start

1. **Install dependencies**:
   ```powershell
   pip install -r requirements_new.txt
   ```

2. **Run the app**:
   ```powershell
   streamlit run app_new.py
   ```

3. **Access the app**:
   - Open browser to: http://localhost:8501

## Deploying to Streamlit Cloud (Free)

### Step 1: Prepare Your Repository

1. Push your code to GitHub
2. Ensure these files are in your repo:
   - `app_new.py`
   - `requirements_new.txt`
   - `.streamlit/secrets.toml` (add to .gitignore)
   - All `services/` and `components/` folders

### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file: `app_new.py`
6. Click "Deploy"

### Step 3: Configure Secrets

In Streamlit Cloud dashboard:

1. Go to app settings
2. Click "Secrets"
3. Add:
   ```toml
   OPENROUTE_API_KEY = "your_api_key_here"
   ```

## Alternative Deployment Options

### Heroku

1. Create `Procfile`:
   ```
   web: streamlit run app_new.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Docker

1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements_new.txt .
   RUN pip install -r requirements_new.txt
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app_new.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. Build and run:
   ```bash
   docker build -t farm-route-optimizer .
   docker run -p 8501:8501 farm-route-optimizer
   ```

### AWS EC2

1. Launch EC2 instance (Ubuntu)
2. SSH into instance
3. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install -r requirements_new.txt
   ```
4. Run with nohup:
   ```bash
   nohup streamlit run app_new.py --server.port=8501 &
   ```
5. Configure security group to allow port 8501

## Environment Variables

For production, set these environment variables:

```bash
export OPENROUTE_API_KEY="your_key_here"
```

## Performance Optimization

### Caching

The app uses `@st.cache_resource` for:
- Service initialization
- Map rendering

### Rate Limiting

- OpenRouteService: 2000 requests/day (free tier)
- Open-Meteo: Unlimited (free)

### Fallback Strategy

If APIs fail:
- Map service falls back to direct line calculation
- Weather service returns default safe conditions

## Monitoring

### Streamlit Cloud

- Built-in analytics
- View logs in dashboard
- Monitor API usage

### Custom Monitoring

Add to `app_new.py`:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log route calculations
logger.info(f"Route calculated: {distance}km")
```

## Security Checklist

- [ ] API keys in secrets, not code
- [ ] `.streamlit/secrets.toml` in `.gitignore`
- [ ] HTTPS enabled (automatic on Streamlit Cloud)
- [ ] Input validation for coordinates
- [ ] Rate limiting on API calls

## Troubleshooting Deployment

**App won't start?**
- Check Python version (3.8+)
- Verify all dependencies in requirements_new.txt
- Check logs for errors

**API errors?**
- Verify API keys are set correctly
- Check rate limits
- Test APIs independently

**Map not rendering?**
- Ensure streamlit-folium is installed
- Check browser console for errors
- Verify internet connection

## Scaling

For high traffic:

1. **Use Streamlit Cloud Teams** ($25/month)
   - More resources
   - Better performance

2. **Deploy on Kubernetes**
   - Horizontal scaling
   - Load balancing

3. **Upgrade API plans**
   - OpenRouteService Premium
   - Consider MapBox for production

## Cost Estimates

**Free Tier (Recommended for testing):**
- Streamlit Cloud: Free (1 public app)
- OpenRouteService: Free (2000 req/day)
- Open-Meteo: Free (unlimited)
- **Total: $0/month**

**Production:**
- Streamlit Cloud Teams: $25/month
- OpenRouteService Premium: €50/month (40k req/day)
- **Total: ~$80/month**

## Support

- Streamlit: https://discuss.streamlit.io
- OpenRouteService: https://ask.openrouteservice.org
- Open-Meteo: https://github.com/open-meteo/open-meteo

---

**Ready to deploy! 🚀**
