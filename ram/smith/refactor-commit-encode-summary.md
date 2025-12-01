# mx commit --encode-only Refactor

## Changes Made

### Files Modified
- `/home/w3surf/work/personal/code/mx/src/main.rs`

### What Changed

1. **Consolidated encode-commit into commit command**
   - Added `--encode-only` flag to `commit` command
   - Added `--title` and `--body` flags (require `--encode-only`)
   - Made `message` argument optional when using `--encode-only`
   - Added validation: `--title` and `--body` require each other

2. **Deprecated encode-commit**
   - Marked with `#[command(hide = true)]` - hidden from help
   - Prints warning to stderr: "Warning: 'mx encode-commit' is deprecated. Use 'mx commit --encode-only' instead."
   - Still functional for backward compatibility

3. **Updated command handler**
   - Added logic to handle `--encode-only` mode
   - PR-style encoding: prints encoded message to stdout
   - Normal mode: behaves exactly as before

## New Interface

```bash
# Normal commit (unchanged behavior)
mx commit "msg"                              # commit
mx commit "msg" -a                           # stage all + commit
mx commit "msg" -p                           # commit + push
mx commit "msg" -a -p                        # stage all + commit + push

# Encode-only mode (new)
mx commit --encode-only --title "x" --body "y"   # print encoded message

# Deprecated (still works, shows warning)
mx encode-commit --title "x" --body "y"     # warning to stderr, encoded to stdout
```

## Validation Tests

✓ `mx commit` (no args) → error: MESSAGE required
✓ `mx commit --encode-only` → error: requires --title and --body  
✓ `mx commit --encode-only --title "x"` → error: --body required
✓ `mx commit --encode-only --title "x" --body "y"` → prints encoded message
✓ `mx encode-commit --title "x" --body "y"` → warning to stderr, encoded to stdout
✓ `mx --help` → encode-commit NOT listed
✓ `mx encode-commit --help` → shows help with deprecation notice
✓ All 60 tests pass
✓ Build successful

## Implementation Notes

- No changes to `commit.rs` - reused existing `encode_commit_message()` function
- `--encode-only` conflicts with `-a` and `-p` (no sense staging/pushing in encode-only mode)
- Deprecation warning goes to stderr, encoded output to stdout (clean piping)
- Clap validation handles all edge cases automatically

## No Issues Encountered

Refactor completed successfully. All tests pass. Interface validated.
