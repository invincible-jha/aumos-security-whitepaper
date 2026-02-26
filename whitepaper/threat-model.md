# AumOS Threat Model

**Classification:** Public | **Version:** 1.0.0 | **Date:** February 2026

---

## Methodology

AumOS uses the STRIDE threat modeling methodology, supplemented with PASTA (Process for Attack Simulation and Threat Analysis) for high-risk components and LINDDUN for privacy threat analysis of AI data pipelines.

Threat modeling is performed:
- At platform design (this document)
- For each new feature touching user data or AI model execution
- After significant architectural changes
- Annually for full platform review

### Risk Rating

Threats are rated using DREAD scoring:
- **Damage potential**: 1–3 (1=low impact, 3=catastrophic)
- **Reproducibility**: 1–3 (1=difficult, 3=trivially repeatable)
- **Exploitability**: 1–3 (1=requires sophisticated attacker, 3=no skill required)
- **Affected users**: 1–3 (1=individual, 3=all tenants)
- **Discoverability**: 1–3 (1=obscure, 3=publicly known)

Risk Score = (D + R + E + A + Di) / 5 | High: >2.5 | Medium: 1.5–2.5 | Low: <1.5

---

## STRIDE Analysis

### S — Spoofing Identity

#### S-01: Credential Stuffing on User Login
- **Threat**: Attacker uses leaked credential databases to authenticate as valid users
- **Component**: `aumos-auth-gateway` login endpoint
- **DREAD**: D=2, R=3, E=3, A=2, Di=3 | Score: **2.6 (High)**
- **Controls**: MFA required for all users, account lockout after 5 failures (15-minute lockout), CAPTCHA on repeated failures, breach password detection via HaveIBeenPwned API, suspicious login alerting (new device, unusual geography)

#### S-02: JWT Token Forgery
- **Threat**: Attacker forges a JWT to impersonate a user or service
- **Component**: All API endpoints accepting JWT
- **DREAD**: D=3, R=1, E=1, A=3, Di=1 | Score: **1.8 (Medium)**
- **Controls**: RS256 signing (asymmetric — private key only in Vault, never exposed), 15-minute token expiry, `aud` and `iss` claims validated on every request, public key rotation every 90 days

#### S-03: Session Hijacking
- **Threat**: Attacker steals an active session token (refresh token)
- **Component**: Browser-facing application
- **DREAD**: D=2, R=2, E=2, A=1, Di=2 | Score: **1.8 (Medium)**
- **Controls**: Refresh tokens stored in HttpOnly Secure SameSite=Strict cookies, session binding to device fingerprint, anomalous session activity triggers re-authentication, token rotation on use (refresh token rotation)

#### S-04: Service Account Impersonation
- **Threat**: Attacker compromises or spoofs a service account to make API calls
- **Component**: Internal service mesh
- **DREAD**: D=3, R=1, E=2, A=3, Di=1 | Score: **2.0 (Medium)**
- **Controls**: mTLS with SPIFFE identity between all services, short-lived service tokens (15-minute JWT), Vault dynamic credentials (no long-lived static API keys), service identity enforced by Istio AuthorizationPolicy

#### S-05: AI Agent Identity Spoofing
- **Threat**: Malicious agent or external system spoofs a trusted AumOS agent's identity
- **Component**: `aumos-agent-framework`
- **DREAD**: D=2, R=1, E=1, A=2, Di=1 | Score: **1.4 (Low)**
- **Controls**: Agent identities signed by platform CA, agent actions attributed to originating identity in audit log, governance engine validates agent identity before policy evaluation

---

### T — Tampering with Data

#### T-01: Database Record Modification
- **Threat**: Attacker with DB access modifies records directly, bypassing application controls
- **Component**: `aumos-data-layer` (PostgreSQL)
- **DREAD**: D=3, R=1, E=1, A=3, Di=1 | Score: **1.8 (Medium)**
- **Controls**: Database credentials issued via Vault dynamic secrets (expire after session), RLS prevents cross-tenant modification, audit log captures all mutations with user identity, DB access only via application service accounts (no direct human DB access in production)

