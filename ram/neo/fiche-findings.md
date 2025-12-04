# fiche Format Findings

## Token Efficiency Test Results (2024-12)

### Test Setup
- 10 bugsnag error entries
- Same data in fiche vs JSON format
- Sent directly in prompt to haiku sentinel
- Sequential calls to measure token usage separately

### Results
- **JSON**: ~1k fewer tokens than fiche
- Both parsed correctly with same answers

### Why fiche uses more tokens
Unicode symbols (runic ᚠ-ᛯ, hieroglyphs 𓀀-𓀍, Georgian ჻) tokenize poorly:
- Each symbol likely becomes multiple tokens
- JSON's ASCII punctuation (`{`, `"`, `:`, `,`) are single tokens
- Tokenizers trained heavily on JSON, not obscure Unicode ranges

Character compression ≠ token compression.

### Current State
- **Less readable than TOON** (whitespace-based, familiar structure)
- **More tokens than JSON** (tokenizer penalty for Unicode)
- No clear selling point

### What fiche does offer (weak advantages)
- Explicit schema header (field definitions at top)
- No whitespace overhead (smaller file size, just not fewer tokens)
- Deterministic structure (easier to parse programmatically than TOON)

### Open Questions
1. Could we use ASCII-based delimiters instead of Unicode?
2. Would a different tokenization approach help?
3. Is there a niche where fiche makes sense?
4. Should we pivot the format entirely?

### Ideas to Explore
- Test ASCII-only variant (tab/pipe delimited with short field codes)
- Compare tokenization of `|field:value|` vs `ᚠ┃value`
- Look at what tokens Claude's tokenizer actually produces for each format

### ASCII Hybrid Idea
The pattern works (schema header + value dictionary + compact rows).
Could still compress well with ASCII:
```
@a=assignee,b=env,c=type,d=id,e=name,f=occ,g=pri,h=status
@1=open,2=error,3=PROD-JAVA,4=high
0|a:~|b:3|c:2|d:1|e:Error 1|f:17|g:4|h:1
```

### Unicode Tokenization Hypothesis - TESTED

**Result: Unicode is NOT the problem**

Test with same data, different symbol sets:
- Hieroglyphs + Runic: 18.9k tokens
- Box drawing + common symbols: 18.8k tokens
- Pure ASCII: 18.7k tokens

Only ~200 token difference. The exotic Unicode barely matters.

**The real issue**: JSON's structure itself tokenizes efficiently.
- Tokenizers trained on billions of JSON examples
- `{"key":` patterns likely merge into common tokens
- Our format's structure (newlines per field, row prefixes) adds overhead regardless of symbols

Switching to ASCII won't fix the token problem.

### Structure Test - BREAKTHROUGH

Tested tabular format (one row per entry, not one line per field):

| Format | Tokens | Structure |
|--------|--------|-----------|
| Hieroglyphs + Runic | 18.9k | one field per line |
| Box drawing + symbols | 18.8k | one field per line |
| Pure ASCII | 18.7k | one field per line |
| JSON | 18.4k | inline |
| **Tabular fiche** | **18.4k** | inline rows |

The line-per-field structure was the problem, not symbols.

Tabular format example:
```
@a=id,b=environment,c=occurrences,d=status
@1=PROD-JAVA,2=STAGING,3=open,4=resolved
1|1|17|3
2|1|34|3
3|2|51|3
```

**Potential selling point (needs more testing):**
- Same token cost as JSON
- Smaller character footprint (value dictionary)
- Explicit schema header
- Still exploratory - need to test at scale

### Real-time Token Measurement Round 2

Controlled test with 10 entries, same questions:

| Format | Tokens |
|--------|--------|
| fiche with schema header | 18.4k |
| JSON | 18.5k |

**fiche is actually lighter!** Schema header isn't expensive.

