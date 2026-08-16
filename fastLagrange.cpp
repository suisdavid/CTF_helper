// Fast finite-field interpolation solver for encoded.txt.
//
// Ubuntu / Debian:
//   sudo apt install libgmp-dev
//   g++ -O3 -march=native -std=c++17 solver.cpp -lgmp -o solver
//   ./solver
//
// With no arguments, the program reads encoded.txt and writes
// recovered_flag.bmp. Optional usage: ./solver INPUT OUTPUT
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <string>
#include <utility>
#include <vector>

// Use the normal GMP development header when available. The small fallback
// declaration below is only for minimal Linux environments that ship libgmp
// without the development package.
#if __has_include(<gmp.h>)
#include <gmp.h>
#else
extern "C" {
typedef unsigned long mp_limb_t;
typedef struct {
    int _mp_alloc;
    int _mp_size;
    mp_limb_t *_mp_d;
} __mpz_struct;
typedef __mpz_struct mpz_t[1];

void __gmpz_init(mpz_t);
void __gmpz_clear(mpz_t);
void __gmpz_import(mpz_t, size_t, int, size_t, int, size_t, const void *);
void __gmpz_mul(mpz_t, const mpz_t, const mpz_t);
}
#endif

using u64 = uint64_t;
using u128 = unsigned __int128;
using Poly = std::vector<u64>;

static constexpr u64 MOD = 7514777789ULL;
static constexpr size_t EXPECTED_POINTS = 1769611;
static constexpr unsigned BLOCK_BITS = 88;
static constexpr size_t BASE_BLOCK = 16;
static constexpr size_t NAIVE_LIMIT = 1024;

static_assert(sizeof(mp_limb_t) == 8, "This solver requires 64-bit GMP limbs");

static inline u64 add_mod(u64 a, u64 b) {
    u64 s = a + b;
    return s >= MOD ? s - MOD : s;
}

static inline u64 mul_mod(u64 a, u64 b) {
    return static_cast<u64>(static_cast<u128>(a) * b % MOD);
}

static u64 pow_mod(u64 a, u64 e) {
    u64 r = 1;
    while (e) {
        if (e & 1) r = mul_mod(r, a);
        a = mul_mod(a, a);
        e >>= 1;
    }
    return r;
}

static Poly mul_naive(const Poly &a, const Poly &b) {
    if (a.empty() || b.empty()) return {};
    Poly c(a.size() + b.size() - 1);
    for (size_t k = 0; k < c.size(); ++k) {
        const size_t lo = k >= b.size() - 1 ? k - (b.size() - 1) : 0;
        const size_t hi = std::min(k, a.size() - 1);
        u128 acc = 0;
        for (size_t i = lo; i <= hi; ++i) {
            acc += static_cast<u128>(a[i]) * b[k - i];
        }
        c[k] = static_cast<u64>(acc % MOD);
    }
    return c;
}

static void import_packed(mpz_t z, const Poly &a) {
    const size_t limb_bits = 8 * sizeof(mp_limb_t);
    const size_t total_bits = a.size() * BLOCK_BITS;
    const size_t count = (total_bits + limb_bits - 1) / limb_bits;
    std::vector<mp_limb_t> limbs(count, 0);

    for (size_t i = 0; i < a.size(); ++i) {
        const size_t bit = i * BLOCK_BITS;
        const size_t q = bit / limb_bits;
        const unsigned s = static_cast<unsigned>(bit % limb_bits);
        limbs[q] |= static_cast<mp_limb_t>(a[i] << s);
        if (s && s + 33 > limb_bits) {
            limbs[q + 1] |= static_cast<mp_limb_t>(a[i] >> (limb_bits - s));
        }
    }
    __gmpz_import(z, count, -1, sizeof(mp_limb_t), 0, 0, limbs.data());
}

