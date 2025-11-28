#!/usr/bin/env python3
"""
test_sync_merge.py - Tests for three-way merge logic

Critical tests for sync_merge.py to prevent data loss from wrong merge decisions.
"""

import pytest
from sync_merge import (
    compute_field_changes,
    merge_labels,
    merge_fields,
    should_update,
    create_snapshot,
)


# ============================================================================
# compute_field_changes() - Priority 1
# ============================================================================

class TestComputeFieldChanges:
    """Test all change type combinations in compute_field_changes()"""

    def test_unchanged_string_field(self):
        """Unchanged: neither local nor remote changed from base"""
        local = {"title": "Original Title"}
        remote = {"title": "Original Title"}
        base = {"title": "Original Title"}

        changes = compute_field_changes(local, remote, base, ["title"])

        assert changes["title"][0] == "unchanged"
        assert changes["title"][1] == "Original Title"  # local_val
        assert changes["title"][2] == "Original Title"  # remote_val
        assert changes["title"][3] == "Original Title"  # base_val

    def test_local_only_change_string(self):
        """Local only: local changed, remote stayed same"""
        local = {"title": "New Local Title"}
        remote = {"title": "Original Title"}
        base = {"title": "Original Title"}

        changes = compute_field_changes(local, remote, base, ["title"])

        assert changes["title"][0] == "local_only"
        assert changes["title"][1] == "New Local Title"
        assert changes["title"][2] == "Original Title"

    def test_remote_only_change_string(self):
        """Remote only: remote changed, local stayed same"""
        local = {"title": "Original Title"}
        remote = {"title": "New Remote Title"}
        base = {"title": "Original Title"}

        changes = compute_field_changes(local, remote, base, ["title"])

        assert changes["title"][0] == "remote_only"
        assert changes["title"][1] == "Original Title"
        assert changes["title"][2] == "New Remote Title"

    def test_both_same_change_string(self):
        """Both same: both changed to identical value"""
        local = {"title": "Same New Title"}
        remote = {"title": "Same New Title"}
        base = {"title": "Original Title"}

        changes = compute_field_changes(local, remote, base, ["title"])

        assert changes["title"][0] == "both_same"
        assert changes["title"][1] == "Same New Title"
        assert changes["title"][2] == "Same New Title"

    def test_conflict_string(self):
        """Conflict: both changed to different values"""
        local = {"title": "Local Title"}
        remote = {"title": "Remote Title"}
        base = {"title": "Original Title"}

        changes = compute_field_changes(local, remote, base, ["title"])

        assert changes["title"][0] == "conflict"
        assert changes["title"][1] == "Local Title"
        assert changes["title"][2] == "Remote Title"

    def test_unchanged_list_field(self):
        """Unchanged: list fields with same content"""
        local = {"labels": ["bug", "priority"]}
        remote = {"labels": ["priority", "bug"]}  # Order doesn't matter
        base = {"labels": ["bug", "priority"]}

        changes = compute_field_changes(local, remote, base, ["labels"])

        assert changes["labels"][0] == "unchanged"

    def test_local_only_change_list(self):
        """Local only: added label locally"""
        local = {"labels": ["bug", "priority", "urgent"]}
        remote = {"labels": ["bug", "priority"]}
        base = {"labels": ["bug", "priority"]}

        changes = compute_field_changes(local, remote, base, ["labels"])

        assert changes["labels"][0] == "local_only"

    def test_remote_only_change_list(self):
        """Remote only: removed label remotely"""
        local = {"labels": ["bug", "priority"]}
        remote = {"labels": ["bug"]}
        base = {"labels": ["bug", "priority"]}

        changes = compute_field_changes(local, remote, base, ["labels"])

        assert changes["labels"][0] == "remote_only"

    def test_both_same_change_list(self):
        """Both same: both added same label"""
        local = {"labels": ["bug", "priority", "urgent"]}
        remote = {"labels": ["urgent", "bug", "priority"]}  # Different order
        base = {"labels": ["bug", "priority"]}

        changes = compute_field_changes(local, remote, base, ["labels"])

        assert changes["labels"][0] == "both_same"

    def test_conflict_list(self):
        """Conflict: different additions to list"""
        local = {"labels": ["bug", "priority", "local-tag"]}
        remote = {"labels": ["bug", "priority", "remote-tag"]}
        base = {"labels": ["bug", "priority"]}

        changes = compute_field_changes(local, remote, base, ["labels"])

        assert changes["labels"][0] == "conflict"

    def test_none_normalization_to_empty_string(self):
        """Edge: None should normalize to empty string for string fields"""
        local = {"body": None}
        remote = {"body": ""}
        base = {"body": ""}

        changes = compute_field_changes(local, remote, base, ["body"])

        # None -> "" so should be unchanged
        assert changes["body"][0] == "unchanged"
        assert changes["body"][1] == ""  # local_val normalized

    def test_none_normalization_to_empty_list(self):
        """Edge: None should normalize to empty list for list fields"""
        local = {"labels": None}
        remote = {"labels": []}
        base = {"labels": []}

        changes = compute_field_changes(local, remote, base, ["labels"])

        assert changes["labels"][0] == "unchanged"
        assert changes["labels"][1] == []

    def test_none_base_infers_type_from_local(self):
        """Edge: When base is None, infer type from local"""
        local = {"labels": ["bug"]}
        remote = {"labels": ["bug"]}
        base = {"labels": None}

        changes = compute_field_changes(local, remote, base, ["labels"])

        # Base None -> [] because local is list
        assert changes["labels"][3] == []  # base_val

    def test_none_base_infers_type_from_remote(self):
        """Edge: When base and local are None, infer from remote"""
        local = {"labels": None}
        remote = {"labels": ["bug"]}
        base = {"labels": None}

        changes = compute_field_changes(local, remote, base, ["labels"])

        # All should be lists
        assert isinstance(changes["labels"][1], list)  # local_val
        assert isinstance(changes["labels"][2], list)  # remote_val
        assert isinstance(changes["labels"][3], list)  # base_val

    def test_multiple_fields(self):
        """Multiple fields in one call"""
        local = {"title": "New Title", "body": "Same Body", "labels": ["bug"]}
        remote = {"title": "Original Title", "body": "Same Body", "labels": ["bug", "urgent"]}
        base = {"title": "Original Title", "body": "Old Body", "labels": ["bug"]}

        changes = compute_field_changes(local, remote, base, ["title", "body", "labels"])

        assert changes["title"][0] == "local_only"
        assert changes["body"][0] == "both_same"
        assert changes["labels"][0] == "remote_only"

    def test_deeply_nested_not_supported(self):
        """Edge: Deeply nested structures are treated as values (not deep-merged)"""
        local = {"data": {"nested": {"key": "local_value"}}}
        remote = {"data": {"nested": {"key": "remote_value"}}}
        base = {"data": {"nested": {"key": "base_value"}}}

        # Since we're comparing dicts directly, they'll all differ
        changes = compute_field_changes(local, remote, base, ["data"])

        # Different dict objects = conflict
        assert changes["data"][0] == "conflict"


