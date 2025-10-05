<!--
Sync Impact Report:
Version change: v1.3.0 → v1.4.0
Changes:
  - Added Principle VII: Feature Branch Impact Analysis
  - No existing principles modified
Added sections:
  - New Principle VII
Removed sections:
  - None
Templates requiring updates:
  ✅ .specify/templates/plan-template.md - no changes needed (impact analysis not applicable to planning)
  ✅ .specify/templates/spec-template.md - no changes needed (spec creation not affected by impact analysis)
  ✅ .specify/templates/tasks-template.md - no changes needed (task execution not affected by impact analysis)
Follow-up TODOs: None
-->

# Kira Prolongation Support Constitution

## Core Principles

### I. Simple and Direct
Write the simplest code that solves the problem. No abstractions, patterns, or "best practices" until you actually need them. If it works and you understand it, ship it.

### II. Test What Matters
Only write tests for things that will actually break or are hard to verify by running the app. Manual testing is fine. Don't chase coverage numbers - chase confidence.

### III. Done Over Perfect
Working code beats perfect code. Ship features when they work, not when they're polished. You can always improve it later if needed.

### IV. Use Context7 for Library Research
When planning implementation or creating tasks, use the Context7 MCP server to get up-to-date documentation for libraries and frameworks. This ensures you're using current best practices and APIs instead of outdated information.

### V. TCMB as Single Source of Truth for Exchange Rates
Use only the Central Bank of Turkey (TCMB) as the exchange rate source. Do not implement backup APIs or fallback mechanisms. If TCMB data is unavailable, allow manual entry instead of automatically falling back to less authoritative sources. This ensures data accuracy and consistency with official Turkish financial standards.

**Rationale**: For Turkish rental negotiations, using official central bank rates provides the most defensible and legally sound exchange rate data. Backup APIs may use different methodologies or timing, creating inconsistencies in negotiation arguments.

### VI. Test-Driven Bug Fixes
When a user reports a bug, MUST write a unit test that reproduces the bug first, then fix it. The test serves as regression prevention and validates the fix works. No bug fix commits without accompanying tests.

**Rationale**: User-reported bugs represent real-world failure scenarios that automated tests missed. Capturing them as tests ensures they never return silently and builds confidence in the codebase over time.

### VII. Feature Branch Impact Analysis
When starting a new feature branch as a response to `/specify` command, MUST perform comprehensive impact analysis. Document all existing requirements and explicitly specify what needs to be changed while ensuring other features remain unaffected. This includes identifying dependencies, affected components, and potential side effects before implementation begins.

**Rationale**: Feature changes can have unintended consequences on existing functionality. Explicit impact analysis prevents breaking changes, ensures clear scope boundaries, and maintains system stability. It also provides clear documentation for review and future maintenance.

## Governance

This is a personal project. These principles are guidelines, not laws. Change them whenever they stop being helpful.

**Update this doc if:**
- You keep hitting the same problem
- A principle becomes annoying instead of helpful
- You learn something that changes your approach

**Version**: 1.4.0 | **Ratified**: 2025-10-05 | **Last Amended**: 2025-10-05
