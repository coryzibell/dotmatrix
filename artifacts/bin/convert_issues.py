#!/usr/bin/env python3
"""
md2yaml.py - Convert issue markdown files to YAML format

Reads structured markdown issue files and converts them to machine-readable YAML
format suitable for GitHub API consumption.

Usage:
    python md2yaml.py <input-dir> [output-dir]

Example:
    python md2yaml.py ~/.matrix/cache/construct/matrix/issues/
    python md2yaml.py ./issues ./output

If output-dir not specified, YAML files are written alongside the markdown files.
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def extract_title(content: str, filename: str) -> str:
    """
    Extract title from first # heading or fallback to filename.

    Returns:
        Title string without the # prefix
    """
    # Find first # heading (single hash, not ##)
    match = re.search(r'^#\s+([^#].+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    # Fallback to filename without extension
    return Path(filename).stem.replace('-', ' ').replace('_', ' ').title()


def extract_type(content: str) -> str:
    """
    Extract type from **Type:** line.

    Format: **Type:** `issue` or **Type:** `idea` or **Type:** `discussion`

    Returns:
        Type string ("issue" or "idea"), defaults to "issue" if not found
        Note: "discussion" is treated as "idea" for GitHub Discussions
    """
    match = re.search(r'\*\*Type:\*\*\s+`([^`]+)`', content, re.MULTILINE)
    if match:
        type_value = match.group(1).strip().lower()
        if type_value in ['issue', 'idea']:
            return type_value
        if type_value == 'discussion':
            return 'idea'
    return 'issue'


def extract_labels(content: str) -> List[str]:
    """
    Extract labels from **Labels:** line.

    Format: **Labels:** `label1`, `label2`, `label3`

    Returns:
        List of label strings without backticks
    """
    match = re.search(r'\*\*Labels:\*\*\s+(.+)$', content, re.MULTILINE)
    if not match:
        return []

    labels_line = match.group(1)
    # Extract text within backticks
    labels = re.findall(r'`([^`]+)`', labels_line)
    return [label.strip() for label in labels]


def parse_section(content: str, heading: str) -> str:
    """
    Extract content of a section by heading.

    Captures everything from ### {heading} until the next ### or end of content.

    Returns:
        Section content (empty string if section not found)
    """
    # Match from ### heading to next ### or end
    pattern = rf'^###\s+{re.escape(heading)}\s*$(.+?)(?=^###\s+|\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if match:
        return match.group(1).strip()

    return ""


def parse_implementation_steps(section_text: str) -> List[Dict[str, any]]:
    """
    Parse numbered implementation steps.

    Format:
        1. First step
        2. Second step

    Returns:
        List of dicts with step number and action
    """
    if not section_text:
        return []

    steps = []
    # Match numbered lines like "1. Action"
    for match in re.finditer(r'^\s*(\d+)\.\s+(.+)$', section_text, re.MULTILINE):
        step_num = int(match.group(1))
        action = match.group(2).strip()
        steps.append({
            'step': step_num,
            'action': action
        })

    return steps


def parse_acceptance_criteria(section_text: str) -> List[Dict[str, any]]:
    """
    Parse acceptance criteria checkboxes.

    Format:
        - [ ] Unchecked criterion
        - [x] Checked criterion

    Returns:
        List of dicts with checked status and criterion text
    """
    if not section_text:
        return []

    criteria = []
    # Match checkbox lines
    for match in re.finditer(r'^\s*-\s+\[([ x])\]\s+(.+)$', section_text, re.MULTILINE):
        checked = match.group(1).lower() == 'x'
        criterion = match.group(2).strip()
        criteria.append({
            'checked': checked,
            'criterion': criterion
        })

    return criteria


def parse_handoff_workflow(section_text: str) -> List[Dict[str, any]]:
    """
    Parse handoff workflow steps.

    Handles two formats:
    1. Numbered list with identity mentions:
       "1. Deus verifies with security-focused tests"
    2. After {identity} pattern:
       "After Smith implements:"

    Returns:
        List of dicts with step number, identity (if detectable), and action
    """
    if not section_text:
        return []

    workflow = []
    step_num = 0

    # Known identities for detection
    identities = [
        'smith', 'trinity', 'morpheus', 'oracle', 'architect', 'cypher',
        'niobe', 'keymaker', 'merovingian', 'librarian', 'twins', 'trainman',
        'deus', 'hamann', 'spoon', 'sati', 'ramakandra', 'persephone',
        'lock', 'zee', 'mouse', 'apoc', 'switch', 'neo', 'seraph', 'tank'
    ]

    # Match numbered lines
    for match in re.finditer(r'^\s*(\d+)\.\s+(.+)$', section_text, re.MULTILINE):
        step_num = int(match.group(1))
        action_text = match.group(2).strip()

        # Try to extract identity from action text
        identity = None
        for ident in identities:
            # Case-insensitive match for identity name
            if re.search(rf'\b{ident}\b', action_text, re.IGNORECASE):
                identity = ident.lower()
                break

        workflow.append({
            'step': step_num,
            'identity': identity,
            'action': action_text
        })

    return workflow


def generate_body_markdown(content: str) -> str:
    """
    Generate the body_markdown field for GitHub rendering.

    Extracts everything after the title, type, and labels, preserving all sections.

    Returns:
        Cleaned markdown content for GitHub issue body
    """
    # Remove the title line (first ## heading)
    content = re.sub(r'^##\s+.+$', '', content, count=1, flags=re.MULTILINE)

    # Remove the type line
    content = re.sub(r'\*\*Type:\*\*\s+.+$', '', content, flags=re.MULTILINE)

    # Remove the labels line
    content = re.sub(r'\*\*Labels:\*\*\s+.+$', '', content, flags=re.MULTILINE)

    # Remove leading/trailing whitespace
    content = content.strip()

    return content


def markdown_to_yaml(md_content: str, filename: str) -> str:
    """
    Convert markdown issue content to YAML format.

    Args:
        md_content: Full markdown content
        filename: Original filename (for title fallback)

    Returns:
        YAML formatted string
    """
    # Extract components
    title = extract_title(md_content, filename)
    issue_type = extract_type(md_content)
    labels = extract_labels(md_content)

    # Extract sections
    context = parse_section(md_content, 'Context')
    problem = parse_section(md_content, 'Problem')
    solution = parse_section(md_content, 'Solution')
    implementation_text = parse_section(md_content, 'Implementation Steps')
    acceptance_text = parse_section(md_content, 'Acceptance Criteria')
    handoff_text = parse_section(md_content, 'Handoff')

    # Parse structured sections
    implementation_steps = parse_implementation_steps(implementation_text)
    acceptance_criteria = parse_acceptance_criteria(acceptance_text)
    handoff_workflow = parse_handoff_workflow(handoff_text)

    # Generate body markdown
    body_markdown = generate_body_markdown(md_content)

    # Build YAML structure
    yaml_lines = [
        "# GitHub Issue (YAML)",
        "# Auto-generated from markdown by md2yaml.py",
        "",
        "metadata:",
        f'  title: "{title}"',
        f'  type: "{issue_type}"'
    ]

    # Add labels
    if labels:
        yaml_lines.append("  labels:")
        for label in labels:
            yaml_lines.append(f'    - "{label}"')
    else:
        yaml_lines.append("  labels: []")

    yaml_lines.extend([
        "  assignees: []",
        "  milestone: null",
        ""
    ])

    # Add context section
    if context:
        yaml_lines.append("context:")
        # Indent each line with 2 spaces, escape quotes
        for line in context.split('\n'):
            if line.strip():
                escaped = line.replace('"', '\\"')
                yaml_lines.append(f'  {escaped}')
        yaml_lines.append("")

    # Add problem section
    if problem:
        yaml_lines.append("problem:")
        yaml_lines.append('  description: |')
        for line in problem.split('\n'):
            yaml_lines.append(f'    {line}')
        yaml_lines.append("")

    # Add solution section
    if solution:
        yaml_lines.append("solution:")
        yaml_lines.append('  description: |')
        for line in solution.split('\n'):
            yaml_lines.append(f'    {line}')
        yaml_lines.append("")

    # Add implementation steps
    if implementation_steps:
        yaml_lines.append("implementation:")
        yaml_lines.append("  steps:")
        for step in implementation_steps:
            yaml_lines.append(f"    - step: {step['step']}")
            action = step['action'].replace('"', '\\"')
            yaml_lines.append(f'      action: "{action}"')
        yaml_lines.append("")

    # Add acceptance criteria
    if acceptance_criteria:
        if 'implementation:' not in '\n'.join(yaml_lines):
            yaml_lines.append("implementation:")
        yaml_lines.append("  acceptance_criteria:")
        for criterion in acceptance_criteria:
            yaml_lines.append(f"    - checked: {str(criterion['checked']).lower()}")
            text = criterion['criterion'].replace('"', '\\"')
            yaml_lines.append(f'      criterion: "{text}"')
        yaml_lines.append("")

    # Add handoff workflow
    if handoff_workflow:
        yaml_lines.append("handoff:")
        yaml_lines.append("  workflow:")
        for item in handoff_workflow:
            yaml_lines.append(f"    - step: {item['step']}")
            if item['identity']:
                yaml_lines.append(f"      identity: \"{item['identity']}\"")
            action = item['action'].replace('"', '\\"')
            yaml_lines.append(f'      action: "{action}"')
        yaml_lines.append("")

    # Add body markdown
    yaml_lines.extend([
        "# GitHub Issue Body (Markdown for rendering)",
        "body_markdown: |"
    ])
    for line in body_markdown.split('\n'):
        yaml_lines.append(f'  {line}')

    return '\n'.join(yaml_lines)


def convert_file(md_path: Path, output_dir: Path) -> Tuple[bool, str]:
    """
    Convert a single markdown file to YAML.

    Args:
        md_path: Path to markdown file
        output_dir: Directory for output YAML file

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Read markdown content
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Convert to YAML
        yaml_content = markdown_to_yaml(md_content, md_path.name)

        # Generate output path
        yaml_filename = md_path.stem + '.yaml'
        yaml_path = output_dir / yaml_filename

        # Write YAML file
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        return True, f"Converted: {md_path.name} → {yaml_path}"

    except Exception as e:
        return False, f"Failed to convert {md_path.name}: {e}"


