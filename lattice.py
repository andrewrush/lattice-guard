"""
LatticeGuard — демо постквантовой криптографии на решётках.
Основано на прорыве Astra #7: polynomial-factor hardness of approximation for CVP.

Модуль содержит ядро проекта: генерация LWE-инстансов, эвристика Бабаи,
ортогонализация Грама-Шмидта, LLL-редукция и оценки параметров безопасности.
"""

from __future__ import annotations

import warnings
from typing import Tuple

from numpy.typing import NDArray
import numpy as np

__all__ = [
    "generate_lwe_instance",
    "babai_rounding",
    "gs_min_norm",
    "key_size_bytes",
    "key_size_module_lwe",
    "compare_security_params",
    "attack_complexity",
    "kyber_real_params",
    "lll_reduction",
    "compare_basis_quality",
    "_gram_schmidt_coeffs",
]


def generate_lwe_instance(
    n: int, q: int, seed: int | None = None
) -> Tuple[NDArray[np.int64], NDArray[np.int64], NDArray[np.int64], NDArray[np.int64]]:
    """
    Генерирует случайный LWE-инстанс (A, b = As + e mod q).

    Parameters
    ----------
    n : int
        Размерность решётки (должна быть > 0).
    q : int
        Модуль (должен быть > 1).
    seed : int, optional
        Seed для воспроизводимости.

    Returns
    -------
    A : ndarray shape (n, n)
        Публичная матрица.
    b : ndarray shape (n,)
        Публичный вектор.
    s : ndarray shape (n,)
        Секретный вектор.
    e : ndarray shape (n,)
        Малошумный вектор ошибки из {-1, 0, 1}.

    Raises
    ------
    ValueError
        Если n <= 0 или q <= 1.
    """
    if n <= 0:
        raise ValueError("Размерность n должна быть положительной.")
    if q <= 1:
        raise ValueError("Модуль q должен быть больше 1.")

    rng = np.random.default_rng(seed)
    A = rng.integers(0, q, size=(n, n), dtype=np.int64)
    s = rng.integers(0, q, size=n, dtype=np.int64)
    e = rng.integers(-1, 2, size=n, dtype=np.int64)  # ошибка из {-1, 0, 1}
    b = (A @ s + e) % q
    return A, b, s, e


def babai_rounding(B: NDArray[np.int64], t: NDArray[np.int64]) -> NDArray[np.int64]:
    """
    Алгоритм Бабаи (rounding) для приближённого решения CVP.

    На случайном базисе работает крайне плохо — это и демонстрирует
    вычислительную трудность CVP в реальных криптосистемах.

    Parameters
    ----------
    B : ndarray shape (n, n)
        Базис решётки (столбцы — векторы базиса).
    t : ndarray shape (n,)
        Целевой вектор.

    Returns
    -------
    v : ndarray shape (n,)
        Ближайший вектор решётки (приближённо).

    Raises
    ------
    ValueError
        Если B вырождена (det == 0).
    """
    B_float = B.astype(np.float64)
    t_float = t.astype(np.float64)

    # Проверка на вырожденность (численно)
    cond = np.linalg.cond(B_float)
    if cond > 1e12:
        warnings.warn(
            f"Базис плохо обусловлен (cond={cond:.2e}). "
            "Babai rounding может быть нестабильным.",
            RuntimeWarning,
            stacklevel=2,
        )

    try:
        coeffs = np.linalg.solve(B_float, t_float)
    except np.linalg.LinAlgError as exc:
        raise ValueError("Базис вырожден — решение невозможно.") from exc

    rounded = np.round(coeffs)
    v = (B_float @ rounded).astype(np.int64)
    return v


def gs_min_norm(B: NDArray[np.int64]) -> float:
    """
    Минимальная длина вектора Грама-Шмидта (оценка качества базиса).

    Использует модифицированный алгоритм Грама-Шмидта.
    Векторизованная реализация через NumPy для производительности.

    Parameters
    ----------
    B : ndarray shape (n, n)
        Базис решётки (столбцы — векторы).

    Returns
    -------
    float
        Минимальная норма среди ортогонализированных векторов.
    """
    n = B.shape[1]
    B_star = B.astype(np.float64).copy()
    norms = []

    for i in range(n):
        for j in range(i):
            mu = np.dot(B_star[:, i], B_star[:, j]) / np.dot(B_star[:, j], B_star[:, j])
            B_star[:, i] -= mu * B_star[:, j]
        norms.append(np.linalg.norm(B_star[:, i]))

    return float(min(norms))


def key_size_bytes(n: int, q: int) -> int:
    """
    Оценка размера публичного ключа в байтах для generic LWE (плотная матрица).

    Формула: n² · ⌈log₂(q)⌉ / 8
    Моделирует плотную n×n матрицу без сжатия.
    """
    bits_per_entry = int(np.ceil(np.log2(q)))
    return (n * n * bits_per_entry) // 8


