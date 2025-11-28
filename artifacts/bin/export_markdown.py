#!/usr/bin/env python3
"""
Convert YAML issue/discussion files to readable Markdown.

Usage:
    python export_markdown.py <yaml-dir> [output-dir]
    python export_markdown.py ~/.matrix/cache/construct/matrix/issues/ ./docs/issues/
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


def parse_date(date_str: str) -> str:
    """Format ISO8601 date string to readable format."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except Exception:
        return date_str


def extract_repo_info(data: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    """Extract owner and repo from YAML data."""
    # Hardcoded default for matrix project
    default_owner = "coryzibell"
    default_repo = "matrix"

    # Try to find in various possible locations
    if 'repository' in data:
        repo = data['repository']
        if isinstance(repo, dict):
            return repo.get('owner'), repo.get('name')
        elif isinstance(repo, str) and '/' in repo:
            owner, name = repo.split('/', 1)
            return owner, name

    # Try repository_url
    if 'repository_url' in data:
        url = data['repository_url']
        parts = url.rstrip('/').split('/')
        if len(parts) >= 2:
            return parts[-2], parts[-1]

    # Try html_url
    if 'html_url' in data:
        url = data['html_url']
        parts = url.rstrip('/').split('/')
        if len(parts) >= 4:
            return parts[-4], parts[-3]

    # Fall back to hardcoded default
    return default_owner, default_repo


def build_github_url(data: Dict[str, Any], owner: Optional[str], repo: Optional[str]) -> Optional[str]:
    """Build GitHub URL for issue or discussion."""
    # First try direct html_url in metadata
    metadata = data.get('metadata', {})
    if 'html_url' in metadata:
        return metadata['html_url']

    # Then try top-level html_url
    if 'html_url' in data:
        return data['html_url']

    if not owner or not repo:
        return None

    # Try to get number from metadata first, then fall back to top level
    number = metadata.get('github_issue_number') or metadata.get('github_discussion_number') or data.get('number')
    if not number:
        return None

    # Determine type from metadata or top level
    item_type = metadata.get('type') or data.get('type', 'issue')
    item_type = str(item_type).lower()

    if 'discussion' in item_type or 'github_discussion_number' in metadata:
        return f"https://github.com/{owner}/{repo}/discussions/{number}"
    else:
        return f"https://github.com/{owner}/{repo}/issues/{number}"


def convert_yaml_to_markdown(yaml_path: Path, output_path: Path) -> None:
    """Convert a single YAML file to Markdown."""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if not data:
        print(f"  ⚠️  Skipping {yaml_path.name}: empty file")
        return

    # Extract metadata from nested structure
    metadata = data.get('metadata', {})

    title = metadata.get('title', data.get('title', 'Untitled'))
    item_type = metadata.get('type', data.get('type', 'issue'))
    labels = metadata.get('labels', data.get('labels', []))
    state = metadata.get('state', data.get('state', 'unknown'))

    # Number can be issue or discussion number
    number = metadata.get('github_issue_number') or metadata.get('github_discussion_number') or data.get('number', '?')

    # Body is at top level as body_markdown
    body = data.get('body_markdown', data.get('body', ''))

    # Comments remain at top level
    comments = data.get('comments', [])

    # Updated timestamp from metadata
    updated_at = metadata.get('github_updated_at', data.get('updated_at', data.get('github_updated_at', '')))

    # Extract repo info and build URL
    owner, repo = extract_repo_info(data)
    github_url = build_github_url(data, owner, repo)

    # Build markdown
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**Type:** `{item_type}`")

    if labels:
        if isinstance(labels, list):
            labels_str = ', '.join(f"`{label}`" for label in labels)
        else:
            labels_str = f"`{labels}`"
        lines.append(f"**Labels:** {labels_str}")

    lines.append(f"**Status:** {state}")

    if github_url:
        lines.append(f"**GitHub:** [#{number}]({github_url})")
    else:
        lines.append(f"**Number:** #{number}")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Add body
    if body:
        lines.append(body.rstrip())
        lines.append("")

    # Add comments if present
    if comments:
        lines.append("---")
        lines.append("")
        lines.append("## Comments")
        lines.append("")

        for comment in comments:
            author = comment.get('author', comment.get('user', 'unknown'))
            created = comment.get('created_at', '')
            comment_body = comment.get('body', '')

            formatted_date = parse_date(created) if created else 'unknown date'

            lines.append(f"### @{author} - {formatted_date}")
            lines.append("")
            if comment_body:
                lines.append(comment_body.rstrip())
                lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    if updated_at:
        formatted_updated = parse_date(updated_at)
        lines.append(f"*Last synced: {formatted_updated}*")
    else:
        lines.append("*Last synced: unknown*")

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python export_markdown.py <yaml-dir> [output-dir]")
        print("\nExample:")
        print("  python export_markdown.py ~/.matrix/cache/construct/matrix/issues/ ./docs/issues/")
        sys.exit(1)

    yaml_dir = Path(sys.argv[1]).expanduser()

    if not yaml_dir.exists():
        print(f"Error: Directory not found: {yaml_dir}")
        sys.exit(1)

    if not yaml_dir.is_dir():
        print(f"Error: Not a directory: {yaml_dir}")
        sys.exit(1)

    # Determine output directory
    if len(sys.argv) >= 3:
        output_dir = Path(sys.argv[2]).expanduser()
    else:
        output_dir = yaml_dir

    print(f"Exporting to {output_dir}...\n")

    # Find all YAML files
    yaml_files = sorted(yaml_dir.glob('*.yaml')) + sorted(yaml_dir.glob('*.yml'))

    if not yaml_files:
        print(f"No YAML files found in {yaml_dir}")
        sys.exit(0)

    exported_count = 0
    for yaml_file in yaml_files:
        # Generate output filename
        md_filename = yaml_file.stem + '.md'
        output_path = output_dir / md_filename

        try:
            convert_yaml_to_markdown(yaml_file, output_path)
            print(f"  {yaml_file.name} → {md_filename}")
            exported_count += 1
        except Exception as e:
            print(f"  ❌ {yaml_file.name}: {e}")

    print(f"\nExported {exported_count} file{'s' if exported_count != 1 else ''}.")


if __name__ == '__main__':
    main()
