# Ideas

## Zion Enhancements

### Project Status Field
- **Context:** Compress program needs to know which projects are active vs closed
- **Problem:** Currently no status field in projects table
- **Solution:** Add `status` column (active/dormant/closed) to projects schema
- **Benefit:** Zion Control can skip archiving RAM for closed projects, keep working notes for active ones
