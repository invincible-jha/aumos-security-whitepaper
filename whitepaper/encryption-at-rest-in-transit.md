# AumOS Encryption — At Rest and In Transit

**Classification:** Public | **Version:** 1.0.0 | **Date:** February 2026

---

## Encryption Standards Overview

AumOS applies encryption comprehensively across all data storage and transmission paths. The platform uses only modern, recommended cryptographic algorithms; legacy algorithms (DES, 3DES, RC4, MD5, SHA-1 for signatures) are explicitly disabled.

---

## Encryption at Rest

### Database Encryption

**PostgreSQL (Primary Data Store)**
- Transparent Data Encryption (TDE) via cloud provider disk encryption: AES-256-XTS
- Application-layer encryption (envelope encryption) overlaid on TDE for defense in depth:
  - Tenant Encryption Key (TEK) wraps Data Encryption Keys (DEKs)
  - DEKs wrap individual field values for Restricted data
- Encryption enforced by `aumos-data-layer`; plaintext data never written to database without encryption check
- No unencrypted database replicas or read replicas

**Column-Level Encryption for Sensitive Fields**

Fields classified as Restricted (PII/PHI) are individually encrypted with Field Encryption Keys (FEK):

| Field Type | Algorithm | Key Source |
|-----------|-----------|-----------|
| Email addresses | AES-256-GCM | FEK from Vault |
| Phone numbers | AES-256-GCM | FEK from Vault |
| National ID / SSN | AES-256-GCM | FEK from Vault |
| Health record fields | AES-256-GCM | PHI-specific FEK from Vault |
| Payment card data | AES-256-GCM | Scope-isolated FEK; PCI-DSS zone |
| IP addresses (logs) | AES-256-GCM or truncation | Configurable per tenant |

### Object Storage Encryption

- S3-compatible object storage: AES-256-GCM with per-object DEK (envelope encryption via AWS KMS or customer-managed KMS)
- Server-Side Encryption with Customer-Managed Keys (SSE-CMK)
- Bucket versioning enabled; old version encryption preserved
- No unencrypted buckets (enforced via AWS Config rule / IaC policy)

### Cache Encryption

- Redis / ElastiCache: in-transit encryption (TLS) required, at-rest encryption for persistent caches
- Cache TTLs minimized; sensitive data cached with per-session encryption keys where possible
- Cache keys never contain plaintext tenant IDs or user identifiers (hashed with tenant-specific salt)

### Backup Encryption

- All backups encrypted with a separate Backup Key Encryption Key (BKEK)
- BKEK stored in Vault, separate from production TEK hierarchy
- Backup encryption verified before backup is considered valid
- Restore test monthly includes decryption verification

### Model Weights Encryption

- Model weight files stored encrypted: AES-256-GCM
- Model artifacts signed with MuVeraAI signing key (ED25519) for integrity verification
- Signature verified at load time by `aumos-model-registry` before inference

### Encryption Key Storage

All encryption keys are stored in `aumos-secrets-vault` (HashiCorp Vault):
- Vault seal: Auto-unseal using AWS KMS CMK (avoids manual unseal risk)
- Vault Raft HA: 3-node cluster for availability
- Vault audit log: all key operations logged to immutable storage
- Key material never leaves Vault in plaintext — Vault Transit Secrets Engine performs all crypto operations

---

## Encryption in Transit

### External Traffic (Client to Platform)

- **Protocol**: TLS 1.3 required; TLS 1.2 as minimum for legacy compatibility
- **Cipher suites (TLS 1.3)**: TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256 (in order of preference)
- **Cipher suites (TLS 1.2, if used)**: ECDHE-RSA-AES256-GCM-SHA384, ECDHE-ECDSA-AES256-GCM-SHA384 only (ECDHE required for forward secrecy)
- **Key exchange**: ECDHE with P-256 or X25519 curves only (DHE with weak groups disabled)
- **Certificate type**: RSA-2048 minimum; ECDSA P-256 preferred
- **HSTS**: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- **Certificate pinning**: Available for mobile/native clients (not enabled for web clients due to operational complexity)

### Internal Traffic (Service to Service)

- **Protocol**: mTLS (mutual TLS) enforced across all service-to-service communication
- **Certificate authority**: Internal platform CA managed by SPIRE (SPIFFE Runtime Environment)
- **Certificate lifetime**: 24-hour SVIDs (SPIFFE Verifiable Identity Documents), auto-rotated
- **Cipher suites**: Same as external TLS preferences
- **Enforcement**: Istio service mesh in strict mTLS mode — plaintext connections rejected

### Database Connections

- All application → database connections use TLS (sslmode=require in PostgreSQL connection strings)
- Certificate validation enforced (sslmode=verify-full preferred; verify-ca minimum)
- Database connections over private network only; no public endpoint

### Message Queue (Kafka)

- Producer → Kafka and Consumer → Kafka: TLS 1.2+ with client certificate authentication
- Broker-to-broker communication: mTLS
- Topics containing sensitive data: Confluent Schema Registry with client-side encryption option

### Email (Transactional)

- Outbound transactional email via Resend with SMTP TLS enforced
- DKIM signing on all outbound email (SHA-256)
- DMARC policy: quarantine (minimum), reject (target)
- SPF configured for all sending domains

---

## Key Management

### Key Hierarchy

