<!--
Sync Impact Report:
Version change: [TEMPLATE] → v1.0.0
Changes:
  - Initial constitution created
  - Principles: 5 pragmatic principles focused on simplicity
  - Added sections: Practical Approach, Development Workflow
  - Removed sections: None (initial version)
Templates updated:
  ✅ .specify/templates/plan-template.md - constitution check references updated
  ✅ .specify/templates/spec-template.md - aligned with pragmatic approach
  ✅ .specify/templates/tasks-template.md - aligned with practical testing
Follow-up TODOs: None
-->

# Kira Prolongation Support Constitution

## Core Principles

### I. Keep It Simple
Start with the simplest solution that works. No abstractions, patterns, or frameworks until you actually need them. Write straightforward code that solves the problem at hand. If you find yourself adding layers or complexity "for the future," stop and reconsider.

### II. Working Code First
Ship working features before perfecting them. A working MVP beats a perfect plan. Get something running, test it manually, iterate based on real usage. Premature optimization and gold-plating waste time.

### III. Practical Testing
Write tests for things that break or are hard to verify manually. Don't dogmatically test everything. Integration tests that verify real user flows are more valuable than 100% unit test coverage. Tests should give confidence, not ceremony.

### IV. Clear Over Clever
Code should be obvious to read and understand. Avoid clever tricks, complex abstractions, or showing off. If you need to explain how it works, it's probably too clever. Future you (or your collaborators) will thank you for boring, clear code.

### V. Document What Matters
Document the "why" behind non-obvious decisions. Skip the obvious stuff. A good README and inline comments for tricky parts beat comprehensive API docs that nobody reads. Focus on helping people get started quickly.

## Practical Approach

### What to Avoid
- Don't create abstractions before you have 3+ use cases
- Don't add dependencies without checking if you can solve it simply yourself
- Don't write boilerplate "just in case" (helpers, utils, base classes before needed)
- Don't split code into multiple files until a single file gets unwieldy
- Don't implement features you "might need later"

### What to Do
- Solve the immediate problem with the simplest code
- Add complexity only when the pain of NOT having it is clear
- Refactor when you see duplication the third time
- Keep functions and files small enough to understand easily
- Use standard tools and patterns from the ecosystem

## Development Workflow

### Getting Started
1. Write a clear spec of what the feature should do (user perspective)
2. Sketch out a simple implementation plan
3. Build it the straightforward way
4. Test it manually and with a few automated tests for critical paths
5. Ship it and learn from real usage

### Code Reviews (if collaborating)
Focus on:
- Is it clear what this does?
- Are there obvious bugs?
- Is it simpler than it needs to be or more complex?

Don't nitpick:
- Style preferences (use a formatter)
- Micro-optimizations
- Theoretical edge cases

### When to Refactor
- Code is hard to understand or modify
- You're copying the same logic for the third time
- A file is too big to scan quickly
- Tests are brittle and break for unrelated changes

## Technology Choices

Choose boring, proven technologies. Prefer:
- Languages/frameworks you already know
- Established tools with good documentation
- Standard patterns from the community
- Simple deployment and infrastructure

Avoid:
- Latest trendy tech "to learn it"
- Complex architectures (microservices, event sourcing unless actually needed)
- Custom solutions when good libraries exist
- Over-engineering for scale you don't have

## Governance

This constitution exists to keep the project simple and practical. It should evolve based on real pain points, not theoretical concerns.

### Amendment Process
- Propose changes when you repeatedly hit the same problem
- Discuss with collaborators (if any)
- Update this document with clear reasoning
- Bump version appropriately

### Version Control
- MAJOR: Remove or fundamentally change a principle
- MINOR: Add new principle or major section
- PATCH: Clarify wording, fix typos, minor refinements

### Compliance
This isn't a bureaucratic checklist. Use good judgment. The spirit is:
**Build useful things simply, don't overcomplicate.**

**Version**: 1.0.0 | **Ratified**: 2025-10-05 | **Last Amended**: 2025-10-05
