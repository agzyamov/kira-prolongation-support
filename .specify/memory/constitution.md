<!--
Sync Impact Report:
Version change: v1.5.0 → v1.6.0
Changes:
  - Enhanced Principle VIII: Phase-Based Commits with enforcement mechanisms
  - No existing principles modified
Added sections:
  - Enhanced Principle VIII with enforcement
Removed sections:
  - None
Templates requiring updates:
  ✅ .specify/templates/plan-template.md - no changes needed (phase commits not applicable to planning)
  ✅ .specify/templates/spec-template.md - no changes needed (spec creation not affected by phase commits)
  ✅ .specify/templates/tasks-template.md - no changes needed (task execution not affected by phase commits)
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

### VIII. Phase-Based Commits
MUST commit implementation work after completing each phase (Setup, Tests, Core Implementation, Integration, Polish). Each commit should represent a working state of the application with clear, descriptive commit messages. This ensures progress is preserved, enables easy rollback if needed, and maintains a clean development history.

**Enforcement**: 
- Implementation MUST halt if more than one phase is completed without a commit
- Each phase completion MUST be verified by running tests before committing
- Commit messages MUST follow format: `feat: complete [Phase Name] - [brief description]`
- If implementation continues without phase commits, the work MUST be rolled back to the last commit

**Rationale**: Phase-based commits provide natural checkpoints during development, making it easier to track progress, debug issues, and collaborate. They also ensure that working states are preserved even if later phases encounter problems, reducing the risk of losing completed work. Enforcement prevents accumulation of uncommitted changes that could lead to data loss or debugging difficulties.

## Governance

This is a personal project. These principles are guidelines, not laws. Change them whenever they stop being helpful.

**Update this doc if:**
- You keep hitting the same problem
- A principle becomes annoying instead of helpful
- You learn something that changes your approach

**Version**: 1.6.0 | **Ratified**: 2025-10-05 | **Last Amended**: 2025-10-05
