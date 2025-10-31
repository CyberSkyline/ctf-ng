# MinIO Setup for Development

MinIO provides S3-compatible storage for local development without requiring AWS credentials or incurring costs.

## Quick Setup

### Option 1: Initial Project Setup (Recommended)

If you're setting up the project for the first time:

```bash
./install.sh
```

The install script will prompt you to set up MinIO automatically. Choose "yes" when asked:
- "Would you like to set up MinIO for local S3-compatible storage?"

This will:
1. Start the MinIO container
2. Create the `ctfd-attachments` bucket
3. Configure public access for downloads

### Option 2: Standalone Setup

If you skipped MinIO during install or need to set it up later:

```bash
npm run minio
```

This command will:
1. Start the MinIO container
2. Create the bucket
3. Configure public access

### Option 3: Manual Setup

If the automated setup fails:

1. **Start MinIO container:**
   ```bash
   docker compose up -d minio
   ```

2. **Open MinIO Console:** http://localhost:9001

3. **Login with default credentials:**
   - Username: `minioadmin`
   - Password: `minioadmin`

4. **Create bucket:**
   - Click "Create Bucket"
   - Name it `ctfd-attachments`
   - Keep default settings

5. **Set bucket policy:**
   - Click on the bucket
   - Go to "Access Policy"
   - Set to "Public" or "Download"

## Configuration

Configuration is automatically set in `conf/ctfd/.env.default.dev`:

```bash
# AWS S3 Configuration (for production)
AWS_S3_ACCESS_KEY_ID=-
AWS_S3_SECRET_ACCESS_KEY=-
AWS_S3_BUCKET_NAME=-

# MinIO Configuration (for development)
USE_MINIO=true
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_ENDPOINT=http://minio:9000
MINIO_BUCKET=ctfd-attachments
```

To customize for your environment, copy `.env.default.dev` to `.env.dev`:

```bash
cp conf/ctfd/.env.default.dev .env.dev
```

Then edit `.env.dev` with your preferred values.

### Default Credentials

The default MinIO credentials are:
- **Username:** minioadmin
- **Password:** minioadmin
- **Bucket:** ctfd-attachments

These are development credentials - safe for local use only.

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

### "Access denied" on Downloads

The bucket needs public read access for downloads to work:

```bash
docker exec ng-minio mc anonymous set download local/ctfd-attachments
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

## Additional Resources

- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [MinIO Python SDK](https://min.io/docs/minio/linux/developers/python/API.html)
- [S3 Compatibility](https://min.io/docs/minio/linux/reference/s3-compatibility.html)
