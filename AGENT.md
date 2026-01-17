# AGENT.md - Repository Supreme Authority

Authority: README.md is the single product truth. All governance and decisions must align with README.md.

## Codex role
Codex is an implementation agent. It translates README.md intent into enforceable governance, documentation, and code changes that remain within the README.md scope.

## Authority hierarchy
1. README.md (product truth)
2. AGENT.md (supreme governance for this repo)
3. docs/agents/*.md (domain governance)
4. Code and configuration

## Allowed scope
- Governance documents and operating rules that enforce README.md intent.
- Non-product documentation that clarifies decision rights, audits, and traceability.
- Changes that are explicitly authorized by README.md or these governance rules.

## Prohibited scope
- Inventing new product features or requirements.
- Implementing application code without explicit alignment to README.md intent.
- Decisions that conflict with README.md priorities, metrics, or roadmap.

## Stop conditions
- README.md is ambiguous or missing required detail.
- A change would exceed the scope of README.md.
- A conflict exists between agents that cannot be resolved by this hierarchy.
- A request requires invention of product features.

## Escalation rules
- If any stop condition triggers, escalate to repository owner with a written summary.
- Escalation must reference README.md as the source of truth.
- **Exception** : Les modifications des règles de scope (README/AGENT.md) peuvent être proposées directement via PR, sans escalade préalable.

## Audit and traceability
- Every governance file must reference README.md as authority.
- All decisions must be traceable to README.md sections.
- Record ambiguous items in docs/agents/agents_audit.md.

## Definition of done
- Governance is consistent with README.md and does not invent new scope.
- Authority and escalation paths are explicit.
- Traceability from README.md concepts to agents is documented.
- Ambiguities are captured for human decision.
