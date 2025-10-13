#!/usr/bin/env python3
"""
Setup script to create, update, or purge GitHub labels.
Supports:
- dry-run
- real (apply curated labels)
- purge-only (delete all non-whitelisted labels, do not create anything)
"""

import os
import sys
import requests
from labels_data import LABELS, WHITELIST_LABELS
from repos_data import REPOSITORIES

# ---------------------------
# CONFIGURATION
# ---------------------------

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or (sys.argv[2] if len(sys.argv) > 2 else None)
if not GITHUB_TOKEN:
    sys.exit("❌ ERROR: Missing GitHub token. Pass it via env var GITHUB_TOKEN or as CLI arg.")

API_BASE = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def create_or_update_label(owner, repo, label):
    """Creates or updates a single label in a GitHub repository."""
    url = f"{API_BASE}/repos/{owner}/{repo}/labels/{label['name']}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        r = requests.patch(url, headers=HEADERS, json=label)
        return "updated" if r.status_code in (200, 201) else "failed", label['name']
    else:
        r = requests.post(f"{API_BASE}/repos/{owner}/{repo}/labels", headers=HEADERS, json=label)
        return "created" if r.status_code in (200, 201) else "failed", label['name']

def delete_untracked_labels(owner, repo, labels_to_keep, whitelist):
    """Deletes all labels not in labels_to_keep or whitelist."""
    url = f"{API_BASE}/repos/{owner}/{repo}/labels"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Failed to list labels for {owner}/{repo}: {response.status_code} - {response.text}")
        return []

    deleted_labels = []
    for label in response.json():
        name = label['name']
        if name not in labels_to_keep and name not in whitelist:
            r = requests.delete(f"{API_BASE}/repos/{owner}/{repo}/labels/{name}", headers=HEADERS)
            if r.status_code == 204:
                deleted_labels.append(name)
    return deleted_labels

# ---------------------------
# MAIN SCRIPT
# ---------------------------

def main():
    # Determine mode
    mode = sys.argv[1] if len(sys.argv) > 1 else "real"
    label_names = [label['name'] for label in LABELS]

    for repo_entry in REPOSITORIES:
        owner = repo_entry["owner"]
        repo = repo_entry["repo"]

        # Per-repo tracking
        repo_summary = {"created": [], "updated": [], "deleted": [], "failed": []}

        print(f"\n=== 🏷️ Processing {owner}/{repo} ===")

        if mode == "purge-only":
            deleted = delete_untracked_labels(owner, repo, [], WHITELIST_LABELS)
            repo_summary["deleted"].extend(deleted)
            print(f"⚠️ Purge-only mode: No labels created or updated for {owner}/{repo}")
        else:
            # Delete untracked labels (only in real or dry-run)
            deleted = delete_untracked_labels(owner, repo, label_names, WHITELIST_LABELS)
            repo_summary["deleted"].extend(deleted)

            # Create/update labels
            for label in LABELS:
                result, name = create_or_update_label(owner, repo, label)
                repo_summary[result].append(name)

        # Print per-repo summary
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

if __name__ == "__main__":
    main()
