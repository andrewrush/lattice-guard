# LatticeGuard

> [🇷🇺 Русский](README_RU.md) | 🇺🇸 English

A pet project based on **OpenAI Astra #7**: *polynomial-factor hardness of approximation for the Closest Vector Problem (CVP)*.

This project demonstrates how new mathematical results could affect practical discussions of post-quantum lattice-based cryptography (LWE / Kyber / Dilithium).

> ⚠️ **Research Status:** This project is an **educational exploration**, not a cryptographic standard. The parameter reductions shown are **illustrative estimates** based on a simplified model. They are **not valid ML-KEM parameters** and must not be used in production cryptography. The status of Astra #7 is "Lean 4 certificates exist, but peer review is ongoing."

---

## Quick Start in Termux

```bash
# 1. Clone
git clone git@github.com:andrewrush/lattice-guard.git
cd lattice-guard

# 2. Install dependencies (automatic)
bash setup.sh

# 3. (Optional) Compile native extension for Gram-Schmidt speed comparison
bash native/build.sh

# 4. Run tests to verify everything works
python test_lattice.py

# 5. Run demo
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
| `python demo.py --json` | Output results as JSON (to stderr, for piping) |
| `python benchmark.py` | Performance benchmark across n = 8, 12, 16, ..., 64 |
| `python benchmark.py --json` | Benchmark output as JSON |
| `python benchmark.py --export results.json` | Save benchmark results to file |
| `python export.py` | Export security tables to JSON |
| `python export.py --samples --format csv` | Export attack samples to CSV |
| `python test_lattice.py` | Run unit tests (no pytest required) |
| `python test_lattice.py -v` | Verbose test output |
| `python gs_native.py` | Test native C extension (Gram-Schmidt only, if compiled) |
| `bash setup.sh` | Auto-install Python and NumPy in Termux |
| `bash native/build.sh` | Compile C extension for Gram-Schmidt |

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

# Export results for analysis on desktop
python benchmark.py --export /sdcard/lattice_benchmark.json
```

---

## What's New (Improved Version)

This release adds several quality-of-life improvements while keeping all original functionality intact:

- **`.gitignore`** — prevents accidental commits of `__pycache__`, virtualenvs, and result files.
- **`requirements.txt`** — pinned NumPy version compatible with Termux.
- **`test_lattice.py`** — 13 unit tests that run without pytest (pure Python), plus 3 native extension tests.
- **`export.py`** — export demo/benchmark results to JSON or CSV (useful for data analysis on desktop).
- **`--json` flag** — both `demo.py` and `benchmark.py` support machine-readable JSON output.
- **`--export` flag** — save benchmark results directly to a file.
- **Robust `setup.sh`** — checks Python version, verifies NumPy works, and gives clear error messages.
- **Input validation** — `lattice.py` now validates parameters and handles degenerate bases gracefully.
- **Standard deviation** — benchmark reports `std_ms` for each dimension.
- **Multi-seed statistics** — CVP demo now runs across multiple seeds to show variability.
- **Native C extension** — optional `gs_native.c` with Python bindings via `ctypes` for Gram-Schmidt performance comparison.

---

## Verified Results

### Environment
- Device: Android 12, aarch64
- **Termux**
- **Python:** 3.13.13
- **NumPy:** 2.4.4
- **Launch time:** ~0.5 sec

### `demo.py` output

```
==============================================================
  LatticeGuard — post-quantum cryptography demo
  Based on Astra #7 breakthrough (CVP hardness)
==============================================================

--- Security parameter comparison (simplified model) ---
   Level |  n old |  n new |  Key old |   Key new |  Saving
--------------------------------------------------------------
 128-bit |    512 |    305 |  384.0 KB |   136.3 KB |  64.5%
 192-bit |    768 |    446 |  864.0 KB |   291.4 KB |  66.3%
 256-bit |   1024 |    584 | 1536.0 KB |   499.6 KB |  67.5%

--- Reference ML-KEM parameter sets (shown for comparison, not modified by this project) ---
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
=> On this random instance, the Babai heuristic did NOT recover the secret.
=> At cryptographic dimensions, this toy experiment is not an attack-cost estimate.

Multi-seed statistics (100 seeds, n=24):
  Average match rate: 0.9%
  Maximum match rate: 8.3%
  Full recovery rate: 0%
  Standard deviation: 1.9%

  Note: At n=24, a single matching coordinate equals ~4.17%. Match rates are discrete
  and should not be over-interpreted as precise probabilities in this toy setting.

Min GS-orthogonalization norm: 27.93
(On an unreduced random basis the norm is large — the Babai heuristic is ineffective for this toy instance)

--- BKZ attack complexity estimate (simplified model) ---
    n |  Classical (bits) |  With Astra (bits) |  Boost
----------------------------------------------------
  128 |             37.4 |             44.4 |   +7.0
  256 |             74.8 |             82.8 |   +8.0
  512 |            149.5 |            158.5 |   +9.0
  768 |            224.3 |            233.8 |   +9.6
 1024 |            299.0 |            309.0 |  +10.0

Under the simplified model used here, the assumed Astra-style factor
is represented as an approximately log₂(n)-bit increase.

==============================================================
  Demo finished. All computations run locally.
  Run with --interactive flag for interactive mode.
==============================================================
```

