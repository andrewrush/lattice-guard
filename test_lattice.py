#!/usr/bin/env python3
"""
LatticeGuard — юнит-тесты ядра.
Запуск: python test_lattice.py
        python test_lattice.py -v

Работает без внешних зависимостей (кроме NumPy, которая уже нужна проекту).
"""

from __future__ import annotations

import sys
import time
import traceback

from numpy.typing import NDArray
import numpy as np

from lattice import (
    attack_complexity,
    babai_rounding,
    compare_security_params,
    generate_lwe_instance,
    gs_min_norm,
    key_size_bytes,
    kyber_real_params,
    lll_reduction,
    _gram_schmidt_coeffs,
)

# Пытаемся импортировать нативное расширение
try:
    from gs_native import gs_min_norm_native, NATIVE_AVAILABLE
except Exception:
    NATIVE_AVAILABLE = False
    gs_min_norm_native = None


class TestRunner:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.passed = 0
        self.failed = 0
        self.tests: list[tuple[str, callable]] = []

    def add(self, name: str, fn: callable):
        self.tests.append((name, fn))

    def run(self) -> int:
        print("=" * 62)
        print("  LatticeGuard — юнит-тесты")
        if NATIVE_AVAILABLE:
            print("  Нативное расширение: доступно")
        else:
            print("  Нативное расширение: недоступно (cd native && bash build.sh)")
        print("=" * 62)
        start = time.perf_counter()

        for name, fn in self.tests:
            try:
                fn()
                self.passed += 1
                if self.verbose:
                    print(f"  ✓ {name}")
            except AssertionError as e:
                self.failed += 1
                print(f"  ✗ {name}")
                if self.verbose:
                    traceback.print_exc()
            except Exception as e:
                self.failed += 1
                print(f"  ✗ {name} (исключение: {e})")
                if self.verbose:
                    traceback.print_exc()

        elapsed = time.perf_counter() - start
        print("\n" + "-" * 62)
        print(f"Результат: {self.passed} пройдено, {self.failed} провалено")
        print(f"Время: {elapsed:.3f} сек")
        print("-" * 62)
        return 0 if self.failed == 0 else 1


def test_generate_lwe_shape():
    A, b, s, e = generate_lwe_instance(16, 97, seed=42)
    assert A.shape == (16, 16)
    assert b.shape == (16,)
    assert s.shape == (16,)
    assert e.shape == (16,)
    assert np.all((A >= 0) & (A < 97))
    assert np.all((s >= 0) & (s < 97))
    assert np.all((e >= -1) & (e <= 1))


def test_generate_lwe_reproducibility():
    A1, b1, s1, e1 = generate_lwe_instance(8, 13, seed=123)
    A2, b2, s2, e2 = generate_lwe_instance(8, 13, seed=123)
    assert np.array_equal(A1, A2)
    assert np.array_equal(b1, b2)
    assert np.array_equal(s1, s2)
    assert np.array_equal(e1, e2)


def test_generate_lwe_modulo():
    A, b, s, e = generate_lwe_instance(8, 13, seed=1)
    expected = (A @ s + e) % 13
    assert np.array_equal(b, expected)


def test_babai_rounding_shape():
    A, b, _, _ = generate_lwe_instance(8, 13, seed=42)
    v = babai_rounding(A, b)
    assert v.shape == (8,)


def test_babai_rounding_deterministic():
    A, b, _, _ = generate_lwe_instance(8, 13, seed=7)
    v1 = babai_rounding(A, b)
    v2 = babai_rounding(A, b)
    assert np.array_equal(v1, v2)


def test_gs_min_norm_positive():
    A, b, _, _ = generate_lwe_instance(8, 13, seed=42)
    norm = gs_min_norm(A)
    assert norm > 0, "Норма GS должна быть положительной"


def test_key_size_bytes():
    assert key_size_bytes(512, 3329) > 0
    assert key_size_bytes(1024, 3329) == 4 * key_size_bytes(512, 3329)


def test_compare_security_params():
    r = compare_security_params(128)
    assert r["security_bits"] == 128
    assert r["n_before"] == 512
    assert r["n_after"] < r["n_before"]
    assert r["saved_percent"] > 0


def test_attack_complexity():
    c = attack_complexity(512)
    assert c["n"] == 512
    assert c["astra_effective_bits"] > c["classical_bits"]
    assert c["boost_bits"] > 0


def test_kyber_params():
    params = kyber_real_params()
    assert len(params) == 3
    names = [p["name"] for p in params]
    assert "ML-KEM-512" in names
    assert "ML-KEM-768" in names
    assert "ML-KEM-1024" in names


def test_invalid_n():
    try:
        generate_lwe_instance(0, 97)
        assert False, "Должно было возникнуть ValueError"
    except ValueError:
        pass


def test_invalid_q():
    try:
        generate_lwe_instance(8, 1)
        assert False, "Должно было возникнуть ValueError"
    except ValueError:
        pass


