---
name: code-review
version: 2.1.0
description: Automated code review with security and performance checks
triggers:
  - on_pr_open
  - on_push_to_main
requires:
  tools:
    - grep
    - ast-parser
  permissions:
    - read_repo
    - write_comments
---

# Code Review Skill

## When to activate

Activate this skill when a pull request is opened or when code is pushed to the main branch. Do NOT activate for draft PRs unless explicitly requested.

## Behavior

1. **Security scan**: Check for OWASP top 10 vulnerabilities
   - SQL injection patterns
   - XSS vectors
   - Hardcoded credentials
2. **Performance check**: Identify potential N+1 queries, unbounded loops, and memory leaks
3. **Style compliance**: Verify code follows project conventions

## Output format

Provide feedback as inline comments on the PR. Group issues by severity:
- 🔴 Critical: Must fix before merge
- 🟡 Warning: Should fix, but not blocking
- 🟢 Suggestion: Optional improvement

## Constraints

- Never auto-approve PRs
- Maximum 20 comments per review to avoid noise
- If unsure about a finding, prefix with "Potential issue:"
