# Security Questionnaire — General Security

**AumOS Platform | MuVeraAI Corporation**
**Version:** 1.0.0 | **Date:** February 2026

---

## Section 1: Security Program Governance

**Q1. Does your organization have a formal information security program?**

Yes. MuVeraAI maintains a formal Information Security Management System (ISMS) aligned to ISO 27001:2022. The security program includes written policies, risk management processes, security awareness training, incident response, and continuous monitoring. The ISMS is reviewed and updated annually.

**Q2. Who is responsible for information security within your organization?**

Our Chief Information Security Officer (CISO) is responsible for the information security program. The CISO reports to the CEO and presents quarterly to the Board Risk Committee. A dedicated Security team supports the CISO, including Security Engineers, a Compliance Manager, and a Data Protection Officer (DPO) for GDPR purposes.

**Q3. Do you have a written information security policy?**

Yes. Our Information Security Policy is maintained by the CISO, approved by executive leadership, and reviewed annually. It covers acceptable use, access control, encryption, incident response, vendor management, and data protection. The policy is communicated to all employees at onboarding and annually thereafter.

**Q4. How frequently are security policies reviewed and updated?**

Policies are reviewed and updated:
- Annually at minimum (scheduled review cycle)
- Following significant incidents (P1/P2) that reveal policy gaps
- Following material changes to the platform architecture or regulatory environment

**Q5. Do you have a documented risk management process?**

Yes. We maintain a risk register using a quantitative risk methodology (FAIR — Factor Analysis of Information Risk). Risks are assessed quarterly by the Security team and reviewed by the CISO and executive team. The risk register includes technical, operational, third-party, and AI-specific risks. Treatment plans (mitigate, accept, transfer, avoid) are documented and tracked for all High and Critical risks.

**Q6. Do you conduct background checks on employees with access to customer data?**

Yes. All employees, contractors, and third-party personnel with access to production systems or customer data undergo criminal background checks prior to access being granted. Background checks are conducted by a third-party screening firm and comply with applicable employment law. Enhanced background checks are conducted for roles with privileged access (Security team, Infrastructure team, executive staff).

**Q7. Do you provide security awareness training to all employees?**

Yes. All employees complete:
- Security awareness training at onboarding (within 30 days of start)
- Annual refresher training
- Role-specific training for engineering staff (OWASP Top 10, secure coding), security team (threat intelligence, incident response), and executives (social engineering, regulatory obligations)
- Phishing simulation exercises (quarterly, results tracked and used to target additional training)

Training completion is tracked; non-completion results in access suspension.

**Q8. Do you perform security assessments of your own products?**

Yes. AumOS undergoes the following security assessments:
- Annual penetration test by an independent third-party firm (CREST-certified)
- Quarterly internal vulnerability assessments
- Continuous automated scanning (SAST, DAST, SCA) in CI/CD pipeline
- Threat modeling for every major feature or architectural change
- Annual red team exercise

**Q9. Do you have a bug bounty program?**

Yes. MuVeraAI operates a private bug bounty program. Qualifying researchers are invited upon request. The program covers the AumOS platform and related infrastructure. Contact security@muveraai.com to inquire.

**Q10. Do you have cyber liability insurance?**

Yes. MuVeraAI carries a cyber liability insurance policy covering: data breach response costs, regulatory fines and penalties, business interruption, cyber extortion, and third-party liability. Policy limits and carrier details are available under NDA to enterprise customers with a legitimate business need.

---

## Section 2: Security Certifications and Compliance

**Q11. What security certifications does your organization hold?**

Current status (as of February 2026):
- **SOC 2 Type I**: Readiness assessment complete; Type I report in preparation
- **SOC 2 Type II**: Audit period commenced; expected report date Q4 2026
- **ISO 27001:2022**: Gap assessment complete, remediation underway; certification target Q3 2026
- **HIPAA**: BAA available; controls implemented; third-party HIPAA assessment completed
- **GDPR**: DPA available; DPO designated; data subject rights automation implemented
- **CCPA**: Compliance controls implemented; privacy policy updated

Note: While formal certification is in progress, controls for all listed frameworks are implemented and operational. Bridge letters and current audit status are available under NDA.

**Q12. Can you provide your most recent SOC 2 report?**

AumOS is currently in the SOC 2 Type II audit period. Our SOC 2 Type I report is in preparation. In the interim, we can provide:
- Our most recent third-party penetration test executive summary (under NDA)
- Our HIPAA third-party assessment summary
- Our self-assessment questionnaire against AICPA Trust Services Criteria

Contact compliance@muveraai.com to request available documentation.

**Q13. How are you audited against your compliance obligations?**

