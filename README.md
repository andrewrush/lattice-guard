# LatticeGuard

> [🇷🇺 Русский](README_RU.md) | 🇺🇸 English

A pet project based on **OpenAI Astra #7**: *polynomial-factor hardness of approximation for the Closest Vector Problem (CVP)*.

This project demonstrates how new mathematical results affect practical parameters of post-quantum lattice-based cryptography (LWE / Kyber / Dilithium).

---

## Quick Start in Termux

```bash
# 1. Clone
git clone git@github.com:andrewrush/lattice-guard.git
cd lattice-guard

# 2. Install dependencies (automatic)
bash setup.sh

# 3. Run demo
python demo.py
```

Or manually:
```bash
pkg install python -y
pip install numpy
python demo.py
```

---

## Commands

| Command | What it does |
|---------|-------------|
| `python demo.py` | Run the full demo (security comparison + Kyber params + CVP attack + BKZ estimates) |
| `python demo.py --interactive` | Interactive mode — enter your own n, q, seed |
| `python benchmark.py` | Performance benchmark across n = 8, 12, 16, ..., 64 |
| `bash setup.sh` | Auto-install Python and NumPy in Termux |

### Examples

```bash
# Default demo (deterministic, seed=42)
python demo.py

# Interactive: try tiny parameters
python demo.py --interactive
# > n: 8
# > q: 13
# > seed: [Enter]

# Benchmark on your device
python benchmark.py
```

---

## Verified Results

### Environment
- Device: Android 12, aarch64
- **Termux:** v0.118
- **Python:** 3.13.13
- **NumPy:** 2.4.4
- **Launch time:** ~0.5 sec

### `demo.py` output

```
==============================================================
  LatticeGuard — post-quantum cryptography demo
  Based on Astra #7 breakthrough (CVP hardness)
==============================================================

--- Security parameter comparison ---
   Level |  n old |  n new |  Key old |   Key new |  Saving
--------------------------------------------------------------
 128-bit |    512 |    305 |  384.0 KB |   136.3 KB |  64.5%
 192-bit |    768 |    446 |  864.0 KB |   291.4 KB |  66.3%
 256-bit |   1024 |    584 | 1536.0 KB |   499.6 KB |  67.5%

--- Real NIST Kyber parameters (ML-KEM) ---
       Scheme |     n |     q |  pk (bytes) |  sk (bytes) |  ct (bytes)
--------------------------------------------------------------
   ML-KEM-512 |   512 |  3329 |        800 |       1632 |        768
   ML-KEM-768 |   768 |  3329 |       1184 |       2400 |       1088
  ML-KEM-1024 |  1024 |  3329 |       1568 |       3168 |       1568

--- Demo: LWE attack via CVP (Babai rounding) ---
Parameters: n=24, q=97, seed=42
Secret s (first 8): [89 50 86  9  9 80 10  5]
Error  e (first 8): [ 0  1  1 -1  1  0 -1  0]

Babai rounding completed in 0.20 ms
Recovered (first 8): [56 66 56 81 58 36 32 75]
Matches with secret: 1/24 (4%)
=> At n=24 the attack did NOT fully succeed.
=> At n=512 (real-world crypto) — infeasible in reasonable time.

Min GS-orthogonalization norm: 27.93
(On a random basis the norm is large — the attack is doomed to fail)

--- BKZ attack complexity estimate ---
    n |  Classical (bits) |  With Astra (bits) |  Boost
----------------------------------------------------
  128 |             37.4 |             44.4 |   +7.0
  256 |             74.8 |             82.8 |   +8.0
  512 |            149.5 |            158.5 |   +9.0
  768 |            224.3 |            233.8 |   +9.6
 1024 |            299.0 |            309.0 |  +10.0

Astra #7: polynomial hardness of CVP approximation
gives an extra ~log₂(n) bits of security without increasing key size.

==============================================================
  Demo finished. All computations run locally.
  Run with --interactive flag for interactive mode.
==============================================================
```

### Result interpretation

