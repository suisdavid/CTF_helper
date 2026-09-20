#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#if defined(__x86_64__) || defined(_M_X64) || defined(__i386) || defined(_M_IX86)
#include <immintrin.h>
#include <x86intrin.h>
#define HAS_RDTSC 1
#else
#define HAS_RDTSC 0
#endif

namespace {

using Block = std::array<uint8_t, 16>;

constexpr std::array<uint8_t, 256> SBOX = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b,
    0xfe, 0xd7, 0xab, 0x76, 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,
    0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 0xb7, 0xfd, 0x93, 0x26,
    0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2,
    0xeb, 0x27, 0xb2, 0x75, 0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0,
    0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84, 0x53, 0xd1, 0x00, 0xed,
    0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f,
    0x50, 0x3c, 0x9f, 0xa8, 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5,
    0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 0xcd, 0x0c, 0x13, 0xec,
    0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14,
    0xde, 0x5e, 0x0b, 0xdb, 0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c,
    0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79, 0xe7, 0xc8, 0x37, 0x6d,
    0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f,
    0x4b, 0xbd, 0x8b, 0x8a, 0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e,
    0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e, 0xe1, 0xf8, 0x98, 0x11,
    0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f,
    0xb0, 0x54, 0xbb, 0x16};

constexpr std::array<uint8_t, 10> RCON = {
    0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36};

std::array<uint8_t, 256> INV_SBOX{};
alignas(64) uint32_t TE0[256];
alignas(64) uint32_t TE1[256];
alignas(64) uint32_t TE2[256];
alignas(64) uint32_t TE3[256];

uint8_t xtime(uint8_t x) {
    return static_cast<uint8_t>((x << 1) ^ ((x & 0x80) ? 0x1b : 0x00));
}

uint32_t load_be32(const uint8_t *p) {
    return (static_cast<uint32_t>(p[0]) << 24) |
           (static_cast<uint32_t>(p[1]) << 16) |
           (static_cast<uint32_t>(p[2]) << 8) |
           static_cast<uint32_t>(p[3]);
}

void store_be32(uint32_t x, uint8_t *p) {
    p[0] = static_cast<uint8_t>(x >> 24);
    p[1] = static_cast<uint8_t>(x >> 16);
    p[2] = static_cast<uint8_t>(x >> 8);
    p[3] = static_cast<uint8_t>(x);
}

uint32_t sub_word(uint32_t w) {
    return (static_cast<uint32_t>(SBOX[(w >> 24) & 0xff]) << 24) |
           (static_cast<uint32_t>(SBOX[(w >> 16) & 0xff]) << 16) |
           (static_cast<uint32_t>(SBOX[(w >> 8) & 0xff]) << 8) |
           static_cast<uint32_t>(SBOX[w & 0xff]);
}

uint32_t rot_word(uint32_t w) {
    return (w << 8) | (w >> 24);
}

std::string hex_encode(const Block &block) {
    std::ostringstream oss;
    oss << std::hex << std::setfill('0');
    for (uint8_t b : block) {
        oss << std::setw(2) << static_cast<int>(b);
    }
    return oss.str();
}

Block parse_hex_block(const std::string &hex) {
    if (hex.size() != 32) {
        throw std::runtime_error("AES-128 key must be exactly 32 hex characters");
    }
    Block out{};
    for (size_t i = 0; i < out.size(); ++i) {
        const std::string byte = hex.substr(2 * i, 2);
        char *end = nullptr;
        const long value = std::strtol(byte.c_str(), &end, 16);
        if (*end != '\0' || value < 0 || value > 255) {
            throw std::runtime_error("invalid hex byte in key");
        }
        out[i] = static_cast<uint8_t>(value);
    }
    return out;
}

