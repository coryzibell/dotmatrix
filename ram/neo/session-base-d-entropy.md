# Session: base-d Entropy Features

## What We Built

### base-d CLI Changes (shipped to crate)
- `--hash` without arg = random algorithm (md5, sha256, sha512, blake3, xxh64, xxh3)
- `--compress` without arg = random algorithm (gzip, zstd, brotli, lz4)
- Removed default dictionary from `dictionaries.toml` - requires explicit `-e <dict>` or `--dejavu`
- Fixed composition bug where `--compress --dejavu` was outputting hex instead of encoded

### Technical Pattern: Optional CLI Args in Clap
```rust
#[arg(long, value_name = "ALGORITHM")]
hash: Option<Option<String>>,
```
- `None` = flag not present
- `Some(None)` = flag present, no value (random)
- `Some(Some(x))` = flag present with value

### upload-commit.py (`~/.matrix/artifacts/`)
"Broken blockchain" commits - deterministic signatures outside git's hash:
- **Title**: SHA of staged diff, random hash algo, random dictionary (`base-d --hash --dejavu`)
- **Body**: Human message, random compression, random dictionary (`base-d --compress <algo> --dejavu`)
- **Footer**: Compression hint `[algo]` for decoding

Python picks compression algo (needs it for footer), base-d randomizes everything else.

## Future Ideas (stored in `~/.matrix/future/` and `ram/neo/base-d-entropy-design.md`)
- `--entropy` flag: meta-randomization (random whether to hash/compress/encode, random algos, maybe raw output)
- Neo mode streaming blockchain: watch hashes scroll like Matrix rain
- Auto-detect compression algorithm in base-d

## Process Learnings
- **"Roll forward"**: Test and move, don't ask permission until blocker or ready to commit
- **Bash escaping → Python**: When subshell/quoting gets hairy, just write a script
- **Design doc first**: For multi-phase work, write the phases before coding
- **Zion gets Opus**: Permanent knowledge deserves full weight, not haiku

## Files Modified
- `/home/w3surf/work/personal/code/base-d/src/cli/mod.rs` - CLI args, composition logic
- `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs` - `select_random_hash()`, `select_random_compress()`
- `/home/w3surf/work/personal/code/base-d/dictionaries.toml` - Removed default_dictionary
- `/home/w3surf/.matrix/artifacts/upload-commit.py` - The upload script

## Next
- Sync `.matrix` (pull from dotmatrix)
- Reboot to get zion-control agent
- Pass learnings to Zion properly
