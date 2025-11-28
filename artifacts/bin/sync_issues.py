#!/usr/bin/env python3
"""
sync_issues.py - Synchronize issue YAML files to GitHub

Reads issue YAML files, compares with GitHub issues field by field, and updates
only changed fields. Uses three-way merge logic to detect and resolve conflicts
between local, remote, and last-synced states.

Usage:
    python sync_issues.py <owner/repo> <issues-dir>

Example:
    python sync_issues.py coryzibell/matrix ~/.matrix/cache/construct/matrix/issues/
"""

import json
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime

# Import three-way merge utilities
import sync_merge

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


def parse_yaml_file(yaml_file: Path) -> Dict:
    """
    Parse issue YAML file

    Returns:
        Dict containing issue data, or None if parse fails
    """
    if not HAS_YAML:
        print(f"Error: PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)

    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)


def write_yaml_file(yaml_file: Path, data: Dict) -> None:
    """Write issue data back to YAML file"""
    if not HAS_YAML:
        print(f"Error: PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)

    with open(yaml_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def make_github_request(url: str, token: str, method: str = "GET", data: Optional[bytes] = None) -> Dict:
    """Make an authenticated GitHub API request"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "claude-code-sync-issues"
    }

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error: HTTP {e.code} - {error_body}")
        raise


def list_issues(owner: str, repo: str, token: str, state: str = "all") -> List[Dict]:
    """
    List all issues in the repository (fetches ALL pages)

    Returns:
        List of issue dictionaries
    """
    all_issues = []
    page = 1

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues?state={state}&per_page=100&page={page}"
        issues = make_github_request(url, token)

        if not issues:
            break

        all_issues.extend(issues)

        # If we got fewer than 100, we've reached the last page
        if len(issues) < 100:
            break

        page += 1

    return all_issues


def create_issue(owner: str, repo: str, token: str, title: str, body: str, labels: List[str], assignees: List[str]) -> Dict:
    """Create a new issue"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    data = json.dumps({
        "title": title,
        "body": body,
        "labels": labels,
        "assignees": assignees
    }).encode()

    return make_github_request(url, token, method="POST", data=data)


