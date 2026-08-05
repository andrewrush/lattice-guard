#ifndef BABAI_H
#define BABAI_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Babai rounding — нахождение ближайшего вектора решётки.
 * 
 * Параметры:
 *   basis:  базис решётки (n x n, row-major, double)
 *   target: целевой вектор (n-мерный, double)
 *   result: выходной вектор решётки (n-мерный, double)
 *   n:      размерность
 * 
 * Возвращает: 0 при успехе, -1 при ошибке (вырожденный базис или bad alloc)
 * 
 * Алгоритм:
 *   1. Модифицированный Gram-Schmidt (MGS) для получения ортогонального базиса
 *   2. Для i от n-1 до 0:
 *      c_i = <target, b_i*> / <b_i*, b_i*>
 *      target -= round(c_i) * basis[i]
 *   3. result = исходный target - модифицированный target
 */
int babai_rounding_c(
    const double *basis,
    const double *target,
    double *result,
    size_t n
);

/*
 * Быстрая версия с предвыделенной памятью для бенчмарков.
 * НЕ потокобезопасна! Вызывающий должен выделить:
 *   gs_workspace: n*n doubles
 *   mu_workspace: n*n doubles
 */
int babai_rounding_fast_c(
    const double *basis,
    const double *target,
    double *result,
    size_t n,
    double *gs_workspace,
    double *mu_workspace
);

#ifdef __cplusplus
}
#endif

#endif /* BABAI_H */
