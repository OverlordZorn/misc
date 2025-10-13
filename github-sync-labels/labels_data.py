# labels_data.py
"""
Label definitions for Arma 3 mod repositories.
This file acts as the "label database" imported by setup_labels.py
"""

LABELS = [

    # --- PR Labels ---
    {"name": "pr/feature", "color": "2ecc71", "description": "New gameplay features, mechanics, or assets"},
    {"name": "pr/improvement", "color": "27ae60", "description": "Enhancements or optimizations to existing gameplay functionality"},
    {"name": "pr/fix", "color": "e74c3c", "description": "Bug fixes or issues affecting gameplay"},
    {"name": "pr/refactor", "color": "95a5a6", "description": "Internal code or structure changes without altering gameplay"},
    {"name": "pr/docs", "color": "3498db", "description": "Documentation updates or wiki improvements"},
    {"name": "pr/cleanup", "color": "7f8c8d", "description": "File, asset, or project structure cleanup"},
    {"name": "pr/meta", "color": "9b59b6", "description": "CI/CD, build system, release pipeline, or other meta changes"},
    {"name": "pr/ignore", "color": "000000", "description": "This PR will be excluded from the release changelog"},

    # --- Issue Labels ---
    {"name": "issue/bug", "color": "c0392b", "description": "Something is broken, malfunctioning, or causes errors"},
    {"name": "issue/feature-request", "color": "1abc9c", "description": "Suggestions for new features, mechanics, or assets"},
    {"name": "issue/docs", "color": "3498db", "description": "Documentation or wiki-related issues"},
    {"name": "issue/help-wanted", "color": "9b59b6", "description": "Community contributions or assistance requested"},
    {"name": "issue/blocked", "color": "7f8c8d", "description": "This issue is blocked by another issue or dependency"},
    {"name": "issue/meta", "color": "8e44ad", "description": "Meta-level issues, planning, or internal tasks"},
]

# Whitelisted labels that should never be deleted
WHITELIST_LABELS = [
    "Legacy"
]
