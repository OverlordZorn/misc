#!/usr/bin/env python3
"""
Setup script to create or update GitHub labels across multiple repositories.
- Works with both personal and organization repos listed in repos_data.py
- Keeps curated labels from labels_data.py
- Deletes labels not in the curated set unless whitelisted
- Supports optional dry-run mode
- Provides summary of actions at the end
"""

import os
import sys
import requests
from labels_data import LABELS
from repos_data import REPOSITORIES

# ---------------------------
# CONFIGURATION
# ---------------------------

# Token is passed via GitHub Action environment variable or CLI argument
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)
if not GITHUB_TOKEN:
    sys.exit("❌ ERROR: Missing GitHub token. Pass it via env var GITHUB_TOKEN or as CLI arg.")

# Set True to preview deletions without making changes
DRY_RUN = False

# Labels that are protected from deletion even if not in LABELS
WHITELIST_LABELS = [ "Legacy" ]

API_BASE = "https://api.github.com"

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def create_or_update_label(owner, repo, label, token):
    """Creates or updates a single label in a GitHub repository."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"{API_BASE}/repos/{owner}/{repo}/labels/{label['name']}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        r = requests.patch(url, headers=headers, json=label)
        if r.status_code in (200, 201):
            return "updated"
        else:
            print(f"❌ Failed to update '{label['name']}' in {owner}/{repo}: {r.status_code} - {r.text}")
            return "failed"
    else:
        r = requests.post(f"{API_BASE}/repos/{owner}/{repo}/labels", headers=headers, json=label)
        if r.status_code in (200, 201):
            return "created"
        else:
            print(f"❌ Failed to create '{label['name']}' in {owner}/{repo}: {r.status_code} - {r.text}")
            return "failed"

def delete_untracked_labels(owner, repo, token, labels_to_keep, whitelist):
    """
    Delete all labels in the repo that are NOT in labels_to_keep or the whitelist.
    Returns a list of deleted label names.
    """
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
        label_name = label['name']
        if label_name not in labels_to_keep and label_name not in whitelist:
            if DRY_RUN:
                print(f"🗑️ [DRY RUN] Would delete label '{label_name}' from {owner}/{repo}")
            else:
                del_url = f"{API_BASE}/repos/{owner}/{repo}/labels/{label_name}"
                del_response = requests.delete(del_url, headers=headers)
                if del_response.status_code == 204:
                    print(f"🗑️ Deleted label '{label_name}' from {owner}/{repo}")
                    deleted_labels.append(label_name)
                else:
                    print(f"❌ Failed to delete '{label_name}' from {owner}/{repo}: {del_response.status_code} - {del_response.text}")
    return deleted_labels

# ---------------------------
# MAIN SCRIPT
# ---------------------------

def main():
    summary = {
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "failed": 0
    }

    token = GITHUB_TOKEN
    label_names = [label['name'] for label in LABELS]

    for repo_entry in REPOSITORIES:
        owner = repo_entry["owner"]
        repo = repo_entry["repo"]

        print(f"\n=== 🏷️ Cleaning extra labels in {owner}/{repo} ===")
        deleted = delete_untracked_labels(owner, repo, token, label_names, WHITELIST_LABELS)
        summary["deleted"] += len(deleted)

        print(f"=== 🏷️ Applying standard labels to {owner}/{repo} ===")
        for label in LABELS:
            result = create_or_update_label(owner, repo, label, token)
            if result in summary:
                summary[result] += 1
            else:
                summary["failed"] += 1

    print("\n✅ Label update completed!")
    print(f"Labels created: {summary['created']}")
    print(f"Labels updated: {summary['updated']}")
    print(f"Labels deleted: {summary['deleted']}")
    print(f"Failures: {summary['failed']}")
    if DRY_RUN:
        print("⚠️ DRY RUN mode enabled — no labels were actually deleted or created.")
    if WHITELIST_LABELS:
        print(f"⚠️ Whitelisted labels not deleted: {', '.join(WHITELIST_LABELS)}")

if __name__ == "__main__":
    main()
