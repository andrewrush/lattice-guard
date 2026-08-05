#!/bin/bash
# Сборка native/babai.c для Termux/Linux/macOS
# Экспериментальная оптимизация Babai rounding (необязательная)

set -e

echo "=== Building babai native library (experimental) ==="

OS="$(uname -s)"
ARCH="$(uname -m)"
echo "OS: $OS | Arch: $ARCH"

if command -v clang &> /dev/null; then
    CC="clang"
elif command -v gcc &> /dev/null; then
    CC="gcc"
else
    echo "Error: No C compiler found"
    exit 1
fi

CFLAGS="-O3 -Wall -Wextra -fPIC"

if [ "$OS" = "Darwin" ]; then
    OUT="libbabai.dylib"
    LDFLAGS="-dynamiclib"
else
    OUT="libbabai.so"
    LDFLAGS="-shared"
fi

cd "$(dirname "$0")"
$CC $CFLAGS -c babai.c -o babai.o
$CC $LDFLAGS -o $OUT babai.o -lm
rm -f babai.o

echo "=== Built: native/$OUT ==="
echo "Optional. Project works fine without it."
