#!/bin/bash
set -euo pipefail

# Legio-Cognito Archive Script for MirrorWatcherAI
# Archives MirrorWatcherAI results to the Legio-Cognito scroll storage system

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

# Check if jq is available
check_jq() {
    if ! command -v jq >/dev/null 2>&1; then
        log_warning "jq is not installed. JSON processing will be limited"
        return 1
    fi
    return 0
}

# Archive results to Legio-Cognito
archive_results() {
    local results_file="$1"
    local archive_name="${2:-$(date +%Y%m%d_%H%M%S)}"
    
    log_info "Archiving results to Legio-Cognito: $results_file"
    
    if [ ! -f "$results_file" ]; then
        log_error "Results file not found: $results_file"
        return 1
    fi
    
    # Validate results file
    if check_jq && ! jq empty "$results_file" >/dev/null 2>&1; then
        log_error "Invalid JSON in results file: $results_file"
        return 1
    fi
    
    # Check if Legio-Cognito is configured
    if [ -z "${LEGIO_COGNITO_API_KEY:-}" ] || [ -z "${LEGIO_COGNITO_ENDPOINT:-}" ]; then
        log_warning "Legio-Cognito not configured, storing locally only"
        return archive_locally "$results_file" "$archive_name"
    fi
    
    # Prepare archive payload
    local temp_payload=$(mktemp)
    create_archive_payload "$results_file" "$archive_name" > "$temp_payload"
    
    # Submit to Legio-Cognito
    local response=$(mktemp)
    local http_code
    
    log_info "Submitting to Legio-Cognito endpoint..."
    
    http_code=$(curl -s -w "%{http_code}" \
        -H "Authorization: Bearer $LEGIO_COGNITO_API_KEY" \
        -H "Content-Type: application/json" \
        -H "X-Archive-Type: mirror_watcher_results" \
        -X POST \
        --data @"$temp_payload" \
        "$LEGIO_COGNITO_ENDPOINT/scrolls/archive" \
        -o "$response")
    
    # Clean up temp files
    rm -f "$temp_payload"
    
    # Check response
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        log_success "Successfully archived to Legio-Cognito"
        
        if check_jq; then
            local archive_id=$(jq -r '.archive_id // "unknown"' "$response" 2>/dev/null || echo "unknown")
            log_info "Archive ID: $archive_id"
        fi
        
        # Also store locally as backup
        archive_locally "$results_file" "$archive_name"
        
        rm -f "$response"
        return 0
    else
        log_error "Failed to archive to Legio-Cognito (HTTP $http_code)"
        if [ -s "$response" ]; then
            log_error "Response: $(cat "$response")"
        fi
        
        # Fall back to local storage
        log_info "Falling back to local storage"
        archive_locally "$results_file" "$archive_name"
        
        rm -f "$response"
        return 1
    fi
}

# Create archive payload for Legio-Cognito
create_archive_payload() {
    local results_file="$1"
    local archive_name="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Create archive metadata
    cat << EOF
{
  "scroll_metadata": {
    "type": "MirrorWatcherAI_Results",
    "version": "1.0.0",
    "created_at": "$timestamp",
    "archive_id": "mirror_watcher_$archive_name",
    "classification": "ecosystem_analysis",
    "retention": "permanent",
    "access_level": "triune_internal"
  },
  "content": $(cat "$results_file"),
  "integrity": {
    "content_hash": "$(sha256sum "$results_file" | cut -d' ' -f1)",
    "verification": {
      "timestamp": "$timestamp",
      "source": "MirrorWatcherAI_Archive_Script"
    }
  },
  "legio_metadata": {
    "scroll_classification": "routine",
    "indexing_tags": ["mirror_watcher", "ecosystem_analysis", "triune_oracle", "automated"],
    "search_keywords": ["ecosystem", "analysis", "repositories", "health", "compliance"]
  }
}
EOF
}

