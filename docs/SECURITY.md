# Tamizh JARVIS Security Policies

## Defense-in-Depth Pipeline
Every incoming user instruction and planned tool invocation passes through a strict 3-tier security gate:

```
Tool Request
     │
     ▼
[ ActionValidator ] ─────> Parameter type validation & injection detection (`;`, `&&`, `rm -rf`, `cmd.exe`)
     │
     ▼
[ RiskClassifier ] ──────> Classifies action into 4 tiers:
                           • LOW: Auto-permitted (Read queries, NBA calculation)
                           • MEDIUM: Auto-logged (Task create/update, Study logging)
                           • HIGH: Requires explicit confirmation (Task deletion)
                           • CRITICAL: Strictly blocked (Raw terminal, shell commands, destructive OS ops)
     │
     ▼
[ PermissionManager ] ───> Enforces security settings and user confirmation
```

## Security Guarantees
- **No Unrestricted Shell Access:** Raw bash, powershell, or shell command tools are disabled and blocked.
- **Credential Protection:** API keys and credentials are never exposed in log outputs or client responses.
- **Safe Structured Reasoning:** Decision breakdown only reveals user-facing mathematical factors, not hidden chain-of-thought.
