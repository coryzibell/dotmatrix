#!/usr/bin/env python3
"""
sync_discussions.py - Synchronize idea YAML files to GitHub Discussions

Reads idea YAML files (where metadata.type == "idea"), compares with GitHub
Discussions field by field, and updates only changed fields. Uses three-way merge
logic to detect and resolve conflicts between local, remote, and last-synced states.

Usage:
    python sync_discussions.py <owner/repo> <ideas-dir>

Example:
    python sync_discussions.py coryzibell/matrix ~/.matrix/cache/construct/matrix/issues/
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
    Parse idea YAML file

    Returns:
        Dict containing idea data, or None if parse fails
    """
    if not HAS_YAML:
        print(f"Error: PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)

    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)


def write_yaml_file(yaml_file: Path, data: Dict) -> None:
    """Write idea data back to YAML file"""
    if not HAS_YAML:
        print(f"Error: PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)

    with open(yaml_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def make_graphql_request(token: str, query: str, variables: Optional[Dict] = None) -> Dict:
    """Make an authenticated GitHub GraphQL API request"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "claude-code-sync-discussions"
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


def get_discussion_category_id(owner: str, repo: str, token: str, category_name: str = "Ideas") -> Tuple[str, str]:
    """
    Get the discussion category ID by name, fallback to first category if not found

    Returns:
        Tuple of (category_id, category_name)
    """
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
        raise Exception("No discussion categories found in repository")

    # Try to find the requested category
    for category in categories:
        if category["name"] == category_name:
            return category["id"], category["name"]

    # Fall back to first category
    first_category = categories[0]
    print(f"Warning: '{category_name}' category not found, using '{first_category['name']}' instead")
    return first_category["id"], first_category["name"]


def list_discussions(owner: str, repo: str, token: str) -> List[Dict]:
    """
    List all discussions in the repository

    Returns:
        List of discussion dictionaries
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
    """
    Get label IDs for given label names

    Returns:
        Dict mapping label name to label ID
    """
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

    label_map = {}
    for label in all_labels:
        if label["name"] in label_names:
            label_map[label["name"]] = label["id"]

    return label_map


def create_discussion(owner: str, repo: str, token: str, repository_id: str, category_id: str,
                     title: str, body: str, label_ids: List[str]) -> Dict:
    """Create a new discussion"""
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

    # Add labels if provided
    if label_ids:
        add_labels_to_discussion(token, discussion["id"], label_ids)

    return discussion


def update_discussion(token: str, discussion_id: str, title: str, body: str, label_ids: List[str]) -> Dict:
    """Update an existing discussion"""
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

    # Update labels if provided
    if label_ids is not None:
        # Note: This replaces all labels. To preserve existing labels, we'd need to fetch them first.
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

    variables = {
        "labelableId": discussion_id,
        "labelIds": label_ids
    }

    make_graphql_request(token, mutation, variables)


def parse_github_timestamp(timestamp_str: str) -> datetime:
    """Parse GitHub ISO 8601 timestamp"""
    # GitHub returns timestamps like: "2024-01-15T10:30:45Z"
    return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")


def get_file_modified_time(file_path: Path) -> datetime:
    """Get file modification time as datetime"""
    return datetime.fromtimestamp(file_path.stat().st_mtime)


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


def is_idea(yaml_data: Dict) -> bool:
    """
    Check if YAML represents an idea rather than an issue

    Returns:
        True if type is "idea", False otherwise
    """
    metadata = yaml_data.get("metadata", {})
    return metadata.get("type") == "idea"


def extract_idea_data(yaml_data: Dict) -> Tuple[str, str, List[str], Optional[str]]:
    """
    Extract idea fields from YAML data

    Returns:
        (title, body, labels, github_discussion_id)
    """
    metadata = yaml_data.get("metadata", {})

    title = metadata.get("title", "Untitled Idea")
    body = yaml_data.get("body_markdown", "")
    labels = metadata.get("labels", [])
    github_discussion_id = metadata.get("github_discussion_id")

    return title, body, labels, github_discussion_id


def get_last_synced(yaml_data: Dict) -> Optional[Dict]:
    """
    Get last_synced snapshot from YAML metadata.

    Returns:
        Dict with last synced field values, or None if not present
    """
    metadata = yaml_data.get("metadata", {})
    return metadata.get("last_synced")


def save_last_synced(yaml_file: Path, yaml_data: Dict, title: str, body: str,
                     labels: List[str], updated_at: str) -> None:
    """
    Update last_synced snapshot in YAML file.

    Args:
        yaml_file: Path to YAML file
        yaml_data: Current YAML data dict
        title: Synced title
        body: Synced body
        labels: Synced labels
        updated_at: GitHub updated_at timestamp
    """
    if "metadata" not in yaml_data:
        yaml_data["metadata"] = {}

    yaml_data["metadata"]["last_synced"] = sync_merge.create_snapshot(
        title, body, labels, updated_at
    )

    write_yaml_file(yaml_file, yaml_data)


def sync_discussions(owner: str, repo: str, ideas_dir: Path) -> None:
    """Main synchronization logic"""
    print(f"Syncing ideas to {owner}/{repo} discussions")
    print(f"From directory: {ideas_dir}")
    print()

    # Validate directory
    if not ideas_dir.exists():
        print(f"Error: Directory does not exist: {ideas_dir}")
        sys.exit(1)

    if not ideas_dir.is_dir():
        print(f"Error: Not a directory: {ideas_dir}")
        sys.exit(1)

    # Read configuration
    token = read_github_token()

    # Find all YAML files
    yaml_files = list(ideas_dir.glob("*.yaml")) + list(ideas_dir.glob("*.yml"))

    if not yaml_files:
        print(f"No YAML files found in {ideas_dir}")
        sys.exit(0)

    print(f"Found {len(yaml_files)} YAML files")

    # Get repository and category IDs
    print("Fetching repository information...")
    repository_id = get_repository_id(owner, repo, token)
    category_id, category_name = get_discussion_category_id(owner, repo, token)
    print(f"Using discussion category: {category_name}")
    print()

    # Fetch existing discussions
    print("Fetching existing discussions from GitHub...")
    existing_discussions = list_discussions(owner, repo, token)
    print(f"Found {len(existing_discussions)} existing discussions in repository")
    print()

    # Track statistics
    created = []
    updated = []
    skipped_unchanged = []
    skipped_issues = []
    errors = []

    # Process each YAML file
    for yaml_file in sorted(yaml_files):
        print(f"Processing: {yaml_file.name}")

        try:
            # Parse YAML
            yaml_data = parse_yaml_file(yaml_file)

            # Skip non-ideas (issues)
            if not is_idea(yaml_data):
                metadata = yaml_data.get("metadata", {})
                title = metadata.get("title", "Untitled")
                file_type = metadata.get("type", "unknown")
                print(f"  Skipping (type: {file_type}): {title}")
                skipped_issues.append((yaml_file.name, title))
                continue

            # Extract idea data
            title, body, labels, github_discussion_id = extract_idea_data(yaml_data)

            # Get label IDs for the labels
            label_id_map = get_label_ids(owner, repo, token, labels)
            label_ids = [label_id_map[label] for label in labels if label in label_id_map]

            # Find matching GitHub discussion
            github_discussion = None
            if github_discussion_id:
                # Try by ID first (most reliable)
                github_discussion = find_discussion_by_id(existing_discussions, github_discussion_id)

            if not github_discussion:
                # Fall back to title match
                github_discussion = find_discussion_by_title(existing_discussions, title)

            if not github_discussion:
                # Create new discussion
                print(f"  Creating new discussion: {title}")
                result = create_discussion(owner, repo, token, repository_id, category_id,
                                         title, body, label_ids)

                # Update YAML with GitHub discussion ID and snapshot
                if "metadata" not in yaml_data:
                    yaml_data["metadata"] = {}
                yaml_data["metadata"]["github_discussion_id"] = result["id"]

                # Save snapshot
                save_last_synced(
                    yaml_file, yaml_data,
                    result["title"], result["body"],
                    labels,  # Use local labels since they were just pushed
                    result["updatedAt"]
                )

                print(f"  Created discussion #{result['number']}")
                created.append((yaml_file.name, result["number"], title))
            else:
                # Discussion exists - three-way merge
                github_label_names = [label["name"] for label in github_discussion.get("labels", {}).get("nodes", [])]

                # Get base snapshot
                base = get_last_synced(yaml_data)
                if base is None:
                    # First sync after this change - treat remote as base
                    base = {
                        'title': github_discussion["title"],
                        'body': github_discussion["body"] or "",
                        'labels': github_label_names
                    }

                # Build local/remote state dicts
                local = {
                    'title': title,
                    'body': body,
                    'labels': labels
                }
                remote = {
                    'title': github_discussion["title"],
                    'body': github_discussion["body"] or "",
                    'labels': github_label_names
                }

                # Quick check: any differences?
                if not sync_merge.should_update(local, remote, base, ['title', 'body', 'labels']):
                    # No changes needed
                    skipped_unchanged.append((yaml_file.name, github_discussion["number"], title))

                    # Ensure github_discussion_id is tracked
                    if "metadata" not in yaml_data:
                        yaml_data["metadata"] = {}
                    if "github_discussion_id" not in yaml_data["metadata"]:
                        yaml_data["metadata"]["github_discussion_id"] = github_discussion["id"]
                        write_yaml_file(yaml_file, yaml_data)
                else:
                    # Compute changes
                    changes = sync_merge.compute_field_changes(
                        local, remote, base,
                        ['title', 'body', 'labels']
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

                    # Get label IDs for merged labels
                    merged_label_id_map = get_label_ids(owner, repo, token, merged['labels'])
                    merged_label_ids = [merged_label_id_map[label] for label in merged['labels'] if label in merged_label_id_map]

                    # Update GitHub with merged values
                    print(f"  Updating discussion #{github_discussion['number']}...")
                    result = update_discussion(
                        token,
                        github_discussion["id"],
                        merged['title'], merged['body'],
                        merged_label_ids
                    )

                    # Ensure github_discussion_id is tracked
                    if "metadata" not in yaml_data:
                        yaml_data["metadata"] = {}
                    if "github_discussion_id" not in yaml_data["metadata"]:
                        yaml_data["metadata"]["github_discussion_id"] = github_discussion["id"]

                    # Save snapshot
                    save_last_synced(
                        yaml_file, yaml_data,
                        result["title"], result["body"],
                        merged['labels'],
                        result["updatedAt"]
                    )

                    print(f"  Done. Updated last_synced snapshot.")

                    updated.append((yaml_file.name, github_discussion["number"], title))

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
    print(f"Skipped (issues): {len(skipped_issues)}")
    print(f"Errors: {len(errors)}")
    print()

    if created:
        print("Created discussions:")
        for filename, number, title in created:
            print(f"  #{number} - {title}")
            print(f"    File: {filename}")
        print()

    if updated:
        print("Updated discussions:")
        for filename, number, title in updated:
            print(f"  #{number} - {title}")
            print(f"    File: {filename}")
        print()

    if skipped_issues:
        print("Skipped (issues):")
        for filename, title in skipped_issues:
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
        print("Usage: python sync_discussions.py <owner/repo> <ideas-dir>")
        print("Example: python sync_discussions.py coryzibell/matrix ~/.matrix/cache/construct/matrix/issues/")
        sys.exit(1)

    repo_arg = sys.argv[1]
    ideas_dir_arg = sys.argv[2]

    if "/" not in repo_arg:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)

    owner, repo = repo_arg.split("/", 1)

    # Expand ~ in path
    ideas_dir = Path(ideas_dir_arg).expanduser()

    try:
        sync_discussions(owner, repo, ideas_dir)
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
