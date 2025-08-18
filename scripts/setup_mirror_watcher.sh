#!/bin/bash
# MirrorWatcherAI Setup Script
# Automated deployment and configuration for the complete automation system

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_ROOT/config"
DOCS_DIR="$PROJECT_ROOT/docs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Validate Python version
validate_python() {
    log_step "Validating Python installation..."
    
    if ! command_exists python3; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    required_version="3.9"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        log_error "Python $required_version or higher is required (found: $python_version)"
        exit 1
    fi
    
    log_success "Python $python_version detected"
}

# Install Python dependencies
install_dependencies() {
    log_step "Installing Python dependencies..."
    
    # Update requirements.txt to include MirrorWatcherAI dependencies
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        # Backup original requirements
        cp "$PROJECT_ROOT/requirements.txt" "$PROJECT_ROOT/requirements.txt.backup"
    fi
    
    # Use our enhanced requirements
    cp "$PROJECT_ROOT/requirements_mirror_watcher.txt" "$PROJECT_ROOT/requirements.txt"
    
    # Install dependencies
    python3 -m pip install --upgrade pip
    python3 -m pip install -r "$PROJECT_ROOT/requirements.txt"
    
    log_success "Dependencies installed successfully"
}

# Create directory structure
create_directories() {
    log_step "Creating directory structure..."
    
    directories=(
        "$CONFIG_DIR"
        "$DOCS_DIR"
        "$PROJECT_ROOT/tests"
        "$PROJECT_ROOT/results"
        "$PROJECT_ROOT/.lineage"
        "$PROJECT_ROOT/swarm_data"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        fi
    done
    
    log_success "Directory structure created"
}

# Validate configuration files
validate_configuration() {
    log_step "Validating configuration files..."
    
    config_files=(
        "$CONFIG_DIR/mirror_watcher_config.json"
        "$CONFIG_DIR/triune_endpoints.json"
    )
    
    for config_file in "${config_files[@]}"; do
        if [ ! -f "$config_file" ]; then
            log_error "Configuration file missing: $config_file"
            exit 1
        fi
        
        # Validate JSON syntax
        if ! python3 -m json.tool "$config_file" >/dev/null 2>&1; then
            log_error "Invalid JSON in configuration file: $config_file"
            exit 1
        fi
        
        log_success "Configuration file validated: $(basename "$config_file")"
    done
}

# Test MirrorWatcherAI modules
test_modules() {
    log_step "Testing MirrorWatcherAI module imports..."
    
    python3 -c "
import sys
sys.path.append('$PROJECT_ROOT')
try:
    from src.mirror_watcher_ai import cli_main, TriuneAnalyzer, ShadowScrollsClient, MirrorLineage, TriuneIntegrator
    print('✅ All MirrorWatcherAI modules imported successfully')
except ImportError as e:
    print(f'❌ Module import failed: {e}')
    sys.exit(1)
" || {
        log_error "Module import test failed"
        exit 1
    }
    
    log_success "Module import test passed"
}

