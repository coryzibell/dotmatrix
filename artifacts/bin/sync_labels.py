#!/usr/bin/env python3
"""
sync_labels.py - Synchronize all labels to GitHub repositories

Syncs:
- Identity labels from ~/.matrix/artifacts/etc/identity-colors.yaml
- Category labels from ~/.matrix/artifacts/etc/category-colors.yaml

Usage:
    python sync_labels.py <owner/repo>

Example:
    python sync_labels.py coryzibell/matrix
"""

import json
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Dict, Tuple, Optional, List

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


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
    print("Expected path: projects.<project>.mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN")
    sys.exit(1)


def parse_yaml_colors(yaml_file: Path) -> Dict[str, Tuple[str, str]]:
    """
    Parse identity colors from YAML file

    Returns:
        Dict mapping identity name to (hex_color, rationale) tuple
    """
    if HAS_YAML:
        # Use PyYAML if available
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
    else:
        # Simple parser for our specific YAML structure
        # Only handles the identities section with color/rationale pairs
        data = {'identities': {}}
        current_identity = None

        with open(yaml_file, 'r') as f:
            for line in f:
                line = line.rstrip()

                # Skip comments and empty lines
                if not line or line.lstrip().startswith('#'):
                    continue

                # Detect identity name (two-space indent)
                if line.startswith('  ') and not line.startswith('    ') and ':' in line:
                    current_identity = line.strip().rstrip(':')
                    data['identities'][current_identity] = {}

                # Detect color/rationale (four-space indent)
                elif current_identity and line.startswith('    ') and ':' in line:
                    key, _, value = line.strip().partition(':')
                    value = value.strip().strip('"')
                    data['identities'][current_identity][key] = value

    # Convert to expected format
    identities = {}
    for name, attrs in data.get('identities', {}).items():
        color = attrs.get('color', '').lstrip('#')
        rationale = attrs.get('rationale', '')
        if color:
            identities[name.lower()] = (color, rationale)

    return identities


def parse_markdown_colors(md_file: Path) -> Dict[str, Tuple[str, str]]:
    """
    Parse identity colors from markdown table (backwards compatibility)

    Returns:
        Dict mapping identity name to (hex_color, rationale) tuple
    """
    with open(md_file, 'r') as f:
        content = f.read()

    # Parse the markdown table
    # Format: | Identity | Hex Color | Rationale |
    identities = {}
    in_table = False

    for line in content.split('\n'):
        line = line.strip()

        # Start parsing after the table header separator (contains dashes and pipes)
        if '|' in line and all(c in '|-: \t' for c in line):
            in_table = True
            continue

        if in_table and line.startswith('|'):
            # Split by | and clean up whitespace
            parts = [p.strip() for p in line.split('|')]
            # Filter out empty strings from leading/trailing |
            parts = [p for p in parts if p]

            if len(parts) >= 3:
                identity = parts[0]
                hex_color = parts[1]
                rationale = parts[2]

                # Skip if not a valid row
                if not identity or not hex_color:
                    continue

                # Ensure hex color doesn't have # prefix
                hex_color = hex_color.lstrip('#')

                identities[identity.lower()] = (hex_color, rationale)

        # Stop parsing if we hit the ## Usage section or similar
        elif in_table and line.startswith('##'):
            break

    return identities


def parse_identity_colors() -> Dict[str, Tuple[str, str]]:
    """
    Parse identity colors from ~/.matrix/artifacts/etc/identity-colors.yaml
    Falls back to identity-colors.md if YAML not found.

    Returns:
        Dict mapping identity name to (hex_color, rationale) tuple
    """
    base_path = Path.home() / ".matrix" / "artifacts" / "etc"
    yaml_file = base_path / "identity-colors.yaml"
    md_file = base_path / "identity-colors.md"

    # Try YAML first
    if yaml_file.exists():
        try:
            return parse_yaml_colors(yaml_file)
        except Exception as e:
            print(f"Warning: Failed to parse YAML file: {e}")
            print(f"Falling back to markdown...")

    # Fall back to markdown
    if md_file.exists():
        return parse_markdown_colors(md_file)

    # Neither file found
    print(f"Error: Neither {yaml_file} nor {md_file} found")
    sys.exit(1)


def parse_category_colors() -> Dict[str, Tuple[str, str]]:
    """
    Parse category colors from ~/.matrix/artifacts/etc/category-colors.yaml

    Returns:
        Dict mapping label name to (hex_color, description) tuple
    """
    yaml_file = Path.home() / ".matrix" / "artifacts" / "etc" / "category-colors.yaml"

    if not yaml_file.exists():
        print(f"Warning: {yaml_file} not found, skipping category labels")
        return {}

    if not HAS_YAML:
        print(f"Warning: PyYAML not installed, skipping category labels")
        return {}

    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    labels = {}

    # Parse categories (no prefix)
    for name, attrs in data.get('categories', {}).items():
        color = attrs.get('color', '').lstrip('#')
        desc = attrs.get('description', '')
        if color:
            labels[name] = (color, desc)

    # Parse priorities (no prefix)
    for name, attrs in data.get('priorities', {}).items():
        color = attrs.get('color', '').lstrip('#')
        desc = attrs.get('description', '')
        if color:
            labels[name] = (color, desc)

    # Parse types (no prefix)
    for name, attrs in data.get('types', {}).items():
        color = attrs.get('color', '').lstrip('#')
        desc = attrs.get('description', '')
        if color:
            labels[name] = (color, desc)

    # Parse special labels (no prefix)
    for name, attrs in data.get('special', {}).items():
        color = attrs.get('color', '').lstrip('#')
        desc = attrs.get('description', '')
        if color:
            labels[name] = (color, desc)

    return labels


