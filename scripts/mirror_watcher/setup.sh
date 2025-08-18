#!/bin/bash
set -euo pipefail

# MirrorWatcherAI Setup Script
# Installs and configures the complete MirrorWatcherAI automation system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    MirrorWatcherAI Setup                    ║"
    echo "║              Complete Automation System                     ║"
    echo "║                  Triune Oracle Ecosystem                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    log_info "Checking Python installation..."
    
    if ! command_exists python3; then
        log_error "Python 3 is required but not installed"
        return 1
    fi
    
    local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    local required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        log_error "Python $required_version or higher is required. Found: $python_version"
        return 1
    fi
    
    log_success "Python $python_version found"
    return 0
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Install requirements
    if [ -f requirements.txt ]; then
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
        log_success "Core dependencies installed"
    fi
    
    # Install additional MirrorWatcherAI dependencies
    python3 -m pip install aiohttp>=3.8.0
    log_success "MirrorWatcherAI dependencies installed"
}

# Create necessary directories
create_directories() {
    log_info "Creating directory structure..."
    
    cd "$PROJECT_ROOT"
    
    # Create main directories
    mkdir -p .shadowscrolls/reports
    mkdir -p .mirror_lineage/deltas
    mkdir -p .legio_cognito/archive
    mkdir -p .triune_monitor
    
    # Set permissions
    chmod 755 .shadowscrolls .mirror_lineage .legio_cognito .triune_monitor
    chmod 755 .shadowscrolls/reports .mirror_lineage/deltas .legio_cognito/archive
    
    log_success "Directory structure created"
}

# Validate environment variables
validate_environment() {
    log_info "Validating environment configuration..."
    
    local required_vars=(
        "REPO_SYNC_TOKEN"
        "SHADOWSCROLLS_ENDPOINT"
        "SHADOWSCROLLS_API_KEY"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_warning "Missing environment variables: ${missing_vars[*]}"
        log_info "Run scripts/setup-secrets.sh to configure secrets"
        return 1
    fi
    
    log_success "Environment variables configured"
    return 0
}

# Test MirrorWatcherAI installation
test_installation() {
    log_info "Testing MirrorWatcherAI installation..."
    
    cd "$PROJECT_ROOT"
    
    # Test import
    if python3 -c "from src.mirror_watcher_ai import cli_main" 2>/dev/null; then
        log_success "Module import successful"
    else
        log_error "Failed to import MirrorWatcherAI module"
        return 1
    fi
    
    # Test CLI
    if python3 -m src.mirror_watcher_ai.cli --help >/dev/null 2>&1; then
        log_success "CLI interface working"
    else
        log_error "CLI interface not working"
        return 1
    fi
    
    # Test validation if environment is configured
    if validate_environment >/dev/null 2>&1; then
        if python3 -m src.mirror_watcher_ai.cli --validate >/dev/null 2>&1; then
            log_success "Validation test passed"
        else
            log_warning "Validation test failed (check configuration)"
        fi
    else
        log_info "Skipping validation test (environment not configured)"
    fi
    
    return 0
}

# Setup GitHub Actions workflow
setup_workflow() {
    log_info "Checking GitHub Actions workflow..."
    
    local workflow_file="$PROJECT_ROOT/.github/workflows/mirror-watcher-daily.yml"
    
    if [ -f "$workflow_file" ]; then
        log_success "GitHub Actions workflow found"
    else
        log_warning "GitHub Actions workflow not found"
        log_info "Workflow should be at: $workflow_file"
    fi
}

# Generate initial configuration
generate_config() {
    log_info "Checking configuration files..."
    
    local config_dir="$PROJECT_ROOT/config/mirror_watcher"
    
    if [ -d "$config_dir" ]; then
        log_success "Configuration directory found"
        
        local config_files=("default.json" "repositories.json" "attestation.json" "legio_config.json")
        local missing_configs=()
        
        for config in "${config_files[@]}"; do
            if [ ! -f "$config_dir/$config" ]; then
                missing_configs+=("$config")
            fi
        done
        
        if [ ${#missing_configs[@]} -gt 0 ]; then
            log_warning "Missing configuration files: ${missing_configs[*]}"
        else
            log_success "All configuration files present"
        fi
    else
        log_warning "Configuration directory not found: $config_dir"
    fi
}

# Update .gitignore
update_gitignore() {
    log_info "Updating .gitignore..."
    
    cd "$PROJECT_ROOT"
    
    local gitignore_entries=(
        "# MirrorWatcherAI artifacts"
        ".shadowscrolls/reports/*.json"
        ".mirror_lineage/current_state.json"
        ".legio_cognito/archive/*.json"
        ".triune_monitor/*.json"
        "mirror_watcher_results.json"
    )
    
    local gitignore_file=".gitignore"
    local needs_update=false
    
    for entry in "${gitignore_entries[@]}"; do
        if ! grep -Fxq "$entry" "$gitignore_file" 2>/dev/null; then
            needs_update=true
            break
        fi
    done
    
    if [ "$needs_update" = true ]; then
        echo "" >> "$gitignore_file"
        echo "# MirrorWatcherAI artifacts" >> "$gitignore_file"
        echo ".shadowscrolls/reports/*.json" >> "$gitignore_file"
        echo ".mirror_lineage/current_state.json" >> "$gitignore_file"
        echo ".legio_cognito/archive/*.json" >> "$gitignore_file"
        echo ".triune_monitor/*.json" >> "$gitignore_file"
        echo "mirror_watcher_results.json" >> "$gitignore_file"
        
        log_success "Updated .gitignore"
    else
        log_success ".gitignore already configured"
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    log_info "Setup completed! Next steps:"
    echo ""
    echo "1. Configure secrets (if not already done):"
    echo "   ./scripts/setup-secrets.sh --interactive"
    echo ""
    echo "2. Validate installation:"
    echo "   python3 -m src.mirror_watcher_ai.cli --validate"
    echo ""
    echo "3. Run manual test:"
    echo "   python3 -m src.mirror_watcher_ai.cli --analyze"
    echo ""
    echo "4. Check GitHub Actions workflow:"
    echo "   - Workflow runs daily at 06:00 UTC"
    echo "   - Can be triggered manually from GitHub Actions tab"
    echo ""
    echo "5. Monitor execution:"
    echo "   - Results stored in workflow artifacts"
    echo "   - Status updates sent to Triune Monitor"
    echo "   - ShadowScrolls attestations created"
    echo ""
    log_success "MirrorWatcherAI is ready for automated operation!"
}

# Main setup function
main() {
    print_banner
    
    log_info "Starting MirrorWatcherAI setup..."
    log_info "Project root: $PROJECT_ROOT"
    
    # Run setup steps
    if ! check_python; then
        log_error "Python check failed"
        exit 1
    fi
    
    if ! install_dependencies; then
        log_error "Dependency installation failed"
        exit 1
    fi
    
    create_directories
    generate_config
    setup_workflow
    update_gitignore
    
    if ! test_installation; then
        log_error "Installation test failed"
        exit 1
    fi
    
    show_next_steps
    
    log_success "MirrorWatcherAI setup completed successfully!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi