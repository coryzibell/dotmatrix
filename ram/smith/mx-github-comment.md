# mx github comment - Implementation Summary

## Task
Implemented `mx github comment` subcommand for posting comments to GitHub issues and discussions using dotmatrix-ai GitHub App authentication.

## Changes Made

### 1. src/main.rs
- Added `CommentCommands` enum with `Issue` and `Discussion` subcommands
- Extended `GithubCommands` enum with `Comment` variant
- Added `handle_comment()` function to route comment commands

**CLI Structure:**
```bash
mx github comment issue <repo> <number> <message> [--identity NAME]
mx github comment discussion <repo> <number> <message> [--identity NAME]
```

### 2. src/github.rs
- Added `format_comment_body()` - formats message with optional identity signature
- Added `post_issue_comment()` - posts comment to issue via REST API
- Added `post_discussion_comment()` - posts comment to discussion via GraphQL
- Added REST helper `create_issue_comment()` with types:
  - `CreateCommentRequest` (request)
  - `IssueComment` (response)
- Added GraphQL helper `add_discussion_comment()`
- Uses `get_installation_token()` for GitHub App authentication

**Identity Signature Format:**
```markdown
**[smith]**

Your message here

---
*Posted by dotmatrix-ai • Identity: smith*
```

### 3. src/sync/github/rest.rs
- Added `post_json<T, R>()` method - generic POST request with JSON body
- Used by issue comment creation

### 4. src/sync/github/graphql.rs
- Added `add_discussion_comment()` method
- Added response types:
  - `AddDiscussionCommentResponse`
  - `AddDiscussionCommentPayload`
  - `DiscussionCommentCreated` (public, contains id and url)

**GraphQL Mutation:**
```graphql
mutation($discussionId: ID!, $body: String!) {
  addDiscussionComment(input: {discussionId: $discussionId, body: $body}) {
    comment {
      id
      url
    }
  }
}
```

## API Usage

### Issue Comments (REST)
```
POST /repos/{owner}/{repo}/issues/{number}/comments
Body: {"body": "comment text"}
Response: {"html_url": "https://github.com/..."}
```

### Discussion Comments (GraphQL)
1. Get discussion ID from number (existing `get_discussion_id()`)
2. Call `addDiscussionComment` mutation
3. Returns comment with `id` and `url`

## Authentication
Uses GitHub App installation token via `sync::github::app_auth::get_installation_token()`:
- Reads `DOTMATRIX_APP_ID`, `DOTMATRIX_INSTALLATION_ID`, `DOTMATRIX_PRIVATE_KEY`
- Generates JWT, exchanges for installation token
- Token cached with 5-minute expiry buffer

## Build Verification
```bash
cargo build  # Success with warnings (unused imports/fields only)
mx github comment --help  # CLI verified
mx github comment issue --help  # Arguments correct
mx github comment discussion --help  # Arguments correct
```

## Example Usage
```bash
# Simple comment
mx github comment issue coryzibell/mx 42 "This looks good!"

# With identity signature
mx github comment discussion coryzibell/mx 5 "Implementation complete" --identity smith

# Output
Comment posted: https://github.com/coryzibell/mx/issues/42#issuecomment-12345
```

## Files Modified
- `/home/w3surf/work/personal/code/mx/src/main.rs` (CLI structure)
- `/home/w3surf/work/personal/code/mx/src/github.rs` (comment logic)
- `/home/w3surf/work/personal/code/mx/src/sync/github/rest.rs` (REST client extension)
- `/home/w3surf/work/personal/code/mx/src/sync/github/graphql.rs` (GraphQL client extension)

## Status
Complete. Command implemented, builds successfully, CLI verified.
