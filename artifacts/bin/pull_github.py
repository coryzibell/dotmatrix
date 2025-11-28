#!/usr/bin/env python3
"""
pull_github.py - Pull GitHub issues and discussions into local YAML files

Fetches issues and discussions from a GitHub repository and creates/updates
local YAML files. Uses last_synced metadata to merge changes intelligently
without overwriting local modifications.

Usage:
    python pull_github.py <owner/repo> <output-dir>

Example:
    python pull_github.py coryzibell/matrix ~/.matrix/cache/construct/matrix/issues/
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def read_github_token() -> str:
    """Read GitHub token from environment or ~/.claude.json"""
    # Try environment variable first
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token

    # Fall back to ~/.claude.json
    claude_config = Path.home() / ".claude.json"

    if not claude_config.exists():
        print(f"Error: GITHUB_TOKEN not set and {claude_config} not found")
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

    print("Error: GitHub token not found")
    print("Set GITHUB_TOKEN environment variable or configure in ~/.claude.json")
    sys.exit(1)


def make_rest_request(url: str, token: str) -> Dict:
    """Make an authenticated GitHub REST API request"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "claude-code-pull-github"
    }

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error: HTTP {e.code} - {error_body}")
        raise


def make_graphql_request(token: str, query: str, variables: Optional[Dict] = None) -> Dict:
    """Make an authenticated GitHub GraphQL API request"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "claude-code-pull-github"
    }

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    data = json.dumps(payload).encode()
    url = "https://api.github.com/graphql"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())

            # Check for GraphQL errors
            if "errors" in result:
                error_messages = [e.get("message", str(e)) for e in result["errors"]]
                raise Exception(f"GraphQL errors: {', '.join(error_messages)}")

            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error: HTTP {e.code} - {error_body}")
        raise


def fetch_issues(owner: str, repo: str, token: str) -> List[Dict]:
    """
    Fetch all open issues from repository

    Returns:
        List of issue dictionaries with comments
    """
    all_issues = []
    page = 1

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=open&per_page=100&page={page}"
        issues = make_rest_request(url, token)

        if not issues:
            break

        # Filter out pull requests
        issues = [i for i in issues if "pull_request" not in i]

        # Fetch comments for each issue
        for issue in issues:
            comments_url = issue["comments_url"]
            comments = make_rest_request(comments_url, token)
            issue["comments_data"] = comments

        all_issues.extend(issues)

        if len(issues) < 100:
            break

        page += 1

    return all_issues


def fetch_discussions(owner: str, repo: str, token: str) -> List[Dict]:
    """
    Fetch all discussions from repository via GraphQL

    Returns:
        List of discussion dictionaries with comments
    """
    query = """
    query($owner: String!, $repo: String!, $cursor: String) {
        repository(owner: $owner, name: $repo) {
            discussions(first: 100, after: $cursor) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    id
                    number
                    title
                    body
                    createdAt
                    updatedAt
                    labels(first: 100) {
                        nodes {
                            name
                        }
                    }
                    category {
                        name
                    }
                    comments(first: 100) {
                        nodes {
                            id
                            author {
                                login
                            }
                            body
                            createdAt
                            updatedAt
                        }
                    }
                }
            }
        }
    }
    """

    all_discussions = []
    cursor = None

    while True:
        result = make_graphql_request(token, query, {"owner": owner, "repo": repo, "cursor": cursor})
        discussions_data = result["data"]["repository"]["discussions"]
        all_discussions.extend(discussions_data["nodes"])

        if not discussions_data["pageInfo"]["hasNextPage"]:
            break

        cursor = discussions_data["pageInfo"]["endCursor"]

    return all_discussions


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to filename-safe slug"""
    # Lowercase
    slug = text.lower()
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove special characters
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Trim hyphens from ends
    slug = slug.strip('-')
    # Truncate
    return slug[:max_length]


