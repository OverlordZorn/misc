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

# Token setup - support multiple PATs for different orgs/users
def get_token_for_repo(owner):
    """Get the appropriate token for a repo owner."""
    # Try owner-specific token first (e.g., PAT_OVERLORDZORN, PAT_CVO_ORG)
    env_key = f"PAT_{owner.upper().replace('-', '_')}"
    org_token = os.getenv(env_key)
    if org_token:
        return org_token
    
    return None

def get_headers(owner):
    """Get authorization headers for a repo owner."""
    token = get_token_for_repo(owner)
    if not token:
        env_key = f"PAT_{owner.upper().replace('-', '_')}"
        sys.exit(f"❌ ERROR: Missing token for {owner}. Set {env_key} as an environment variable.")
    
    return {
        "Authorization": f"token {token}",
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
    r = requests.get(url, headers=get_headers(owner))
    return r.json() if r.status_code == 200 else None


def ensure_directory(owner, repo, path):
    """Create parent directory structure recursively by adding .gitkeep files."""
    parent_dir = "/".join(path.split("/")[:-1])
    if not parent_dir:
        return True
    
    # Split path into parts and create each level
    parts = parent_dir.split("/")
    for i in range(len(parts)):
        current_dir = "/".join(parts[:i+1])
        gitkeep_path = f"{current_dir}/.gitkeep"
        
        if DRY_RUN:
            print(f"  [Dry-run] Would create: {current_dir}")
            continue
        
        # Check if this level already exists
        existing = get_remote_file(owner, repo, gitkeep_path)
        if existing:
            continue
        
        data = {
            "message": f"Create directory: {current_dir}",
            "content": base64.b64encode(b"").decode(),
            "branch": "main",
        }
        
        url = f"{API_BASE}/repos/{owner}/{repo}/contents/{gitkeep_path}"
        r = requests.put(url, headers=get_headers(owner), json=data)
        
        if r.status_code not in (200, 201):
            try:
                error_msg = r.json().get("message", r.text)
            except:
                error_msg = r.text
            print(f"  ⚠️  Could not create {current_dir}: {r.status_code} - {error_msg}")
            if r.status_code == 404:
                print(f"     (Trying to PUT: {url})")
            return False
        
        print(f"  📁 Created: {current_dir}")
    
    return True


def upload_file(owner, repo, path, content, message):
    """Upload or update a single file in the repo."""
    if DRY_RUN:
        print(f"[Dry-run] Would sync: {owner}/{repo}/{path}")
        return True

    # Ensure parent directory exists
    if not ensure_directory(owner, repo, path):
        return False

    remote_file = get_remote_file(owner, repo, path)
    data = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": "main",
    }
    if remote_file and "sha" in remote_file:
        data["sha"] = remote_file["sha"]

    url = f"{API_BASE}/repos/{owner}/{repo}/contents/{path}"
    r = requests.put(url, headers=get_headers(owner), json=data)

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