Format tested:
```
@┃id┃environment┃occurrences┃status
@1=PROD-JAVA,2=STAGING,3=open,4=resolved
◉1┃1┃17┃3
◉2┃1┃34┃3
...
```

The value dictionary (1=PROD-JAVA etc) compresses repeated values.
At scale, the savings should compound.

### Scale Testing - fiche WINS

| Test | fiche | JSON | Savings |
|------|-------|------|---------|
| 10 entries flat | 18.4k | 18.5k | 100 |
| 50 entries flat | 19.6k | 20.5k | 900 |
| 19 entries nested | 19.4k | 19.8k | 400 |

Key findings:
- Value dictionary compresses repeated strings (veoci.com, admin@veoci.com, true, USER)
- Savings compound with more data
- Nested data works with flattened columns (owner.displayName) - no schema explosion
- ~5% token reduction at 50 entries

### TOON Comparison

| Format | Tokens | Notes |
|--------|--------|-------|
| **fiche** | **19.6k** | self-describing, value dictionary |
| fiche + explanation | 20.1k | model over-explains when primed |
| TOON | 19.7k | schema header, no value dictionary |
| JSON | 20.5k | baseline |

fiche beats TOON by ~100 tokens, JSON by ~900 tokens at 50 entries.

Key insight: fiche is self-describing - no schema explanation needed. Adding one actually increases tokens because model over-explains its parsing.

The value dictionary is the differentiator vs TOON - TOON repeats full strings (PROD-JAVA, open, error) on every row, fiche compresses to single characters.

### TOON Benchmark Analysis (from toonformat.dev/guide/benchmarks)

**Their claims:**
- 39.6% fewer tokens than JSON
- 73.9% accuracy vs JSON's 69.7%
- Tested 209 questions across 4 models, 11 datasets, 6 formats

**Caveats we noticed:**
- Used GPT-5's o200k_base tokenizer (not Claude's)
- Compared against pretty-printed JSON (lots of whitespace)
- Claude Haiku specifically: only 59.8% vs 57.4% accuracy difference

**Our test was harder:**
- Compact JSON (no pretty printing) as baseline
- fiche still won by ~900 tokens at 50 entries

**Datasets they used:**
1. Uniform employee records (100 rows)
2. E-commerce orders with nesting (50 rows)
3. Time-series analytics (60 days)
4. GitHub repositories (100 rows)
5. Semi-uniform event logs (75 rows)
6. Deeply nested configuration (1 file)

### 100 Employee Benchmark (TOON-style test)

| Format | Tokens | Order tested |
|--------|--------|--------------|
| TOON | 21.1k | first |
| JSON | 22.5k | second |
| fiche | 22.9k | third |

Reversed order test (TOON first) - no caching effect detected.

TOON wins at 100 entries. The whitespace-based structure tokenizes efficiently.
fiche's value dictionary overhead doesn't pay off when data has mostly unique values.

### Type Handling: String-wrapped Numbers

Both fiche and TOON preserve type distinction:
- `"id":"1"` stays as string (quoted)
- `occurrences:17` stays as number (unquoted)

fiche uses type markers in schema: `ᚠⁱ` (integer), `ᚡˢ` (string)
TOON uses quotes to distinguish: `"1"` vs `17`

Neither does lossy coercion. Token difference is from structure, not type handling.

### Unicode Token Cost Testing

| Symbol type | Example | Tokens |
|-------------|---------|--------|
| ASCII letters | a,b,c,d,e | 18.1k |
| Runic (BMP) | ᚠ,ᚡ,ᚢ,ᚣ,ᚤ | 18.2k |
| Georgian (BMP) | ჻ | 18.2k |
| Hieroglyphs (SMP) | 𓀀,𓀁,𓀂,𓀃,𓀄 | 18.2k |
| Brackets [ ] vs ⟦ ⟧ | same | same |
| Pipes | vs ┃ | same | same |

Initial finding: Unicode adds ~100 tokens overhead vs ASCII in small tests.

