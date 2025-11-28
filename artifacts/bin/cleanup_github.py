#!/usr/bin/env python3
"""
GitHub Cleanup Script

Closes issues and deletes discussions by number.

Usage:
    python cleanup_github.py owner/repo --issues 2,3,4,5,6,7 --discussions 8,9,10,11,12,13,14
"""

import argparse
import json
import os
import requests
import sys
from pathlib import Path


def load_github_token():
    """Load GitHub token from ~/.claude.json"""
    config_path = Path.home() / ".claude.json"
    if not config_path.exists():
        print(f"Error: {config_path} not found")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = json.load(f)

    # Navigate to the GitHub token
    projects = config.get("projects", {})
    home_project = projects.get(str(Path.home()), {})
    mcp_servers = home_project.get("mcpServers", {})
    github_server = mcp_servers.get("github", {})
    env = github_server.get("env", {})
    token = env.get("GITHUB_PERSONAL_ACCESS_TOKEN")

    if not token:
        print("Error: GITHUB_PERSONAL_ACCESS_TOKEN not found in ~/.claude.json")
        sys.exit(1)

    return token


def close_issue(owner, repo, issue_number, token):
    """Close an issue and mark it as duplicate"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"state": "closed", "labels": ["duplicate"]}

    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        return True, "closed"
    else:
        return False, response.json().get("message", "Unknown error")


def delete_discussion(owner, repo, discussion_number, token):
    """Delete a discussion via GraphQL"""
    # First, get the discussion ID
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        discussion(number: $number) {
          id
        }
      }
    }
    """

    headers = {
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json",
    }

    variables = {"owner": owner, "repo": repo, "number": discussion_number}

    response = requests.post(
        "https://api.github.com/graphql",
        headers=headers,
        json={"query": query, "variables": variables},
    )

    if response.status_code != 200:
        return False, f"Failed to fetch discussion: {response.text}"

    data = response.json()
    if "errors" in data:
        return False, data["errors"][0]["message"]

    discussion_id = data["data"]["repository"]["discussion"]["id"]

    # Now delete it
    mutation = """
    mutation($discussionId: ID!) {
      deleteDiscussion(input: {id: $discussionId}) {
        clientMutationId
      }
    }
    """

    variables = {"discussionId": discussion_id}

    response = requests.post(
        "https://api.github.com/graphql",
        headers=headers,
        json={"query": mutation, "variables": variables},
    )

    if response.status_code == 200:
        result = response.json()
        if "errors" in result:
            return False, result["errors"][0]["message"]
        return True, "deleted"
    else:
        return False, f"Delete failed: {response.text}"


def parse_numbers(numbers_str):
    """Parse comma-separated numbers into a list of integers"""
    if not numbers_str:
        return []
    return [int(n.strip()) for n in numbers_str.split(",")]


def main():
    parser = argparse.ArgumentParser(
        description="Close GitHub issues and delete discussions"
    )
    parser.add_argument("repo", help="Repository in format owner/repo")
    parser.add_argument("--issues", help="Comma-separated issue numbers to close")
    parser.add_argument(
        "--discussions", help="Comma-separated discussion numbers to delete"
    )

    args = parser.parse_args()

    if "/" not in args.repo:
        print("Error: Repository must be in format owner/repo")
        sys.exit(1)

    owner, repo = args.repo.split("/", 1)
    token = load_github_token()

    issues = parse_numbers(args.issues) if args.issues else []
    discussions = parse_numbers(args.discussions) if args.discussions else []

    if not issues and not discussions:
        print("Error: Specify at least one issue or discussion to process")
        sys.exit(1)

    print(f"Repository: {owner}/{repo}\n")

    # Process issues
    if issues:
        print(f"Closing {len(issues)} issue(s)...")
        for issue_num in issues:
            success, message = close_issue(owner, repo, issue_num, token)
            status = "✓" if success else "✗"
            print(f"  {status} Issue #{issue_num}: {message}")

    # Process discussions
    if discussions:
        print(f"\nDeleting {len(discussions)} discussion(s)...")
        for disc_num in discussions:
            success, message = delete_discussion(owner, repo, disc_num, token)
            status = "✓" if success else "✗"
            print(f"  {status} Discussion #{disc_num}: {message}")

    print("\nDone.")


if __name__ == "__main__":
    main()