def test_singular_basis_warning():
    B = np.ones((3, 3), dtype=np.int64)
    t = np.array([1, 2, 3], dtype=np.int64)
    try:
        babai_rounding(B, t)
    except ValueError:
        pass  # Ожидаемое поведение


# --- Тесты нативного расширения (только Gram-Schmidt) ---

def test_native_gs_min_norm():
    if not NATIVE_AVAILABLE:
        return  # skip
    A, _, _, _ = generate_lwe_instance(16, 97, seed=42)
    r1 = gs_min_norm(A)
    r2 = gs_min_norm_native(A)
    assert abs(r1 - r2) < 1e-6, f"GS mismatch: {r1} vs {r2}"


def test_native_gs_consistency():
    if not NATIVE_AVAILABLE:
        return
    for n in [8, 16, 32, 64]:
        A, _, _, _ = generate_lwe_instance(n, 97, seed=n)
        r1 = gs_min_norm(A)
        r2 = gs_min_norm_native(A)
        assert abs(r1 - r2) < 1e-6, f"GS mismatch at n={n}: {r1} vs {r2}"


def test_native_limits():
    if not NATIVE_AVAILABLE:
        return
    # n > 64 должно вызывать ValueError
    A, _, _, _ = generate_lwe_instance(65, 97, seed=1)
    try:
        gs_min_norm_native(A)
        assert False, "Должно было возникнуть ValueError для n>64"
    except ValueError:
        pass


def test_lll_2d_example():
    """Классический 2D пример: LLL должен найти короткий базис."""
    B = np.array([[2, 1], [0, 1]], dtype=np.int64)
    B_lll = lll_reduction(B)
    # Проверяем, что базис порождает ту же решётку
    assert abs(np.linalg.det(B_lll)) == abs(np.linalg.det(B))
    # Проверяем, что векторы короче
    assert np.linalg.norm(B_lll[:, 0]) <= np.linalg.norm(B[:, 0])


def test_lll_lovasz_condition():
    """Проверка условия Ловаса после LLL."""
    A, _, _, _ = generate_lwe_instance(8, 97, seed=42)
    A_lll = lll_reduction(A)
    mu, norms = _gram_schmidt_coeffs(A_lll)
    delta = 0.75
    for k in range(1, 8):
        assert norms[k] >= (delta - mu[k, k-1]**2) * norms[k-1] - 1e-6,             f"Lovasz failed at k={k}"


def test_lll_size_reduction():
    """Проверка size-reduction после LLL."""
    A, _, _, _ = generate_lwe_instance(8, 97, seed=42)
    A_lll = lll_reduction(A)
    mu, _ = _gram_schmidt_coeffs(A_lll)
    for i in range(8):
        for j in range(i):
            assert abs(mu[i, j]) <= 0.5 + 1e-6,                 f"Size reduction failed at mu[{i},{j}] = {mu[i,j]}"


def test_lll_improves_norms():
    """LLL должен уменьшать среднюю длину векторов."""
    A, _, _, _ = generate_lwe_instance(12, 97, seed=42)
    A_lll = lll_reduction(A)
    avg_before = sum(np.linalg.norm(A[:, i]) for i in range(12)) / 12
    avg_after = sum(np.linalg.norm(A_lll[:, i]) for i in range(12)) / 12
    assert avg_after < avg_before, "LLL не уменьшил среднюю длину векторов"


def main() -> int:
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    runner = TestRunner(verbose=verbose)

    # Core tests
    runner.add("LWE shape correctness", test_generate_lwe_shape)
    runner.add("LWE reproducibility", test_generate_lwe_reproducibility)
    runner.add("LWE modulo identity", test_generate_lwe_modulo)
    runner.add("Babai output shape", test_babai_rounding_shape)
    runner.add("Babai determinism", test_babai_rounding_deterministic)
    runner.add("GS norm positive", test_gs_min_norm_positive)
    runner.add("Key size formula", test_key_size_bytes)
    runner.add("Security params comparison", test_compare_security_params)
    runner.add("Attack complexity boost", test_attack_complexity)
    runner.add("Kyber params structure", test_kyber_params)
    runner.add("Invalid n raises error", test_invalid_n)
    runner.add("Invalid q raises error", test_invalid_q)
    runner.add("Singular basis handling", test_singular_basis_warning)

    # LLL tests
    runner.add("LLL 2D example", test_lll_2d_example)
    runner.add("LLL Lovasz condition", test_lll_lovasz_condition)
    runner.add("LLL size reduction", test_lll_size_reduction)
    runner.add("LLL improves norms", test_lll_improves_norms)

    # Native extension tests
    if NATIVE_AVAILABLE:
        runner.add("Native GS min norm", test_native_gs_min_norm)
        runner.add("Native GS consistency (8-64)", test_native_gs_consistency)
        runner.add("Native n>64 limit", test_native_limits)
    else:
        print("\n  [INFO] Нативные тесты пропущены — скомпилируйте: cd native && bash build.sh")

    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