# ============================================================================
# merge_labels() - Priority 1
# ============================================================================

class TestMergeLabels:
    """Test union of additions, intersection of removals"""

    def test_no_changes(self):
        """No changes to labels"""
        result = merge_labels(
            local_labels=["bug", "priority"],
            remote_labels=["bug", "priority"],
            base_labels=["bug", "priority"]
        )

        assert set(result) == {"bug", "priority"}

    def test_local_addition_only(self):
        """Local added a label, remote unchanged"""
        result = merge_labels(
            local_labels=["bug", "priority", "urgent"],
            remote_labels=["bug", "priority"],
            base_labels=["bug", "priority"]
        )

        assert set(result) == {"bug", "priority", "urgent"}

    def test_remote_addition_only(self):
        """Remote added a label, local unchanged"""
        result = merge_labels(
            local_labels=["bug", "priority"],
            remote_labels=["bug", "priority", "enhancement"],
            base_labels=["bug", "priority"]
        )

        assert set(result) == {"bug", "priority", "enhancement"}

    def test_both_add_different_labels(self):
        """Union: both sides added different labels"""
        result = merge_labels(
            local_labels=["bug", "priority", "local-tag"],
            remote_labels=["bug", "priority", "remote-tag"],
            base_labels=["bug", "priority"]
        )

        # Union of additions
        assert set(result) == {"bug", "priority", "local-tag", "remote-tag"}

    def test_both_add_same_label(self):
        """Union: both sides added same label (no duplicate)"""
        result = merge_labels(
            local_labels=["bug", "priority", "urgent"],
            remote_labels=["bug", "priority", "urgent"],
            base_labels=["bug", "priority"]
        )

        assert set(result) == {"bug", "priority", "urgent"}

    def test_local_removal_only(self):
        """Local removed label, remote unchanged → label stays"""
        result = merge_labels(
            local_labels=["bug"],
            remote_labels=["bug", "priority"],
            base_labels=["bug", "priority"]
        )

        # Only removed on local side, not both → stays
        assert set(result) == {"bug", "priority"}

    def test_remote_removal_only(self):
        """Remote removed label, local unchanged → label stays"""
        result = merge_labels(
            local_labels=["bug", "priority"],
            remote_labels=["bug"],
            base_labels=["bug", "priority"]
        )

        # Only removed on remote side, not both → stays
        assert set(result) == {"bug", "priority"}

    def test_both_remove_same_label(self):
        """Intersection: both sides removed same label → actually remove it"""
        result = merge_labels(
            local_labels=["bug"],
            remote_labels=["bug"],
            base_labels=["bug", "priority"]
        )

        # Removed on both sides → actually removed
        assert set(result) == {"bug"}

    def test_both_remove_different_labels(self):
        """Intersection: both removed different labels → both stay"""
        result = merge_labels(
            local_labels=["bug", "priority"],
            remote_labels=["bug", "urgent"],
            base_labels=["bug", "priority", "urgent"]
        )

        # Local removed "urgent", remote removed "priority"
        # Neither removed on BOTH sides → both stay
        assert set(result) == {"bug", "priority", "urgent"}

    def test_empty_base_all_additions(self):
        """Edge: empty base, all are additions"""
        result = merge_labels(
            local_labels=["local-tag"],
            remote_labels=["remote-tag"],
            base_labels=[]
        )

        # Union of all additions
        assert set(result) == {"local-tag", "remote-tag"}

    def test_empty_local_and_remote(self):
        """Edge: everything removed on both sides"""
        result = merge_labels(
            local_labels=[],
            remote_labels=[],
            base_labels=["bug", "priority"]
        )

        # Both removed everything → actually remove
        assert result == []

    def test_result_is_sorted(self):
        """Result should be sorted alphabetically"""
        result = merge_labels(
            local_labels=["zebra", "alpha"],
            remote_labels=["beta"],
            base_labels=[]
        )

        assert result == ["alpha", "beta", "zebra"]


