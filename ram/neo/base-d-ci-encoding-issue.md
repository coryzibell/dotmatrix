# CI Encoding Issue - base-d version bump commits

## Problem

GitHub web UI shows replacement characters `��������...` for some commit titles created by CI.

## Investigation

- Commit `3979fe011ae3e1146cda64c3951776bfcf19a14c` (base-d v0.4.1 bump)
- `git show` reveals the title is **empty/whitespace** - not actually containing the encoded text
- The body encodes fine (emoji visible)

## Root Cause

In `.github/workflows/wake-up.yml` lines 113-123:

```bash
# Encode with upload pattern
TITLE=$(echo -n "$VERSION" | base-d --hash sha256 --dejavu)
ALGOS=("gzip" "zstd" "brotli" "lz4")
ALGO=${ALGOS[$RANDOM % ${#ALGOS[@]}]}
BODY=$(echo -n "$MESSAGE" | base-d --compress "$ALGO" --dejavu)

git commit -m "$TITLE

$BODY

[$ALGO]"
```

The `$TITLE` variable is likely:
1. Empty due to base-d failure/error not being captured
2. Contains characters that get stripped by bash/git
3. Old crates.io version of base-d has a bug

## Theories

1. **Shell quoting** - The heredoc-style commit message might be stripping/mangling Unicode
2. **base-d stderr** - The `--dejavu` flag prints "Note: Using..." to stderr, but if there's an error, stdout might be empty
3. **Old base-d version** - CI does `cargo install base-d` from crates.io, which may lag behind

## Progress

### mx commit footer expanded (2025-11-29)
- Updated `mx` to capture hash algorithm from base-d stderr
- New footer format: `[hash_algo:title_dict|compress_algo:body_dict]`
- Example: `[sha512:cuneiform|brotli:base64_math]`
- Pushed to mx repo, waiting for crates.io publish

### Next Steps

1. Wait for mx publish to crates.io
2. Update base-d CI to use new footer format (currently still `[$ALGO]`)
3. Monitor CI commits for garbled titles - footer will reveal the culprit algo/dict
4. Add error checking to CI: `TITLE=$(... || echo "fallback")`

## Stress Test Results

Ran 300 local `mx commit` iterations - no failures found. Issue is CI-specific.

## Related Files

- `/home/w3surf/work/personal/code/base-d/.github/workflows/wake-up.yml`
- `/home/w3surf/work/personal/code/mx/src/commit.rs`
