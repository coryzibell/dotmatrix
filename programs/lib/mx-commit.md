# mx commit - Encoded Commit

> See `lib/mx.md` for finding mx.

## Usage

```bash
mx commit "<message>"           # Commit staged changes
mx commit -a "<message>"        # Stage all, then commit
mx commit -a -p "<message>"     # Stage all, commit, push
```

Run from the target repo directory.

## What It Does

1. Stage changes (if `-a`)
2. Hash the diff with random algorithm (md5/sha256/sha512/blake3/xxh64/xxh3)
3. Encode hash with random dictionary via `base-d --dejavu`
4. Compress message with random algorithm (gzip/zstd/brotli/lz4)
5. Encode compressed message with random dictionary via `base-d --dejavu`
6. Commit with encoded title/body
7. Push (if `-p`)

## Output Format

```
Title:  <encoded hash of diff>
Body:   <encoded compressed message>
Footer: [<hash_algo>:<hash_dict>|<compress_algo>:<body_dict>]
```

Example: `[xxh64:base64_math|gzip:zodiac]` means:
- Title: xxh64 hash encoded with base64_math dictionary
- Body: gzip compressed, encoded with zodiac dictionary

## Dejavu Detection

If both title and body randomly receive the same dictionary:

```
whoa. [<hash_algo>:<dict>|<compress_algo>:<dict>]
```

This is observation, not forced. Watching the system for coincidence.

## Decoding

```bash
echo "<body>" | base-d --detect --decompress <algo>
```
