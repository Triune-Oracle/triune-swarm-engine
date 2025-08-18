#!/usr/bin/env python3
"""
Deploy Keys Manager - Secure key management with automatic rotation
Manages encrypted deploy keys and API credentials for MirrorWatcherAI
"""

import os
import json
import hashlib
import base64
import secrets
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DeployKeysManager:
    """Secure management of deploy keys and API credentials."""
    
    def __init__(self, keys_dir: str = "./.deploy_keys"):
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(exist_ok=True, mode=0o700)
        self.keys_file = self.keys_dir / 'encrypted_keys.json'
        self.rotation_log = self.keys_dir / 'rotation_log.json'
        
    def encrypt_key(self, key: str, password: str) -> str:
        """Encrypt a key using a password."""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            
            # Generate salt
            salt = os.urandom(16)
            
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            derived_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Encrypt the key
            fernet = Fernet(derived_key)
            encrypted_key = fernet.encrypt(key.encode())
            
            # Return salt + encrypted key (base64 encoded)
            return base64.b64encode(salt + encrypted_key).decode()
            
        except ImportError:
            logger.warning("Cryptography library not available, using basic encoding")
            # Fallback to basic base64 encoding (not secure)
            return base64.b64encode(key.encode()).decode()
    
    def decrypt_key(self, encrypted_key: str, password: str) -> str:
        """Decrypt a key using a password."""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            
            # Decode the encrypted data
            data = base64.b64decode(encrypted_key.encode())
            
            # Extract salt and encrypted key
            salt = data[:16]
            encrypted_data = data[16:]
            
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            derived_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Decrypt the key
            fernet = Fernet(derived_key)
            decrypted_key = fernet.decrypt(encrypted_data)
            
            return decrypted_key.decode()
            
        except ImportError:
            logger.warning("Cryptography library not available, using basic decoding")
            # Fallback to basic base64 decoding
            return base64.b64decode(encrypted_key.encode()).decode()
    
    def store_key(self, key_name: str, key_value: str, password: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store an encrypted key with metadata."""
        try:
            # Load existing keys
            keys_data = self.load_keys_data()
            
            # Encrypt the key
            encrypted_key = self.encrypt_key(key_value, password)
            
            # Store key with metadata
            keys_data['keys'][key_name] = {
                'encrypted_value': encrypted_key,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'last_rotated': datetime.now(timezone.utc).isoformat(),
                'metadata': metadata or {},
                'hash': hashlib.sha256(key_value.encode()).hexdigest()[:16]
            }
            
            # Save keys data
            self.save_keys_data(keys_data)
            
            # Log the operation
            self.log_operation('store', key_name, success=True)
            
            logger.info(f"Key '{key_name}' stored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store key '{key_name}': {str(e)}")
            self.log_operation('store', key_name, success=False, error=str(e))
            return False
    
    def retrieve_key(self, key_name: str, password: str) -> Optional[str]:
        """Retrieve and decrypt a key."""
        try:
            keys_data = self.load_keys_data()
            
            if key_name not in keys_data['keys']:
                logger.error(f"Key '{key_name}' not found")
                return None
            
            key_info = keys_data['keys'][key_name]
            encrypted_value = key_info['encrypted_value']
            
            # Decrypt the key
            decrypted_key = self.decrypt_key(encrypted_value, password)
            
            # Verify integrity
            current_hash = hashlib.sha256(decrypted_key.encode()).hexdigest()[:16]
            stored_hash = key_info['hash']
            
            if current_hash != stored_hash:
                logger.error(f"Key integrity check failed for '{key_name}'")
                return None
            
            # Log the operation
            self.log_operation('retrieve', key_name, success=True)
            
            return decrypted_key
            
        except Exception as e:
            logger.error(f"Failed to retrieve key '{key_name}': {str(e)}")
            self.log_operation('retrieve', key_name, success=False, error=str(e))
            return None
    
    def rotate_key(self, key_name: str, new_key_value: str, password: str) -> bool:
        """Rotate an existing key."""
        try:
            keys_data = self.load_keys_data()
            
            if key_name not in keys_data['keys']:
                logger.error(f"Key '{key_name}' not found for rotation")
                return False
            
            # Backup old key info
            old_key_info = keys_data['keys'][key_name].copy()
            
            # Encrypt new key
            encrypted_key = self.encrypt_key(new_key_value, password)
            
            # Update key info
            keys_data['keys'][key_name].update({
                'encrypted_value': encrypted_key,
                'last_rotated': datetime.now(timezone.utc).isoformat(),
                'hash': hashlib.sha256(new_key_value.encode()).hexdigest()[:16],
                'rotation_count': keys_data['keys'][key_name].get('rotation_count', 0) + 1
            })
            
            # Save keys data
            self.save_keys_data(keys_data)
            
            # Log the rotation with old hash for audit
            self.log_operation('rotate', key_name, success=True, metadata={
                'old_hash': old_key_info['hash'],
                'new_hash': keys_data['keys'][key_name]['hash']
            })
            
            logger.info(f"Key '{key_name}' rotated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate key '{key_name}': {str(e)}")
            self.log_operation('rotate', key_name, success=False, error=str(e))
            return False
    
    def list_keys(self) -> Dict[str, Any]:
        """List all stored keys with metadata (excluding actual values)."""
        try:
            keys_data = self.load_keys_data()
            
            key_summary = {}
            for key_name, key_info in keys_data['keys'].items():
                key_summary[key_name] = {
                    'created_at': key_info['created_at'],
                    'last_rotated': key_info['last_rotated'],
                    'rotation_count': key_info.get('rotation_count', 0),
                    'hash_preview': key_info['hash'],
                    'metadata': key_info.get('metadata', {})
                }
            
            return {
                'keys': key_summary,
                'total_keys': len(key_summary),
                'last_updated': keys_data.get('last_updated')
            }
            
        except Exception as e:
            logger.error(f"Failed to list keys: {str(e)}")
            return {'error': str(e)}
    
    def check_rotation_needed(self, max_age_days: int = 90) -> Dict[str, Any]:
        """Check which keys need rotation based on age."""
        try:
            keys_data = self.load_keys_data()
            rotation_needed = []
            current_time = datetime.now(timezone.utc)
            
            for key_name, key_info in keys_data['keys'].items():
                last_rotated = datetime.fromisoformat(key_info['last_rotated'].replace('Z', '+00:00'))
                age_days = (current_time - last_rotated).days
                
                if age_days >= max_age_days:
                    rotation_needed.append({
                        'key_name': key_name,
                        'age_days': age_days,
                        'last_rotated': key_info['last_rotated']
                    })
            
            return {
                'rotation_needed': rotation_needed,
                'max_age_days': max_age_days,
                'check_time': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to check rotation needs: {str(e)}")
            return {'error': str(e)}
    
    def load_keys_data(self) -> Dict[str, Any]:
        """Load keys data from storage."""
        if not self.keys_file.exists():
            return {
                'version': '1.0',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'keys': {}
            }
        
        try:
            with open(self.keys_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load keys data: {str(e)}")
            return {'keys': {}, 'error': str(e)}
    
    def save_keys_data(self, keys_data: Dict[str, Any]) -> None:
        """Save keys data to storage."""
        keys_data['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        with open(self.keys_file, 'w') as f:
            json.dump(keys_data, f, indent=2)
        
        # Set restrictive permissions
        os.chmod(self.keys_file, 0o600)
    
    def log_operation(self, operation: str, key_name: str, success: bool, error: str = None, metadata: Dict[str, Any] = None) -> None:
        """Log key operations for audit purposes."""
        try:
            # Load existing log
            if self.rotation_log.exists():
                with open(self.rotation_log, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'operations': []}
            
            # Add new operation
            operation_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'operation': operation,
                'key_name': key_name,
                'success': success,
                'metadata': metadata or {}
            }
            
            if error:
                operation_entry['error'] = error
            
            log_data['operations'].append(operation_entry)
            
            # Keep only last 1000 operations
            if len(log_data['operations']) > 1000:
                log_data['operations'] = log_data['operations'][-1000:]
            
            # Save log
            with open(self.rotation_log, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(self.rotation_log, 0o600)
            
        except Exception as e:
            logger.error(f"Failed to log operation: {str(e)}")


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for the deploy keys manager."""
    parser = argparse.ArgumentParser(
        description='Deploy Keys Manager - Secure key management with automatic rotation'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Store key command
    store_parser = subparsers.add_parser('store', help='Store a new encrypted key')
    store_parser.add_argument('key_name', help='Name of the key to store')
    store_parser.add_argument('--key-value', help='Key value (will prompt if not provided)')
    store_parser.add_argument('--password', help='Encryption password (will prompt if not provided)')
    store_parser.add_argument('--metadata', help='JSON metadata for the key')
    
    # Retrieve key command
    retrieve_parser = subparsers.add_parser('retrieve', help='Retrieve and decrypt a key')
    retrieve_parser.add_argument('key_name', help='Name of the key to retrieve')
    retrieve_parser.add_argument('--password', help='Decryption password (will prompt if not provided)')
    
    # Rotate key command
    rotate_parser = subparsers.add_parser('rotate', help='Rotate an existing key')
    rotate_parser.add_argument('key_name', help='Name of the key to rotate')
    rotate_parser.add_argument('--new-key-value', help='New key value (will prompt if not provided)')
    rotate_parser.add_argument('--password', help='Encryption password (will prompt if not provided)')
    
    # List keys command
    list_parser = subparsers.add_parser('list', help='List all stored keys')
    
    # Check rotation command
    check_parser = subparsers.add_parser('check-rotation', help='Check which keys need rotation')
    check_parser.add_argument('--max-age-days', type=int, default=90, help='Maximum age in days before rotation needed')
    
    return parser


def main():
    """Main entry point for the deploy keys manager."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    manager = DeployKeysManager()
    
    try:
        if args.command == 'store':
            key_value = args.key_value
            if not key_value:
                import getpass
                key_value = getpass.getpass(f"Enter key value for '{args.key_name}': ")
            
            password = args.password
            if not password:
                import getpass
                password = getpass.getpass("Enter encryption password: ")
            
            metadata = None
            if args.metadata:
                metadata = json.loads(args.metadata)
            
            success = manager.store_key(args.key_name, key_value, password, metadata)
            if success:
                print(f"✅ Key '{args.key_name}' stored successfully")
            else:
                print(f"❌ Failed to store key '{args.key_name}'")
        
        elif args.command == 'retrieve':
            password = args.password
            if not password:
                import getpass
                password = getpass.getpass("Enter decryption password: ")
            
            key_value = manager.retrieve_key(args.key_name, password)
            if key_value:
                print(f"Key '{args.key_name}': {key_value}")
            else:
                print(f"❌ Failed to retrieve key '{args.key_name}'")
        
        elif args.command == 'rotate':
            new_key_value = args.new_key_value
            if not new_key_value:
                import getpass
                new_key_value = getpass.getpass(f"Enter new key value for '{args.key_name}': ")
            
            password = args.password
            if not password:
                import getpass
                password = getpass.getpass("Enter encryption password: ")
            
            success = manager.rotate_key(args.key_name, new_key_value, password)
            if success:
                print(f"✅ Key '{args.key_name}' rotated successfully")
            else:
                print(f"❌ Failed to rotate key '{args.key_name}'")
        
        elif args.command == 'list':
            keys_info = manager.list_keys()
            if 'error' in keys_info:
                print(f"❌ Error listing keys: {keys_info['error']}")
            else:
                print(f"📋 Total keys: {keys_info['total_keys']}")
                print(f"Last updated: {keys_info.get('last_updated', 'Unknown')}")
                print()
                
                for key_name, key_info in keys_info['keys'].items():
                    print(f"🔑 {key_name}")
                    print(f"   Created: {key_info['created_at']}")
                    print(f"   Last rotated: {key_info['last_rotated']}")
                    print(f"   Rotations: {key_info['rotation_count']}")
                    print(f"   Hash preview: {key_info['hash_preview']}")
                    if key_info['metadata']:
                        print(f"   Metadata: {key_info['metadata']}")
                    print()
        
        elif args.command == 'check-rotation':
            rotation_check = manager.check_rotation_needed(args.max_age_days)
            if 'error' in rotation_check:
                print(f"❌ Error checking rotation: {rotation_check['error']}")
            else:
                rotation_needed = rotation_check['rotation_needed']
                if rotation_needed:
                    print(f"⚠️  {len(rotation_needed)} keys need rotation (older than {args.max_age_days} days):")
                    print()
                    for key_info in rotation_needed:
                        print(f"🔄 {key_info['key_name']}")
                        print(f"   Age: {key_info['age_days']} days")
                        print(f"   Last rotated: {key_info['last_rotated']}")
                        print()
                else:
                    print(f"✅ All keys are up to date (newer than {args.max_age_days} days)")
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        logger.error(f"Fatal error in deploy keys manager: {str(e)}")


if __name__ == '__main__':
    main()