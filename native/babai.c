#include "babai.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

#define EPSILON 1e-12

/*
 * Babai coefficient rounding — решает B*c = t, округляет c,
 * возвращает B * round(c).
 * 
 * Это тот же алгоритм, что Python babai_rounding:
 *   coeffs = np.linalg.solve(B, t)
 *   rounded = np.round(coeffs)
 *   v = B @ rounded
 * 
 * Реализован через Gaussian elimination с частичным выбором главного элемента.
 */
int babai_rounding_c(
    const double *basis,
    const double *target,
    double *result,
    size_t n
) {
    if (!basis || !target || !result || n == 0) return -1;
    if (n > 256) return -1;

    /* Копируем basis и target для модификации */
    double *A = (double *)malloc(n * n * sizeof(double));
    double *b = (double *)malloc(n * sizeof(double));
    double *c = (double *)malloc(n * sizeof(double));

    if (!A || !b || !c) {
        free(A); free(b); free(c);
        return -1;
    }

    memcpy(A, basis, n * n * sizeof(double));
    memcpy(b, target, n * sizeof(double));

    /* Gaussian elimination with partial pivoting */
    for (size_t col = 0; col < n; col++) {
        /* Find pivot row */
        size_t pivot = col;
        double max_val = fabs(A[col * n + col]);
        for (size_t row = col + 1; row < n; row++) {
            if (fabs(A[row * n + col]) > max_val) {
                max_val = fabs(A[row * n + col]);
                pivot = row;
            }
        }
        if (max_val < EPSILON) {
            free(A); free(b); free(c);
            return -1; /* Singular matrix */
        }

        /* Swap rows */
        if (pivot != col) {
            for (size_t j = 0; j < n; j++) {
                double tmp = A[col * n + j];
                A[col * n + j] = A[pivot * n + j];
                A[pivot * n + j] = tmp;
            }
            double tmp = b[col];
            b[col] = b[pivot];
            b[pivot] = tmp;
        }

        /* Eliminate below */
        for (size_t row = col + 1; row < n; row++) {
            double factor = A[row * n + col] / A[col * n + col];
            for (size_t j = col; j < n; j++) {
                A[row * n + j] -= factor * A[col * n + j];
            }
            b[row] -= factor * b[col];
        }
    }

    /* Back substitution */
    for (int i = (int)n - 1; i >= 0; i--) {
        c[i] = b[i];
        for (size_t j = i + 1; j < n; j++) {
            c[i] -= A[i * n + j] * c[j];
        }
        c[i] /= A[i * n + i];
    }

    /* Round coefficients and compute result = basis @ round(c) */
    for (size_t i = 0; i < n; i++) {
        result[i] = 0.0;
        for (size_t j = 0; j < n; j++) {
            result[i] += basis[i * n + j] * round(c[j]);
        }
    }

    free(A); free(b); free(c);
    return 0;
}

/*
 * Быстрая версия с предвыделенной памятью для бенчмарков.
 * НЕ потокобезопасна! Вызывающий должен выделить:
 *   workspace: n*n + n + n doubles (достаточно n*n + 2*n)
 */
int babai_rounding_fast_c(
    const double *basis,
    const double *target,
    double *result,
    size_t n,
    double *workspace,
    double *workspace2
) {
    if (!basis || !target || !result || !workspace || !workspace2 || n == 0) return -1;
    if (n > 256) return -1;

    double *A = workspace;
    double *b = workspace2;
    double *c = workspace2 + n;

    memcpy(A, basis, n * n * sizeof(double));
    memcpy(b, target, n * sizeof(double));

    for (size_t col = 0; col < n; col++) {
        size_t pivot = col;
        double max_val = fabs(A[col * n + col]);
        for (size_t row = col + 1; row < n; row++) {
            if (fabs(A[row * n + col]) > max_val) {
                max_val = fabs(A[row * n + col]);
                pivot = row;
            }
        }
        if (max_val < EPSILON) return -1;

        if (pivot != col) {
            for (size_t j = 0; j < n; j++) {
                double tmp = A[col * n + j];
                A[col * n + j] = A[pivot * n + j];
                A[pivot * n + j] = tmp;
            }
            double tmp = b[col];
            b[col] = b[pivot];
            b[pivot] = tmp;
        }

        for (size_t row = col + 1; row < n; row++) {
            double factor = A[row * n + col] / A[col * n + col];
            for (size_t j = col; j < n; j++) {
                A[row * n + j] -= factor * A[col * n + j];
            }
            b[row] -= factor * b[col];
        }
    }

    for (int i = (int)n - 1; i >= 0; i--) {
        c[i] = b[i];
        for (size_t j = i + 1; j < n; j++) {
            c[i] -= A[i * n + j] * c[j];
        }
        c[i] /= A[i * n + i];
    }

    for (size_t i = 0; i < n; i++) {
        result[i] = 0.0;
        for (size_t j = 0; j < n; j++) {
            result[i] += basis[i * n + j] * round(c[j]);
        }
    }

    return 0;
}
