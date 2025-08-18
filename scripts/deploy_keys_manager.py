#!/usr/bin/env python3
"""
Deploy Keys Manager for MirrorWatcherAI
=======================================

Secure management of deployment keys and API tokens for the MirrorWatcherAI system.
Provides automated rotation, validation, and secure storage capabilities.
"""

import os
import sys
import json
import argparse
import subprocess
import secrets
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeployKeysManager:
    """
    Secure deployment keys and API tokens manager.
    
    Provides:
    - Secure key generation and rotation
    - GitHub repository secrets management
    - API key validation and testing
    - Audit logging and compliance
    - Emergency key revocation
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.keys_directory = self.project_root / ".keys"
        self.audit_log = self.project_root / "logs" / "keys_audit.log"
        
        # Ensure directories exist
        os.makedirs(self.keys_directory, exist_ok=True)
        os.makedirs(self.audit_log.parent, exist_ok=True)
        
        # Configuration
        self.github_owner = "Triune-Oracle"
        self.github_repo = "triune-swarm-engine"
        
        # Required secrets configuration
        self.required_secrets = {
            "REPO_SYNC_TOKEN": {
                "description": "GitHub Personal Access Token for repository synchronization",
                "scopes": ["repo", "workflow", "read:org"],
                "validation_endpoint": "https://api.github.com/user",
                "rotation_days": 90
            },
            "SHADOWSCROLLS_ENDPOINT": {
                "description": "ShadowScrolls API endpoint URL",
                "default": "https://api.shadowscrolls.triune-oracle.com/v1",
                "validation_method": "url_format",
                "rotation_days": None
            },
            "SHADOWSCROLLS_API_KEY": {
                "description": "ShadowScrolls API authentication key",
                "prefix": "ss_live_",
                "length": 40,
                "validation_endpoint": "/health",
                "rotation_days": 60
            },
            "LEGIO_COGNITO_API_KEY": {
                "description": "Legio-Cognito API authentication key",
                "prefix": "lc_",
                "length": 32,
                "validation_endpoint": "/v1/health",
                "rotation_days": 60
            },
            "TRIUMVIRATE_MONITOR_API_KEY": {
                "description": "Triumvirate Monitor API authentication key",
                "prefix": "tm_",
                "length": 32,
                "validation_endpoint": "/v1/health",
                "rotation_days": 60
            },
            "SWARM_ENGINE_API_KEY": {
                "description": "Swarm Engine API authentication key",
                "prefix": "se_",
                "length": 32,
                "validation_endpoint": "/v1/health",
                "rotation_days": 60
            }
        }
    
    def audit_log_entry(self, action: str, details: Dict[str, Any]):
        """Log audit entry for key management operations."""
        
        timestamp = datetime.now(timezone.utc).isoformat()
        audit_entry = {
            "timestamp": timestamp,
            "action": action,
            "details": details,
            "user": os.getenv("USER", "unknown"),
            "system": os.uname().sysname if hasattr(os, 'uname') else "unknown"
        }
        
        try:
            with open(self.audit_log, 'a') as f:
                f.write(json.dumps(audit_entry) + '\n')
            logger.info(f"Audit log entry: {action}")
        except Exception as e:
            logger.error(f"Failed to write audit log: {str(e)}")
    
    def generate_api_key(self, prefix: str = "", length: int = 32) -> str:
        """
        Generate a cryptographically secure API key.
        
        Args:
            prefix: Key prefix (e.g., 'ss_live_')
            length: Key length in characters
            
        Returns:
            Generated API key
        """
        # Generate random bytes
        key_bytes = secrets.token_bytes(length // 2)
        key_hex = key_bytes.hex()
        
        # Apply prefix if provided
        if prefix:
            api_key = f"{prefix}{key_hex}"
        else:
            api_key = key_hex
        
        return api_key
    
    def validate_github_token(self, token: str) -> Dict[str, Any]:
        """
        Validate GitHub personal access token.
        
        Args:
            token: GitHub token to validate
            
        Returns:
            Validation results
        """
        try:
            import requests
            
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "MirrorWatcherAI-KeysManager/1.0.0"
            }
            
            # Test token validity
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Check token scopes
                token_scopes = response.headers.get("X-OAuth-Scopes", "").split(", ")
                required_scopes = self.required_secrets["REPO_SYNC_TOKEN"]["scopes"]
                missing_scopes = [scope for scope in required_scopes if scope not in token_scopes]
                
                return {
                    "valid": True,
                    "user": user_data.get("login"),
                    "user_id": user_data.get("id"),
                    "scopes": token_scopes,
                    "missing_scopes": missing_scopes,
                    "scope_sufficient": len(missing_scopes) == 0
                }
            
            elif response.status_code == 401:
                return {
                    "valid": False,
                    "error": "Invalid or expired token",
                    "status_code": response.status_code
                }
            
            else:
                return {
                    "valid": False,
                    "error": f"API error: {response.status_code}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation failed: {str(e)}"
            }
    
    def validate_api_endpoint(self, endpoint: str, api_key: str, health_path: str = "/health") -> Dict[str, Any]:
        """
        Validate API endpoint connectivity and authentication.
        
        Args:
            endpoint: Base API endpoint URL
            api_key: API key for authentication
            health_path: Health check endpoint path
            
        Returns:
            Validation results
        """
        try:
            import requests
            
            # Construct health check URL
            health_url = endpoint.rstrip('/') + health_path
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "User-Agent": "MirrorWatcherAI-KeysManager/1.0.0"
            }
            
            response = requests.get(health_url, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                return {
                    "valid": True,
                    "endpoint": health_url,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
            
            elif response.status_code == 401:
                return {
                    "valid": False,
                    "error": "Authentication failed - invalid API key",
                    "endpoint": health_url,
                    "status_code": response.status_code
                }
            
            elif response.status_code == 404:
                # Health endpoint might not exist - try root endpoint
                root_response = requests.get(endpoint, headers=headers, timeout=10)
                return {
                    "valid": root_response.status_code in [200, 201],
                    "endpoint": endpoint,
                    "status_code": root_response.status_code,
                    "note": "Health endpoint not found, tested root endpoint"
                }
            
            else:
                return {
                    "valid": False,
                    "error": f"API error: {response.status_code}",
                    "endpoint": health_url,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": f"Endpoint validation failed: {str(e)}",
                "endpoint": health_url if 'health_url' in locals() else endpoint
            }
    
    def get_github_repository_secrets(self) -> Dict[str, Any]:
        """
        Get current GitHub repository secrets (metadata only).
        
        Returns:
            Repository secrets information
        """
        try:
            # This would use GitHub CLI or API to get secrets metadata
            # For security, actual secret values are never retrieved
            
            github_token = os.getenv("REPO_SYNC_TOKEN") or os.getenv("GITHUB_TOKEN")
            if not github_token:
                return {"error": "No GitHub token available"}
            
            import requests
            
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/actions/secrets"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                secrets_list = data.get("secrets", [])
                
                return {
                    "success": True,
                    "total_count": data.get("total_count", 0),
                    "secrets": [secret["name"] for secret in secrets_list],
                    "configured_secrets": [
                        name for name in self.required_secrets.keys() 
                        if name in [s["name"] for s in secrets_list]
                    ]
                }
            
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get repository secrets: {str(e)}"
            }
    
    def update_github_repository_secret(self, secret_name: str, secret_value: str) -> Dict[str, Any]:
        """
        Update a GitHub repository secret.
        
        Args:
            secret_name: Name of the secret
            secret_value: Value of the secret
            
        Returns:
            Update results
        """
        try:
            github_token = os.getenv("REPO_SYNC_TOKEN") or os.getenv("GITHUB_TOKEN")
            if not github_token:
                return {"success": False, "error": "No GitHub token available"}
            
            # Use GitHub CLI if available (more secure)
            if self._has_github_cli():
                return self._update_secret_via_cli(secret_name, secret_value)
            
            # Fallback to direct API (requires encryption)
            return self._update_secret_via_api(secret_name, secret_value, github_token)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update secret: {str(e)}"
            }
    
    def _has_github_cli(self) -> bool:
        """Check if GitHub CLI is available."""
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _update_secret_via_cli(self, secret_name: str, secret_value: str) -> Dict[str, Any]:
        """Update secret using GitHub CLI."""
        try:
            cmd = [
                "gh", "secret", "set", secret_name,
                "--repo", f"{self.github_owner}/{self.github_repo}",
                "--body", secret_value
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "method": "github_cli",
                "secret_name": secret_name
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"GitHub CLI error: {e.stderr}",
                "method": "github_cli"
            }
    
    def _update_secret_via_api(self, secret_name: str, secret_value: str, github_token: str) -> Dict[str, Any]:
        """Update secret using GitHub API (requires public key encryption)."""
        try:
            import requests
            import base64
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.primitives import hashes
            
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Get repository public key
            public_key_url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/actions/secrets/public-key"
            response = requests.get(public_key_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get public key: {response.status_code}"
                }
            
            public_key_data = response.json()
            key_id = public_key_data["key_id"]
            public_key_b64 = public_key_data["key"]
            
            # Decode and load public key
            public_key_bytes = base64.b64decode(public_key_b64)
            public_key = serialization.load_der_public_key(public_key_bytes)
            
            # Encrypt secret value
            encrypted_value = public_key.encrypt(
                secret_value.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            encrypted_value_b64 = base64.b64encode(encrypted_value).decode()
            
            # Update secret
            secret_url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/actions/secrets/{secret_name}"
            secret_data = {
                "encrypted_value": encrypted_value_b64,
                "key_id": key_id
            }
            
            response = requests.put(secret_url, json=secret_data, headers=headers, timeout=10)
            
            if response.status_code in [201, 204]:
                return {
                    "success": True,
                    "method": "github_api",
                    "secret_name": secret_name,
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "method": "github_api"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"API update failed: {str(e)}",
                "method": "github_api"
            }
    
    def rotate_api_key(self, secret_name: str) -> Dict[str, Any]:
        """
        Rotate an API key (generate new key and update in GitHub).
        
        Args:
            secret_name: Name of the secret to rotate
            
        Returns:
            Rotation results
        """
        if secret_name not in self.required_secrets:
            return {
                "success": False,
                "error": f"Unknown secret: {secret_name}"
            }
        
        secret_config = self.required_secrets[secret_name]
        
        try:
            # Generate new API key
            if secret_name == "REPO_SYNC_TOKEN":
                return {
                    "success": False,
                    "error": "GitHub token rotation requires manual process"
                }
            
            elif secret_name == "SHADOWSCROLLS_ENDPOINT":
                return {
                    "success": False,
                    "error": "Endpoint URL does not require rotation"
                }
            
            else:
                # Generate new API key
                prefix = secret_config.get("prefix", "")
                length = secret_config.get("length", 32)
                new_key = self.generate_api_key(prefix, length)
                
                # Update in GitHub
                update_result = self.update_github_repository_secret(secret_name, new_key)
                
                if update_result["success"]:
                    # Log rotation
                    self.audit_log_entry("key_rotation", {
                        "secret_name": secret_name,
                        "rotation_method": update_result.get("method"),
                        "new_key_prefix": new_key[:8] + "..."
                    })
                    
                    return {
                        "success": True,
                        "secret_name": secret_name,
                        "new_key_preview": new_key[:8] + "...",
                        "update_method": update_result.get("method")
                    }
                
                else:
                    return {
                        "success": False,
                        "error": f"Failed to update secret: {update_result.get('error')}",
                        "secret_name": secret_name
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Key rotation failed: {str(e)}",
                "secret_name": secret_name
            }
    
    def check_key_expiration(self) -> Dict[str, Any]:
        """
        Check which keys are approaching expiration.
        
        Returns:
            Expiration status for all keys
        """
        expiration_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "keys": {},
            "action_required": []
        }
        
        for secret_name, config in self.required_secrets.items():
            rotation_days = config.get("rotation_days")
            
            if rotation_days is None:
                expiration_status["keys"][secret_name] = {
                    "status": "no_rotation_required",
                    "message": "This key does not require rotation"
                }
                continue
            
            # For this implementation, we'll simulate key age
            # In production, you'd track actual key creation dates
            simulated_age_days = 30  # Simulate keys are 30 days old
            days_until_expiration = rotation_days - simulated_age_days
            
            if days_until_expiration <= 7:
                status = "urgent"
                expiration_status["action_required"].append(secret_name)
            elif days_until_expiration <= 14:
                status = "warning"
            else:
                status = "ok"
            
            expiration_status["keys"][secret_name] = {
                "status": status,
                "days_until_expiration": days_until_expiration,
                "rotation_required_days": rotation_days,
                "age_days": simulated_age_days
            }
        
        return expiration_status
    
    def generate_setup_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive setup and security report.
        
        Returns:
            Complete setup report
        """
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "report_version": "1.0.0",
            "system_status": {},
            "secrets_status": {},
            "security_recommendations": []
        }
        
        # Check GitHub repository secrets
        github_secrets = self.get_github_repository_secrets()
        report["system_status"]["github_secrets"] = github_secrets
        
        # Check key expiration
        expiration_status = self.check_key_expiration()
        report["system_status"]["key_expiration"] = expiration_status
        
        # Validate each configured secret
        for secret_name in self.required_secrets.keys():
            secret_value = os.getenv(secret_name)
            
            if not secret_value:
                report["secrets_status"][secret_name] = {
                    "configured": False,
                    "error": "Secret not found in environment"
                }
                continue
            
            # Validate specific secret types
            if secret_name == "REPO_SYNC_TOKEN":
                validation = self.validate_github_token(secret_value)
                report["secrets_status"][secret_name] = {
                    "configured": True,
                    "validation": validation
                }
            
            elif secret_name == "SHADOWSCROLLS_ENDPOINT":
                # Validate URL format
                import re
                url_pattern = r'^https?://[a-zA-Z0-9.-]+(/.*)?$'
                is_valid_url = bool(re.match(url_pattern, secret_value))
                
                report["secrets_status"][secret_name] = {
                    "configured": True,
                    "validation": {
                        "valid": is_valid_url,
                        "format": "url",
                        "value_preview": secret_value
                    }
                }
            
            else:
                # For other API keys, just check format
                config = self.required_secrets[secret_name]
                prefix = config.get("prefix", "")
                expected_length = len(prefix) + config.get("length", 32)
                
                format_valid = (
                    secret_value.startswith(prefix) and 
                    len(secret_value) >= expected_length
                )
                
                report["secrets_status"][secret_name] = {
                    "configured": True,
                    "validation": {
                        "valid": format_valid,
                        "format": "api_key",
                        "expected_prefix": prefix,
                        "value_preview": secret_value[:8] + "..." if len(secret_value) > 8 else "***"
                    }
                }
        
        # Generate security recommendations
        recommendations = []
        
        # Check for missing secrets
        missing_secrets = [
            name for name, status in report["secrets_status"].items()
            if not status.get("configured", False)
        ]
        
        if missing_secrets:
            recommendations.append({
                "priority": "high",
                "category": "missing_secrets",
                "message": f"Configure missing secrets: {', '.join(missing_secrets)}",
                "action": "Add missing secrets to GitHub repository secrets"
            })
        
        # Check for invalid secrets
        invalid_secrets = [
            name for name, status in report["secrets_status"].items()
            if status.get("configured") and not status.get("validation", {}).get("valid", True)
        ]
        
        if invalid_secrets:
            recommendations.append({
                "priority": "high",
                "category": "invalid_secrets",
                "message": f"Fix invalid secrets: {', '.join(invalid_secrets)}",
                "action": "Update invalid secrets with correct values"
            })
        
        # Check for keys needing rotation
        if expiration_status.get("action_required"):
            recommendations.append({
                "priority": "medium",
                "category": "key_rotation",
                "message": f"Rotate expiring keys: {', '.join(expiration_status['action_required'])}",
                "action": "Use the rotate-key command to update expiring keys"
            })
        
        report["security_recommendations"] = recommendations
        
        return report


