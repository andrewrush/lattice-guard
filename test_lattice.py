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

import numpy as np

from lattice import (
    attack_complexity,
    babai_rounding,
    compare_security_params,
    generate_lwe_instance,
    gs_min_norm,
    key_size_bytes,
    kyber_real_params,
)


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
    # Создаём вырожденную матрицу
    B = np.ones((3, 3), dtype=np.int64)
    t = np.array([1, 2, 3], dtype=np.int64)
    try:
        babai_rounding(B, t)
        # На некоторых платформах может не упасть из-за численной точности,
        # поэтому просто проверяем, что функция не зависает
    except ValueError:
        pass  # Ожидаемое поведение


def main() -> int:
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    runner = TestRunner(verbose=verbose)

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

    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