static Poly mul_packed(const Poly &a, const Poly &b) {
    if (a.empty() || b.empty()) return {};
    if (a.size() * b.size() <= NAIVE_LIMIT) return mul_naive(a, b);

    mpz_t A, B, C;
    __gmpz_init(A);
    __gmpz_init(B);
    __gmpz_init(C);
    import_packed(A, a);
    import_packed(B, b);
    __gmpz_mul(C, A, B);

    const size_t out_len = a.size() + b.size() - 1;
    const size_t limb_count = C[0]._mp_size < 0
        ? static_cast<size_t>(-C[0]._mp_size)
        : static_cast<size_t>(C[0]._mp_size);
    const mp_limb_t *limbs = C[0]._mp_d;
    const u128 mask = (static_cast<u128>(1) << BLOCK_BITS) - 1;
    Poly out(out_len);

    auto get_limb = [&](size_t i) -> u64 {
        return i < limb_count ? static_cast<u64>(limbs[i]) : 0;
    };

    for (size_t i = 0; i < out_len; ++i) {
        const size_t bit = i * BLOCK_BITS;
        const size_t q = bit / 64;
        const unsigned s = static_cast<unsigned>(bit % 64);
        const unsigned first = 64 - s;

        u128 v = static_cast<u128>(get_limb(q) >> s);
        if (first < BLOCK_BITS) {
            v |= static_cast<u128>(get_limb(q + 1)) << first;
        }
        if (first + 64 < BLOCK_BITS) {
            v |= static_cast<u128>(get_limb(q + 2)) << (first + 64);
        }
        v &= mask;
        out[i] = static_cast<u64>(v % MOD);
    }

    __gmpz_clear(A);
    __gmpz_clear(B);
    __gmpz_clear(C);
    return out;
}

struct Node {
    // M = product (X - x_i), N = sum w_i * product_{j != i} (X - x_j)
    Poly M;
    Poly N;
};

static Node make_base_block(size_t lo, size_t hi, const std::vector<u64> &w) {
    Poly M(1, 1);
    Poly N(1, 0);

    for (size_t i = lo; i < hi; ++i) {
        const u64 neg_i = i == 0 ? 0 : MOD - static_cast<u64>(i);
        Poly next_M(M.size() + 1, 0);
        Poly next_N(N.size() + 1, 0);

        for (size_t j = 0; j < M.size(); ++j) {
            next_M[j] = add_mod(next_M[j], mul_mod(neg_i, M[j]));
            next_M[j + 1] = add_mod(next_M[j + 1], M[j]);
            next_N[j] = add_mod(next_N[j], mul_mod(w[i], M[j]));
        }
        for (size_t j = 0; j < N.size(); ++j) {
            next_N[j] = add_mod(next_N[j], mul_mod(neg_i, N[j]));
            next_N[j + 1] = add_mod(next_N[j + 1], N[j]);
        }

        M = std::move(next_M);
        N = std::move(next_N);
    }
    return {std::move(M), std::move(N)};
}

static Node combine(Node &&left, Node &&right) {
    Poly M = mul_packed(left.M, right.M);
    Poly a = mul_packed(left.N, right.M);
    Poly b = mul_packed(left.M, right.N);
    if (a.size() < b.size()) a.resize(b.size());
    for (size_t i = 0; i < b.size(); ++i) a[i] = add_mod(a[i], b[i]);
    return {std::move(M), std::move(a)};
}

static u64 eval_poly(const Poly &p, u64 x) {
    u64 r = 0;
    for (size_t i = p.size(); i-- > 0;) r = add_mod(mul_mod(r, x), p[i]);
    return r;
}

static uint32_t read_le32(const Poly &p, size_t off) {
    return static_cast<uint32_t>(p[off])
        | (static_cast<uint32_t>(p[off + 1]) << 8)
        | (static_cast<uint32_t>(p[off + 2]) << 16)
        | (static_cast<uint32_t>(p[off + 3]) << 24);
}