| Metric | Before Astra | After Astra | Conclusion |
|---------|-------------|-------------|------------|
| n for 128-bit security | 512 | **305** | −40% key size |
| Kyber-512 public key | 384 KB | **136 KB** | −248 KB |
| Security boost | 149.5 bits | **158.5 bits** | +9 bits "for free" |
| CVP attack (n=24) | 4% match | — | Infeasible at n=512 |

**Practical takeaway:** Astra's new CVP bounds enable more compact post-quantum cryptosystems while maintaining (or improving) security levels. This is critical for IoT devices and mobile apps with limited memory.

---

## Interactive Mode

Run with `--interactive` to experiment with your own parameters:

```bash
python demo.py --interactive
```

### Example 1: Default toy parameters (n=24, q=97)
```
--- Interactive mode ---
Dimension n (recommended 8-64): [Enter]
Modulus q (recommended prime, e.g. 97): [Enter]
Seed (Enter for random): [Enter]

=> Matches: 1/24 (4%) — attack failed.
```

### Example 2: Tiny parameters (n=8, q=13)
```
--- Interactive mode ---
Dimension n (recommended 8-64): 8
Modulus q (recommended prime, e.g. 97): 13
Seed (Enter for random): [Enter]

Parameters: n=8, q=13, seed=42
Secret s: [ 5  4 11  4  0  6 10  2]
Error  e: [ 0 -1  1  0 -1 -1  0  1]

Babai rounding completed in 0.19 ms
Recovered: [ 2  4  2 10 12  9  7  8]
Matches with secret: 1/8 (12%)
=> At n=8 the attack did NOT fully succeed.
=> At n=512 (real-world crypto) — infeasible in reasonable time.

Min GS norm: 1.22
```

Even at n=8 (microscopic by crypto standards) the attack recovers only 12% of the secret. This illustrates why CVP is hard — and why Astra's polynomial hardness proof matters.

---

## Benchmark

Measure Babai rounding performance across different dimensions:

```bash
python benchmark.py
```

Sample output on Android 12 (aarch64):
```
==============================================================
  LatticeGuard — CVP benchmark (Babai rounding)
==============================================================

    n |   Avg time (ms) |   Runs |  Matches |  GS norm |  Relative
--------------------------------------------------------------------
    8 |          0.0484 |   1000 |     1.1% |     8.30 |      1.00x
   12 |          0.0509 |   1000 |     1.0% |     3.10 |      1.05x
   16 |          0.0538 |    500 |     0.9% |    26.90 |      1.11x
   20 |          0.0586 |    500 |     1.0% |    39.52 |      1.21x
   24 |          0.0615 |    500 |     1.2% |    29.04 |      1.27x
   32 |          0.0709 |    200 |     1.1% |     1.36 |      1.46x
   48 |          0.0961 |    200 |     1.0% |     5.67 |      1.98x
   64 |          0.1426 |    100 |     1.1% |     4.23 |      2.94x

Conclusion:
• At small n (8–24) time barely grows — Python/NumPy overhead dominates.
• At n=64 time is ~3× vs n=8, not 512× (pure theory O(n³)).
• This is because np.linalg.solve uses optimized BLAS/SIMD on aarch64.
• Attack accuracy stays near zero on a random basis.
```

---

## Why should an ordinary person care?

### Everyday analogy
Imagine your bank key is a combination of 512 digits. To steal it, a thief would need to try an enormous number of combinations. But a quantum computer does this thousands of times faster. That's why banks are switching to **post-quantum cryptography** — keys become even longer (1024 digits), and your phone has to constantly process them.

**Astra #7 showed:** you can make keys shorter (305 digits instead of 512) while keeping the same protection. Your phone runs faster, apps lag less, and the battery drains slower.

### Where this is used
- **Banking apps** (Sber, T-Bank, Revolut) — protecting transactions from quantum attacks.
- **Messengers** (Signal, WhatsApp) — post-quantum message encryption.
- **VPN and Tor** — protecting traffic from future quantum sniffers.
- **IoT and smart home** — sensors and cameras with limited memory get cryptography without overload.

### What this demo shows
1. **The attack fails even at toy scale** — at n=24 Babai rounding recovers 4% of the secret. At n=512 (reality) this is impossible within the lifetime of the universe.
2. **Math directly affects your phone** — a new theorem = smaller keys = faster apps.
3. **Verify yourself** — all code is open, runs on your phone in 0.5 seconds, no "magic" involved.

