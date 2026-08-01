#!/bin/bash
# LatticeGuard — скрипт установки для Termux

set -e

echo "[LatticeGuard] Установка зависимостей..."

# Обновление пакетов
pkg update -y

# Установка Python (если не установлен)
if ! command -v python &> /dev/null; then
    pkg install python -y
fi

# Установка NumPy
pip install numpy

echo "[LatticeGuard] Установка завершена!"
echo ""
echo "Запуск демо:"
echo "  python demo.py"
echo ""
echo "Запуск бенчмарка:"
echo "  python benchmark.py"
echo ""
echo "Интерактивный режим:"
echo "  python demo.py --interactive"