def main():
    """Main entry point for the deploy keys manager."""
    
    parser = argparse.ArgumentParser(
        description="Deploy Keys Manager for MirrorWatcherAI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate key command
    gen_parser = subparsers.add_parser("generate-key", help="Generate a new API key")
    gen_parser.add_argument("--prefix", help="Key prefix")
    gen_parser.add_argument("--length", type=int, default=32, help="Key length")
    
    # Validate command
    val_parser = subparsers.add_parser("validate", help="Validate API keys and configuration")
    val_parser.add_argument("--secret", help="Specific secret to validate")
    
    # Rotate key command
    rot_parser = subparsers.add_parser("rotate-key", help="Rotate an API key")
    rot_parser.add_argument("secret_name", help="Name of the secret to rotate")
    
    # List secrets command
    subparsers.add_parser("list-secrets", help="List GitHub repository secrets")
    
    # Check expiration command
    subparsers.add_parser("check-expiration", help="Check key expiration status")
    
    # Generate report command
    subparsers.add_parser("report", help="Generate comprehensive setup report")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize manager
    manager = DeployKeysManager()
    
    try:
        if args.command == "generate-key":
            key = manager.generate_api_key(args.prefix or "", args.length)
            print(f"Generated API key: {key}")
        
        elif args.command == "validate":
            if args.secret:
                # Validate specific secret
                secret_value = os.getenv(args.secret)
                if not secret_value:
                    print(f"Secret {args.secret} not found in environment")
                    sys.exit(1)
                
                if args.secret == "REPO_SYNC_TOKEN":
                    result = manager.validate_github_token(secret_value)
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Validation for {args.secret} not yet implemented")
            else:
                # Validate all secrets
                report = manager.generate_setup_report()
                print(json.dumps(report["secrets_status"], indent=2))
        
        elif args.command == "rotate-key":
            result = manager.rotate_api_key(args.secret_name)
            print(json.dumps(result, indent=2))
        
        elif args.command == "list-secrets":
            result = manager.get_github_repository_secrets()
            print(json.dumps(result, indent=2))
        
        elif args.command == "check-expiration":
            result = manager.check_key_expiration()
            print(json.dumps(result, indent=2))
        
        elif args.command == "report":
            report = manager.generate_setup_report()
            print(json.dumps(report, indent=2))
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"Command failed: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()