def make_github_request(url: str, token: str, method: str = "GET", data: Optional[bytes] = None) -> Dict:
    """Make an authenticated GitHub API request"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "claude-code-sync-labels"
    }

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error: HTTP {e.code} - {error_body}")
        raise


def list_labels(owner: str, repo: str, token: str) -> Dict[str, Dict]:
    """
    List existing labels in the repository (fetches ALL pages)

    Returns:
        Dict mapping label name to label data
    """
    all_labels = []
    page = 1

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/labels?per_page=100&page={page}"
        labels = make_github_request(url, token)

        if not labels:
            break

        all_labels.extend(labels)

        # If we got fewer than 100, we've reached the last page
        if len(labels) < 100:
            break

        page += 1

    return {label["name"]: label for label in all_labels}


def create_label(owner: str, repo: str, token: str, name: str, color: str, description: str, dry_run: bool = False) -> None:
    """Create a new label"""
    if dry_run:
        return

    url = f"https://api.github.com/repos/{owner}/{repo}/labels"
    data = json.dumps({
        "name": name,
        "color": color,
        "description": description
    }).encode()

    make_github_request(url, token, method="POST", data=data)


def update_label(owner: str, repo: str, token: str, name: str, color: str, description: str, dry_run: bool = False) -> None:
    """Update an existing label"""
    if dry_run:
        return

    # URL encode the label name for the path
    encoded_name = urllib.parse.quote(name, safe='')
    url = f"https://api.github.com/repos/{owner}/{repo}/labels/{encoded_name}"
    data = json.dumps({
        "color": color,
        "description": description
    }).encode()

    make_github_request(url, token, method="PATCH", data=data)


def sync_label_set(owner: str, repo: str, token: str, labels: Dict[str, Tuple[str, str]],
                   existing_labels: Dict[str, Dict], prefix: str = "", dry_run: bool = False) -> Tuple[list, list, list]:
    """
    Sync a set of labels to GitHub.

    Args:
        owner: Repo owner
        repo: Repo name
        token: GitHub token
        labels: Dict mapping name to (color, description)
        existing_labels: Already existing labels in repo
        prefix: Optional prefix for label names (e.g., "identity:")
        dry_run: Show what would happen without making changes

    Returns:
        Tuple of (created, updated, skipped) lists
    """
    created = []
    updated = []
    skipped = []

    for name, (color, description) in sorted(labels.items()):
        label_name = f"{prefix}{name}" if prefix else name
        description = description[:100]  # GitHub limit is 100 chars

        if label_name in existing_labels:
            existing = existing_labels[label_name]
            needs_update = (
                existing["color"].lower() != color.lower() or
                existing.get("description", "") != description
            )

            if needs_update:
                if dry_run:
                    print(f"  [DRY RUN] Would update: {label_name} (color: {color})")
                else:
                    print(f"  Updating: {label_name}")
                update_label(owner, repo, token, label_name, color, description, dry_run)
                updated.append(label_name)
            else:
                skipped.append(label_name)
        else:
            if dry_run:
                print(f"  [DRY RUN] Would create: {label_name} (color: {color})")
            else:
                print(f"  Creating: {label_name} ({color})")
            create_label(owner, repo, token, label_name, color, description, dry_run)
            created.append(label_name)

    return created, updated, skipped


def sync_labels(owner: str, repo: str, dry_run: bool = False) -> None:
    """Main synchronization logic"""
    if dry_run:
        print(f"[DRY RUN] Syncing labels to {owner}/{repo}")
    else:
        print(f"Syncing labels to {owner}/{repo}")
    print()

    # Read configuration
    token = read_github_token()
    identities = parse_identity_colors()
    categories = parse_category_colors()

    print(f"Found {len(identities)} identity labels")
    print(f"Found {len(categories)} category labels")

    # Fetch existing labels
    existing_labels = list_labels(owner, repo, token)
    print(f"Found {len(existing_labels)} existing labels in repository")
    print()

    # Track statistics
    all_created = []
    all_updated = []
    all_skipped = []

    # Sync identity labels (with prefix)
    print("Identity labels:")
    created, updated, skipped = sync_label_set(
        owner, repo, token, identities, existing_labels, prefix="identity:", dry_run=dry_run
    )
    all_created.extend(created)
    all_updated.extend(updated)
    all_skipped.extend(skipped)
    print()

    # Sync category labels (no prefix)
    print("Category labels:")
    created, updated, skipped = sync_label_set(
        owner, repo, token, categories, existing_labels, prefix="", dry_run=dry_run
    )
    all_created.extend(created)
    all_updated.extend(updated)
    all_skipped.extend(skipped)
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Created: {len(all_created)}")
    print(f"Updated: {len(all_updated)}")
    print(f"Skipped: {len(all_skipped)} (already correct)")
    print()

    if all_created:
        print("Created labels:")
        for label in all_created:
            print(f"  - {label}")
        print()

    if all_updated:
        print("Updated labels:")
        for label in all_updated:
            print(f"  - {label}")
        print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Synchronize labels to GitHub repositories")
    parser.add_argument("repo", help="Repository in format 'owner/repo'")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making changes")
    args = parser.parse_args()

    if "/" not in args.repo:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)

    owner, repo = args.repo.split("/", 1)

    try:
        sync_labels(owner, repo, dry_run=args.dry_run)
    except urllib.error.HTTPError as e:
        print(f"\nFailed with HTTP error {e.code}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
