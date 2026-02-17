#!/usr/bin/env bash

set -euo pipefail

API_URL="http://localhost:8000/api/v1"
EMAIL=""
PASSWORD=""
DRY_RUN="false"
ONLY_ERROR="false"

usage() {
  cat <<'EOF'
Reindex all documents for all projects owned by one user.

Usage:
  scripts/reindex_all_documents_for_user.sh --email <email> --password <password> [--api-url <url>] [--dry-run] [--only-error]

Options:
  --email     User email used for login (required)
  --password  User password used for login (required)
  --api-url   API base URL (default: http://localhost:8000/api/v1)
  --dry-run   List what would be reindexed without calling reindex endpoint
  --only-error Reindex only documents with status=error
  -h, --help  Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --email)
      EMAIL="${2:-}"
      shift 2
      ;;
    --password)
      PASSWORD="${2:-}"
      shift 2
      ;;
    --api-url)
      API_URL="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    --only-error)
      ONLY_ERROR="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$EMAIL" || -z "$PASSWORD" ]]; then
  echo "Error: --email and --password are required." >&2
  usage
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required." >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required." >&2
  exit 1
fi

API_URL="${API_URL%/}"

echo "Logging in user: $EMAIL"
login_payload="$(jq -n --arg email "$EMAIL" --arg password "$PASSWORD" '{email: $email, password: $password}')"
token_response="$(
  curl -fsS \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -X POST \
    -d "$login_payload" \
    "$API_URL/auth/login"
)"

TOKEN="$(jq -r '.access_token // empty' <<<"$token_response")"
if [[ -z "$TOKEN" ]]; then
  echo "Error: login failed, no access_token returned." >&2
  echo "$token_response" >&2
  exit 1
fi

auth_header=(-H "Authorization: Bearer $TOKEN")
json_header=(-H "Accept: application/json")

echo "Fetching projects from: $API_URL/projects"
projects_json="$(curl -fsS "${auth_header[@]}" "${json_header[@]}" "$API_URL/projects")"
project_rows="$(jq -r '.[] | "\(.id)\t\(.name // "")"' <<<"$projects_json")"

if [[ -z "$project_rows" ]]; then
  echo "No project found for this user."
  exit 0
fi

total_projects=0
total_documents=0
successes=0
failures=0
skipped=0

while IFS=$'\t' read -r project_id project_name; do
  [[ -z "$project_id" ]] && continue
  total_projects=$((total_projects + 1))
  echo
  if [[ -n "$project_name" ]]; then
    echo "Project: $project_name ($project_id)"
  else
    echo "Project: $project_id"
  fi

  documents_json="$(curl -fsS "${auth_header[@]}" "${json_header[@]}" "$API_URL/projects/$project_id/documents")"
  document_ids=()
  while IFS= read -r document_id; do
    [[ -n "$document_id" ]] && document_ids+=("$document_id")
  done < <(jq -r '.[].id' <<<"$documents_json")

  if [[ "$ONLY_ERROR" == "true" ]]; then
    status_summary="$(jq -r 'group_by(.status) | map("\(.[0].status):\(length)") | join(", ")' <<<"$documents_json")"
    if [[ -n "$status_summary" ]]; then
      echo "  Statuses: $status_summary"
    fi
  fi

  if [[ ${#document_ids[@]} -eq 0 ]]; then
    echo "  No documents."
    continue
  fi

  for document_id in "${document_ids[@]}"; do
    [[ -z "$document_id" ]] && continue

    if [[ "$ONLY_ERROR" == "true" ]]; then
      status="$(
        jq -r --arg id "$document_id" '.[] | select(.id == $id) | .status // ""' <<<"$documents_json" \
        | tr '[:upper:]' '[:lower:]'
      )"
      if [[ "$status" != "error" ]]; then
        skipped=$((skipped + 1))
        continue
      fi
    fi

    total_documents=$((total_documents + 1))

    if [[ "$DRY_RUN" == "true" ]]; then
      echo "  [dry-run] would reindex: $document_id"
      continue
    fi

    status_code="$(
      curl -sS -o /tmp/raggae-reindex-response.json -w "%{http_code}" \
        -X POST \
        "${auth_header[@]}" \
        "${json_header[@]}" \
        "$API_URL/projects/$project_id/documents/$document_id/reindex"
    )"

    if [[ "$status_code" == "200" ]]; then
      successes=$((successes + 1))
      echo "  [ok] reindexed: $document_id"
    else
      failures=$((failures + 1))
      echo "  [error] $document_id (HTTP $status_code)"
      if [[ -s /tmp/raggae-reindex-response.json ]]; then
        if jq -e . >/dev/null 2>&1 </tmp/raggae-reindex-response.json; then
          jq -r '.' /tmp/raggae-reindex-response.json
        else
          cat /tmp/raggae-reindex-response.json
        fi
      fi
    fi
  done
done <<<"$project_rows"

echo
echo "Done."
echo "Projects processed: $total_projects"
echo "Documents found: $total_documents"
if [[ "$ONLY_ERROR" == "true" ]]; then
  echo "Documents skipped (status != error): $skipped"
fi
if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry-run mode enabled: no reindex calls made."
else
  echo "Reindex success: $successes"
  echo "Reindex failures: $failures"
fi
