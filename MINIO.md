# MinIO Setup for Development

MinIO provides S3-compatible storage for local development without requiring AWS credentials or incurring costs.

## Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
npm run minio
```

This command will:
1. Start the MinIO container
2. Create the `ctfd-uploads` bucket
3. Configure public access for presigned URLs

✅ Done! Your MinIO storage is ready.

### Option 2: Manual Setup

If the automated setup fails:

1. **Start MinIO container:**
   ```bash
   docker compose up -d minio
   ```

2. **Open MinIO Console:** http://localhost:9001

3. **Login with default credentials:**
   - Username: `ctfd-dev`
   - Password: `ctfd-dev-secret-key-12345`

4. **Create bucket:**
   - Click "Create Bucket"
   - Name it `ctfd-uploads`
   - Keep default settings

5. **Set bucket policy:**
   - Click on the bucket
   - Go to "Access Policy"
   - Set to "Public" or "Download"

## Configuration

### For Team Members

Add these fields to your `.env.dev` file:

```bash
# MinIO Configuration
MINIO_ACCESS_KEY=ctfd-dev
MINIO_SECRET_KEY=ctfd-dev-secret-key-12345
MINIO_ENDPOINT=http://minio:9000
MINIO_BUCKET=ctfd-uploads

# AWS S3 Configuration (if you want to test with real AWS)
AWS_S3_ACCESS_KEY_ID=your-aws-key-here
AWS_S3_SECRET_ACCESS_KEY=your-aws-secret-here
AWS_S3_BUCKET_NAME=your-bucket-name
```

### Default Credentials

The docker-compose.yaml file sets up MinIO with these default credentials:
- **Username:** ctfd-dev
- **Password:** ctfd-dev-secret-key-12345

These are shared development credentials - everyone uses the same ones, but data is isolated per developer's machine.

## Usage

### Starting Development

```bash
# Default (uses MinIO for storage)
npm start

# Explicitly use AWS S3 instead
npm run start-aws

# Production (always uses AWS)
npm run start-prod
```

The `npm start` command now defaults to using MinIO. To test with real AWS S3, use `npm run start-aws`.

## How It Works

The backend service (`s3_upload_service.py`) checks the `USE_MINIO` environment variable:

1. **USE_MINIO=true** → Uses MinIO (local storage)
2. **USE_MINIO=false** → Uses AWS S3 (cloud storage)
3. **No credentials configured** → File uploads disabled gracefully

### Storage Fallback Order

1. If `USE_MINIO=true`:
   - Try MinIO first
   - Fall back to AWS if MinIO not configured
   - Disable uploads if neither configured

2. If `USE_MINIO=false` or not set:
   - Use AWS S3
   - Disable uploads if not configured

## Verifying Setup

### Test Upload

After setup, test by uploading an image to a support ticket:

1. Create a support ticket
2. Upload a WebP image
3. Check the console logs for: `"File uploaded successfully to minio"`

### MinIO Web Console

Access the MinIO dashboard at: http://localhost:9001

Here you can:
- View uploaded files
- Browse bucket contents
- Monitor storage usage
- Download files directly

## Troubleshooting

### "Connection refused" Error

```bash
# Check if MinIO is running
docker ps | grep minio

# If not running, start it
docker compose up -d minio

# Restart if needed
docker compose restart minio
```

### "Bucket not found" Error

```bash
# Run the setup script again
npm run minio

# Or create manually via web console
```

### "Access denied" on Presigned URLs

The bucket needs public read access for presigned URLs to work:

```bash
docker exec ng-minio mc anonymous set download local/ctfd-uploads
```

### MinIO Container Won't Start

Check for port conflicts:
```bash
# Check if ports 9000 or 9001 are in use
lsof -i :9000
lsof -i :9001

# Kill conflicting processes or change MinIO ports in docker-compose.yaml
```

## Data Persistence

MinIO data is stored in `.data/minio/` directory:
- This directory is git-ignored
- Data persists across container restarts
- Each developer has their own isolated storage

To reset MinIO completely:
```bash
docker compose down minio
rm -rf .data/minio
docker compose up -d minio
npm run minio  # Re-run setup
```

## Production Deployment

In production, you'll typically use real AWS S3. The plugin supports both:

1. **Self-hosted with MinIO:**
   - Deploy MinIO in production
   - Use same configuration approach
   - Consider MinIO clusters for high availability

2. **Cloud with AWS S3:**
   - Set `USE_MINIO=false` or remove it
   - Configure real AWS credentials
   - Ensure S3 bucket exists with proper permissions

## Security Notes

⚠️ **Development Only:** The default credentials are for development only. In production:
- Use strong, unique credentials
- Store credentials securely (environment variables, secrets manager)
- Enable MinIO TLS/HTTPS
- Configure proper access policies

## Additional Resources

- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [MinIO Python SDK](https://min.io/docs/minio/linux/developers/python/API.html)
- [S3 Compatibility](https://min.io/docs/minio/linux/reference/s3-compatibility.html)