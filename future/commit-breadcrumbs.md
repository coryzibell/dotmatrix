# Commit Breadcrumbs

The encoded commit pattern creates a trail for the curious.

## The Pattern
- **Title**: Hash of diff (random algo, random dictionary)
- **Body**: Compressed message (random algo, random dictionary)
- **Footer**: `[compression_algo]` - the hint

## The Path
Anyone can decode if they follow the breadcrumbs:
1. Footer reveals compression algorithm
2. `base-d --detect --decompress <algo>` finds the dictionary
3. Message revealed

## Philosophy
Not encrypted. Encoded. A puzzle for those who seek.

> "The information is there for anyone who knows how to look."

## Lifecycle Integration Ideas
- CLI command: `mx decode <commit>` - follow the path automatically
- Git hook: optionally show decoded message in log
- Documentation: teach the pattern to contributors
- Easter eggs: special messages in milestone commits

## See Also
- `mx commit` - the upload pattern
- `base-d --detect` - dictionary detection
