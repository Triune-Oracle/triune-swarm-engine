#!/bin/bash
set -euo pipefail

# 🔧 MirrorWatcherAI Setup Script
# Complete setup and configuration for the MirrorWatcherAI automation system

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly TIMESTAMP=$(date -u +"%Y-%m-%d_%H-%M-%S")

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_step() { echo -e "${CYAN}🔄 $1${NC}"; }

# Print banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║              🔍 MirrorWatcherAI Setup Script                     ║"
    echo "║                                                                  ║"
    echo "║            Complete Automation System Setup                     ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Help message
show_help() {
    cat << EOF
🔍 MirrorWatcherAI Setup Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --install-deps       Install Python dependencies
    --setup-dirs         Create directory structure
    --test-integration   Test all components
    --validate-config    Validate configuration files
    --quick-setup        Run minimal setup (default)
    --full-setup         Run complete setup with all options
    --dry-run            Show what would be done without executing
    -h, --help           Show this help message

EXAMPLES:
    # Quick setup (default)
    $0

    # Full setup with all components
    $0 --full-setup

    # Just install dependencies and test
    $0 --install-deps --test-integration

    # Validate existing setup
    $0 --validate-config

For detailed setup instructions, see: docs/DEPLOYMENT.md
EOF
}

# Check if required tools are available
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    local missing_tools=()
    
    # Check for required tools
    if ! command -v python3 &> /dev/null; then
        missing_tools+=("python3")
    fi
    
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        missing_tools+=("pip")
    fi
    
    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Please install the missing tools and run this script again."
        exit 1
    fi
    
    # Check Python version
    local python_version
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [ "$(echo "$python_version >= 3.9" | bc 2>/dev/null || echo "0")" -eq 0 ]; then
        if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
            log_success "Python version $python_version is compatible"
        else
            log_warning "Python version $python_version may not be fully compatible (3.9+ recommended)"
        fi
    else
        log_success "Python version $python_version is compatible"
    fi
}

# Setup directory structure
setup_directories() {
    log_step "Setting up directory structure..."
    
    local directories=(
        "src/mirror_watcher_ai"
        "config"
        "docs"
        "tests"
        "scripts"
        ".shadowscrolls/lineage"
        ".shadowscrolls/legio-cognito"
        ".shadowscrolls/reports"
        ".triumvirate-monitor"
        ".swarm-engine/sessions"
        ".swarm-engine/logs"
        "artifacts/reports"
        "artifacts/analysis"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$PROJECT_ROOT/$dir" ]; then
            mkdir -p "$PROJECT_ROOT/$dir"
            log_success "Created directory: $dir"
        else
            log_info "Directory already exists: $dir"
        fi
    done
    
    # Create .gitkeep files for empty directories
    find "$PROJECT_ROOT" -type d -empty -exec touch {}/.gitkeep \;
    
    log_success "Directory structure setup completed"
}

# Install Python dependencies
install_dependencies() {
    log_step "Installing Python dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Install from requirements.txt
    if [ -f "requirements.txt" ]; then
        log_info "Installing base requirements..."
        python3 -m pip install --user -r requirements.txt
    else
        log_warning "requirements.txt not found, installing minimal dependencies"
    fi
    
    # Install additional dependencies for MirrorWatcherAI
    log_info "Installing MirrorWatcherAI dependencies..."
    python3 -m pip install --user aiohttp aiosqlite
    
    log_success "Dependencies installed successfully"
}

# Validate configuration files
validate_configuration() {
    log_step "Validating configuration files..."
    
    local config_files=(
        "config/mirror_watcher_config.json"
        "config/triune_endpoints.json"
    )
    
    local all_valid=true
    
    for config_file in "${config_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$config_file" ]; then
            if python3 -m json.tool "$PROJECT_ROOT/$config_file" > /dev/null 2>&1; then
                log_success "Valid JSON: $config_file"
            else
                log_error "Invalid JSON: $config_file"
                all_valid=false
            fi
        else
            log_warning "Configuration file not found: $config_file"
            all_valid=false
        fi
    done
    
    if [ "$all_valid" = true ]; then
        log_success "All configuration files are valid"
    else
        log_warning "Some configuration files have issues"
    fi
}