def key_size_module_lwe(n: int, q: int, k: int = 2, d_u: int = 10) -> int:
    """
    Оценка размера публичного ключа для Module-LWE (ML-KEM-подобная схема).

    В отличие от generic LWE (плотная n×n матрица), Module-LWE:
    - Генерирует A из seed (32 байта вместо n² коэффициентов)
    - Использует полиномиальное кольцо ℤ_q[x]/(xⁿ+1)
    - Сжимает коэффициенты t-вектора до d_u бит

    Формула (упрощённая toy-модель):
        pk = seed_A + k · n · d_u / 8

    Параметры
    ----------
    n : int
        Размерность полиномиального кольца (степень xⁿ+1).
        В ML-KEM: n = 256 для всех уровней безопасности.
    q : int
        Модуль поля (например, 3329 для Kyber).
    k : int, default 2
        Ранг модуля. ML-KEM-512: k=2, ML-KEM-768: k=3, ML-KEM-1024: k=4.
    d_u : int, default 10
        Битовая точность сжатия t-вектора.
        ML-KEM-512/768: d_u=10, ML-KEM-1024: d_u=11.

    Returns
    -------
    int
        Размер публичного ключа в байтах (toy-оценка).

    Notes
    -----
    Это упрощённая модель. Реальный ML-KEM добавляет дополнительные
    байты для метаданных, поэтому реальные размеры (800/1184/1568 bytes)
    немного больше этой оценки. Главная цель — показать порядок
    величины: ~0.8 KB (Module-LWE) vs ~384 KB (generic LWE).
    """
    seed_bytes = 32  # SHA3-512 seed для детерминированной генерации A
    t_compressed = k * n * d_u // 8
    return seed_bytes + t_compressed


def compare_security_params(security_bits: int = 128) -> dict:
    """
    Сравнивает параметры криптосистемы до и после результатов Astra.

    Astra #7 утверждает полиномиальную трудность аппроксимации CVP.
    Это позволяет использовать меньшую размерность n (~на 25-40%)
    при сохранении того же security level.

    Parameters
    ----------
    security_bits : int, default 128
        Целевой уровень безопасности (128, 192 или 256).

    Returns
    -------
    dict
        Словарь с параметрами до и после Astra.

    Notes
    -----
    Коэффициент 0.25 в формуле boost — HEURISTIC PLACEHOLDER.
    Astra #7 сообщает о полиномиальной трудности CVP-аппроксимации,
    но конкретный фактор для криптографических параметров требует
    отдельного concrete-security анализа. Здесь boost моделируется
    как ~log₁₀(n) с эмпирическим коэффициентом 0.25 для наглядности
    в toy-модели. Это НЕ доказанная оценка для ML-KEM.
    """
    q = 3329  # модуль, как в Kyber

    if security_bits == 128:
        n_before = 512
    elif security_bits == 192:
        n_before = 768
    elif security_bits == 256:
        n_before = 1024
    else:
        n_before = security_bits * 4  # грубая эвристика

    # HEURISTIC: полиномиальная hardness даёт boost ~log(n).
    # Коэффициент 0.25 — placeholder для toy-модели.
    # См. Notes в docstring.
    boost = 1 + 0.25 * np.log10(n_before)
    n_after = int(n_before / boost)

    size_before = key_size_bytes(n_before, q)
    size_after = key_size_bytes(n_after, q)

    return {
        "security_bits": security_bits,
        "q": q,
        "n_before": n_before,
        "n_after": n_after,
        "key_before_kb": round(size_before / 1024, 1),
        "key_after_kb": round(size_after / 1024, 1),
        "saved_kb": round((size_before - size_after) / 1024, 1),
        "saved_percent": round((1 - size_after / size_before) * 100, 1),
    }


def attack_complexity(n: int, q: int = 3329) -> dict:
    """
    Оценка сложности известных атак на LWE.

    Классическая оценка (BKZ): ~ 2^(0.292 * n) операций.
    С учётом Astra: атакующий ограничен полиномиальным фактором
    при аппроксимации CVP, что эквивалентно +log(n) битам security.

    Parameters
    ----------
    n : int
        Размерность решётки.
    q : int, default 3329
        Модуль.

    Returns
    -------
    dict
        Словарь с оценками сложности.
    """
    classical = 0.292 * n
    astra_boost = np.log2(n) if n > 1 else 0
    return {
        "n": n,
        "classical_bits": round(classical, 1),
        "astra_effective_bits": round(classical + astra_boost, 1),
        "boost_bits": round(astra_boost, 1),
    }


