#include <algorithm>
#include <cctype>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

struct Reg {
    int n;
    uint32_t taps;
};

static const int SIDE1 = 0;
static const int SELECTOR = 1;
static const int SIDE0 = 2;
static const int TOPK = 8;

static const Reg REGS[3] = {
    {19, 0x6df19},
    {21, 0xb7d01},
    {23, 0xc112d},
};

// Known output / keystream bytes, MSB-first. This is not ciphertext.
static const string KNOWN_OUTPUT_HEX =
    "b420d58e20de354cb3aa4a2a469b570824a2f282846fc208ee7dd28ad6b49f44"
    "305b0d7749c47c63d6b34d878412afa459193fba4718ab82c63e08fafb61e8b"
    "3cfbf7646b9d5bdfca3cb24523aba1e71959a6d8577aeef102f33788ad71642"
    "632dc916f6f869ce8c36819e2a717196cf1ee3eadbbf89bb02835681508516"
    "59f8ce863d7b9e13600679374a1195793690de3e18";

int bitcount(uint64_t x) {
    int c = 0;
    while (x) {
        ++c;
        x &= x - 1;
    }
    return c;
}

int parity(uint64_t x) {
    return bitcount(x) & 1;
}

int hex_value(char c) {
    if ('0' <= c && c <= '9') return c - '0';
    if ('a' <= c && c <= 'f') return c - 'a' + 10;
    if ('A' <= c && c <= 'F') return c - 'A' + 10;
    throw runtime_error("bad hex character");
}

vector<int> parse_hex_bits(string s) {
    string t;
    for (char c : s) {
        if (!isspace(static_cast<unsigned char>(c))) {
            t.push_back(c);
        }
    }
    if (t.size() >= 2 && t[0] == '0' && (t[1] == 'x' || t[1] == 'X')) {
        t = t.substr(2);
    }
    if (t.size() & 1) {
        t = "0" + t;
    }

    vector<int> bits;
    bits.reserve(t.size() * 4);
    for (size_t i = 0; i < t.size(); i += 2) {
        int byte = (hex_value(t[i]) << 4) | hex_value(t[i + 1]);
        for (int b = 7; b >= 0; --b) {
            bits.push_back((byte >> b) & 1);
        }
    }
    return bits;
}

void fwht(vector<int>& a) {
    for (size_t h = 1; h < a.size(); h <<= 1) {
        for (size_t i = 0; i < a.size(); i += h << 1) {
            for (size_t j = 0; j < h; ++j) {
                int x = a[i + j];
                int y = a[i + j + h];
                a[i + j] = x + y;
                a[i + j + h] = x - y;
            }
        }
    }
}

vector<uint32_t> lfsr_rows(int n, uint32_t taps, int m) {
    vector<uint32_t> state(n), rows;
    rows.reserve(m);
    for (int i = 0; i < n; ++i) {
        state[i] = uint32_t(1) << i;
    }

    for (int t = 0; t < m; ++t) {
        rows.push_back(state[0]);
        uint32_t fb = 0;
        for (int i = 0; i < n; ++i) {
            if ((taps >> i) & 1U) {
                fb ^= state[i];
            }
        }
        for (int i = 0; i + 1 < n; ++i) {
            state[i] = state[i + 1];
        }
        state[n - 1] = fb;
    }
    return rows;
}

vector<uint32_t> recover_correlated_candidates(const Reg& reg,
                                               const vector<int>& known,
                                               const string& name) {
    vector<uint32_t> rows = lfsr_rows(reg.n, reg.taps, int(known.size()));
    size_t size = size_t(1) << reg.n;
    vector<int> score(size, 0);

    for (size_t i = 0; i < known.size(); ++i) {
        score[rows[i]] += known[i] ? -1 : 1;
    }

    fwht(score);

    vector<pair<int, uint32_t> > top;
    for (uint32_t st = 1; st < size; ++st) {
        pair<int, uint32_t> item(score[st], st);
        if (top.size() < TOPK) {
            top.push_back(item);
            sort(top.rbegin(), top.rend());
        } else if (item > top.back()) {
            top.back() = item;
            sort(top.rbegin(), top.rend());
        }
    }

    cout << name << " candidates:\n";
    vector<uint32_t> states;
    for (auto [corr, st] : top) {
        int matches = (int(known.size()) + corr) / 2;
        cout << "  state = 0x" << hex << st << dec
             << "    matches = " << matches << "/" << known.size() << "\n";
        states.push_back(st);
    }
    return states;
}

vector<int> lfsr_bits(const Reg& reg, uint32_t state, int m) {
    vector<int> bits;
    bits.reserve(m);
    for (int i = 0; i < m; ++i) {
        bits.push_back(state & 1U);
        int fb = parity(state & reg.taps);
        state = (state >> 1) | (uint32_t(fb) << (reg.n - 1));
    }
    return bits;
}

