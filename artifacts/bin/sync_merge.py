#!/usr/bin/env python3
"""
sync_merge.py - Three-way merge utilities for GitHub sync operations

Handles conflict detection and resolution when syncing local YAML files with
remote GitHub state. Uses three-way merge logic:
- local: current YAML file state
- remote: current GitHub state
- base: last synced snapshot

Change types:
- local_only: local changed, remote didn't → push local
- remote_only: remote changed, local didn't → keep remote
- both_same: both changed to same value → no conflict
- conflict: both changed differently → needs resolution
- unchanged: neither changed
"""

from typing import Dict, Tuple, Optional, List, Any


def compute_field_changes(local: dict, remote: dict, base: dict, fields: list[str]) -> dict:
    """
    For each field, determine change type using three-way merge logic.

    Args:
        local: Current local YAML state
        remote: Current GitHub state
        base: Last synced snapshot (baseline)
        fields: List of field names to check

    Returns:
        Dict mapping field -> (change_type, local_val, remote_val, base_val)

        change_type is one of:
        - 'local_only': local changed, remote didn't → push local
        - 'remote_only': remote changed, local didn't → keep remote
        - 'both_same': both changed to same value → no conflict
        - 'conflict': both changed differently → needs resolution
        - 'unchanged': neither changed
    """
    changes = {}

    for field in fields:
        local_val = local.get(field)
        remote_val = remote.get(field)
        base_val = base.get(field)

        # Normalize None to empty values based on type
        if local_val is None:
            local_val = [] if isinstance(base_val, list) or isinstance(remote_val, list) else ""
        if remote_val is None:
            remote_val = [] if isinstance(base_val, list) or isinstance(local_val, list) else ""
        if base_val is None:
            base_val = [] if isinstance(local_val, list) else ""

        # Convert lists to sets for comparison (order-independent)
        local_comparable = set(local_val) if isinstance(local_val, list) else local_val
        remote_comparable = set(remote_val) if isinstance(remote_val, list) else remote_val
        base_comparable = set(base_val) if isinstance(base_val, list) else base_val

        local_changed = local_comparable != base_comparable
        remote_changed = remote_comparable != base_comparable

        if not local_changed and not remote_changed:
            change_type = 'unchanged'
        elif local_changed and not remote_changed:
            change_type = 'local_only'
        elif remote_changed and not local_changed:
            change_type = 'remote_only'
        elif local_comparable == remote_comparable:
            # Both changed to the same value
            change_type = 'both_same'
        else:
            # Both changed to different values
            change_type = 'conflict'

        changes[field] = (change_type, local_val, remote_val, base_val)

    return changes


def prompt_conflict_resolution(field: str, local_val: Any, remote_val: Any) -> str:
    """
    Interactive prompt for true conflicts.
    Shows both values, asks user to pick [L]ocal / [R]emote / [S]kip

    Args:
        field: Field name with conflict
        local_val: Local value
        remote_val: Remote value

    Returns:
        'local', 'remote', or 'skip'
    """
    print()
    print(f"  CONFLICT in field '{field}':")
    print(f"    Local:  {repr(local_val)}")
    print(f"    Remote: {repr(remote_val)}")
    print()

    while True:
        response = input("  Choose: [L]ocal / [R]emote / [S]kip this item? ").strip().lower()
        if response in ['l', 'local']:
            return 'local'
        elif response in ['r', 'remote']:
            return 'remote'
        elif response in ['s', 'skip']:
            return 'skip'
        else:
            print("  Invalid choice. Please enter L, R, or S.")


def merge_labels(local_labels: List[str], remote_labels: List[str], base_labels: List[str]) -> List[str]:
    """
    Special merge logic for labels: union of additions, intersection of removals.

    Args:
        local_labels: Current local labels
        remote_labels: Current remote labels
        base_labels: Base snapshot labels

    Returns:
        Merged label list
    """
    local_set = set(local_labels)
    remote_set = set(remote_labels)
    base_set = set(base_labels)

    # Labels added locally
    local_added = local_set - base_set
    # Labels removed locally
    local_removed = base_set - local_set

    # Labels added remotely
    remote_added = remote_set - base_set
    # Labels removed remotely
    remote_removed = base_set - remote_set

    # Start with base
    merged = base_set.copy()

    # Add all additions from both sides (union)
    merged |= local_added
    merged |= remote_added

    # Remove only if removed on BOTH sides (intersection)
    both_removed = local_removed & remote_removed
    merged -= both_removed

    return sorted(list(merged))


