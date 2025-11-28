#!/usr/bin/env python3
"""
sync_github.py - Synchronize YAML files to GitHub Issues and Discussions

Reads YAML files, routes to GitHub Issues (type: issue) or Discussions (type: idea)
based on the metadata.type field. Uses three-way merge logic to detect and resolve
conflicts between local, remote, and last-synced states.

Usage:
    python sync_github.py <owner/repo> <yaml-dir>

Example:
    python sync_github.py coryzibell/matrix ~/.matrix/cache/construct/matrix/issues/
"""

import json
import sys
import urllib.request
import urllib.error
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


# =============================================================================
# Configuration & Utilities
# =============================================================================

def read_github_token() -> str:
    """Read GitHub token from ~/.claude.json"""
    claude_config = Path.home() / ".claude.json"

    if not claude_config.exists():
        print(f"Error: {claude_config} not found")
        sys.exit(1)

    with open(claude_config, 'r') as f:
        config = json.load(f)

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
    """Parse YAML file"""
    if not HAS_YAML:
        print(f"Error: PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)

    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)


def write_yaml_file(yaml_file: Path, data: Dict) -> None:
    """Write data back to YAML file"""
    if not HAS_YAML:
        print(f"Error: PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)

    with open(yaml_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def get_item_type(yaml_data: Dict) -> str:
    """
    Get item type from YAML data.

    Checks root level 'type' first, then metadata.type.
    Normalizes "discussion" to "idea" for backward compatibility.

    Returns:
        "issue" or "idea"
    """
    # Check root level first
    item_type = yaml_data.get("type")

    # Fall back to metadata.type
    if item_type is None:
        metadata = yaml_data.get("metadata", {})
        item_type = metadata.get("type", "issue")

    # Normalize "discussion" to "idea"
    if item_type == "discussion":
        item_type = "idea"

    return item_type


# =============================================================================
# GitHub REST API (for Issues)
# =============================================================================

def make_rest_request(url: str, token: str, method: str = "GET", data: Optional[bytes] = None) -> Dict:
    """Make an authenticated GitHub REST API request"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "claude-code-sync-github"
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
    """List all issues in the repository (fetches ALL pages)"""
    all_issues = []
    page = 1

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues?state={state}&per_page=100&page={page}"
        issues = make_rest_request(url, token)

        if not issues:
            break

        all_issues.extend(issues)

        if len(issues) < 100:
            break

        page += 1

    return all_issues


def create_issue(owner: str, repo: str, token: str, title: str, body: str,
                 labels: List[str], assignees: List[str], dry_run: bool = False) -> Dict:
    """Create a new issue"""
    if dry_run:
        return {"number": 0, "title": title, "body": body, "labels": [{"name": l} for l in labels], "assignees": [{"login": a} for a in assignees], "updated_at": ""}

    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    data = json.dumps({
        "title": title,
        "body": body,
        "labels": labels,
        "assignees": assignees
    }).encode()

    return make_rest_request(url, token, method="POST", data=data)


def update_issue(owner: str, repo: str, token: str, issue_number: int, title: str,
                 body: str, labels: List[str], assignees: List[str], dry_run: bool = False) -> Dict:
    """Update an existing issue"""
    if dry_run:
        return {"number": issue_number, "title": title, "body": body, "labels": [{"name": l} for l in labels], "assignees": [{"login": a} for a in assignees], "updated_at": ""}

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    data = json.dumps({
        "title": title,
        "body": body,
        "labels": labels,
        "assignees": assignees
    }).encode()

    return make_rest_request(url, token, method="PATCH", data=data)


# =============================================================================
# GitHub GraphQL API (for Discussions)
# =============================================================================

def make_graphql_request(token: str, query: str, variables: Optional[Dict] = None) -> Dict:
    """Make an authenticated GitHub GraphQL API request"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "claude-code-sync-github"
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

            if "errors" in result:
                error_messages = [e.get("message", str(e)) for e in result["errors"]]
                raise Exception(f"GraphQL errors: {', '.join(error_messages)}")

            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error: HTTP {e.code} - {error_body}")
        raise


def get_repository_id(owner: str, repo: str, token: str) -> str:
    """Get the GitHub repository ID using GraphQL"""
    query = """
    query($owner: String!, $repo: String!) {
        repository(owner: $owner, name: $repo) {
            id
        }
    }
    """
    result = make_graphql_request(token, query, {"owner": owner, "repo": repo})
    return result["data"]["repository"]["id"]


def get_all_discussion_categories(owner: str, repo: str, token: str) -> Dict[str, str]:
    """Get all discussion categories as a name->id mapping"""
    query = """
    query($owner: String!, $repo: String!) {
        repository(owner: $owner, name: $repo) {
            discussionCategories(first: 20) {
                nodes {
                    id
                    name
                }
            }
        }
    }
    """

    result = make_graphql_request(token, query, {"owner": owner, "repo": repo})
    categories = result["data"]["repository"]["discussionCategories"]["nodes"]

    if not categories:
        raise Exception("No discussion categories found in repository. Enable Discussions first.")

    # Build name->id mapping (case-insensitive keys for easier lookup)
    return {cat["name"].lower(): cat["id"] for cat in categories}


def get_discussion_category_id(owner: str, repo: str, token: str,
                                category_name: str = "Ideas") -> Tuple[str, str]:
    """Get the discussion category ID by name"""
    query = """
    query($owner: String!, $repo: String!) {
        repository(owner: $owner, name: $repo) {
            discussionCategories(first: 20) {
                nodes {
                    id
                    name
                }
            }
        }
    }
    """

    result = make_graphql_request(token, query, {"owner": owner, "repo": repo})
    categories = result["data"]["repository"]["discussionCategories"]["nodes"]

    if not categories:
        raise Exception("No discussion categories found in repository. Enable Discussions first.")

    for category in categories:
        if category["name"] == category_name:
            return category["id"], category["name"]

    first_category = categories[0]
    print(f"  Warning: '{category_name}' category not found, using '{first_category['name']}'")
    return first_category["id"], first_category["name"]


def list_discussions(owner: str, repo: str, token: str) -> List[Dict]:
    """List all discussions in the repository"""
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
                    updatedAt
                    labels(first: 100) {
                        nodes {
                            id
                            name
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


def get_label_ids(owner: str, repo: str, token: str, label_names: List[str]) -> Dict[str, str]:
    """Get label IDs for given label names"""
    if not label_names:
        return {}

    query = """
    query($owner: String!, $repo: String!) {
        repository(owner: $owner, name: $repo) {
            labels(first: 100) {
                nodes {
                    id
                    name
                }
            }
        }
    }
    """

    result = make_graphql_request(token, query, {"owner": owner, "repo": repo})
    all_labels = result["data"]["repository"]["labels"]["nodes"]

    return {label["name"]: label["id"] for label in all_labels if label["name"] in label_names}


def create_discussion(owner: str, repo: str, token: str, repository_id: str,
                      category_id: str, title: str, body: str, label_ids: List[str], dry_run: bool = False) -> Dict:
    """Create a new discussion"""
    if dry_run:
        return {"id": "", "number": 0, "title": title, "body": body, "updatedAt": ""}

    mutation = """
    mutation($repositoryId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
        createDiscussion(input: {repositoryId: $repositoryId, categoryId: $categoryId, title: $title, body: $body}) {
            discussion {
                id
                number
                title
                body
                updatedAt
            }
        }
    }
    """

    variables = {
        "repositoryId": repository_id,
        "categoryId": category_id,
        "title": title,
        "body": body
    }

    result = make_graphql_request(token, mutation, variables)
    discussion = result["data"]["createDiscussion"]["discussion"]

    if label_ids:
        add_labels_to_discussion(token, discussion["id"], label_ids)

    return discussion


def update_discussion(token: str, discussion_id: str, title: str, body: str,
                      label_ids: List[str], dry_run: bool = False) -> Dict:
    """Update an existing discussion"""
    if dry_run:
        return {"id": discussion_id, "number": 0, "title": title, "body": body, "updatedAt": ""}

    mutation = """
    mutation($discussionId: ID!, $title: String!, $body: String!) {
        updateDiscussion(input: {discussionId: $discussionId, title: $title, body: $body}) {
            discussion {
                id
                number
                title
                body
                updatedAt
            }
        }
    }
    """

    variables = {
        "discussionId": discussion_id,
        "title": title,
        "body": body
    }

    result = make_graphql_request(token, mutation, variables)
    discussion = result["data"]["updateDiscussion"]["discussion"]

    if label_ids is not None:
        add_labels_to_discussion(token, discussion_id, label_ids)

    return discussion


def add_labels_to_discussion(token: str, discussion_id: str, label_ids: List[str]) -> None:
    """Add labels to a discussion"""
    if not label_ids:
        return

    mutation = """
    mutation($labelableId: ID!, $labelIds: [ID!]!) {
        addLabelsToLabelable(input: {labelableId: $labelableId, labelIds: $labelIds}) {
            clientMutationId
        }
    }
    """

    make_graphql_request(token, mutation, {"labelableId": discussion_id, "labelIds": label_ids})


# =============================================================================
# Sync Logic
# =============================================================================

def find_issue_by_title(issues: List[Dict], title: str) -> Optional[Dict]:
    """Find an issue by exact title match"""
    for issue in issues:
        if "pull_request" in issue:
            continue
        if issue["title"] == title:
            return issue
    return None


def find_issue_by_number(issues: List[Dict], number: int) -> Optional[Dict]:
    """Find an issue by number"""
    for issue in issues:
        if "pull_request" in issue:
            continue
        if issue["number"] == number:
            return issue
    return None


def find_discussion_by_title(discussions: List[Dict], title: str) -> Optional[Dict]:
    """Find a discussion by exact title match"""
    for discussion in discussions:
        if discussion["title"] == title:
            return discussion
    return None


def find_discussion_by_id(discussions: List[Dict], discussion_id: str) -> Optional[Dict]:
    """Find a discussion by ID"""
    for discussion in discussions:
        if discussion["id"] == discussion_id:
            return discussion
    return None


def sync_issue(yaml_file: Path, yaml_data: Dict, owner: str, repo: str, token: str,
               existing_issues: List[Dict], stats: Dict, dry_run: bool = False) -> None:
    """Sync a single issue YAML file to GitHub Issues"""
    metadata = yaml_data.get("metadata", {})

    # Check root level first, then metadata (for backward compat)
    title = yaml_data.get("title") or metadata.get("title", "Untitled Issue")
    body = yaml_data.get("body") or yaml_data.get("body_markdown") or metadata.get("body", "")
    labels = yaml_data.get("labels") or metadata.get("labels", [])
    assignees = yaml_data.get("assignees") or metadata.get("assignees", [])
    github_issue_number = metadata.get("github_issue_number")

    # Find matching GitHub issue
    github_issue = None
    if github_issue_number:
        github_issue = find_issue_by_number(existing_issues, github_issue_number)
    if not github_issue:
        github_issue = find_issue_by_title(existing_issues, title)

    if not github_issue:
        # Create new issue
        if dry_run:
            print(f"  [DRY RUN] Would create issue: {title}")
        else:
            print(f"  Creating issue: {title}")
        result = create_issue(owner, repo, token, title, body, labels, assignees, dry_run)

        if "metadata" not in yaml_data:
            yaml_data["metadata"] = {}
        yaml_data["metadata"]["github_issue_number"] = result["number"]

        if not dry_run:
            yaml_data["metadata"]["last_synced"] = sync_merge.create_snapshot(
                result["title"], result["body"],
                [label["name"] for label in result.get("labels", [])],
                result["updated_at"],
                [assignee["login"] for assignee in result.get("assignees", [])]
            )
            write_yaml_file(yaml_file, yaml_data)

        if dry_run:
            print(f"  [DRY RUN] Would save metadata")
        else:
            print(f"  Created issue #{result['number']}")
        stats["created"].append((yaml_file.name, result["number"], title, "issue"))
    else:
        # Issue exists - three-way merge
        github_labels = [label["name"] for label in github_issue.get("labels", [])]
        github_assignees = [assignee["login"] for assignee in github_issue.get("assignees", [])]

        base = metadata.get("last_synced")
        if base is None:
            base = {
                'title': github_issue["title"],
                'body': github_issue["body"] or "",
                'labels': github_labels,
                'assignees': github_assignees
            }

        local = {'title': title, 'body': body, 'labels': labels, 'assignees': assignees}
        remote = {
            'title': github_issue["title"],
            'body': github_issue["body"] or "",
            'labels': github_labels,
            'assignees': github_assignees
        }

        fields = ['title', 'body', 'labels', 'assignees']
        if not sync_merge.should_update(local, remote, base, fields):
            stats["unchanged"].append((yaml_file.name, github_issue["number"], title, "issue"))

            # Ensure tracking ID is saved
            if "github_issue_number" not in metadata:
                yaml_data["metadata"]["github_issue_number"] = github_issue["number"]
                write_yaml_file(yaml_file, yaml_data)
        else:
            changes = sync_merge.compute_field_changes(local, remote, base, fields)

            # Merge labels
            if 'labels' in changes and changes['labels'][0] == 'conflict':
                merged_labels = sync_merge.merge_labels(
                    changes['labels'][1], changes['labels'][2], changes['labels'][3]
                )
                changes['labels'] = ('both_same', merged_labels, merged_labels, changes['labels'][3])

            resolutions = {}
            merged, should_skip = sync_merge.merge_fields(changes, resolutions, interactive=True)

            if should_skip:
                print(f"  Skipping (user requested): {title}")
                return

            sync_merge.print_sync_summary(title, changes, resolutions, {})

            if dry_run:
                print(f"  [DRY RUN] Would update issue #{github_issue['number']}")
            else:
                print(f"  Updating issue #{github_issue['number']}...")
            result = update_issue(owner, repo, token, github_issue["number"],
                                 merged['title'], merged['body'],
                                 merged['labels'], merged['assignees'], dry_run)

            if not dry_run:
                yaml_data["metadata"]["github_issue_number"] = github_issue["number"]
                yaml_data["metadata"]["last_synced"] = sync_merge.create_snapshot(
                    result["title"], result["body"],
                    [label["name"] for label in result.get("labels", [])],
                    result["updated_at"],
                    [assignee["login"] for assignee in result.get("assignees", [])]
                )
                write_yaml_file(yaml_file, yaml_data)

            if dry_run:
                print(f"  [DRY RUN] Would save metadata")
            else:
                print(f"  Done.")
            stats["updated"].append((yaml_file.name, github_issue["number"], title, "issue"))


def sync_discussion(yaml_file: Path, yaml_data: Dict, owner: str, repo: str, token: str,
                    repository_id: str, category_map: Dict[str, str], default_category_id: str,
                    existing_discussions: List[Dict], stats: Dict, dry_run: bool = False) -> None:
    """Sync a single idea YAML file to GitHub Discussions"""
    metadata = yaml_data.get("metadata", {})

    # Check root level first, then metadata (for backward compat)
    title = yaml_data.get("title") or metadata.get("title", "Untitled Idea")
    body = yaml_data.get("body") or yaml_data.get("body_markdown") or metadata.get("body", "")
    labels = yaml_data.get("labels") or metadata.get("labels", [])
    github_discussion_id = metadata.get("github_discussion_id")

    # Get category - check YAML field, fall back to default
    yaml_category = yaml_data.get("category") or metadata.get("category", "")
    category_id = category_map.get(yaml_category.lower(), default_category_id) if yaml_category else default_category_id

    # Get label IDs
    label_id_map = get_label_ids(owner, repo, token, labels)
    label_ids = [label_id_map[label] for label in labels if label in label_id_map]

    # Find matching GitHub discussion
    github_discussion = None
    if github_discussion_id:
        github_discussion = find_discussion_by_id(existing_discussions, github_discussion_id)
    if not github_discussion:
        github_discussion = find_discussion_by_title(existing_discussions, title)

    if not github_discussion:
        # Create new discussion
        if dry_run:
            print(f"  [DRY RUN] Would create discussion: {title}")
        else:
            print(f"  Creating discussion: {title}")
        result = create_discussion(owner, repo, token, repository_id, category_id,
                                  title, body, label_ids, dry_run)

        if "metadata" not in yaml_data:
            yaml_data["metadata"] = {}
        yaml_data["metadata"]["github_discussion_id"] = result["id"]

        if not dry_run:
            yaml_data["metadata"]["last_synced"] = sync_merge.create_snapshot(
                result["title"], result["body"], labels, result["updatedAt"]
            )
            write_yaml_file(yaml_file, yaml_data)

        if dry_run:
            print(f"  [DRY RUN] Would save metadata")
        else:
            print(f"  Created discussion #{result['number']}")
        stats["created"].append((yaml_file.name, result["number"], title, "discussion"))
    else:
        # Discussion exists - three-way merge
        github_label_names = [label["name"] for label in github_discussion.get("labels", {}).get("nodes", [])]

        base = metadata.get("last_synced")
        if base is None:
            base = {
                'title': github_discussion["title"],
                'body': github_discussion["body"] or "",
                'labels': github_label_names
            }

        local = {'title': title, 'body': body, 'labels': labels}
        remote = {
            'title': github_discussion["title"],
            'body': github_discussion["body"] or "",
            'labels': github_label_names
        }

        fields = ['title', 'body', 'labels']
        if not sync_merge.should_update(local, remote, base, fields):
            stats["unchanged"].append((yaml_file.name, github_discussion["number"], title, "discussion"))

            if "github_discussion_id" not in metadata:
                yaml_data["metadata"]["github_discussion_id"] = github_discussion["id"]
                write_yaml_file(yaml_file, yaml_data)
        else:
            changes = sync_merge.compute_field_changes(local, remote, base, fields)

            if 'labels' in changes and changes['labels'][0] == 'conflict':
                merged_labels = sync_merge.merge_labels(
                    changes['labels'][1], changes['labels'][2], changes['labels'][3]
                )
                changes['labels'] = ('both_same', merged_labels, merged_labels, changes['labels'][3])

            resolutions = {}
            merged, should_skip = sync_merge.merge_fields(changes, resolutions, interactive=True)

            if should_skip:
                print(f"  Skipping (user requested): {title}")
                return

            sync_merge.print_sync_summary(title, changes, resolutions, {})

            merged_label_id_map = get_label_ids(owner, repo, token, merged['labels'])
            merged_label_ids = [merged_label_id_map[label] for label in merged['labels'] if label in merged_label_id_map]

            if dry_run:
                print(f"  [DRY RUN] Would update discussion #{github_discussion['number']}")
            else:
                print(f"  Updating discussion #{github_discussion['number']}...")
            result = update_discussion(token, github_discussion["id"],
                                      merged['title'], merged['body'], merged_label_ids, dry_run)

            if not dry_run:
                yaml_data["metadata"]["github_discussion_id"] = github_discussion["id"]
                yaml_data["metadata"]["last_synced"] = sync_merge.create_snapshot(
                    result["title"], result["body"], merged['labels'], result["updatedAt"]
                )
                write_yaml_file(yaml_file, yaml_data)

            if dry_run:
                print(f"  [DRY RUN] Would save metadata")
            else:
                print(f"  Done.")
            stats["updated"].append((yaml_file.name, github_discussion["number"], title, "discussion"))


# =============================================================================
# Main
# =============================================================================

def sync_all(owner: str, repo: str, yaml_dir: Path, dry_run: bool = False) -> None:
    """Main synchronization logic"""
    if dry_run:
        print(f"[DRY RUN] Syncing to {owner}/{repo}")
    else:
        print(f"Syncing to {owner}/{repo}")
    print(f"From directory: {yaml_dir}")
    print()

    if not yaml_dir.exists() or not yaml_dir.is_dir():
        print(f"Error: Invalid directory: {yaml_dir}")
        sys.exit(1)

    token = read_github_token()

    yaml_files = list(yaml_dir.glob("*.yaml")) + list(yaml_dir.glob("*.yml"))
    if not yaml_files:
        print(f"No YAML files found in {yaml_dir}")
        sys.exit(0)

    print(f"Found {len(yaml_files)} YAML files")

    # Categorize files by type
    issue_files = []
    idea_files = []
    errors = []

    for yaml_file in sorted(yaml_files):
        try:
            yaml_data = parse_yaml_file(yaml_file)
            item_type = get_item_type(yaml_data)
            if item_type == "idea":
                idea_files.append((yaml_file, yaml_data))
            else:
                issue_files.append((yaml_file, yaml_data))
        except Exception as e:
            errors.append((yaml_file.name, str(e)))

    print(f"  {len(issue_files)} issues, {len(idea_files)} discussions")
    print()

    stats = {"created": [], "updated": [], "unchanged": [], "errors": errors}

    # Fetch existing GitHub data
    existing_issues = []
    existing_discussions = []
    repository_id = None
    category_map = {}
    default_category_id = None

    if issue_files:
        print("Fetching existing issues...")
        existing_issues = list_issues(owner, repo, token, state="all")
        print(f"Found {len(existing_issues)} existing issues")

    if idea_files:
        print("Fetching repository info for discussions...")
        try:
            repository_id = get_repository_id(owner, repo, token)
            category_map = get_all_discussion_categories(owner, repo, token)
            # Default to "Ideas" category, or first available
            default_category_id = category_map.get("ideas") or list(category_map.values())[0]
            print(f"Found {len(category_map)} discussion categories")

            print("Fetching existing discussions...")
            existing_discussions = list_discussions(owner, repo, token)
            print(f"Found {len(existing_discussions)} existing discussions")
        except Exception as e:
            print(f"Warning: Could not fetch discussions: {e}")
            print("Discussions will be skipped. Enable Discussions on the repo first.")
            # Move idea files to errors
            for yaml_file, yaml_data in idea_files:
                title = yaml_data.get("title") or yaml_data.get("metadata", {}).get("title", "Untitled")
                stats["errors"].append((yaml_file.name, f"Discussions not available: {title}"))
            idea_files = []

    print()

    # Process issues
    for yaml_file, yaml_data in issue_files:
        print(f"Processing: {yaml_file.name}")
        try:
            sync_issue(yaml_file, yaml_data, owner, repo, token, existing_issues, stats, dry_run)
        except Exception as e:
            print(f"  Error: {e}")
            stats["errors"].append((yaml_file.name, str(e)))
        print()

    # Process discussions
    for yaml_file, yaml_data in idea_files:
        print(f"Processing: {yaml_file.name}")
        try:
            sync_discussion(yaml_file, yaml_data, owner, repo, token,
                          repository_id, category_map, default_category_id,
                          existing_discussions, stats, dry_run)
        except Exception as e:
            print(f"  Error: {e}")
            stats["errors"].append((yaml_file.name, str(e)))
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Created: {len(stats['created'])}")
    print(f"Updated: {len(stats['updated'])}")
    print(f"Unchanged: {len(stats['unchanged'])}")
    print(f"Errors: {len(stats['errors'])}")
    print()

    if stats["created"]:
        print("Created:")
        for filename, number, title, item_type in stats["created"]:
            print(f"  #{number} [{item_type}] {title}")
        print()

    if stats["updated"]:
        print("Updated:")
        for filename, number, title, item_type in stats["updated"]:
            print(f"  #{number} [{item_type}] {title}")
        print()

    if stats["errors"]:
        print("Errors:")
        for filename, error in stats["errors"]:
            print(f"  {filename}: {error}")
        print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Synchronize YAML files to GitHub Issues and Discussions")
    parser.add_argument("repo", help="Repository in format 'owner/repo'")
    parser.add_argument("yaml_dir", help="Directory containing YAML files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making changes")
    args = parser.parse_args()

    if "/" not in args.repo:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)

    owner, repo = args.repo.split("/", 1)
    yaml_dir = Path(args.yaml_dir).expanduser()

    try:
        sync_all(owner, repo, yaml_dir, dry_run=args.dry_run)
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