### Result interpretation

| Metric | Before Astra | After Astra | Conclusion |
|---------|-------------|-------------|------------|
| n for 128-bit security (model) | 512 | **305** | −40% key size in toy model |
| Toy-model public key (n=512→305) | 384 KB | **136 KB** | −248 KB in simplified estimate |
| Security boost (model) | 149.5 bits | **158.5 bits** | +9 bits in simplified estimate |
| Babai heuristic (n=24) | 4% match | — | Failed on this random instance |

**Important:** These numbers come from a **simplified theoretical model**, not from a full concrete-security analysis of ML-KEM. Real ML-KEM parameters involve compression, error distributions, Module-LWE structure, and failure probabilities that are not captured here.

**Formula used:** `toy_key_size = n² · ⌈log₂(q)⌉ / 8` bytes. This is **not** the actual ML-KEM public key size.

**Practical takeaway (if Astra #7 is confirmed):** stronger CVP bounds could enable discussions about more compact post-quantum parameters, but any real parameter change requires rigorous independent analysis.

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

=> On this instance, Babai heuristic matched 1/24 (4%).
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
=> On this random instance, the Babai heuristic did NOT recover the secret.
=> At cryptographic dimensions, this toy experiment is not an attack-cost estimate.

Min GS norm: 1.22
```

Even at n=8 (microscopic by crypto standards) the heuristic recovers only 12% of the secret on this instance. This illustrates that unreduced random bases are unsuitable for recovering this toy instance with the Babai heuristic — and why a rigorous hardness result for approximate CVP could matter, if confirmed and shown to apply to the relevant cryptographic setting.

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

    n |   Avg time (ms) |   Std dev |   Runs |  Matches |  GS norm |  Relative
--------------------------------------------------------------------------------
    8 |          0.0484 |    0.0021 |   1000 |     1.1% |     8.30 |      1.00x
   12 |          0.0509 |    0.0023 |   1000 |     1.0% |     3.10 |      1.05x
   16 |          0.0538 |    0.0028 |    500 |     0.9% |    26.90 |      1.11x
   20 |          0.0586 |    0.0031 |    500 |     1.0% |    39.52 |      1.21x
   24 |          0.0615 |    0.0032 |    500 |     1.2% |    29.04 |      1.27x
   32 |          0.0709 |    0.0041 |    200 |     1.1% |     1.36 |      1.46x
   48 |          0.0961 |    0.0054 |    200 |     1.0% |     5.67 |      1.98x
   64 |          0.1426 |    0.0089 |    100 |     1.1% |     4.23 |      2.94x

Conclusion:
• At small n (8–24) time barely grows — Python/NumPy overhead dominates.
• At n=64 time is ~3× vs n=8. The idealized cubic ratio would be 512×, but fixed overhead (Python interpreter, NumPy dispatch) and optimized BLAS dominate at this scale.
• This is because np.linalg.solve uses optimized BLAS/SIMD on aarch64.
• Attack accuracy stays near zero on a random basis.
```

---


## Lattice Reduction: LLL

The project includes a pure-Python implementation of the **LLL (Lenstra-Lenstra-Lovász)** lattice reduction algorithm. This demonstrates a key concept in lattice cryptography: a "good" basis makes the lattice look very different from a "bad" one, but it does **not** break properly constructed LWE.

### What LLL does

LLL transforms a random basis into an equivalent basis that is:
- **Nearly orthogonal** — vectors are close to 90° to each other
- **Relatively short** — vector lengths are bounded by a factor of the shortest possible

### Demo: random vs LLL basis

```bash
python demo.py
```

Sample output (n=16):
```
--- Demo: effect of LLL reduction on Babai rounding ---
Parameters: n=16, q=97, seed=42

Average basis vector length:
  Random: 219.0
  LLL:    98.9
  Improvement: 2.2×

Babai rounding — matches with secret:
  Random basis: 0/16 (0%)
  LLL basis:    0/16 (0%)

=> LLL makes the basis ~2× shorter,
=> but Babai rounding still does not recover the secret.
=> This toy experiment does not model the full range of lattice attacks against LWE, which may use approximate reduction, enumeration, sieving, decoding, or primal/dual strategies. LLL alone does not provide a concrete security estimate for LWE.
```

### Interpretation

| Basis type | Avg vector length | Babai match rate | Conclusion |
|-----------|-------------------|------------------|------------|
| Random | ~219 | ~0% | Bad basis, heuristic fails |
| LLL-reduced | ~99 | ~0% | Good basis, heuristic **still** fails |

This is the core security argument for LWE: even with a high-quality basis, the **Closest Vector Problem** remains hard because the error vector `e` is carefully chosen to place the target point `b` far from any lattice vector. LLL helps with CVP *approximation*, but LWE is designed to resist exactly that.

### Where this fits in real cryptography

In lattice-based cryptography:
- A public LWE instance can be embedded into a lattice basis that is unsuitable for known attacks.
- This should not be interpreted as saying that the secret key is literally a short or reduced basis. The exact relation between public parameters and secret key depends on the specific scheme and attack formulation.
- ML-KEM (Kyber) uses Module-LWE, not a simple trapdoor lattice scheme in the GPV/Falcon sense.
- LLL alone cannot break properly parameterised LWE.

---
## Native C Extension (Optional)

For educational comparison between Python and native C performance on Gram-Schmidt orthogonalization:

```bash
# Compile
bash native/build.sh

# Test
python gs_native.py
```

The native extension implements **Gram-Schmidt orthogonalization** only. Babai rounding remains in Python (already fast enough at ~0.7 ms). The extension exists to demonstrate FFI and measure the Python interpreter overhead on tight loops.

**Measured speedup on Android 12 (aarch64):**

| n | Python (ms) | Native C (ms) | Speedup |
|---|-------------|---------------|---------|
| 8 | 0.57 | 0.22 | **2.6×** |
| 16 | 1.85 | 0.11 | **17.5×** |
| 32 | 7.15 | 0.18 | **39.7×** |
| 64 | 28.87 | 0.45 | **64.8×** |

The speedup grows with n because the Python implementation uses nested loops, while the C version eliminates interpreter overhead.

**Numerical equivalence:** `max_abs_error(Python, C) = 8.44e-14` — all tested dimensions match to machine precision.

> **Note:** These numbers measure only the explicit Gram–Schmidt loops. The main `benchmark.py` measures the complete NumPy-based routine (including `np.linalg.solve` for Babai), which is why its times differ. The native extension changes performance only; it does not change the security model or attack success probability.

---

## Why should an ordinary person care?

### Everyday analogy

Imagine your bank uses a mathematical puzzle with hundreds of coordinates in a high-dimensional space. To steal your key, a thief would need to solve an enormously complex geometric problem. But a quantum computer makes this thousands of times faster. That's why banks are switching to **post-quantum cryptography** — the puzzles become even larger, and your phone has to constantly process them.

**If Astra #7 is confirmed and applicable:** it might enable discussions about more efficient puzzles while keeping the same protection. Your phone could run faster, apps could lag less, and the battery could drain slower. But this is still a research direction, not a deployed solution.

### Where this is used
- **Banking apps** (Sber, T-Bank, Revolut) — protecting transactions from quantum attacks.
- **Messengers** (Signal, WhatsApp) — post-quantum message encryption.
- **VPN and Tor** — protecting traffic from future quantum sniffers.
- **IoT and smart home** — sensors and cameras with limited memory get cryptography without overload.

### What this demo shows
1. **The Babai heuristic fails even at toy scale** — at n=24 it recovers 4% of the secret on this instance. At cryptographic dimensions, this toy experiment is not an attack-cost estimate.
2. **Math directly affects your phone** — a new theorem, if confirmed, could inspire smaller keys and faster apps.
3. **Verify yourself** — all code is open, runs on your phone in 0.5 seconds, no "magic" involved.

---

## Reproducibility

- **Security parameters and BKZ estimates** — fully deterministic (formulas from simplified model).
- **Demo attack (Babai rounding)** — uses fixed `seed=42`, so the result (1/24, 4%) is reproducible. Removing the seed yields variation in the 0–15% match range — this is normal and demonstrates basis randomness.
- **Multi-seed statistics** — running 100 seeds shows the heuristic consistently fails across random instances.
- **Execution time** — depends on device; < 0.3 sec on modern flagships, up to 2 sec on budget phones.

---

## Project Structure

```
lattice-guard/
├── lattice.py          # Core: LWE, Babai CVP, security estimates
├── demo.py             # Interactive demo (+ --json, multi-seed stats)
├── benchmark.py        # Performance benchmark (+ --export)
├── export.py           # Export results to JSON/CSV
├── test_lattice.py     # Unit tests (no pytest needed)
├── gs_native.py        # Python bindings for optional C extension (Gram-Schmidt only)
├── native/
│   ├── gs_native.c     # Native Gram-Schmidt (C)
│   └── build.sh        # Build script for Termux/Linux/macOS
├── setup.sh            # Termux setup script (robust)
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
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
- **First Proof precedent:** in February 2026, OpenAI submitted 10 proofs to the _First Proof_ challenge; 5 were deemed "likely correct," 1 was later retracted, and the rest remain under review.

**Bottom line:** the Lean certificates make these results _significantly more credible_ than typical AI math announcements, but the mathematical community's verdict is still pending. This demo treats Astra #7 as a _plausible direction_ for parameter optimization, not as settled fact.

---

## Serious Tools for Lattice Analysis

This project is a **toy educational demo**. For production-grade lattice cryptography analysis, use professional tools:

- **[lattice-estimator](https://github.com/malb/lattice-estimator)** — Python library for concrete security estimation of LWE and NTRU
- **[fplll / fpylll](https://github.com/fplll/fplll)** — state-of-the-art lattice reduction (C++ / Python bindings)
- **[LWE-Estimator](https://lattice-estimator.readthedocs.io/)** — comprehensive concrete hardness estimates
- **[NIST PQC Standardization](https://csrc.nist.gov/projects/post-quantum-cryptography)** — official ML-KEM / ML-DSA specifications

---

## Troubleshooting

### `ImportError: No module named numpy`
Run `bash setup.sh` or `pip install numpy`.

### `ldd: error: expected absolute path`
This is a Termux quirk unrelated to this project. Use `readelf -d ./file | grep NEEDED` instead.

### Tests fail on first run
Make sure you are in the project directory and `lattice.py` is importable:
```bash
cd ~/lattice-guard
python test_lattice.py
```

### Benchmark is slow on old device
This is expected. Try smaller dimensions:
```bash
python benchmark.py --n 8 12 16 24
```

### Native extension fails to compile
Make sure you have a C compiler installed:
```bash
pkg install clang
bash native/build.sh
```
If compilation fails, the project works fine without it — just ignore the warning.

---

## Theory

- **LWE (Learning With Errors):** foundation of post-quantum cryptography (Kyber, Dilithium).
- **CVP (Closest Vector Problem):** finding the nearest lattice vector to a given point.
- **Astra #7:** proved polynomial hardness of CVP approximation — meaning even approximate solutions remain computationally hard (if the proof holds).
- **Babai rounding:** simplest CVP heuristic. On a random basis it is practically useless — as the demo shows.

## References

### OpenAI Astra Breakthrough (August 2026)
- **Official announcement:** [Ten advances in mathematics and theoretical computer science](https://openai.com/index/ten-advances-in-mathematics/)
- **Research paper:** [ten-proofs-oai.pdf](https://cdn.openai.com/pdf/ten-proofs-oai.pdf)
- **Model reasoning:** [reasoning-walkthroughs.pdf](https://cdn.openai.com/pdf/reasoning-walkthroughs.pdf)
- **Lean code:** [github.com/openai/ten-proofs](https://github.com/openai/ten-proofs)

### Post-Quantum Cryptography
- **Regev, O.** _On Lattices, Learning with Errors, Random Linear Codes, and Cryptography._ JACM 2009.
- **NIST PQC Standardization** — [csrc.nist.gov/projects/post-quantum-cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)
- **Kyber** (ML-KEM): [pq-crystals.org/kyber](https://pq-crystals.org/kyber/)
- **Dilithium** (ML-DSA): [pq-crystals.org/dilithium](https://pq-crystals.org/dilithium/)

### Lattice Algorithms
- **Babai, L.** _On Lovász' lattice reduction and the nearest lattice point problem._ Combinatorica, 1986.
- **Schnorr, C. P. & Euchner, M.** _Lattice basis reduction: improved practical algorithms and solving subset sum problems._ Math. Programming, 1994.
- **Albrecht, M. R. et al.** _On the concrete hardness of Learning with Errors._ J. Mathematical Cryptology, 2015.

## License

MIT
