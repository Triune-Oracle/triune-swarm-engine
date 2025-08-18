#!/bin/bash
set -euo pipefail

# Triune Monitor Sync Script for MirrorWatcherAI
# Synchronizes status and results with the TtriumvirateMonitor-Mobile system

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

# Sync status with Triune Monitor
sync_status() {
    local results_file="$1"
    
    log_info "Syncing status with Triune Monitor: $results_file"
    
    if [ ! -f "$results_file" ]; then
        log_error "Results file not found: $results_file"
        return 1
    fi
    
    # Validate results file
    if check_jq && ! jq empty "$results_file" >/dev/null 2>&1; then
        log_error "Invalid JSON in results file: $results_file"
        return 1
    fi
    
    # Check if Triune Monitor is configured
    if [ -z "${TRIUNE_MONITOR_API_KEY:-}" ] || [ -z "${TRIUNE_MONITOR_ENDPOINT:-}" ]; then
        log_warning "Triune Monitor not configured, storing status locally only"
        return store_status_locally "$results_file"
    fi
    
    # Prepare status payload
    local temp_payload=$(mktemp)
    create_status_payload "$results_file" > "$temp_payload"
    
    # Submit to Triune Monitor
    local response=$(mktemp)
    local http_code
    
    log_info "Submitting status to Triune Monitor..."
    
    http_code=$(curl -s -w "%{http_code}" \
        -H "Authorization: Bearer $TRIUNE_MONITOR_API_KEY" \
        -H "Content-Type: application/json" \
        -H "X-Monitor-Source: MirrorWatcherAI" \
        -X POST \
        --data @"$temp_payload" \
        "$TRIUNE_MONITOR_ENDPOINT/status/mirror-watcher" \
        -o "$response")
    
    # Clean up temp files
    rm -f "$temp_payload"
    
    # Check response
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        log_success "Successfully synced with Triune Monitor"
        
        if check_jq; then
            local status_id=$(jq -r '.status_id // "unknown"' "$response" 2>/dev/null || echo "unknown")
            log_info "Status ID: $status_id"
        fi
        
        # Also store locally as backup
        store_status_locally "$results_file"
        
        rm -f "$response"
        return 0
    else
        log_error "Failed to sync with Triune Monitor (HTTP $http_code)"
        if [ -s "$response" ]; then
            log_error "Response: $(cat "$response")"
        fi
        
        # Fall back to local storage
        log_info "Falling back to local storage"
        store_status_locally "$results_file"
        
        rm -f "$response"
        return 1
    fi
}