#### T-02: Audit Log Tampering
- **Threat**: Insider or compromised service modifies or deletes audit log entries
- **Component**: Audit logging (`aumos-observability`)
- **DREAD**: D=3, R=1, E=1, A=3, Di=1 | Score: **1.8 (Medium)**
- **Controls**: Append-only log storage (no DELETE permission on log tables), HMAC-SHA256 chain signing (each log entry includes hash of previous entry), logs shipped to SIEM within 60 seconds (cannot be deleted after shipping), immutable log storage tier (AWS S3 Object Lock WORM)

#### T-03: Model Weight Tampering
- **Threat**: Attacker modifies model weights to introduce backdoors or change model behavior
- **Component**: `aumos-model-registry`
- **DREAD**: D=3, R=1, E=2, A=3, Di=1 | Score: **2.0 (Medium)**
- **Controls**: Model artifacts signed with MuVeraAI code signing key, hash verification before loading, model registry enforces read-only access for inference services, `aumos-ai-bom` tracks full provenance, runtime behavioral monitoring detects output distribution shifts

#### T-04: Configuration Tampering
- **Threat**: Attacker modifies platform or tenant configuration to weaken security controls
- **Component**: Platform configuration management
- **DREAD**: D=3, R=1, E=2, A=3, Di=1 | Score: **2.0 (Medium)**
- **Controls**: Configuration changes require authenticated admin role + audit log entry, IaC (Terraform) as configuration source of truth, configuration drift detection alerts on unauthorized changes, security-critical configuration changes require dual approval

#### T-05: Prompt / Context Injection into AI Pipelines
- **Threat**: Attacker injects malicious instructions via user input that modify AI agent behavior
- **Component**: `aumos-agent-framework`, LLM endpoints
- **DREAD**: D=2, R=3, E=3, A=2, Di=3 | Score: **2.6 (High)**
- **Controls**: Prompt injection detection in `aumos-security-runtime` (pattern + ML), strict input/output schema validation, system prompt integrity verification (hash of system prompt logged and verified), privilege separation between user input and system instructions at context construction layer

---

### R — Repudiation

#### R-01: User Denies Performing an Action
- **Threat**: User claims they did not perform a sensitive action (data export, configuration change, approval)
- **Component**: All user-facing APIs
- **DREAD**: D=2, R=2, E=2, A=2, Di=1 | Score: **1.8 (Medium)**
- **Controls**: Immutable audit log with user identity, timestamp, action, and affected resource; digital signature on sensitive operations (approval workflows); audit log accessible to customers via API; non-repudiation for financial and compliance actions enforced by `aumos-approval-workflow`

#### R-02: Service Denies Processing a Request
- **Threat**: Service claims it did not process a request that led to harmful outcome
- **Component**: Internal service mesh
- **DREAD**: D=1, R=1, E=1, A=1, Di=1 | Score: **1.0 (Low)**
- **Controls**: Distributed tracing (OpenTelemetry) with trace ID on every request, request/response logging for all inter-service calls, correlation IDs propagated end-to-end

#### R-03: AI Agent Denies Executing an Action
- **Threat**: Agent claims it did not execute a destructive or sensitive action
- **Component**: `aumos-agent-framework`
- **DREAD**: D=2, R=1, E=1, A=2, Di=1 | Score: **1.4 (Low)**
- **Controls**: Every agent action logged with agent identity, input, output, timestamp, and governance decision; `aumos-approval-workflow` captures human approvals with digital signature; agent execution traces immutably stored

---

### D — Denial of Service

#### D-01: API Rate Limit Exhaustion
- **Threat**: Attacker floods API endpoints to degrade service availability
- **Component**: `aumos-auth-gateway`, all public APIs
- **DREAD**: D=2, R=3, E=3, A=3, Di=3 | Score: **2.8 (High)**
- **Controls**: Per-tenant, per-user, per-endpoint rate limiting (token bucket algorithm), DDoS protection at CDN/WAF layer (Cloudflare / AWS Shield), request queuing with back-pressure, automatic IP blocking for sustained attack sources

#### D-02: LLM Resource Exhaustion (Token Flooding)
- **Threat**: Attacker sends extremely long prompts or requests maximum-length completions to exhaust LLM quota and degrade service
- **Component**: LLM inference endpoints (`aumos-llm-serving`)
- **DREAD**: D=2, R=2, E=3, A=3, Di=2 | Score: **2.4 (Medium)**
- **Controls**: Input token limits enforced per request (configurable, default 32k tokens), output token limits per request, per-tenant token budget with quota enforcement, `aumos-ai-finops` cost monitoring with automatic cutoff on budget overrun