def main():
    # Parse arguments
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python md2yaml.py <input-dir> [output-dir]")
        print()
        print("Example:")
        print("  python md2yaml.py ~/.matrix/cache/construct/matrix/issues/")
        print("  python md2yaml.py ./issues ./output")
        print()
        print("If output-dir not specified, YAML files are written alongside markdown files.")
        sys.exit(1)

    input_dir = Path(sys.argv[1]).expanduser().resolve()

    if len(sys.argv) == 3:
        output_dir = Path(sys.argv[2]).expanduser().resolve()
    else:
        output_dir = input_dir

    # Validate input directory
    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}")
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"Error: Input path is not a directory: {input_dir}")
        sys.exit(1)

    # Create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all markdown files
    md_files = sorted(input_dir.glob('*.md'))

    if not md_files:
        print(f"No markdown files found in {input_dir}")
        sys.exit(0)

    print(f"Found {len(md_files)} markdown file(s) in {input_dir}")
    print(f"Output directory: {output_dir}")
    print()

    # Convert each file
    success_count = 0
    failure_count = 0

    for md_path in md_files:
        success, message = convert_file(md_path, output_dir)
        print(message)

        if success:
            success_count += 1
        else:
            failure_count += 1

    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Success: {success_count}")
    print(f"Failed:  {failure_count}")
    print()

    if failure_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
