# AumOS Data Protection

**Classification:** Public | **Version:** 1.0.0 | **Date:** February 2026

---

## Data Classification Framework

AumOS implements a four-tier data classification system. All data ingested, processed, or stored by the platform is assigned a classification at creation and handled according to the corresponding controls.

| Class | Label | Description | Examples |
|-------|-------|-------------|---------|
| 1 | Public | Intentionally public, no confidentiality requirement | Documentation, marketing content, public APIs |
| 2 | Internal | Business data, not intended for public disclosure | Tenant configurations, non-sensitive logs, analytics aggregates |
| 3 | Confidential | Sensitive business or customer data | Customer prompts, AI model outputs, usage data, business logic |
| 4 | Restricted | Regulated or highly sensitive personal data | PII (names, emails, addresses), PHI (health records), financial data |

Classification is applied automatically by `aumos-data-pipeline` based on:
- Data source (customer-declared sensitivity)
- Content scanning (`aumos-privacy-engine` PII detection)
- Regulatory context (healthcare tenants = PHI by default)

---

## Data Inventory

### Data Types by Component

| Component | Data Types | Classification | Retention |
|-----------|-----------|----------------|-----------|
| `aumos-auth-gateway` | User credentials (hashed), session tokens, auth events | Restricted (credentials), Internal (events) | 7 years (audit), session duration (tokens) |
| `aumos-agent-framework` | Agent inputs, outputs, execution traces | Confidential | 90 days (default), configurable |
| `aumos-llm-serving` | Prompts, completions, model call metadata | Confidential | 30 days (default), configurable |
| `aumos-data-layer` | All application data | Varies by tenant/type | Per data class and tenant policy |
| `aumos-observability` | Audit logs, metrics, traces | Internal (metrics), Internal (audit) | 1 year hot, 7 years cold |
| `aumos-model-registry` | Model weights, metadata, evaluation results | Confidential | Indefinite while active, deleted on decommission |
| `aumos-privacy-engine` | PII scan results, anonymized datasets | Restricted (originals), Internal (anonymized) | 30 days (results), per policy (data) |

---

## Data Handling Controls by Classification

### Class 1 — Public

- No encryption required (but HTTPS used for all transport)
- No access controls required beyond basic authentication
- May be cached at CDN layer

### Class 2 — Internal

- Encrypted at rest (AES-256-GCM)
- Access limited to authenticated users with appropriate RBAC role
- Audit log on write operations

### Class 3 — Confidential

- Encrypted at rest with tenant-scoped DEK (AES-256-GCM)
- Encrypted in transit (TLS 1.3)
- Access requires MEMBER role or higher
- Full audit log on read and write
- 90-day default retention; configurable up to 3 years
- Export requires ADMIN role approval

### Class 4 — Restricted (PII/PHI)

- Encrypted at rest with field-level encryption (per-field FEK)
- Encrypted in transit (TLS 1.3)
- Access requires explicit data access role; JIT approval for sensitive reads
- Full audit log on every access (read/write/delete)
- PII fields masked in logs and analytics (e.g., email → `j****@example.com`)
- Retention governed by regulatory requirement (minimum legal retention, maximum per policy)
- De-identification applied before use in analytics or AI training
- Data subject rights automation (GDPR Art. 15, 16, 17 — access, rectification, erasure)

---

## Privacy Engineering

### PII Detection (`aumos-privacy-engine`)

Automated PII detection applied to:
- All data ingested from external sources
- AI model inputs and outputs
- Log streams before storage
- Data exports

Detection capabilities:
- Regex-based patterns: email, phone, SSN, credit card, passport numbers
- NER (Named Entity Recognition) model for names, addresses, organizations
- De-identification: masking, pseudonymization, generalization, suppression
- Confidence scoring: high-confidence auto-redact; medium-confidence flag for review

### Differential Privacy for AI Training

When customer data is used for model training or fine-tuning:
- Differential privacy (DP-SGD) applied during training
- Privacy budget tracking (epsilon/delta parameters)
- Privacy budget exhaustion triggers automatic training halt
- DP parameters disclosed to customers before training consent

### Data Minimization

AumOS collects and processes only the data necessary for the declared purpose:
- Purpose binding: data tagged with processing purpose at ingestion
- Minimization checks in `aumos-data-pipeline`: unused fields not stored
- Aggregation preference: anonymized aggregates used in preference to individual records for analytics
- Customer-configurable data collection opt-outs

