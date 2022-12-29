#!/usr/bin/env python3


import requests, os

NAME = os.environ['NAME']
QNAME = os.environ['QNAME']
PAT = os.environ['PAT']
SECRET = os.environ['GITHUB_SECRET']


# Set the URL for the first page of results
url = f"https://api.github.com/{QNAME}/repos?type=public&direction=desc&sort=pushed&per_page=1000"

response = requests.get(url, headers={"Authorization": f"Bearer {PAT}"})
result = response.json()
print(result)
for repo in result:
        repo_name = repo["name"]
        print(f"Updating webhook secret for repository {repo_name}...")

        # Get the list of webhooks for the repository
        response = requests.get(
            f"https://api.github.com/repos/{NAME}/{repo_name}/hooks",
            headers={"Authorization": f"Bearer {PAT}"}
        )
        webhooks = response.json()

        # Find the webhook that you want to update
        print(webhooks)
        webhook = next(w for w in webhooks if 'spam' in w["config"]['url'])
        webhook_id = webhook["id"]

        # Update the webhook secret
        requests.patch(
            f"https://api.github.com/repos/{NAME}/{repo_name}/hooks/{webhook_id}/config",
            headers={"Authorization": f"Bearer {PAT}", "Content-Type": "application/json"},
            json={"secret": SECRET},
        )


print("Done!")