# ============================================================================
# merge_fields() - Priority 1
# ============================================================================

class TestMergeFields:
    """Test conflict resolution paths in merge_fields()"""

    def test_unchanged_field(self):
        """Unchanged field uses local value"""
        changes = {
            "title": ("unchanged", "Same Title", "Same Title", "Same Title")
        }

        merged, should_skip = merge_fields(changes, {}, interactive=False)

        assert merged["title"] == "Same Title"
        assert should_skip is False

    def test_local_only_uses_local(self):
        """Local-only change uses local value"""
        changes = {
            "title": ("local_only", "Local Title", "Base Title", "Base Title")
        }

        merged, should_skip = merge_fields(changes, {}, interactive=False)

        assert merged["title"] == "Local Title"
        assert should_skip is False

    def test_remote_only_uses_remote(self):
        """Remote-only change uses remote value"""
        changes = {
            "title": ("remote_only", "Base Title", "Remote Title", "Base Title")
        }

        merged, should_skip = merge_fields(changes, {}, interactive=False)

        assert merged["title"] == "Remote Title"
        assert should_skip is False

    def test_both_same_uses_either(self):
        """Both-same change uses either value (they're identical)"""
        changes = {
            "title": ("both_same", "Same New", "Same New", "Base Title")
        }

        merged, should_skip = merge_fields(changes, {}, interactive=False)

        assert merged["title"] == "Same New"
        assert should_skip is False

    def test_conflict_with_preexisting_resolution_local(self):
        """Conflict resolved via pre-existing resolution: local"""
        changes = {
            "title": ("conflict", "Local Title", "Remote Title", "Base Title")
        }
        resolutions = {"title": "local"}

        merged, should_skip = merge_fields(changes, resolutions, interactive=False)

        assert merged["title"] == "Local Title"
        assert should_skip is False

    def test_conflict_with_preexisting_resolution_remote(self):
        """Conflict resolved via pre-existing resolution: remote"""
        changes = {
            "title": ("conflict", "Local Title", "Remote Title", "Base Title")
        }
        resolutions = {"title": "remote"}

        merged, should_skip = merge_fields(changes, resolutions, interactive=False)

        assert merged["title"] == "Remote Title"
        assert should_skip is False

    def test_conflict_with_preexisting_resolution_skip(self):
        """Conflict resolved via pre-existing resolution: skip"""
        changes = {
            "title": ("conflict", "Local Title", "Remote Title", "Base Title")
        }
        resolutions = {"title": "skip"}

        merged, should_skip = merge_fields(changes, resolutions, interactive=False)

        # Should break early, merged may be incomplete
        assert should_skip is True

    def test_conflict_non_interactive_treats_as_skip(self):
        """Non-interactive mode with unresolved conflict → skip"""
        changes = {
            "title": ("conflict", "Local Title", "Remote Title", "Base Title")
        }

        merged, should_skip = merge_fields(changes, {}, interactive=False)

        assert should_skip is True

    def test_multiple_fields_stop_on_skip(self):
        """Multiple fields: stop processing when skip encountered"""
        changes = {
            "title": ("local_only", "Local Title", "Base", "Base"),
            "body": ("conflict", "Local Body", "Remote Body", "Base"),
            "labels": ("remote_only", ["base"], ["remote"], ["base"])
        }
        resolutions = {"body": "skip"}

        merged, should_skip = merge_fields(changes, resolutions, interactive=False)

        # Should have processed title before hitting skip
        assert "title" in merged
        assert merged["title"] == "Local Title"

        # But should NOT have processed labels after skip
        assert "labels" not in merged
        assert should_skip is True

    def test_all_change_types_together(self):
        """All change types in one merge"""
        changes = {
            "unchanged": ("unchanged", "Same", "Same", "Same"),
            "local_only": ("local_only", "Local", "Base", "Base"),
            "remote_only": ("remote_only", "Base", "Remote", "Base"),
            "both_same": ("both_same", "New", "New", "Old"),
            "conflict_local": ("conflict", "L", "R", "Base"),
            "conflict_remote": ("conflict", "L2", "R2", "Base2"),
        }
        resolutions = {
            "conflict_local": "local",
            "conflict_remote": "remote"
        }

        merged, should_skip = merge_fields(changes, resolutions, interactive=False)

        assert merged["unchanged"] == "Same"
        assert merged["local_only"] == "Local"
        assert merged["remote_only"] == "Remote"
        assert merged["both_same"] == "New"
        assert merged["conflict_local"] == "L"
        assert merged["conflict_remote"] == "R2"
        assert should_skip is False


