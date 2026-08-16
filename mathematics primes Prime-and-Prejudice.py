from collections import namedtuple
from Crypto.Util.number import *
from sympy.ntheory.modular import crt
import libnum, itertools, operator, functools, tqdm, json
from pwn import remote


'''
基于 Miller-Rabin, 生成在某组确定的素数基下的强伪素数
'''
class StrongPseudoPrimeGenerator:
    check_QR = lambda a, p: pow(a, (p - 1) // 2, p) == 1
    SPPG_Result = namedtuple('SPPG_Result', ['ok', 'pseudoPrime', 'factors'])

    def miller_rabin(self, n):
        """
        Miller Rabin test testing over prime basis `self.basis`
        """
        if n == 2 or n == 3:
            return True

        if n % 2 == 0:
            return False

        r, s = 0, n - 1
        while s % 2 == 0:
            r += 1
            s //= 2
        for b in self.basis:
            x = pow(b, s, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True

    def init_Sa(self):
        self.Sa = []
        for p in self.basis:
            f = set()
            for i in range(3, 200 * p):
                if isPrime(i) and not StrongPseudoPrimeGenerator.check_QR(p, i):
                    f.add(i % (4 * p))
            if p in f:
                f.remove(p)
            self.Sa.append(list(f))

    def init_Sb(self):
        self.Sb = []
        for idx, f in enumerate(self.Sa):
            p = self.basis[idx]
            cur = set(f)
            for i in range(1, len(self.k)):
                new = set()
                for num in f:
                    res = (num + self.k[i] - 1) * inverse(self.k[i], p * 4)
                    if res % 4 == 3:
                        new.add(res % (p * 4))
                cur = cur.intersection(new)
            self.Sb.append(list(cur))
    
    def generate_p(self, p1):
        return [i * (p1 - 1) + 1 for i in self.k]

    def get_p_prod(self, p1):
        return functools.reduce(operator.mul, self.generate_p(p1))

    def __init__(self, basis, k: list = [1, 101, 181]):
        self.basis = sorted(list(set(basis))) # 去重
        self.k = k
        for num in self.basis:
            if not isPrime(num):
                raise ValueError('basis should be prime list')
        if len(k) < 3:
            raise ValueError('len(k) should >= 3')
        if k[0] != 1:
            raise ValueError('k[0] should be 1')
        if len(k) != len(set(k)):
            raise ValueError('k should not contains same number')
        self.init_Sa()
        self.init_Sb()
    
    def generate(self, boundl, boundr):
        for chosen_set in itertools.product(*self.Sb):
            residues = [self.k[1] - inverse(self.k[2], self.k[1]), self.k[2] - inverse(self.k[1], self.k[2])]
            modules = [self.k[1], self.k[2]]
            for i, t in enumerate(chosen_set):
                residues.append(t)
                modules.append(4 * self.basis[i])
            result = crt(modules, residues)
            if not result:
                continue
            sol, mod = result
            found = False
            range_left = sol
            l, r = 1, boundl
            while l <= r:
                mid = (l + r) // 2
                if self.get_p_prod(mid * mod + sol) < boundl:
                    l = mid + 1
                else:
                    r = mid - 1
                    range_left = mid * mod + sol
            for cur_t in tqdm.tqdm(range(range_left, min(range_left + 100000 * mod, boundr), mod)):
                if isPrime(cur_t):
                    pseudoPrime = self.get_p_prod(cur_t)
                    factors = self.generate_p(cur_t)
                    if self.miller_rabin(pseudoPrime):
                        if boundl <= pseudoPrime <= boundr:
                            found = True
                            return StrongPseudoPrimeGenerator.SPPG_Result(ok=True, pseudoPrime=pseudoPrime, factors=factors)
        return StrongPseudoPrimeGenerator.SPPG_Result(ok=False, pseudoPrime=-1, factors=[])

def generate_basis(n):
    basis = [True] * n
    for i in range(3, int(n**0.5)+1, 2):
        if basis[i]:
            basis[i*i::2*i] = [False]*((n-i*i-1)//(2*i)+1)
    return [2] + [i for i in range(3, n, 2) if basis[i]]

gen = StrongPseudoPrimeGenerator(generate_basis(64))
result = gen.generate(2**100, 2**101)
if result.ok:
    print('Success')
    toSend = {'prime': result.pseudoPrime, 'base': result.factors[0]}
    r = remote('socket.cryptohack.org', 13385)
    r.recvline()
    r.send(json.dumps(toSend).encode() + b'\n')
    print(json.loads(r.recvline().decode())['Response'])
else:
    print('Fail')
