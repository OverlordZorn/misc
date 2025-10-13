#!/usr/bin/env python3
"""
Syncs files from the local Data directory into multiple GitHub repositories.
Refactored for safety, clarity, and performance.
Includes a blacklist feature: files listed in BLACKLIST_FILES are deleted from the repo if present.
"""

import os
import sys
import base64
import requests
from sync_data import REPOSITORIES, IGNORE_FILES, PATH_MAP, BLACKLIST_FILES

API_BASE = "https://api.github.com"

# =============================================================================
#  Auth & Configuration
# =============================================================================

def get_token_for_repo(owner):
    """Get the appropriate PAT for a repo owner (e.g., PAT_OVERLORDZORN)."""
    env_key = f"PAT_{owner.upper().replace('-', '_')}"
    token = os.getenv(env_key)
    if not token:
        sys.exit(f"❌ ERROR: Missing token for {owner}. Please set {env_key} in environment.")
    return token

def get_headers(owner):
    """Return authorization headers for API calls."""
    token = get_token_for_repo(owner)
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

DATA_DIR = os.path.join(os.path.dirname(__file__), "Data")
MODE = sys.argv[1] if len(sys.argv) > 1 else "dry-run"
DRY_RUN = MODE.lower() == "dry-run"

# =============================================================================
#  Utility Functions
# =============================================================================

def should_ignore(repo_info, relative_path):
    """Return True if file should be ignored."""
    filename = os.path.basename(relative_path)
    if filename in IGNORE_FILES:
        return True
    for pattern in repo_info.get("ignore", []):
        if relative_path.endswith(pattern):
            return True
    return False

def map_relative_path(relative_path):
    """Map local path (under Data/) to remote repo path via PATH_MAP."""
    for local_prefix, remote_prefix in PATH_MAP.items():
        if relative_path.startswith(local_prefix):
            remainder = relative_path[len(local_prefix):]
            mapped = os.path.join(remote_prefix, remainder).replace("\\", "/")
            print(f"  🔀 {relative_path} → {mapped}")
            return mapped
    print(f"  ⚠️  No mapping found for: {relative_path} (using as-is)")
    return relative_path

def get_remote_file(owner, repo, path):
    """Fetch file metadata from GitHub (returns dict or None)."""
    url = f"{API_BASE}/repos/{owner}/{repo}/contents/{path}"
    r = requests.get(url, headers=get_headers(owner))
    if r.status_code == 200:
        return r.json()
    return None

def upload_file(owner, repo, path, content, message):
    """Upload or update a file in a target repository."""
    if DRY_RUN:
        print(f"  [Dry-run] Would sync: {path}")
        return True

    existing = get_remote_file(owner, repo, path)

    # Check for no changes (avoid unnecessary commits)
    encoded_content = base64.b64encode(content.encode()).decode()
    if existing and existing.get("content"):
        try:
            remote_content = base64.b64decode(existing["content"]).decode().strip()
            if remote_content.strip() == content.strip():
                print(f"  ⏩ Skipped (no change): {path}")
                return True
        except Exception:
            pass  # if decoding fails, proceed to upload

    data = {
        "message": message,
        "content": encoded_content,
        "branch": "main",
    }

    if existing and "sha" in existing:
        data["sha"] = existing["sha"]

    url = f"{API_BASE}/repos/{owner}/{repo}/contents/{path}"
    r = requests.put(url, headers=get_headers(owner), json=data)

    if r.status_code in (200, 201):
        print(f"  ✅ Synced: {path}")
        return True
    else:
        try:
            err = r.json().get("message", r.text)
        except Exception:
            err = r.text
        print(f"  ❌ Failed: {path} ({r.status_code}) - {err}")
        return False

def delete_file(owner, repo, path):
    """Delete a file in the repository if it exists."""
    if DRY_RUN:
        print(f"  [Dry-run] Would delete: {path}")
        return True

    existing = get_remote_file(owner, repo, path)
    if not existing or "sha" not in existing:
        print(f"  ⏩ Skipped delete (file not found): {path}")
        return True

    data = {
        "message": f"🗑️ Delete blacklisted file {path}",
        "sha": existing["sha"],
        "branch": "main",
    }

    url = f"{API_BASE}/repos/{owner}/{repo}/contents/{path}"
    r = requests.delete(url, headers=get_headers(owner), json=data)

    if r.status_code in (200, 201):
        print(f"  ✅ Deleted: {path}")
        return True
    else:
        try:
            err = r.json().get("message", r.text)
        except Exception:
            err = r.text
        print(f"  ❌ Failed to delete {path}: {r.status_code} - {err}")
        return False

# =============================================================================
#  Main Sync Logic
# =============================================================================

def main():
    print(f"🔧 Mode: {'Dry-Run' if DRY_RUN else 'Real'}\n")

    if not os.path.exists(DATA_DIR):
        sys.exit(f"❌ Data directory not found: {DATA_DIR}")

    total_synced = 0
    total_skipped = 0
    total_deleted = 0
    total_failed = 0

    for repo_info in REPOSITORIES:
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        print(f"\n📦 {owner}/{repo}")

        for root, _, files in os.walk(DATA_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, DATA_DIR).replace("\\", "/")
                mapped_path = map_relative_path(relative_path)

                # --- Blacklist handling ---
                if mapped_path in BLACKLIST_FILES:
                    ok = delete_file(owner, repo, mapped_path)
                    if ok:
                        total_deleted += 1
                    else:
                        total_failed += 1
                    continue  # skip to next file

                # --- Ignore handling ---
                if should_ignore(repo_info, relative_path):
                    print(f"  🚫 Ignored: {relative_path}")
                    total_skipped += 1
                    continue

                # --- Upload file ---
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    print(f"  ❌ Failed to read {relative_path}: {e}")
                    total_failed += 1
                    continue

                ok = upload_file(
                    owner,
                    repo,
                    mapped_path,
                    content,
                    f"📝 Update {mapped_path}"
                )

                if ok:
                    total_synced += 1
                else:
                    total_failed += 1

    # Summary
    print("\n📊 Summary:")
    print(f"  ✅ Synced:   {total_synced}")
    print(f"  🚫 Skipped:  {total_skipped}")
    print(f"  🗑️ Deleted:  {total_deleted}")
    print(f"  ❌ Failed:   {total_failed}")

    if total_failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 Sync complete!")


if __name__ == "__main__":
    main()