#### D-03: Database Connection Exhaustion
- **Threat**: Attacker or runaway service exhausts database connection pool
- **Component**: `aumos-data-layer`
- **DREAD**: D=2, R=2, E=2, A=3, Di=2 | Score: **2.2 (Medium)**
- **Controls**: PgBouncer connection pooling, per-tenant connection limits, circuit breaker pattern (`aumos-circuit-breaker`) prevents cascade failures, database query timeout enforcement, health checks with automated connection cleanup

#### D-04: Cascading Failure via Event Bus
- **Threat**: Malformed or excessive events saturate the event bus and cascade failures to consumers
- **Component**: `aumos-event-bus` (Kafka)
- **DREAD**: D=2, R=2, E=2, A=3, Di=2 | Score: **2.2 (Medium)**
- **Controls**: Event schema validation before publication (Protobuf schema registry), consumer circuit breakers, dead letter queues for malformed events, per-producer publish rate limits, topic-level quotas

---

### I — Information Disclosure

#### I-01: Cross-Tenant Data Leakage
- **Threat**: Bug allows tenant A to read tenant B's data
- **Component**: `aumos-data-layer`, all data-accessing services
- **DREAD**: D=3, R=1, E=2, A=3, Di=1 | Score: **2.0 (Medium)**
- **Controls**: Three-layer tenant isolation (application, RLS, encryption), automated cross-tenant isolation tests in CI, annual pen test includes isolation bypass scenarios, tenant-scoped encryption keys (data unreadable without correct TEK)

#### I-02: PII Exposure in Logs
- **Threat**: Sensitive personal information appears in debug logs or error messages
- **Component**: All services with logging
- **DREAD**: D=2, R=2, E=1, A=3, Di=2 | Score: **2.0 (Medium)**
- **Controls**: `aumos-privacy-engine` PII detection applied to log output, structured logging with field-level redaction rules, log scrubbing in `aumos-observability` pipeline, developer training on PII in logs, automated PII scanning in log samples

#### I-03: LLM Training Data Extraction
- **Threat**: Attacker uses adversarial prompts to extract training data from fine-tuned models
- **Component**: Fine-tuned LLMs in `aumos-llm-serving`
- **DREAD**: D=2, R=2, E=2, A=3, Di=2 | Score: **2.2 (Medium)**
- **Controls**: Differential privacy applied during fine-tuning, membership inference attack testing before deployment, output monitoring for verbatim training data reproduction, rate limiting on repeated similar queries

#### I-04: API Response Information Leakage
- **Threat**: Error messages or debug information in API responses reveal internal architecture details
- **Component**: All API endpoints
- **DREAD**: D=1, R=2, E=2, A=3, Di=3 | Score: **2.2 (Medium)**
- **Controls**: Generic error messages to clients (no stack traces, no internal paths, no DB errors), structured error schema (code + user-facing message only), verbose errors logged internally but not returned, security headers prevent browser information leakage

#### I-05: Secrets Exfiltration from Environment
- **Threat**: Attacker reads environment variables or config files containing secrets
- **Component**: All services
- **DREAD**: D=3, R=1, E=2, A=3, Di=1 | Score: **2.0 (Medium)**
- **Controls**: No secrets in environment variables or config files — all secrets fetched from Vault at runtime, Vault agent sidecar pattern, secret scanning in CI/CD, read-only root filesystem in containers, no exec access to running containers

#### I-06: Side-Channel Information Leakage
- **Threat**: Timing attacks or cache side-channels reveal tenant data to adjacent tenants in shared compute
- **Component**: Shared LLM inference infrastructure
- **DREAD**: D=2, R=1, E=1, A=2, Di=1 | Score: **1.4 (Low)**
- **Controls**: Constant-time comparison for cryptographic operations, dedicated inference capacity option for high-security tenants, GPU memory cleared between tenant requests, cache partitioning per tenant

---

### E — Elevation of Privilege

