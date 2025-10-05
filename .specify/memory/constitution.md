<!--
Sync Impact Report:
Version change: v1.1.0 → v1.2.0
Changes:
  - Added Principle V: TCMB as Single Source of Truth for Exchange Rates
  - Technical constraint: Remove backup API fallback, rely only on official Central Bank data
  - No existing principles modified
Added sections:
  - New Principle V
Removed sections:
  - None
Templates requiring updates:
  ✅ .specify/templates/plan-template.md - no changes needed (technical decision documented)
  ✅ .specify/templates/spec-template.md - no changes needed (NFR-002 already specifies source flexibility)
  ⚠ src/services/exchange_rate_service.py - REQUIRES CODE UPDATE to remove backup API fallback
  ⚠ specs/001-problem-statement-i/spec.md - SHOULD update NFR-002 to reflect TCMB-only decision
Follow-up TODOs:
  - Remove backup API code from ExchangeRateService
  - Update spec.md NFR-002 to document TCMB-only approach
  - Update README.md if it mentions backup APIs
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

## Governance

This is a personal project. These principles are guidelines, not laws. Change them whenever they stop being helpful.

**Update this doc if:**
- You keep hitting the same problem
- A principle becomes annoying instead of helpful
- You learn something that changes your approach

**Version**: 1.2.0 | **Ratified**: 2025-10-05 | **Last Amended**: 2025-10-05
