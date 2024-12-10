from bib.bls12381 import n, MINUS1

def lagrange_polynomial(points, prime=n):
    return __interpolate_polynomial(
        [i[0] for i in points], [k[1] for k in points], prime
    )


def polynomial_division(polynomial, divisor):
    polynomial.reverse()
    c1 = polynomial[0]
    remainder = polynomial[1]
    final_polynomial = []
    for i in range(len(polynomial) - 1):
        final_polynomial.append(c1)
        c1 = (MINUS1 * c1 * divisor + remainder) % n
        if i < len(polynomial) - 2:
            remainder = polynomial[i + 2]
    final_polynomial.reverse()
    return final_polynomial


# low-level lagrange interpolation reduced mod prime
def __interpolate_polynomial(x, y, prime):
    M = [[_x**i * (-1) ** (i * len(x)) for _x in x] for i in range(len(x))]
    N = [(M + [y] + M)[d : d + len(x)] for d in range(len(x) + 1)]
    C = [__determinant(k) for k in N]
    fac = __mod_inv(C[0] * (-1) ** (len(x) + 1), prime)
    C = [i * fac % prime for i in C]
    return C[1:]


def __determinant(m):
    M = [row[:] for row in m]
    N, sign, prev = len(M), 1, 1
    for i in range(N - 1):
        if M[i][i] == 0:
            swapto = next((j for j in range(i + 1, N) if M[j][i] != 0), None)
            if swapto is None:
                return 0
            M[i], M[swapto], sign = M[swapto], M[i], -sign
        for j in range(i + 1, N):
            for k in range(i + 1, N):
                assert (M[j][k] * M[i][i] - M[j][i] * M[i][k]) % prev == 0
                M[j][k] = (M[j][k] * M[i][i] - M[j][i] * M[i][k]) // prev
        prev = M[i][i]
    return sign * M[-1][-1]

# modular math
def __mod_inv(x, p):
	assert __gcd(x, p) == 1, "Divisor %d not coprime to modulus %d" % (x, p)
	z, a = (x % p), 1
	while z != 1:
		q = - (p // z)
		z, a = (p + q * z), (q * a) % p
	return a

def __gcd(a, b):
	while b:
		a, b = b, a % b
	return a