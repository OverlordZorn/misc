#!/usr/bin/env python3
"""
Setup script to create, update, or delete GitHub labels.
Writes a protocol file next to the script to log all changes.
Supports dry-run, real, and purge-only modes.
"""

import os
import sys
import requests
from labels_data import LABELS, WHITELIST_LABELS
from repos_data import REPOSITORIES

# ---------------------------
# CONFIGURATION
# ---------------------------

# Token is passed via GitHub Action env var or CLI argument
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or (sys.argv[2] if len(sys.argv) > 2 else None)
MODE = sys.argv[1] if len(sys.argv) > 1 else "dry-run"  # dry-run, real, purge-only

if not GITHUB_TOKEN:
    sys.exit("❌ ERROR: Missing GitHub token. Pass it via env var GITHUB_TOKEN or as CLI arg.")

API_BASE = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

changes_log = []

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def create_or_update_label(owner, repo, label):
    """Creates or updates a single label in a GitHub repository."""
    url = f"{API_BASE}/repos/{owner}/{repo}/labels/{label['name']}"
    response = requests.get(url, headers=HEADERS)

    if MODE == "dry-run":
        if response.status_code == 200:
            changes_log.append(f"(Dry-run) Would update label '{label['name']}' in {owner}/{repo}")
        else:
            changes_log.append(f"(Dry-run) Would create label '{label['name']}' in {owner}/{repo}")
        return

    if response.status_code == 200:
        print(f"🔄 Updating label '{label['name']}' in {owner}/{repo}")
        r = requests.patch(url, headers=HEADERS, json=label)
        if r.status_code in (200, 201):
            changes_log.append(f"Updated label '{label['name']}' in {owner}/{repo}")
        else:
            changes_log.append(f"❌ Failed to update '{label['name']}' in {owner}/{repo}: {r.text}")
    else:
        print(f"➕ Creating label '{label['name']}' in {owner}/{repo}")
        r = requests.post(f"{API_BASE}/repos/{owner}/{repo}/labels", headers=HEADERS, json=label)
        if r.status_code in (200, 201):
            changes_log.append(f"Created label '{label['name']}' in {owner}/{repo}")
        else:
            changes_log.append(f"❌ Failed to create '{label['name']}' in {owner}/{repo}: {r.text}")


def delete_unlisted_labels(owner, repo):
    """Deletes labels that are not in LABELS or WHITELIST_LABELS."""
    url = f"{API_BASE}/repos/{owner}/{repo}/labels"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        changes_log.append(f"❌ Failed to fetch labels for {owner}/{repo}")
        return

    existing_labels = [l['name'] for l in response.json()]
    allowed_labels = [l['name'] for l in LABELS] + WHITELIST_LABELS

    for label_name in existing_labels:
        if label_name not in allowed_labels:
            if MODE == "dry-run":
                changes_log.append(f"(Dry-run) Would delete label '{label_name}' from {owner}/{repo}")
                continue
            if MODE == "purge-only" or MODE == "real":
                print(f"🗑️ Deleting label '{label_name}' from {owner}/{repo}")
                r = requests.delete(f"{API_BASE}/repos/{owner}/{repo}/labels/{label_name}", headers=HEADERS)
                if r.status_code == 204:
                    changes_log.append(f"Deleted label '{label_name}' from {owner}/{repo}")
                else:
                    changes_log.append(f"❌ Failed to delete '{label_name}' in {owner}/{repo}: {r.text}")


# ---------------------------
# MAIN
# ---------------------------

def main():
    for owner, repos in REPOSITORIES.items():
        for repo in repos:
            print(f"\n=== 🏷️ Applying labels to {owner}/{repo} ===")
            if MODE in ("real", "dry-run"):
                for label in LABELS:
                    create_or_update_label(owner, repo, label)
            if MODE in ("real", "purge-only", "dry-run"):
                delete_unlisted_labels(owner, repo)

    # Write protocol
    protocol_file = os.path.join(os.path.dirname(__file__), "protocol.md")
    with open(protocol_file, "w", encoding="utf-8") as f:
        f.write("# Label Updater Protocol\n\n")
        f.write(f"**Mode:** {MODE}\n\n")
        f.write("## Changes Applied\n")
        for line in changes_log:
            f.write(f"- {line}\n")
    print(f"\n📄 Protocol written to {protocol_file}")


if __name__ == "__main__":
    main()
