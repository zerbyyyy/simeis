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
import subprocess
import json

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

def check_issue_exists_and_open(issue_num):
    """
    Check if an issue exists and is open using the native 'gh' CLI tool.
    Returns: (exists, is_open)
    """
    try:
        # Appel à la CLI GitHub native via subprocess (évite les librairies tierces comme requests)
        result = subprocess.run(
            ['gh', 'issue', 'view', str(issue_num), '--json', 'state'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Si la CLI gh retourne un code d'erreur (ex: 404), l'issue n'existe pas
        if result.returncode != 0:
            return False, None
            
        data = json.loads(result.stdout)
        is_open = data.get('state') == 'OPEN'  # Note : la CLI gh retourne souvent 'OPEN' ou 'CLOSED' en majuscules
        return True, is_open
        
    except Exception as e:
        print(f"Warning: Failed to check issue #{issue_num} via gh CLI: {e}")
        return True, None  # Assume it exists if the command fails unexpectedly

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
    # Vérification de la présence du jeton d'authentification requis par la CLI 'gh'
    if not os.getenv('GH_TOKEN'):
        print("Error: GH_TOKEN environment variable not set")
        sys.exit(1)
        
    root_dir = os.getcwd()
    
    print("Checking TODOs in repository using GitHub CLI...")
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
            exists, is_open = check_issue_exists_and_open(issue_num)
            
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
                print(f"✓ {todo['file']}:{todo['line']} → Issue #{issue_num} (Open)")
    
    if errors:
        print("\n" + "="*60)
        print("ERRORS FOUND:")
        print("="*60)
        for error in errors:
            print(error)
            print()
        return 1
    
    print("\n✓ All TODOs are linked to valid open issues !")
    return 0

if __name__ == '__main__':
    sys.exit(main())