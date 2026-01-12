# authority_map.md

Authority: README.md is the single product truth.

## Decision rights
- README.md defines product intent, scope, metrics, and roadmap.
- AGENT.md enforces governance, stop conditions, and escalation.
- docs/agents/*.md define domain ownership within README.md scope.
- Code and configuration implement approved decisions only.

## Conflict resolution
1. If conflict exists, defer to README.md.
2. If still unclear, defer to AGENT.md stop conditions and escalate.
3. Domain agents must not override AGENT.md or README.md.

## Explicit precedence
README.md > AGENT.md > docs/agents/*.md > code
