#!/bin/bash
set -euo pipefail

curl -X POST -H "Authorization: Bearer $PAT" -H "Content-Type: application/json" -d '{
    "name": "web",
    "active": true,
    "events": ["*"],
    "config": {
      "url": "'"$WEBHOOK_URL"'",
      "content_type": "json"
    }
}' "https://api.github.com/repos/$NAME/$REPO/hooks"



