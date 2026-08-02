#!/usr/bin/env python3
"""
LatticeGuard — утилита экспорта результатов.
Запуск: python export.py
        python export.py --format csv
        python export.py --format json --out results.json

Полезна для сбора данных на телефоне и передачи на десктоп для анализа.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any

from lattice import (
    attack_complexity,
    compare_security_params,
    generate_lwe_instance,
    babai_rounding,
    gs_min_norm,
    kyber_real_params,
)


def export_security_json() -> dict[str, Any]:
    """Экспорт таблицы параметров безопасности."""
    return {
        "security_comparison": [compare_security_params(b) for b in (128, 192, 256)],
        "kyber_params": kyber_real_params(),
        "attack_complexity": [attack_complexity(n) for n in (128, 256, 512, 768, 1024)],
    }


def export_attack_samples(
    n_values: list[int] = None,
    q: int = 97,
    seeds: list[int] = None,
) -> list[dict[str, Any]]:
    """Экспорт результатов атаки для разных параметров."""
    if n_values is None:
        n_values = [8, 12, 16, 24, 32]
    if seeds is None:
        seeds = list(range(10))

    results = []
    for n in n_values:
        for seed in seeds:
            A, b, s, e = generate_lwe_instance(n, q, seed=seed)
            v = babai_rounding(A, b)
            v_mod = v % q
            matches = int((v_mod == s).sum())
            results.append({
                "n": n,
                "q": q,
                "seed": seed,
                "matches": matches,
                "match_percent": round(100 * matches / n, 1),
                "gs_min_norm": round(gs_min_norm(A), 2),
            })
    return results


def write_json(data: Any, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"JSON сохранён: {path}")


def write_csv_attack(data: list[dict], path: Path) -> None:
    if not data:
        print("Нет данных для экспорта.")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"CSV сохранён: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="LatticeGuard — экспорт результатов")
    parser.add_argument("--format", choices=["json", "csv"], default="json",
                        help="Формат экспорта")
    parser.add_argument("--out", default=None, help="Путь к выходному файлу")
    parser.add_argument("--samples", action="store_true",
                        help="Экспортировать сэмплы атаки (много данных)")
    args = parser.parse_args()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    default_name = f"lattice_guard_{timestamp}.{args.format}"
    out_path = Path(args.out) if args.out else Path(default_name)

    if args.samples:
        data = export_attack_samples()
        if args.format == "csv":
            write_csv_attack(data, out_path)
        else:
            write_json(data, out_path)
    else:
        data = {
            "meta": {
                "project": "LatticeGuard",
                "exported_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            **export_security_json(),
        }
        write_json(data, out_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
