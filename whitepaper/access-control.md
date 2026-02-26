# AumOS Access Control

**Classification:** Public | **Version:** 1.0.0 | **Date:** February 2026

---

## Overview

AumOS implements defense-in-depth access control through multiple complementary mechanisms: Role-Based Access Control (RBAC) as the primary authorization model, Attribute-Based Access Control (ABAC) for fine-grained policy, Just-in-Time (JIT) access for privileged operations, and Privileged Access Management (PAM) for infrastructure-level access.

---

## Identity Lifecycle Management

### User Provisioning

Users are provisioned through two paths:

**IdP-Driven (Preferred)**
- SCIM 2.0 automated provisioning from Okta, Azure AD, Google Workspace, or Ping Identity
- User attributes (name, email, department, role mappings) sourced from IdP
- Role assignments mapped from IdP group memberships via configurable mapping rules
- Deprovisioning triggered automatically when IdP account is disabled or deleted (within 2 hours)

**Manual Provisioning**
- Available for tenants without SCIM-capable IdP
- User created by ORG_ADMIN; invitation email sent
- Default role: READ_ONLY; elevated by ORG_ADMIN after provisioning
- Requires MFA enrollment within 24 hours of first login

### User Deprovisioning

Deprovisioning sequence:
1. IdP account disabled → SCIM event received → AumOS account disabled within 2 hours
2. All active sessions invalidated immediately
3. All OAuth tokens and API keys revoked
4. JIT access sessions terminated
5. User account archived (not deleted) with 90-day retention for audit
6. Quarterly orphan account audit: accounts with no IdP record or no login in 90 days flagged for review

---

## Role-Based Access Control (RBAC)

### Role Hierarchy

```
SUPER_ADMIN (Level 5)
├─ Platform-wide configuration and access
├─ Only MuVeraAI staff; requires dual-person approval for sensitive actions
└─ All actions logged to separate immutable SUPER_ADMIN audit trail

ORG_ADMIN (Level 4)
├─ Manage all resources within a tenant
├─ User management: create, modify, deactivate users
├─ Billing and subscription management
└─ Requires MFA always; JIT for most sensitive actions

ADMIN (Level 3)
├─ Manage team resources and workspaces
├─ Configure integrations and API keys
├─ Read all audit logs within scope
└─ Cannot modify other ADMIN or ORG_ADMIN accounts

MEMBER (Level 2)
├─ Create and modify own resources
├─ Run agents and workflows
├─ Access to own interaction history and outputs
└─ Cannot access other members' private resources

READ_ONLY (Level 1)
├─ View resources shared with them
├─ Run read-only reports
└─ No create, modify, or delete permissions
```

### Permission Matrix (Illustrative)

| Action | READ_ONLY | MEMBER | ADMIN | ORG_ADMIN | SUPER_ADMIN |
|--------|-----------|--------|-------|-----------|-------------|
| View shared workspaces | Y | Y | Y | Y | Y |
| Run agents | N | Y | Y | Y | Y |
| Create workspaces | N | Y | Y | Y | Y |
| Configure integrations | N | N | Y | Y | Y |
| Manage users | N | N | N | Y | Y |
| View audit logs | N | N | Y | Y | Y |
| Manage billing | N | N | N | Y | Y |
| Platform configuration | N | N | N | N | Y |
| Access all tenants | N | N | N | N | Y |

### Role Assignment Controls

- Roles can only be assigned by users with a higher privilege level
- Role assignments are logged: who assigned, to whom, when, which role
- Bulk role assignments (>10 users) require ORG_ADMIN + secondary ADMIN approval
- Role escalation alerts: automated notification to ORG_ADMIN on any privilege elevation
- No self-escalation: users cannot assign themselves a higher role under any circumstances

---

## Attribute-Based Access Control (ABAC)

For organizations requiring finer-grained control beyond roles, AumOS supports ABAC via Open Policy Agent (OPA) integrated in `aumos-governance-engine`.

### Policy Examples

```rego
# Only allow access to PHI data from approved network ranges
allow {
    input.resource.classification == "PHI"
    input.user.network_zone == "corporate"
    input.time.hour >= 8
    input.time.hour <= 18
}

# Require manager approval for bulk data exports
allow {
    input.action == "bulk_export"
    input.approval.approved == true
    input.approval.approver_role >= "ADMIN"
}
```

### Contextual Access Conditions

ABAC policies can enforce conditions including:
- Network zone (corporate vs. external, VPN-connected)
- Device trust posture (MDM-enrolled, certificate present)
- Time of access (business hours, after-hours)
- Geographic location (country, region)
- Data classification of the requested resource
- Prior approval for the specific operation

---

## Just-in-Time (JIT) Access

For privileged operations — production database access, key management, infrastructure changes — AumOS enforces JIT access rather than standing privileges.

### JIT Workflow

1. User requests elevated access via the JIT portal, specifying:
   - Resource scope (specific database, environment, key path)
   - Duration (max 4 hours, default 1 hour)
   - Business justification
