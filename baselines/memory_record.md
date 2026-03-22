---
name: auth_middleware_rewrite
description: Auth middleware is being rewritten due to legal/compliance requirements around session token storage
type: project
created: 2026-03-15
updated: 2026-03-20
---

The auth middleware rewrite was initiated because legal flagged the current implementation for storing session tokens in a way that doesn't meet new compliance requirements (GDPR Article 32, SOC2 Type II).

**Why:** This is a compliance-driven change, not tech-debt cleanup. The old middleware stored raw session tokens in Redis without encryption-at-rest, and audit logs showed token values in plaintext.

**How to apply:** When making scope decisions on this rewrite, favor compliance over developer ergonomics. Specifically:
- All tokens must be encrypted at rest using AES-256-GCM
- Token rotation must happen every 15 minutes (down from 24 hours)
- Audit logs must redact token values, showing only the last 4 characters
- The migration must be zero-downtime; coordinate with the SRE team on the rollout plan

**Key stakeholders:**
- Legal: Sarah Chen (sign-off required before deploy)
- SRE: Platform team #infra-platform channel
- Timeline: Must be completed before April 1 audit deadline