# Check environment variables
check_environment() {
    log_step "Checking environment configuration..."
    
    required_secrets=(
        "REPO_SYNC_TOKEN"
        "SHADOWSCROLLS_ENDPOINT"
        "SHADOWSCROLLS_API_KEY"
    )
    
    optional_secrets=(
        "LEGIO_COGNITO_API_KEY"
        "TRIUMVIRATE_MONITOR_API_KEY"
    )
    
    missing_required=()
    missing_optional=()
    
    for secret in "${required_secrets[@]}"; do
        if [ -z "${!secret:-}" ]; then
            missing_required+=("$secret")
        else
            log_success "$secret is configured"
        fi
    done
    
    for secret in "${optional_secrets[@]}"; do
        if [ -z "${!secret:-}" ]; then
            missing_optional+=("$secret")
        else
            log_success "$secret is configured"
        fi
    done
    
    if [ ${#missing_required[@]} -gt 0 ]; then
        log_error "Required environment variables missing:"
        for secret in "${missing_required[@]}"; do
            log_error "  - $secret"
        done
        log_info "Please configure these in GitHub Secrets or environment variables"
        exit 1
    fi
    
    if [ ${#missing_optional[@]} -gt 0 ]; then
        log_warning "Optional environment variables missing:"
        for secret in "${missing_optional[@]}"; do
            log_warning "  - $secret"
        done
        log_info "These services will use mock implementations"
    fi
}

# Test CLI functionality
test_cli() {
    log_step "Testing MirrorWatcherAI CLI..."
    
    cd "$PROJECT_ROOT"
    
    # Test version command
    if python3 -m src.mirror_watcher_ai.cli version >/dev/null 2>&1; then
        log_success "CLI version command works"
    else
        log_error "CLI version command failed"
        exit 1
    fi
    
    # Test help command
    if python3 -m src.mirror_watcher_ai.cli --help >/dev/null 2>&1; then
        log_success "CLI help command works"
    else
        log_error "CLI help command failed"
        exit 1
    fi
    
    log_success "CLI functionality test passed"
}

# Setup GitHub Actions workflow
setup_workflow() {
    log_step "Validating GitHub Actions workflow..."
    
    workflow_file="$PROJECT_ROOT/.github/workflows/mirror-watcher-automation.yml"
    
    if [ ! -f "$workflow_file" ]; then
        log_error "GitHub Actions workflow file missing: $workflow_file"
        exit 1
    fi
    
    # Basic YAML validation (if yamllint is available)
    if command_exists yamllint; then
        if yamllint "$workflow_file" >/dev/null 2>&1; then
            log_success "Workflow YAML is valid"
        else
            log_warning "Workflow YAML validation failed (yamllint)"
        fi
    else
        log_info "yamllint not available, skipping YAML validation"
    fi
    
    log_success "GitHub Actions workflow validated"
}

# Create initial lineage
initialize_lineage() {
    log_step "Initializing MirrorLineage system..."
    
    cd "$PROJECT_ROOT"
    
    python3 -c "
import sys
sys.path.append('.')
from src.mirror_watcher_ai.lineage import MirrorLineage
import json

# Initialize lineage with default config
config = {
    'encryption': True,
    'hash_algorithm': 'sha256',
    'compression': True,
    'storage_path': './.lineage'
}

lineage = MirrorLineage(config)
print('✅ MirrorLineage initialized successfully')
" || {
        log_error "MirrorLineage initialization failed"
        exit 1
    }
    
    log_success "MirrorLineage system initialized"
}

# Main setup function
main() {
    echo "🚀 MirrorWatcherAI Complete Automation System Setup"
    echo "=================================================="
    echo ""
    
    log_info "Starting setup process..."
    echo ""
    
    # Run setup steps
    validate_python
    echo ""
    
    create_directories
    echo ""
    
    install_dependencies
    echo ""
    
    validate_configuration
    echo ""
    
    test_modules
    echo ""
    
    check_environment
    echo ""
    
    test_cli
    echo ""
    
    setup_workflow
    echo ""
    
    initialize_lineage
    echo ""
    
    # Final success message
    echo "🎉 MirrorWatcherAI Setup Complete!"
    echo "=================================="
    echo ""
    log_success "All components are ready for automated operation"
    log_info "Next steps:"
    echo "  1. Ensure GitHub Secrets are configured:"
    echo "     - REPO_SYNC_TOKEN"
    echo "     - SHADOWSCROLLS_ENDPOINT"
    echo "     - SHADOWSCROLLS_API_KEY"
    echo "  2. The workflow will run daily at 06:00 UTC"
    echo "  3. Manual execution: python3 -m src.mirror_watcher_ai.cli daily"
    echo "  4. Health check: python3 -m src.mirror_watcher_ai.cli --help"
    echo ""
    echo "🔗 First automated run scheduled for tomorrow at 06:00 UTC"
    echo "📊 Results will be available in GitHub Actions artifacts"
    echo "🛡️ ShadowScrolls attestation will be automatically submitted"
    echo ""
}

# Run main function
main "$@"