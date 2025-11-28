#!/usr/bin/env python3
"""
Upload commit: Commit staged changes with maximum entropy encoding.

Title: Random hash of the staged diff, random encoding
Body: Human-readable commit message, random compression, random encoding
Footer: Compression algorithm hint (for decoding)

All randomization handled by base-d --hash --compress --dejavu flags.

Usage:
    upload-commit.py <message> [repo_path]

If repo_path is not provided, uses current directory.
"""

import subprocess
import sys
import os
from pathlib import Path


def run(cmd: list[str], cwd: str = None, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture,
        text=True,
    )


def get_base_d() -> str:
    """Find base-d binary - prefer PATH, fall back to cargo."""
    base_d = "base-d"
    cargo_bin = os.path.expanduser("~/.cargo/bin/base-d")
    if subprocess.run(["which", "base-d"], capture_output=True).returncode != 0:
        if os.path.exists(cargo_bin):
            base_d = cargo_bin
    return base_d


def get_staged_diff(repo_path: str) -> str:
    """Get the staged diff from git."""
    result = run(["git", "diff", "--staged"], cwd=repo_path)
    if result.returncode != 0:
        raise RuntimeError(f"git diff failed: {result.stderr}")
    return result.stdout


def encode_hash(text: str) -> str:
    """Hash text with random algorithm, encode with random dictionary."""
    base_d = get_base_d()
    # --hash without arg = random algorithm
    # --dejavu = random dictionary
    result = subprocess.run(
        [base_d, "--hash", "--dejavu"],
        input=text,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"base-d hash failed: {result.stderr}")
    return result.stdout.strip()


def encode_compress(text: str) -> tuple[str, str]:
    """Compress text with random algorithm, encode with random dictionary.

    Returns (encoded_text, compression_algorithm).
    Since base-d doesn't report which algorithm was used, we pick it ourselves.
    """
    import random
    base_d = get_base_d()

    # Pick compression algorithm (we need to know for the footer)
    compress_algos = ["gzip", "zstd", "brotli", "lz4"]
    compress_algo = random.choice(compress_algos)

    result = subprocess.run(
        [base_d, "--compress", compress_algo, "--dejavu"],
        input=text,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"base-d compress failed: {result.stderr}")
    return result.stdout.strip(), compress_algo


def commit(repo_path: str, title: str, body: str, footer: str) -> str:
    """Create a commit with title, body, and footer."""
    message = f"{title}\n\n{body}\n\n{footer}"
    result = run(["git", "commit", "-m", message], cwd=repo_path)
    if result.returncode != 0:
        raise RuntimeError(f"git commit failed: {result.stderr}")
    return result.stdout


def push(repo_path: str) -> str:
    """Push to origin."""
    result = run(["git", "push"], cwd=repo_path)
    if result.returncode != 0:
        raise RuntimeError(f"git push failed: {result.stderr}")
    return result.stdout


def main():
    if len(sys.argv) < 2:
        print("Usage: upload-commit.py <message> [repo_path]")
        sys.exit(1)

    human_message = sys.argv[1]
    repo_path = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    repo_path = str(Path(repo_path).resolve())

    # Check for staged changes
    diff = get_staged_diff(repo_path)
    if not diff.strip():
        print("No staged changes to commit.")
        sys.exit(1)

    # Generate title (diff hash with random algo and encoding)
    title = encode_hash(diff)

    # Generate body (message with random compression and encoding)
    body, compress_algo = encode_compress(human_message)

    # Footer hints at compression (for decoding)
    footer = f"[{compress_algo}]"

    print(f"Title:  {title}")
    print(f"Body:   {body}")
    print(f"Footer: {footer}")

    # Commit
    commit(repo_path, title, body, footer)
    print("Committed.")

    # Push
    push(repo_path)
    print("Pushed.")


if __name__ == "__main__":
    main()
