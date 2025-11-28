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
Footer: [<compress_algo>]
```

## Dejavu Detection

If both title and body randomly receive the same dictionary, footer becomes:

```
[<compress_algo>]
whoa. base-d --detect --decompress <compress_algo>
```

This is observation, not forced. Watching the system for coincidence.

## Decoding

```bash
echo "<body>" | base-d --detect --decompress <algo>
```
