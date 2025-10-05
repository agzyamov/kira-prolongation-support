<!--
Sync Impact Report:
Version change: v1.4.1 → v1.5.0
Changes:
  - Added Principle VIII: Specify Command Branch Management
  - No existing principles modified
Added sections:
  - New Principle VIII
Removed sections:
  - None
Templates requiring updates:
  ✅ .specify/templates/plan-template.md - no changes needed (branch management not applicable to planning)
  ✅ .specify/templates/spec-template.md - no changes needed (spec creation already handles branch management)
  ✅ .specify/templates/tasks-template.md - no changes needed (task execution not affected by branch management)
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

### VII. Latest Stable Dependencies
Pin all dependencies to their latest stable releases as of September 2025. Use specific version numbers in requirements.txt, not version ranges. Use Streamlit 1.50.0 as the web framework. Regularly update dependencies to maintain security patches and bug fixes while ensuring compatibility.

**Rationale**: Specific version pinning ensures reproducible builds and prevents unexpected breaking changes from automatic updates. Using September 2025 as the baseline ensures we start with recent, well-tested versions that include the latest security patches and performance improvements. Streamlit 1.50.0 provides the latest features and stability for the web interface.

### VIII. Specify Command Branch Management
The `/specify` command MUST continue working on the current specification branch until it is merged to main. Only create new feature branches after the current specification has been merged to main. This prevents branch proliferation and maintains a clean development workflow.

**Rationale**: Creating multiple specification branches before completing and merging the current one leads to confusion and scattered work. This principle ensures focus on completing one specification at a time and maintains a linear development progression.

## Governance

This is a personal project. These principles are guidelines, not laws. Change them whenever they stop being helpful.

**Update this doc if:**
- You keep hitting the same problem
- A principle becomes annoying instead of helpful
- You learn something that changes your approach

**Version**: 1.5.0 | **Ratified**: 2025-10-05 | **Last Amended**: 2025-10-05
