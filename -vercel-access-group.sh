#!/bin/bash

# Usage:
#   export VERCEL_TOKEN=your_token_here
#   ./create-vercel-access-group.sh "Engineering Admins" "prj_xxx" "ADMIN" "usr_1a2b3c4d5e6f7g8h9i0j,usr_2b3c4d5e6f7g8h9i0j1k"
#
# Arguments:
#   $1 - Access group name (e.g., "Engineering Admins")
#   $2 - Project ID (e.g., "prj_xxxxxxxx")
#   $3 - Role (e.g., "ADMIN")
#   $4 - Comma-separated user IDs (e.g., "usr_x,usr_y")

set -euo pipefail

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required but not installed."
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Warning: jq is not installed. API response will not be pretty-printed."
  JQ_PRESENT=0
else
  JQ_PRESENT=1
fi

if [ -z "${VERCEL_TOKEN:-}" ]; then
  echo "Error: Please set the VERCEL_TOKEN environment variable."
  exit 1
fi

if [ "$#" -ne 4 ]; then
  echo "Usage: $0 \"Group Name\" \"ProjectID\" \"Role\" \"UserID1,UserID2,...\""
  exit 1
fi

GROUP_NAME="$1"
PROJECT_ID="$2"
ROLE="$3"
USER_IDS="$4"

# Convert comma-separated user IDs to JSON array
IFS=',' read -ra IDS <<< "$USER_IDS"
MEMBERS_JSON=$(printf '"%s",' "${IDS[@]}")
MEMBERS_JSON="[${MEMBERS_JSON%,}]"

DATA=$(cat <<EOF
{
  "name": "$GROUP_NAME",
  "projects": [
    {
      "projectId": "$PROJECT_ID",
      "role": "$ROLE"
    }
  ],
  "membersToAdd": $MEMBERS_JSON
}
EOF
)

RESPONSE=$(curl --silent --show-error --fail --request POST \
  --url "https://api.vercel.com/v1/access-groups" \
  --header "Authorization: Bearer $VERCEL_TOKEN" \
  --header "Content-Type: application/json" \
  --data "$DATA"
)

if [ $? -eq 0 ]; then
  echo "Access group created successfully:"
  if [ "$JQ_PRESENT" -eq 1 ]; then
    echo "$RESPONSE" | jq .
  else
    echo "$RESPONSE"
  fi
else
  echo "Failed to create access group."
  exit 1
fi
