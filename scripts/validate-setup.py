#!/usr/bin/env python3
"""
🔍 Triune Swarm Engine - Setup Validation Script

Comprehensive validation framework for Mirror Watcher automation setup.
Verifies secrets configuration, API connectivity, and system integration.

Usage:
    python scripts/validate-setup.py [OPTIONS]

Options:
    --check-secrets      Validate secret presence and format
    --check-api          Test API connectivity  
    --check-permissions  Verify access permissions
    --check-structure    Validate file and directory structure
    --debug              Enable debug output
    --env-file PATH      Custom environment file path
    --quiet              Minimal output mode
    --json               Output results in JSON format

Version: 1.0.0
"""

import os
import sys
import json
import argparse
import re
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

class ValidationResult:
    """Container for validation results"""
    def __init__(self, check_name: str):
        self.check_name = check_name
        self.passed = False
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.info: List[str] = []
        self.details: Dict[str, Any] = {}
    
    def add_error(self, message: str):
        self.errors.append(message)
        self.passed = False
    
    def add_warning(self, message: str):
        self.warnings.append(message)
    
    def add_info(self, message: str):
        self.info.append(message)
    
    def set_passed(self, passed: bool = True):
        self.passed = passed and len(self.errors) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'check_name': self.check_name,
            'passed': self.passed,
            'warnings': self.warnings,
            'errors': self.errors,
            'info': self.info,
            'details': self.details
        }