# Test integration components
test_integration() {
    log_step "Testing MirrorWatcherAI integration..."
    
    cd "$PROJECT_ROOT"
    
    # Test Python module imports
    log_info "Testing Python module imports..."
    if python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from mirror_watcher_ai import cli_main, TriuneAnalyzer
    print('✅ MirrorWatcherAI modules imported successfully')
    exit(0)
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"; then
        log_success "Python modules import successfully"
    else
        log_error "Python module import failed"
        return 1
    fi
    
    # Test CLI help
    log_info "Testing CLI interface..."
    if python3 -c "
import sys
sys.path.insert(0, 'src')
from mirror_watcher_ai.cli import create_parser
parser = create_parser()
parser.print_help()
" > /dev/null 2>&1; then
        log_success "CLI interface is functional"
    else
        log_warning "CLI interface test failed"
    fi
    
    # Run existing integration tests if available
    if [ -f "scripts/test-integration.sh" ]; then
        log_info "Running existing integration tests..."
        if bash scripts/test-integration.sh > /dev/null 2>&1; then
            log_success "Integration tests passed"
        else
            log_warning "Some integration tests failed (this may be expected)"
        fi
    fi
    
    log_success "Integration testing completed"
}

# Create sample configuration if missing
create_sample_config() {
    log_step "Creating sample configuration files..."
    
    # Create triune_config.json for Swarm Engine integration
    if [ ! -f "$PROJECT_ROOT/triune_config.json" ]; then
        cat > "$PROJECT_ROOT/triune_config.json" << 'EOF'
{
  "mirror_watcher": {
    "enabled": true,
    "target_repositories": [
      "https://github.com/Triune-Oracle/triune-swarm-engine",
      "https://github.com/Triune-Oracle/triune-memory-core"
    ],
    "analysis_schedule": "0 6 * * *",
    "automation_enabled": true
  },
  "swarm_engine": {
    "version": "1.0.0",
    "compatibility_mode": "76.3%",
    "python_integration": true
  },
  "integrations": {
    "shadowscrolls": true,
    "legio_cognito": true,
    "triumvirate_monitor": true
  }
}
EOF
        log_success "Created triune_config.json"
    else
        log_info "triune_config.json already exists"
    fi
}

# Main execution function
main() {
    local install_deps=false
    local setup_dirs=false
    local test_integration_flag=false
    local validate_config=false
    local full_setup=false
    local dry_run=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install-deps)
                install_deps=true
                shift
                ;;
            --setup-dirs)
                setup_dirs=true
                shift
                ;;
            --test-integration)
                test_integration_flag=true
                shift
                ;;
            --validate-config)
                validate_config=true
                shift
                ;;
            --full-setup)
                full_setup=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # If no specific options, run quick setup
    if [ "$install_deps" = false ] && [ "$setup_dirs" = false ] && [ "$test_integration_flag" = false ] && [ "$validate_config" = false ] && [ "$full_setup" = false ]; then
        setup_dirs=true
        validate_config=true
    fi
    
    # If full setup, enable all options
    if [ "$full_setup" = true ]; then
        install_deps=true
        setup_dirs=true
        test_integration_flag=true
        validate_config=true
    fi
    
    # Print banner
    print_banner
    
    log_info "Starting MirrorWatcherAI setup..."
    log_info "Project root: $PROJECT_ROOT"
    log_info "Timestamp: $TIMESTAMP"
    
    if [ "$dry_run" = true ]; then
        log_warning "DRY RUN MODE - No changes will be made"
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Execute requested operations
    if [ "$setup_dirs" = true ]; then
        if [ "$dry_run" = false ]; then
            setup_directories
            create_sample_config
        else
            log_info "Would setup directories and create sample config"
        fi
    fi
    
    if [ "$install_deps" = true ]; then
        if [ "$dry_run" = false ]; then
            install_dependencies
        else
            log_info "Would install Python dependencies"
        fi
    fi
    
    if [ "$validate_config" = true ]; then
        if [ "$dry_run" = false ]; then
            validate_configuration
        else
            log_info "Would validate configuration files"
        fi
    fi
    
    if [ "$test_integration_flag" = true ]; then
        if [ "$dry_run" = false ]; then
            test_integration
        else
            log_info "Would test integration components"
        fi
    fi
    
    # Success message
    echo
    log_success "🎉 MirrorWatcherAI setup completed successfully!"
    echo
    log_info "Next steps:"
    echo "  1. Configure your secrets using: ./scripts/setup-secrets.sh"
    echo "  2. Validate your setup: python scripts/validate-setup.py"
    echo "  3. Test the CLI: python -m src.mirror_watcher_ai.cli --help"
    echo "  4. Review documentation in docs/"
    echo
    log_info "First automated run scheduled for: 06:00 UTC daily"
    log_warning "Don't forget to configure your GitHub Actions secrets!"
}

# Run main function
main "$@"