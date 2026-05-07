#!/usr/bin/env python3
"""
Script pour créer les issues GitHub manquantes pour les TODOs.
Exécutez ce script après avoir authentifié GitHub CLI:
  gh auth login
  python create_missing_issues.py
"""

import subprocess
import sys

# Issues manquantes à créer
ISSUES_TO_CREATE = {
    33: {
        "title": "SDK: Implement Unload, Unload_all, get_syslogs, resources, wages",
        "body": "Implement missing SDK methods:\n- Unload\n- Unload_all\n- get_syslogs\n- Add resources info\n- Get ship wages cost\n- Industry methods",
        "labels": "enhancement,sdk"
    },
    34: {
        "title": "Reduce stack size from async task",
        "body": "Reduce the stack size allocated for the async task in main.rs (currently > 1024)",
        "labels": "optimization,performance"
    },
    35: {
        "title": "Implement POST body for complex API requests",
        "body": "Pass complex requests via POST body instead of URL parameters",
        "labels": "api,enhancement"
    },
    36: {
        "title": "Add endpoints for all information types",
        "body": "Create comprehensive endpoints for all kinds of information",
        "labels": "api,enhancement"
    },
    37: {
        "title": "Document API greatly",
        "body": "Comprehensive API documentation and usage examples",
        "labels": "documentation"
    },
    31: {
        "title": "Optimize Galaxy data structure with RwLock",
        "body": "Use RwLock on each field instead of single lock, index discovered by sector ID in BTreeMap",
        "labels": "optimization,refactor"
    },
    25: {
        "title": "Remove solid field and implement condition-based behavior",
        "body": "Remove 'solid' field from Planet and make behavior depend on conditions, temperature, etc.",
        "labels": "refactor"
    }
}

def create_issue(number, title, body, labels):
    """Create a GitHub issue using gh CLI."""
    try:
        cmd = [
            "gh", "issue", "create",
            "--title", title,
            "--body", body,
            "--label", labels
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ Issue #{number} created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create issue #{number}")
        print(f"  {e.stderr}")
        return False

def main():
    """Create all missing issues."""
    print("Creating missing GitHub issues...")
    print("=" * 60)
    
    if not sys.argv[1:]:
        print("\nUsage: gh auth login && python create_missing_issues.py")
        print("\nIssues to create:")
        for num, info in sorted(ISSUES_TO_CREATE.items()):
            print(f"  #{num}: {info['title']}")
        print("\nNote: Issues will be created in order #25, #31, #33, #34, #35, #36, #37")
        return 0
    
    created = 0
    for number in sorted(ISSUES_TO_CREATE.keys()):
        info = ISSUES_TO_CREATE[number]
        if create_issue(number, info["title"], info["body"], info["labels"]):
            created += 1
    
    print("=" * 60)
    print(f"Created {created}/{len(ISSUES_TO_CREATE)} issues")
    return 0 if created == len(ISSUES_TO_CREATE) else 1

if __name__ == "__main__":
    sys.exit(main())
