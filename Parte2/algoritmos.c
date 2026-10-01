#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* ---------------- Versiones originales del lab ---------------- */

void funcion_a(int n) {
    int i, j, k, counter = 0;
    for (i = n/2; i <= n; i++) {
        for (j = 1; j+n/2 <= n; j++) {
            for (k = 1; k <= n; k = k*2) {
                counter++;
            }
        }
    }
}

void funcion_b(int n) {
    if (n <= 1) return;
    int i, j;
    for (i = 1; i <= n; i++) {
        for (j = 1; j <= n; j++) {
            printf("Sequence\n");
            break;
        }
    }
}

void funcion_c(int n) {
    int i, j;
    for (i = 1; i <= n/3; i++) {
        for (j = 1; j <= n; j += 4) {
            printf("Sequence\n");
        }
    }
}

/* ---------------- Versiones contadas (1 por linea ejecutada) ---------------- */

long long contar_a(int n) {
    long long ops = 0;
    int i, j, k, counter = 0;                 ops++;   /* linea 1 */
    for (i = n/2; ; i++) {
        ops++;                                          /* linea 2: verificacion i <= n */
        if (!(i <= n)) break;
        for (j = 1; ; j++) {
            ops++;                                      /* linea 3: verificacion j+n/2 <= n */
            if (!(j+n/2 <= n)) break;
            for (k = 1; ; k = k*2) {
                ops++;                                  /* linea 4: verificacion k <= n */
                if (!(k <= n)) break;
                counter++;                    ops++;   /* linea 5 */
            }
        }
    }
    (void)counter;
    return ops;
}

long long contar_b(int n) {
    long long ops = 0;
    ops++;                                              /* linea 1: if (n <= 1) return; */
    if (n <= 1) return ops;
    int i, j;                                 ops++;   /* linea 2 */
    (void)j;
    for (i = 1; ; i++) {
        ops++;                                          /* linea 3: verificacion i <= n */
        if (!(i <= n)) break;
        for (j = 1; ; j++) {
            ops++;                                      /* linea 4: verificacion j <= n */
            if (!(j <= n)) break;
            ops++;                                      /* linea 5: printf */
            ops++;                                      /* linea 6: break */
            break;
        }
    }
    return ops;
}

long long contar_c(int n) {
    long long ops = 0;
    int i, j;                                 ops++;   /* linea 1 */
    for (i = 1; ; i++) {
        ops++;                                          /* linea 2: verificacion i <= n/3 */
        if (!(i <= n/3)) break;
        for (j = 1; ; j += 4) {
            ops++;                                      /* linea 3: verificacion j <= n */
            if (!(j <= n)) break;
            ops++;                                      /* linea 4: printf */
        }
    }
    return ops;
}

/* ---------------- main ---------------- */

static double ahora(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr, "uso: %s tiempo <a|b|c> <n> <reps>  |  %s conteo <a|b|c> <n>\n",
                argv[0], argv[0]);
        return 1;
    }
    const char *modo = argv[1];
    char alg = argv[2][0];
    int n = atoi(argv[3]);

    if (strcmp(modo, "conteo") == 0) {
        long long ops = alg == 'a' ? contar_a(n) : alg == 'b' ? contar_b(n) : contar_c(n);
        printf("%lld\n", ops);
        return 0;
    }

    int reps = argc > 4 ? atoi(argv[4]) : 1;
    void (*f)(int) = alg == 'a' ? funcion_a : alg == 'b' ? funcion_b : funcion_c;

    double t0 = ahora();
    for (int r = 0; r < reps; r++) f(n);
    fflush(stdout);
    double t1 = ahora();

    fprintf(stderr, "%.9f\n", (t1 - t0) / reps);
    return 0;
}