```
HSM Hardware Root (FIPS 140-2 Level 3)
└─ Vault Master Key (Shamir Secret Sharing — 5 key shares, 3-of-5 threshold)
    ├─ Vault Auto-Unseal Key (AWS KMS CMK — for operational availability)
    ├─ Platform Signing Key (RS256 / ED25519)
    │   ├─ JWT Signing Key (RS256, rotated every 90 days)
    │   ├─ Model Artifact Signing Key (ED25519)
    │   └─ Audit Log Signing Key (HMAC-SHA256)
    ├─ TLS Root CA (ECDSA P-256, 10-year validity)
    │   └─ Intermediate CA (ECDSA P-256, 1-year validity, issued to SPIRE)
    │       └─ Service SVIDs (ECDSA P-256, 24-hour validity, per-service)
    └─ Encryption Key Hierarchy
        ├─ Platform Master Encryption Key (PMEK)
        │   └─ Per-Tenant Key Encryption Key (TEK)
        │       ├─ Data Encryption Key — General (DEK-G, 256-bit AES)
        │       ├─ Data Encryption Key — PII (DEK-PII, 256-bit AES)
        │       ├─ Data Encryption Key — PHI (DEK-PHI, 256-bit AES)
        │       └─ Field Encryption Keys (FEK, per-field, 256-bit AES)
        └─ Backup Key Encryption Key (BKEK, separate hierarchy)
```

### Key Rotation Schedule

| Key Type | Rotation Frequency | Rotation Method |
|---------|-------------------|----------------|
| JWT Signing Key | 90 days | Automated; overlap period for token validation |
| TLS Certificates (external) | 90 days (Let's Encrypt) | Automated via cert-manager |
| mTLS SVIDs | 24 hours | Automated by SPIRE |
| TLS Intermediate CA | 1 year | Automated with HSM re-signing |
| Tenant DEKs | 1 year | Automated with re-encryption job |
| Field Encryption Keys | On demand / 2 years max | Admin-triggered or scheduled |
| Vault Master Key (shares) | Annual | Manual ceremony with quorum |
| BKEK | Annual | Manual ceremony with quorum |

### Bring Your Own Key (BYOK)

Enterprise customers may supply their own root encryption key:

1. Customer creates a CMK in their own KMS (AWS KMS, Azure Key Vault, Google Cloud KMS)
2. Customer grants AumOS kms:Encrypt and kms:Decrypt permissions (not kms:GenerateDataKey for key generation — only for envelope operations)
3. AumOS wraps TEKs under the customer-supplied CMK
4. Customer-supplied CMK can be rotated or revoked at any time; revocation immediately renders AumOS-encrypted data unreadable by AumOS (complete data sovereignty)
5. BYOK key usage logged in both customer's KMS audit trail and AumOS audit log

---

## Homomorphic Encryption (Advanced)

For the most sensitive analytical workloads where even encrypted data must not be decrypted during computation, `aumos-homomorphic-encryption` provides:

- Partial homomorphic encryption (PHE) for sum and average operations on encrypted numerical data
- Fully Homomorphic Encryption (FHE) via TFHE library for complex predicates (compute on encrypted data without decryption)
- Use case: Cross-tenant analytics, privacy-preserving benchmarking, encrypted ML inference
- Current performance: ~10–1000x overhead vs. plaintext computation (acceptable for batch analytics, not real-time)
- Scheme support: BFV (integer arithmetic), CKKS (approximate real-number arithmetic)

---

## Cipher Algorithm Prohibition List

The following algorithms are explicitly prohibited and disabled in all AumOS-controlled components:

| Prohibited | Category | Reason |
|-----------|----------|--------|
| DES, 3DES | Block cipher | Insufficient key size, known weaknesses |
| RC4, RC2 | Stream cipher | Known biases, insecure |
| MD5 | Hash | Collision attacks; not for signatures |
| SHA-1 | Hash | Collision attacks; not for signatures (OK for HMAC with known caveats) |
| RSA < 2048 bits | Asymmetric | Insufficient key size |
| DHE with primes < 2048 | Key exchange | Logjam vulnerability |
| EXPORT cipher suites | Various | Intentionally weakened |
| NULL cipher suites | Various | No encryption |
| Anonymous DH (aDH) | Key exchange | No authentication |
| SSL 2.0, SSL 3.0, TLS 1.0, TLS 1.1 | Protocol | Known vulnerabilities (POODLE, BEAST, DROWN) |

Compliance with this prohibition list is enforced by:
- Cryptographic library configuration (OpenSSL, BoringSSL, rustls)
- Automated TLS configuration scanning (testssl.sh in CI)
- Annual penetration test TLS configuration assessment

---

## Post-Quantum Readiness

`aumos-quantum-readiness` tracks the evolving post-quantum cryptography landscape:

- Current algorithms (RSA-2048, ECDSA P-256, ECDHE X25519) are quantum-vulnerable to Grover/Shor algorithms with a sufficiently capable quantum computer
- Harvest Now, Decrypt Later (HNDL) threat: data encrypted today may be decryptable by future quantum computers
- Migration path planned to NIST PQC standards:
  - Key Encapsulation: ML-KEM (Kyber) — FIPS 203
  - Digital Signatures: ML-DSA (Dilithium) — FIPS 204
  - Hybrid mode: classical + PQC in parallel during transition
- Timeline: Migration tooling ready by 2027; full migration by 2028 per NIST guidance
- High-sensitivity customers (government, healthcare) may request expedited PQC migration

See `aumos-quantum-readiness` documentation for detailed migration roadmap.
