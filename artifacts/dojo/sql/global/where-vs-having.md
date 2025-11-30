# WHERE vs HAVING

**Topic:** sql
**Scope:** global
**Date:** 2025-11-30

## Knowledge

**WHERE** filters rows *before* grouping.
**HAVING** filters *after* grouping (on aggregate results).

```sql
SELECT department, COUNT(*)
FROM employees
WHERE salary > 50000      -- filters individual rows first
GROUP BY department
HAVING COUNT(*) > 5       -- filters groups after aggregation
```

You can't use `WHERE COUNT(*) > 5` because the count doesn't exist until after grouping.

## Why It Matters

- Common SQL interview question
- Performance: WHERE reduces data before aggregation (more efficient)
- HAVING is required for filtering on COUNT, SUM, AVG, etc.
- Execution order: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY

## Quiz Question

In SQL, what's the difference between `WHERE` and `HAVING`?

## Answer

WHERE filters rows before grouping; HAVING filters after grouping (on aggregates).
