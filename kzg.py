from util import rand_int
from bls12381 import n
from ec import G1Generator, G2Generator
from polynomial import lagrange_polynomial, polynomial_division
from binascii import hexlify
from pairing import tate_pairing

G1 = G1Generator()
G2 = G2Generator()

default_length = 16


def trusted_setup(length=default_length):
    s = rand_int(n)
    s = 4407697174071727152978788492618288547108724430693899596767139174863299291018
    # print(s)
    s_powers = [s**i % n for i in range(length)]
    return [j * G1 for j in s_powers], s * G2


# how we encode the data in the poly is currently very basic
# but not really important in the context of the actual proof scheme
def encode_as_polynomial(data, length=default_length):
    # print(data)
    chunk_size = 31  # simple way to get chunks that safely map to GF(n)
    data = format_data(data, length * chunk_size)
    points = [
        (i, int(hexlify(data[i * chunk_size : (i + 1) * chunk_size]).decode(), 16))
        for i in range(length)
    ]
    poly = lagrange_polynomial(points)
    return points, poly


def commit(poly, setup_g1):
    assert len(poly) == len(setup_g1), "poly too large"
    return sum([i1 * i2 for i1, i2 in zip(poly, setup_g1)])


def proof(poly, b, setup_g1):
    poly = [((n - 1) * b[1] + poly[0]) % n] + poly[1:]
    qx, _ = polynomial_division(poly, (n - 1) * b[0])
    return sum([i1 * i2 for i1, i2 in zip(qx, setup_g1[: len(qx)])])


def verify(commitment, proof, b, s_g2):
    s_minus_x = (n - b[0]) * G2 + s_g2
    result = tate_pairing(proof, s_minus_x)
    c_minus_y = (n - b[1]) * G1 + commitment
    return result == tate_pairing(c_minus_y, G2)


def format_data(data, data_len):
    if type(data) != bytes:
        data = data.encode("utf-8")
    assert len(data) <= data_len, "data too large"
    if len(data) < data_len:
        padding = b"\x00" * (data_len - len(data))
        data = data + padding
    return data
