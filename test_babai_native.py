#!/usr/bin/env python3
"""
Тест корректности и скорости native/babai.c против Python-реализации.
Запуск: python test_babai_native.py
"""

from __future__ import annotations

import time
import numpy as np

from lattice import babai_rounding
from babai_native import is_available, babai_rounding_native


def test_correctness(n: int, seed: int = 42) -> dict:
    """Сравнивает Python и C версии на одних данных."""
    rng = np.random.default_rng(seed)
    B_int = rng.integers(0, 97, size=(n, n), dtype=np.int64)
    t_int = rng.integers(0, 97, size=n, dtype=np.int64)

    py_result = babai_rounding(B_int, t_int)
    c_result = babai_rounding_native(B_int.astype(np.float64), t_int.astype(np.float64))

    diff = np.abs(py_result.astype(np.float64) - c_result)
    return {
        "n": n,
        "max_diff": float(np.max(diff)),
        "mean_diff": float(np.mean(diff)),
        "match": float(np.max(diff)) < 1e-6,
    }


def benchmark_speed(n: int, runs: int = 500) -> dict:
    """Замеряет время Python vs C."""
    rng = np.random.default_rng(123 + n)
    B = rng.integers(0, 97, size=(n, n), dtype=np.int64)
    t = rng.integers(0, 97, size=n, dtype=np.int64)

    start = time.perf_counter()
    for _ in range(runs):
        _ = babai_rounding(B, t)
    py_time = (time.perf_counter() - start) * 1000

    B_f = B.astype(np.float64)
    t_f = t.astype(np.float64)
    start = time.perf_counter()
    for _ in range(runs):
        _ = babai_rounding_native(B_f, t_f)
    c_time = (time.perf_counter() - start) * 1000

    return {
        "n": n,
        "runs": runs,
        "py_avg_ms": round(py_time / runs, 4),
        "c_avg_ms": round(c_time / runs, 4),
        "speedup": round(py_time / c_time, 1) if c_time > 0 else float('inf'),
    }


def main() -> int:
    print("=" * 62)
    print("  LatticeGuard — тест native Babai rounding")
    print("=" * 62)

    if not is_available():
        print("\n❌ Native library НЕ найдена.")
        print("   Соберите: cd native && bash build_babai.sh")
        return 1

    print("\n✅ Native library доступна")
    print()

    print("--- Корректность (Python vs C, допуск < 1e-6) ---")
    print(f"{'n':>4} | {'max diff':>12} | {'mean diff':>12} | {'status':>8}")
    print("-" * 50)

    all_ok = True
    for n in [8, 12, 16, 24, 32]:
        r = test_correctness(n)
        status = "✅ OK" if r["match"] else "❌ FAIL"
        if not r["match"]:
            all_ok = False
        print(f"{n:>4} | {r['max_diff']:>12.2e} | {r['mean_diff']:>12.2e} | {status}")

    print()
    print("--- Скорость (Python vs C) ---")
    print(f"{'n':>4} | {'runs':>6} | {'Python (ms)':>12} | {'C (ms)':>10} | {'speedup':>8}")
    print("-" * 60)

    for n in [8, 16, 24, 32]:
        runs = 1000 if n <= 16 else 500
        r = benchmark_speed(n, runs)
        print(f"{r['n']:>4} | {r['runs']:>6} | "
              f"{r['py_avg_ms']:>10.4f} | {r['c_avg_ms']:>8.4f} | {r['speedup']:>6.1f}x")

    print()
    if all_ok:
        print("✅ Все тесты пройдены. Native Babai rounding работает корректно.")
    else:
        print("⚠️  Есть расхождения. Алгоритмы должны быть идентичны.")

    return 0 if all_ok else 1


if __name__ == "__main__":
    exit(main())
