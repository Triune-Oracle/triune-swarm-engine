#!/bin/bash

# 🔍 MirrorWatcherAI Setup Script
# Complete automation system setup for production deployment

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_VERSION="1.0.0"
readonly SCRIPT_NAME="MirrorWatcherAI Setup"
readonly LOG_FILE="mirror_watcher_setup.log"
readonly BACKUP_DIR=".backup/$(date +%Y%m%d_%H%M%S)"

# Global variables
FORCE_SETUP=false
DRY_RUN=false
VERBOSE=false
SKIP_DEPS=false

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${LOG_FILE}"
}

# Print functions
print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    🔍 MIRRORWATCHERAI SETUP                     ║"
    echo "║                  Complete Automation System                      ║"
    echo "║                        Version ${SCRIPT_VERSION}                          ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
    log "INFO" "STEP: $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS" "$1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING" "$1"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    log "ERROR" "$1"
}

print_info() {
    echo -e "${WHITE}ℹ️  $1${NC}"
    log "INFO" "$1"
}

# Help function
show_help() {
    cat << EOF
${SCRIPT_NAME} v${SCRIPT_VERSION}

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -f, --force         Force setup even if already configured
    -d, --dry-run       Show what would be done without making changes
    -v, --verbose       Enable verbose output
    -s, --skip-deps     Skip dependency installation
    -h, --help          Show this help message

EXAMPLES:
    $0                  # Standard setup
    $0 --force          # Force re-setup
    $0 --dry-run        # Preview changes
    $0 --verbose        # Detailed output

EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--force)
                FORCE_SETUP=true
                shift
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -s|--skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites"
    
    local missing_deps=()
    
    # Check required commands
    local required_commands=("python3" "pip3" "git" "jq" "curl")
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        print_info "Please install missing dependencies and try again"
        exit 1
    fi
    
    # Check Python version
    local python_version
    python_version=$(python3 --version | cut -d' ' -f2)
    local required_version="3.9"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
        print_error "Python 3.9+ required. Found: ${python_version}"
        exit 1
    fi
    
    print_success "All prerequisites satisfied"
}

# Create directory structure
create_directories() {
    print_step "Creating directory structure"
    
    local directories=(
        "src/mirror_watcher_ai"
        "config"
        "docs"
        "tests"
        "scripts"
        ".shadowscrolls/lineage"
        ".shadowscrolls/attestations"
        ".shadowscrolls/legio_archive"
        ".shadowscrolls/dashboard"
        ".shadowscrolls/reports"
        ".cache/mirror_watcher"
        "logs"
        "artifacts"
    )
    
    for dir in "${directories[@]}"; do
        if [[ "$DRY_RUN" == "true" ]]; then
            print_info "Would create directory: $dir"
        else
            mkdir -p "$dir"
            if [[ "$VERBOSE" == "true" ]]; then
                print_info "Created directory: $dir"
            fi
        fi
    done
    
    print_success "Directory structure created"
}

# Install Python dependencies
install_dependencies() {
    if [[ "$SKIP_DEPS" == "true" ]]; then
        print_info "Skipping dependency installation"
        return 0
    fi
    
    print_step "Installing Python dependencies"
    
    local dependencies=(
        "aiohttp>=3.8.0"
        "aiosqlite>=0.19.0"
        "GitPython>=3.1.0"
        "requests>=2.28.0"
        "pydantic>=2.0.0"
        "cryptography>=3.4.0"
        "click>=8.0.0"
        "rich>=13.0.0"
        "pytest>=7.0.0"
        "pytest-asyncio>=0.21.0"
    )
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "Would install dependencies:"
        printf '%s\n' "${dependencies[@]}"
    else
        # Update pip first
        python3 -m pip install --upgrade pip
        
        # Install dependencies
        for dep in "${dependencies[@]}"; do
            if [[ "$VERBOSE" == "true" ]]; then
                print_info "Installing: $dep"
            fi
            python3 -m pip install "$dep"
        done
    fi
    
    print_success "Dependencies installed"
}

