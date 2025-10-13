# sync_data.py
# Defines repositories, ignore rules, and mapping for file sync.

# Global ignore list (applies to all repos)
IGNORE_FILES = [
    # ".gitkeep",
    # "README.md",
]


BLACKLIST_FILES = [
    ".github/.gitkeep",
    ".github/release.yml",

    ".github/workflows/sqf-validator.yml",
    ".github/workflows/arma.yml",
    ".github/workflows/validate.yml",
    ".github/workflows/hemtt.yml",

    "tools/stringtablediag.py",
    "tools/sqf_validator.py",
    "tools/config_style_checker.py",
    "tools/update_hemtt.bat"
]



# Path mappings: local → remote
# Keys are relative paths inside your Data/ folder.
# Values are the target path inside the destination repo.
PATH_MAP = {
    ".github/": ".github/",                     # copy as-is
    "workflows/": ".github/workflows/",         # Data/workflows → .github/workflows/
    "tools/": "tools/",
}

# Repositories to sync and their per-repo ignore rules
REPOSITORIES = [
    {
        "owner": "OverlordZorn", "repo": "ZRN-Mod-Template",
        "ignore": [
        #    ".github/workflows/custom-build.yml",
        ],
    },
    {
        "owner": "OverlordZorn", "repo": "STORM-Framework",
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
    {
        "owner": "CVO-Org", "repo": "ron",
        "ignore": [],
    },
    {
        "owner": "CVO-Org", "repo": "ZEIC",
        "ignore": [],
    },
    {
        "owner": "CVO-Org", "repo": "CVO-CBA-Settings",
        "ignore": [],
    },
    {
        "owner": "CVO-Org", "repo": "CVO-Compatibilities",
        "ignore": [],
    },
]
