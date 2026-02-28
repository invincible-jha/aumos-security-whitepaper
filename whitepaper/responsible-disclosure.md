# Responsible Disclosure Policy (GAP-516)

**Effective Date:** 2026-03-01
**Last Updated:** 2026-02-28

MuVeraAI Corporation (operating AumOS Enterprise) is committed to maintaining the security
of our platform. We appreciate the security research community's efforts to identify and
responsibly disclose vulnerabilities.

---

## Scope

This policy covers vulnerabilities in:

- **AumOS production APIs:** `api.aumos.ai` and all `/api/v1/` endpoints
- **Trust Center:** `trust.aumos.ai`
- **Documentation portal:** `docs.aumos.ai`
- **AumOS SDKs:** packages published under the `@aumos-ai` NPM scope and `aumos-*` PyPI packages

**Out of scope:**
- Third-party services and infrastructure not operated by MuVeraAI
- Denial of service attacks (flooding, resource exhaustion)
- Social engineering of MuVeraAI employees
- Physical security vulnerabilities
- Vulnerabilities in customer-operated instances of AumOS (contact your AumOS admin)
- Already known vulnerabilities (check our security bulletins first)

---

## How to Report

**Preferred:** Email `security@muveraai.com` with:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact assessment
4. Your name/handle for acknowledgment (optional)
5. Any proof-of-concept code (if applicable)

**PGP Key:** Available at `trust.aumos.ai/security/pgp-key.asc` for encrypted submissions.

**Response SLA:**
- Initial acknowledgment: within 48 hours
- Triage and severity assessment: within 5 business days
- Resolution plan communicated: within 10 business days
- Critical vulnerabilities: remediation target within 30 days

---

## Our Commitments

When you follow this policy, we commit to:

1. **Not pursue legal action** against researchers who follow this policy and do not
   exfiltrate data, disrupt services, or access customer data.
2. **Acknowledge** your contribution in our security acknowledgments (if desired).
3. **Keep you informed** of remediation progress.
4. **Coordinate disclosure** — we ask for a minimum 90-day embargo before public
   disclosure to allow remediation.

---

## Safe Harbor

MuVeraAI will not take legal action against security researchers who:
- Test only systems within the stated scope
- Do not access, modify, or delete customer data
- Do not perform denial of service attacks
- Do not share vulnerability details with third parties before remediation
- Act in good faith

Testing that accesses, exfiltrates, or modifies customer data is not covered by
safe harbor regardless of intent.

---

## Bug Bounty Program

We intend to launch a formal bug bounty program on HackerOne by Q3 2026.
Until that program is live, this responsible disclosure policy governs all reports.

Researchers who report qualifying vulnerabilities before the HackerOne launch
will be considered for retroactive rewards upon program launch.

**Expected reward tiers (subject to change at HackerOne launch):**

| Severity | Reward Range |
|----------|-------------|
| Critical (CVSS 9.0+) | $5,000 — $15,000 |
| High (CVSS 7.0-8.9) | $1,000 — $5,000 |
| Medium (CVSS 4.0-6.9) | $250 — $1,000 |
| Low (CVSS < 4.0) | Recognition only |

---

## Security Acknowledgments

We thank the following researchers for responsible disclosure:

*(none yet — be the first)*

---

## Contact

Security Team: `security@muveraai.com`
Trust Center: `trust.aumos.ai`
LinkedIn: `linkedin.com/company/muveraai`
