/*
 * gs_native.c — нативная реализация модифицированного Грама-Шмидта.
 * Работает с row-major матрицами (как NumPy по умолчанию).
 *
 * Сборка в Termux:
 *   cd native && bash build.sh
 *
 * Parameters:
 *   n      — размерность (матрица n×n)
 *   B      — матрица базиса, row-major (C-style), shape (n, n)
 *            B[i*n + k] = элемент (i, k) = B[i, k] в NumPy
 *   norms  — выходной массив длины n
 *
 * Returns:
 *   минимальная норма среди всех векторов
 *
 * Note: B модифицируется in-place.
 */

#include <math.h>

/*
 * gram_schmidt — модифицированный алгоритм Грама-Шмидта.
 * Row-major layout: B[row*n + col] = B[row, col]
 * Столбец col: B[0*n + col], B[1*n + col], ..., B[(n-1)*n + col]
 */
double gram_schmidt(int n, double* B, double* norms) {
    int i, j, k;
    double mu, bj_norm, norm, min_norm;

    for (i = 0; i < n; i++) {
        for (j = 0; j < i; j++) {
            mu = 0.0;
            bj_norm = 0.0;
            for (k = 0; k < n; k++) {
                /* B[k*n + i] = элемент (k, i) — i-й столбец, k-я строка */
                mu += B[k*n + i] * B[k*n + j];
                bj_norm += B[k*n + j] * B[k*n + j];
            }
            if (bj_norm > 1e-15) {
                mu /= bj_norm;
            } else {
                mu = 0.0;
            }
            for (k = 0; k < n; k++) {
                B[k*n + i] -= mu * B[k*n + j];
            }
        }
        norm = 0.0;
        for (k = 0; k < n; k++) {
            norm += B[k*n + i] * B[k*n + i];
        }
        norms[i] = sqrt(norm);
    }

    min_norm = norms[0];
    for (i = 1; i < n; i++) {
        if (norms[i] < min_norm) {
            min_norm = norms[i];
        }
    }
    return min_norm;
}
