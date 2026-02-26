# Contributing to AumOS Security Documentation

## Who Should Contribute

- AumOS Security team (primary owners)
- Compliance and legal counsel (for framework mappings)
- Engineering leads (for technical accuracy reviews)

External contributions are not accepted for this repository. All content is maintained by MuVeraAI Corporation.

## Accuracy Standard

Every claim in this documentation must be:

1. **Technically accurate** — reflects actual platform capabilities, not aspirational goals
2. **Verifiable** — references a specific control, configuration, or codebase component
3. **Current** — kept in sync with platform changes within 30 days of a security-relevant deployment

If a feature described here does not yet exist, it must be marked `[PLANNED - Q{quarter} {year}]` with a linked engineering tracking issue.

## Contribution Process

1. Branch from `main` using prefix `docs/` or `fix/`
2. Make changes in Markdown — maintain control IDs for all compliance matrices
3. For Mermaid diagram changes, validate rendering locally (e.g., VS Code + Mermaid Preview extension)
4. Open a PR with `docs:` or `fix:` conventional commit title
5. Require review from at least one Security team member and one Compliance team member
6. Squash-merge once approved

## Control ID Stability

Compliance matrix control IDs (e.g., `SOC2-CC6.1`, `ISO-A.8.1`, `HIPAA-164.312(a)(1)`) are used as stable references in external questionnaire responses and audit evidence packages. Do not renumber or remove existing IDs — only deprecate with a note.

## Questionnaire Response Guidelines

When updating questionnaire responses:
- Be specific: "AumOS uses AES-256-GCM" not "AumOS uses strong encryption"
- Reference the actual component: "(see `aumos-secrets-vault`, `aumos-auth-gateway`)"
- Date-stamp any response that references a specific audit, certification, or test result

## Sensitive Information

Never include in this repository:
- Internal IP addresses, VPC CIDR ranges, or infrastructure identifiers
- Actual cryptographic keys, secrets, or credentials
- Customer names or tenants
- Pen test findings details (summarized mitigations only)
- Any information governed by an NDA
