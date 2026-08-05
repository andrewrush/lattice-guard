#!/usr/bin/env python3
"""
Экспериментальные Python bindings для native/babai.c.

Если библиотека не скомпилирована, проект продолжает работать
на чистом Python без потери функциональности.

Сборка (опционально):
    cd native && bash build_babai.sh
"""

from __future__ import annotations

import ctypes
import os
import platform
import numpy as np
from numpy.typing import NDArray

_SYSTEM = platform.system()
if _SYSTEM == "Darwin":
    _LIB_NAME = "babai_native.dylib"
else:
    _LIB_NAME = "babai_native.so"

_LIB = None
_LIB_PATH = os.path.join(os.path.dirname(__file__), "native", _LIB_NAME)

try:
    if os.path.exists(_LIB_PATH):
        _LIB = ctypes.CDLL(_LIB_PATH)
        _LIB.babai_rounding_c.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
        ]
        _LIB.babai_rounding_c.restype = ctypes.c_int
        _LIB.babai_rounding_fast_c.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
        ]
        _LIB.babai_rounding_fast_c.restype = ctypes.c_int
except Exception:
    _LIB = None


def is_available() -> bool:
    """Проверяет, доступна ли нативная библиотека."""
    return _LIB is not None


def babai_rounding_native(
    basis: NDArray[np.float64],
    target: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Babai rounding через нативную C-библиотеку."""
    if not is_available():
        raise RuntimeError("Native babai library not available. Build: cd native && bash build_babai.sh")

    n = basis.shape[0]
    basis_c = np.ascontiguousarray(basis, dtype=np.float64)
    target_c = np.ascontiguousarray(target, dtype=np.float64)
    result_c = np.empty(n, dtype=np.float64)

    ret = _LIB.babai_rounding_c(
        basis_c.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        target_c.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        result_c.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        n,
    )
    if ret != 0:
        raise RuntimeError(f"babai_rounding_c failed: code {ret}")
    return result_c