void build_tables() {
    static bool built = false;
    if (built) {
        return;
    }
    for (size_t i = 0; i < 256; ++i) {
        INV_SBOX[SBOX[i]] = static_cast<uint8_t>(i);
        const uint8_t s = SBOX[i];
        const uint8_t s2 = xtime(s);
        const uint8_t s3 = static_cast<uint8_t>(s2 ^ s);
        TE0[i] = (static_cast<uint32_t>(s2) << 24) |
                 (static_cast<uint32_t>(s) << 16) |
                 (static_cast<uint32_t>(s) << 8) |
                 static_cast<uint32_t>(s3);
        TE1[i] = (static_cast<uint32_t>(s3) << 24) |
                 (static_cast<uint32_t>(s2) << 16) |
                 (static_cast<uint32_t>(s) << 8) |
                 static_cast<uint32_t>(s);
        TE2[i] = (static_cast<uint32_t>(s) << 24) |
                 (static_cast<uint32_t>(s3) << 16) |
                 (static_cast<uint32_t>(s2) << 8) |
                 static_cast<uint32_t>(s);
        TE3[i] = (static_cast<uint32_t>(s) << 24) |
                 (static_cast<uint32_t>(s) << 16) |
                 (static_cast<uint32_t>(s3) << 8) |
                 static_cast<uint32_t>(s2);
    }
    built = true;
}

class AES128 {
public:
    explicit AES128(const Block &key) {
        build_tables();
        expand_key(key);
    }

    __attribute__((noinline)) Block encrypt(const Block &input) const {
        uint32_t s0 = load_be32(input.data() + 0) ^ round_keys_[0];
        uint32_t s1 = load_be32(input.data() + 4) ^ round_keys_[1];
        uint32_t s2 = load_be32(input.data() + 8) ^ round_keys_[2];
        uint32_t s3 = load_be32(input.data() + 12) ^ round_keys_[3];

        for (int round = 1; round < 10; ++round) {
            const uint32_t t0 =
                TE0[(s0 >> 24) & 0xff] ^
                TE1[(s1 >> 16) & 0xff] ^
                TE2[(s2 >> 8) & 0xff] ^
                TE3[s3 & 0xff] ^
                round_keys_[4 * round + 0];
            const uint32_t t1 =
                TE0[(s1 >> 24) & 0xff] ^
                TE1[(s2 >> 16) & 0xff] ^
                TE2[(s3 >> 8) & 0xff] ^
                TE3[s0 & 0xff] ^
                round_keys_[4 * round + 1];
            const uint32_t t2 =
                TE0[(s2 >> 24) & 0xff] ^
                TE1[(s3 >> 16) & 0xff] ^
                TE2[(s0 >> 8) & 0xff] ^
                TE3[s1 & 0xff] ^
                round_keys_[4 * round + 2];
            const uint32_t t3 =
                TE0[(s3 >> 24) & 0xff] ^
                TE1[(s0 >> 16) & 0xff] ^
                TE2[(s1 >> 8) & 0xff] ^
                TE3[s2 & 0xff] ^
                round_keys_[4 * round + 3];
            s0 = t0;
            s1 = t1;
            s2 = t2;
            s3 = t3;
        }

        Block output{};
        const uint32_t rk0 = round_keys_[40];
        const uint32_t rk1 = round_keys_[41];
        const uint32_t rk2 = round_keys_[42];
        const uint32_t rk3 = round_keys_[43];

        const uint32_t o0 =
            (static_cast<uint32_t>(SBOX[(s0 >> 24) & 0xff]) << 24) ^
            (static_cast<uint32_t>(SBOX[(s1 >> 16) & 0xff]) << 16) ^
            (static_cast<uint32_t>(SBOX[(s2 >> 8) & 0xff]) << 8) ^
            static_cast<uint32_t>(SBOX[s3 & 0xff]) ^
            rk0;
        const uint32_t o1 =
            (static_cast<uint32_t>(SBOX[(s1 >> 24) & 0xff]) << 24) ^
            (static_cast<uint32_t>(SBOX[(s2 >> 16) & 0xff]) << 16) ^
            (static_cast<uint32_t>(SBOX[(s3 >> 8) & 0xff]) << 8) ^
            static_cast<uint32_t>(SBOX[s0 & 0xff]) ^
            rk1;
        const uint32_t o2 =
            (static_cast<uint32_t>(SBOX[(s2 >> 24) & 0xff]) << 24) ^
            (static_cast<uint32_t>(SBOX[(s3 >> 16) & 0xff]) << 16) ^
            (static_cast<uint32_t>(SBOX[(s0 >> 8) & 0xff]) << 8) ^
            static_cast<uint32_t>(SBOX[s1 & 0xff]) ^
            rk2;
        const uint32_t o3 =
            (static_cast<uint32_t>(SBOX[(s3 >> 24) & 0xff]) << 24) ^
            (static_cast<uint32_t>(SBOX[(s0 >> 16) & 0xff]) << 16) ^
            (static_cast<uint32_t>(SBOX[(s1 >> 8) & 0xff]) << 8) ^
            static_cast<uint32_t>(SBOX[s2 & 0xff]) ^
            rk3;

        store_be32(o0, output.data() + 0);
        store_be32(o1, output.data() + 4);
        store_be32(o2, output.data() + 8);
        store_be32(o3, output.data() + 12);
        return output;
    }

