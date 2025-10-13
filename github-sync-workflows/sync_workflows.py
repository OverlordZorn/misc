#!/usr/bin/env python3
"""
Syncs files from the local Data directory into multiple GitHub repositories.
"""

import os
import sys
import base64
import requests
from sync_data import REPOSITORIES, IGNORE_FILES, PATH_MAP

API_BASE = "https://api.github.com"

# Token setup
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or (sys.argv[2] if len(sys.argv) > 2 else None)
if not GITHUB_TOKEN:
    sys.exit("❌ ERROR: Missing GitHub token. Set GITHUB_TOKEN as an environment variable or pass as CLI arg.")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "Data")
MODE = sys.argv[1] if len(sys.argv) > 1 else "dry-run"
DRY_RUN = MODE.lower() == "dry-run"


def should_ignore(repo_info, relative_path):
    """Check if a file should be ignored."""
    filename = os.path.basename(relative_path)
    if filename in IGNORE_FILES:
        return True
    for pattern in repo_info.get("ignore", []):
        if relative_path.endswith(pattern):
            return True
    return False


def map_relative_path(relative_path):
    """Convert a Data-relative path into a repo-relative path using PATH_MAP."""
    for local_prefix, remote_prefix in PATH_MAP.items():
        if relative_path.startswith(local_prefix):
            remainder = relative_path[len(local_prefix):]
            mapped = os.path.join(remote_prefix, remainder).replace("\\", "/")
            print(f"  🔀 Mapped: {relative_path} → {mapped}")
            return mapped
    print(f"  ⚠️  No mapping found for: {relative_path} (using as-is)")
    return relative_path


def get_remote_file(owner, repo, path):
    """Fetch existing file info (for update checks)."""
    url = f"{API_BASE}/repos/{owner}/{repo}/contents/{path}"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else None


def upload_file(owner, repo, path, content, message):
    """Upload or update a single file in the repo."""
    if DRY_RUN:
        print(f"[Dry-run] Would sync: {owner}/{repo}/{path}")
        return True

    remote_file = get_remote_file(owner, repo, path)
    data = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": "main",
    }
    if remote_file and "sha" in remote_file:
        data["sha"] = remote_file["sha"]

    url = f"{API_BASE}/repos/{owner}/{repo}/contents/{path}"
    r = requests.put(url, headers=HEADERS, json=data)

    if r.status_code not in (200, 201):
        print(f"❌ Failed: {owner}/{repo}/{path} - {r.status_code}")
        return False
    else:
        print(f"✅ Synced: {owner}/{repo}/{path}")
        return True


def main():
    print(f"Mode: {'Dry-Run' if DRY_RUN else 'Real'}\n")

    for repo_info in REPOSITORIES:
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        print(f"📦 {owner}/{repo}")

        if not os.path.exists(DATA_DIR):
            print(f"❌ Data directory not found: {DATA_DIR}")
            continue

        for root, _, files in os.walk(DATA_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, DATA_DIR).replace("\\", "/")

                if should_ignore(repo_info, relative_path):
                    continue

                mapped_path = map_relative_path(relative_path)

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    print(f"❌ Failed to read {relative_path}: {e}")
                    continue

                upload_file(
                    owner,
                    repo,
                    mapped_path,
                    content,
                    f"📝 Updated {mapped_path}"
                )

    print("\n✅ Sync complete!")


if __name__ == "__main__":
    main()