#!/usr/bin/env python3
"""
LatticeGuard — нативное расширение (Gram-Schmidt).

Загружает скомпилированную shared library из native/gs_native.so.
Если .so не найден, автоматически падает обратно на чистый Python.

Сборка в Termux:
    bash native/build.sh

Или вручную:
    cd native
    clang -shared -o gs_native.so -fPIC -O3 gs_native.c -lm
"""

from __future__ import annotations

import ctypes
import os
import warnings
from pathlib import Path
from typing import Optional

import numpy as np

__all__ = ["gs_min_norm_native", "NATIVE_AVAILABLE"]

# Путь к shared library
NATIVE_DIR = Path(__file__).parent / "native"
SO_PATH = NATIVE_DIR / "gs_native.so"

_lib: Optional[ctypes.CDLL] = None
NATIVE_AVAILABLE = False


def _load_lib() -> Optional[ctypes.CDLL]:
    """Загружает нативную библиотеку, если она существует."""
    global NATIVE_AVAILABLE
    if not SO_PATH.exists():
        return None
    try:
        lib = ctypes.CDLL(str(SO_PATH))
        NATIVE_AVAILABLE = True
        return lib
    except OSError:
        return None


def _init():
    global _lib
    _lib = _load_lib()
    if _lib is None:
        warnings.warn(
            "Native extension not found. Run 'bash native/build.sh' to compile. "
            "Falling back to pure Python implementation.",
            RuntimeWarning,
            stacklevel=2,
        )


_init()


def gs_min_norm_native(B: np.ndarray) -> float:
    """
    Нативная реализация Gram-Schmidt с возвратом минимальной нормы.
    Работает с row-major матрицами (как NumPy по умолчанию).

    Parameters
    ----------
    B : ndarray shape (n, n)
        Базис решётки (столбцы — векторы).

    Returns
    -------
    float
        Минимальная норма среди ортогонализированных векторов.

    Raises
    ------
    RuntimeError
        Если нативное расширение не загружено.
    """
    if _lib is None:
        raise RuntimeError(
            "Native extension not available. "
            "Compile with: cd native && bash build.sh"
        )

    n = B.shape[1]
    if n > 64:
        raise ValueError("Native implementation supports n <= 64 only.")

    # Row-major copy (C-order), как в Python gs_min_norm
    B_copy = B.astype(np.float64).copy()
    norms = np.zeros(n, dtype=np.float64)

    _lib.gram_schmidt.argtypes = [
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
    ]
    _lib.gram_schmidt.restype = ctypes.c_double

    result = _lib.gram_schmidt(
        n,
        B_copy.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        norms.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
    )
    return float(result)


if __name__ == "__main__":
    import time
    from lattice import generate_lwe_instance, gs_min_norm

    print("Native extension test (Gram-Schmidt only)")
    print(f"NATIVE_AVAILABLE = {NATIVE_AVAILABLE}")

    if not NATIVE_AVAILABLE:
        print("Compile first: cd native && bash build.sh")
        exit(1)

    max_error = 0.0
    for n in [8, 16, 32, 64]:
        A, _, _, _ = generate_lwe_instance(n, 97, seed=42)

        t0 = time.perf_counter()
        r1 = gs_min_norm(A)
        t1 = time.perf_counter()

        t2 = time.perf_counter()
        r2 = gs_min_norm_native(A)
        t3 = time.perf_counter()

        err = abs(r1 - r2)
        max_error = max(max_error, err)
        match = err < 1e-12

        print(
            f"n={n:>2} | "
            f"Python: {r1:.4f} in {(t1-t0)*1000:>7.3f} ms | "
            f"Native: {r2:.4f} in {(t3-t2)*1000:>7.3f} ms | "
            f"Match: {match} | err={err:.2e}"
        )

    print(f"\nmax_abs_error(Python, C) = {max_error:.2e}")
    print(f"Numerical equivalence: {max_error < 1e-12}")
