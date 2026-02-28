# SOC 2 Control Evidence Map (GAP-509)

Maps each SOC 2 Trust Service Criteria (TSC) to the AumOS control implementation
and the evidence artifacts the auditor will collect.

**SOC 2 Observation Period Start:** Set `AUMOS_SOC2_OBSERVATION_START` env var
when Vanta/Drata begins monitoring.

**Auditor:** TBD (target: Schellman, Coalfire, or A-LIGN via Vanta partner network)

---

## CC1 — Common Criteria: Control Environment

| Criteria | Control | AumOS Implementation | Evidence Artifact |
|----------|---------|---------------------|------------------|
| CC1.1 | Board oversight of security | Executive security review (quarterly) | Board meeting minutes |
| CC1.2 | Management commitment | CISO designation; security policies published | Policy document + org chart |
| CC1.3 | Org structure and authority | Defined security roles in HR system | Job descriptions, RACI matrix |
| CC1.4 | Competence requirements | Security training completion tracking | Training completion records (Vanta) |
| CC1.5 | Accountability | Access reviews, termination procedures | User access review reports |

## CC2 — Common Criteria: Communication and Information

| Criteria | Control | AumOS Implementation | Evidence Artifact |
|----------|---------|---------------------|------------------|
| CC2.1 | Information quality | Structured logging (structlog) in all services | `aumos-observability`: log samples |
| CC2.2 | Internal communication | Incident communication procedures | Incident response runbooks |
| CC2.3 | External communication | Trust center portal (trust.aumos.ai) | Trust center availability logs |

## CC3 — Common Criteria: Risk Assessment

| Criteria | Control | AumOS Implementation | Evidence Artifact |
|----------|---------|---------------------|------------------|
| CC3.1 | Risk identification | Annual risk assessment process | Risk register (maintained in Vanta) |
| CC3.2 | Risk analysis | STRIDE threat model | `threat-model/stride-threat-model.md` |
| CC3.3 | Risk response | Security roadmap, remediation tracking | Remediation tickets in Jira |

## CC6 — Logical and Physical Access Controls

| Criteria | Control | AumOS Implementation | Evidence Artifact |
|----------|---------|---------------------|------------------|
| CC6.1 | Logical access controls | JWT + RBAC via aumos-auth-gateway | `aumos-auth-gateway/src/aumos_auth_gateway/middleware/` — code review |
| CC6.2 | Authentication | MFA enforced on all admin accounts | MFA enrollment reports (Vanta) |
| CC6.3 | Access provisioning | Access requests require manager approval | Jira ticket history |
| CC6.4 | Credential management | Secrets in aumos-secrets-vault, no hardcoding | `aumos-secrets-vault` code review |
| CC6.5 | Logical access removal | Automated off-boarding via Okta | Off-boarding procedure + Okta logs |
| CC6.6 | Tenant isolation | PostgreSQL RLS on all tenant tables | `aumos-data-layer`: RLS policy code |
| CC6.7 | Network access | VPC with private subnets; no direct DB access | Cloud architecture diagram |
| CC6.8 | Anti-malware | Endpoint protection on all developer machines | MDM enrollment + AV reports |

## CC7 — System Operations

| Criteria | Control | AumOS Implementation | Evidence Artifact |
|----------|---------|---------------------|------------------|
| CC7.1 | Vulnerability management | Dependabot + Snyk scanning | Snyk scan reports |
| CC7.2 | Alert monitoring | `aumos-observability`: Prometheus + alerting | Alert definitions + runbooks |
| CC7.3 | Incident response | Defined IR plan with RTO/RPO | `whitepaper/incident-response.md` |
| CC7.4 | Incident communication | Statuspage for customer notifications | Statuspage incident history |
| CC7.5 | Backup and recovery | Automated PostgreSQL backups (daily) | Backup completion logs; restore test records |

## A1 — Availability

| Criteria | Control | AumOS Implementation | Evidence Artifact |
|----------|---------|---------------------|------------------|
| A1.1 | Availability requirements | 99.9% SLA defined per service | `aumos-platform-core`: SLA documentation |
| A1.2 | Performance monitoring | Load testing (`aumos-load-testing`) | Load test reports |
| A1.3 | Environmental controls | Cloud provider redundancy (multi-AZ) | Cloud architecture diagram |

## C1 — Confidentiality

| Criteria | Control | AumOS Implementation | Evidence Artifact |
|----------|---------|---------------------|------------------|
| C1.1 | Confidential information | Data classification policy | Data classification documentation |
| C1.2 | Confidential info disposal | Data retention + deletion procedures | `aumos-privacy-engine`: purge procedures |

## PI1 — Processing Integrity

| Criteria | Control | AumOS Implementation | Evidence Artifact |
|----------|---------|---------------------|------------------|
| PI1.1 | Processing completeness | Kafka event audit log | Kafka topic logs |
| PI1.2 | Error handling | Structured error responses with codes | `aumos-common/errors.py` code review |

---

## Vanta/Drata Integration Checklist

Before engaging the auditor, configure Vanta or Drata to monitor:

- [ ] AWS/GCP/Azure account — resource inventory
- [ ] GitHub organization — code repository access controls
- [ ] Okta — user provisioning and MFA status
- [ ] Jira — access request ticket tracking
- [ ] PagerDuty — incident response alert history
- [ ] All production Kubernetes clusters — workload inventory
- [ ] PostgreSQL instances — backup status and encryption

**Target:** All controls in this map must be 100% green in Vanta before inviting the auditor.