# Archive results locally
archive_locally() {
    local results_file="$1"
    local archive_name="$2"
    local archive_dir="$PROJECT_ROOT/.legio_cognito/archive"
    
    log_info "Storing archive locally: $archive_name"
    
    # Ensure archive directory exists
    mkdir -p "$archive_dir"
    
    # Create local archive file
    local archive_file="$archive_dir/mirror_watcher_${archive_name}.json"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Create local archive with metadata
    cat > "$archive_file" << EOF
{
  "archive_metadata": {
    "type": "MirrorWatcherAI_Results_Local",
    "version": "1.0.0",
    "created_at": "$timestamp",
    "archive_id": "mirror_watcher_$archive_name",
    "storage_type": "local_fallback",
    "original_file": "$results_file"
  },
  "content": $(cat "$results_file"),
  "integrity": {
    "content_hash": "$(sha256sum "$results_file" | cut -d' ' -f1)",
    "file_size": $(stat -c%s "$results_file"),
    "verification": {
      "timestamp": "$timestamp",
      "method": "local_archive_script"
    }
  }
}
EOF
    
    if [ $? -eq 0 ]; then
        log_success "Local archive created: $archive_file"
        
        # Set appropriate permissions
        chmod 644 "$archive_file"
        
        return 0
    else
        log_error "Failed to create local archive"
        return 1
    fi
}

# List archived results
list_archives() {
    local archive_dir="$PROJECT_ROOT/.legio_cognito/archive"
    
    log_info "Local archives in $archive_dir:"
    
    if [ ! -d "$archive_dir" ]; then
        log_warning "Archive directory does not exist"
        return 1
    fi
    
    local archives=("$archive_dir"/mirror_watcher_*.json)
    
    if [ ! -e "${archives[0]}" ]; then
        log_info "No local archives found"
        return 0
    fi
    
    for archive in "${archives[@]}"; do
        local filename=$(basename "$archive")
        local filesize=$(stat -c%s "$archive" 2>/dev/null || echo "unknown")
        local modified=$(stat -c%y "$archive" 2>/dev/null || echo "unknown")
        
        echo "  $filename (${filesize} bytes, modified: $modified)"
        
        # Show summary if jq is available
        if check_jq; then
            local timestamp=$(jq -r '.archive_metadata.created_at // .content.timestamp // "unknown"' "$archive" 2>/dev/null)
            local repos=$(jq -r '.content.analysis.repositories | keys | length // 0' "$archive" 2>/dev/null)
            local health=$(jq -r '.content.analysis.ecosystem_health.average_compliance_score // "unknown"' "$archive" 2>/dev/null)
            
            echo "    Created: $timestamp, Repos: $repos, Health: $health%"
        fi
        
        echo ""
    done
}

# Retrieve specific archive
retrieve_archive() {
    local archive_id="$1"
    local output_file="${2:-}"
    local archive_dir="$PROJECT_ROOT/.legio_cognito/archive"
    
    log_info "Retrieving archive: $archive_id"
    
    # First try Legio-Cognito API if configured
    if [ -n "${LEGIO_COGNITO_API_KEY:-}" ] && [ -n "${LEGIO_COGNITO_ENDPOINT:-}" ]; then
        log_info "Checking Legio-Cognito API..."
        
        local response=$(mktemp)
        local http_code
        
        http_code=$(curl -s -w "%{http_code}" \
            -H "Authorization: Bearer $LEGIO_COGNITO_API_KEY" \
            -H "Accept: application/json" \
            "$LEGIO_COGNITO_ENDPOINT/scrolls/$archive_id" \
            -o "$response")
        
        if [ "$http_code" -eq 200 ]; then
            log_success "Retrieved from Legio-Cognito API"
            
            if [ -n "$output_file" ]; then
                cp "$response" "$output_file"
                log_success "Saved to: $output_file"
            else
                cat "$response"
            fi
            
            rm -f "$response"
            return 0
        else
            log_info "Not found in Legio-Cognito, checking local storage"
        fi
        
        rm -f "$response"
    fi
    
    # Try local storage
    local archive_file="$archive_dir/mirror_watcher_${archive_id}.json"
    
    if [ -f "$archive_file" ]; then
        log_success "Found in local storage: $archive_file"
        
        if [ -n "$output_file" ]; then
            cp "$archive_file" "$output_file"
            log_success "Saved to: $output_file"
        else
            cat "$archive_file"
        fi
        
        return 0
    else
        log_error "Archive not found: $archive_id"
        return 1
    fi
}

