#!/bin/bash
set -euo pipefail

# Deploy Key Management Script for MirrorWatcherAI
# Manages secure deploy keys for repository access across the Triune ecosystem

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if GitHub CLI is available
check_gh_cli() {
    if ! command -v gh >/dev/null 2>&1; then
        log_error "GitHub CLI (gh) is required but not installed"
        log_info "Install from: https://cli.github.com/"
        return 1
    fi
    
    # Check if authenticated
    if ! gh auth status >/dev/null 2>&1; then
        log_error "GitHub CLI is not authenticated"
        log_info "Run: gh auth login"
        return 1
    fi
    
    log_success "GitHub CLI is available and authenticated"
    return 0
}

# Generate SSH key pair
generate_ssh_key() {
    local key_name="$1"
    local key_path="$HOME/.ssh/$key_name"
    
    log_info "Generating SSH key pair: $key_name"
    
    if [ -f "$key_path" ]; then
        log_warning "SSH key already exists: $key_path"
        read -p "Overwrite existing key? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Skipping key generation"
            return 0
        fi
    fi
    
    # Generate key pair
    ssh-keygen -t ed25519 -f "$key_path" -N "" -C "mirror-watcher-ai@triune-oracle"
    
    if [ $? -eq 0 ]; then
        log_success "SSH key pair generated: $key_path"
        chmod 600 "$key_path"
        chmod 644 "$key_path.pub"
        return 0
    else
        log_error "Failed to generate SSH key pair"
        return 1
    fi
}

# Add deploy key to repository
add_deploy_key() {
    local repo="$1"
    local key_path="$2"
    local key_title="$3"
    
    log_info "Adding deploy key to $repo"
    
    if [ ! -f "$key_path.pub" ]; then
        log_error "Public key not found: $key_path.pub"
        return 1
    fi
    
    # Read public key
    local public_key=$(cat "$key_path.pub")
    
    # Add deploy key using GitHub CLI
    if gh api repos/"$repo"/keys -f title="$key_title" -f key="$public_key" -F read_only=true >/dev/null 2>&1; then
        log_success "Deploy key added to $repo"
        return 0
    else
        log_error "Failed to add deploy key to $repo"
        log_warning "Key may already exist or you may lack permissions"
        return 1
    fi
}

# List deploy keys for repository
list_deploy_keys() {
    local repo="$1"
    
    log_info "Deploy keys for $repo:"
    
    if ! gh api repos/"$repo"/keys --jq '.[] | "\(.id): \(.title) (read_only: \(.read_only))"' 2>/dev/null; then
        log_warning "Could not list deploy keys for $repo (may lack permissions)"
    fi
}

# Remove deploy key from repository
remove_deploy_key() {
    local repo="$1"
    local key_id="$2"
    
    log_info "Removing deploy key $key_id from $repo"
    
    if gh api -X DELETE repos/"$repo"/keys/"$key_id" >/dev/null 2>&1; then
        log_success "Deploy key removed from $repo"
        return 0
    else
        log_error "Failed to remove deploy key from $repo"
        return 1
    fi
}

# Setup deploy keys for all Triune repositories
setup_triune_deploy_keys() {
    local key_name="mirror_watcher_deploy_key"
    local key_path="$HOME/.ssh/$key_name"
    
    log_info "Setting up deploy keys for Triune ecosystem repositories"
    
    # Generate SSH key if it doesn't exist
    if [ ! -f "$key_path" ]; then
        generate_ssh_key "$key_name"
    fi
    
    # List of Triune repositories
    local repositories=(
        "Triune-Oracle/triune-swarm-engine"
        "Triune-Oracle/Legio-Cognito"
        "Triune-Oracle/TtriumvirateMonitor-Mobile"
        "Triune-Oracle/Triune-retrieval-node"
    )
    
    # Add deploy key to each repository
    for repo in "${repositories[@]}"; do
        add_deploy_key "$repo" "$key_path" "MirrorWatcherAI Deploy Key"
    done
    
    log_success "Deploy key setup completed"
    
    # Show instructions for GitHub Actions
    echo ""
    log_info "To use this key in GitHub Actions, add the private key as a secret:"
    echo ""
    echo "1. Copy the private key:"
    echo "   cat $key_path"
    echo ""
    echo "2. Go to repository Settings > Secrets and variables > Actions"
    echo "3. Add new secret named: MIRROR_WATCHER_DEPLOY_KEY"
    echo "4. Paste the private key as the value"
    echo ""
}

