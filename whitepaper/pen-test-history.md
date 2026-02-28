# Penetration Test History (GAP-511)

This document tracks all commissioned penetration tests for the AumOS platform.
Update after each engagement. Summary results are shared in the trust center;
full reports are available under NDA to qualifying enterprise customers.

---

## Engagement History

| Year | Firm | Scope | Critical Findings | High Findings | Status |
|------|------|-------|-------------------|---------------|--------|
| (none yet) | — | — | — | — | — |

---

## How to Update This File

After each penetration test engagement, add a row to the table above and create
a detailed section below following the template.

---

## Template: Penetration Test Engagement Report Summary

### [YEAR] Annual Penetration Test — [FIRM NAME]

**Engagement Dates:** [START DATE] — [END DATE]
**Firm:** [FIRM NAME] ([FIRM URL])
**Scope:**
- External network penetration testing
- API security testing (all `/api/v1/` endpoints)
- Web application testing (trust.aumos.ai, docs.aumos.ai)
- Authentication and authorization testing (aumos-auth-gateway)
- Insider threat / privilege escalation testing

**Findings Summary:**

| Severity | Count | Remediated | In Progress | Accepted Risk |
|----------|-------|-----------|-------------|---------------|
| Critical | [N] | [N] | [N] | [N] |
| High | [N] | [N] | [N] | [N] |
| Medium | [N] | [N] | [N] | [N] |
| Low | [N] | [N] | [N] | [N] |
| Informational | [N] | — | — | — |

**Notable Findings (no CVE details — summary only):**

1. [FINDING TITLE] (Critical/High/Medium) — [One sentence description. No exploitation details.]
   - Status: Remediated [DATE] / In progress (target: [DATE]) / Accepted (rationale: [REASON])

**Remediation Tracking:**

All critical and high findings must be remediated before this summary is published.
Medium findings tracked in Jira with target remediation dates.

**Full Report Availability:**

The full detailed penetration test report is available to enterprise customers
under NDA via the trust center at trust.aumos.ai/reports.

---

## Vendor Selection Criteria

When issuing RFPs for penetration testing firms:

**Required qualifications:**
- CREST, OSCP, or equivalent certification for all testers
- AICPA-recognized security audit firm (for SOC 2 evidence credit)
- Documented methodology (OWASP, PTES, or NIST SP 800-115)
- Minimum 5 years experience testing SaaS/cloud API platforms
- US-based (or EU-based for European infrastructure)

**Preferred firms (based on industry reputation):**
- Bishop Fox — API and cloud specialization
- NCC Group — broad enterprise security practice
- Coalfire — SOC 2 and FedRAMP expertise (useful for audit credit)
- Rapid7 — managed pen test service with Metasploit integration
- Big 4 cybersecurity practices (Deloitte, PwC, EY, KPMG) — for board reporting credibility

**RFP Process:**
1. Issue RFP to 3-4 firms with standardized scope document
2. Evaluate proposals on methodology, team credentials, and price
3. Select firm; execute MSA and Statement of Work
4. Kick-off meeting: define rules of engagement, emergency contact list
5. Conduct test (typically 2-3 weeks)
6. Receive draft report; review for accuracy
7. Remediate findings before receiving final report
8. Publish summary in trust center

---

## Emergency Contact Protocol During Testing

During active penetration testing, the following must be informed:
- Engineering lead: notified that authorized testing is in progress
- Cloud infrastructure team: whitelist tester IP ranges to avoid blocking
- Security team: available for real-time communication with testers
- NOC/operations: do NOT respond to alerts from authorized tester IPs as incidents
