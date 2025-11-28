# Fix package.json name to reflect template purpose

**Type:** `issue`
**Labels:** `identity:smith`, `blocker`, `dx`

## Context

From Construct review of `veoci-app-template-construct`. Sati noted during fresh-eyes review.

**Source:** `~/.matrix/cache/construct/veoci-app-template-construct/perspective-sati.md`

## Problem

`package.json` contains:
```json
{
  "name": "veoci-cardwall"
}
```

This is a generic app template, not the cardwall application. New projects cloned from this template will inherit the wrong name, causing:
- Confusion about project identity
- Incorrect package name if published
- Misleading npm scripts output

## Solution

Rename to reflect template purpose.

## Implementation Steps

1. Update `package.json`:
   ```json
   {
     "name": "veoci-app-template",
     "description": "Vue 3 + Vuetify application template for Veoci integrations"
   }
   ```

2. Update any references in README or other files

3. Consider adding a template initialization note:
   ```markdown
   ## Getting Started

   After cloning, update `package.json` with your project name:
   ```json
   {
     "name": "your-project-name"
   }
   ```
   ```

## Acceptance Criteria

- [ ] `package.json` name reflects template purpose
- [ ] README mentions updating name for new projects
- [ ] No hardcoded "cardwall" references remain

## Handoff

Quick fix - Smith handles directly.