2. Request auto-approved if within policy (e.g., on-call engineer for their service), otherwise routed for approval
3. Approver (peer or manager) reviews and approves/denies
4. Credentials issued via Vault dynamic secrets — specific to the granted scope
5. All actions during JIT session tagged with JIT session ID in audit log
6. Credentials automatically expire at session end; revocation available before expiry
7. Post-access review: automated report to manager summarizing actions taken

### JIT-Required Operations

- Production database direct access
- Vault root token operations
- Infrastructure Terraform apply (production)
- Customer data access for support purposes
- Security configuration changes
- Cryptographic key management

---

## Privileged Access Management (PAM)

### MuVeraAI Staff Access to Production

MuVeraAI staff access to production infrastructure is strictly controlled:
- No standing production access for engineering staff
- All production access via JIT with 4-hour maximum session
- Production access requires separate authentication from development systems
- SSH access via bastion host or AWS SSM Session Manager — no direct SSH from internet
- All session commands logged and recorded (session recording)
- Break-glass access (for critical incidents) requires CISO or VP Engineering approval + post-incident review

### Customer Data Access

MuVeraAI staff access to customer data is:
- Prohibited by default; only permitted for:
  - Customer-authorized support operations (written consent required)
  - Legal obligation (subpoena, law enforcement request — customers notified unless prohibited by law)
  - Security incident investigation (with post-incident disclosure to customer)
- Every access to customer data logged and reported to customer in their audit log
- Customer data never accessed for model training without explicit consent

### Shared Account Prohibition

- No shared user accounts; every action must be attributable to a named individual
- Service accounts used only for automated processes — no human logins to service accounts
- Emergency "break-glass" accounts are sealed, require quorum to open, and each use is reported to CISO

---

## Multi-Factor Authentication (MFA)

### MFA Policy

| Account Type | MFA Required | Allowed Factors | Notes |
|-------------|-------------|-----------------|-------|
| All users | Yes — enforced | TOTP, FIDO2, SMS (fallback) | Cannot be disabled by user |
| Admin / ORG_ADMIN | Yes | TOTP, FIDO2 only | SMS not accepted at admin levels |
| SUPER_ADMIN | Yes | FIDO2 only | Hardware security key required |
| Service accounts | N/A | JWT + mTLS | MFA concept replaced by cryptographic identity |
| API access | Covered by service token | — | Tokens signed, short-lived |

### MFA Bypass

- Tenant ORG_ADMIN may request temporary MFA waiver for a specific user (max 24 hours)
- Waiver requires CISO approval + documented emergency reason
- All actions during waiver period are flagged in audit log
- No automatic waiver for any circumstance

### MFA Recovery

- Recovery codes: 8 single-use codes generated at MFA enrollment, stored by user
- Lost authenticator: identity re-verification via IdP or video identity check + ADMIN approval
- Recovery actions logged at elevated priority in audit trail

---

## API Access Control

### API Key Management

- API keys issued per user or per service account
- API keys have configurable scopes (specific endpoints and methods only)
- API key expiry: configurable (default 90 days); permanent keys available only for approved service accounts
- API keys never logged in plaintext — logged by masked ID only
- Key rotation enforced at expiry; rotation reminder 14 days before expiry
- API key compromise: immediate revocation via API or portal, automated detection of unusual usage patterns

### OAuth 2.0 / OIDC Delegation

For third-party integrations:
- OAuth 2.0 with PKCE (Proof Key for Code Exchange) for authorization code flow
- Scopes enforced: tokens limited to requested, approved scopes
- Token introspection endpoint for real-time validity check
- Refresh token rotation: old token invalidated when refresh token is used
- Application authorization listings viewable and revocable by user

---

## Access Review Program

### Regular Reviews

| Review Type | Frequency | Scope | Process |
|-------------|-----------|-------|---------|
| User access review | Quarterly | All active users | Manager attestation via automated workflow |
| Admin role review | Monthly | All admin-level accounts | CISO review |
| Service account review | Quarterly | All service accounts | Owning team attestation |
| Orphan account audit | Monthly | Accounts with no login in 90 days | Automated suspension + notification |
| Third-party access review | Quarterly | All OAuth grants and API keys | User notification to review |

### Access Review Workflow

1. Automated report generated listing all access grants
2. Email notification to reviewers with inline approve/revoke links
3. 14-day review window; escalation to ORG_ADMIN if not completed
4. Unreviewed access revoked automatically after 30-day grace period
5. Review completion and any changes logged in audit trail

---

## Physical Access Controls

Physical access to data center infrastructure is governed by the cloud provider (AWS, GCP):
- SOC 2 Type II certified providers with physical access controls including biometric authentication, security guards, and CCTV
- MuVeraAI staff have no physical data center access — all access is API/console-based
- For on-premises or sovereign deployments, customer is responsible for physical security; AumOS provides hardening guide
