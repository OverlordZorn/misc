# 🧩 GitHub Workflow Sync Tool

This folder contains a small automation that keeps workflow files in sync across multiple repositories.

---

## 🚀 Purpose

This action copies files from this repo’s local `Data/` directory into a set of target repositories.  
It’s ideal for sharing common GitHub workflows, templates, or configuration files between projects.

For example:
```
Data/workflows/release-drafter.yml → <target>/.github/workflows/release-drafter.yml
```

---

## 🧠 How It Works

- Defined repositories, ignore rules, and path mappings live in [`sync_data.py`](./sync_data.py).  
- The sync process is handled by [`sync_workflows.py`](./sync_workflows.py).  
- The GitHub Action workflow (`.github/workflows/sync-workflows.yml`) runs the script:
  - Automatically when relevant files change.
  - Or manually via the “Run workflow” button.

The script:
1. Reads the local `Data/` directory.  
2. Maps each file’s destination using `PATH_MAP`.  
3. Skips ignored files.  
4. Uploads or updates the files in each target repo using the GitHub API.  
5. Skips uploads if the file content hasn’t changed.  
6. Reports a summary of synced / skipped / failed files.

---

## ⚙️ Environment Setup

To authenticate, it uses **Personal Access Tokens (PATs)** — one per GitHub org or user.

Set these as repository secrets:

| Secret name | Used for | Required scopes |
|--------------|-----------|------------------|
| `PAT_OVERLORDZORN` | Pushes to repos owned by `overlordZorn` | `repo`, `workflow` |
| `PAT_CVO_ORG` | Pushes to repos under `CVO-Org` | `repo`, `workflow` |

> For fine-grained tokens, ensure **Contents: Read & write** and **Workflows: Read & write** permissions,  
> and include all relevant target repositories.

---

## 🧪 Running the Sync

You can run it in two modes:

| Mode | Description |
|------|--------------|
| `dry-run` | Prints what would be synced — no commits are made. |
| `real` | Uploads files and commits to the target repos. |

**Manual Run:**
1. Go to **Actions → Sync Workflows → Run workflow**.
2. Choose `dry-run` or `real`.
3. Watch the logs for the detailed sync summary.

---

## 🧾 Example Output

```
🔧 Mode: Real

📦 CVO-Org/CVO-Auxiliary
  🔀 workflows/release-drafter.yml → .github/workflows/release-drafter.yml
  ✅ Synced: .github/workflows/release-drafter.yml

📊 Summary:
  ✅ Synced:  2
  🚫 Skipped: 1
  ❌ Failed:  0

🎉 Sync complete!
```

---

## 🧰 Maintenance Tips

- To add or remove target repos: edit `REPOSITORIES` in [`sync_data.py`](./sync_data.py).
- To change which local folders sync where: update `PATH_MAP`.
- To skip certain files globally: add them to `IGNORE_FILES`.
- To ignore files per-repo: use the `ignore` list under each repo definition.

---

## 🧹 Common Issues

| Symptom | Likely Cause | Fix |
|----------|---------------|------|
| `403 - Resource not accessible by personal access token` | Token missing proper scopes | Re-generate PAT with `repo` + `workflow` scopes |
| `404 Not Found` | Repo name or branch mismatch | Ensure `branch="main"` exists, or adjust in script |
| No files updated | Nothing changed (SHA check skips identical content) | Modify file contents locally |

---

## 🏁 Quick Commands (Optional local run)

You can also test locally if you have Python 3 and your PATs exported:

```bash
export PAT_OVERLORDZORN=<your-token>
export PAT_CVO_ORG=<your-token>
python github-sync-workflows/sync_workflows.py dry-run
```

---

## 🧭 Visual Overview

```
             ┌───────────────────────────────┐
             │         This Repo             │
             │   github-sync-workflows/      │
             │       ├── Data/               │
             │       │   ├── workflows/...   │
             │       │   └── .github/...     │
             │       ├── sync_workflows.py   │
             │       └── sync_data.py        │
             └──────────────┬────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │       Target Repos          │
              │   e.g. CVO-Org/CVO-OGG      │
              │        overlordZorn/misc    │
              │        CVO-Org/CVO-Auxiliary│
              └─────────────────────────────┘
```

---

_Authored with ❤️ by your future self — because debugging GitHub API syncs twice is once too many._