# Create status payload for Triune Monitor
create_status_payload() {
    local results_file="$1"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    if check_jq; then
        # Extract key metrics using jq
        local total_repos=$(jq -r '.analysis.repositories | keys | length // 0' "$results_file" 2>/dev/null || echo "0")
        local successful_repos=$(jq -r '[.analysis.repositories[] | select(.status == "success")] | length // 0' "$results_file" 2>/dev/null || echo "0")
        local health_score=$(jq -r '.analysis.ecosystem_health.average_compliance_score // 0' "$results_file" 2>/dev/null || echo "0")
        local ecosystem_status=$(jq -r '.analysis.ecosystem_health.ecosystem_status // "unknown"' "$results_file" 2>/dev/null || echo "unknown")
        local recommendations_count=$(jq -r '.analysis.recommendations | length // 0' "$results_file" 2>/dev/null || echo "0")
        local execution_status=$(jq -r '.status // "unknown"' "$results_file" 2>/dev/null || echo "unknown")
        local execution_timestamp=$(jq -r '.timestamp // "unknown"' "$results_file" 2>/dev/null || echo "unknown")
        
        # Determine status level
        local status_level="info"
        if [ "$execution_status" != "completed" ]; then
            status_level="critical"
        elif [ "$(echo "$health_score < 50" | bc -l 2>/dev/null || echo "0")" = "1" ]; then
            status_level="critical"
        elif [ "$(echo "$health_score < 70" | bc -l 2>/dev/null || echo "0")" = "1" ]; then
            status_level="warning"
        elif [ "$(echo "$health_score >= 90" | bc -l 2>/dev/null || echo "0")" = "1" ]; then
            status_level="success"
        fi
        
        # Create status message
        local status_message
        if [ "$execution_status" = "completed" ]; then
            if [ "$(echo "$health_score >= 90" | bc -l 2>/dev/null || echo "0")" = "1" ]; then
                status_message="✅ Ecosystem healthy - $total_repos repositories analyzed, compliance at ${health_score}%"
            elif [ "$(echo "$health_score >= 70" | bc -l 2>/dev/null || echo "0")" = "1" ]; then
                status_message="⚠️ Ecosystem stable - $total_repos repositories, $recommendations_count recommendations"
            elif [ "$(echo "$health_score >= 50" | bc -l 2>/dev/null || echo "0")" = "1" ]; then
                status_message="🔶 Ecosystem needs attention - ${health_score}% compliance, $recommendations_count recommendations"
            else
                status_message="🚨 Ecosystem critical - ${health_score}% compliance, immediate action required"
            fi
        else
            status_message="❌ MirrorWatcherAI execution failed"
        fi
        
        # Calculate next execution (daily at 06:00 UTC)
        local next_execution=$(date -d "tomorrow 06:00 UTC" -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT06:00:00Z")
        
        # Extract repository summary
        local repo_summary
        repo_summary=$(jq -c '[.analysis.repositories | to_entries[] | select(.value.status == "success") | {
            name: (.key | split("/")[1]),
            language: .value.language,
            stars: (.value.stars // 0),
            compliance_score: (.value.triune_compliance.score // 0),
            last_updated: .value.updated_at
        }] | sort_by(-.compliance_score) | .[0:10]' "$results_file" 2>/dev/null || echo "[]")
        
        # Extract alerts
        local alerts='[]'
        if [ "$(echo "$health_score < 50" | bc -l 2>/dev/null || echo "0")" = "1" ]; then
            alerts='[{"type": "critical", "message": "Ecosystem health critical", "action": "Immediate review required"}]'
        elif [ "$(echo "$health_score < 70" | bc -l 2>/dev/null || echo "0")" = "1" ]; then
            alerts='[{"type": "warning", "message": "Ecosystem health degraded", "action": "Review recommendations"}]'
        fi
        
        cat << EOF
{
  "system": "MirrorWatcherAI",
  "timestamp": "$timestamp",
  "status": {
    "level": "$status_level",
    "health_score": $health_score,
    "ecosystem_status": "$ecosystem_status",
    "message": "$status_message"
  },
  "metrics": {
    "repositories_analyzed": $total_repos,
    "successful_analyses": $successful_repos,
    "failed_analyses": $((total_repos - successful_repos)),
    "recommendations_count": $recommendations_count,
    "analysis_success_rate": $(echo "scale=2; $successful_repos * 100 / $total_repos" | bc -l 2>/dev/null || echo "0")
  },
  "integration_status": {
    "shadowscrolls": {
      "enabled": true,
      "status": "operational",
      "last_attestation": "$execution_timestamp"
    },
    "legio_cognito": {
      "enabled": true,
      "status": "operational",
      "last_archive": "$execution_timestamp"
    },
    "automation": {
      "status": "operational",
      "last_execution": "$execution_timestamp"
    }
  },
  "alerts": $alerts,
  "next_execution": "$next_execution",
  "dashboard_data": {
    "ecosystem_overview": {
      "total_repositories": $total_repos,
      "health_score": $health_score,
      "status": "$ecosystem_status"
    },
    "repository_summary": $repo_summary,
    "trends": {
      "health_trend": "stable",
      "repository_growth": "stable",
      "automation_trend": "improving"
    }
  }
}
EOF
    else
        # Fallback without jq
        cat << EOF
{
  "system": "MirrorWatcherAI",
  "timestamp": "$timestamp",
  "status": {
    "level": "info",
    "message": "Status sync without detailed analysis (jq not available)"
  },
  "metrics": {
    "repositories_analyzed": 0,
    "successful_analyses": 0,
    "failed_analyses": 0
  },
  "next_execution": "$(date -d "tomorrow 06:00 UTC" -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT06:00:00Z")"
}
EOF
    fi
}

# Store status locally
store_status_locally() {
    local results_file="$1"
    local status_dir="$PROJECT_ROOT/.triune_monitor"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    log_info "Storing status locally"
    
    # Ensure status directory exists
    mkdir -p "$status_dir"
    
    # Create status file
    local status_file="$status_dir/status_update_${timestamp}.json"
    create_status_payload "$results_file" > "$status_file"
    
    if [ $? -eq 0 ]; then
        log_success "Local status stored: $status_file"
        
        # Update current status file
        local current_status_file="$status_dir/current_status.json"
        cp "$status_file" "$current_status_file"
        
        # Set appropriate permissions
        chmod 644 "$status_file" "$current_status_file"
        
        return 0
    else
        log_error "Failed to store local status"
        return 1
    fi
}

# Send alert to Triune Monitor
send_alert() {
    local alert_type="$1"
    local message="$2"
    local priority="${3:-medium}"
    
    log_info "Sending alert to Triune Monitor: $alert_type"
    
    # Check if Triune Monitor is configured
    if [ -z "${TRIUNE_MONITOR_API_KEY:-}" ] || [ -z "${TRIUNE_MONITOR_ENDPOINT:-}" ]; then
        log_warning "Triune Monitor not configured, storing alert locally only"
        return store_alert_locally "$alert_type" "$message" "$priority"
    fi
    
    # Prepare alert payload
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local temp_payload=$(mktemp)
    
    cat > "$temp_payload" << EOF
{
  "system": "MirrorWatcherAI",
  "timestamp": "$timestamp",
  "alert": {
    "type": "$alert_type",
    "priority": "$priority",
    "message": "$message"
  }
}
EOF
    
    # Submit alert
    local response=$(mktemp)
    local http_code
    
    http_code=$(curl -s -w "%{http_code}" \
        -H "Authorization: Bearer $TRIUNE_MONITOR_API_KEY" \
        -H "Content-Type: application/json" \
        -X POST \
        --data @"$temp_payload" \
        "$TRIUNE_MONITOR_ENDPOINT/alerts" \
        -o "$response")
    
    # Clean up temp files
    rm -f "$temp_payload"
    
    # Check response
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        log_success "Alert sent successfully"
        rm -f "$response"
        return 0
    else
        log_error "Failed to send alert (HTTP $http_code)"
        if [ -s "$response" ]; then
            log_error "Response: $(cat "$response")"
        fi
        
        # Store locally as fallback
        store_alert_locally "$alert_type" "$message" "$priority"
        
        rm -f "$response"
        return 1
    fi
}

# Store alert locally
store_alert_locally() {
    local alert_type="$1"
    local message="$2"
    local priority="$3"
    local status_dir="$PROJECT_ROOT/.triune_monitor"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    # Ensure directory exists
    mkdir -p "$status_dir"
    
    # Create alert file
    local alert_file="$status_dir/alert_${timestamp}.json"
    
    cat > "$alert_file" << EOF
{
  "system": "MirrorWatcherAI",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "alert": {
    "type": "$alert_type",
    "priority": "$priority",
    "message": "$message"
  },
  "storage": "local_fallback"
}
EOF
    
    if [ $? -eq 0 ]; then
        log_success "Alert stored locally: $alert_file"
        chmod 644 "$alert_file"
        return 0
    else
        log_error "Failed to store alert locally"
        return 1
    fi
}

# Get current status
get_status() {
    local status_dir="$PROJECT_ROOT/.triune_monitor"
    local current_status_file="$status_dir/current_status.json"
    
    if [ -f "$current_status_file" ]; then
        log_info "Current status:"
        if check_jq; then
            jq '.' "$current_status_file"
        else
            cat "$current_status_file"
        fi
        return 0
    else
        log_warning "No current status available"
        return 1
    fi
}

# List status history
list_status_history() {
    local count="${1:-10}"
    local status_dir="$PROJECT_ROOT/.triune_monitor"
    
    log_info "Recent status updates (last $count):"
    
    if [ ! -d "$status_dir" ]; then
        log_warning "Status directory does not exist"
        return 1
    fi
    
    local status_files=("$status_dir"/status_update_*.json)
    
    if [ ! -e "${status_files[0]}" ]; then
        log_info "No status history found"
        return 0
    fi
    
    # Sort by filename (timestamp) and show latest first
    printf '%s\n' "${status_files[@]}" | sort -r | head -n "$count" | while read -r file; do
        local filename=$(basename "$file")
        local timestamp_part=$(echo "$filename" | sed 's/status_update_\(.*\)\.json/\1/')
        local formatted_time=$(echo "$timestamp_part" | sed 's/\(..\)\(..\)\(..\)_\(..\)\(..\)\(..\)/20\1-\2-\3 \4:\5:\6/')
        
        echo "  $formatted_time: $filename"
        
        if check_jq; then
            local status_level=$(jq -r '.status.level // "unknown"' "$file" 2>/dev/null)
            local health_score=$(jq -r '.status.health_score // "unknown"' "$file" 2>/dev/null)
            local message=$(jq -r '.status.message // "No message"' "$file" 2>/dev/null)
            
            echo "    Level: $status_level, Health: $health_score%, Message: $message"
        fi
        
        echo ""
    done
}

# Clean up old status files
cleanup_status() {
    local retention_days="${1:-30}"
    local status_dir="$PROJECT_ROOT/.triune_monitor"
    
    log_info "Cleaning up status files older than $retention_days days"
    
    if [ ! -d "$status_dir" ]; then
        log_info "No status directory to clean"
        return 0
    fi
    
    local cleaned_count=0
    
    # Find and remove old files (but keep current_status.json)
    while IFS= read -r -d '' file; do
        if [ "$(basename "$file")" != "current_status.json" ]; then
            rm -f "$file"
            ((cleaned_count++))
            log_info "Removed: $(basename "$file")"
        fi
    done < <(find "$status_dir" -name "*.json" -type f -mtime +$retention_days -print0 2>/dev/null)
    
    if [ $cleaned_count -eq 0 ]; then
        log_info "No status files to clean up"
    else
        log_success "Cleaned up $cleaned_count old status files"
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  sync FILE                Sync status with Triune Monitor using results file"
    echo "  alert TYPE MESSAGE [PRI] Send alert (priority: low|medium|high)"
    echo "  status                   Show current status"
    echo "  history [COUNT]          Show status history (default: 10)"
    echo "  cleanup [DAYS]           Clean up status files older than DAYS (default: 30)"
    echo "  help                     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 sync mirror_watcher_results.json"
    echo "  $0 alert workflow_failure 'Daily workflow failed' high"
    echo "  $0 status"
    echo "  $0 history 5"
    echo "  $0 cleanup 14"
    echo ""
    echo "Environment variables:"
    echo "  TRIUNE_MONITOR_ENDPOINT  API endpoint for Triune Monitor"
    echo "  TRIUNE_MONITOR_API_KEY   API key for authentication"
}

# Main function
main() {
    local command="${1:-help}"
    
    case "$command" in
        sync)
            if [ $# -ne 2 ]; then
                log_error "Usage: $0 sync FILE"
                exit 1
            fi
            sync_status "$2"
            ;;
        alert)
            if [ $# -lt 3 ]; then
                log_error "Usage: $0 alert TYPE MESSAGE [PRIORITY]"
                exit 1
            fi
            send_alert "$2" "$3" "${4:-medium}"
            ;;
        status)
            get_status
            ;;
        history)
            list_status_history "${2:-10}"
            ;;
        cleanup)
            cleanup_status "${2:-30}"
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