    Block round10_key() const {
        Block out{};
        for (int i = 0; i < 4; ++i) {
            store_be32(round_keys_[40 + i], out.data() + 4 * i);
        }
        return out;
    }

private:
    void expand_key(const Block &key) {
        for (int i = 0; i < 4; ++i) {
            round_keys_[i] = load_be32(key.data() + 4 * i);
        }
        for (int i = 4; i < 44; ++i) {
            uint32_t temp = round_keys_[i - 1];
            if (i % 4 == 0) {
                temp = sub_word(rot_word(temp)) ^
                       (static_cast<uint32_t>(RCON[(i / 4) - 1]) << 24);
            }
            round_keys_[i] = round_keys_[i - 4] ^ temp;
        }
    }

    std::array<uint32_t, 44> round_keys_{};
};

uint64_t now_ns() {
    return static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(
            std::chrono::steady_clock::now().time_since_epoch())
            .count());
}

uint64_t rdtsc_begin() {
#if HAS_RDTSC
    _mm_lfence();
    const uint64_t t = __rdtsc();
    _mm_lfence();
    return t;
#else
    return 0;
#endif
}

uint64_t rdtsc_end() {
#if HAS_RDTSC
    unsigned int aux = 0;
    const uint64_t t = __rdtscp(&aux);
    _mm_lfence();
    return t;
#else
    return 0;
#endif
}

Block random_block(std::mt19937_64 &rng) {
    Block block{};
    for (size_t i = 0; i < block.size(); i += 8) {
        const uint64_t x = rng();
        for (size_t j = 0; j < 8; ++j) {
            block[i + j] = static_cast<uint8_t>(x >> (8 * j));
        }
    }
    return block;
}

volatile uint8_t cache_sink = 0;

void evict_cache(std::vector<uint8_t> &buffer) {
    uint8_t acc = 0;
    for (size_t i = 0; i < buffer.size(); i += 64) {
        acc ^= buffer[i];
        buffer[i] = static_cast<uint8_t>(buffer[i] + 1);
    }
    cache_sink ^= acc;
}

std::array<double, 16> simulated_sbox_probe_times(
    const Block &ciphertext,
    const Block &round10_key,
    std::mt19937_64 &rng) {
    constexpr size_t kCacheLines = 16;
    constexpr size_t kSboxBytesPerLine = 16;

    std::array<bool, kCacheLines> touched{};
    for (size_t i = 0; i < ciphertext.size(); ++i) {
        const uint8_t sbox_input = INV_SBOX[ciphertext[i] ^ round10_key[i]];
        touched[sbox_input / kSboxBytesPerLine] = true;
    }

    std::normal_distribution<double> hit_time(55.0, 7.0);
    std::normal_distribution<double> miss_time(190.0, 14.0);
    std::array<double, kCacheLines> timings{};
    for (size_t line = 0; line < kCacheLines; ++line) {
        timings[line] = touched[line] ? hit_time(rng) : miss_time(rng);
    }
    return timings;
}

void usage(const char *argv0) {
    std::cerr
        << "Usage: " << argv0 << " [options]\n"
        << "Options:\n"
        << "  --samples N          number of random plaintext blocks, default 20000\n"
        << "  --output FILE        CSV output path, default output.csv\n"
        << "  --seed N             deterministic RNG seed\n"
        << "  --key-hex HEX        fixed AES-128 key, 32 hex chars\n"
        << "  --write-key FILE     write the experiment key to a separate file\n"
        << "  --warmup N           warm-up encryptions before measurement, default 1000\n"
        << "  --no-evict           skip cache eviction before each measured encryption\n";
}

struct Config {
    size_t samples = 20000;
    size_t warmup = 1000;
    std::string output = "output.csv";
    std::string write_key;
    bool has_seed = false;
    uint64_t seed = 0;
    bool has_key = false;
    Block key{};
    bool evict = true;
};

