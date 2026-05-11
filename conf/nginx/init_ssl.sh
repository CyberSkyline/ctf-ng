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
SECRET_JSON=$(aws secretsmanager get-secret-value \
    --secret-id "$AWS_SECRET_NAME" \
    --region "$AWS_REGION" \
    --query 'SecretString' \
    --output text)

# Extract certificate and key using awscli's --query + text output
aws secretsmanager get-secret-value \
    --secret-id "$AWS_SECRET_NAME" \
    --region "$AWS_REGION" \
    --query 'SecretString' \
    --output text \
  | python3 -c "
import json, sys, os
secrets = json.load(sys.stdin)
ssl_dir = os.environ['SSL_DIR']
for filename, content in secrets.items():
    filepath = os.path.join(ssl_dir, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    os.chmod(filepath, 0o600 if filename.endswith('.key') else 0o644)
    print(f'  - {filename}: OK')
"

if [ ! -f "$SSL_DIR/certificate.crt" ] || [ ! -f "$SSL_DIR/certificate.key" ]; then
    echo "ERROR: Expected certificate.crt and certificate.key not found in $SSL_DIR" >&2
    exit 1
fi

echo "SSL certificates initialized successfully"


echo "Initializing nginx SSL certificates..."
echo "  Target directory: $SSL_DIR"
echo "  AWS Secret: $AWS_SECRET_NAME"
echo "  AWS Region: $AWS_REGION"

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"
chmod 700 "$SSL_DIR"

# Fetch SSL certificates from AWS Secrets Manager
echo "Fetching SSL certificates from AWS..."
python3 << 'PYTHON_SCRIPT'
import json
import os
import sys
import boto3
from pathlib import Path

try:
    ssl_dir = os.getenv("SSL_DIR", "/etc/nginx/ssl")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    secret_name = os.getenv("AWS_SECRET_NAME", "ctfd/nginx-ssl")
    
    # Connect to AWS Secrets Manager
    client = boto3.client("secretsmanager", region_name=aws_region)
    
    # Fetch secret
    response = client.get_secret_value(SecretId=secret_name)
    
    if "SecretString" in response:
        secrets = json.loads(response["SecretString"])
    else:
        secrets = json.loads(response["SecretBinary"])
    
    # Write certificate files
    for filename, content in secrets.items():
        filepath = os.path.join(ssl_dir, filename)
        
        # Ensure parent directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Write file with restricted permissions
        with open(filepath, 'w') as f:
            # If content looks like base64, decode it
            if filename.endswith('.key') and len(content) > 100:
                try:
                    import base64
                    decoded = base64.b64decode(content)
                    if decoded.startswith(b'-----BEGIN'):
                        f.write(decoded.decode('utf-8'))
                    else:
                        f.write(content)
                except Exception:
                    f.write(content)
            else:
                f.write(content)
        
        # Set permissions
        if filename.endswith('.key'):
            os.chmod(filepath, 0o600)  # Private key: read-only for owner
        else:
            os.chmod(filepath, 0o644)  # Certificate: readable
        
        print(f"✓ Created {filename}")
    
    print(f"✓ Successfully loaded {len(secrets)} SSL certificates")
    sys.exit(0)

except Exception as e:
    print(f"✗ Failed to initialize SSL certificates: {e}", file=sys.stderr)
    sys.exit(1)

PYTHON_SCRIPT

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✓ SSL certificates initialized successfully"
    
    # Verify certificates exist
    if [ -f "$SSL_DIR/certificate.crt" ]; then
        echo "  - certificate.crt: OK"
    fi
    if [ -f "$SSL_DIR/certificate.key" ]; then
        echo "  - certificate.key: OK (permissions: 0600)"
    fi
    if [ -f "$SSL_DIR/intermediate.crt" ]; then
        echo "  - intermediate.crt: OK"
    fi
else
    echo "✗ Failed to initialize SSL certificates"
    exit 1
fi