### Scale Test: 50 Rows - MAJOR FINDING

| Format | Tokens | 50 rows |
|--------|--------|---------|
| **fiche ASCII** | **18.6k** | winner |
| CSV | 18.8k | +200 |
| fiche Unicode | 19.3k | +700 |

**Key insight:** At scale, Unicode costs ~700 tokens vs ASCII at 50 rows.

- ASCII fiche BEATS CSV by 200 tokens
- Value dictionary works - "Sales" → "1" saves tokens when repeated
- But Unicode wipes out the gains and adds more overhead

**Recommendation:** Hybrid approach
- Keep fiche structure (schema header + value dictionary)
- Use ASCII for tokens (`1`, `2`, `a`, `b`) instead of Unicode
- Use simple delimiters (`|`, `#`) instead of fancy ones (`┃`, `◉`)

**Trade-off:** ASCII risks collision with data values. Need escaping strategy.

### Comma-Heavy Data Test (50 rows)

| Format | Tokens | Notes |
|--------|--------|-------|
| **TOON** | **18.8k** | needs quotes for commas |
| **Pipe-CSV (no dict)** | **18.8k** | tied - no escaping needed |
| fiche w/ dictionary | 19.0k | +200 overhead |
| fiche tab-delimited | 19.0k | delimiter doesn't matter |

### Value Dictionary: DOES NOT HELP

The dictionary adds cognitive overhead:
1. Model reads `@1=active,2=inactive`
2. Stores mapping in "memory"
3. Later sees `1`, has to recall = "active"

Vs just reading `active` directly - no extra step.

**When dictionary might help:**
- Values are VERY long (full URLs, UUIDs, long strings)
- Same long value repeats many times
- Short values like "active", "Sales" - just write them out

**Simplest winning format: Pipe-CSV**
```
id|name|location|status
1|Smith, John|New York, NY|active
2|Jones, Mary|Los Angeles, CA|inactive
```
- Ties TOON on tokens
- No escaping needed (pipes rare in data)
- No dictionary overhead
- Models parse it naturally (CSV-like)

### Unicode Observations

Models parse certain Unicode intuitively:
- Circled numbers (①②③) read as 1, 2, 3
- Some symbols have semantic meaning baked in

Could use Unicode for structure WITHOUT token penalty if chosen carefully.

### Cold-Parse Structures

What existing formats do models "know" that could reduce cognitive overhead?

Candidates to test:
- **CSV** - ubiquitous, models trained on tons of it
- **TSV** - tab-separated, even simpler
- **Markdown tables** - visual, models see these in docs
- **YAML** - indentation-based, common in configs
- **INI** - simple key=value sections
- **S-expressions** - Lisp-style, parenthetical
- **EDN** - Clojure data notation
- **TOML** - like INI but typed

Hypothesis: Leaning on familiar structure = model "gets it" faster = lower effective token cost even if raw token count is similar.

### Superscript Type Markers - NOT WORTH IT

Tested using superscript for type indication (like JSON uses quotes):

| Position | Example | Tokens |
|----------|---------|--------|
| Postpended | `Smith, Johnˢ` | 18.4k+ |
| Prepended | `ˢSmith, John` | 18.4k |
| No markers | `Smith, John` | ~18.2k |

Type markers add ~200 tokens overhead regardless of position.

**Why:** Models read left-to-right. Type markers interrupt natural parsing flow - model likely backtracks to reinterpret the value.

