# AumOS Audit Logging

**Classification:** Public | **Version:** 1.0.0 | **Date:** February 2026

---

## Overview

AumOS maintains a comprehensive, immutable audit trail of all security-relevant events across the platform. The audit log is a first-class architectural component — not an afterthought — designed to satisfy the requirements of SOC 2, ISO 27001, HIPAA, and enterprise forensic investigation needs.

---

## Audit Log Architecture

### Log Pipeline

```
Event Source (each microservice)
    │
    ▼
Structured Event Emission (OpenTelemetry + custom audit SDK)
    │
    ▼
aumos-event-bus (Kafka — audit-events topic)
    │
    ├──► aumos-observability (hot storage — Elasticsearch, 1 year)
    │         │
    │         ▼
    │    SIEM Integration (Splunk / Elastic SIEM / Microsoft Sentinel / Chronicle)
    │
    ├──► Immutable Cold Storage (S3 Object Lock WORM — 7 years)
    │         │
    │         ▼
    │    Chain-Signed Archives (cryptographic integrity verification)
    │
    └──► Customer Audit API (real-time streaming + historical query)
```

### Immutability Guarantees

1. **Append-only database table**: Audit log table has no DELETE or UPDATE permissions granted to any application role. Only INSERT is permitted.
2. **Cryptographic chain signing**: Each audit event includes an HMAC-SHA256 over (event_id + timestamp + event_body + hash_of_previous_event). Tampering with any event breaks the chain.
3. **S3 Object Lock (WORM)**: Audit archives in cold storage are stored with Object Lock Compliance mode — cannot be deleted or modified even by bucket owner or MuVeraAI staff for the retention period (7 years).
4. **Independent replication**: Audit logs are replicated to a separate AWS account inaccessible to production services — a compromised production environment cannot reach the audit log replica.
5. **SIEM forwarding**: Logs are forwarded to customer SIEM within 60 seconds of generation — deletion from AumOS systems cannot remove the SIEM copy.

---

## Event Categories and Fields

### Standard Audit Event Schema

```json
{
  "event_id": "uuid-v4",
  "timestamp": "ISO-8601 with milliseconds",
  "event_type": "string (category.action)",
  "severity": "INFO | WARNING | CRITICAL",
  "actor": {
    "type": "USER | SERVICE | AGENT | SYSTEM",
    "id": "string",
    "name": "string",
    "email": "string (for users)",
    "ip_address": "string",
    "user_agent": "string",
    "session_id": "string"
  },
  "tenant_id": "string",
  "resource": {
    "type": "string",
    "id": "string",
    "name": "string"
  },
  "action": "string (CRUD verb or specific action)",
  "result": "SUCCESS | FAILURE | PARTIAL",
  "failure_reason": "string (if FAILURE)",
  "request_id": "string (trace correlation)",
  "previous_state": "object (for mutations, where applicable)",
  "new_state": "object (for mutations, where applicable)",
  "metadata": "object (event-type specific additional fields)",
  "chain_hash": "HMAC-SHA256 of event + previous event hash"
}
```

### Event Types Captured

#### Authentication Events

| Event Type | Trigger | Severity |
|-----------|---------|---------|
| `auth.login.success` | Successful user login | INFO |
| `auth.login.failure` | Failed login attempt | WARNING |
| `auth.login.mfa_success` | MFA challenge passed | INFO |
| `auth.login.mfa_failure` | MFA challenge failed | WARNING |
| `auth.login.lockout` | Account locked after failures | WARNING |
| `auth.sso.assertion_received` | SAML/OIDC assertion received | INFO |
| `auth.session.created` | New session established | INFO |
| `auth.session.terminated` | Session ended (logout or expiry) | INFO |
| `auth.session.revoked` | Session forcefully revoked | WARNING |
| `auth.token.issued` | JWT access token issued | INFO |
| `auth.token.refreshed` | Access token refreshed | INFO |
| `auth.token.revoked` | Token revoked before expiry | WARNING |
| `auth.apikey.used` | API key used for authentication | INFO |
| `auth.apikey.expired` | API key expired | INFO |

#### Authorization Events

| Event Type | Trigger | Severity |
|-----------|---------|---------|
| `authz.access.granted` | Authorization check passed | INFO |
| `authz.access.denied` | Authorization check failed | WARNING |
| `authz.role.assigned` | Role assigned to user | INFO |
| `authz.role.revoked` | Role removed from user | INFO |
| `authz.privilege.escalated` | JIT privilege elevation | WARNING |
| `authz.privilege.expired` | JIT session expired | INFO |
| `authz.policy.evaluated` | OPA policy evaluation (for sensitive resources) | INFO |

#### Data Access Events

| Event Type | Trigger | Severity |
|-----------|---------|---------|
| `data.read` | Data record read (Restricted class) | INFO |
| `data.write` | Data record created or updated | INFO |
| `data.delete` | Data record deleted | WARNING |
| `data.export` | Bulk data export | WARNING |
| `data.import` | Bulk data import | INFO |
| `data.classification.changed` | Data classification modified | WARNING |

#### Administrative Events

| Event Type | Trigger | Severity |
|-----------|---------|---------|
| `admin.user.created` | New user account created | INFO |
| `admin.user.deactivated` | User account disabled | INFO |
| `admin.user.deleted` | User account deleted | WARNING |
| `admin.config.changed` | Platform configuration change | WARNING |
| `admin.integration.created` | New integration configured | INFO |
| `admin.integration.deleted` | Integration removed | WARNING |
| `admin.key.rotated` | Encryption key rotated | INFO |
| `admin.key.destroyed` | Encryption key destroyed | CRITICAL |