class SetupValidator:
    """Main validation class for Triune Swarm Engine setup"""
    
    def __init__(self, args):
        self.args = args
        self.results: List[ValidationResult] = []
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / (args.env_file or '.env.local')
        self.secrets = {}
        
        # Load environment variables
        self._load_environment()
    
    def _load_environment(self):
        """Load environment variables from file and system"""
        # Load from environment file if it exists
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        
        # Extract secrets
        self.secrets = {
            'REPO_SYNC_TOKEN': os.getenv('REPO_SYNC_TOKEN'),
            'SHADOWSCROLLS_ENDPOINT': os.getenv('SHADOWSCROLLS_ENDPOINT'),
            'SHADOWSCROLLS_API_KEY': os.getenv('SHADOWSCROLLS_API_KEY'),
        }
    
    def print_status(self, message: str, status: str = 'info'):
        """Print formatted status message"""
        if self.args.quiet:
            return
        
        colors = {
            'info': Colors.BLUE,
            'success': Colors.GREEN,
            'warning': Colors.YELLOW,
            'error': Colors.RED,
            'debug': Colors.PURPLE
        }
        
        icons = {
            'info': 'ℹ️ ',
            'success': '✅',
            'warning': '⚠️ ',
            'error': '❌',
            'debug': '🔍'
        }
        
        if not self.args.json:
            color = colors.get(status, Colors.NC)
            icon = icons.get(status, '')
            print(f"{color}{icon} {message}{Colors.NC}")
    
    def debug_print(self, message: str):
        """Print debug message if debug mode is enabled"""
        if self.args.debug:
            self.print_status(f"DEBUG: {message}", 'debug')
    
    def validate_secrets_presence(self) -> ValidationResult:
        """Validate that all required secrets are present"""
        result = ValidationResult("secrets_presence")
        
        required_secrets = [
            'REPO_SYNC_TOKEN',
            'SHADOWSCROLLS_ENDPOINT', 
            'SHADOWSCROLLS_API_KEY'
        ]
        
        for secret in required_secrets:
            value = self.secrets.get(secret)
            if not value:
                result.add_error(f"Secret {secret} is not set")
            else:
                result.add_info(f"Secret {secret} is present")
                self.debug_print(f"{secret}: {value[:8]}...")
        
        result.set_passed(len(result.errors) == 0)
        result.details['found_secrets'] = len([s for s in required_secrets if self.secrets.get(s)])
        result.details['total_secrets'] = len(required_secrets)
        
        return result
    
    def validate_secret_formats(self) -> ValidationResult:
        """Validate secret format compliance"""
        result = ValidationResult("secret_formats")
        
        # GitHub token format: ghp_[36 characters]
        repo_token = self.secrets.get('REPO_SYNC_TOKEN')
        if repo_token:
            if re.match(r'^ghp_[A-Za-z0-9]{36}$', repo_token):
                result.add_info("REPO_SYNC_TOKEN format is valid")
            else:
                result.add_error("REPO_SYNC_TOKEN format is invalid (expected: ghp_[36 chars])")
        
        # ShadowScrolls endpoint format: https://domain/path
        ss_endpoint = self.secrets.get('SHADOWSCROLLS_ENDPOINT')
        if ss_endpoint:
            if re.match(r'^https?://[a-zA-Z0-9.-]+(/.*)?$', ss_endpoint):
                result.add_info("SHADOWSCROLLS_ENDPOINT format is valid")
            else:
                result.add_error("SHADOWSCROLLS_ENDPOINT format is invalid (expected: https://domain/path)")
        
        # ShadowScrolls API key format: ss_live_[32 characters]
        ss_key = self.secrets.get('SHADOWSCROLLS_API_KEY')
        if ss_key:
            if re.match(r'^ss_live_[A-Za-z0-9]{32}$', ss_key):
                result.add_info("SHADOWSCROLLS_API_KEY format is valid")
            else:
                result.add_error("SHADOWSCROLLS_API_KEY format is invalid (expected: ss_live_[32 chars])")
        
        result.set_passed(len(result.errors) == 0)
        return result
    
    def validate_github_connectivity(self) -> ValidationResult:
        """Test GitHub API connectivity and token validity"""
        result = ValidationResult("github_connectivity")
        
        repo_token = self.secrets.get('REPO_SYNC_TOKEN')
        if not repo_token:
            result.add_error("REPO_SYNC_TOKEN not available for testing")
            return result
        
        try:
            # Test GitHub API
            req = urllib.request.Request('https://api.github.com/user')
            req.add_header('Authorization', f'token {repo_token}')
            req.add_header('User-Agent', 'Triune-Swarm-Engine-Validator/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    username = data.get('login', 'unknown')
                    result.add_info(f"GitHub token is valid for user: {username}")
                    result.details['github_user'] = username
                    result.set_passed(True)
                else:
                    result.add_error(f"GitHub API returned status {response.status}")
        
        except urllib.error.HTTPError as e:
            if e.code == 401:
                result.add_error("GitHub token is invalid or expired")
            else:
                result.add_error(f"GitHub API error: {e.code} {e.reason}")
        except Exception as e:
            result.add_warning(f"Could not test GitHub connectivity: {str(e)}")
        
        return result
    
    def validate_shadowscrolls_connectivity(self) -> ValidationResult:
        """Test ShadowScrolls API connectivity"""
        result = ValidationResult("shadowscrolls_connectivity")
        
        endpoint = self.secrets.get('SHADOWSCROLLS_ENDPOINT')
        api_key = self.secrets.get('SHADOWSCROLLS_API_KEY')
        
        if not endpoint or not api_key:
            result.add_error("ShadowScrolls credentials not available for testing")
            return result
        
        try:
            # Try health endpoint first
            health_url = f"{endpoint.rstrip('/')}/health"
            req = urllib.request.Request(health_url)
            req.add_header('Authorization', f'Bearer {api_key}')
            req.add_header('User-Agent', 'Triune-Swarm-Engine-Validator/1.0')
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status in [200, 201]:
                        result.add_info("ShadowScrolls health endpoint is accessible")
                        result.set_passed(True)
                    else:
                        result.add_warning(f"ShadowScrolls health endpoint returned status {response.status}")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    result.add_info("ShadowScrolls health endpoint not found (this is normal)")
                    result.set_passed(True)
                elif e.code == 401:
                    result.add_error("ShadowScrolls API key is invalid")
                else:
                    result.add_warning(f"ShadowScrolls API error: {e.code}")
        
        except Exception as e:
            result.add_warning(f"Could not test ShadowScrolls connectivity: {str(e)}")
        
        return result
    
    def validate_file_structure(self) -> ValidationResult:
        """Validate required file and directory structure"""
        result = ValidationResult("file_structure")
        
        required_files = [
            'SECRETS_SETUP.md',
            'scripts/setup-secrets.sh',
            'scripts/validate-setup.py',
            '.shadowscrolls/reports/initial-setup-20250818-171022.json'
        ]
        
        optional_files = [
            '.env.local',
            '.gitignore'
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                result.add_info(f"Required file exists: {file_path}")
                
                # Check if script files are executable
                if file_path.endswith('.sh') and not os.access(full_path, os.X_OK):
                    result.add_warning(f"Script file is not executable: {file_path}")
            else:
                result.add_error(f"Required file missing: {file_path}")
        
        for file_path in optional_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                result.add_info(f"Optional file exists: {file_path}")
            else:
                result.add_info(f"Optional file not found: {file_path}")
        
        # Check directory structure
        required_dirs = [
            'scripts',
            '.shadowscrolls',
            '.shadowscrolls/reports'
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.is_dir():
                result.add_info(f"Required directory exists: {dir_path}")
            else:
                result.add_error(f"Required directory missing: {dir_path}")
        
        result.set_passed(len(result.errors) == 0)
        result.details['required_files_found'] = len([f for f in required_files if (self.project_root / f).exists()])
        result.details['total_required_files'] = len(required_files)
        
        return result
    
    def validate_shadowscrolls_report(self) -> ValidationResult:
        """Validate the initial ShadowScrolls report structure"""
        result = ValidationResult("shadowscrolls_report")
        
        report_path = self.project_root / '.shadowscrolls/reports/initial-setup-20250818-171022.json'
        
        if not report_path.exists():
            result.add_error("Initial ShadowScrolls report file not found")
            return result
        
        try:
            with open(report_path, 'r') as f:
                report_data = json.load(f)
            
            # Validate required fields
            required_fields = [
                'scroll_metadata',
                'setup_context',
                'configuration_status',
                'traceability_metadata'
            ]
            
            for field in required_fields:
                if field in report_data:
                    result.add_info(f"Report contains required field: {field}")
                else:
                    result.add_error(f"Report missing required field: {field}")
            
            # Validate scroll ID
            scroll_metadata = report_data.get('scroll_metadata', {})
            scroll_id = scroll_metadata.get('scroll_id')
            if scroll_id == "#001 – Initial Mirror Setup":
                result.add_info("Scroll ID is correct")
            else:
                result.add_error(f"Incorrect scroll ID: {scroll_id}")
            
            # Validate timestamp
            timestamp = scroll_metadata.get('timestamp')
            if timestamp == "2025-08-18T17:10:22Z":
                result.add_info("Timestamp is correct")
            else:
                result.add_warning(f"Unexpected timestamp: {timestamp}")
            
            result.set_passed(len(result.errors) == 0)
            result.details['report_size_bytes'] = report_path.stat().st_size
            result.details['fields_validated'] = len(required_fields)
        
        except json.JSONDecodeError as e:
            result.add_error(f"Invalid JSON in report file: {str(e)}")
        except Exception as e:
            result.add_error(f"Error reading report file: {str(e)}")
        
        return result
    
    def validate_environment_security(self) -> ValidationResult:
        """Check environment security configuration"""
        result = ValidationResult("environment_security")
        
        # Check .gitignore for .env.local
        gitignore_path = self.project_root / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
            
            if '.env.local' in gitignore_content:
                result.add_info(".env.local is excluded in .gitignore")
            else:
                result.add_warning(".env.local should be added to .gitignore")
        else:
            result.add_warning(".gitignore file not found")
        
        # Check for secrets in git history (basic check)
        env_file_tracked = False
        try:
            import subprocess
            git_result = subprocess.run(
                ['git', 'log', '--oneline', '--', '.env.local'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if git_result.stdout.strip():
                env_file_tracked = True
                result.add_error(".env.local has been committed to git history")
            else:
                result.add_info(".env.local has not been committed to git")
        except Exception:
            result.add_info("Could not check git history (git not available)")
        
        # Check file permissions
        if self.env_file.exists():
            file_mode = oct(self.env_file.stat().st_mode)[-3:]
            if file_mode in ['600', '644']:
                result.add_info(f"Environment file has appropriate permissions: {file_mode}")
            else:
                result.add_warning(f"Environment file permissions may be too permissive: {file_mode}")
        
        result.set_passed(len(result.errors) == 0)
        return result
    
    def run_validation(self) -> Dict[str, Any]:
        """Run all validation checks"""
        self.print_status("🔍 Starting Triune Swarm Engine setup validation...")
        
        # Define checks to run based on arguments
        all_checks = {
            'secrets': [self.validate_secrets_presence, self.validate_secret_formats],
            'api': [self.validate_github_connectivity, self.validate_shadowscrolls_connectivity],
            'permissions': [self.validate_environment_security],
            'structure': [self.validate_file_structure, self.validate_shadowscrolls_report]
        }
        
        checks_to_run = []
        
        if self.args.check_secrets:
            checks_to_run.extend(all_checks['secrets'])
        elif self.args.check_api:
            checks_to_run.extend(all_checks['api'])
        elif self.args.check_permissions:
            checks_to_run.extend(all_checks['permissions'])
        elif self.args.check_structure:
            checks_to_run.extend(all_checks['structure'])
        else:
            # Run all checks
            for check_list in all_checks.values():
                checks_to_run.extend(check_list)
        
        # Run selected checks
        for check_func in checks_to_run:
            self.debug_print(f"Running check: {check_func.__name__}")
            result = check_func()
            self.results.append(result)
            
            # Print immediate feedback
            if result.passed:
                self.print_status(f"{result.check_name}: PASSED", 'success')
            else:
                self.print_status(f"{result.check_name}: FAILED", 'error')
                for error in result.errors:
                    self.print_status(f"  ❌ {error}", 'error')
            
            for warning in result.warnings:
                self.print_status(f"  ⚠️  {warning}", 'warning')
        
        # Generate summary
        total_checks = len(self.results)
        passed_checks = len([r for r in self.results if r.passed])
        failed_checks = total_checks - passed_checks
        
        summary = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'validation_summary': {
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': failed_checks,
                'success_rate': round((passed_checks / total_checks) * 100, 2) if total_checks > 0 else 0
            },
            'results': [r.to_dict() for r in self.results],
            'overall_status': 'PASSED' if failed_checks == 0 else 'FAILED',
            'environment_file': str(self.env_file),
            'project_root': str(self.project_root)
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print validation summary"""
        if self.args.json:
            print(json.dumps(summary, indent=2))
            return
        
        print("\n" + "="*60)
        print(f"{Colors.BOLD}🔍 VALIDATION SUMMARY{Colors.NC}")
        print("="*60)
        
        validation_summary = summary['validation_summary']
        overall_status = summary['overall_status']
        
        status_color = Colors.GREEN if overall_status == 'PASSED' else Colors.RED
        print(f"\nOverall Status: {status_color}{overall_status}{Colors.NC}")
        
        print(f"\nChecks Summary:")
        print(f"  ✅ Passed: {validation_summary['passed_checks']}")
        print(f"  ❌ Failed: {validation_summary['failed_checks']}")
        print(f"  📊 Success Rate: {validation_summary['success_rate']}%")
        
        if validation_summary['failed_checks'] > 0:
            print(f"\n{Colors.YELLOW}⚠️  Issues Found:{Colors.NC}")
            for result in self.results:
                if not result.passed:
                    print(f"\n  🔴 {result.check_name}:")
                    for error in result.errors:
                        print(f"    ❌ {error}")
                    for warning in result.warnings:
                        print(f"    ⚠️  {warning}")
        
        print(f"\n{Colors.CYAN}📋 Next Steps:{Colors.NC}")
        if overall_status == 'PASSED':
            print("  🎉 All validations passed! Your setup is ready.")
            print("  🚀 You can now proceed with Mirror Watcher automation.")
        else:
            print("  🔧 Fix the issues above and run validation again.")
            print("  📖 Refer to SECRETS_SETUP.md for detailed instructions.")
        
        print(f"\nValidation completed at: {summary['timestamp']}")
        print("="*60)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Validate Triune Swarm Engine setup configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate-setup.py                    # Run all checks
  python scripts/validate-setup.py --check-secrets    # Only validate secrets
  python scripts/validate-setup.py --json             # Output JSON results
  python scripts/validate-setup.py --debug            # Enable debug output
        """
    )
    
    parser.add_argument('--check-secrets', action='store_true',
                        help='Only validate secret presence and format')
    parser.add_argument('--check-api', action='store_true',
                        help='Only test API connectivity')
    parser.add_argument('--check-permissions', action='store_true',
                        help='Only verify access permissions')
    parser.add_argument('--check-structure', action='store_true',
                        help='Only validate file and directory structure')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output')
    parser.add_argument('--env-file', type=str,
                        help='Custom environment file path')
    parser.add_argument('--quiet', action='store_true',
                        help='Minimal output mode')
    parser.add_argument('--json', action='store_true',
                        help='Output results in JSON format')
    
    args = parser.parse_args()
    
    try:
        validator = SetupValidator(args)
        summary = validator.run_validation()
        validator.print_summary(summary)
        
        # Exit with error code if validation failed
        exit_code = 0 if summary['overall_status'] == 'PASSED' else 1
        sys.exit(exit_code)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Validation interrupted by user{Colors.NC}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}❌ Validation failed with error: {str(e)}{Colors.NC}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()