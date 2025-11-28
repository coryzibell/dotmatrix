#!/usr/bin/env python3
"""
sync_wiki.py - Sync markdown documentation to GitHub wiki

Clones the wiki repo, copies/updates markdown files, commits and pushes.

Usage:
    python sync_wiki.py <owner/repo> <source-dir> [--page-name NAME]
    python sync_wiki.py <owner/repo> <source-file> --page-name NAME

Examples:
    # Sync all .md files from a directory
    python sync_wiki.py coryzibell/matrix ~/.matrix/cache/construct/matrix/

    # Sync a single file as a specific wiki page
    python sync_wiki.py coryzibell/matrix ./report.md --page-name "Construct-Report"

    # Sync synthesis.md as the construct report
    python sync_wiki.py Veoci-Labs/veoci-app-template-construct ./synthesis.md --page-name "Construct-Report"
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


def read_github_token() -> str:
    """Read GitHub token from ~/.claude.json"""
    claude_config = Path.home() / ".claude.json"

    if not claude_config.exists():
        print(f"Error: {claude_config} not found")
        sys.exit(1)

    with open(claude_config, 'r') as f:
        config = json.load(f)

    # Navigate through the projects structure to find the GitHub token
    projects = config.get("projects", {})
    for project_path, project_config in projects.items():
        mcp_servers = project_config.get("mcpServers", {})
        if "github" in mcp_servers:
            token = mcp_servers["github"].get("env", {}).get("GITHUB_PERSONAL_ACCESS_TOKEN")
            if token:
                return token

    print("Error: GitHub token not found in ~/.claude.json")
    sys.exit(1)


def run_git(args: list, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command"""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    if check and result.returncode != 0:
        print(f"Git error: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
    return result


def clone_wiki(owner: str, repo: str, token: str, target_dir: Path) -> bool:
    """Clone the wiki repository"""
    wiki_url = f"https://{token}@github.com/{owner}/{repo}.wiki.git"

    print(f"Cloning wiki from {owner}/{repo}...")

    result = subprocess.run(
        ["git", "clone", "--depth", "1", wiki_url, str(target_dir)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        if "not found" in result.stderr.lower() or "does not exist" in result.stderr.lower():
            print("Error: Wiki repository not found.")
            print("Make sure:")
            print("  1. Wiki is enabled in repo settings")
            print("  2. At least one wiki page exists (create via GitHub UI)")
            return False
        print(f"Clone error: {result.stderr}")
        return False

    return True


def sanitize_page_name(name: str) -> str:
    """Convert a name to valid wiki page filename"""
    # GitHub wiki uses filenames as page names
    # Spaces become hyphens, special chars removed
    name = name.replace(" ", "-")
    # Remove .md extension if present (we'll add it back)
    if name.endswith(".md"):
        name = name[:-3]
    # Keep only alphanumeric, hyphens, underscores
    sanitized = "".join(c for c in name if c.isalnum() or c in "-_")
    return sanitized


def sync_file(source: Path, wiki_dir: Path, page_name: Optional[str] = None) -> str:
    """Copy a single file to the wiki directory"""
    if page_name:
        dest_name = sanitize_page_name(page_name) + ".md"
    else:
        dest_name = source.name

    dest = wiki_dir / dest_name
    shutil.copy(source, dest)
    return dest_name


def sync_directory(source_dir: Path, wiki_dir: Path, pattern: str = "*.md") -> list:
    """Copy all matching files from source to wiki directory"""
    synced = []
    for md_file in source_dir.glob(pattern):
        # Skip files that start with numbers (like 001-blocker-...)
        # These are issue files, not wiki content
        if md_file.stem[0].isdigit():
            continue
        dest = wiki_dir / md_file.name
        shutil.copy(md_file, dest)
        synced.append(md_file.name)
    return synced


def commit_and_push(wiki_dir: Path, message: str, dry_run: bool = False) -> bool:
    """Commit changes and push to remote"""
    # Configure git user for this repo
    if not dry_run:
        run_git(["config", "user.email", "neo@construct.local"], wiki_dir, check=False)
        run_git(["config", "user.name", "Neo (Construct)"], wiki_dir, check=False)

    # Add all changes (check status either way)
    if not dry_run:
        run_git(["add", "-A"], wiki_dir)

    # Check if there are changes to commit
    result = run_git(["status", "--porcelain"], wiki_dir)
    if not result.stdout.strip():
        print("No changes to commit")
        return True

    if dry_run:
        print(f"[DRY RUN] Would commit: {message}")
        print(f"[DRY RUN] Would push to wiki")
        print(f"[DRY RUN] Files that would be committed:")
        for line in result.stdout.strip().split('\n'):
            print(f"  {line}")
    else:
        # Commit
        print(f"Committing: {message}")
        run_git(["commit", "-m", message], wiki_dir)

        # Push
        print("Pushing to wiki...")
        run_git(["push"], wiki_dir)

    return True


def sync_wiki(owner: str, repo: str, source: Path, page_name: Optional[str] = None, dry_run: bool = False) -> bool:
    """Main sync function"""
    token = read_github_token()

    # Create temp directory for wiki clone
    with tempfile.TemporaryDirectory() as tmp:
        wiki_dir = Path(tmp) / "wiki"

        # Clone wiki
        if dry_run:
            print(f"[DRY RUN] Would clone wiki from {owner}/{repo}")
        if not clone_wiki(owner, repo, token, wiki_dir):
            return False

        # Sync files
        if source.is_file():
            if not page_name:
                page_name = source.stem
            if dry_run:
                dest_name = sanitize_page_name(page_name) + ".md"
                print(f"[DRY RUN] Would sync: {source.name} → {dest_name}")
            synced = sync_file(source, wiki_dir, page_name)
            if not dry_run:
                print(f"Synced: {source.name} → {synced}")
            commit_msg = f"Update {synced}"
        elif source.is_dir():
            if dry_run:
                print(f"[DRY RUN] Would sync all .md files from {source}")
            synced = sync_directory(source, wiki_dir)
            if not synced:
                print("No markdown files found to sync")
                return True
            if dry_run:
                print(f"[DRY RUN] Would sync {len(synced)} files:")
            else:
                print(f"Synced {len(synced)} files:")
            for f in synced:
                if dry_run:
                    print(f"  - [DRY RUN] {f}")
                else:
                    print(f"  - {f}")
            commit_msg = f"Sync {len(synced)} documentation files"
        else:
            print(f"Error: {source} is not a file or directory")
            return False

        # Commit and push
        if not commit_and_push(wiki_dir, commit_msg, dry_run):
            return False

        print()
        if dry_run:
            print(f"[DRY RUN] Would update wiki: https://github.com/{owner}/{repo}/wiki")
        else:
            print(f"✓ Wiki updated: https://github.com/{owner}/{repo}/wiki")
        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sync markdown documentation to GitHub wiki")
    parser.add_argument("repo", help="Repository in format 'owner/repo'")
    parser.add_argument("source", help="File or directory to sync")
    parser.add_argument("--page-name", help="Wiki page name (for single file sync)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making changes")
    args = parser.parse_args()

    if "/" not in args.repo:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)

    owner, repo = args.repo.split("/", 1)
    source = Path(args.source).expanduser().resolve()

    if not source.exists():
        print(f"Error: {source} does not exist")
        sys.exit(1)

    try:
        success = sync_wiki(owner, repo, source, args.page_name, dry_run=args.dry_run)
        sys.exit(0 if success else 1)
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
