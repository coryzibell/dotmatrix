# Storage Resolution

Determine public vs private storage based on working directory.

## Logic

```
if cwd matches ~/work/*/ (except ~/work/personal/):
  storage = ~/.matrix-private/
else:
  storage = ~/.matrix/
```

## Quick Reference

| Working Directory | Storage Base |
|-------------------|--------------|
| `~/work/*/` (not personal) | `~/.matrix-private/` |
| `~/work/personal/*` | `~/.matrix/` |
| `~/.matrix/*` | `~/.matrix/` |
| Open source repos | `~/.matrix/` |

## Paths

Once you've determined `{storage}`:

- RAM: `{storage}/ram/{identity}/`
- Cache: `{storage}/cache/`
- Zion: `{storage}/zion/`
- Artifacts: `{storage}/artifacts/`

## Why

`~/.matrix/` is a public dotfiles repo. Client work, user lists, internal architecture details must stay in `~/.matrix-private/`.
