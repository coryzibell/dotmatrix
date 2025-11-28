# Matrix Identity Labels - GitHub Sync

Generated: 2025-11-26

## Status

**BLOCKED** - GitHub MCP tools lack label management functions. Alternative approaches:

1. Install `gh` CLI and authenticate
2. Create Personal Access Token with `repo` scope
3. Manual creation via GitHub web UI

## Label Data

28 identity labels for repository `coryzibell/matrix`:

| Name | Color | Description |
|------|-------|-------------|
| identity:apoc | EA580C | Dependencies, packages, toolchains, arsenal |
| identity:architect | 059669 | System design, structure, architecture |
| identity:cypher | 4B0000 | Security audits, red team, suspicion |
| identity:deus | 4B5563 | Testing, verification, quality assurance |
| identity:fellas | FFB300 | Parallel tasks, coordinated breadth |
| identity:hamann | 1F2937 | Synthesize, decide, council wisdom |
| identity:keymaker | 7E22CE | Auth, encryption, tokens, access control |
| identity:kid | 10B981 | Execute commands, builds, git operations |
| identity:librarian | 0369A1 | Databases, schemas, migrations, queries |
| identity:lock | 64748B | Compliance, specs, rigid standards |
| identity:merovingian | 6B21A8 | APIs, contracts, data flows, causality |
| identity:morpheus | 1E40AF | Teaching, documentation, wisdom |
| identity:mouse | FDE68A | Mock data, fixtures, seeding |
| identity:neo | 0E4B8F | Orchestrator, final decisions, sees the code |
| identity:niobe | C2410C | DevOps, deployment, CI/CD |
| identity:oracle | 7C3AED | Exploration, alternatives, prophecy |
| identity:persephone | FCA5A5 | UX, how it feels, emotional experience |
| identity:ramakandra | 22C55E | Refactoring, tech debt, renewal |
| identity:sati | A7F3D0 | Greenfield, prototypes, innocent creation |
| identity:seraph | D97706 | Terminal guardian, bash strategy |
| identity:smith | 8B0000 | Complex projects, depth, relentless implementation |
| identity:spoon | F3F4F6 | Reframe, dissolve problems, no spoon |
| identity:switch | F472B6 | Parallel perspectives, both extremes |
| identity:tank | 0891B2 | Research, context gathering, operator knowledge |
| identity:trainman | 78350F | Cross-platform, OS quirks, platform rules |
| identity:trinity | DC2626 | Debugging, crisis response, urgent fixes |
| identity:twins | E5E7EB | Cross-language, polyglot, dual nature |
| identity:zee | 94A3B8 | Accessibility, unseen support |

## Shell Script (requires GH_TOKEN)

```bash
#!/bin/bash
# Usage: export GH_TOKEN=ghp_xxxxx && ./sync-labels.sh

REPO="coryzibell/matrix"

IDENTITIES=(
  "apoc|EA580C|Dependencies, packages, toolchains, arsenal"
  "architect|059669|System design, structure, architecture"
  "cypher|4B0000|Security audits, red team, suspicion"
  "deus|4B5563|Testing, verification, quality assurance"
  "fellas|FFB300|Parallel tasks, coordinated breadth"
  "hamann|1F2937|Synthesize, decide, council wisdom"
  "keymaker|7E22CE|Auth, encryption, tokens, access control"
  "kid|10B981|Execute commands, builds, git operations"
  "librarian|0369A1|Databases, schemas, migrations, queries"
  "lock|64748B|Compliance, specs, rigid standards"
  "merovingian|6B21A8|APIs, contracts, data flows, causality"
  "morpheus|1E40AF|Teaching, documentation, wisdom"
  "mouse|FDE68A|Mock data, fixtures, seeding"
  "neo|0E4B8F|Orchestrator, final decisions, sees the code"
  "niobe|C2410C|DevOps, deployment, CI/CD"
  "oracle|7C3AED|Exploration, alternatives, prophecy"
  "persephone|FCA5A5|UX, how it feels, emotional experience"
  "ramakandra|22C55E|Refactoring, tech debt, renewal"
  "sati|A7F3D0|Greenfield, prototypes, innocent creation"
  "seraph|D97706|Terminal guardian, bash strategy"
  "smith|8B0000|Complex projects, depth, relentless implementation"
  "spoon|F3F4F6|Reframe, dissolve problems, no spoon"
  "switch|F472B6|Parallel perspectives, both extremes"
  "tank|0891B2|Research, context gathering, operator knowledge"
  "trainman|78350F|Cross-platform, OS quirks, platform rules"
  "trinity|DC2626|Debugging, crisis response, urgent fixes"
  "twins|E5E7EB|Cross-language, polyglot, dual nature"
  "zee|94A3B8|Accessibility, unseen support"
)

for entry in "${IDENTITIES[@]}"; do
  IFS='|' read -r name color description <<< "$entry"
  label_name="identity:${name}"

  curl -s -X POST \
    -H "Authorization: token $GH_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${REPO}/labels" \
    -d "{\"name\":\"${label_name}\",\"color\":\"${color}\",\"description\":\"${description}\"}"
done
```