# Configure environment
configure_environment() {
    print_step "Configuring environment"
    
    local env_file=".env.mirror_watcher"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "Would create environment file: $env_file"
        return 0
    fi
    
    # Create environment template
    cat > "$env_file" << 'EOF'
# MirrorWatcherAI Environment Configuration
# Generated by setup script

# GitHub Integration
# REPO_SYNC_TOKEN=your_github_token_here

# ShadowScrolls Configuration
# SHADOWSCROLLS_ENDPOINT=https://api.shadowscrolls.triune-oracle.com/v1
# SHADOWSCROLLS_API_KEY=your_shadowscrolls_api_key_here

# Triune Ecosystem Integration
# LEGIO_COGNITO_API_KEY=your_legio_cognito_api_key_here
# TRIUMVIRATE_MONITOR_API_KEY=your_triumvirate_monitor_api_key_here
# SWARM_ENGINE_API_KEY=your_swarm_engine_api_key_here

# Operational Configuration
MIRROR_WATCHER_LOG_FILE=logs/mirror_watcher.log
MIRROR_WATCHER_LOG_LEVEL=INFO
MIRROR_WATCHER_CACHE_DIR=.cache/mirror_watcher

# Development Settings (uncomment for development)
# MIRROR_WATCHER_DEBUG=true
# MIRROR_WATCHER_VERBOSE=true
EOF
    
    print_success "Environment configuration created: $env_file"
    print_warning "Please update $env_file with your actual API keys"
}

# Setup database
setup_database() {
    print_step "Setting up lineage database"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "Would initialize lineage database"
        return 0
    fi
    
    # Initialize database using Python
    python3 -c "
import asyncio
import sys
import os
sys.path.insert(0, '.')

async def setup_db():
    try:
        from src.mirror_watcher_ai.lineage import MirrorLineageLogger
        logger = MirrorLineageLogger()
        await logger._initialize_database()
        print('Database initialized successfully')
    except Exception as e:
        print(f'Database setup failed: {e}')
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(setup_db())
"
    
    if [[ $? -eq 0 ]]; then
        print_success "Lineage database initialized"
    else
        print_error "Database initialization failed"
        exit 1
    fi
}

