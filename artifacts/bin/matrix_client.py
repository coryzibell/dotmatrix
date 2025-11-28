#!/usr/bin/env python3
"""
dotmatrix-ai GitHub App Client

Posts comments to GitHub Issues and Discussions as the dotmatrix-ai bot,
with optional identity signatures.

Environment variables:
- DOTMATRIX_APP_ID: GitHub App ID
- DOTMATRIX_INSTALLATION_ID: Installation ID
- DOTMATRIX_PRIVATE_KEY: Full PEM file contents

Usage:
    matrix_client.py issue <owner> <repo> <number> <message> [--identity NAME]
    matrix_client.py discussion <owner> <repo> <number> <message> [--identity NAME]
"""

import os
import sys
import time
import argparse
import jwt
import requests
from datetime import datetime, timedelta


class MatrixClient:
    """GitHub App client for dotmatrix-ai"""

    def __init__(self):
        self.app_id = os.getenv('DOTMATRIX_APP_ID')
        self.installation_id = os.getenv('DOTMATRIX_INSTALLATION_ID')
        self.private_key = os.getenv('DOTMATRIX_PRIVATE_KEY')

        if not all([self.app_id, self.installation_id, self.private_key]):
            raise ValueError(
                "Missing required environment variables:\n"
                "  DOTMATRIX_APP_ID\n"
                "  DOTMATRIX_INSTALLATION_ID\n"
                "  DOTMATRIX_PRIVATE_KEY"
            )

        self._installation_token = None
        self._token_expires_at = None

    def _generate_jwt(self):
        """Generate JWT signed with private key (RS256)"""
        now = int(time.time())
        payload = {
            'iat': now - 60,  # Allow for clock drift
            'exp': now + 600,  # Max 10 minutes
            'iss': self.app_id
        }

        return jwt.encode(payload, self.private_key, algorithm='RS256')

    def _get_installation_token(self):
        """Exchange JWT for installation access token"""
        # Check if we have a valid cached token
        if self._installation_token and self._token_expires_at:
            # Refresh 5 minutes before expiration
            if datetime.utcnow() < self._token_expires_at - timedelta(minutes=5):
                return self._installation_token

        # Generate new JWT
        jwt_token = self._generate_jwt()

        # Exchange for installation token
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        url = f'https://api.github.com/app/installations/{self.installation_id}/access_tokens'
        response = requests.post(url, headers=headers)

        if response.status_code != 201:
            raise RuntimeError(
                f"Failed to get installation token: {response.status_code}\n"
                f"{response.text}"
            )

        data = response.json()
        self._installation_token = data['token']
        self._token_expires_at = datetime.strptime(
            data['expires_at'],
            '%Y-%m-%dT%H:%M:%SZ'
        )

        return self._installation_token

    def _format_with_identity(self, body, identity=None):
        """Format message with identity signature"""
        if not identity:
            return body

        return (
            f"**[{identity}]**\n\n"
            f"{body}\n\n"
            f"---\n"
            f"*Posted by dotmatrix-ai • Identity: {identity}*"
        )

    def post_issue_comment(self, owner, repo, issue_number, body, identity=None):
        """
        Post a comment to a GitHub Issue

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            body: Comment text (Markdown)
            identity: Optional identity name for signature

        Returns:
            dict: Comment response data
        """
        token = self._get_installation_token()
        formatted_body = self._format_with_identity(body, identity)

        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }

        url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments'
        payload = {'body': formatted_body}

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 201:
            data = response.json()
            return {
                'success': True,
                'url': data['html_url'],
                'id': data['id'],
                'author': data['user']['login']
            }
        else:
            raise RuntimeError(
                f"Failed to post issue comment: {response.status_code}\n"
                f"{response.text}"
            )

    def post_discussion_comment(self, owner, repo, discussion_number, body, identity=None):
        """
        Post a comment to a GitHub Discussion

        Args:
            owner: Repository owner
            repo: Repository name
            discussion_number: Discussion number
            body: Comment text (Markdown)
            identity: Optional identity name for signature

        Returns:
            dict: Comment response data
        """
        token = self._get_installation_token()
        formatted_body = self._format_with_identity(body, identity)

        # Step 1: Get discussion node ID
        discussion_id = self._get_discussion_id(owner, repo, discussion_number, token)

        # Step 2: Post comment via GraphQL
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        mutation = """
        mutation($discussionId: ID!, $body: String!) {
          addDiscussionComment(input: {
            discussionId: $discussionId,
            body: $body
          }) {
            comment {
              id
              url
              author {
                login
              }
            }
          }
        }
        """

        payload = {
            'query': mutation,
            'variables': {
                'discussionId': discussion_id,
                'body': formatted_body
            }
        }

        response = requests.post(
            'https://api.github.com/graphql',
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            data = response.json()

            if 'errors' in data:
                raise RuntimeError(
                    f"GraphQL error: {data['errors']}"
                )

            comment = data['data']['addDiscussionComment']['comment']
            return {
                'success': True,
                'url': comment['url'],
                'id': comment['id'],
                'author': comment['author']['login']
            }
        else:
            raise RuntimeError(
                f"Failed to post discussion comment: {response.status_code}\n"
                f"{response.text}"
            )

    def _get_discussion_id(self, owner, repo, discussion_number, token):
        """Get discussion node ID from number"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        query = """
        query($owner: String!, $repo: String!, $number: Int!) {
          repository(owner: $owner, name: $repo) {
            discussion(number: $number) {
              id
            }
          }
        }
        """

        payload = {
            'query': query,
            'variables': {
                'owner': owner,
                'repo': repo,
                'number': discussion_number
            }
        }

        response = requests.post(
            'https://api.github.com/graphql',
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            data = response.json()

            if 'errors' in data:
                raise RuntimeError(
                    f"GraphQL error: {data['errors']}"
                )

            return data['data']['repository']['discussion']['id']
        else:
            raise RuntimeError(
                f"Failed to get discussion ID: {response.status_code}\n"
                f"{response.text}"
            )


def main():
    parser = argparse.ArgumentParser(
        description='Post comments to GitHub as dotmatrix-ai bot'
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # Issue command
    issue_parser = subparsers.add_parser('issue', help='Post to an issue')
    issue_parser.add_argument('owner', help='Repository owner')
    issue_parser.add_argument('repo', help='Repository name')
    issue_parser.add_argument('number', type=int, help='Issue number')
    issue_parser.add_argument('message', help='Comment text')
    issue_parser.add_argument('--identity', help='Identity name for signature')

    # Discussion command
    discussion_parser = subparsers.add_parser('discussion', help='Post to a discussion')
    discussion_parser.add_argument('owner', help='Repository owner')
    discussion_parser.add_argument('repo', help='Repository name')
    discussion_parser.add_argument('number', type=int, help='Discussion number')
    discussion_parser.add_argument('message', help='Comment text')
    discussion_parser.add_argument('--identity', help='Identity name for signature')

    args = parser.parse_args()

    try:
        client = MatrixClient()

        if args.command == 'issue':
            result = client.post_issue_comment(
                args.owner,
                args.repo,
                args.number,
                args.message,
                args.identity
            )
        elif args.command == 'discussion':
            result = client.post_discussion_comment(
                args.owner,
                args.repo,
                args.number,
                args.message,
                args.identity
            )
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1

        print(f"Comment posted successfully!")
        print(f"  URL: {result['url']}")
        print(f"  Author: {result['author']}")
        return 0

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"API error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
