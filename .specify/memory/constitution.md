<!--
SYNC IMPACT REPORT
==================
Version Change: 0.0.0 → 1.0.0 (Initial Constitution)
Date: 2025-11-08

Modified Principles:
- N/A (Initial creation)

Added Sections:
- Core Principles (5 principles established)
- Technical Standards
- Development Workflow
- Governance

Removed Sections:
- N/A (Initial creation)

Templates Updated:
✅ .specify/templates/plan-template.md - Compatible (has Constitution Check section)
✅ .specify/templates/spec-template.md - Compatible (follows TDD principles)
✅ .specify/templates/tasks-template.md - Compatible (supports user story priorities and TDD)

Follow-up TODOs:
- None
-->

# doit Constitution

## Core Principles

### I. Simplicity First

Keep the codebase simple and focused. Follow YAGNI (You Aren't Gonna Need It) principles - build only what is currently needed, not what might be needed in the future. Avoid over-engineering solutions. Start with the simplest implementation that works and refactor only when complexity is justified by actual requirements.

**Rationale**: Simpler code is easier to understand, maintain, debug, and extend. Premature optimization and unnecessary abstraction create technical debt without delivering immediate value.

### II. Code Quality

Write clean, readable, and maintainable code. All functions and modules MUST include proper documentation explaining their purpose, parameters, and return values. Use meaningful, descriptive names for variables, functions, and classes. Follow Python PEP 8 style guidelines for consistency. Code MUST be reviewed before merging.

**Rationale**: High-quality code reduces bugs, speeds up onboarding, and makes collaboration effective. Well-documented code serves as living documentation that stays accurate.

### III. Test-Driven Development (NON-NEGOTIABLE)

TDD is mandatory for all features. The development cycle MUST follow: Write tests → Get user approval → Verify tests fail → Implement code → Verify tests pass → Refactor. All features MUST have corresponding tests before implementation begins. Tests MUST fail initially to prove they test real behavior.

**Rationale**: TDD ensures code correctness, prevents regressions, improves design through testability requirements, and provides living documentation of expected behavior. Writing tests first forces clarity about requirements.

### IV. Version Control Best Practices

Use semantic versioning (MAJOR.MINOR.PATCH) for all releases. MAJOR for breaking changes, MINOR for new features, PATCH for bug fixes. Write clear, descriptive commit messages following conventional commit format (e.g., "feat:", "fix:", "docs:"). Review all changes before committing. Create feature branches for new work.

**Rationale**: Clear version signals help users understand impact of updates. Good commit messages enable effective debugging, collaboration, and project history comprehension.

### V. Web Application Standards

Follow OWASP Top 10 security best practices. Validate all user inputs. Implement proper authentication and authorization. Use HTTPS for all communications. Ensure responsive design that works across devices. Implement comprehensive error handling with user-friendly messages. Maintain API documentation for all endpoints with request/response examples.

**Rationale**: Web security is non-negotiable - vulnerabilities put users at risk. Good UX across devices maximizes accessibility. Clear API docs enable integration and reduce support burden.

## Technical Standards

### Technology Stack Requirements

- **Language**: Python 3.11+ for all backend code
- **Framework**: Use established frameworks appropriate for web development (e.g., Flask, FastAPI, Django)
- **Testing**: pytest for all test suites
- **Code Quality**: Use linters (pylint/flake8) and formatters (black) to maintain consistency
- **Documentation**: Use docstrings for all public functions, classes, and modules

### Security & Compliance

- All dependencies MUST be kept up to date
- Security vulnerabilities MUST be addressed within 48 hours of discovery
- Sensitive data (API keys, passwords) MUST NOT be committed to version control
- Use environment variables or secure vaults for configuration secrets
- Regular security audits MUST be performed before major releases

## Development Workflow

### Code Review Process

- All code changes MUST go through pull request review before merging
- At least one approval required for merging
- Automated tests MUST pass before merge
- Pull requests SHOULD be small and focused on a single concern

### Testing Requirements

- Unit tests for all business logic
- Integration tests for API endpoints and database operations
- Contract tests for external service interactions
- Tests MUST maintain minimum 80% code coverage for new features

### Deployment Process

- Use continuous integration for automated testing
- Staging environment MUST mirror production
- Deploy to staging first, validate, then production
- Maintain rollback capability for all deployments

## Governance

This constitution supersedes all other development practices. All code changes, architectural decisions, and feature implementations MUST comply with these principles.

**Amendment Process**: Constitution amendments require:
1. Written justification explaining the need for change
2. Impact analysis on existing code and processes
3. Team approval through documented consensus
4. Migration plan if existing code needs updates

**Compliance Review**: All pull requests MUST verify compliance with constitutional principles. Violations of Simplicity First principle MUST be justified in the PR description explaining why additional complexity is necessary.

**Constitution Evolution**: As the project grows, principles may be refined but never weakened. The Test-Driven Development principle is NON-NEGOTIABLE and cannot be removed or diluted.

**Version**: 1.0.0 | **Ratified**: 2025-11-08 | **Last Amended**: 2025-11-08
