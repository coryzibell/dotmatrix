#!/usr/bin/env python3
"""
Matrix Setup - Sync agents and CLAUDE.md to Claude Code directory
Detects MATRIX_ROOT and syncs to ~/.claude/
"""

import json
import sys
import shutil
from pathlib import Path


def detect_matrix_root():
    """Detect MATRIX_ROOT: .matrix/ in cwd or ~/.matrix/"""
    cwd_matrix = Path.cwd() / ".matrix"
    home_matrix = Path.home() / ".matrix"
    
    if cwd_matrix.is_dir():
        return cwd_matrix
    elif home_matrix.is_dir():
        return home_matrix
    else:
        print("Error: No .matrix directory found in current directory or home", file=sys.stderr)
        sys.exit(1)


def sync_agents(matrix_root, force=True):
    """Sync agent files from .matrix/agents/ to ~/.claude/agents/"""
    agents_source = matrix_root / "agents"
    agents_target = Path.home() / ".claude" / "agents"
    
    if not agents_source.is_dir():
        print(f"Error: {agents_source} does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Create target directory
    agents_target.mkdir(parents=True, exist_ok=True)
    
    print(f"Syncing agents from {agents_source} to {agents_target}")
    
    # Remove all existing .md files in target if force mode
    if force:
        for existing_file in agents_target.glob("*.md"):
            existing_file.unlink()
            print(f"Removed: {existing_file.name}")
    
    # Copy all agent files
    synced_count = 0
    for agent_file in agents_source.glob("*.md"):
        target_file = agents_target / agent_file.name
        shutil.copy2(agent_file, target_file)
        print(f"Synced: {agent_file.name}")
        synced_count += 1
    
    print(f"Synced {synced_count} agent files")


def sync_claude_md(matrix_root, force=True):
    """Sync CLAUDE.md from .matrix/ to ~/.claude/"""
    claude_source = matrix_root / "CLAUDE.md"
    claude_target = Path.home() / ".claude" / "CLAUDE.md"

    if not claude_source.is_file():
        print(f"Warning: {claude_source} not found, skipping CLAUDE.md sync", file=sys.stderr)
        return

    # Create target directory
    claude_target.parent.mkdir(parents=True, exist_ok=True)

    # Always overwrite if force mode
    if force or not claude_target.exists():
        shutil.copy2(claude_source, claude_target)
        print(f"Synced CLAUDE.md to {claude_target}")
    else:
        print(f"CLAUDE.md already exists at {claude_target}, use --force to overwrite")


def sync_commands(matrix_root, force=True):
    """Sync command files from .matrix/commands/ to ~/.claude/commands/"""
    commands_source = matrix_root / "commands"
    commands_target = Path.home() / ".claude" / "commands"

    if not commands_source.is_dir():
        print(f"No commands directory at {commands_source}, skipping")
        return

    # Create target directory
    commands_target.mkdir(parents=True, exist_ok=True)

    print(f"Syncing commands from {commands_source} to {commands_target}")

    # Remove all existing .md files in target if force mode
    if force:
        for existing_file in commands_target.glob("*.md"):
            existing_file.unlink()
            print(f"Removed: {existing_file.name}")

    # Copy all command files
    synced_count = 0
    for cmd_file in commands_source.glob("*.md"):
        target_file = commands_target / cmd_file.name
        shutil.copy2(cmd_file, target_file)
        print(f"Synced: {cmd_file.name}")
        synced_count += 1

    print(f"Synced {synced_count} command files")


def configure_settings():
    """Configure Claude Code settings in ~/.claude/settings.json"""
    settings_path = Path.home() / ".claude" / "settings.json"

    # Load existing settings or start fresh
    if settings_path.exists():
        try:
            with open(settings_path) as f:
                settings = json.load(f)
        except json.JSONDecodeError:
            settings = {}
    else:
        settings = {}

    # Apply our preferred settings
    settings["includeCoAuthoredBy"] = False
    settings["gitAttribution"] = False

    # Write back
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

    print(f"Configured settings at {settings_path}")


def main():
    """Main setup routine"""
    force = "--force" in sys.argv or len(sys.argv) == 1  # Force by default

    matrix_root = detect_matrix_root()
    print(f"MATRIX_ROOT: {matrix_root}")

    sync_agents(matrix_root, force=force)
    sync_commands(matrix_root, force=force)
    sync_claude_md(matrix_root, force=force)
    configure_settings()

    print(f"\nMatrix setup complete. MATRIX_ROOT={matrix_root}")


if __name__ == "__main__":
    main()