# ============================================================================
# should_update() - Helper function
# ============================================================================

class TestShouldUpdate:
    """Test quick update check logic"""

    def test_identical_no_update_needed(self):
        """Local and remote identical → no update"""
        local = {"title": "Same", "labels": ["bug"]}
        remote = {"title": "Same", "labels": ["bug"]}
        base = {"title": "Old", "labels": []}

        assert should_update(local, remote, base, ["title", "labels"]) is False

    def test_string_difference_needs_update(self):
        """String field differs → update needed"""
        local = {"title": "Local"}
        remote = {"title": "Remote"}
        base = {}

        assert should_update(local, remote, base, ["title"]) is True

    def test_list_difference_needs_update(self):
        """List field differs → update needed"""
        local = {"labels": ["bug"]}
        remote = {"labels": ["bug", "urgent"]}
        base = {}

        assert should_update(local, remote, base, ["labels"]) is True

    def test_list_order_independent(self):
        """List order doesn't matter"""
        local = {"labels": ["bug", "priority"]}
        remote = {"labels": ["priority", "bug"]}
        base = {}

        assert should_update(local, remote, base, ["labels"]) is False

    def test_none_normalization(self):
        """None normalized properly"""
        local = {"body": None}
        remote = {"body": ""}
        base = {}

        # None -> "" so they're identical
        assert should_update(local, remote, base, ["body"]) is False