def find_existing_yaml(output_dir: Path, github_issue_number: Optional[int] = None,
                       github_discussion_id: Optional[str] = None,
                       github_discussion_number: Optional[int] = None) -> Optional[Path]:
    """Find existing YAML file by GitHub identifiers"""
    yaml_files = list(output_dir.glob("*.yaml")) + list(output_dir.glob("*.yml"))

    if not HAS_YAML:
        return None

    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                metadata = data.get("metadata", {})

                if github_issue_number and metadata.get("github_issue_number") == github_issue_number:
                    return yaml_file
                if github_discussion_id and metadata.get("github_discussion_id") == github_discussion_id:
                    return yaml_file
                if github_discussion_number and metadata.get("github_discussion_number") == github_discussion_number:
                    return yaml_file
        except:
            continue

    return None


def has_local_changes(metadata: Dict, field: str, remote_value) -> bool:
    """
    Check if local has changes compared to last_synced

    Returns:
        True if local differs from last_synced (has local changes)
    """
    last_synced = metadata.get("last_synced", {})
    if not last_synced:
        return False

    local_value = None
    if field == "title":
        local_value = metadata.get("title")
    elif field == "body":
        # Body is outside metadata
        return False  # Caller must check separately
    elif field == "labels":
        local_value = metadata.get("labels", [])

    base_value = last_synced.get(field)

    # Normalize for comparison
    if isinstance(local_value, list):
        local_value = sorted(local_value)
        base_value = sorted(base_value) if base_value else []

    return local_value != base_value


