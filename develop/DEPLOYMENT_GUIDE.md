# SAHAYAK - GCP Deployment Guide

## Step-by-Step Google Cloud Platform Deployment

### Prerequisites
1. Google Cloud Platform account
2. Billing enabled on your GCP project
3. Google Cloud SDK installed on your local machine

### Step 1: Set Up Google Cloud SDK

1. **Install Google Cloud SDK:**
   ```bash
   # For macOS
   brew install google-cloud-sdk
   
   # For Windows/Linux - download from:
   # https://cloud.google.com/sdk/docs/install
   ```

2. **Initialize and authenticate:**
   ```bash
   gcloud init
   gcloud auth login
   ```

3. **Create a new project (or select existing):**
   ```bash
   gcloud projects create sahayak-ai-assistant --name="SAHAYAK AI Assistant"
   gcloud config set project sahayak-ai-assistant
   ```

4. **Enable required APIs:**
   ```bash
   gcloud services enable appengine.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

### Step 2: Prepare Your Application

1. **Navigate to your project directory:**
   ```bash
   cd /path/to/your/sahayak/project
   ```

2. **Verify you have these files:**
   ```
   ├── main.py                 # Flask web application
   ├── sahayak_analytics.py    # Core analytics engine
   ├── requirements.txt        # Python dependencies
   ├── app.yaml               # GCP App Engine configuration
   ├── templates/             # HTML templates
   │   ├── index.html
   │   ├── demo.html
   │   ├── upload.html
   │   └── about.html
   └── static/                # Static files (optional)
   ```

3. **Update environment variables in app.yaml:**
   ```yaml
   env_variables:
     SECRET_KEY: "your-secret-key-here"
     OPENAI_API_KEY: "your-api-key-here"
     OPENAI_BASE_URL: "your-api-base-url-here"
   ```

### Step 3: Deploy to Google App Engine

1. **Initialize App Engine:**
   ```bash
   gcloud app create --region=us-central1
   ```
   
   *Choose region closest to your users. For India, consider:*
   - `asia-south1` (Mumbai)
   - `asia-southeast1` (Singapore)

2. **Deploy your application:**
   ```bash
   gcloud app deploy
   ```
   
   *This will:*
   - Upload your code to GCP
   - Install dependencies from requirements.txt
   - Start your Flask application
   - Provide you with a URL

3. **View your deployed application:**
   ```bash
   gcloud app browse
   ```

### Step 4: Custom Domain (Optional)

1. **Add custom domain:**
   ```bash
   gcloud app domain-mappings create yourdomain.com
   ```

2. **Follow DNS configuration instructions provided by GCP**

### Step 5: Monitoring and Logs

1. **View application logs:**
   ```bash
   gcloud app logs tail -s default
   ```

2. **Monitor in GCP Console:**
   - Go to https://console.cloud.google.com
   - Navigate to App Engine > Services
   - Monitor traffic, errors, and performance

### Step 6: Environment Variables Management (Secure)

For production, manage sensitive data securely:

1. **Use Secret Manager:**
   ```bash
   gcloud services enable secretmanager.googleapis.com
   
   # Store API key securely
   echo "your-api-key" | gcloud secrets create openai-api-key --data-file=-
   ```

2. **Update app.yaml to use secrets:**
   ```yaml
   env_variables:
     SECRET_KEY: "your-secret-key"
   
   beta_settings:
     cloud_sql_instances: your-instance
   ```

### Common Commands

```bash
# Deploy updates
gcloud app deploy

# View logs
gcloud app logs tail -s default

# Check app status
gcloud app versions list

# Stop/Start versions
gcloud app versions stop VERSION_ID
gcloud app versions start VERSION_ID

# Set traffic allocation
gcloud app services set-traffic default --splits=VERSION_ID=1.0
```

### Estimated Costs

**Google App Engine Standard Environment:**
- Free tier: 28 frontend instance hours per day
- Additional instances: ~$0.05/hour
- Bandwidth: $0.12/GB

**For typical usage (educational):**
- Low traffic: $0-5/month
- Medium traffic: $5-25/month
- High traffic: $25-100/month

### Troubleshooting

1. **Build failures:**
   ```bash
   # Check build logs
   gcloud app logs tail -s default
   
   # Verify requirements.txt
   pip install -r requirements.txt
   ```

2. **Memory issues:**
   - Increase memory in app.yaml
   - Optimize image processing
   - Use external storage for large files

3. **API connectivity:**
   - Verify environment variables
   - Check API key permissions
   - Test API endpoints locally

### Security Best Practices

1. **API Keys:**
   - Use Secret Manager for sensitive data
   - Rotate keys regularly
   - Limit API key permissions

2. **Access Control:**
   - Use IAM roles
   - Enable audit logging
   - Set up monitoring alerts

3. **File Upload Security:**
   - Validate file types
   - Limit file sizes
   - Scan uploaded content

### Scaling Configuration

```yaml
# In app.yaml
automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6
  target_throughput_utilization: 0.6
  max_concurrent_requests: 80
```

### Next Steps After Deployment

1. **Test all functionality:**
   - Demo report generation
   - File upload
   - PDF download

2. **Monitor performance:**
   - Response times
   - Error rates
   - User engagement

3. **Gather feedback:**
   - Teacher usability
   - Report quality
   - Feature requests

### Support Resources

- **GCP Documentation:** https://cloud.google.com/appengine/docs
- **App Engine Pricing:** https://cloud.google.com/appengine/pricing
- **Status Page:** https://status.cloud.google.com

### Quick Deployment Checklist

- [ ] GCP project created and billing enabled
- [ ] APIs enabled (App Engine, Cloud Build)
- [ ] Environment variables configured in app.yaml
- [ ] All files present (main.py, requirements.txt, templates/)
- [ ] Dependencies tested locally
- [ ] App Engine initialized
- [ ] Application deployed
- [ ] Custom domain configured (if needed)
- [ ] Monitoring and logging set up
- [ ] Security best practices implemented

Your SAHAYAK application should now be live and accessible to teachers worldwide!