Config parse_args(int argc, char **argv) {
    Config cfg;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto need_value = [&](const char *name) -> std::string {
            if (i + 1 >= argc) {
                throw std::runtime_error(std::string("missing value for ") + name);
            }
            return argv[++i];
        };

        if (arg == "--samples") {
            cfg.samples = static_cast<size_t>(std::stoull(need_value("--samples")));
        } else if (arg == "--output") {
            cfg.output = need_value("--output");
        } else if (arg == "--seed") {
            cfg.has_seed = true;
            cfg.seed = std::stoull(need_value("--seed"));
        } else if (arg == "--key-hex") {
            cfg.has_key = true;
            cfg.key = parse_hex_block(need_value("--key-hex"));
        } else if (arg == "--write-key") {
            cfg.write_key = need_value("--write-key");
        } else if (arg == "--warmup") {
            cfg.warmup = static_cast<size_t>(std::stoull(need_value("--warmup")));
        } else if (arg == "--no-evict") {
            cfg.evict = false;
        } else if (arg == "--help" || arg == "-h") {
            usage(argv[0]);
            std::exit(0);
        } else {
            throw std::runtime_error("unknown option: " + arg);
        }
    }
    return cfg;
}

void self_test() {
    const Block key = parse_hex_block("000102030405060708090a0b0c0d0e0f");
    const Block plaintext = parse_hex_block("00112233445566778899aabbccddeeff");
    const std::string expected = "69c4e0d86a7b0430d8cdb78070b4c55a";
    AES128 aes(key);
    const Block ciphertext = aes.encrypt(plaintext);
    if (hex_encode(ciphertext) != expected) {
        throw std::runtime_error("AES self-test failed");
    }
}

}  // namespace

int main(int argc, char **argv) {
    try {
        self_test();
        const Config cfg = parse_args(argc, argv);

        std::random_device rd;
        const uint64_t seed = cfg.has_seed
                                  ? cfg.seed
                                  : ((static_cast<uint64_t>(rd()) << 32) ^ rd());
        std::mt19937_64 rng(seed);
        std::mt19937_64 probe_rng(seed ^ 0xd1b54a32d192ed03ULL);

        const Block key = cfg.has_key ? cfg.key : random_block(rng);
        AES128 aes(key);
        const Block round10_key = aes.round10_key();

        if (!cfg.write_key.empty()) {
            std::ofstream key_file(cfg.write_key);
            if (!key_file) {
                throw std::runtime_error("cannot open key output file");
            }
            key_file << hex_encode(key) << "\n";
        }

        for (size_t i = 0; i < cfg.warmup; ++i) {
            const Block pt = random_block(rng);
            const Block ct = aes.encrypt(pt);
            cache_sink ^= ct[0];
        }

        std::vector<uint8_t> eviction_buffer(8 * 1024 * 1024, 0x5a);
        std::ofstream out(cfg.output);
        if (!out) {
            throw std::runtime_error("cannot open output file");
        }

        out << "sample,plaintext_hex,ciphertext_hex,time_ns,cycles";
        for (int line = 0; line < 16; ++line) {
            out << ",line" << line;
        }
        out << '\n';
        out << std::fixed << std::setprecision(3);
        for (size_t i = 0; i < cfg.samples; ++i) {
            const Block plaintext = random_block(rng);
            if (cfg.evict) {
                evict_cache(eviction_buffer);
            }

            const uint64_t t0_ns = now_ns();
            const uint64_t c0 = rdtsc_begin();
            const Block ciphertext = aes.encrypt(plaintext);
            const uint64_t c1 = rdtsc_end();
            const uint64_t t1_ns = now_ns();

            const auto probe_times =
                simulated_sbox_probe_times(ciphertext, round10_key, probe_rng);
            cache_sink ^= ciphertext[i & 15];
            out << i << ','
                << hex_encode(plaintext) << ','
                << hex_encode(ciphertext) << ','
                << (t1_ns - t0_ns) << ','
                << (HAS_RDTSC ? (c1 - c0) : 0);
            for (double probe_time : probe_times) {
                out << ',' << probe_time;
            }
            out << '\n';
        }

        std::cerr << "wrote " << cfg.samples << " traces to " << cfg.output << "\n";
        std::cerr << "seed=" << seed << "\n";
        if (!cfg.write_key.empty()) {
            std::cerr << "key written to " << cfg.write_key << "\n";
        }
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "error: " << e.what() << "\n";
        usage(argv[0]);
        return 1;
    }
}
