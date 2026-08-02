# Security Notice

## Educational Use Only

This repository is **strictly educational**.

**Do not use** any generated parameters, algorithms, or code from this project for:
- Protecting real data or communications
- Production cryptographic systems
- Security-critical applications

## Why this matters

- The parameter estimates are from a **simplified toy model**, not a concrete security analysis.
- The native C extension has **not been audited** for side-channel resistance or correctness.
- The status of Astra #7 is "Lean 4 certificates exist, but peer review is ongoing."

## What you should use instead

For production post-quantum cryptography, use **NIST-standardized** implementations:
- **ML-KEM** (Kyber): [pq-crystals.org/kyber](https://pq-crystals.org/kyber/)
- **ML-DSA** (Dilithium): [pq-crystals.org/dilithium](https://pq-crystals.org/dilithium/)
- Reference implementations: [github.com/pq-crystals](https://github.com/pq-crystals)

## Reporting issues

If you discover a security issue in this educational code, please open a GitHub issue. Do not expect a CVE or rapid fix — this is a hobby project.
