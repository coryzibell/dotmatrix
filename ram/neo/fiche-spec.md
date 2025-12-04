# fiche Format Specification

## Overview

fiche is a compact data serialization format optimized for LLM token efficiency. It uses a schema header, value dictionary, and inline rows.

Two modes:
- **ASCII mode** - Maximum token efficiency for API calls
- **Unicode mode** - Transport safety for web/cross-system paste

## Structure

```
schema;dictionary;row;row;row...
```

Three sections separated by semicolons:
1. **Schema** - Field names in order (comma-separated)
2. **Dictionary** - Value mappings for repeated strings (comma-separated key=value pairs)
3. **Rows** - Data rows (semicolon-separated, fields comma-separated within)

## ASCII Mode

Best for: API efficiency, token optimization

```
id,name,email,dept,status,salary;D1=Sales,D2=Marketing,D3=HR,S1=active,S2=onleave;1,Alice,a@x.com,D1,S1,50000;2,Bob,b@x.com,D2,S2,60000;3,Carol,c@x.com,D3,S1,55000
```

### Delimiters
- `;` - Section/row separator
- `,` - Field separator within rows
- `=` - Key-value mapping in dictionary

### Value Dictionary Codes
Short alphanumeric codes for repeated values:
- `D1`, `D2`, `D3` - Categorical values (departments, statuses, etc.)
- `L1`, `L2` - Locations
- `R1`, `R2` - Roles
- `P1`, `P2` - Plans
- etc.

Convention: Single letter prefix + number (e.g., D1=Sales, D2=HR)

## Unicode Mode

Best for: Transport safety, collision avoidance, web paste

```
id,name,email,dept,status,salary;𓀀=Sales,𓀁=Marketing,𓀂=HR,𓀃=active,𓀄=onleave;1,Alice,a@x.com,𓀀,𓀃,50000;2,Bob,b@x.com,𓀁,𓀄,60000;3,Carol,c@x.com,𓀂,𓀃,55000
```

### Delimiters (optional Unicode)
- `;` or `▓` - Section/row separator
- `,` or `┃` - Field separator
- `=` - Key-value mapping

### Value Dictionary Codes
Egyptian hieroglyphs (U+13000 range) for values:
- `𓀀`, `𓀁`, `𓀂`, `𓀃`, `𓀄`...

Benefits:
- Won't appear in real data (collision-safe)
- Visually distinct
- Smaller character count (1 char vs 2-3 for ASCII codes)

## Nested Data

Flatten nested structures using dot-notation in schema:

JSON:
```json
{"user": {"profile": {"name": "Alice", "email": "a@x.com"}}}
```

fiche:
```
user.profile.name,user.profile.email;Alice,a@x.com
```

## Type Handling

Types are implicit from values:
- Numbers: unquoted (`50000`)
- Strings: unquoted (`Alice`)
- Booleans: `1`/`0` or `true`/`false`
- Null: empty field (`,,`)

No quotes needed - the schema defines field order, position determines meaning.

## Escaping

If data contains delimiters:
- ASCII mode: Use Unicode mode instead, or URL-encode problematic values
- Unicode mode: Hieroglyph delimiters won't appear in real data

## Benchmarks (vs JSON, TOON)

### 250 rows flat data (Sonnet)
| Format | Bytes | Tokens |
|--------|-------|--------|
| ASCII fiche | 14KB | 26.0k |
| TOON | 20KB | 27.5k |
| JSON | 55KB | 34.2k |

### 100 rows nested with repeated values (Sonnet)
| Format | Bytes | Tokens |
|--------|-------|--------|
| ASCII fiche | 6KB | 22.6k |
| TOON | 12KB | 23.2k |
| JSON | 26KB | 26.3k |

## When to Use Each Mode

| Scenario | Mode | Why |
|----------|------|-----|
| API calls | ASCII | Token efficiency |
| Copy-paste to web AI | Unicode | Char efficiency, collision safety |
| Data with commas/semicolons | Unicode | No escaping needed |
| File storage | ASCII | Byte efficiency |
| Cross-system transport | Unicode | Survives regex/parsing |

## Key Findings from Research

1. **Newlines are expensive** - 30% more tokens than other delimiters. Always use inline format.

2. **Unicode symbols tokenize poorly** - Each hieroglyph = multiple tokens. Use ASCII for API efficiency.

3. **Value dictionary works** - Compressing "San Francisco, CA" → "L1" saves tokens AND bytes.

4. **JSON structure is heavily optimized** in tokenizers, but fiche still wins by avoiding key repetition.

5. **Schema header is cheap** - One-time cost, enables positional values.