def merge_fields(changes: dict, resolutions: dict, interactive: bool = True) -> Tuple[dict, bool]:
    """
    Apply the merge logic based on change types and conflict resolutions.

    Args:
        changes: Dict from compute_field_changes()
        resolutions: Dict mapping field -> resolution ('local', 'remote', 'skip')
        interactive: If True, prompt for conflicts. If False, treat conflicts as skip.

    Returns:
        Tuple of (merged_values, should_skip)
        - merged_values: Dict of field -> merged value
        - should_skip: True if user chose to skip this item entirely
    """
    merged = {}
    should_skip = False

    for field, (change_type, local_val, remote_val, base_val) in changes.items():
        if change_type == 'unchanged':
            merged[field] = local_val
        elif change_type == 'local_only':
            merged[field] = local_val
        elif change_type == 'remote_only':
            merged[field] = remote_val
        elif change_type == 'both_same':
            merged[field] = local_val  # Same as remote
        elif change_type == 'conflict':
            # Need resolution
            if field in resolutions:
                resolution = resolutions[field]
            elif interactive:
                resolution = prompt_conflict_resolution(field, local_val, remote_val)
                resolutions[field] = resolution
            else:
                # Non-interactive mode: treat as skip
                resolution = 'skip'

            if resolution == 'local':
                merged[field] = local_val
            elif resolution == 'remote':
                merged[field] = remote_val
            elif resolution == 'skip':
                should_skip = True
                break  # Stop processing this item

    return merged, should_skip


def print_sync_summary(title: str, changes: dict, resolutions: dict, special_handling: Optional[dict] = None):
    """
    Print readable summary of what's happening in this sync.

    Args:
        title: Item title/name
        changes: Dict from compute_field_changes()
        resolutions: Dict mapping field -> resolution
        special_handling: Optional dict mapping field -> custom message
    """
    print(f"Syncing: {title}")
    print()

    for field, (change_type, local_val, remote_val, base_val) in changes.items():
        if change_type == 'unchanged':
            continue  # Don't print unchanged fields

        # Check for special handling message
        if special_handling and field in special_handling:
            print(f"  {field}: {special_handling[field]}")
            continue

        if change_type == 'local_only':
            print(f"  {field}: Local changed → pushing local")
        elif change_type == 'remote_only':
            print(f"  {field}: Remote changed → keeping remote")
        elif change_type == 'both_same':
            print(f"  {field}: Both changed to same value → no conflict")
        elif change_type == 'conflict':
            resolution = resolutions.get(field, 'unknown')
            if resolution == 'local':
                print(f"  {field}: Conflict resolved → using local")
            elif resolution == 'remote':
                print(f"  {field}: Conflict resolved → using remote")
            elif resolution == 'skip':
                print(f"  {field}: Conflict → skipping item")

    print()


def create_snapshot(title: str, body: str, labels: List[str], updated_at: str, assignees: Optional[List[str]] = None) -> dict:
    """
    Create a snapshot dict for storing in last_synced.

    Args:
        title: Issue/discussion title
        body: Issue/discussion body
        labels: List of label names
        updated_at: GitHub updated_at timestamp
        assignees: Optional list of assignees (issues only)

    Returns:
        Snapshot dict ready for YAML storage
    """
    snapshot = {
        'title': title,
        'body': body,
        'labels': labels,
        'github_updated_at': updated_at
    }

    if assignees is not None:
        snapshot['assignees'] = assignees

    return snapshot


def should_update(local: dict, remote: dict, base: Optional[dict], fields: list[str]) -> bool:
    """
    Quick check: should we even attempt an update?

    Returns False if local and remote are identical (no update needed).
    Returns True if there are any differences.

    Args:
        local: Current local state
        remote: Current remote state
        base: Last synced snapshot (can be None)
        fields: Fields to check

    Returns:
        True if update needed, False otherwise
    """
    for field in fields:
        local_val = local.get(field)
        remote_val = remote.get(field)

        # Normalize None
        if local_val is None:
            local_val = [] if isinstance(remote_val, list) else ""
        if remote_val is None:
            remote_val = [] if isinstance(local_val, list) else ""

        # Compare
        local_comparable = set(local_val) if isinstance(local_val, list) else local_val
        remote_comparable = set(remote_val) if isinstance(remote_val, list) else remote_val

        if local_comparable != remote_comparable:
            return True

    return False