# ============================================================================
# create_snapshot() - Helper function
# ============================================================================

class TestCreateSnapshot:
    """Test snapshot creation"""

    def test_basic_snapshot(self):
        """Basic snapshot without assignees"""
        snapshot = create_snapshot(
            title="Test Issue",
            body="Test body",
            labels=["bug", "priority"],
            updated_at="2025-01-01T00:00:00Z"
        )

        assert snapshot["title"] == "Test Issue"
        assert snapshot["body"] == "Test body"
        assert snapshot["labels"] == ["bug", "priority"]
        assert snapshot["github_updated_at"] == "2025-01-01T00:00:00Z"
        assert "assignees" not in snapshot

    def test_snapshot_with_assignees(self):
        """Snapshot with assignees (issues only)"""
        snapshot = create_snapshot(
            title="Test Issue",
            body="Test body",
            labels=["bug"],
            updated_at="2025-01-01T00:00:00Z",
            assignees=["user1", "user2"]
        )

        assert snapshot["assignees"] == ["user1", "user2"]

    def test_snapshot_empty_assignees(self):
        """Snapshot with empty assignees list"""
        snapshot = create_snapshot(
            title="Test",
            body="",
            labels=[],
            updated_at="2025-01-01T00:00:00Z",
            assignees=[]
        )

        assert snapshot["assignees"] == []


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_string_vs_none_in_body(self):
        """Empty string and None should be treated the same"""
        local = {"body": ""}
        remote = {"body": None}
        base = {"body": ""}

        changes = compute_field_changes(local, remote, base, ["body"])

        # Both normalize to "" → unchanged
        assert changes["body"][0] == "unchanged"

    def test_empty_list_vs_none_in_labels(self):
        """Empty list and None should be treated the same"""
        local = {"labels": []}
        remote = {"labels": None}
        base = {"labels": []}

        changes = compute_field_changes(local, remote, base, ["labels"])

        # Both normalize to [] → unchanged
        assert changes["labels"][0] == "unchanged"

    def test_missing_field_in_local(self):
        """Missing field treated as None → conflict when base also has value"""
        local = {}  # Missing "title"
        remote = {"title": "Remote"}
        base = {"title": "Base"}

        changes = compute_field_changes(local, remote, base, ["title"])

        # local missing → None → ""
        # local changed from "Base" to "", remote changed to "Remote" → conflict
        assert changes["title"][0] == "conflict"
        assert changes["title"][1] == ""  # local normalized to empty string

    def test_all_missing_field(self):
        """All three missing the field"""
        local = {}
        remote = {}
        base = {}

        changes = compute_field_changes(local, remote, base, ["title"])

        # All None → all "" → unchanged
        assert changes["title"][0] == "unchanged"

    def test_missing_base_both_have_same_value(self):
        """Base missing, both local and remote have same value"""
        local = {"title": "Same"}
        remote = {"title": "Same"}
        base = {}  # Missing base

        changes = compute_field_changes(local, remote, base, ["title"])

        # Base "" → both changed to "Same" → both_same
        assert changes["title"][0] == "both_same"

    def test_missing_base_different_values(self):
        """Base missing, local and remote have different values"""
        local = {"title": "Local"}
        remote = {"title": "Remote"}
        base = {}  # Missing base

        changes = compute_field_changes(local, remote, base, ["title"])

        # Base "" → both changed to different values → conflict
        assert changes["title"][0] == "conflict"
