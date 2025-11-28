# Unicode Marker Protocol

When you need structured output from a system that produces unstructured or hard-to-parse output (like Claude's stream-json execution files), use rare Unicode characters as markers.

## The Technique

Instead of parsing complex output formats, instruct the output source to prefix/wrap data with a unique Unicode marker.

**Example - Hieroglyph Protocol:**
```
Prompt: "Output the identity name prefixed with 𓀀 (e.g., 𓀀smith)"
Output: "𓀀ramakandra"
Parser: content.match(/𓀀(\w+)/)
```

## Good Marker Characters

From `~/work/personal/code/base-d/dictionaries.toml`:

| Block | Example | Use Case |
|-------|---------|----------|
| Egyptian Hieroglyphs | 𓀀𓀁𓀂 | Single value markers |
| Cuneiform | 𒀀𒀁𒀂 | Alternative markers |
| Alchemy Symbols | 🜀🜁🜂 | Category markers |
| Runic | ᚠᚡᚢ | Delimiter markers |

## When to Use

- Parsing LLM output where format is unpredictable
- Extracting specific values from verbose logs
- Creating machine-readable sections in human-readable output
- Avoiding conflicts with common delimiters (quotes, braces, etc.)

## Identity Notes

This is a **Spoon-style reframe**: "There is no parsing problem" - instead of parsing better, change what you're parsing.

Twins might also suggest this when dealing with cross-format data extraction.

## Origin

Discovered during dotmatrix GitHub Actions development (2025-11-27). kautau suggested using hieroglyphs from base-d dictionaries as markers.
