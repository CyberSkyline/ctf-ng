"""
AWS Secrets Manager integration for production environment initialization

Loads environment from .env.prod (config) and AWS Secrets Manager (secrets).
"""

import json
import logging
import os
from typing import Any, Dict, Optional

try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

from dotenv import dotenv_values

logger = logging.getLogger(__name__)

class SecretsManager:
    """
    Manages environment variables from .env.prod and AWS Secrets Manager
    """

    def __init__(self):
        """Initialize the secrets manager"""
        self._secrets_cache: Dict[str, Any] = {}
        self._loaded = False

    def load_secrets(self, secret_name: Optional[str] = None) -> Dict[str, str]:
        """Load configuration and secrets from .env.prod and AWS Secrets Manager"""
        if self._loaded and self._secrets_cache:
            return self._secrets_cache

        try:
            self._secrets_cache = self._load_production_config(secret_name)
            self._loaded = True
            return self._secrets_cache
        
        except Exception as e:
            logger.error(f"Failed to load environment variables: {str(e)}")
            raise

    def _load_production_config(self, secret_name: Optional[str] = None) -> Dict[str, str]:
        """Load configuration from .env.prod and overlay with AWS secrets"""
        config = {}

        # Load base configuration from .env.prod
        if os.path.exists(".env.prod"):
            try:
                env_config = dotenv_values(".env.prod")
                config.update(env_config)
                logger.info(f"Loaded {len(env_config)} variables from .env.prod")
            except Exception as e:
                logger.warning(f"Failed to load .env.prod: {str(e)}")

        # Overlay secrets from AWS Secrets Manager
        try:
            aws_secrets = self._load_from_aws_secrets_manager(secret_name)
            config.update(aws_secrets)
            logger.info(f"Loaded {len(aws_secrets)} secrets from AWS Secrets Manager")
        except Exception as e:
            logger.warning(f"Failed to load AWS secrets: {str(e)}")
            if not config:
                raise RuntimeError(
                    "No configuration found. Ensure either .env.prod exists or AWS secrets are accessible."
                ) from e

        logger.info(f"Loaded {len(config)} total environment variables")
        return config

    def _load_from_aws_secrets_manager(self, secret_name: Optional[str] = None) -> Dict[str, str]:
        """Fetch secrets from AWS Secrets Manager"""
        if not HAS_BOTO3:
            raise RuntimeError("boto3 is required for production. Install it with: pip install boto3")

        secret_name = secret_name or os.getenv("AWS_SECRET_NAME", "ctfd/production")
        region_name = os.getenv("AWS_REGION", "us-east-1")

        try:
            client = boto3.client("secretsmanager", region_name=region_name)
            response = client.get_secret_value(SecretId=secret_name)

            if "SecretString" in response:
                secrets = json.loads(response["SecretString"])
            else:
                secrets = json.loads(response["SecretBinary"])

            return secrets

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                logger.error(f"Secret '{secret_name}' not found in AWS Secrets Manager")
            elif error_code == "AccessDeniedException":
                logger.error("Access denied to AWS Secrets Manager. Check IAM permissions.")
            else:
                logger.error(f"AWS Secrets Manager error: {error_code}")
            raise




if __name__ == "__main__":
    # Print shell export statements for eval in run_production.sh:
    #   eval "$(python3 init_secrets.py)"
    import shlex
    sm = SecretsManager()
    secrets = sm.load_secrets()
    for key, value in secrets.items():
        print(f"export {key}={shlex.quote(str(value))}")
