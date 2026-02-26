# AumOS Security Whitepaper — CLAUDE.md

## Purpose

CISO-targeted security documentation repository. Contains the AumOS platform security architecture whitepaper, enterprise security questionnaire responses (200+), STRIDE threat model, data flow diagrams, and compliance control matrices for SOC 2, ISO 27001, HIPAA, and NIST CSF.

## Repository Type

Documentation-only. No application code, no services, no deployments. Pure Markdown content for enterprise sales and compliance workflows.

## Audience

- Chief Information Security Officers (CISOs)
- Security architects
- Compliance and risk teams
- Procurement / vendor assessment teams

## Structure

```
whitepaper/          # Core security architecture documents
questionnaire/       # 200+ Q&A for vendor security reviews
threat-model/        # STRIDE analysis and attack surface
data-flow/           # Mermaid diagrams for data flow and tenant isolation
compliance-matrix/   # SOC 2, ISO 27001, HIPAA, NIST CSF mappings
```

## Editing Guidelines

- All content in GitHub-flavored Markdown
- Mermaid diagrams for all architecture visuals (render in GitHub/Obsidian)
- Control IDs are stable identifiers — do not change existing IDs without updating all cross-references
- Version changes in CHANGELOG.md following Conventional Commits
- Questionnaire responses must be accurate, specific, and reference actual AumOS capabilities

## Content Standards

- No vague marketing language — every claim must be verifiable
- Reference specific AumOS repos (e.g., `aumos-security-runtime`, `aumos-auth-gateway`) where relevant
- Compliance control mappings cite actual framework control IDs
- Threat model updated whenever new attack surface is introduced
