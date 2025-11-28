# Adapt existing Rust repos to template CI

## Context
Created `rust-template` with Matrix-themed CI workflows. Need to backport to existing repos.

## Repos to update
- `base-d` - has older CI, needs the new workflows
- `mx` - already has the new workflows (source of truth)
- Any other Rust repos

## Changes needed per repo
1. Replace `.github/workflows/` with template versions:
   - `wake-up.yml`
   - `the-matrix-has-you.yml`
   - `follow-the-white-rabbit.yml`
   - `knock-knock.yml`

2. Remove old workflow files (if different names)

3. Ensure secrets are set:
   - `PAT_TOKEN` - for tag creation
   - `CARGO_REGISTRY_TOKEN` - for crates.io publish

## Approach
Could script this or do manually per repo. Low priority - works as-is, just not unified.

## Priority
Low - do when touching each repo anyway, or batch when bored.
