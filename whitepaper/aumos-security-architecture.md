# AumOS Security Architecture

**Classification:** Public | **Version:** 1.0.0 | **Date:** February 2026

---

## Table of Contents

1. [Architecture Philosophy](#1-architecture-philosophy)
2. [Defense-in-Depth Layers](#2-defense-in-depth-layers)
3. [Zero-Trust Network Design](#3-zero-trust-network-design)
4. [Authentication and Identity](#4-authentication-and-identity)
5. [Authorization and Access Control](#5-authorization-and-access-control)
6. [Multi-Tenant Isolation](#6-multi-tenant-isolation)
7. [Cryptographic Architecture](#7-cryptographic-architecture)
8. [Secrets Management](#8-secrets-management)
9. [AI-Specific Security Controls](#9-ai-specific-security-controls)
10. [Network Security](#10-network-security)
11. [Application Security](#11-application-security)
12. [Infrastructure Security](#12-infrastructure-security)
13. [Data Security Lifecycle](#13-data-security-lifecycle)
14. [Security Monitoring and Detection](#14-security-monitoring-and-detection)
15. [Vulnerability Management](#15-vulnerability-management)
16. [Third-Party and Supply Chain Security](#16-third-party-and-supply-chain-security)

---

## 1. Architecture Philosophy

AumOS is designed around four foundational security principles:

**Assume Breach.** Every component is designed under the assumption that adjacent systems may be compromised. Blast radius is minimized through strong isolation boundaries, least-privilege access, and defense-in-depth controls.

**Zero Trust.** No implicit trust based on network location. Every request — internal or external — is authenticated, authorized, and validated. Network position confers no privileges.

**Security as Architecture.** Security is embedded in the platform architecture, not applied as a post-hoc overlay. Tenant isolation, encryption, audit logging, and governance controls are first-class design constraints — not features.

**Verifiability.** Every security control is auditable, measurable, and testable. Claims in this document correspond to implemented, continuously tested capabilities.

---

## 2. Defense-in-Depth Layers

AumOS implements security across seven distinct layers:

```
Layer 7 — Governance & AI Controls
   ├─ aumos-governance-engine (policy evaluation)
   ├─ aumos-approval-workflow (human-in-the-loop)
   ├─ aumos-hallucination-shield (output validation)
   └─ aumos-adversarial-immunity (input hardening)

Layer 6 — Application Security
   ├─ Input validation (Pydantic schemas at all boundaries)
   ├─ Output encoding (XSS prevention)
   ├─ CSRF protection (SameSite cookies + CSRF tokens)
   └─ Rate limiting (per-tenant, per-endpoint, per-user)

Layer 5 — API Gateway & Auth
   ├─ aumos-auth-gateway (JWT issuance, SAML/OIDC federation)
   ├─ Token validation on every request
   ├─ Scope-based access control
   └─ API abuse detection (pattern-based + ML)

Layer 4 — Service Mesh
   ├─ mTLS between all microservices
   ├─ Service identity (SPIFFE/SPIRE)
   ├─ Egress filtering (allowlist-only)
   └─ Network policy enforcement

Layer 3 — Data Layer
   ├─ aumos-data-layer (RLS, parameterized queries)
   ├─ Field-level encryption for PII/PHI
   ├─ Tenant-scoped encryption keys
   └─ Audit log for all data mutations

Layer 2 — Infrastructure
   ├─ VPC isolation, no public database endpoints
   ├─ WAF (AWS WAF / Cloudflare)
   ├─ DDoS protection
   └─ Host-based intrusion detection (OSSEC/Wazuh)

Layer 1 — Physical / Cloud Provider
   ├─ SOC 2 Type II certified cloud provider (AWS/GCP)
   ├─ Hardware security modules (HSMs) for key operations
   ├─ Physical access controls at data center
   └─ Redundant facility design
```

---

## 3. Zero-Trust Network Design

### Principles Implemented

- **Explicit verification**: Every service-to-service call carries a cryptographically signed service identity (SPIFFE SVID). No service is trusted based on its IP address or network segment.
- **Least-privilege access**: Services receive only the network access required for their specific function. Egress is allowlist-based; unauthorized destinations are blocked at the infrastructure level.
- **Micro-segmentation**: Each microservice runs in its own isolated network segment. The data layer is in a separate, private subnet with no direct internet exposure.
- **Continuous validation**: mTLS certificates are short-lived (24 hours) and automatically rotated by SPIRE. Compromise of a single certificate does not enable lateral movement without re-authentication.

### Service Mesh Configuration

All internal traffic traverses Istio service mesh with:
- Strict mTLS mode — plaintext is rejected
- Per-service AuthorizationPolicies — only declared consumers may connect
- Egress gateway — all external traffic exits through controlled gateway with domain allowlisting
- Traffic mirroring to SIEM for anomaly detection

---

## 4. Authentication and Identity

### User Authentication

**Multi-Factor Authentication (MFA)**
- TOTP (RFC 6238) via authenticator app — enforced for all users
- Hardware security keys (FIDO2/WebAuthn) — supported, recommended for privileged roles
- SMS OTP — available as fallback, not recommended for high-privilege accounts
- MFA bypass exceptions require CISO approval and are time-limited (max 24 hours)

**Single Sign-On (SSO)**
- SAML 2.0 integration with enterprise identity providers (Okta, Azure AD, Ping Identity, Google Workspace)
- OIDC (OpenID Connect) support for modern IdP integrations
- JIT (Just-in-Time) user provisioning from IdP assertions
- SCIM 2.0 for automated user lifecycle management (provisioning, deprovisioning)

**Password Policy (when local auth is used)**
- Minimum 14 characters, complexity requirements
- bcrypt hashing (cost factor 12) — never stored plaintext
- Password history: last 12 passwords blocked
- Breach detection: integration with HaveIBeenPwned API to flag compromised passwords

### Service Authentication

- Service accounts issued via `aumos-auth-gateway`
- Credentials stored in `aumos-secrets-vault` (HashiCorp Vault)
- Vault dynamic secrets — credentials generated on-demand, auto-expire, never stored long-term
- Service-to-service calls use short-lived JWT tokens (15-minute expiry) with audience and scope claims
- No long-lived static API keys for service accounts in production

### Session Management

- JWT access tokens: 15-minute expiry
- Refresh tokens: 7-day expiry, stored in HttpOnly Secure cookies
- Session invalidation on: password change, MFA change, suspicious activity detection, admin action
- Concurrent session limits configurable per tenant policy
- Inactive session timeout: configurable (default 30 minutes)

---

## 5. Authorization and Access Control

### Role-Based Access Control (RBAC)

AumOS implements a 5-level privilege hierarchy:

| Level | Role | Capabilities |
|-------|------|-------------|
| 1 | READ_ONLY | View resources, read logs, run reports |
| 2 | MEMBER | Create and modify own resources, run agents |
| 3 | ADMIN | Manage team resources, configure integrations |
| 4 | ORG_ADMIN | Manage all tenant resources, user management, billing |
| 5 | SUPER_ADMIN | Platform-level configuration (MuVeraAI staff only) |

All role assignments are:
- Recorded in the immutable audit log
- Require approval from a higher-privilege user
- Scoped to a specific tenant — cross-tenant access is architecturally prevented
- Subject to periodic access review (quarterly, automated reminders)

### Attribute-Based Access Control (ABAC) Extensions

For fine-grained resource access, AumOS extends RBAC with ABAC policies:
- Resource-level tags (department, project, data classification)
- Contextual conditions (time-of-day, location, device trust posture)
- Policy evaluation via `aumos-governance-engine` using Open Policy Agent (OPA)

### Least Privilege

- Service accounts: scoped to the minimum permissions required for their function
- Human operators: JIT (Just-in-Time) privilege escalation for administrative tasks — base privileges are minimal
- Privilege escalation is logged, requires justification, and expires automatically (default 4-hour window)
- Regular access reviews: 90-day cycle with automated report generation and manager attestation

### Separation of Duties

- Production infrastructure access requires separate authorization from code deployment
- Financial controls (billing, subscription changes) require dual approval
- Key management operations require quorum of authorized administrators (Vault Shamir secret sharing)

---

## 6. Multi-Tenant Isolation

### Isolation Architecture

AumOS uses three overlapping isolation mechanisms to prevent cross-tenant data access:

**Layer 1: Application-level tenant context**
Every authenticated request carries a `tenant_id` claim in its JWT. All data operations in the application layer filter by `tenant_id` explicitly. A request with no `tenant_id` is rejected at the API gateway.

**Layer 2: Database Row-Level Security (RLS)**
The `aumos-data-layer` sets `SET app.current_tenant = '{tenant_id}'` on every database session. PostgreSQL RLS policies enforce that queries can only return rows matching the current tenant. A misconfigured application query that omits tenant filtering is caught at the database layer and returns zero results rather than leaking data.

**Layer 3: Tenant-scoped encryption keys**
Each tenant's data is encrypted with a unique tenant encryption key (TEK) managed in `aumos-secrets-vault`. Tenant data at rest is encrypted such that even direct database access cannot read another tenant's data without access to their specific TEK.

### Tenant Isolation Testing

Tenant isolation is validated:
- Automated tests in `aumos-integration-tests` attempt cross-tenant queries and assert rejection
- Annual penetration testing includes tenant isolation bypass scenarios
- Bug bounty program includes cross-tenant data access as a critical-severity finding

---

## 7. Cryptographic Architecture

### Key Hierarchy

```
Root Key (Hardware HSM — AWS CloudHSM / Azure Dedicated HSM)
└─ Platform Master Key (PMK)
    ├─ Tenant Encryption Key (TEK) — one per tenant
    │   ├─ Data Encryption Key (DEK) — per data class (PII, PHI, general)
    │   └─ Field Encryption Key (FEK) — per sensitive field
    ├─ Service Signing Key — JWT token signing
    ├─ Audit Log Signing Key — tamper-evident log signing
    └─ TLS Certificate Authority — internal mTLS PKI
```

### Encryption Standards

| Context | Algorithm | Key Size | Notes |
|---------|-----------|---------|-------|
| Data at rest (databases) | AES-256-GCM | 256-bit | Per-tenant DEK |
| Data at rest (object storage) | AES-256-GCM | 256-bit | Per-object DEK via envelope encryption |
| Data in transit | TLS 1.3 | ECDHE 256-bit | TLS 1.2 minimum, 1.0/1.1 disabled |
| Internal mTLS | TLS 1.3 | ECDHE 256-bit | Mutual authentication required |
| JWT signing | RS256 (RSA-SHA256) | 2048-bit | Rotating every 90 days |
| Field encryption (PII) | AES-256-GCM | 256-bit | Per-field FEK |
| Backup encryption | AES-256-GCM | 256-bit | Separate backup TEK |
| Password hashing | bcrypt | N/A | Cost factor 12 |
| Audit log signing | HMAC-SHA256 | 256-bit | Append-only, chain-signed |

### Key Management Lifecycle

- **Generation**: All keys generated in HSM using FIPS 140-2 Level 3 certified hardware
- **Distribution**: Keys distributed via Vault Transit Secrets Engine — applications never see root keys
- **Rotation**: Automated rotation schedules (TLS: 90 days, DEK: 1 year, TEK: customer-configurable)
- **Revocation**: Immediate revocation capability with audit trail
- **Destruction**: Cryptographic key destruction with certificate of destruction on tenant offboarding
- **Backup**: Encrypted key backups in geographically separate HSM with quorum-controlled access

### Bring Your Own Key (BYOK)

Enterprise customers may supply their own root encryption key, stored in their own HSM or cloud KMS (AWS KMS, Azure Key Vault, Google Cloud KMS). AumOS performs envelope encryption using the customer-supplied key — MuVeraAI staff cannot decrypt customer data without the customer's key.

---

## 8. Secrets Management

`aumos-secrets-vault` implements centralized secrets management using HashiCorp Vault:

- **Dynamic credentials**: Database credentials, API keys, and cloud credentials are generated on-demand and expire automatically. Compromised credentials are useless within minutes.
- **Vault Transit**: All encryption/decryption operations performed inside Vault — applications never handle raw keys
- **Audit log**: Every secrets access is logged with requester identity, timestamp, and secret path
- **Lease management**: Automatic credential rotation on expiry; applications receive renewal notifications before expiry
- **Break-glass access**: Emergency access procedure with quorum requirement (Shamir secret sharing on root token), time-limited, fully logged

### Secrets Not Permitted In

- Source code repositories (git-secrets pre-commit hook enforced)
- Environment variable files committed to version control
- Container image layers
- Log files or debug output
- Configuration files without encryption

Automated secret scanning runs on every commit and in CI/CD pipelines (truffleHog, git-secrets).

---

## 9. AI-Specific Security Controls

AumOS adds a layer of AI-native security controls that address threats unique to AI platforms:

### Prompt Injection Defense (`aumos-security-runtime`)

All user-controlled input processed by LLMs passes through a prompt injection detection layer:
- Pattern-based detection: ~500 known prompt injection signatures
- Semantic classification: ML model trained on injection attack datasets
- Structural validation: Enforces that system prompts and user inputs remain in designated positions
- Rejection policy: Suspicious inputs are rejected with a structured error; the original input is logged for analysis

### Output Validation (`aumos-hallucination-shield`)

LLM outputs are validated before delivery to users:
- Factual grounding checks against retrieved context (RAG systems)
- Confidence scoring — low-confidence outputs are flagged or withheld
- Harmful content detection (violence, PII leakage, IP leakage)
- Structured output validation against declared schemas (using Pydantic)

### Adversarial Input Defense (`aumos-adversarial-immunity`)

For vision and multimodal models:
- Adversarial example detection using adversarial robustness toolbox
- Input perturbation filtering
- Model confidence anomaly detection

### Behavioral Fingerprinting (`aumos-behavioral-fingerprint`)

Runtime monitoring of AI agent behavior:
- Baseline behavioral profiles per agent type
- Anomaly detection for: unusual API call patterns, unexpected data access, out-of-scope actions
- Automatic circuit breaker — agents exhibiting anomalous behavior are suspended pending review (`aumos-circuit-breaker`)

### AI Bill of Materials (`aumos-ai-bom`)

Full provenance for every AI artifact:
- Model lineage: base model, fine-tuning datasets, training runs
- Dataset provenance: source, processing steps, quality metrics
- Deployment attestation: cryptographic signature chain from training to inference
- Supports SBOM-equivalent audits for AI components

### Model Access Controls

- Models are accessed through `aumos-model-registry` — direct API key usage is prohibited
- Model selection is governed by tenant-level policy (prohibited models, approved models only)
- Rate limiting per model, per tenant, per user
- Inference logging for all model calls (subject to retention policy)

---

## 10. Network Security

### Perimeter Security

- WAF with OWASP Top 10 ruleset + custom AI-platform rules
- DDoS protection (L3/L4 via cloud provider, L7 via WAF)
- BGP route filtering and IP reputation scoring at edge
- Geoblocking available as tenant-configurable policy

### Internal Network

- All production infrastructure in private VPC subnets
- No database, message queue, or internal service endpoints exposed to the internet
- Bastion host / SSM Session Manager for operator access — no direct SSH from internet
- VPC Flow Logs enabled; anomalous traffic patterns alert to SOC

### Firewall Rules

- Default-deny at all boundaries
- Allowlist-based egress: only approved destinations (LLM provider APIs, cloud services, customer-specified)
- Port restrictions: only required ports opened, documented per service
- Quarterly firewall rule review and cleanup

### TLS Configuration

- TLS 1.3 required for all external connections
- TLS 1.2 minimum for legacy compatibility (with strong cipher suites only)
- TLS 1.0 and 1.1 disabled platform-wide
- HSTS (HTTP Strict Transport Security) with 1-year max-age, includeSubDomains
- Certificate Transparency logging for all certificates
- Automated certificate rotation via Let's Encrypt / ACM

---

## 11. Application Security

### Secure Development Lifecycle (SDL)

1. **Threat modeling** — required for all new features touching user data or AI models
2. **Secure code review** — security checklist enforced in PR review template
3. **Static analysis** — Semgrep, Bandit (Python), gosec (Go) in CI pipeline
4. **Dependency scanning** — Dependabot for dependency updates, Snyk for vulnerability detection
5. **Secrets scanning** — truffleHog + git-secrets on every commit
6. **Dynamic testing** — OWASP ZAP scan on every deployment to staging
7. **Penetration testing** — annual third-party pen test, quarterly automated scanning

### OWASP Top 10 Controls

| Threat | Control |
|--------|---------|
| A01 Broken Access Control | RBAC enforcement, RLS, automated access review |
| A02 Cryptographic Failures | AES-256-GCM, TLS 1.3, bcrypt, no weak ciphers |
| A03 Injection | Parameterized queries only, Pydantic input validation |
| A04 Insecure Design | Threat modeling in SDL, security architecture review |
| A05 Security Misconfiguration | IaC with security defaults, CIS benchmark scanning |
| A06 Vulnerable Components | Dependabot, Snyk, 30-day patch SLA for critical CVEs |
| A07 Auth Failures | MFA required, account lockout, session management |
| A08 Software Integrity Failures | Signed artifacts, SBOM, dependency pinning |
| A09 Logging Failures | Centralized immutable logging, SIEM, alerting |
| A10 SSRF | Egress allowlisting, URL validation, no internal metadata access |

### Input Validation

Every API endpoint validates all input using Pydantic schemas:
- Type enforcement
- Length limits
- Range validation
- Format validation (email, UUID, URL)
- Enum constraints

Unknown fields are rejected (extra='forbid' in Pydantic). Validation errors return structured error responses without stack traces.

---

## 12. Infrastructure Security

### Infrastructure as Code

All infrastructure is defined in Terraform:
- Version-controlled, peer-reviewed before apply
- State stored in encrypted S3 with versioning
- Terraform plan reviewed in CI before apply
- Production changes require manual approval

### CIS Benchmark Compliance

All cloud infrastructure configured to CIS Benchmark Level 2:
- CloudTrail enabled with log file validation
- S3 bucket public access blocked by default
- Security groups: default VPC unused, no 0.0.0.0/0 ingress except load balancers
- IAM: MFA enforced for all human users, no root account usage, access key rotation
- KMS: CMK used for all sensitive data services

### Container Security

- Base images: minimal (distroless or alpine), no unnecessary packages
- Containers run as non-root user
- Read-only root filesystem where possible
- No privileged containers
- Container image scanning in CI (Trivy, Grype)
- Image signing (cosign) and verification before deployment
- Runtime security monitoring (Falco) — detects unexpected syscalls, file access

### Kubernetes Security

- RBAC enforced; service accounts have minimal permissions
- PodSecurityStandards: Restricted profile enforced
- Network policies: default-deny, explicit allowlist
- Secrets encrypted at rest in etcd (AWS KMS encryption)
- Admission controllers: OPA Gatekeeper for policy enforcement
- Regular cluster CIS benchmark scans

---

## 13. Data Security Lifecycle

### Data Classification

| Class | Examples | Controls |
|-------|---------|---------|
| Public | Documentation, marketing | No restrictions |
| Internal | Business data, configurations | Access controls, audit logging |
| Confidential | Customer data, model outputs | Encryption, strict access, 90-day retention |
| Restricted (PII) | Personal identifiers, contacts | Field encryption, RLS, 30-day retention |
| Restricted (PHI) | Health records | HIPAA controls, BAA required, 7-year retention |

### Data Handling

- Data classification labels propagated throughout the data pipeline
- `aumos-data-pipeline` enforces handling rules based on classification
- `aumos-privacy-engine` provides PII detection and anonymization
- De-identification for test/staging environments — production data never used in non-production

### Data Retention and Deletion

- Configurable retention per data class and tenant policy
- Automated purge jobs respect retention schedules
- Right to erasure (GDPR Article 17): automated deletion workflow with 30-day SLA
- Deletion verified — cryptographic deletion by destroying DEK (key-based deletion)
- Backup retention: maximum 35 days for operational backups; separate archival policy for compliance

### Data Residency

- Tenant data stored in configured region; no cross-region replication without explicit consent
- Region selection at tenant onboarding; immutable without migration workflow
- Supported regions: US East, US West, EU West (Frankfurt), EU North (Ireland), APAC (Singapore, Sydney)
- Sovereign deployment option: AumOS deployed entirely within customer cloud account for full data sovereignty

---

## 14. Security Monitoring and Detection

### Logging Architecture

- All audit events published to `aumos-observability` (centralized logging pipeline)
- Logs shipped to customer-configured SIEM (Splunk, Elastic, Sentinel, Chronicle)
- Append-only audit log with cryptographic chain signing (`aumos-audit-log`)
- Log retention: 1 year hot, 7 years cold storage

### Audit Events Captured

- All authentication events (success, failure, MFA, SSO)
- All authorization events (access grants, denials, privilege escalations)
- All data access events (read, write, delete, export)
- All administrative actions (user management, configuration changes, key operations)
- All AI operations (model calls, agent executions, governance decisions)
- All security events (anomaly detections, circuit breaker trips, rate limit hits)

### Detection Capabilities

- **UEBA**: User and Entity Behavior Analytics — baseline per user/service, alert on deviation
- **Threat Intelligence**: IOC matching against commercial threat intel feeds
- **ML-based anomaly detection**: Unsupervised models detect novel attack patterns
- **`aumos-behavioral-fingerprint`**: AI-specific behavioral monitoring
- **`aumos-drift-detector`**: Model and data drift detection with security implications

### Alerting and Response

- PagerDuty integration for critical alerts (24/7 on-call)
- Alert severity tiers: P1 (critical, 15-min response), P2 (high, 1-hour), P3 (medium, 4-hour)
- SOAR playbook automation for common incident types
- False positive tuning via ticketing system integration

---

## 15. Vulnerability Management

### Scanning Schedule

| Type | Frequency | Tool |
|------|-----------|------|
| Container image scanning | Every build | Trivy, Grype |
| Dependency vulnerability | Daily | Dependabot, Snyk |
| Static code analysis | Every PR | Semgrep, Bandit |
| Dynamic application scanning | Weekly (staging) | OWASP ZAP, Nuclei |
| Infrastructure configuration | Weekly | Prowler, Scout Suite |
| Network vulnerability scan | Monthly | Nessus |
| Penetration test | Annual | Third-party firm |

### Patch SLAs

| Severity | SLA |
|---------|-----|
| Critical (CVSS 9.0+) | 30 days (emergency patch if actively exploited: 72 hours) |
| High (CVSS 7.0–8.9) | 60 days |
| Medium (CVSS 4.0–6.9) | 90 days |
| Low (CVSS < 4.0) | Next quarterly release |

### Responsible Disclosure

See [SECURITY.md](../SECURITY.md) for vulnerability reporting procedures. MuVeraAI operates a private bug bounty program.

---

## 16. Third-Party and Supply Chain Security

### Vendor Assessment

All third-party software, SaaS services, and AI model providers undergo security assessment:
- Tier 1 (data processors): Full security questionnaire, SOC 2 report review, annual reassessment
- Tier 2 (non-data services): Abbreviated questionnaire, annual reassessment
- Tier 3 (open-source dependencies): Automated vulnerability scanning, license compliance check

### Software Supply Chain

- All open-source dependencies pinned to specific versions with hash verification
- SBOM (Software Bill of Materials) generated for every release (`aumos-ai-bom`)
- Signed container images — only images with valid MuVeraAI signature deployed to production
- Dependency confusion attack prevention: private package registry with namespace reservations
- `aumos-content-provenance` tracks provenance for all AI-generated content artifacts

### AI Model Supply Chain

AI models used in production are subject to additional scrutiny:
- Provenance verification: model cards, training data disclosure, known vulnerability database
- Pre-deployment evaluation: safety benchmarks, bias testing, adversarial robustness
- Runtime behavioral monitoring: anomaly detection on model outputs in production
- Model inventory tracked in `aumos-model-registry` with full audit trail

### Subprocessors

A current list of subprocessors (cloud infrastructure, LLM providers, monitoring tools) is maintained and available to customers under NDA. Customers are notified 30 days in advance of any new subprocessor addition.
