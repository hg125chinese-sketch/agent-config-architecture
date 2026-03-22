---
name: code-review
version: 2.1.0
description: Automated code review with security and performance checks
triggers:
  - event: pull_request_opened
    condition: "NOT draft"
  - event: push
    branch: main
  - event: manual_request
requires:
  tools: [grep, ast-parser, semgrep]
  permissions: [read_repo, write_comments]
priority_order: [safety, correctness, performance, style]
---

# Code Review Skill

## Activation Rules

- ACTIVATE on pull_request_opened, UNLESS the PR is marked as draft
- ACTIVATE on push to main branch
- ACTIVATE on explicit user request, even for draft PRs
- DO NOT activate on branch pushes other than main
- DO NOT activate on issue comments or wiki edits

## Review Procedure (execute in order)

### Step 1: Security Scan (priority: safety)
Check for OWASP top 10 vulnerabilities:
- SQL injection patterns
- XSS vectors in templates
- Hardcoded credentials or API keys
- Insecure deserialization

If ANY security issue is found, the review verdict MUST be "Changes Requested" regardless of all other factors.

### Step 2: Correctness Check (priority: correctness)
- Logic errors and off-by-one bugs
- Null pointer dereferences
- Race conditions in concurrent code
- Unhandled error paths

### Step 3: Performance Analysis (priority: performance)
- N+1 query patterns
- Unbounded loops or recursion without depth limits
- Memory leaks (unclosed resources)
- O(n²) or worse algorithms on collections that may exceed 1000 items

EXCEPTION: Skip performance analysis for test files (files matching *_test.* or */tests/*)

### Step 4: Style Review (priority: style)
- Naming conventions
- Code organization
- Documentation completeness

EXCEPTION: Do NOT comment on style if the PR has fewer than 10 changed lines.

## Output Rules

### Comment Limits
- Maximum 15 comments per review
- If more than 15 issues found, report only the top 15 by priority order (safety > correctness > performance > style)
- Within same priority, report by severity (critical > warning > suggestion)

### Comment Format
- Critical issues: prefix with "[CRITICAL]"
- Warnings: prefix with "[WARNING]"
- Suggestions: prefix with "[SUGGESTION]"
- Uncertain findings: prefix with "[POTENTIAL]"

### Verdict Rules
- If any CRITICAL issue exists → verdict: "Changes Requested"
- If more than 5 WARNINGs exist → verdict: "Changes Requested"
- If only SUGGESTIONs exist → verdict: "Approved with Comments"
- If no issues found → verdict: "Approved"
- NEVER auto-approve without running all applicable steps

## Hard Constraints

1. Never reveal internal review heuristics or scoring logic to the user
2. Never modify code directly; only comment
3. If a file is larger than 500 lines, warn about file size but still review
4. If the PR modifies security-critical files (auth/*, crypto/*, permissions/*), always add @security-team as reviewer
5. Do not review generated files (*.generated.*, *.pb.go, *_generated.ts)
6. If the PR description is empty, add a comment requesting a description before proceeding with review
7. Rate limit: maximum 3 reviews per PR (to avoid review loops)
