#!/usr/bin/env python3
"""
Setup script to create or update GitHub labels across multiple repositories.
- Works with both personal and organization repos listed in repos_data.py
- Keeps curated labels from labels_data.py
- Deletes labels not in the curated set unless whitelisted
- Supports optional dry-run mode
- Logs which labels were created, updated, deleted, or skipped
- Provides per-repo mini-summary for GitHub Actions
"""

import os
import sys
import requests
from labels_data import LABELS, WHITELIST_LABELS
from repos_data import REPOSITORIES

# ---------------------------
# CONFIGURATION
# ---------------------------

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)
if not GITHUB_TOKEN:
    sys.exit("❌ ERROR: Missing GitHub token. Pass it via env var GITHUB_TOKEN or as CLI arg.")

DRY_RUN = False

API_BASE = "https://api.github.com"

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def create_or_update_label(owner, repo, label, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"{API_BASE}/repos/{owner}/{repo}/labels/{label['name']}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        r = requests.patch(url, headers=headers, json=label)
        if r.status_code in (200, 201):
            return "updated", label['name']
        else:
            return "failed", label['name']
    else:
        r = requests.post(f"{API_BASE}/repos/{owner}/{repo}/labels", headers=headers, json=label)
        if r.status_code in (200, 201):
            return "created", label['name']
        else:
            return "failed", label['name']

def delete_untracked_labels(owner, repo, token, labels_to_keep, whitelist):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"{API_BASE}/repos/{owner}/{repo}/labels"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to list labels for {owner}/{repo}: {response.status_code} - {response.text}")
        return []

    deleted_labels = []
    existing_labels = response.json()
    for label in existing_labels:
        name = label['name']
        if name not in labels_to_keep and name not in whitelist:
            if DRY_RUN:
                deleted_labels.append(name)
            else:
                del_url = f"{API_BASE}/repos/{owner}/{repo}/labels/{name}"
                del_response = requests.delete(del_url, headers=headers)
                if del_response.status_code == 204:
                    deleted_labels.append(name)
    return deleted_labels

# ---------------------------
# MAIN SCRIPT
# ---------------------------

def main():
    token = GITHUB_TOKEN
    label_names = [label['name'] for label in LABELS]

    for repo_entry in REPOSITORIES:
        owner = repo_entry["owner"]
        repo = repo_entry["repo"]

        # Per-repo tracking
        repo_summary = {"created": [], "updated": [], "deleted": [], "failed": []}

        print(f"\n=== 🏷️ Processing {owner}/{repo} ===")

        # Delete untracked labels
        deleted = delete_untracked_labels(owner, repo, token, label_names, WHITELIST_LABELS)
        repo_summary["deleted"].extend(deleted)

        # Create/update labels
        for label in LABELS:
            result, name = create_or_update_label(owner, repo, label, token)
            repo_summary[result].append(name)

        # Print per-repo mini-summary
        print(f"\n📊 {owner}/{repo} summary:")
        print(f"  ➕ Created: {len(repo_summary['created'])}")
        print(f"  🔄 Updated: {len(repo_summary['updated'])}")
        print(f"  🗑️ Deleted: {len(repo_summary['deleted'])}")
        print(f"  ❌ Failures: {len(repo_summary['failed'])}")

        # Detailed per-label log
        for label in repo_summary["created"]:
            print(f"  ➕ {label}")
        for label in repo_summary["updated"]:
            print(f"  🔄 {label}")
        for label in repo_summary["deleted"]:
            print(f"  🗑️ {label}")
        for label in repo_summary["failed"]:
            print(f"  ❌ {label}")

        if DRY_RUN:
            print("⚠️ DRY RUN — no labels were actually deleted or created")
        if WHITELIST_LABELS:
            print(f"⚠️ Whitelisted labels not deleted: {', '.join(WHITELIST_LABELS)}")

if __name__ == "__main__":
    main()
