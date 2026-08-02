#!/usr/bin/env python3
"""
LatticeGuard — интерактивное демо.
Запуск: python demo.py
        python demo.py --interactive
        python demo.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

import numpy as np

from lattice import (
    attack_complexity,
    babai_rounding,
    compare_security_params,
    generate_lwe_instance,
    gs_min_norm,
    kyber_real_params,
)


def print_header() -> None:
    print("=" * 62)
    print("  LatticeGuard — демо постквантовой криптографии")
    print("  Основано на прорыве Astra #7 (CVP hardness)")
    print("=" * 62)


def demo_security_comparison() -> list[dict[str, Any]]:
    print("\n--- Сравнение параметров безопасности ---")
    print(
        f"{'Level':>8} | {'n до':>6} | {'n после':>7} | "
        f"{'Ключ до':>9} | {'Ключ после':>10} | {'Экономия':>8}"
    )
    print("-" * 62)
    results = []
    for bits in (128, 192, 256):
        r = compare_security_params(bits)
        results.append(r)
        print(
            f"{r['security_bits']:>6}-bit | "
            f"{r['n_before']:>6} | "
            f"{r['n_after']:>7} | "
            f"{r['key_before_kb']:>7.1f} KB | "
            f"{r['key_after_kb']:>8.1f} KB | "
            f"{r['saved_percent']:>6.1f}%"
        )
    return results


def demo_kyber_comparison() -> list[dict[str, Any]]:
    print("\n--- Реальные параметры NIST Kyber (ML-KEM) ---")
    print(
        f"{'Scheme':>12} | {'n':>5} | {'q':>5} | "
        f"{'pk (bytes)':>10} | {'sk (bytes)':>10} | {'ct (bytes)':>10}"
    )
    print("-" * 62)
    params = kyber_real_params()
    for p in params:
        print(
            f"{p['name']:>12} | "
            f"{p['n']:>5} | "
            f"{p['q']:>5} | "
            f"{p['pk_bytes']:>10} | "
            f"{p['sk_bytes']:>10} | "
            f"{p['ct_bytes']:>10}"
        )
    print("\nЭто реальные цифры из NIST FIPS 203.")
    print("Astra #7 позволяет теоретически снизить n на 25-40% при той же security.")
    return params


def demo_cvp_attack(n: int = 24, q: int = 97, seed: int = 42) -> dict[str, Any]:
    print(f"\n--- Демо: атака на LWE через CVP (Babai rounding) ---")
    print(f"Параметры: n={n}, q={q}, seed={seed}")

    A, b, s, e = generate_lwe_instance(n, q, seed=seed)

    print(f"Секрет s (первые 8): {s[:8]}")
    print(f"Ошибка e (первые 8): {e[:8]}")

    start = time.perf_counter()
    v = babai_rounding(A, b)
    elapsed_ms = (time.perf_counter() - start) * 1000

    v_mod = np.mod(v, q)
    matches = int(np.sum(v_mod == s))

    print(f"\nBabai rounding завершён за {elapsed_ms:.2f} мс")
    print(f"Восстановлено (первые 8): {v_mod[:8]}")
    print(f"Совпадений с секретом: {matches}/{n} ({100*matches/n:.0f}%)")

    if matches < n:
        print(f"=> При n={n} атака НЕ удалась полностью.")
        print("=> При n=512 (реальная криптография) — невозможна за разумное время.")

    min_norm = gs_min_norm(A)
    print(f"\nМин. норма GS-ортогонализации: {min_norm:.2f}")
    print("(На случайном базисе норма велика — атака обречена на провал)")

    return {
        "n": n,
        "q": q,
        "seed": seed,
        "time_ms": round(elapsed_ms, 2),
        "matches": matches,
        "match_percent": round(100 * matches / n, 1),
        "gs_min_norm": round(min_norm, 2),
        "secret_first8": s[:8].tolist(),
        "error_first8": e[:8].tolist(),
        "recovered_first8": v_mod[:8].tolist(),
    }


def demo_attack_complexity() -> list[dict[str, Any]]:
    print("\n--- Оценка сложности атаки BKZ ---")
    print(f"{'n':>5} | {'Классика (бит)':>16} | {'С Astra (бит)':>14} | {'Буст':>6}")
    print("-" * 52)
    results = []
    for n in (128, 256, 512, 768, 1024):
        c = attack_complexity(n)
        results.append(c)
        print(
            f"{c['n']:>5} | "
            f"{c['classical_bits']:>16.1f} | "
            f"{c['astra_effective_bits']:>14.1f} | "
            f"+{c['boost_bits']:>4.1f}"
        )
    print("\nAstra #7: полиномиальная трудность CVP-аппроксимации")
    print("даёт дополнительные ~log₂(n) бит security без увеличения ключа.")
    return results


def interactive_mode() -> dict[str, Any]:
    print("\n--- Интерактивный режим ---")
    try:
        n_in = input("Размерность n (рекомендуется 8-64): ").strip()
        n = int(n_in) if n_in else 24
        if n < 4:
            print("⚠️ n слишком мало для наглядности, использую n=8")
            n = 8
        if n > 512:
            print("⚠️ n > 512 — это может занять много времени на телефоне, продолжаю...")

        q_in = input("Модуль q (рекомендуется простое, например 97): ").strip()
        q = int(q_in) if q_in else 97

        seed_in = input("Seed (Enter для случайного): ").strip()
        seed = int(seed_in) if seed_in else None
    except (ValueError, EOFError):
        print("Неверный ввод, использую значения по умолчанию.")
        n, q, seed = 24, 97, 42

    return demo_cvp_attack(n, q, seed)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LatticeGuard — демо постквантовой криптографии",
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Интерактивный режим"
    )
    parser.add_argument(
        "--json", action="store_true", help="Вывести результаты в JSON (полезно для piping)"
    )
    args = parser.parse_args()

    results: dict[str, Any] = {
        "meta": {
            "project": "LatticeGuard",
            "based_on": "Astra #7",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    }

    print_header()
    results["security_comparison"] = demo_security_comparison()
    results["kyber_params"] = demo_kyber_comparison()
    results["cvp_attack"] = demo_cvp_attack()
    results["attack_complexity"] = demo_attack_complexity()

    if args.interactive:
        results["interactive"] = interactive_mode()

    print("\n" + "=" * 62)
    print("  Демо завершено. Все вычисления выполнены локально.")
    print("  Запустите с флагом --interactive для интерактивного режима.")
    print("=" * 62)

    if args.json:
        # JSON выводим в stderr, чтобы не мешать основному stdout (если piping)
        print("\n--- JSON Output ---", file=sys.stderr)
        print(json.dumps(results, indent=2, ensure_ascii=False), file=sys.stderr)


if __name__ == "__main__":
    main()
