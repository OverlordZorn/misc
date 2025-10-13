# labels_data.py
"""
Label definitions for Arma 3 mod repositories.
This file acts as the "label database" imported by setup_labels.py
"""

LABELS = [
    """
    # --- PR Labels ---
    {"name": "pr/feature", "color": "2ecc71", "description": "New gameplay features, mechanics, or assets"},
    {"name": "pr/improvement", "color": "27ae60", "description": "Enhancements to existing functionality"},
    {"name": "pr/fix", "color": "e74c3c", "description": "Bug or issue fixes"},
    {"name": "pr/balance", "color": "f1c40f", "description": "Gameplay tuning or balance changes"},
    {"name": "pr/optimization", "color": "16a085", "description": "Performance improvements"},
    {"name": "pr/refactor", "color": "95a5a6", "description": "Internal refactoring, no gameplay change"},
    {"name": "pr/docs", "color": "3498db", "description": "Documentation or wiki updates"},
    {"name": "pr/cleanup", "color": "7f8c8d", "description": "File or asset cleanup, reorganization"},
    {"name": "pr/ci", "color": "9b59b6", "description": "CI/CD, build, or release pipeline changes"},

    # --- Issue Labels ---
    {"name": "issue/bug", "color": "c0392b", "description": "Something is broken or malfunctioning"},
    {"name": "issue/feature-request", "color": "1abc9c", "description": "Suggestion for a new feature"},
    {"name": "issue/improvement", "color": "2ecc71", "description": "Enhancement of an existing feature"},
    {"name": "issue/balance", "color": "f39c12", "description": "Gameplay balance or tuning issue"},
    {"name": "issue/question", "color": "2980b9", "description": "Question or clarification"},
    {"name": "issue/docs", "color": "3498db", "description": "Documentation or wiki-related issue"},
    {"name": "issue/help-wanted", "color": "9b59b6", "description": "Community contributions requested"},
    {"name": "issue/blocked", "color": "7f8c8d", "description": "Blocked by another issue or dependency"},
    {"name": "issue/meta", "color": "8e44ad", "description": "Meta-level issue or planning"},

    # --- Meta Labels ---
    {"name": "meta/ci", "color": "9b59b6", "description": "CI/CD or automation task"},
    {"name": "meta/release", "color": "8e44ad", "description": "Release management or changelog configuration"},
    {"name": "meta/docs", "color": "2980b9", "description": "Meta-level documentation (contributing, repo setup)"},
    {"name": "meta/config", "color": "34495e", "description": "Repository configuration or GitHub settings"},
    {"name": "meta/maintenance", "color": "7f8c8d", "description": "Repo maintenance or cleanup"},
    {"name": "meta/policy", "color": "16a085", "description": "Contribution guidelines or licensing"},
    {"name": "meta/discussion", "color": "95a5a6", "description": "General discussion or planning"},
    """
]

# Whitelisted labels that should never be deleted
WHITELIST_LABELS = [
    "Legacy"
]
