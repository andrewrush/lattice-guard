#!/bin/bash
# LatticeGuard — сборка нативного расширения
# Запускать из любой директории

set -e

# Переходим в директорию скрипта
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}[Native]${NC} Сборка gs_native.so..."

# Определяем компилятор
if command -v clang &> /dev/null; then
    CC=clang
    echo -e "${GREEN}[Native]${NC} Используется clang"
elif command -v gcc &> /dev/null; then
    CC=gcc
    echo -e "${GREEN}[Native]${NC} Используется gcc"
else
    echo -e "${RED}[Native]${NC} Ошибка: не найден clang или gcc"
    echo "Установите: pkg install clang"
    exit 1
fi

# Сборка
$CC -shared -o gs_native.so -fPIC -O3 gs_native.c -lm

if [ -f "gs_native.so" ]; then
    echo -e "${GREEN}[Native]${NC} Сборка успешна: gs_native.so"
    echo ""
    echo "Проверка:"
    echo "  python ../gs_native.py"
else
    echo -e "${RED}[Native]${NC} Ошибка сборки"
    exit 1
fi