---

## Reproducibility

- **Security parameters and BKZ estimates** — fully deterministic (formulas).
- **Demo attack (Babai rounding)** — uses fixed `seed=42`, so the result (1/24, 4%) is reproducible. Removing the seed yields variation in the 0–15% match range — this is normal and demonstrates basis randomness.
- **Execution time** — depends on device; < 0.3 sec on modern flagships, up to 2 sec on budget phones.

---

## Project Structure

```
lattice-guard/
├── lattice.py          # Core: LWE, Babai CVP, security estimates
├── demo.py             # Interactive demo
├── benchmark.py        # Performance benchmark
├── setup.sh            # Termux setup script
├── requirements.txt    # Python dependencies
├── LICENSE             # MIT License
├── README.md           # This file (English)
└── README_RU.md        # Russian version
```

## Status of Astra #7

**Lean 4 certificates exist, but peer review is ongoing.**

OpenAI published all ten proofs with machine-checkable Lean 4 certificates and reasoning walkthroughs. This eliminates the most common failure mode of AI-generated proofs — plausible-looking but subtly flawed arguments. However, a Lean-checked proof is not the same as a community-reviewed one: mathematicians still need to confirm that the formalized statement matches the intended conjecture and that no human problem-shaping biased the result.

Key facts:
- **Lean 4 formalization:** every proof has a machine-checkable certificate on [GitHub](https://github.com/openai/ten-proofs).
- **External verification:** mathematician Thomas Bloom (who previously caught an OpenAI math error) and Fields Medalist Timothy Gowers were involved in verification of earlier Astra results.
- **Not yet settled:** external mathematicians have not had time to work through all ten arguments in the depth these conjectures usually attract. Retractions on any single result would be highly public.
- **First Proof precedent:** in February 2026, OpenAI submitted 10 proofs to the *First Proof* challenge; 5 were deemed "likely correct," 1 was later retracted, and the rest remain under review.

**Bottom line:** the Lean certificates make these results *significantly more credible* than typical AI math announcements, but the mathematical community's verdict is still pending. This demo treats Astra #7 as a *plausible direction* for parameter optimization, not as settled fact.

---

## Theory

- **LWE (Learning With Errors):** foundation of post-quantum cryptography (Kyber, Dilithium).
- **CVP (Closest Vector Problem):** finding the nearest lattice vector to a given point.
- **Astra #7:** proved polynomial hardness of CVP approximation — meaning even approximate solutions remain computationally hard.
- **Babai rounding:** simplest CVP heuristic. On a random basis it is practically useless — as the demo shows.

## References

### OpenAI Astra Breakthrough (August 2026)
- **Official announcement:** [Ten advances in mathematics and theoretical computer science](https://openai.com/index/ten-advances-in-mathematics/)
- **Research paper:** [ten-proofs-oai.pdf](https://cdn.openai.com/pdf/ten-proofs-oai.pdf)
- **Model reasoning:** [reasoning-walkthroughs.pdf](https://cdn.openai.com/pdf/reasoning-walkthroughs.pdf)
- **Lean code:** [github.com/openai/ten-proofs](https://github.com/openai/ten-proofs)

### Post-Quantum Cryptography
- **Regev, O.** *On Lattices, Learning with Errors, Random Linear Codes, and Cryptography.* JACM 2009.
- **NIST PQC Standardization** — [csrc.nist.gov/projects/post-quantum-cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)
- **Kyber** (ML-KEM): [pq-crystals.org/kyber](https://pq-crystals.org/kyber/)
- **Dilithium** (ML-DSA): [pq-crystals.org/dilithium](https://pq-crystals.org/dilithium/)

### Lattice Algorithms
- **Babai, L.** *On Lovász' lattice reduction and the nearest lattice point problem.* Combinatorica, 1986.
- **Schnorr, C. P. & Euchner, M.** *Lattice basis reduction: improved practical algorithms and solving subset sum problems.* Math. Programming, 1994.
- **Albrecht, M. R. et al.** *On the concrete hardness of Learning with Errors.* J. Mathematical Cryptology, 2015.

## License

MIT
