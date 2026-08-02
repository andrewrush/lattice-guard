#!/bin/bash
# LatticeGuard — скрипт установки для Termux
# Улучшенная версия с проверками и диагностикой

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}[LatticeGuard]${NC} Установка зависимостей..."

# Проверка, что мы в Termux (не обязательно, но полезно)
if [[ "$PREFIX" == *"com.termux"* ]]; then
    echo -e "${GREEN}[LatticeGuard]${NC} Обнаружен Termux ($PREFIX)"
else
    echo -e "${YELLOW}[LatticeGuard]${NC} Termux не обнаружен, продолжаем в обычном окружении..."
fi

# Обновление пакетов
echo -e "${GREEN}[LatticeGuard]${NC} Обновление списка пакетов..."
pkg update -y

# Проверка Python
if command -v python &> /dev/null; then
    PYTHON_VER=$(python --version 2>&1)
    echo -e "${GREEN}[LatticeGuard]${NC} Python найден: $PYTHON_VER"
else
    echo -e "${YELLOW}[LatticeGuard]${NC} Python не найден, устанавливаю..."
    pkg install python -y
fi

# Проверка pip
if ! command -v pip &> /dev/null; then
    echo -e "${YELLOW}[LatticeGuard]${NC} pip не найден, устанавливаю..."
    python -m ensurepip --upgrade || pkg install python-pip -y
fi

# Установка NumPy с проверкой
echo -e "${GREEN}[LatticeGuard]${NC} Установка NumPy..."
pip install --upgrade pip
pip install -r requirements.txt

# Проверка, что NumPy работает
echo -e "${GREEN}[LatticeGuard]${NC} Проверка NumPy..."
python -c "import numpy; print(f'NumPy {numpy.__version__} OK')" || {
    echo -e "${RED}[LatticeGuard]${NC} Ошибка: NumPy не работает. Попробуйте:"
    echo "  pkg install clang -y"
    echo "  pip install numpy --no-build-isolation"
    exit 1
}

# Проверка, что скрипты запускаются
echo -e "${GREEN}[LatticeGuard]${NC} Проверка импортов..."
python -c "from lattice import generate_lwe_instance, babai_rounding; print('Импорты OK')"

echo ""
echo -e "${GREEN}[LatticeGuard]${NC} Установка завершена успешно!"
echo ""
echo "Запуск демо:"
echo "  python demo.py"
echo ""
echo "Запуск бенчмарка:"
echo "  python benchmark.py"
echo ""
echo "Интерактивный режим:"
echo "  python demo.py --interactive"
echo ""
echo "Экспорт в JSON:"
echo "  python demo.py --json"
echo "  python benchmark.py --export results.json"
echo ""
echo "Запуск тестов:"
echo "  python test_lattice.py"
