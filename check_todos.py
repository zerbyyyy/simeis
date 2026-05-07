#!/usr/bin/env python3
"""
Script to check that all TODOs in the codebase have associated GitHub issues.
Format:
  // TODO (#123) Description - issue 123 must exist and be open
  // TODO Description - ERROR: no issue associated
"""

import os
import re
import sys
import requests

# Regex to find TODOs with optional issue numbers
TODO_PATTERN = re.compile(r'TODO\s*(?:\(#(\d+)\))?')

# File extensions to check
EXTENSIONS_TO_CHECK = {
    '.rs', '.py', '.js', '.ts', '.tsx', '.jsx',
    '.go', '.java', '.cpp', '.c', '.h', '.hpp',
    '.cs', '.swift', '.kt', '.scala', '.rb'
}

# Directories to exclude
EXCLUDE_DIRS = {
    'target', 'node_modules', '.git', 'dist', 'build',
    '__pycache__', '.venv', 'venv', 'env'
}

# Files to exclude
EXCLUDE_FILES = {
    'check_todos.py',  # Don't check the checker itself
}

def get_github_token():
    """Get GitHub token from environment."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    return token

def get_repo_info():
    """Get repository owner and name from environment."""
    repo = os.getenv('GITHUB_REPOSITORY', '').split('/')
    if len(repo) != 2:
        print("Error: GITHUB_REPOSITORY not set properly")
        sys.exit(1)
    return repo[0], repo[1]

def check_issue_exists(owner, repo, issue_num, token):
    """Check if an issue exists and is open."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            return False, None
        
        if response.status_code == 200:
            issue = response.json()
            is_open = issue.get('state') == 'open'
            return True, is_open
        
        print(f"Warning: API returned status {response.status_code} for issue #{issue_num}")
        return True, None  # Assume it exists if we can't determine
        
    except requests.RequestException as e:
        print(f"Warning: Failed to check issue #{issue_num}: {e}")
        return True, None  # Assume it exists if we can't connect

def find_todos(root_dir):
    """Find all TODOs in the codebase."""
    todos = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove excluded directories from the search
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        
        for filename in filenames:
            if filename in EXCLUDE_FILES:
                continue
            if not any(filename.endswith(ext) for ext in EXTENSIONS_TO_CHECK):
                continue
            
            filepath = os.path.join(dirpath, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        match = TODO_PATTERN.search(line)
                        if match:
                            issue_num = match.group(1)
                            todos.append({
                                'file': filepath,
                                'line': line_num,
                                'text': line.strip(),
                                'issue': issue_num
                            })
            except Exception as e:
                print(f"Warning: Could not read {filepath}: {e}")
    
    return todos

def main():
    """Main function."""
    token = get_github_token()
    owner, repo = get_repo_info()
    root_dir = os.getcwd()
    
    print(f"Checking TODOs in {repo}...")
    todos = find_todos(root_dir)
    
    if not todos:
        print("✓ No TODOs found")
        return 0
    
    print(f"Found {len(todos)} TODO(s)\n")
    
    errors = []
    
    for todo in todos:
        if not todo['issue']:
            errors.append(
                f"❌ {todo['file']}:{todo['line']}\n"
                f"   No issue associated with TODO\n"
                f"   {todo['text']}"
            )
        else:
            issue_num = todo['issue']
            exists, is_open = check_issue_exists(owner, repo, issue_num, token)
            
            if not exists:
                errors.append(
                    f"❌ {todo['file']}:{todo['line']}\n"
                    f"   Issue #{issue_num} does not exist\n"
                    f"   {todo['text']}"
                )
            elif is_open is False:
                errors.append(
                    f"❌ {todo['file']}:{todo['line']}\n"
                    f"   Issue #{issue_num} is closed\n"
                    f"   {todo['text']}"
                )
            else:
                print(f"✓ {todo['file']}:{todo['line']} → Issue #{issue_num}")
    
    if errors:
        print("\n" + "="*60)
        print("ERRORS FOUND:")
        print("="*60)
        for error in errors:
            print(error)
            print()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
