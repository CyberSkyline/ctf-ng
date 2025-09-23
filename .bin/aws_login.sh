#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
source $DIR/utils.sh
load_env

# Check if awscli is configured
if [[ -z "$AWS_ACCESS_KEY_ID" || "$AWS_ACCESS_KEY_ID" == "-" || -z "$AWS_SECRET_ACCESS_KEY" || "$AWS_SECRET_ACCESS_KEY" == "-" ]]; then
  echo "Error: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must both be set in your .env"
  exit 1
fi

if [[ -z "$AWS_MFA_ARN" || "$AWS_MFA_ARN" == "-" ]]; then
  echo "Error: AWS_MFA_ARN must be set in your .env"
  exit 1
fi

# Check if MFA specified
MFA_CODE=$1
if [[ -z "$MFA_CODE" ]]; then
  echo "Usage: pnpm aws-login 111111"
  exit 1
fi

# Sign in to AWS
creds=$(AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY aws sts get-session-token --serial-number $AWS_MFA_ARN --token-code $MFA_CODE)

if [[ $? -ne 0 ]]; then
  echo "Error: Failed to get AWS session token."
  exit 1
fi

AWS_ACCESS_KEY_ID=$(echo $creds | python3 -c "import sys, json; print(json.load(sys.stdin)['Credentials']['AccessKeyId'])")
AWS_SECRET_ACCESS_KEY=$(echo $creds | python3 -c "import sys, json; print(json.load(sys.stdin)['Credentials']['SecretAccessKey'])")
AWS_SESSION_TOKEN=$(echo $creds | python3 -c "import sys, json; print(json.load(sys.stdin)['Credentials']['SessionToken'])")

echo "AWS login successful"

# Sign in to ECR
if [[ -z "$AWS_ECR_URI" ]]; then
  echo "Error: AWS_ECR_URI must be set in your .env"
  exit 1
fi
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN aws ecr get-login-password | docker login --username AWS --password-stdin $AWS_ECR_URI
