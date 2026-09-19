# Tamizh JARVIS Security Specification (Phase 9 Release Candidate)

## Security Architecture & Defense-in-Depth

Every planned action passes through a 3-stage validation pipeline before tool execution:

```
Planned Tool Action
        │
        ▼
[ 1. ActionValidator ] ──► Sanitizes parameters; detects SQL injection, shell metacharacters (; && | ` $).
        │
        ▼
[ 2. RiskClassifier ] ───► Classifies action into 4 Risk Tiers:
                           • LOW: Read operations (read briefing, weak topics). Auto-approved.
                           • MEDIUM: Non-destructive writes (create task, log study). Auto-approved.
                           • HIGH: Potentially destructive (delete task). Requires explicit user confirmation.
                           • CRITICAL: Prohibited actions (arbitrary shell command, OS formatting). Strictly blocked.
        │
        ▼
[ 3. PermissionManager ] ─► Enforces configuration policies and human-in-the-loop authorization.
```

## Security Status

| Protection Feature | Status | Details |
|---|---|---|
| **No Arbitrary Shell Execution** | ✅ IMPLEMENTED | No tool exists with raw shell execution capability (`bash`, `cmd`, `powershell` disabled). |
| **Parameter Injection Prevention** | ✅ IMPLEMENTED | Regex and pattern checking against command chaining sequences (`rm -rf`, `DROP TABLE`, `;`, `&&`). |
| **High-Risk Confirmation Gate** | ✅ IMPLEMENTED | High-risk actions return `auth=False` unless `user_confirmed=True` is provided. |
| **Credential Masking** | ✅ IMPLEMENTED | API keys (Gemini, local tokens) are masked (`AIza...6789`) and never printed in logs or client payloads. |
| **CORS Origin Restriction** | ✅ IMPLEMENTED | No wildcard (`*`) allowed origins when credentials are enabled. Configurable via `ALLOWED_ORIGINS`. |
| **Error Sanitization** | ✅ IMPLEMENTED | Production mode hides raw internal stack traces; returns user-safe structured JSON errors. |
| **Automated Security Tests** | ✅ IMPLEMENTED | Suite `tests/test_security.py` tests and validates all 4 risk tiers and injection rejections. |
| **OAuth2 Multi-Tenant Auth** | 🟡 PLANNED | Role-based JWT access control for multi-user cloud hosting. |