---

## Data Retention and Deletion

### Retention Schedule

| Data Type | Default Retention | Regulatory Minimum | Maximum |
|-----------|------------------|-------------------|---------|
| Audit logs | 1 year hot, 7 years cold | 7 years (SOX), 3 years (SOC 2) | 10 years |
| User account data | Account lifetime + 30 days | N/A | 3 years post-deletion |
| AI interaction logs | 90 days | N/A | 3 years |
| Model outputs | 30 days | N/A | 1 year |
| PHI (HIPAA) | 7 years | 6 years (HIPAA) | 10 years |
| PII (GDPR) | Minimum necessary | N/A | 3 years post last interaction |
| Financial records | 7 years | 7 years (IRS) | 10 years |
| Security event logs | 1 year | 90 days (PCI) | 7 years |

### Deletion Process

**Soft Delete (Logical)**
- Record marked as deleted, access blocked at application layer
- Data remains encrypted in storage for configurable grace period (default 30 days)

**Hard Delete (Cryptographic)**
- DEK for the data scope is destroyed in Vault
- Data becomes computationally unrecoverable without DEK
- Backup DEK copies destroyed per backup policy
- Deletion certificate generated for compliance records

**Right to Erasure (GDPR Article 17)**
- Request received via API or customer portal
- Automated workflow in `aumos-data-pipeline` identifies all records for subject
- Hard delete executed within 30 days
- Deletion confirmation report provided to customer
- Audit log of erasure retained (without personal data) for compliance

### Backup Data

- Operational backups retained maximum 35 days (point-in-time recovery)
- Backup data encrypted with separate backup KEK (key encryption key)
- Backup deletion triggered by tenant offboarding, with verification
- Backup restoration tested quarterly

---

## Data Transfer and Sharing

### Cross-Border Transfers

- Data stored in tenant-configured region; no cross-region replication without explicit consent
- EU data: GDPR-compliant transfer mechanisms (Standard Contractual Clauses for transfers outside EEA)
- International transfers documented in Data Processing Agreement (DPA)
- Transfer Impact Assessments available on request for Tier 1 enterprise customers

### Third-Party Data Sharing

- No customer data shared with third parties without explicit consent or contractual requirement
- LLM providers receive only the minimum necessary context; no tenant identifiers in prompts to providers
- Sub-processor list maintained and available under NDA
- Data Processing Agreement (DPA) required with all sub-processors

### Customer Data Export

- Customers may export all their data in machine-readable format (GDPR Art. 20 — data portability)
- Export available via API or customer portal
- Export encrypted with customer-provided public key or password-protected ZIP
- Export audit trail: who requested, when, what scope

---

## Data Loss Prevention (DLP)

`aumos-data-pipeline` implements DLP controls:

- **Exfiltration detection**: Anomalous bulk export patterns trigger alert and temporary hold
- **Classification enforcement**: Data cannot be downgraded in classification without admin approval + audit entry
- **Boundary controls**: Confidential/Restricted data cannot be sent to external destinations not on the approved integrations list
- **AI output scanning**: Model outputs scanned for potential customer data leakage before delivery
- **Watermarking**: Optional digital watermarking for exported confidential documents

---

## Regulatory Compliance

### GDPR Compliance

| Requirement | Implementation |
|-------------|----------------|
| Lawful basis for processing | Documented in privacy policy and DPA; consent management built-in |
| Data subject rights | Automated access, rectification, erasure, portability workflows |
| Privacy by design | Data minimization, purpose binding, PII detection built into platform |
| Data breach notification | 72-hour notification to supervisory authority; customer notification per DPA |
| DPO appointment | DPO designated; contact privacy@muveraai.com |
| ROPA maintenance | Records of Processing Activities maintained and available on request |

### CCPA Compliance

| Requirement | Implementation |
|-------------|----------------|
| Right to know | Data inventory available to consumers on request |
| Right to delete | Erasure workflow with 45-day SLA |
| Right to opt-out of sale | Data not sold; opt-out mechanism available |
| Non-discrimination | No differentiated service for data rights exercised |

### HIPAA Compliance

- Business Associate Agreement (BAA) available for covered entities and business associates
- PHI handling controls per HIPAA Security Rule (Administrative, Physical, Technical Safeguards)
- See [compliance-matrix/hipaa-mapping.md](../compliance-matrix/hipaa-mapping.md) for full control mapping
