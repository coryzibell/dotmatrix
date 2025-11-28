#!/usr/bin/env python3
"""
dotmatrix environment health check.
Verifies required files, directories, and configuration for Claude identities.
"""

import os
import sys
from pathlib import Path


# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

    @staticmethod
    def is_tty():
        return sys.stdout.isatty()

    @classmethod
    def ok(cls):
        return f"{cls.GREEN}[OK]{cls.RESET}" if cls.is_tty() else "[OK]"

    @classmethod
    def fail(cls):
        return f"{cls.RED}[FAIL]{cls.RESET}" if cls.is_tty() else "[FAIL]"


def check_file(path: Path, description: str) -> bool:
    """Check if file exists and is readable."""
    if path.is_file():
        print(f"{Colors.ok()} {description}")
        return True
    else:
        print(f"{Colors.fail()} {description} (not found: {path})")
        return False


def check_dir(path: Path, description: str) -> bool:
    """Check if directory exists."""
    if path.is_dir():
        print(f"{Colors.ok()} {description}")
        return True
    else:
        print(f"{Colors.fail()} {description} (not found: {path})")
        return False


def check_github_token() -> bool:
    """Check GitHub token environment variable."""
    token = os.getenv('GITHUB_TOKEN')

    if not token:
        print(f"{Colors.fail()} GitHub token (GITHUB_TOKEN not set)")
        return False

    # Validate format
    if not (token.startswith('ghp_') or token.startswith('github_pat_')):
        print(f"{Colors.fail()} GitHub token (invalid format)")
        return False

    print(f"{Colors.ok()} GitHub token")
    return True


def main():
    """Run all health checks."""
    print("Checking dotmatrix environment...\n")

    home = Path.home()
    claude_dir = home / '.claude'

    all_passed = True

    # Required agent files
    all_passed &= check_file(
        claude_dir / 'agents' / 'neo.md',
        'agents/neo.md'
    )
    all_passed &= check_file(
        claude_dir / 'agents' / '_base.md',
        'agents/_base.md'
    )

    # Core configuration files
    all_passed &= check_file(
        claude_dir / 'orchestration.md',
        'orchestration.md'
    )
    all_passed &= check_file(
        claude_dir / 'paths.md',
        'paths.md'
    )
    all_passed &= check_file(
        claude_dir / 'CLAUDE.md',
        'CLAUDE.md'
    )

    # Artifact files
    all_passed &= check_file(
        claude_dir / 'artifacts' / 'etc' / 'identity-colors.yaml',
        'artifacts/etc/identity-colors.yaml'
    )
    all_passed &= check_file(
        claude_dir / 'artifacts' / 'etc' / 'category-colors.yaml',
        'artifacts/etc/category-colors.yaml'
    )

    # RAM directories
    all_passed &= check_dir(
        claude_dir / 'ram' / 'neo',
        'ram/neo/'
    )

    # Symlink integrity
    agents_path = claude_dir / 'agents'
    if agents_path.is_dir():
        print(f"{Colors.ok()} agents/ directory")
    else:
        print(f"{Colors.fail()} agents/ directory (not found or not a directory)")
        all_passed = False

    # GitHub token
    all_passed &= check_github_token()

    # Summary
    print()
    if all_passed:
        print("All checks passed. System ready.")
        return 0
    else:
        print("System has issues. Fix before running workflows.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