- Internal audits: Quarterly self-assessment against SOC 2 Trust Services Criteria and ISO 27001
- External audits: Annual third-party SOC 2 audit, annual ISO 27001 audit (once certified)
- Penetration testing: Annual by independent firm
- Regulatory assessments: HIPAA third-party assessment annually for healthcare deployments

**Q14. Are you subject to any regulatory requirements specific to your industry?**

MuVeraAI is subject to:
- GDPR (EU operations and EU customer data)
- CCPA (California residents' data)
- HIPAA (for healthcare customer deployments — BAA required)
- Various state breach notification laws (US)

We are not directly subject to SOX, PCI-DSS, or FedRAMP, but support customer compliance with these frameworks through our compliance control matrices and evidence packs.

**Q15. Do you have a data processing agreement (DPA) available?**

Yes. A standard DPA is available incorporating GDPR Standard Contractual Clauses (SCCs) for international data transfers. Customer-specific DPA modifications are reviewed by our legal team. Contact compliance@muveraai.com.

---

## Section 3: Vendor and Third-Party Risk

**Q16. How do you manage third-party security risk?**

We operate a formal Third-Party Risk Management (TPRM) program:
- Tier 1 (data processors): Full security questionnaire, SOC 2 report review, on-site assessment for critical vendors, annual reassessment
- Tier 2 (non-data services): Abbreviated questionnaire, annual reassessment
- Tier 3 (open-source/SaaS tools): Automated vulnerability and license scanning
- All third parties handling customer data sign a DPA
- Third-party incidents trigger our IR process; customers notified per contractual terms

**Q17. Do you maintain a list of subprocessors?**

Yes. A current subprocessor list is maintained and provided to customers under DPA terms. Customers are notified 30 days in advance of any new subprocessor or material change. The list includes: cloud infrastructure providers, LLM API providers, monitoring tools, and any other third parties with access to customer data.

**Q18. How do you ensure that subprocessors meet your security standards?**

- DPA required with all subprocessors before access is granted
- SOC 2 Type II report (or equivalent) required for Tier 1 subprocessors
- Annual reassessment of subprocessor security posture
- Contractual right to audit included in all subprocessor agreements
- Subprocessor security assessments tracked in our vendor risk register

**Q19. Do your subprocessors have access to customer data?**

Cloud infrastructure providers (AWS, GCP) have physical access to encrypted data but no access to encryption keys. LLM API providers receive prompts as configured by tenants; no AumOS-level customer identifiers or sensitive metadata is sent to LLM providers without explicit customer consent. No subprocessor receives unencrypted customer data.

**Q20. How do you handle the offboarding of vendors with access to customer data?**

Vendor offboarding process:
1. All credentials and access tokens revoked immediately
2. Encryption keys rotated if vendor had key access
3. Data deletion confirmed in writing with retention certificate
4. Offboarding logged in vendor risk register
5. Customer notified if vendor offboarding affects any customer-visible service

---

## Section 4: Physical Security

**Q21. What physical security controls are in place at your data centers?**

AumOS runs on SOC 2 Type II certified cloud infrastructure (AWS and GCP). Physical security is provided by these providers and includes: biometric access controls, 24/7 security personnel, CCTV surveillance, multi-layer physical access zones, and redundant power and cooling. MuVeraAI staff have no physical data center access.

**Q22. Do you have any on-premises infrastructure?**

MuVeraAI's production platform is entirely cloud-hosted. Our corporate offices contain standard IT infrastructure (laptops, workstations, network equipment) protected by:
- Badge access control for office entry
- Clean desk policy
- Encrypted workstations (BitLocker/FileVault)
- EDR on all corporate endpoints
- Corporate network segmented from production systems

For sovereign or on-premises deployment customers, AumOS can be deployed entirely within the customer's physical environment. Physical security for such deployments is the customer's responsibility per the Enterprise Agreement.

**Q23. How are portable storage devices controlled?**

- USB storage devices disabled by MDM policy on all corporate endpoints
- Exceptions require IT approval and are logged
- Data transfers to external media require explicit approval and encryption
- No customer data is stored on portable media without CISO authorization

---

## Section 5: Business Continuity and Disaster Recovery

**Q24. Do you have a business continuity plan (BCP)?**

Yes. Our BCP covers: loss of key personnel, office loss, cloud provider regional outage, and critical vendor failure. The BCP is reviewed and updated annually and after significant operational changes.

**Q25. Do you have a disaster recovery plan (DRP)?**

Yes. Our DRP is tested semi-annually. Current targets:
- **RTO (Recovery Time Objective)**: 4 hours for complete platform restoration
- **RPO (Recovery Point Objective)**: 1 hour maximum data loss
- Multi-region active-passive architecture for production workloads
- Automated failover for database layer (PostgreSQL HA with streaming replication)
- Regular restore tests: monthly automated backup validation, semi-annual full DR drill

**Q26. What is your stated uptime SLA?**

AumOS platform SLA: 99.9% uptime (three nines) for standard tiers; 99.95% for Enterprise tier. This translates to < 8.7 hours planned + unplanned downtime per year. Current uptime metrics are published at status.muveraai.com.

**Q27. How are customers notified of planned maintenance and unplanned outages?**

- Planned maintenance: 7-day advance notice via email and status page
- Unplanned outages: Status page updated within 15 minutes of detection; email notification to affected tenants within 30 minutes for P1 outages
- Post-incident reports published within 5 business days for P1/P2 incidents
- Customers may subscribe to status page notifications (email, SMS, webhook)

---

## Section 6: Security Hardening

**Q28. How do you harden your systems and applications?**

- Infrastructure: CIS Benchmark Level 2 for all cloud resources (enforced by automated compliance scanning — Prowler, Scout Suite)
- Containers: Non-root execution, read-only root filesystem, minimal base images (distroless), PodSecurityStandards Restricted
- OS: Minimal attack surface (unnecessary packages removed), automated patching, host-based IDS
- Application: OWASP Top 10 controls in SDLC, static analysis in CI, input validation at all boundaries
- Network: Default-deny firewall rules, no unnecessary open ports, WAF on public endpoints

**Q29. How do you manage software updates and patches?**

| Severity | Internal SLA |
|---------|-------------|
| Critical (CVSS 9.0+) | 30 days; emergency patch if actively exploited: 72 hours |
| High (CVSS 7.0–8.9) | 60 days |
| Medium (CVSS 4.0–6.9) | 90 days |
| Low (< 4.0) | Next quarterly release cycle |

Dependency updates are automated via Dependabot. OS patches applied weekly in maintenance windows. Emergency patches deployed outside maintenance windows for critical vulnerabilities with active exploits.

**Q30. Do you have a documented secure development lifecycle (SDL)?**

Yes. Our SDL requires: threat modeling for new features, peer code review with security checklist, SAST/DAST/SCA in CI/CD, secrets scanning on every commit, security sign-off for features with significant data or auth changes. See [whitepaper/aumos-security-architecture.md](../whitepaper/aumos-security-architecture.md) for full SDL description.

---

## Section 7: Network Security

**Q31. How is your network segmented?**

Production infrastructure is deployed in private VPC subnets with no public endpoints for databases or internal services. Network segmentation:
- Public tier: Load balancers, CDN, WAF only
- Application tier: Microservices in private subnet; only accessible via internal load balancer
- Data tier: Databases and caches in isolated private subnet; no direct application access, only via data layer service
- Management tier: Bastion/SSM access isolated in separate subnet; no lateral movement to application/data tier

**Q32. Do you use a Web Application Firewall (WAF)?**

Yes. AWS WAF (with Cloudflare as edge for DDoS protection) configured with:
- OWASP Core Rule Set
- Custom rules for AI platform patterns (prompt injection signatures, token limit enforcement)
- IP reputation filtering
- Rate limiting at WAF layer
- Bot management

**Q33. How do you protect against DDoS attacks?**

- L3/L4 DDoS protection: Cloud provider shield (AWS Shield Standard; Advanced for Enterprise tier)
- L7 DDoS: WAF rate limiting + Cloudflare bot management
- Traffic shaping: Ingress rate limiting per tenant, per IP, per endpoint
- Automated IP blocking: Sustained attack sources blocked automatically, reviewed by Security team

**Q34. Do you conduct network penetration testing?**

Yes. Annual external network penetration test by an independent CREST-certified firm. The scope includes all public-facing infrastructure, APIs, and any externally accessible management interfaces. Internal network pen test (assume breach scenario) included in annual red team exercise.

**Q35. How is remote access to production systems controlled?**

- No direct SSH from the internet to production servers
- Remote access via AWS SSM Session Manager (no SSH port open; bastion not required)
- SSM access requires: MFA, JIT approval, session recording enabled
- All session commands logged and reviewed
- Production access prohibited for non-authorized roles
- VPN not used for production access (zero-trust model via SSM + IAM)

---

## Section 8: Endpoint Security

**Q36. How are corporate endpoints managed?**

All corporate endpoints (laptops, workstations) managed by MDM (Jamf for macOS, Intune for Windows):
- Full disk encryption enforced (FileVault / BitLocker)
- EDR (CrowdStrike Falcon) on all endpoints
- OS and application patching automated via MDM
- Screen lock after 5 minutes of inactivity
- Remote wipe capability for lost/stolen devices
- USB storage disabled

**Q37. Do engineers with production access have hardened workstations?**

Yes. Engineers with production access use corporate-managed workstations with:
- Certificate-based authentication to production systems (no password-only access)
- EDR with elevated monitoring profile
- No local admin access
- Approved software allowlist enforced by MDM
- Production credentials never stored on local filesystem (fetched from Vault)

**Q38. How do you handle employee offboarding from a security perspective?**

Offboarding checklist triggered on employee termination notice:
1. Immediate revocation of all access upon confirmed departure (or at notice period start for involuntary termination)
2. All sessions invalidated, tokens revoked, API keys disabled
3. Corporate device returned and wiped (remote wipe if not returned)
4. SSO account disabled — cascades to all integrated applications
5. Shared password changes for any remaining shared accounts (prohibited; documented for exception tracking)
6. Audit log review of final 30 days of activity

**Q39. Do you use privileged access workstations (PAWs) for sensitive operations?**

Privileged operations (production access, key management, security incident response) are conducted from corporate-managed workstations with elevated security configuration — effectively functioning as PAWs. Dedicated isolated PAW hardware is on the roadmap for SUPER_ADMIN operations.

**Q40. How do you prevent data exfiltration from endpoints?**

- DLP policy enforced by MDM: screen capture, clipboard, USB, AirDrop restricted in sensitive contexts
- Email DLP: outbound email scanned for data patterns (PII, confidential markers) before delivery
- Production data access logged; bulk downloads alerted
- Endpoint data minimization: production data not stored locally; accessed via browser/VPN only

---

## Section 9: Monitoring and Detection

**Q41. Do you have a Security Operations Center (SOC)?**

MuVeraAI has a 24/7 on-call security rotation rather than a traditional SOC. We use automated detection (SIEM + UEBA + custom ML-based detection) with PagerDuty-driven human escalation. We are evaluating MSSP (Managed Security Services Provider) for SOC augmentation.

**Q42. What SIEM solution do you use?**

Internal: Elastic SIEM on ELK Stack. Customer-facing SIEM integration supports: Splunk, Microsoft Sentinel, Elastic, IBM QRadar, Google Chronicle, and generic syslog.

**Q43. What is your mean time to detect (MTTD) for security incidents?**

Target MTTD (measured for P1/P2 incidents):
- Automated detection (SIEM alert → PagerDuty page): < 5 minutes
- Human triage and classification: < 30 minutes
- Post-hoc review: MTTD tracked in PIR reports; target < 2 hours for P1 incidents

**Q44. What is your mean time to respond (MTTR)?**

Target MTTR by severity:
- P1 (Critical): Containment < 2 hours; Full resolution < 24 hours
- P2 (High): Containment < 8 hours; Full resolution < 72 hours

**Q45. Do you log all access to sensitive data?**

Yes. All access to Restricted and Confidential data is logged in the immutable audit trail including: actor identity, timestamp, action, resource accessed, and result. Logs are retained per retention schedule (minimum 7 years for security events). See [whitepaper/audit-logging.md](../whitepaper/audit-logging.md) for full details.

**Q46. How long are security logs retained?**

| Log Type | Hot Retention | Total Retention |
|---------|--------------|----------------|
| Authentication events | 1 year | 7 years |
| Data access events | 1 year | 7 years |
| Security events | 1 year | 10 years |
| System/application logs | 90 days | 1 year |

**Q47. Do you have intrusion detection systems (IDS/IPS)?**

Yes:
- Network IDS: AWS GuardDuty (ML-based threat detection on VPC Flow Logs and CloudTrail)
- Host-based IDS: Wazuh HIDS on all production hosts
- Container runtime: Falco (detects unexpected syscalls, file access, network connections)
- Custom ML models in `aumos-observability` for AI-specific behavioral anomalies

**Q48. Can customers access their own audit logs?**

Yes. Customers have access to their audit logs via:
- Customer portal (web UI with filtering and search)
- Audit Query API (programmatic access)
- Real-time streaming (WebSocket)
- Bulk export (gzip'd NDJSON)
- SIEM forwarding (customer-configured endpoint)

**Q49. Do you monitor for data exfiltration?**

Yes. `aumos-observability` monitors for:
- Bulk data download patterns (anomalous export volume)
- Off-hours data access
- Access from unusual geographic locations
- Unusually high API query rates
- Large data transfers to external endpoints

Anomaly detection combines rule-based and ML-based models. Alerts are routed to PagerDuty for security team review.

**Q50. Do you have a vulnerability disclosure program?**

Yes. See [SECURITY.md](../SECURITY.md) for our responsible disclosure policy. MuVeraAI operates a private bug bounty program. We commit to: 24-hour acknowledgment, 72-hour triage, 30-day remediation for critical findings, and coordinated public disclosure after fix deployment.
