# sync_data.py
# Defines repositories, ignore rules, and mapping for file sync.

# Global ignore list (applies to all repos)
IGNORE_FILES = [
    # ".gitkeep",
    # "README.md",
]

# Path mappings: local → remote
# Keys are relative paths inside your Data/ folder.
# Values are the target path inside the destination repo.
PATH_MAP = {
    ".github/": ".github/",                     # copy as-is
    "workflows/": ".github/workflows/",         # Data/workflows → .github/workflows/
}

# Repositories to sync and their per-repo ignore rules
REPOSITORIES = [
    {
        "owner": "overlordZorn", "repo": "misc",
        "ignore": [
        #    ".github/workflows/custom-build.yml",
        ],
    },
    {
        "owner": "CVO-Org", "repo": "CVO-Auxiliary",
        "ignore": [],
    },
    {
        "owner": "CVO-Org", "repo": "CVO-OGG",
        "ignore": [],
    },
]
