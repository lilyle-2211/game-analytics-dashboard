# Deployment Guide for Streamlit Community Cloud

## BigQuery Authentication Setup

To deploy this dashboard to Streamlit Community Cloud with BigQuery access, follow these steps:

### 1. Create a Google Cloud Service Account

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to IAM & Admin > Service Accounts
3. Click "Create Service Account"
4. Give it a name like "streamlit-dashboard"
5. Grant the following roles:
   - BigQuery Data Viewer
   - BigQuery Job User
6. Create a JSON key file and download it

### 2. Configure Streamlit Community Cloud Secrets

1. In your Streamlit Community Cloud app settings, go to "Secrets"
2. Add the contents of your service account JSON file in this format:

```toml
[GOOGLE_CLOUD_CREDENTIALS]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

### 3. Deploy to Streamlit Community Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. The app will automatically deploy with BigQuery access

### 4. Demo Mode

If BigQuery credentials are not available, the dashboard will run in demo mode with sample data, allowing users to explore the interface and A/B testing calculators without requiring database access.

## Local Development

For local development, you can either:

1. **Use gcloud auth**: Run `gcloud auth application-default login`
2. **Use service account file**: Place your `service-account-key.json` in the project root
3. **Use browser auth**: The app will fall back to browser authentication if other methods fail

## Troubleshooting

- Ensure your service account has the correct BigQuery permissions
- Check that all credentials are properly formatted in the secrets
- Verify your project ID matches your BigQuery project
- The dashboard will show warnings instead of errors for authentication issues