# Clean up old archives
cleanup_archives() {
    local retention_days="${1:-90}"
    local archive_dir="$PROJECT_ROOT/.legio_cognito/archive"
    
    log_info "Cleaning up archives older than $retention_days days"
    
    if [ ! -d "$archive_dir" ]; then
        log_info "No archive directory to clean"
        return 0
    fi
    
    local cleaned_count=0
    
    # Find and remove old files
    while IFS= read -r -d '' file; do
        rm -f "$file"
        ((cleaned_count++))
        log_info "Removed: $(basename "$file")"
    done < <(find "$archive_dir" -name "mirror_watcher_*.json" -type f -mtime +$retention_days -print0 2>/dev/null)
    
    if [ $cleaned_count -eq 0 ]; then
        log_info "No archives to clean up"
    else
        log_success "Cleaned up $cleaned_count old archives"
    fi
}

# Verify archive integrity
verify_archive() {
    local archive_file="$1"
    
    log_info "Verifying archive integrity: $archive_file"
    
    if [ ! -f "$archive_file" ]; then
        log_error "Archive file not found: $archive_file"
        return 1
    fi
    
    # Check JSON validity
    if check_jq && ! jq empty "$archive_file" >/dev/null 2>&1; then
        log_error "Invalid JSON in archive file"
        return 1
    fi
    
    # Verify hash if present
    if check_jq; then
        local stored_hash=$(jq -r '.integrity.content_hash // empty' "$archive_file" 2>/dev/null)
        
        if [ -n "$stored_hash" ]; then
            # Extract content and calculate hash
            local temp_content=$(mktemp)
            jq -r '.content' "$archive_file" > "$temp_content"
            local calculated_hash=$(sha256sum "$temp_content" | cut -d' ' -f1)
            rm -f "$temp_content"
            
            if [ "$stored_hash" = "$calculated_hash" ]; then
                log_success "Hash verification passed"
            else
                log_error "Hash verification failed"
                log_error "Stored: $stored_hash"
                log_error "Calculated: $calculated_hash"
                return 1
            fi
        else
            log_warning "No hash available for verification"
        fi
    fi
    
    log_success "Archive integrity verified"
    return 0
}

# Show usage information
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  archive FILE [NAME]      Archive results file to Legio-Cognito"
    echo "  list                     List local archives"
    echo "  retrieve ID [OUTPUT]     Retrieve archive by ID"
    echo "  verify FILE              Verify archive integrity"
    echo "  cleanup [DAYS]           Clean up archives older than DAYS (default: 90)"
    echo "  help                     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 archive mirror_watcher_results.json"
    echo "  $0 archive results.json custom_name"
    echo "  $0 list"
    echo "  $0 retrieve mirror_watcher_20250818_060000"
    echo "  $0 retrieve mirror_watcher_20250818_060000 output.json"
    echo "  $0 verify .legio_cognito/archive/mirror_watcher_20250818_060000.json"
    echo "  $0 cleanup 30"
    echo ""
    echo "Environment variables:"
    echo "  LEGIO_COGNITO_ENDPOINT   API endpoint for Legio-Cognito"
    echo "  LEGIO_COGNITO_API_KEY    API key for authentication"
}

# Main function
main() {
    local command="${1:-help}"
    
    case "$command" in
        archive)
            if [ $# -lt 2 ]; then
                log_error "Usage: $0 archive FILE [NAME]"
                exit 1
            fi
            archive_results "$2" "${3:-$(date +%Y%m%d_%H%M%S)}"
            ;;
        list)
            list_archives
            ;;
        retrieve)
            if [ $# -lt 2 ]; then
                log_error "Usage: $0 retrieve ID [OUTPUT]"
                exit 1
            fi
            retrieve_archive "$2" "${3:-}"
            ;;
        verify)
            if [ $# -ne 2 ]; then
                log_error "Usage: $0 verify FILE"
                exit 1
            fi
            verify_archive "$2"
            ;;
        cleanup)
            cleanup_archives "${2:-90}"
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