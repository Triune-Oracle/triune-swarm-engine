#!/bin/bash

# 🔐 Triune Swarm Engine - Secrets Setup Script
# Automated configuration for local development environment
# Version: 1.0.0

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
ENV_FILE=".env.local"
BACKUP_FILE=".env.local.backup"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Banner
print_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                   🔐 TRIUNE SWARM ENGINE                         ║"
    echo "║                    Secrets Setup Script                         ║"
    echo "║                                                                  ║"
    echo "║              Mirror Watcher Automation Setup                    ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Logging functions
log_info() { echo -e "${BLUE}ℹ  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_step() { echo -e "${CYAN}🔄 $1${NC}"; }

# Help message
show_help() {
    cat << EOF
🔐 Triune Swarm Engine - Secrets Setup Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -t, --token TOKEN        GitHub Personal Access Token (REPO_SYNC_TOKEN)
    -e, --endpoint URL       ShadowScrolls API endpoint URL
    -k, --key KEY           ShadowScrolls API key
    -f, --file PATH         Custom environment file path (default: .env.local)
    -i, --interactive       Interactive mode (default)
    -s, --silent            Silent mode - use provided values only
    -b, --backup            Create backup of existing environment file
    -v, --validate          Validate configuration after setup
    -h, --help              Show this help message

EXAMPLES:
    # Interactive setup (default)
    $0

    # Silent setup with all parameters
    $0 --token "ghp_xxx" --endpoint "https://api.shadowscrolls.com/v1" --key "ss_live_xxx"

    # Setup with validation
    $0 --interactive --validate

    # Custom environment file
    $0 --file ".env.production" --backup

REQUIRED SECRETS:
    REPO_SYNC_TOKEN        - GitHub Personal Access Token for file sync
    SHADOWSCROLLS_ENDPOINT - ShadowScrolls API endpoint URL
    SHADOWSCROLLS_API_KEY  - ShadowScrolls authentication key

For detailed setup instructions, see: SECRETS_SETUP.md
EOF
}

# Validate GitHub token format
validate_github_token() {
    local token="$1"
    if [[ ! "$token" =~ ^ghp_[A-Za-z0-9]{36}$ ]]; then
        log_error "Invalid GitHub token format. Expected: ghp_[36 characters]"
        return 1
    fi
    return 0
}

# Validate URL format
validate_url() {
    local url="$1"
    if [[ ! "$url" =~ ^https?://[a-zA-Z0-9.-]+(/.*)?$ ]]; then
        log_error "Invalid URL format. Expected: https://domain.com/path"
        return 1
    fi
    return 0
}

# Validate ShadowScrolls API key format
validate_shadowscrolls_key() {
    local key="$1"
    if [[ ! "$key" =~ ^ss_live_[A-Za-z0-9]{32}$ ]]; then
        log_error "Invalid ShadowScrolls API key format. Expected: ss_live_[32 characters]"
        return 1
    fi
    return 0
}

# Interactive input with validation
get_input() {
    local prompt="$1"
    local validator="$2"
    local value=""
    
    while true; do
        echo -e -n "${CYAN}$prompt: ${NC}"
        read -r value
        
        if [[ -n "$value" ]] && $validator "$value"; then
            echo "$value"
            return 0
        fi
        
        log_warning "Invalid input. Please try again."
    done
}

# Get GitHub token securely
get_github_token() {
    local token=""
    
    echo -e "${CYAN}Enter your GitHub Personal Access Token:${NC}"
    echo -e "${YELLOW}⚠️  The token will be hidden while typing${NC}"
    echo -e -n "${CYAN}REPO_SYNC_TOKEN: ${NC}"
    read -rs token
    echo
    
    if validate_github_token "$token"; then
        echo "$token"
        return 0
    else
        return 1
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Test GitHub token
test_github_token() {
    local token="$1"
    log_step "Testing GitHub token..."
    
    if ! command_exists curl; then
        log_warning "curl not found. Skipping GitHub token test."
        return 0
    fi
    
    local response
    response=$(curl -s -H "Authorization: token $token" https://api.github.com/user)
    
    if echo "$response" | grep -q "login"; then
        local username=$(echo "$response" | grep -o '"login":"[^"]*"' | cut -d'"' -f4)
        log_success "GitHub token validated for user: $username"
        return 0
    else
        log_error "GitHub token validation failed"
        return 1
    fi
}

# Test ShadowScrolls endpoint
test_shadowscrolls_endpoint() {
    local endpoint="$1"
    local api_key="$2"
    log_step "Testing ShadowScrolls endpoint..."
    
    if ! command_exists curl; then
        log_warning "curl not found. Skipping ShadowScrolls endpoint test."
        return 0
    fi
    
    local health_url="$endpoint/health"
    local response
    response=$(curl -s -H "Authorization: Bearer $api_key" "$health_url" || echo "ERROR")
    
    if [[ "$response" != "ERROR" ]] && echo "$response" | grep -q -E "(ok|healthy|status)" 2>/dev/null; then
        log_success "ShadowScrolls endpoint is accessible"
        return 0
    else
        log_warning "ShadowScrolls endpoint test inconclusive (endpoint may not have /health route)"
        return 0
    fi
}

# Create environment file
create_env_file() {
    local repo_token="$1"
    local ss_endpoint="$2"
    local ss_api_key="$3"
    local env_file="$4"
    
    log_step "Creating environment file: $env_file"
    
    # Create backup if file exists
    if [[ -f "$env_file" ]] && [[ "$CREATE_BACKUP" == "true" ]]; then
        cp "$env_file" "$BACKUP_FILE"
        log_success "Backup created: $BACKUP_FILE"
    fi
    
    # Generate timestamp
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat > "$env_file" << EOF
# 🔐 Triune Swarm Engine - Environment Configuration
# Generated: $timestamp
# Script: setup-secrets.sh v1.0.0

# ════════════════════════════════════════════════════════════════════
# Mirror Watcher Automation Configuration
# ════════════════════════════════════════════════════════════════════

# GitHub Personal Access Token for repository synchronization
REPO_SYNC_TOKEN=$repo_token

# ShadowScrolls Integration Configuration
SHADOWSCROLLS_ENDPOINT=$ss_endpoint
SHADOWSCROLLS_API_KEY=$ss_api_key

# ════════════════════════════════════════════════════════════════════
# Development Environment Settings
# ════════════════════════════════════════════════════════════════════

# Environment mode
NODE_ENV=development

# Debug logging (uncomment to enable)
# DEBUG=triune:*

# Optional: Override settings for local development
# SHADOWSCROLLS_TIMEOUT=30000
# SYNC_INTERVAL=300
# LOG_LEVEL=info

# ════════════════════════════════════════════════════════════════════
# Security Notice
# ════════════════════════════════════════════════════════════════════
# 
# ⚠️  IMPORTANT: Never commit this file to version control!
# ⚠️  Add .env.local to your .gitignore file
# ⚠️  Rotate secrets regularly (every 90 days recommended)
# 
# For production deployment, use secure secret management instead
# of environment files.
# ════════════════════════════════════════════════════════════════════
EOF

    log_success "Environment file created successfully"
}

# Update gitignore
update_gitignore() {
    local gitignore_file="$PROJECT_ROOT/.gitignore"
    local env_pattern=".env.local"
    
    if [[ -f "$gitignore_file" ]]; then
        if ! grep -q "$env_pattern" "$gitignore_file"; then
            echo "" >> "$gitignore_file"
            echo "# Local environment files" >> "$gitignore_file"
            echo ".env.local" >> "$gitignore_file"
            echo ".env.*.local" >> "$gitignore_file"
            log_success "Updated .gitignore to exclude environment files"
        else
            log_info ".gitignore already configured"
        fi
    else
        log_warning ".gitignore not found - consider creating one"
    fi
}

# Run validation
run_validation() {
    local validation_script="$SCRIPT_DIR/validate-setup.py"
    
    if [[ -f "$validation_script" ]]; then
        log_step "Running setup validation..."
        
        if command_exists python3; then
            python3 "$validation_script" || log_warning "Validation completed with warnings"
        elif command_exists python; then
            python "$validation_script" || log_warning "Validation completed with warnings"
        else
            log_warning "Python not found. Skipping validation."
        fi
    else
        log_warning "Validation script not found: $validation_script"
    fi
}

# Main setup function
main() {
    # Parse command line arguments
    REPO_TOKEN=""
    SS_ENDPOINT=""
    SS_API_KEY=""
    INTERACTIVE=true
    SILENT=false
    CREATE_BACKUP=false
    RUN_VALIDATION=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--token)
                REPO_TOKEN="$2"
                shift 2
                ;;
            -e|--endpoint)
                SS_ENDPOINT="$2"
                shift 2
                ;;
            -k|--key)
                SS_API_KEY="$2"
                shift 2
                ;;
            -f|--file)
                ENV_FILE="$2"
                shift 2
                ;;
            -i|--interactive)
                INTERACTIVE=true
                shift
                ;;
            -s|--silent)
                SILENT=true
                INTERACTIVE=false
                shift
                ;;
            -b|--backup)
                CREATE_BACKUP=true
                shift
                ;;
            -v|--validate)
                RUN_VALIDATION=true
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
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    print_banner
    
    log_info "Setting up Mirror Watcher automation secrets..."
    log_info "Project root: $PROJECT_ROOT"
    log_info "Environment file: $ENV_FILE"
    
    # Interactive mode
    if [[ "$INTERACTIVE" == "true" ]]; then
        log_step "Starting interactive setup..."
        
        # Get GitHub token
        if [[ -z "$REPO_TOKEN" ]]; then
            log_info "GitHub Personal Access Token (REPO_SYNC_TOKEN)"
            echo "  Required scopes: repo, workflow, read:org"
            echo "  Generate at: https://github.com/settings/tokens"
            echo
            while true; do
                REPO_TOKEN=$(get_github_token) && break
            done
        fi
        
        # Get ShadowScrolls endpoint
        if [[ -z "$SS_ENDPOINT" ]]; then
            SS_ENDPOINT=$(get_input "ShadowScrolls API endpoint (e.g., https://api.shadowscrolls.com/v1)" validate_url)
        fi
        
        # Get ShadowScrolls API key
        if [[ -z "$SS_API_KEY" ]]; then
            echo -e "${CYAN}Enter your ShadowScrolls API key:${NC}"
            echo -e "${YELLOW}⚠️  The key will be hidden while typing${NC}"
            echo -e -n "${CYAN}SHADOWSCROLLS_API_KEY: ${NC}"
            read -rs SS_API_KEY
            echo
            while ! validate_shadowscrolls_key "$SS_API_KEY"; do
                echo -e -n "${CYAN}SHADOWSCROLLS_API_KEY: ${NC}"
                read -rs SS_API_KEY
                echo
            done
        fi
    fi
    
    # Validate required values
    if [[ -z "$REPO_TOKEN" ]] || [[ -z "$SS_ENDPOINT" ]] || [[ -z "$SS_API_KEY" ]]; then
        log_error "Missing required parameters. Use --help for usage information."
        exit 1
    fi
    
    # Validate formats
    if ! validate_github_token "$REPO_TOKEN"; then
        log_error "Invalid GitHub token format"
        exit 1
    fi
    
    if ! validate_url "$SS_ENDPOINT"; then
        log_error "Invalid ShadowScrolls endpoint URL"
        exit 1
    fi
    
    if ! validate_shadowscrolls_key "$SS_API_KEY"; then
        log_error "Invalid ShadowScrolls API key format"
        exit 1
    fi
    
    # Test connections (optional)
    if [[ "$INTERACTIVE" == "true" ]]; then
        test_github_token "$REPO_TOKEN" || log_warning "GitHub token test failed - continuing anyway"
        test_shadowscrolls_endpoint "$SS_ENDPOINT" "$SS_API_KEY" || true
    fi
    
    # Create environment file
    create_env_file "$REPO_TOKEN" "$SS_ENDPOINT" "$SS_API_KEY" "$ENV_FILE"
    
    # Update gitignore
    update_gitignore
    
    # Run validation if requested
    if [[ "$RUN_VALIDATION" == "true" ]]; then
        run_validation
    fi
    
    # Success message
    echo
    log_success "🎉 Setup completed successfully!"
    echo
    log_info "Next steps:"
    echo "  1. Verify your configuration: python scripts/validate-setup.py"
    echo "  2. Test the Mirror Watcher: npm run test-sync"  
    echo "  3. Review the setup guide: SECRETS_SETUP.md"
    echo
    log_warning "Security reminder: Never commit $ENV_FILE to version control!"
}

# Run main function
main "$@"