#!/bin/bash
# Initialize nginx SSL certificates from AWS Secrets Manager

set -euo pipefail

SSL_DIR="${SSL_DIR:-/etc/nginx/ssl}"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_SECRET_NAME="${AWS_SECRET_NAME:-ctf-ng/nginx-ssl}"

echo "Initializing nginx SSL certificates..."
echo "  Target directory: $SSL_DIR"
echo "  AWS Secret: $AWS_SECRET_NAME"
echo "  AWS Region: $AWS_REGION"

mkdir -p "$SSL_DIR"
chmod 700 "$SSL_DIR"

echo "Fetching SSL certificates from AWS..."
aws secretsmanager get-secret-value \
    --secret-id "$AWS_SECRET_NAME" \
    --region "$AWS_REGION" \
    --query 'SecretString' \
    --output text \
  | python3 -c '
import json, sys, os
secrets = json.load(sys.stdin)
ssl_dir = os.environ["SSL_DIR"]
for filename, content in secrets.items():
    filepath = os.path.join(ssl_dir, filename)
    with open(filepath, "w") as f:
        f.write(content)
    os.chmod(filepath, 0o600 if filename.endswith(".key") else 0o644)
    print(f"  - {filename}: OK")
'

if [ ! -f "$SSL_DIR/certificate.crt" ] || [ ! -f "$SSL_DIR/certificate.key" ]; then
    echo "ERROR: Expected certificate.crt and certificate.key not found in $SSL_DIR" >&2
    exit 1
fi

echo "SSL certificates initialized successfully"
