#!/bin/bash
set -euo pipefail

URL="https://api.github.com/$QNAME/repos?type=public&direction=desc&sort=pushed&per_page=1000"
result=$(curl -s -H "Authorization: Bearer $PAT" "$URL")
repos=$(echo "$result" | jq -r '.[] | .name')

printf '%s\n' "${repos[@]}"
#exit 0

for repo in $repos; do
  export REPO=$repo
  set -x
  ./add_webhook_to_repo.sh
done