# Verify deploy key access
verify_deploy_key() {
    local repo="$1"
    local key_path="$2"
    
    log_info "Verifying deploy key access to $repo"
    
    if [ ! -f "$key_path" ]; then
        log_error "Private key not found: $key_path"
        return 1
    fi
    
    # Test SSH connection
    local ssh_result
    ssh_result=$(ssh -T -i "$key_path" -o StrictHostKeyChecking=no git@github.com 2>&1 || true)
    
    if echo "$ssh_result" | grep -q "successfully authenticated"; then
        log_success "SSH authentication successful"
        
        # Test repository access
        local temp_dir=$(mktemp -d)
        if git clone --depth 1 git@github.com:"$repo".git "$temp_dir" >/dev/null 2>&1; then
            log_success "Repository access verified for $repo"
            rm -rf "$temp_dir"
            return 0
        else
            log_error "Repository access failed for $repo"
            rm -rf "$temp_dir"
            return 1
        fi
    else
        log_error "SSH authentication failed"
        echo "$ssh_result"
        return 1
    fi
}

# Rotate deploy keys
rotate_deploy_keys() {
    log_info "Rotating deploy keys for security"
    
    local old_key_name="mirror_watcher_deploy_key"
    local new_key_name="mirror_watcher_deploy_key_$(date +%Y%m%d)"
    
    # Generate new key
    generate_ssh_key "$new_key_name"
    
    # List of repositories
    local repositories=(
        "Triune-Oracle/triune-swarm-engine"
        "Triune-Oracle/Legio-Cognito"
        "Triune-Oracle/TtriumvirateMonitor-Mobile"
        "Triune-Oracle/Triune-retrieval-node"
    )
    
    # Add new key to each repository
    for repo in "${repositories[@]}"; do
        add_deploy_key "$repo" "$HOME/.ssh/$new_key_name" "MirrorWatcherAI Deploy Key ($(date +%Y-%m-%d))"
    done
    
    log_warning "New deploy keys added. Update GitHub Actions secrets with the new private key:"
    echo "cat $HOME/.ssh/$new_key_name"
    echo ""
    log_warning "After updating secrets, remove old deploy keys manually"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup                    Setup deploy keys for all Triune repositories"
    echo "  generate KEY_NAME        Generate new SSH key pair"
    echo "  add REPO KEY_PATH        Add deploy key to repository"
    echo "  list REPO               List deploy keys for repository"
    echo "  remove REPO KEY_ID       Remove deploy key from repository"
    echo "  verify REPO KEY_PATH     Verify deploy key access to repository"
    echo "  rotate                   Rotate all deploy keys"
    echo "  help                     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup"
    echo "  $0 generate my_deploy_key"
    echo "  $0 add Triune-Oracle/triune-swarm-engine ~/.ssh/deploy_key"
    echo "  $0 list Triune-Oracle/triune-swarm-engine"
    echo "  $0 verify Triune-Oracle/triune-swarm-engine ~/.ssh/deploy_key"
    echo "  $0 rotate"
}

# Main function
main() {
    local command="${1:-help}"
    
    case "$command" in
        setup)
            if ! check_gh_cli; then
                exit 1
            fi
            setup_triune_deploy_keys
            ;;
        generate)
            if [ $# -ne 2 ]; then
                log_error "Usage: $0 generate KEY_NAME"
                exit 1
            fi
            generate_ssh_key "$2"
            ;;
        add)
            if [ $# -ne 3 ]; then
                log_error "Usage: $0 add REPO KEY_PATH"
                exit 1
            fi
            if ! check_gh_cli; then
                exit 1
            fi
            add_deploy_key "$2" "$3" "MirrorWatcherAI Deploy Key"
            ;;
        list)
            if [ $# -ne 2 ]; then
                log_error "Usage: $0 list REPO"
                exit 1
            fi
            if ! check_gh_cli; then
                exit 1
            fi
            list_deploy_keys "$2"
            ;;
        remove)
            if [ $# -ne 3 ]; then
                log_error "Usage: $0 remove REPO KEY_ID"
                exit 1
            fi
            if ! check_gh_cli; then
                exit 1
            fi
            remove_deploy_key "$2" "$3"
            ;;
        verify)
            if [ $# -ne 3 ]; then
                log_error "Usage: $0 verify REPO KEY_PATH"
                exit 1
            fi
            verify_deploy_key "$2" "$3"
            ;;
        rotate)
            if ! check_gh_cli; then
                exit 1
            fi
            rotate_deploy_keys
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"