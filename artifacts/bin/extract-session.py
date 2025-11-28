#!/usr/bin/env python3
"""Extract Claude Code session to readable markdown."""

import json
import sys
from pathlib import Path
from datetime import datetime

def extract_session(jsonl_path: Path, output_path: Path):
    """Extract human/assistant messages from JSONL to markdown."""

    with open(output_path, 'w') as out:
        out.write("# Claude Code Session Export\n\n")
        out.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        out.write(f"**Source:** `{jsonl_path.name}`\n\n")
        out.write("---\n\n")

        with open(jsonl_path) as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

                msg_type = msg.get('type')

                # Human messages
                if msg_type == 'user':
                    content = msg.get('message', {}).get('content', [])

                    # Handle string content directly
                    if isinstance(content, str):
                        text = content.strip()
                        if len(text) > 10 and not text.startswith('<system-reminder>'):
                            out.write(f"## Human\n\n{text}\n\n---\n\n")
                    # Handle list content (tool results, etc)
                    elif isinstance(content, list):
                        text_parts = []
                        has_tool_result = False
                        for block in content:
                            if isinstance(block, dict):
                                if block.get('type') == 'text':
                                    text_parts.append(block.get('text', ''))
                                elif block.get('type') == 'tool_result':
                                    has_tool_result = True

                        if text_parts and not has_tool_result:
                            text = '\n'.join(text_parts)
                            if len(text.strip()) > 10 and not text.startswith('<system-reminder>'):
                                out.write(f"## Human\n\n{text}\n\n---\n\n")

                # Assistant messages
                elif msg_type == 'assistant':
                    content = msg.get('message', {}).get('content', [])
                    text_parts = []
                    tool_uses = []

                    for block in content:
                        if isinstance(block, dict):
                            if block.get('type') == 'text':
                                text_parts.append(block.get('text', ''))
                            elif block.get('type') == 'tool_use':
                                tool_name = block.get('name', 'unknown')
                                tool_input = block.get('input', {})
                                # Summarize tool use
                                if tool_name == 'Edit':
                                    tool_uses.append(f"*Edited `{tool_input.get('file_path', '?')}`*")
                                elif tool_name == 'Write':
                                    tool_uses.append(f"*Wrote `{tool_input.get('file_path', '?')}`*")
                                elif tool_name == 'Read':
                                    tool_uses.append(f"*Read `{tool_input.get('file_path', '?')}`*")
                                elif tool_name == 'Bash':
                                    cmd = tool_input.get('command', '?')[:60]
                                    tool_uses.append(f"*Ran: `{cmd}...`*")
                                elif tool_name == 'Task':
                                    desc = tool_input.get('description', '?')
                                    tool_uses.append(f"*Spawned agent: {desc}*")
                                else:
                                    tool_uses.append(f"*Used {tool_name}*")

                    output_parts = []
                    if text_parts:
                        output_parts.append('\n'.join(text_parts))
                    if tool_uses:
                        output_parts.append('\n'.join(tool_uses))

                    if output_parts:
                        out.write(f"## Assistant\n\n{chr(10).join(output_parts)}\n\n---\n\n")

                # Summary messages (context continuation)
                elif msg_type == 'summary':
                    summary = msg.get('summary', '')
                    if summary:
                        out.write(f"## [Context Summary]\n\n*Session continued from previous conversation:*\n\n{summary[:2000]}...\n\n---\n\n")

    print(f"Exported to {output_path}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Find most recent session
        projects_dir = Path.home() / '.claude' / 'projects' / '-home-w3surf'
        sessions = sorted(projects_dir.glob('*.jsonl'), key=lambda p: p.stat().st_mtime, reverse=True)
        # Filter out agent files
        sessions = [s for s in sessions if not s.name.startswith('agent-')]
        if sessions:
            jsonl_path = sessions[0]
        else:
            print("No session found")
            sys.exit(1)
    else:
        jsonl_path = Path(sys.argv[1])

    output_path = Path.home() / '.claude' / 'cache' / f'session-export-{datetime.now().strftime("%Y%m%d-%H%M")}.md'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    extract_session(jsonl_path, output_path)