struct SolveResult {
    bool ok;
    uint32_t state;
    int rank;
};

SolveResult solve_gf2(int n, const vector<pair<uint32_t, int> >& equations) {
    vector<uint64_t> rows;
    rows.reserve(equations.size());
    for (auto [mask, rhs] : equations) {
        rows.push_back(uint64_t(mask) | (uint64_t(rhs & 1) << n));
    }

    int rank = 0;
    vector<int> pivots;
    for (int col = 0; col < n; ++col) {
        int pivot = -1;
        for (int r = rank; r < int(rows.size()); ++r) {
            if ((rows[r] >> col) & 1ULL) {
                pivot = r;
                break;
            }
        }
        if (pivot == -1) {
            continue;
        }

        swap(rows[rank], rows[pivot]);
        for (int r = 0; r < int(rows.size()); ++r) {
            if (r != rank && ((rows[r] >> col) & 1ULL)) {
                rows[r] ^= rows[rank];
            }
        }
        pivots.push_back(col);
        ++rank;
    }

    uint64_t coeff_mask = (uint64_t(1) << n) - 1;
    for (int r = rank; r < int(rows.size()); ++r) {
        if ((rows[r] & coeff_mask) == 0 && ((rows[r] >> n) & 1ULL)) {
            return {false, 0, rank};
        }
    }

    uint32_t ans = 0;
    for (int i = 0; i < int(pivots.size()); ++i) {
        if ((rows[i] >> n) & 1ULL) {
            ans |= uint32_t(1) << pivots[i];
        }
    }
    return {true, ans, rank};
}

SolveResult recover_selector_state(const vector<int>& known,
                                   uint32_t side1_state,
                                   uint32_t side0_state,
                                   bool verbose) {
    vector<int> side1 = lfsr_bits(REGS[SIDE1], side1_state, int(known.size()));
    vector<int> side0 = lfsr_bits(REGS[SIDE0], side0_state, int(known.size()));
    vector<uint32_t> selector_rows =
        lfsr_rows(REGS[SELECTOR].n, REGS[SELECTOR].taps, int(known.size()));

    vector<pair<uint32_t, int> > equations;
    for (size_t i = 0; i < known.size(); ++i) {
        if (side1[i] == side0[i]) {
            continue;
        }
        equations.push_back(make_pair(selector_rows[i],
                                      known[i] == side1[i] ? 1 : 0));
    }

    SolveResult res = solve_gf2(REGS[SELECTOR].n, equations);
    if (verbose && res.ok) {
        cout << "selector_equations = " << equations.size()
             << ", rank = " << res.rank << "/" << REGS[SELECTOR].n << "\n";
        cout << "selector_state = 0x" << hex << res.state << dec << "\n";
    }
    return res;
}

vector<int> gen_geffe(const uint32_t states[3], int m) {
    vector<int> side1 = lfsr_bits(REGS[SIDE1], states[SIDE1], m);
    vector<int> selector = lfsr_bits(REGS[SELECTOR], states[SELECTOR], m);
    vector<int> side0 = lfsr_bits(REGS[SIDE0], states[SIDE0], m);
    vector<int> out;
    out.reserve(m);
    for (int i = 0; i < m; ++i) {
        out.push_back(selector[i] ? side1[i] : side0[i]);
    }
    return out;
}

int main() {
    vector<int> known = parse_hex_bits(KNOWN_OUTPUT_HEX);
    cout << "known_bits = " << known.size() << "\n";

    vector<uint32_t> side1_candidates =
        recover_correlated_candidates(REGS[SIDE1], known, "side1");
    vector<uint32_t> side0_candidates =
        recover_correlated_candidates(REGS[SIDE0], known, "side0");

    for (uint32_t side1_state : side1_candidates) {
        for (uint32_t side0_state : side0_candidates) {
            SolveResult sel =
                recover_selector_state(known, side1_state, side0_state, false);
            if (!sel.ok) {
                continue;
            }

            uint32_t states[3] = {};
            states[SIDE1] = side1_state;
            states[SELECTOR] = sel.state;
            states[SIDE0] = side0_state;

            if (gen_geffe(states, int(known.size())) == known) {
                recover_selector_state(known, side1_state, side0_state, true);
                cout << "verify = true\n";
                cout << "states = 0x" << hex << states[0]
                     << " 0x" << states[1]
                     << " 0x" << states[2] << dec << "\n";
                return 0;
            }
        }
    }

    cout << "verify = false\n";
    cout << "No candidate pair worked. Check that KNOWN_OUTPUT_HEX is the "
            "keystream/output, not ciphertext.\n";
    return 1;
}