def kyber_real_params() -> list[dict]:
    """
    Реальные параметры NIST-стандартизованного Kyber (ML-KEM).

    Returns
    -------
    list[dict]
        Параметры ML-KEM-512, ML-KEM-768, ML-KEM-1024.
    """
    return [
        {"name": "ML-KEM-512", "n": 512, "q": 3329, "eta": 3, "du": 10, "dv": 4, "pk_bytes": 800, "sk_bytes": 1632, "ct_bytes": 768},
        {"name": "ML-KEM-768", "n": 768, "q": 3329, "eta": 2, "du": 10, "dv": 4, "pk_bytes": 1184, "sk_bytes": 2400, "ct_bytes": 1088},
        {"name": "ML-KEM-1024", "n": 1024, "q": 3329, "eta": 2, "du": 11, "dv": 5, "pk_bytes": 1568, "sk_bytes": 3168, "ct_bytes": 1568},
    ]


def _gram_schmidt_coeffs(B: NDArray[np.int64]) -> tuple:
    """
    Модифицированный Грама-Шмидт с возвратом коэффициентов mu и норм.

    Returns
    -------
    mu : ndarray shape (n, n)
        Коэффициенты Грама-Шмидта mu[i,j] = <b_i, b_j*> / <b_j*, b_j*>.
    norms : ndarray shape (n,)
        Квадраты норм ||b_i*||².
    """
    n = B.shape[1]
    B_star = B.astype(np.float64).copy()
    mu = np.zeros((n, n), dtype=np.float64)
    norms = np.zeros(n, dtype=np.float64)

    for i in range(n):
        for j in range(i):
            mu[i, j] = np.dot(B_star[:, i], B_star[:, j]) / np.dot(B_star[:, j], B_star[:, j])
            B_star[:, i] -= mu[i, j] * B_star[:, j]
        norms[i] = np.dot(B_star[:, i], B_star[:, i])

    return mu, norms


def lll_reduction(B: NDArray[np.int64], delta: float = 0.75) -> NDArray[np.int64]:
    """
    Алгоритм LLL (Lenstra-Lenstra-Lovász) редукции решётки.

    Преобразует базис так, чтобы векторы были почти ортогональны
    и относительно коротки. Это делает эвристики типа Babai
    значительно более эффективными.

    Parameters
    ----------
    B : ndarray shape (n, n)
        Исходный базис (столбцы — векторы).
    delta : float, default 0.75
        Параметр Ловаса (0.25 < delta < 1). Стандартное значение 0.75.

    Returns
    -------
    B_reduced : ndarray shape (n, n)
        LLL-редуцированный базис.
    """
    if not (0.25 < delta < 1.0):
        raise ValueError("delta должен быть в диапазоне (0.25, 1.0)")

    n = B.shape[1]
    B_work = B.astype(np.float64).copy()

    k = 1
    while k < n:
        mu, norms = _gram_schmidt_coeffs(B_work)

        # Size reduction: уменьшаем коэффициенты mu[k,j]
        for j in range(k - 1, -1, -1):
            if abs(mu[k, j]) > 0.5:
                q = round(mu[k, j])
                B_work[:, k] -= q * B_work[:, j]
                # Пересчитываем GS после изменения
                mu, norms = _gram_schmidt_coeffs(B_work)

        # Lovász condition
        if norms[k] >= (delta - mu[k, k - 1] ** 2) * norms[k - 1]:
            k += 1
        else:
            # Swap b_k and b_{k-1}
            temp = B_work[:, k].copy()
            B_work[:, k] = B_work[:, k - 1]
            B_work[:, k - 1] = temp
            k = max(k - 1, 1)

    return np.rint(B_work).astype(np.int64)


def compare_basis_quality(A: NDArray[np.int64], s: NDArray[np.int64], e: NDArray[np.int64],
                          q: int = 97) -> dict:
    """
    Сравнивает качество разных типов базисов для атаки Babai.

    Parameters
    ----------
    A : ndarray shape (n, n)
        Публичная матрица (исходный "плохой" базис).
    s : ndarray shape (n,)
        Секрет.
    e : ndarray shape (n,)
        Ошибка.
    q : int, default 97
        Модуль.

    Returns
    -------
    dict
        Результаты для random и LLL базисов.
    """
    b = (A @ s + e) % q

    results = {}

    # Random basis (исходный)
    v = babai_rounding(A, b)
    v_mod = np.mod(v, q)
    matches = int(np.sum(v_mod == s))
    results["random"] = {
        "matches": matches,
        "match_percent": round(100 * matches / len(s), 1),
        "gs_min_norm": round(gs_min_norm(A), 2),
    }

    # LLL
    try:
        A_lll = lll_reduction(A)
        v = babai_rounding(A_lll, b)
        v_mod = np.mod(v, q)
        matches = int(np.sum(v_mod == s))
        results["lll"] = {
            "matches": matches,
            "match_percent": round(100 * matches / len(s), 1),
            "gs_min_norm": round(gs_min_norm(A_lll), 2),
        }
    except Exception as exc:
        results["lll"] = {"error": str(exc)}

    return results
