# GitHub Label Updater Cheat Sheet

This repository contains a Python-based GitHub label updater for managing multiple Arma 3 mod repositories. It allows you to **create, update, and clean up labels** across repositories in a safe and automated way.

---

## 📁 Folder Structure

```
.github/workflows/sync-labels.yml     # GitHub Actions workflow
/github-sync-labels/
    setup_labels.py                   # Python script
    labels_data.py                    # Your curated labels database
    repos_data.py                     # List of repos to update
```

---

## 🐍 Python Script Overview (`setup_labels.py`)

- **Creates / updates labels** from `labels_data.py`
- **Deletes labels not in your curated database** unless whitelisted (`WHITELIST_LABELS`)
- **Supports dry-run mode** (`DRY_RUN = True`) for safe testing
- **Per-repo summary**:

```
📊 owner/repo summary:
  ➕ Created: X
  🔄 Updated: Y
  🗑️ Deleted: Z
  ❌ Failures: W
```

- **Whitelist** example:

```python
WHITELIST_LABELS = ["Do Not Delete", "Important", "Legacy"]
```

- **Dry-run toggle**:

```python
DRY_RUN = True   # Preview only
DRY_RUN = False  # Actually apply changes
```

---

## 🗂️ Data Files

### `labels_data.py`

```python
LABELS = [
    {"name": "meta/fix", "color": "d73a4a"},
    {"name": "meta/feature", "color": "0e8a16"},
    # Add your standard labels here
]
```

### `repos_data.py`

```python
REPOSITORIES = [
    {"owner": "YourGitHubUsername", "repo": "arma3-core"},
    {"owner": "ArmADevTeam", "repo": "mod_ai_enhancer"},
    # Add more repos here
]
```

---

## ⚙️ GitHub Actions Workflow (`.github/workflows/sync-labels.yml`)

- **Manual trigger (`workflow_dispatch`)** with `mode: dry-run / real`
- **Runs Python script**, enables dry-run automatically if selected
- **Collapsible per-repo logs** for readability

Trigger a dry-run:

```
Actions → Sync Labels → Run workflow → mode: dry-run
```

Trigger a real run:

```
Actions → Sync Labels → Run workflow → mode: real
```

---

## 🔑 Token / Permissions

- **Secret:** `GH_PAT` (personal access token or fine-grained token)
- **Required scopes:**
  - `repo → Read & Write` (for labels)
  - `metadata → Read-only` (if org info needed)
- **Passed to Python script** via environment variable:

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GH_PAT }}
```

---

## 💡 Tips for Future-Proofing

1. **Add more repos** → just edit `repos_data.py`
2. **Add more labels** → just edit `labels_data.py`
3. **Dry-run always safe** → check changes before committing
4. **Logs readable per repo** → easy to scan or collapse in Actions UI
5. **Later expansion:** output Markdown/CSV summaries, post to PRs, support multiple org tokens

---

## ✅ Quick Workflow

1. Trigger **dry-run** to preview changes.
2. Check logs per repo (collapsible sections).
3. Switch to **real mode** to apply changes when confident.

---

This cheat sheet helps you get started quickly and safely manage GitHub labels across all your repositories.