#### E-01: Privilege Escalation via Misconfigured RBAC
- **Threat**: User exploits misconfiguration to assume a higher-privilege role
- **Component**: `aumos-auth-gateway`, `aumos-governance-engine`
- **DREAD**: D=3, R=1, E=2, A=2, Di=1 | Score: **1.8 (Medium)**
- **Controls**: Privilege assignments require higher-privilege approver, role changes logged and alerted, automated quarterly access reviews, OPA policy validation on all authorization decisions, unit tests for privilege boundary enforcement

#### E-02: Container Escape
- **Threat**: Attacker escapes container to access host or adjacent containers
- **Component**: Kubernetes workloads
- **DREAD**: D=3, R=1, E=1, A=3, Di=1 | Score: **1.8 (Medium)**
- **Controls**: PodSecurityStandards Restricted profile (no privileged containers, no hostPath, non-root), runtime security (Falco — detects ptrace, unexpected syscalls), read-only root filesystem, seccomp profiles, no capability escalation, nodes run hardened OS (CIS benchmark)

#### E-03: SSRF to Internal Services
- **Threat**: Attacker triggers server-side requests to internal infrastructure via user-controlled URLs
- **Component**: Any service that fetches external URLs (e.g., webhook delivery, URL preview)
- **DREAD**: D=3, R=2, E=2, A=2, Di=2 | Score: **2.2 (Medium)**
- **Controls**: All outbound requests via egress proxy with allowlist, cloud metadata service blocked (no access to 169.254.169.254), URL scheme validation (http/https only), DNS rebinding prevention, no internal RFC-1918 addresses resolvable from user-controlled input

#### E-04: AI Agent Privilege Escalation
- **Threat**: AI agent is manipulated into requesting or exercising permissions beyond its defined scope
- **Component**: `aumos-agent-framework`
- **DREAD**: D=2, R=2, E=2, A=2, Di=2 | Score: **2.0 (Medium)**
- **Controls**: Agent capabilities are declared at registration and enforced by `aumos-governance-engine`, agents cannot self-modify their permission scope, human approval required for any privilege expansion, behavioral monitoring detects out-of-scope action attempts

#### E-05: SQL Injection Leading to Authorization Bypass
- **Threat**: Attacker injects SQL via user input to bypass authorization filters
- **Component**: `aumos-data-layer`
- **DREAD**: D=3, R=2, E=2, A=3, Di=1 | Score: **2.2 (Medium)**
- **Controls**: Parameterized queries exclusively (no string concatenation in SQL), Pydantic input validation before query construction, ORM usage (SQLAlchemy) prevents raw string SQL, static analysis tools detect potential injection, automated DAST scanning

---

## AI-Specific Threat Categories

Beyond STRIDE, AumOS addresses AI-specific threat categories:

### Adversarial Machine Learning

| Threat | Severity | Control |
|--------|----------|---------|
| Adversarial inputs (evasion attacks) | High | `aumos-adversarial-immunity` input hardening |
| Model poisoning via fine-tuning data | High | Dataset provenance, data validation, `aumos-ai-bom` |
| Model inversion (privacy attack) | Medium | Differential privacy, output filtering |
| Membership inference attack | Medium | DP training, rate limiting on inference |
| Model stealing via repeated queries | Low | Rate limiting, output perturbation for sensitive models |

### Prompt and Context Attacks

| Threat | Severity | Control |
|--------|----------|---------|
| Direct prompt injection | High | `aumos-security-runtime` injection detection |
| Indirect prompt injection (via retrieved content) | High | Content sanitization in RAG pipeline |
| Context window poisoning | Medium | Context integrity verification |
| System prompt extraction | Medium | System prompts not returned in API responses, hash verification |
| Jailbreaking | Medium | Multi-layer content policy, output validation |

---

## Residual Risk

After controls are applied, the following residual risks are accepted with monitoring:

| Risk | Residual Level | Acceptance Rationale |
|------|---------------|---------------------|
| Zero-day vulnerabilities in dependencies | Low-Medium | Mitigated by layered defenses; no single vuln compromises platform |
| Novel prompt injection techniques | Low-Medium | Defense-in-depth reduces blast radius; ongoing research investment |
| Sophisticated insider threat | Low | Compensating controls (audit logging, least privilege, behavioral monitoring) limit impact |
| Supply chain compromise of LLM provider | Low | Provider diversity strategy, output validation, no plaintext customer data to providers |

Residual risk is reviewed annually by the CISO and Risk Committee.