# Create initial configuration
create_initial_config() {
    print_step "Creating initial configuration"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "Would create initial ShadowScrolls report"
        return 0
    fi
    
    # Create initial ShadowScrolls report
    local report_file=".shadowscrolls/reports/initial-setup-$(date +%Y%m%d-%H%M%S).json"
    
    cat > "$report_file" << EOF
{
  "scroll_metadata": {
    "scroll_id": "#001 – Initial MirrorWatcherAI Setup",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "system": "MirrorWatcherAI Automation Setup",
    "version": "${SCRIPT_VERSION}"
  },
  "setup_context": {
    "setup_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "setup_user": "${USER:-unknown}",
    "setup_environment": "$(uname -s)",
    "setup_method": "automated_script",
    "force_setup": ${FORCE_SETUP},
    "dry_run": ${DRY_RUN}
  },
  "configuration_status": {
    "directories_created": true,
    "dependencies_installed": $([ "$SKIP_DEPS" == "true" ] && echo "false" || echo "true"),
    "environment_configured": true,
    "database_initialized": true,
    "initial_config_created": true
  },
  "traceability_metadata": {
    "setup_script_version": "${SCRIPT_VERSION}",
    "configuration_hash": "$(echo -n "$SCRIPT_VERSION-$(date +%s)" | sha256sum | cut -d' ' -f1)",
    "verification_method": "script_execution",
    "audit_trail": {
      "setup_initiated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "setup_completed": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
  },
  "next_steps": {
    "configure_secrets": "Update .env.mirror_watcher with actual API keys",
    "run_validation": "Execute scripts/validate-setup.py",
    "test_system": "Run python -m src.mirror_watcher_ai.cli health",
    "schedule_automation": "GitHub Actions workflow is ready for deployment"
  }
}
EOF
    
    print_success "Initial configuration report created: $report_file"
}

# Validate installation
validate_installation() {
    print_step "Validating installation"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "Would validate installation"
        return 0
    fi
    
    # Test Python imports
    python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from src.mirror_watcher_ai import MirrorWatcherCLI, TriuneAnalyzer
    print('✅ Core modules import successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)

try:
    from src.mirror_watcher_ai.shadowscrolls import ShadowScrollsIntegration
    from src.mirror_watcher_ai.lineage import MirrorLineageLogger
    from src.mirror_watcher_ai.triune_integration import TriuneEcosystemConnector
    print('✅ All modules import successfully')
except ImportError as e:
    print(f'❌ Module import failed: {e}')
    sys.exit(1)
"
    
    if [[ $? -eq 0 ]]; then
        print_success "Module validation passed"
    else
        print_error "Module validation failed"
        exit 1
    fi
    
    # Test CLI accessibility
    if python3 -m src.mirror_watcher_ai.cli --help &> /dev/null; then
        print_success "CLI interface accessible"
    else
        print_warning "CLI interface may have issues"
    fi
    
    # Check file permissions
    local critical_files=(
        "src/mirror_watcher_ai/cli.py"
        "config/mirror_watcher_config.json"
        "config/triune_endpoints.json"
        ".shadowscrolls/lineage/mirror_lineage.db"
    )
    
    for file in "${critical_files[@]}"; do
        if [[ -f "$file" ]]; then
            if [[ "$VERBOSE" == "true" ]]; then
                print_info "File exists: $file"
            fi
        else
            print_warning "Missing file: $file"
        fi
    done
    
    print_success "Installation validation completed"
}

# Generate usage instructions
generate_usage_instructions() {
    print_step "Generating usage instructions"
    
    local instructions_file="MIRRORWATCHER_USAGE.md"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "Would create usage instructions: $instructions_file"
        return 0
    fi
    
    cat > "$instructions_file" << 'EOF'
# 🔍 MirrorWatcherAI Usage Instructions

## Quick Start

1. **Configure API Keys**
   ```bash
   # Edit the environment file
   nano .env.mirror_watcher
   
   # Add your actual API keys
   REPO_SYNC_TOKEN=ghp_your_github_token
   SHADOWSCROLLS_API_KEY=ss_live_your_api_key
   # ... etc
   ```

2. **Validate Setup**
   ```bash
   # Run system validation
   python3 scripts/validate-setup.py
   
   # Test health check
   python3 -m src.mirror_watcher_ai.cli health
   ```

3. **Run Analysis**
   ```bash
   # Full analysis
   python3 -m src.mirror_watcher_ai.cli analyze
   
   # Repository scan only
   python3 -m src.mirror_watcher_ai.cli scan
   
   # Create attestation
   python3 -m src.mirror_watcher_ai.cli attest --data analysis_results.json
   
   # Sync ecosystem
   python3 -m src.mirror_watcher_ai.cli sync
   ```

## Automation

The GitHub Actions workflow is configured for daily execution at 06:00 UTC.
Manual triggers are available via the Actions tab in GitHub.

## Monitoring

- **Logs**: Check `logs/mirror_watcher.log`
- **Artifacts**: Available in GitHub Actions artifacts
- **Dashboard**: Local dashboard at `.shadowscrolls/dashboard/dashboard.html`

## Troubleshooting

- Run health check: `python3 -m src.mirror_watcher_ai.cli health`
- Check logs: `tail -f logs/mirror_watcher.log`
- Validate setup: `python3 scripts/validate-setup.py --debug`

EOF
    
    print_success "Usage instructions created: $instructions_file"
}

# Cleanup function
cleanup() {
    if [[ -f "$LOG_FILE" ]]; then
        print_info "Setup log saved to: $LOG_FILE"
    fi
}

# Main setup function
main() {
    # Set up cleanup trap
    trap cleanup EXIT
    
    # Parse arguments
    parse_arguments "$@"
    
    # Start setup
    print_header
    print_info "Starting MirrorWatcherAI setup..."
    print_info "Setup mode: $([ "$DRY_RUN" == "true" ] && echo "DRY RUN" || echo "LIVE")"
    
    # Check if already set up
    if [[ -f "src/mirror_watcher_ai/__init__.py" ]] && [[ "$FORCE_SETUP" == "false" ]]; then
        print_warning "MirrorWatcherAI appears to already be set up"
        print_info "Use --force to re-run setup"
        exit 0
    fi
    
    # Execute setup steps
    check_prerequisites
    create_directories
    install_dependencies
    configure_environment
    setup_database
    create_initial_config
    validate_installation
    generate_usage_instructions
    
    # Final success message
    echo
    print_success "🎉 MirrorWatcherAI setup completed successfully!"
    echo
    print_info "Next steps:"
    echo "  1. Configure your API keys in .env.mirror_watcher"
    echo "  2. Run: python3 scripts/validate-setup.py"
    echo "  3. Test: python3 -m src.mirror_watcher_ai.cli health"
    echo "  4. See: MIRRORWATCHER_USAGE.md for detailed instructions"
    echo
    print_info "The system is ready for automated execution at 06:00 UTC daily"
}

# Execute main function
main "$@"