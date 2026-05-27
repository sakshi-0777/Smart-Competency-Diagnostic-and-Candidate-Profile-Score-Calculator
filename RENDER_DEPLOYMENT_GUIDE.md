# Render Deployment Guide

## Quick Start

This backend is optimized for deployment on Render's **512MB memory plan**.

### Prerequisites
- Render account (https://render.com)
- GitHub repository with this code
- MySQL database (local or remote)

---

## Step 1: Prepare the Repository

1. Ensure `requirements_optimized.txt` exists in `/backend/`
2. Ensure `Procfile` exists in `/backend/` with content:
   ```
   web: gunicorn -w 2 -b 0.0.0.0:$PORT -t 30 app:app
   ```

3. Update `app.py` database configuration:
   ```python
   # Change from localhost to your Render/external database
   db = mysql.connector.connect(
       host=os.getenv("DB_HOST", "localhost"),
       user=os.getenv("DB_USER", "root"),
       password=os.getenv("DB_PASSWORD", "root"),
       database=os.getenv("DB_NAME", "db11")
   )
   ```

---

## Step 2: Create Render Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:

   | Setting | Value |
   |---------|-------|
   | **Name** | smart-competency-backend |
   | **Environment** | Python 3 |
   | **Region** | Oregon (or closest to users) |
   | **Branch** | main |
   | **Build Command** | `pip install -r requirements_optimized.txt` |
   | **Start Command** | `gunicorn -w 2 -b 0.0.0.0:$PORT -t 30 app:app` |
   | **Plan** | Starter (512MB) or Free |

---

## Step 3: Configure Environment Variables

In Render dashboard, go to **Environment** and add:

```
DB_HOST=your-database-host.com
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=your-database-name
FLASK_ENV=production
PYTHONUNBUFFERED=true
```

Or use `render.yaml` at root level (see template provided).

---

## Step 4: Deploy

1. Click **"Deploy"** button
2. Monitor logs in real-time
3. Wait for "Live" status (usually 2-5 minutes)
4. Test endpoint: `https://your-service.onrender.com/`

---

## Step 5: Verify Deployment

```bash
# Check health
curl https://your-service.onrender.com/

# Check model status
curl https://your-service.onrender.com/model_status

# Test with data (if authenticated)
curl -X POST https://your-service.onrender.com/analyze_resume \
  -F resume=@resume.pdf
```

---

## Environment Variables Setup

### Database Configuration
```
DB_HOST=db.example.com
DB_USER=admin
DB_PASSWORD=secure_password
DB_NAME=smart_competency_db
```

### For Remote MySQL on Render
Use **Render PostgreSQL** or connect to external MySQL:
```
DB_HOST=mysql.example.com:3306
```

### Application Settings
```
FLASK_ENV=production
FLASK_DEBUG=false
JWT_SECRET_KEY=your-secret-key-here
PYTHONUNBUFFERED=true
```

---

## Memory Monitoring

### Check Memory Usage
1. Go to Render dashboard
2. Navigate to your service
3. Click **"Logs"**
4. Look for memory usage patterns

### If Running Out of Memory
Option A: **Reduce Workers**
```
Procfile: web: gunicorn -w 1 -b 0.0.0.0:$PORT app:app
```

Option B: **Upgrade Plan**
- From Starter (512MB) to Standard (1GB)
- Cost: ~$7/month additional

Option C: **Limit Dataset Size**
Edit `backend/model_pipeline.py`:
```python
if len(job_df) > 500:  # Reduce from 1000
    job_df = job_df.head(500)
```

---

## Deployment Checklist

- [ ] Repository has `requirements_optimized.txt`
- [ ] Repository has `Procfile` with correct start command
- [ ] `app.py` uses environment variables for database
- [ ] GitHub repository is connected to Render
- [ ] Build command: `pip install -r requirements_optimized.txt`
- [ ] Start command: `gunicorn -w 2 -b 0.0.0.0:$PORT -t 30 app:app`
- [ ] Environment variables configured
- [ ] Database is accessible from Render
- [ ] Deployment successful (status = "Live")
- [ ] Endpoints are responding

---

## Troubleshooting

### "Out of Memory" Error
```
RuntimeError: Cannot allocate memory
```
**Solution:**
1. Reduce gunicorn workers (`-w 1`)
2. Upgrade to Standard plan (1GB)
3. Reduce dataset size in model_pipeline.py

### "Module not found" Error
```
ModuleNotFoundError: No module named 'sentence_transformers'
```
**Solution:** Make sure to use `requirements_optimized.txt` (no sentence-transformers)

### "Database connection error"
```
mysql.connector.errors.ProgrammingError: 2003 (HY000)
```
**Solution:**
1. Verify DB_HOST, DB_USER, DB_PASSWORD
2. Ensure database is running and accessible
3. Check firewall rules for your Render IP

### "Port binding error"
```
Address already in use
```
**Solution:** Ensure Procfile uses `$PORT` variable:
```
web: gunicorn -b 0.0.0.0:$PORT app:app
```

### "Timeout during startup"
```
Worker timeout
```
**Solution:** Increase timeout or reduce data loading:
```
web: gunicorn -w 2 -b 0.0.0.0:$PORT -t 60 app:app
```

---

## Performance Tips

### 1. Use Regional Database
- Place MySQL in same region as Render service
- Reduces latency significantly

### 2. Enable CORS Caching
```python
@app.after_request
def set_cache(response):
    response.cache_control.max_age = 3600
    return response
```

### 3. Monitor and Scale
- Monitor via Render dashboard
- Consider auto-scaling if traffic increases
- Use CDN for static assets

### 4. Database Optimization
- Add indices on job_title, job_description
- Implement query pagination
- Cache frequently accessed data

---

## Costs

**Render Starter Plan (512MB):**
- First 750 hours/month: **FREE**
- Beyond 750 hours: ~$0.05/hour
- Total monthly cost: **$0 - $5**

**Render Standard Plan (1GB):**
- Monthly: ~$7

**Recommendation:** Start with Starter (Free tier), upgrade if needed.

---

## Advanced: Using render.yaml

Instead of manual configuration, use `render.yaml`:

```yaml
services:
  - type: web
    name: smart-competency-backend
    env: python
    runtime: python-3.11
    buildCommand: pip install -r requirements_optimized.txt
    startCommand: gunicorn -w 2 -b 0.0.0.0:$PORT app:app
```

Deploy with:
```bash
git push origin main  # Render auto-deploys
```

---

## Post-Deployment

1. **Monitor Logs**
   ```bash
   # View in Render dashboard
   Services → Logs
   ```

2. **Test API Endpoints**
   - GET `/` - Health check
   - GET `/model_status` - Model status
   - POST `/analyze_resume` - Resume analysis
   - POST `/search_jobs` - Job search

3. **Setup Frontend**
   - Update API URL in frontend `.env`:
     ```
     VITE_API_URL=https://your-service.onrender.com
     ```

4. **Monitor Performance**
   - Check response times
   - Monitor memory usage
   - Review error logs

---

## Support & Resources

- **Render Documentation**: https://render.com/docs
- **Gunicorn Settings**: https://docs.gunicorn.org/
- **Port Binding**: https://render.com/docs/web-services#port-binding
- **Environment Variables**: https://render.com/docs/environment-variables