int main(int argc, char **argv) {
    // With no arguments: encoded.txt -> recovered_flag.bmp
    // Optional usage: ./solver INPUT OUTPUT
    const char *input_path = argc > 1 ? argv[1] : "encoded.txt";
    const char *output_path = argc > 2 ? argv[2] : "recovered_flag.bmp";
    FILE *fin = std::fopen(input_path, "r");
    if (!fin) {
        std::perror(input_path);
        return 1;
    }

    std::vector<u64> ys;
    ys.reserve(1800000);
    unsigned long long x, y;
    size_t expected_x = 0;
    while (std::fscanf(fin, "%llu %llu", &x, &y) == 2) {
        if (x != expected_x) {
            std::fprintf(stderr, "non-consecutive x at row %zu: got %llu\n", expected_x, x);
            return 1;
        }
        ys.push_back(static_cast<u64>(y % MOD));
        ++expected_x;
    }
    std::fclose(fin);
    const size_t n = ys.size();
    if (n != EXPECTED_POINTS) {
        std::fprintf(stderr, "invalid point count: got %zu, expected %zu\n",
                     n, EXPECTED_POINTS);
        return 1;
    }
    std::fprintf(stderr, "read %zu consecutive points\n", n);

    std::vector<u64> fact(n), invfact(n), weights(n);
    fact[0] = 1;
    for (size_t i = 1; i < n; ++i) fact[i] = mul_mod(fact[i - 1], i);
    invfact[n - 1] = pow_mod(fact[n - 1], MOD - 2);
    for (size_t i = n - 1; i > 0; --i) invfact[i - 1] = mul_mod(invfact[i], i);
    for (size_t i = 0; i < n; ++i) {
        u64 wi = mul_mod(ys[i], mul_mod(invfact[i], invfact[n - 1 - i]));
        if ((n - 1 - i) & 1) wi = wi == 0 ? 0 : MOD - wi;
        weights[i] = wi;
    }

    const std::vector<std::pair<size_t, u64>> checks = {
        {0, ys[0]}, {1, ys[1]}, {2, ys[2]},
        {n / 2, ys[n / 2]}, {n - 1, ys[n - 1]}
    };
    ys.clear();
    ys.shrink_to_fit();
    fact.clear();
    fact.shrink_to_fit();
    invfact.clear();
    invfact.shrink_to_fit();

    std::vector<Node> level;
    level.reserve((n + BASE_BLOCK - 1) / BASE_BLOCK);
    for (size_t lo = 0; lo < n; lo += BASE_BLOCK) {
        level.push_back(make_base_block(lo, std::min(n, lo + BASE_BLOCK), weights));
    }
    weights.clear();
    weights.shrink_to_fit();
    std::fprintf(stderr, "built %zu base blocks\n", level.size());

    size_t round = 0;
    while (level.size() > 1) {
        std::vector<Node> next;
        next.reserve((level.size() + 1) / 2);
        for (size_t i = 0; i < level.size(); i += 2) {
            if (i + 1 == level.size()) next.push_back(std::move(level[i]));
            else next.push_back(combine(std::move(level[i]), std::move(level[i + 1])));
        }
        level = std::move(next);
        ++round;
        std::fprintf(stderr, "interpolation level %zu: %zu nodes\n", round, level.size());
    }

    Poly &coeff = level[0].N;
    if (coeff.size() < n) coeff.resize(n, 0);
    for (const auto &[xi, yi] : checks) {
        const u64 got = eval_poly(coeff, xi);
        if (got != yi) {
            std::fprintf(stderr, "verification failed at x=%zu: got %llu, expected %llu\n",
                         xi, static_cast<unsigned long long>(got),
                         static_cast<unsigned long long>(yi));
            return 1;
        }
    }
    std::fprintf(stderr, "polynomial verified at %zu sample points\n", checks.size());

    for (size_t i = 0; i + 1 < n; ++i) {
        if (coeff[i] > 255) {
            std::fprintf(stderr, "coefficient %zu is not a byte: %llu\n", i,
                         static_cast<unsigned long long>(coeff[i]));
            return 1;
        }
    }
    if (coeff[0] != 'B' || coeff[1] != 'M') {
        std::fprintf(stderr, "recovered data does not have BMP signature\n");
        return 1;
    }
    if (coeff[n - 1] != 0) {
        std::fprintf(stderr, "final coefficient is not the expected zero: %llu\n",
                     static_cast<unsigned long long>(coeff[n - 1]));
        return 1;
    }

    std::ofstream fout(output_path, std::ios::binary);
    for (size_t i = 0; i + 1 < n; ++i) fout.put(static_cast<char>(coeff[i]));
    fout.close();
    if (!fout) {
        std::fprintf(stderr, "failed writing %s\n", output_path);
        return 1;
    }

    std::fprintf(stderr, "BMP header: file_size=%u, pixel_offset=%u, width=%u, height=%u\n",
                 read_le32(coeff, 2), read_le32(coeff, 10),
                 read_le32(coeff, 18), read_le32(coeff, 22));
    std::fprintf(stderr, "wrote %zu bytes to %s; omitted final coefficient %llu\n",
                 n - 1, output_path,
                 static_cast<unsigned long long>(coeff[n - 1]));
    return 0;
}