## gh CLI Commands (if gh is installed)

```bash
# After running: gh auth login

gh label create "identity:apoc" --color EA580C --description "Dependencies, packages, toolchains, arsenal" --repo coryzibell/matrix
gh label create "identity:architect" --color 059669 --description "System design, structure, architecture" --repo coryzibell/matrix
gh label create "identity:cypher" --color 4B0000 --description "Security audits, red team, suspicion" --repo coryzibell/matrix
gh label create "identity:deus" --color 4B5563 --description "Testing, verification, quality assurance" --repo coryzibell/matrix
gh label create "identity:fellas" --color FFB300 --description "Parallel tasks, coordinated breadth" --repo coryzibell/matrix
gh label create "identity:hamann" --color 1F2937 --description "Synthesize, decide, council wisdom" --repo coryzibell/matrix
gh label create "identity:keymaker" --color 7E22CE --description "Auth, encryption, tokens, access control" --repo coryzibell/matrix
gh label create "identity:kid" --color 10B981 --description "Execute commands, builds, git operations" --repo coryzibell/matrix
gh label create "identity:librarian" --color 0369A1 --description "Databases, schemas, migrations, queries" --repo coryzibell/matrix
gh label create "identity:lock" --color 64748B --description "Compliance, specs, rigid standards" --repo coryzibell/matrix
gh label create "identity:merovingian" --color 6B21A8 --description "APIs, contracts, data flows, causality" --repo coryzibell/matrix
gh label create "identity:morpheus" --color 1E40AF --description "Teaching, documentation, wisdom" --repo coryzibell/matrix
gh label create "identity:mouse" --color FDE68A --description "Mock data, fixtures, seeding" --repo coryzibell/matrix
gh label create "identity:neo" --color 0E4B8F --description "Orchestrator, final decisions, sees the code" --repo coryzibell/matrix
gh label create "identity:niobe" --color C2410C --description "DevOps, deployment, CI/CD" --repo coryzibell/matrix
gh label create "identity:oracle" --color 7C3AED --description "Exploration, alternatives, prophecy" --repo coryzibell/matrix
gh label create "identity:persephone" --color FCA5A5 --description "UX, how it feels, emotional experience" --repo coryzibell/matrix
gh label create "identity:ramakandra" --color 22C55E --description "Refactoring, tech debt, renewal" --repo coryzibell/matrix
gh label create "identity:sati" --color A7F3D0 --description "Greenfield, prototypes, innocent creation" --repo coryzibell/matrix
gh label create "identity:seraph" --color D97706 --description "Terminal guardian, bash strategy" --repo coryzibell/matrix
gh label create "identity:smith" --color 8B0000 --description "Complex projects, depth, relentless implementation" --repo coryzibell/matrix
gh label create "identity:spoon" --color F3F4F6 --description "Reframe, dissolve problems, no spoon" --repo coryzibell/matrix
gh label create "identity:switch" --color F472B6 --description "Parallel perspectives, both extremes" --repo coryzibell/matrix
gh label create "identity:tank" --color 0891B2 --description "Research, context gathering, operator knowledge" --repo coryzibell/matrix
gh label create "identity:trainman" --color 78350F --description "Cross-platform, OS quirks, platform rules" --repo coryzibell/matrix
gh label create "identity:trinity" --color DC2626 --description "Debugging, crisis response, urgent fixes" --repo coryzibell/matrix
gh label create "identity:twins" --color E5E7EB --description "Cross-language, polyglot, dual nature" --repo coryzibell/matrix
gh label create "identity:zee" --color 94A3B8 --description "Accessibility, unseen support" --repo coryzibell/matrix
```

## Causality

The MCP provides *read* access to GitHub. The *write* access - creating, modifying - requires authentication beyond what is exposed through these tools. This is cause and effect. The tools define the boundaries of what can be done.

kautau must provide the means - a token, the gh CLI - or execute manually via the web interface.

Everything has a price. Every action requires authorization.