def create_issue_yaml(issue: Dict, output_dir: Path, dry_run: bool = False) -> Tuple[str, Path]:
    """
    Create or update YAML file for GitHub issue

    Returns:
        ("created" | "updated" | "unchanged", file_path)
    """
    if not HAS_YAML:
        print(f"Error: PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)

    number = issue["number"]
    title = issue["title"]
    body = issue.get("body") or ""
    labels = [label["name"] for label in issue.get("labels", [])]
    assignees = [assignee["login"] for assignee in issue.get("assignees", [])]
    state = issue["state"]
    created_at = issue["created_at"]
    updated_at = issue["updated_at"]
    comments = issue.get("comments_data", [])

    # Find existing file
    existing_file = find_existing_yaml(output_dir, github_issue_number=number)

    if existing_file:
        # Update existing
        with open(existing_file, 'r') as f:
            data = yaml.safe_load(f)

        metadata = data.get("metadata", {})
        last_synced = metadata.get("last_synced", {})

        # Check for local changes
        title_changed_locally = has_local_changes(metadata, "title", title)
        body_changed_locally = data.get("body_markdown", "") != last_synced.get("body", "")
        labels_changed_locally = has_local_changes(metadata, "labels", labels)

        # Update fields only if no local changes
        changes = []
        if title != metadata.get("title"):
            if title_changed_locally:
                print(f"    Warning: Local title changes exist, skipping title update")
            else:
                metadata["title"] = title
                changes.append("title")

        if body != data.get("body_markdown", ""):
            if body_changed_locally:
                print(f"    Warning: Local body changes exist, skipping body update")
            else:
                data["body_markdown"] = body
                changes.append("body")

        if sorted(labels) != sorted(metadata.get("labels", [])):
            if labels_changed_locally:
                print(f"    Warning: Local label changes exist, skipping label update")
            else:
                metadata["labels"] = labels
                changes.append("labels")

        # Always update these fields
        metadata["assignees"] = assignees
        metadata["state"] = state
        metadata["github_updated_at"] = updated_at

        # Update last_synced
        metadata["last_synced"] = {
            "title": title,
            "body": body,
            "labels": labels,
            "updated_at": updated_at
        }

        # Update comments (remote-authoritative)
        data["comments"] = [
            {
                "id": c["id"],
                "author": c["user"]["login"],
                "created_at": c["created_at"],
                "updated_at": c["updated_at"],
                "body": c["body"]
            }
            for c in comments
        ]

        data["metadata"] = metadata

        if not dry_run:
            with open(existing_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        if changes:
            return ("updated", existing_file)
        else:
            return ("unchanged", existing_file)

    else:
        # Create new file
        slug = slugify(title)
        filename = f"{number}-{slug}.yaml"
        file_path = output_dir / filename

        data = {
            "metadata": {
                "title": title,
                "type": "issue",
                "labels": labels,
                "assignees": assignees,
                "state": state,
                "github_issue_number": number,
                "github_updated_at": updated_at,
                "last_synced": {
                    "title": title,
                    "body": body,
                    "labels": labels,
                    "updated_at": updated_at
                }
            },
            "body_markdown": body,
            "comments": [
                {
                    "id": c["id"],
                    "author": c["user"]["login"],
                    "created_at": c["created_at"],
                    "updated_at": c["updated_at"],
                    "body": c["body"]
                }
                for c in comments
            ]
        }

        if not dry_run:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        return ("created", file_path)


def create_discussion_yaml(discussion: Dict, output_dir: Path, dry_run: bool = False) -> Tuple[str, Path]:
    """
    Create or update YAML file for GitHub discussion

    Returns:
        ("created" | "updated" | "unchanged", file_path)
    """
    if not HAS_YAML:
        print(f"Error: PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)

    discussion_id = discussion["id"]
    number = discussion["number"]
    title = discussion["title"]
    body = discussion.get("body") or ""
    labels = [label["name"] for label in discussion.get("labels", {}).get("nodes", [])]
    category = discussion["category"]["name"]
    created_at = discussion["createdAt"]
    updated_at = discussion["updatedAt"]
    comments = discussion.get("comments", {}).get("nodes", [])

    # Find existing file
    existing_file = find_existing_yaml(output_dir,
                                       github_discussion_id=discussion_id,
                                       github_discussion_number=number)

    if existing_file:
        # Update existing
        with open(existing_file, 'r') as f:
            data = yaml.safe_load(f)

        metadata = data.get("metadata", {})
        last_synced = metadata.get("last_synced", {})

        # Check for local changes
        title_changed_locally = has_local_changes(metadata, "title", title)
        body_changed_locally = data.get("body_markdown", "") != last_synced.get("body", "")
        labels_changed_locally = has_local_changes(metadata, "labels", labels)

        # Update fields only if no local changes
        changes = []
        if title != metadata.get("title"):
            if title_changed_locally:
                print(f"    Warning: Local title changes exist, skipping title update")
            else:
                metadata["title"] = title
                changes.append("title")

        if body != data.get("body_markdown", ""):
            if body_changed_locally:
                print(f"    Warning: Local body changes exist, skipping body update")
            else:
                data["body_markdown"] = body
                changes.append("body")

        if sorted(labels) != sorted(metadata.get("labels", [])):
            if labels_changed_locally:
                print(f"    Warning: Local label changes exist, skipping label update")
            else:
                metadata["labels"] = labels
                changes.append("labels")

        # Always update these fields
        metadata["category"] = category
        metadata["github_updated_at"] = updated_at
        metadata["github_discussion_number"] = number

        # Update last_synced
        metadata["last_synced"] = {
            "title": title,
            "body": body,
            "labels": labels,
            "updated_at": updated_at
        }

        # Update comments (remote-authoritative)
        data["comments"] = [
            {
                "id": c["id"],
                "author": c["author"]["login"],
                "created_at": c["createdAt"],
                "body": c["body"]
            }
            for c in comments
        ]

        data["metadata"] = metadata

        if not dry_run:
            with open(existing_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        if changes:
            return ("updated", existing_file)
        else:
            return ("unchanged", existing_file)

    else:
        # Create new file
        slug = slugify(title)
        filename = f"{number}-{slug}.yaml"
        file_path = output_dir / filename

        data = {
            "metadata": {
                "title": title,
                "type": "idea",
                "labels": labels,
                "category": category,
                "github_discussion_id": discussion_id,
                "github_discussion_number": number,
                "github_updated_at": updated_at,
                "last_synced": {
                    "title": title,
                    "body": body,
                    "labels": labels,
                    "updated_at": updated_at
                }
            },
            "body_markdown": body,
            "comments": [
                {
                    "id": c["id"],
                    "author": c["author"]["login"],
                    "created_at": c["createdAt"],
                    "body": c["body"]
                }
                for c in comments
            ]
        }

        if not dry_run:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        return ("created", file_path)


def pull_github(owner: str, repo: str, output_dir: Path, dry_run: bool = False) -> None:
    """Main pull logic"""
    if dry_run:
        print(f"[DRY RUN] Pulling from {owner}/{repo}...")
    else:
        print(f"Pulling from {owner}/{repo}...")
    print()

    # Ensure output directory exists
    if dry_run:
        print(f"[DRY RUN] Would create directory: {output_dir}")
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Read token
    token = read_github_token()

    # Fetch issues
    print("Fetching issues...")
    issues = fetch_issues(owner, repo, token)
    print(f"Found {len(issues)} open issues")
    print()

    # Fetch discussions
    print("Fetching discussions...")
    discussions = fetch_discussions(owner, repo, token)
    print(f"Found {len(discussions)} discussions")
    print()

    # Process issues
    print("Issues:")
    created_issues = []
    updated_issues = []
    unchanged_issues = []

    for issue in issues:
        number = issue["number"]
        title = issue["title"]
        comment_count = len(issue.get("comments_data", []))

        status, file_path = create_issue_yaml(issue, output_dir, dry_run)

        if status == "created":
            if dry_run:
                print(f"  [DRY RUN] #{number} {title} ({comment_count} comments) → would create {file_path.name}")
            else:
                print(f"  #{number} {title} ({comment_count} comments) → created {file_path.name}")
            created_issues.append((number, title, comment_count, file_path.name))
        elif status == "updated":
            if dry_run:
                print(f"  [DRY RUN] #{number} {title} ({comment_count} comments) → would update")
            else:
                print(f"  #{number} {title} ({comment_count} comments) → updated")
            updated_issues.append((number, title, comment_count))
        else:
            print(f"  #{number} {title} ({comment_count} comments) → unchanged")
            unchanged_issues.append((number, title, comment_count))

    print()

    # Process discussions
    print("Discussions:")
    created_discussions = []
    updated_discussions = []
    unchanged_discussions = []

    for discussion in discussions:
        number = discussion["number"]
        title = discussion["title"]
        comment_count = len(discussion.get("comments", {}).get("nodes", []))

        status, file_path = create_discussion_yaml(discussion, output_dir, dry_run)

        if status == "created":
            if dry_run:
                print(f"  [DRY RUN] #{number} {title} ({comment_count} comments) → would create {file_path.name}")
            else:
                print(f"  #{number} {title} ({comment_count} comments) → created {file_path.name}")
            created_discussions.append((number, title, comment_count, file_path.name))
        elif status == "updated":
            if dry_run:
                print(f"  [DRY RUN] #{number} {title} ({comment_count} comments) → would update")
            else:
                print(f"  #{number} {title} ({comment_count} comments) → updated")
            updated_discussions.append((number, title, comment_count))
        else:
            print(f"  #{number} {title} ({comment_count} comments) → unchanged")
            unchanged_discussions.append((number, title, comment_count))

    print()

    # Summary
    total_created = len(created_issues) + len(created_discussions)
    total_updated = len(updated_issues) + len(updated_discussions)
    total_unchanged = len(unchanged_issues) + len(unchanged_discussions)

    print(f"Summary: {total_created} created, {total_updated} updated, {total_unchanged} unchanged")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Pull GitHub issues and discussions into local YAML files")
    parser.add_argument("repo", help="Repository in format 'owner/repo'")
    parser.add_argument("output_dir", help="Directory to write YAML files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making changes")
    args = parser.parse_args()

    if "/" not in args.repo:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)

    owner, repo = args.repo.split("/", 1)

    # Expand ~ in path
    output_dir = Path(args.output_dir).expanduser()

    try:
        pull_github(owner, repo, output_dir, dry_run=args.dry_run)
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
