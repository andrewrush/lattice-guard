#include "babai.h"
#include <math.h>
#include <string.h>
#include <stdlib.h>

#define EPSILON 1e-12

static inline double dot(const double *a, const double *b, size_t n) {
    double s = 0.0;
    for (size_t i = 0; i < n; i++) s += a[i] * b[i];
    return s;
}

static inline void vec_sub(double *out, const double *a, const double *b, size_t n) {
    for (size_t i = 0; i < n; i++) out[i] = a[i] - b[i];
}

static inline void vec_scale_sub(double *out, const double *a, double scale, const double *b, size_t n) {
    for (size_t i = 0; i < n; i++) out[i] = a[i] - scale * b[i];
}

/* Модифицированный Gram-Schmidt (row-major) */
static int mgs(const double *basis, double *gs, double *mu, size_t n) {
    if (!basis || !gs || !mu || n == 0) return -1;
    memset(mu, 0, n * n * sizeof(double));

    for (size_t i = 0; i < n; i++) {
        memcpy(&gs[i * n], &basis[i * n], n * sizeof(double));
        for (size_t j = 0; j < i; j++) {
            double num = dot(&basis[i * n], &gs[j * n], n);
            double den = dot(&gs[j * n], &gs[j * n], n);
            if (fabs(den) < EPSILON) return -1;
            mu[i * n + j] = num / den;
            for (size_t k = 0; k < n; k++)
                gs[i * n + k] -= mu[i * n + j] * gs[j * n + k];
        }
        if (dot(&gs[i * n], &gs[i * n], n) < EPSILON) return -1;
    }
    return 0;
}

int babai_rounding_c(
    const double *basis,
    const double *target,
    double *result,
    size_t n
) {
    if (!basis || !target || !result || n == 0) return -1;
    if (n > 256) return -1;  /* safety limit for educational demo */

    double *gs = (double *)malloc(n * n * sizeof(double));
    double *mu = (double *)malloc(n * n * sizeof(double));
    double *work = (double *)malloc(n * sizeof(double));
    double *current = (double *)malloc(n * sizeof(double));

    if (!gs || !mu || !work || !current) {
        free(gs); free(mu); free(work); free(current);
        return -1;
    }

    if (mgs(basis, gs, mu, n) != 0) {
        free(gs); free(mu); free(work); free(current);
        return -1;
    }

    memcpy(current, target, n * sizeof(double));

    for (int i = (int)n - 1; i >= 0; i--) {
        double num = dot(current, &gs[i * n], n);
        double den = dot(&gs[i * n], &gs[i * n], n);
        if (fabs(den) < EPSILON) {
            free(gs); free(mu); free(work); free(current);
            return -1;
        }
        double c = num / den;
        long rounded = (long)round(c);
        vec_scale_sub(current, current, (double)rounded, &basis[i * n], n);
    }

    vec_sub(result, target, current, n);

    free(gs); free(mu); free(work); free(current);
    return 0;
}

int babai_rounding_fast_c(
    const double *basis,
    const double *target,
    double *result,
    size_t n,
    double *gs_workspace,
    double *mu_workspace
) {
    if (!basis || !target || !result || !gs_workspace || !mu_workspace || n == 0) return -1;
    if (n > 256) return -1;

    double *work = (double *)malloc(n * sizeof(double));
    double *current = (double *)malloc(n * sizeof(double));
    if (!work || !current) {
        free(work); free(current);
        return -1;
    }

    if (mgs(basis, gs_workspace, mu_workspace, n) != 0) {
        free(work); free(current);
        return -1;
    }

    memcpy(current, target, n * sizeof(double));

    for (int i = (int)n - 1; i >= 0; i--) {
        double num = dot(current, &gs_workspace[i * n], n);
        double den = dot(&gs_workspace[i * n], &gs_workspace[i * n], n);
        if (fabs(den) < EPSILON) {
            free(work); free(current);
            return -1;
        }
        double c = num / den;
        long rounded = (long)round(c);
        vec_scale_sub(current, current, (double)rounded, &basis[i * n], n);
    }

    vec_sub(result, target, current, n);

    free(work); free(current);
    return 0;
}