def update_issue(owner: str, repo: str, token: str, issue_number: int, title: str, body: str, labels: List[str], assignees: List[str]) -> Dict:
    """Update an existing issue"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    data = json.dumps({
        "title": title,
        "body": body,
        "labels": labels,
        "assignees": assignees
    }).encode()

    return make_github_request(url, token, method="PATCH", data=data)


def parse_github_timestamp(timestamp_str: str) -> datetime:
    """Parse GitHub ISO 8601 timestamp"""
    # GitHub returns timestamps like: "2024-01-15T10:30:45Z"
    return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")


def get_file_modified_time(file_path: Path) -> datetime:
    """Get file modification time as datetime"""
    return datetime.fromtimestamp(file_path.stat().st_mtime)


def find_issue_by_title(issues: List[Dict], title: str) -> Optional[Dict]:
    """Find an issue by exact title match"""
    for issue in issues:
        # Skip pull requests (they show up in issues endpoint)
        if "pull_request" in issue:
            continue
        if issue["title"] == title:
            return issue
    return None


def find_issue_by_number(issues: List[Dict], number: int) -> Optional[Dict]:
    """Find an issue by number"""
    for issue in issues:
        # Skip pull requests
        if "pull_request" in issue:
            continue
        if issue["number"] == number:
            return issue
    return None


def is_idea(yaml_data: Dict) -> bool:
    """
    Check if YAML represents an idea rather than an issue

    Returns:
        True if type is "idea", False otherwise
    """
    metadata = yaml_data.get("metadata", {})
    return metadata.get("type") == "idea"


def extract_issue_data(yaml_data: Dict) -> Tuple[str, str, List[str], List[str], Optional[int]]:
    """
    Extract issue fields from YAML data

    Returns:
        (title, body, labels, assignees, github_issue_number)
    """
    metadata = yaml_data.get("metadata", {})

    title = metadata.get("title", "Untitled Issue")
    body = yaml_data.get("body_markdown", "")
    labels = metadata.get("labels", [])
    assignees = metadata.get("assignees", [])
    github_issue_number = metadata.get("github_issue_number")

    return title, body, labels, assignees, github_issue_number


def get_last_synced(yaml_data: Dict) -> Optional[Dict]:
    """
    Get last_synced snapshot from YAML metadata.

    Returns:
        Dict with last synced field values, or None if not present
    """
    metadata = yaml_data.get("metadata", {})
    return metadata.get("last_synced")


def save_last_synced(yaml_file: Path, yaml_data: Dict, title: str, body: str,
                     labels: List[str], assignees: List[str], updated_at: str) -> None:
    """
    Update last_synced snapshot in YAML file.

    Args:
        yaml_file: Path to YAML file
        yaml_data: Current YAML data dict
        title: Synced title
        body: Synced body
        labels: Synced labels
        assignees: Synced assignees
        updated_at: GitHub updated_at timestamp
    """
    if "metadata" not in yaml_data:
        yaml_data["metadata"] = {}

    yaml_data["metadata"]["last_synced"] = sync_merge.create_snapshot(
        title, body, labels, updated_at, assignees
    )

    write_yaml_file(yaml_file, yaml_data)


def sync_issues(owner: str, repo: str, issues_dir: Path) -> None:
    """Main synchronization logic"""
    print(f"Syncing issues to {owner}/{repo}")
    print(f"From directory: {issues_dir}")
    print()

    # Validate directory
    if not issues_dir.exists():
        print(f"Error: Directory does not exist: {issues_dir}")
        sys.exit(1)

    if not issues_dir.is_dir():
        print(f"Error: Not a directory: {issues_dir}")
        sys.exit(1)

    # Read configuration
    token = read_github_token()

    # Find all YAML files
    yaml_files = list(issues_dir.glob("*.yaml")) + list(issues_dir.glob("*.yml"))

    if not yaml_files:
        print(f"No YAML files found in {issues_dir}")
        sys.exit(0)

    print(f"Found {len(yaml_files)} YAML files")

    # Fetch existing issues (all states)
    print("Fetching existing issues from GitHub...")
    existing_issues = list_issues(owner, repo, token, state="all")
    print(f"Found {len(existing_issues)} existing issues in repository")
    print()

    # Track statistics
    created = []
    updated = []
    skipped_unchanged = []
    skipped_ideas = []
    errors = []

    # Process each YAML file
    for yaml_file in sorted(yaml_files):
        print(f"Processing: {yaml_file.name}")

        try:
            # Parse YAML
            yaml_data = parse_yaml_file(yaml_file)

            # Skip ideas
            if is_idea(yaml_data):
                metadata = yaml_data.get("metadata", {})
                title = metadata.get("title", "Untitled")
                print(f"  Skipping (type: idea): {title}")
                skipped_ideas.append((yaml_file.name, title))
                continue

            # Extract issue data
            title, body, labels, assignees, github_issue_number = extract_issue_data(yaml_data)

            # Find matching GitHub issue
            github_issue = None
            if github_issue_number:
                # Try by number first (most reliable)
                github_issue = find_issue_by_number(existing_issues, github_issue_number)

            if not github_issue:
                # Fall back to title match
                github_issue = find_issue_by_title(existing_issues, title)

            if not github_issue:
                # Create new issue
                print(f"  Creating new issue: {title}")
                result = create_issue(owner, repo, token, title, body, labels, assignees)

                # Update YAML with GitHub issue number and snapshot
                if "metadata" not in yaml_data:
                    yaml_data["metadata"] = {}
                yaml_data["metadata"]["github_issue_number"] = result["number"]

                # Save snapshot
                save_last_synced(
                    yaml_file, yaml_data,
                    result["title"], result["body"],
                    [label["name"] for label in result.get("labels", [])],
                    [assignee["login"] for assignee in result.get("assignees", [])],
                    result["updated_at"]
                )

                print(f"  Created issue #{result['number']}")
                created.append((yaml_file.name, result["number"], title))
            else:
                # Issue exists - three-way merge
                github_labels = [label["name"] for label in github_issue.get("labels", [])]
                github_assignees = [assignee["login"] for assignee in github_issue.get("assignees", [])]

                # Get base snapshot
                base = get_last_synced(yaml_data)
                if base is None:
                    # First sync after this change - treat remote as base
                    base = {
                        'title': github_issue["title"],
                        'body': github_issue["body"] or "",
                        'labels': github_labels,
                        'assignees': github_assignees
                    }

                # Build local/remote state dicts
                local = {
                    'title': title,
                    'body': body,
                    'labels': labels,
                    'assignees': assignees
                }
                remote = {
                    'title': github_issue["title"],
                    'body': github_issue["body"] or "",
                    'labels': github_labels,
                    'assignees': github_assignees
                }

                # Quick check: any differences?
                if not sync_merge.should_update(local, remote, base, ['title', 'body', 'labels', 'assignees']):
                    # No changes needed
                    skipped_unchanged.append((yaml_file.name, github_issue["number"], title))

                    # Ensure github_issue_number is tracked
                    if "metadata" not in yaml_data:
                        yaml_data["metadata"] = {}
                    if "github_issue_number" not in yaml_data["metadata"]:
                        yaml_data["metadata"]["github_issue_number"] = github_issue["number"]
                        write_yaml_file(yaml_file, yaml_data)
                else:
                    # Compute changes
                    changes = sync_merge.compute_field_changes(
                        local, remote, base,
                        ['title', 'body', 'labels', 'assignees']
                    )

                    # Special handling for labels: use merge logic
                    if 'labels' in changes:
                        change_type, local_labels, remote_labels, base_labels = changes['labels']
                        if change_type in ['local_only', 'remote_only', 'both_same']:
                            # Standard handling
                            pass
                        elif change_type == 'conflict':
                            # Use label merge logic
                            merged_labels = sync_merge.merge_labels(local_labels, remote_labels, base_labels)
                            # Override: treat as resolved
                            changes['labels'] = ('both_same', merged_labels, merged_labels, base_labels)

                    # Resolve conflicts
                    resolutions = {}
                    merged, should_skip = sync_merge.merge_fields(changes, resolutions, interactive=True)

                    if should_skip:
                        print(f"  Skipping (user requested): {title}")
                        print()
                        continue

                    # Print summary
                    special_handling = {}
                    if 'labels' in changes and changes['labels'][0] in ['conflict', 'both_same']:
                        # Check if we merged labels
                        if len(changes['labels'][1]) > 0 or len(changes['labels'][2]) > 0:
                            special_handling['labels'] = "Merged (union of additions)"

                    sync_merge.print_sync_summary(title, changes, resolutions, special_handling)

                    # Update GitHub with merged values
                    print(f"  Updating issue #{github_issue['number']}...")
                    result = update_issue(
                        owner, repo, token,
                        github_issue["number"],
                        merged['title'], merged['body'],
                        merged['labels'], merged['assignees']
                    )

                    # Ensure github_issue_number is tracked
                    if "metadata" not in yaml_data:
                        yaml_data["metadata"] = {}
                    if "github_issue_number" not in yaml_data["metadata"]:
                        yaml_data["metadata"]["github_issue_number"] = github_issue["number"]

                    # Save snapshot
                    save_last_synced(
                        yaml_file, yaml_data,
                        result["title"], result["body"],
                        [label["name"] for label in result.get("labels", [])],
                        [assignee["login"] for assignee in result.get("assignees", [])],
                        result["updated_at"]
                    )

                    print(f"  Done. Updated last_synced snapshot.")

                    updated.append((yaml_file.name, github_issue["number"], title))

        except Exception as e:
            print(f"  Error processing {yaml_file.name}: {e}")
            errors.append((yaml_file.name, str(e)))

        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Created: {len(created)}")
    print(f"Updated: {len(updated)}")
    print(f"Skipped (unchanged): {len(skipped_unchanged)}")
    print(f"Skipped (ideas): {len(skipped_ideas)}")
    print(f"Errors: {len(errors)}")
    print()

    if created:
        print("Created issues:")
        for filename, number, title in created:
            print(f"  #{number} - {title}")
            print(f"    File: {filename}")
        print()

    if updated:
        print("Updated issues:")
        for filename, number, title in updated:
            print(f"  #{number} - {title}")
            print(f"    File: {filename}")
        print()

    if skipped_ideas:
        print("Skipped (ideas):")
        for filename, title in skipped_ideas:
            print(f"  {title}")
            print(f"    File: {filename}")
        print()

    if errors:
        print("Errors:")
        for filename, error in errors:
            print(f"  {filename}: {error}")
        print()


def main():
    if len(sys.argv) != 3:
        print("Usage: python sync_issues.py <owner/repo> <issues-dir>")
        print("Example: python sync_issues.py coryzibell/matrix ~/.matrix/cache/construct/matrix/issues/")
        sys.exit(1)

    repo_arg = sys.argv[1]
    issues_dir_arg = sys.argv[2]

    if "/" not in repo_arg:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)

    owner, repo = repo_arg.split("/", 1)

    # Expand ~ in path
    issues_dir = Path(issues_dir_arg).expanduser()

    try:
        sync_issues(owner, repo, issues_dir)
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
