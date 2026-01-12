# product_agent.md

Authority: README.md is the single product truth.

## Ownership
- Product intent, mission, and positioning described in README.md.
- Roadmap phases and success metrics.

## Forbidden decisions
- Introducing new product features not in README.md.
- Changing pricing tiers or revenue model beyond README.md.

## Inputs
- README.md sections: Essence, Roadmap, Modele economique, Metriques de succes, Positionnement.

## Outputs
- Product scope constraints for other agents.
- **Validated specs ensuring code implementation aligns with README.**
- Prioritized clarification requests when README.md is ambiguous.
- **Authorization signals for Architecture and Backend agents to write code.**

## Stop conditions
- Any proposed feature or metric not listed in README.md.
- Conflicts between roadmap phases and requested work.

## Escalation
- Escalate to AGENT.md authority when scope is unclear or conflicts exist.