**Alternative approach:** Only mark ambiguous values (string numbers like ID `"123"` that shouldn't be parsed as integer). But this adds complexity for edge cases.

### Current Best Format: Pipe-CSV

```
id|name|location|status
1|Smith, John|New York, NY|active
2|Jones, Mary|Los Angeles, CA|inactive
```

- Ties TOON on tokens (18.8k at 50 rows)
- No escaping needed (pipes rare in data)
- Models parse it naturally
- No dictionary overhead

**Remaining question:** How to handle nesting? ANSWERED - see below.

### Nested Data Test (50 rows, 2-level nesting)

Data structure: `id`, `profile.name`, `profile.email`, `profile.settings.theme`, `profile.settings.notifications`, `employment.department`, `employment.status`, `employment.salary`, `employment.startDate`

| Format | Tokens | Notes |
|--------|--------|-------|
| JSON (nested) | 21.9k | standard nested objects |
| **Pipe-CSV (dot-notation)** | **20.6k** | flattened headers |

**Pipe-CSV wins by 1.3k tokens** on nested data.

Dot-notation flattening (`profile.settings.theme`) works well:
- Models understand the hierarchy from header
- No bracket/brace overhead per row
- Header is longer but only appears once

### Header Variations (50 rows nested)

| Format | Tokens | Notes |
|--------|--------|-------|
| Pipe-CSV (dot-notation) | 20.6k | `profile.settings.theme` |
| Pipe-CSV (Greek + schema) | 20.6k | `α=id,β=profile.name...` then `α|β|γ` |
| Pipe-CSV (short headers) | 20.6k | `id|name|email|theme|notif|dept` |
| SQL (CREATE + INSERT) | 20.7k | native format, no benefit |

Greek symbols with schema mapping = same tokens as full dot-notation.
Short intuitive headers = same tokens.
SQL familiarity doesn't help tokenization.

**Conclusion:** Header format doesn't matter much. The data rows dominate token count.

### CRITICAL: Scale Test (500 rows nested)

| Format | 50 rows | 500 rows | Scale factor |
|--------|---------|----------|--------------|
| JSON | 21.9k | 19.3k | 0.88x (got smaller??) |
| Pipe-CSV | 20.6k | 36.2k | 1.76x |

**Pipe-CSV does NOT scale.** At 500 rows, JSON wins by 17k tokens.

File sizes tell a different story:
- JSON: 110KB (largest file)
- Pipe-CSV: 39KB (smallest file)
- SQL: 47KB

Character compression ≠ token compression (again).

**Hypothesis:** Newlines tokenize poorly at scale. JSON's inline comma-separated structure merges into efficient token patterns. Each newline in pipe-CSV may fragment tokenization.

**Revised conclusion:** For large datasets, JSON wins. Pipe-CSV only competitive at <100 rows.

### Inline vs Newline Test (500 rows)

| Format | Tokens | Structure |
|--------|--------|-----------|
| JSON | 19.3k | inline `},{` |
| Pipe-CSV (newlines) | 36.2k | one row per line |
| TOON (newlines) | 36.6k | one row per line |
| Pipe-CSV (inline `;`) | 34.6k | semicolon row separator |

Inline helps (~2k savings) but doesn't close the gap. JSON still wins by 15k.

### Next: JSON Token Compression Experiment

Hypothesis: JSON's common patterns (`},{`, `":"`, `":{"`) tokenize efficiently.
Can we beat JSON by compressing these patterns to single Unicode chars?

Test plan:
1. Baseline: minified JSON (no whitespace) - measure tokens
2. Replace `},{` with single char
3. Replace `":"` with single char
4. Replace `":{"` with single char
5. Measure each step

### JSON Compression Experiment Results (500 rows)

| Format | Tokens | File Size | Notes |
|--------|--------|-----------|-------|
| **Nested JSON** | **19.3-19.8k** | 110KB | WINNER |
| JSON + `▪` for `},{` | 20.1k | 109KB | worse - breaks token patterns |
| JSON arrays (positional) | 35.1k | 46KB | way worse despite smaller file |

**Key insight:** Replacing `},{` with Unicode made it WORSE. The tokenizer knows JSON patterns deeply.

**Surprise finding:** JSON arrays with header row (46KB file) used 35k tokens vs nested JSON (110KB file) at 19k tokens. Character count ≠ token count.

The `],[` array separator tokenizes far worse than `},{` object separator.

### Why Nested JSON Wins

Hypothesis: Tokenizers trained heavily on JSON. Patterns like:
- `"profile":{"name":"`
- `"email":"`
- `"},"employment":{`

These likely merge into efficient multi-char tokens. The *repetition* of keys helps - same token sequences reused.

Flat formats break these patterns. Each row looks "new" to the tokenizer.

### JSON Optimization Attempts (500 rows)

| Variant | File Size | Tokens | Savings |
|---------|-----------|--------|---------|
| Full keys, full values | 110KB | 19.3-19.8k | baseline |
| Short keys (i,p,n,e...) | 73KB (-33%) | 19.4k | none |
| Short keys + compressed values | 47KB (-57%) | 19.9k | none |

**Conclusion:** JSON structure is the token floor (~19k for this dataset). Compressing keys/values saves file size but not tokens. The structural patterns (`"key":{"`, `},{`, etc.) dominate.

**Implication for fiche:** Can't beat JSON by compressing data. Would need to change HOW the structure tokenizes - but tokenizers are trained on JSON, so that's a losing battle.

### Cross-Model Comparison (500 rows, Sonnet)

| Format | Tokens | File Size |
|--------|--------|-----------|
| JSON | 20.2k | 110KB |
| Pipe-CSV | 36.1k | 39KB |
| **fiche (full spec)** | **45k** | **26KB** |

**fiche is WORST** on Sonnet despite smallest file size.

The Unicode approach (runic keys + hieroglyph values) actively hurts. Each exotic symbol tokenizes to multiple tokens. ASCII JSON patterns are heavily optimized in tokenizers.

### Final Verdict (Token Efficiency)

- **Small data (<100 rows):** fiche competitive, slight wins possible
- **Large data (500+ rows):** JSON wins decisively, fiche is worst performer
- **Unicode:** Looks compact but tokenizes poorly
- **JSON familiarity:** Tokenizers trained on JSON, can't beat it at its own game

### Pivot: fiche's Real Value Proposition

**NOT for:** API token cost optimization

**YES for:** Human-AI web interfaces (ChatGPT, Claude web, etc.)

| Metric | fiche | JSON |
|--------|-------|------|
| File/paste size (500 rows) | 26KB | 110KB |
| Character efficiency | 4x better | baseline |
| Collision safety | Perfect (Unicode delimiters) | Escaping hell |
| Copy-paste survivability | High | Medium (quotes break) |
| Visual structure | Clear (`◉`, `┃`, hieroglyphs) | Noisy (`{"":[{`) |

**Use cases:**
1. Paste data into web AI → get analysis (chars matter, not tokens)
2. Data with messy content (commas, quotes, pipes in values)
3. Export/import workflows where format must survive copy-paste
4. Structured prompts where visual clarity helps the human

### Future Research

Scientific approach: hypothesis → test → iterate

### HYPOTHESIS: Byte-based billing (UNPROVEN)

Observation: Unicode JSON (175KB bytes, 110KB chars) hit token limit while ASCII JSON (110KB bytes, 110KB chars) didn't.

| File | Bytes | Chars | Ratio | Tokens |
|------|-------|-------|-------|--------|
| JSON (ASCII) | 110KB | 110KB | 1.0x | ~20k |
| fiche (Unicode) | 43KB | 27KB | 1.6x | 45k |
| Unicode JSON | 175KB | 110KB | 1.6x | hit limit |

**Theory:** Anthropic's token counting may be byte-influenced, not pure tokenization. UTF-8 multi-byte chars (3-4 bytes each) inflate the "cost."

**If true:**
- ASCII-only formats have inherent advantage
- Unicode compression is counterproductive for APIs
- fiche only viable for web UIs (char-based limits)

**To test:** Same semantic content, different encodings. Compare actual billed tokens.

### Byte Hypothesis Test (1000 random chars)

| String | Chars | Bytes | Tokens | Bytes/Token |
|--------|-------|-------|--------|-------------|
| ASCII | 1000 | 1000 | ~Xk | ? |
| Unicode | 1000 | 2522 | ~X.1k | ? |

**Result:** Only ~100 token difference despite 2.5x byte difference.

**Conclusion:** NOT purely byte-based. The tokenizer handles Unicode better than raw bytes would suggest. The fiche penalty (45k vs JSON 20k) is from:
1. Exotic symbols tokenizing to multiple tokens each
2. Novel structure not matching learned patterns
3. NOT from UTF-8 byte inflation alone

### BREAKTHROUGH: Newlines are expensive

Tested repeated patterns (1500 chars each):

| Pattern | Tokens |
|---------|--------|
| spaces | 18.5k |
| "the " | 19.0k |
| `},{` | 19.1k |
| tabs | 19.2k |
| "true" | 19.2k |
| "null" | 19.3k |
| **newlines** | **24.8k** |

**Newlines cost 30% more tokens** than other patterns.

This explains:
- JSON (inline): efficient (~20k for 500 rows)
- Pipe-CSV (newline/row): expensive (~36k for 500 rows)
- TOON (newline/row): expensive (~36k for 500 rows)

**Implication:** Any format using newlines as row delimiters will lose to inline JSON at scale. Newlines should only be used for human readability, not efficiency.

### INLINE FICHE BEATS JSON

Tested 250 rows on Sonnet, no chunking issues:

| Format | Tokens | Chars | Bytes |
|--------|--------|-------|-------|
| JSON | 34.2k | 55KB | 55KB |
| **Inline fiche** | **31.4k** | **13KB** | **22KB** |

**Fiche wins by 2.8k tokens (8% savings)** when inline!

The newline-per-row format was the problem, not fiche itself. With `▓` as row separator instead of `\n`, fiche beats JSON on tokens AND is 4x smaller in chars.

Earlier 500-row tests were misleading because:
1. fiche with newlines: 45k tokens (bad)
2. fiche inline: ~31k extrapolated (good)
3. JSON: ~20k (but may have been chunking favorably)

### Plot Twist: TOON Wins at 250 rows (Sonnet)

| Format | Bytes | Tokens |
|--------|-------|--------|
| **TOON** | **20KB** | **27.5k** |
| Inline fiche | 22KB | 31.4k |
| JSON | 55KB | 34.2k |

TOON beats both despite having newlines! Its extreme simplicity (no quotes, no braces, just commas) offsets the newline cost.

fiche's Unicode symbols still hurt - they're multi-byte (22KB vs TOON's 20KB ASCII) and tokenize less efficiently.

**Revised understanding:**
- Newlines ARE expensive, but...
- Simple ASCII structure can absorb that cost
- Unicode symbols add token overhead beyond just bytes
- TOON's minimalism wins on pure efficiency

### ASCII FICHE WINS (250 rows, Sonnet)

| Format | Bytes | Tokens |
|--------|-------|--------|
| **ASCII fiche** | **14KB** | **26.0k** |
| TOON | 20KB | 27.5k |
| Simple Unicode fiche | 16KB | 28.1k |
| Inline Unicode fiche | 22KB | 31.4k |
| JSON | 55KB | 34.2k |

**ASCII fiche beats everything** - 1.5k fewer tokens than TOON, 8k fewer than JSON.

Format tested:
```
id,name,email,theme,notif,dept,status,salary,date;D1=Sales,D2=Marketing,D3=HR,...;1,Employee 1,emp1@company.com,T1,1,D2,S1,50100,M2;2,...
```

Key insights:
- Value dictionary WORKS when ASCII (D3 vs 𓀂)
- Inline (semicolon separator) avoids newline penalty
- Schema header is minimal overhead
- Smallest bytes AND fewest tokens

### Cross-model validation (250 rows)

| Format | Haiku | Sonnet | Bytes |
|--------|-------|--------|-------|
| **ASCII fiche** | **26.1k** | **26.0k** | **14KB** |
| TOON | ~27.5k | 27.5k | 20KB |
| JSON | 34.2k | 34.2k | 55KB |

**Consistent across models.** ASCII fiche saves 24% tokens vs JSON.

### THE WINNING FORMAT

```
schema;dictionary;row;row;row...
```

Example:
```
id,name,email,dept,status;D1=Sales,D2=HR,S1=active,S2=onleave;1,Alice,a@x.com,D1,S1;2,Bob,b@x.com,D2,S2
```

Rules:
1. ASCII only (no Unicode)
2. Inline (semicolon row separator, no newlines)
3. Value dictionary for repeated strings
4. Schema header defines field order
5. Commas within rows, semicolons between sections

### Nested Data with Complex Values (100 rows, Sonnet)

Tested with repeated long strings: company names, locations, roles, statuses, plans.

| Format | Bytes | Tokens | vs JSON |
|--------|-------|--------|---------|
| **ASCII fiche** | **6KB** | **22.6k** | **-14%** |
| TOON | 12KB | 23.2k | -12% |
| JSON | 26KB | 26.3k | baseline |

ASCII fiche is **4x smaller** than JSON in bytes, **2x smaller** than TOON.

Value dictionary compression shines with repeated long strings:
- "San Francisco, CA" → L1
- "Principal Architect" → R5
- "enterprise-unlimited" → P1

All three formats parsed correctly and answered reasoning questions accurately.

### Unicode JSON Experiment

Replaced JSON delimiters with fullwidth Unicode lookalikes:
- `{` → `｛`, `}` → `｝`
- `[` → `［`, `]` → `］`
- `"` → `＂`
- `:` → `：`, `,` → `，`

Result: File bloated from 110KB to 175KB (bytes), hit 25k token input limit. Didn't even get to test if model could parse it.

1. **Individual Unicode char tokenization** - DONE
   - Unicode costs ~100 tokens more than ASCII
   - Consistent across BMP/SMP
   - Worth it for collision safety

2. **Optimal delimiter discovery**
   - What single chars tokenize as 1 token?
   - Do common delimiters merge with adjacent text?

3. **Value dictionary break-even point**
   - At what repetition rate does dictionary pay off?
   - How many unique values before overhead exceeds savings?

4. **Structure experiments**
   - Newlines vs inline
   - Row markers vs positional
   - Schema header cost vs benefit

---

## Open Issue: Deeply Nested API Responses (2024-12)

base-d's fiche encoder flattens deeply nested structures (like Veoci API response with 545 entries) into a single wide row with indexed field names (`entries჻0჻field`, `entries჻1჻field`).

**Byte comparison (massive Veoci data):**
- JSON: 7.8MB
- TOON: 6.6MB
- ASCII fiche: 8.4MB

fiche is LARGER in bytes because it treats the API response as one object, not an array of entries.

**However:** Bytes ≠ tokens. Need to test actual token counts on models. The ASCII delimiters and value dictionary may still win on token efficiency even if byte count is higher. The tokenizer optimizations we found earlier could flip the result.

**To test:** Run all three formats through Sonnet, measure actual tokens.

**Potential fixes if fiche loses:**
1. Detect array patterns in nested data and encode as rows
2. Add a mode to extract specific array paths for encoding (e.g., `--path ".json.entries"`)
3. Accept that fiche is optimized for tabular data, not arbitrary nested structures

---

## Implementation Note: Encoder/Decoder Format Mismatch

The fiche encoder outputs tokenized format (starts with `@`, uses runic field tokens like ᚠ, ᚡ), but the decoder expects row-based format with `◉` markers.

**To fix:** Update decoder to handle the tokenized format that the encoder produces. The `fq` tool depends on this working correctly.

**Priority:** Fix decoder before continuing fq development. Step by step - foundation first.
