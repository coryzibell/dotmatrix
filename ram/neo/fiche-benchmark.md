# fiche Benchmark Study

## Methodology

Adapted from TOON benchmark methodology (toonformat.dev/guide/benchmarks)

### Formats Tested
1. JSON (minified, inline)
2. TOON (with newlines - their native format)
3. ASCII fiche (inline, with value dictionary)

### Models
- Claude Haiku
- Claude Sonnet
- Claude Opus (if budget allows)

### Datasets

**Primary (6):**
1. Employee records - 100 rows, flat uniform data
2. E-commerce orders - 50 rows, nested (customer objects, item arrays)
3. Time-series analytics - 60 rows, dates + numeric metrics
4. GitHub repositories - 100 rows, real-world API structure
5. Event logs - 75 rows, semi-uniform (mix of structures)
6. Nested config - 1 object, deeply nested

**Structural Validation (5):**
- Truncated arrays
- Extra rows
- Missing fields
- Inconsistent field counts
- Corrupted data

### Question Categories

| Category | % of Questions | Description |
|----------|----------------|-------------|
| Field Retrieval | 33% | Direct value lookups |
| Aggregation | 30% | Totals, averages, single filters |
| Filtering | 23% | Multi-condition queries |
| Structure Awareness | 12% | Format-specific features |
| Structural Validation | 2% | Detect corruption |

### Metrics

1. **Accuracy** - % of correct answers (type-aware comparison)
2. **Token Count** - Reported by kautau from UI
3. **Processing Time** - Reported by kautau from UI (seconds)
4. **Efficiency Score** - (Accuracy % ÷ Token Count) × 1,000

### Test Process

1. Generate dataset in all 3 formats
2. Create questions for each category
3. Run each question through sentinel agent (one at a time)
4. kautau reports token count
5. Verify answer correctness
6. Log results

---

## Dataset 1: Employee Records (100 rows)

### Structure
- id (int)
- name (string)
- email (string)
- department (string) - 5 values: Sales, Marketing, HR, Finance, Engineering
- status (string) - 3 values: active, onleave, terminated
- salary (int)
- startDate (string)
- manager (string) - nullable

### Files
- `/home/w3surf/benchmark/bench/employees-100.json`
- `/home/w3surf/benchmark/bench/employees-100.toon`
- `/home/w3surf/benchmark/bench/employees-100.fiche`

### Questions (10)

**Field Retrieval (3):**
1. What is the email of employee with id 47?
2. What is the salary of the employee named "Employee 73"?
3. Who is the manager of employee 28?

**Aggregation (3):**
4. What is the total salary of all employees?
5. How many employees are in the Engineering department?
6. What is the average salary of employees with status "active"?

**Filtering (3):**
7. List all employees in Sales with salary > 70000
8. Which employees started after 2020-06-01 and are on leave?
9. Find all employees in HR or Finance with no manager

**Structure Awareness (1):**
10. How many fields does each employee record have?

---

## Results Log

### Dataset 1: Employees

| Q# | Format | Model | Tokens | Time(s) | Correct | Answer |
|----|--------|-------|--------|---------|---------|--------|
| 1 | JSON | Haiku | 23.1k | 4s | ✓ | emp47@company.com |
| 1 | TOON | Haiku | 21.7k | 5s | ✓ | emp47@company.com |
| 1 | fiche | Haiku | 21.6k | 4s | ✓ | emp47@company.com |
| 2 | JSON | Haiku | 23.1k | 4s | ✓ | 91663 |
| 2 | TOON | Haiku | 21.7k | 4s | ✓ | 91663 |
| 2 | fiche | Haiku | 21.5k | 5s | ✓ | 91663 |
| 3 | JSON | Haiku | 23.1k | 5s | ✓ | Emma Wilson |
| 3 | TOON | Haiku | 21.7k | 3s | ✓ | Emma Wilson |
| 3 | fiche | Haiku | 21.6k | 4s | ✓ | Emma Wilson |
| 4 | JSON | Haiku | 23.1k | 4s | ✗ | 7584234 (expected 7945780) |
| 4 | TOON | Haiku | 21.7k | 4s | ✗ | 7959438 (expected 7945780) |
| 4 | fiche | Haiku | 21.5k | 4s | ✗ | 7627419 (expected 7945780) |
| 5 | JSON | Haiku | 23.1k | 5s | ✓ | 20 |
| 5 | TOON | Haiku | 21.7k | 4s | ✓ | 20 |
| 5 | fiche | Haiku | 21.6k | 7s | ✓ | 20 |
| 7 | JSON | Haiku | 23.2k | 4s | ✓ | 14 employees |
| 7 | TOON | Haiku | 21.8k | 4s | ✓ | 14 employees |
| 7 | fiche | Haiku | 21.6k | 4s | ✓ | 14 employees |
| 8 | JSON | Haiku | 23.5k | 8s | ✓ | 9 employees |
| 8 | TOON | Haiku | 22.2k | 6s | ✓ | 9 employees |
| 8 | fiche | Haiku | 22.0k | 7s | ✓ | 9 employees |

(To be filled during testing)

---

## Running Totals (Dataset 1, Haiku, 7 questions)

| Format | Avg Tokens | Avg Time | Correct | Notes |
|--------|------------|----------|---------|-------|
| JSON | 23.2k | 4.9s | 6/7 | Baseline |
| TOON | 21.8k | 4.6s | 6/7 | -6% tokens vs JSON |
| fiche | 21.6k | 5.0s | 6/7 | -7% tokens vs JSON |

**Q4 (total salary) failed across all formats** - Haiku can't accurately sum 100 numbers. Model limitation, not format-related.

---

## Conclusions

**Data is clear:** fiche consistently uses fewer tokens than both JSON and TOON on every single question tested.

| Finding | Result |
|---------|--------|
| fiche vs JSON | ~7% fewer tokens |
| fiche vs TOON | ~1% fewer tokens |
| Accuracy | Identical across formats |
| Processing time | Similar (network variance) |

**Key insights from full research:**
1. Newlines are expensive (30% token penalty)
2. Value dictionary compression works
3. ASCII mode beats Unicode for token efficiency
4. Unicode mode valuable for transport safety (collision avoidance)
5. All formats parse correctly - accuracy is format-agnostic