#### AI Operation Events

| Event Type | Trigger | Severity |
|-----------|---------|---------|
| `ai.model.invoked` | LLM inference request made | INFO |
| `ai.agent.started` | Agent execution started | INFO |
| `ai.agent.completed` | Agent execution completed | INFO |
| `ai.agent.failed` | Agent execution failed | WARNING |
| `ai.agent.suspended` | Agent suspended by circuit breaker | WARNING |
| `ai.governance.evaluated` | Governance policy evaluated | INFO |
| `ai.governance.blocked` | AI action blocked by governance | WARNING |
| `ai.approval.requested` | Human approval requested | INFO |
| `ai.approval.granted` | Human approval granted | INFO |
| `ai.approval.denied` | Human approval denied | WARNING |

#### Security Events

| Event Type | Trigger | Severity |
|-----------|---------|---------|
| `security.threat.detected` | Threat detection alert | CRITICAL |
| `security.injection.detected` | Prompt injection attempt detected | CRITICAL |
| `security.anomaly.detected` | Behavioral anomaly detected | WARNING |
| `security.ratelimit.hit` | Rate limit threshold reached | WARNING |
| `security.ratelimit.blocked` | Request blocked by rate limiter | WARNING |
| `security.vuln.detected` | Vulnerability scan finding | WARNING |
| `security.breach.suspected` | Potential data breach indicator | CRITICAL |

---

## Audit Log Retention

| Log Category | Hot Retention | Cold Retention | Total |
|-------------|--------------|----------------|-------|
| Authentication events | 1 year | 6 years | 7 years |
| Authorization events | 1 year | 6 years | 7 years |
| Data access events | 1 year | 6 years | 7 years |
| Security events | 1 year | 9 years | 10 years |
| Administrative events | 1 year | 6 years | 7 years |
| AI operation events | 90 days | Configurable | Configurable |

Retention minimums are set to satisfy:
- SOC 2: 1 year minimum
- HIPAA: 6-year requirement for PHI access logs
- SOX: 7-year requirement for financial audit trails
- NIST 800-53 AU family: 3-year minimum for high-impact systems

---

## SIEM Integration

### Supported Integrations

| SIEM Platform | Integration Method | Format |
|--------------|-------------------|--------|
| Splunk | HEC (HTTP Event Collector) | JSON |
| Microsoft Sentinel | Log Analytics Workspace API | JSON + CEF |
| Elastic SIEM | Elasticsearch API | ECS (Elastic Common Schema) |
| IBM QRadar | Syslog over TLS | CEF |
| Google Chronicle | HTTPS ingestion API | UDM (Unified Data Model) |
| Generic Syslog | RFC 5424 syslog over TLS | CEF or JSON |

### Integration Configuration

Customers configure their SIEM endpoint in the AumOS portal. Once configured:
- Real-time forwarding with < 60-second latency
- Retry with exponential backoff on delivery failure (up to 24-hour retry window)
- Delivery confirmation: AumOS tracks and reports successful SIEM delivery
- No duplicate suppression — all events forwarded, deduplication handled by SIEM

---

## Customer Audit API

Customers have programmatic access to their own audit logs:

**Query API**
```
GET /api/v1/audit/events
  ?start_time=ISO-8601
  &end_time=ISO-8601
  &event_type=auth.login.failure
  &actor_id=user-uuid
  &resource_id=resource-uuid
  &page_token=string
  &page_size=100
```

**Streaming API**
- WebSocket endpoint for real-time audit event streaming
- Authenticated with tenant-scoped API key
- Filtering by event_type, severity, resource_type

**Bulk Export**
- Export all events in time range as gzip'd NDJSON
- Signed with tenant's public key if BYOK configured
- Delivery to S3/Azure Blob/GCS or direct download

---

## Log Integrity Verification

Customers and auditors can verify audit log integrity:

1. Download audit log archive (NDJSON + chain hash file)
2. MuVeraAI provides public HMAC verification key (published in DNS as TXT record for discoverability)
3. Verification tool (open-source) re-computes chain hashes and compares
4. Any gap, deletion, or modification is detected

```bash
# Example verification command (open-source tool)
aumos-audit-verify \
  --log-file audit-2026-01.ndjson.gz \
  --hash-file audit-2026-01.chain-hashes \
  --public-key audit-signing-pub.pem
# Output: VERIFIED: 45,832 events, chain intact, no gaps detected
```

---

## Alerting and Monitoring

### Critical Alert Conditions (PagerDuty P1 — 15-minute response)

- `security.breach.suspected` — any event
- `security.injection.detected` — any event
- >10 `auth.login.failure` events for same account in 5 minutes
- Any `admin.key.destroyed` event
- SIEM delivery failure for >5 minutes
- Audit chain hash verification failure

### High Alert Conditions (P2 — 1-hour response)

- `authz.access.denied` — >50 events per user per hour
- `security.anomaly.detected` — any event
- `admin.config.changed` — any production configuration change after hours
- `authz.privilege.escalated` — any JIT escalation for SUPER_ADMIN-level resources
- Audit log replication lag > 5 minutes
