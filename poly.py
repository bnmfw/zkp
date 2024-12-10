from kzg import format_data, lagrange_polynomial, hexlify
from bls12381 import n
from polynomial import polynomial_division


class Polynomial:
    def __init__(self, password):
        if password is None:
            return
        chunk_size = 31  # simple way to get chunks that safely map to GF(n)
        password = format_data(password, 16 * chunk_size)
        self.__points = [
            (
                i,
                int(
                    hexlify(password[i * chunk_size : (i + 1) * chunk_size]).decode(),
                    16,
                ),
            )
            for i in range(16)
        ]
        self.__coeficients: list[int] = lagrange_polynomial(self.__points)

    def setPoly(self, poly: list[int]):
        self.__coeficients: list[int] = poly

    def apply(self, x):
        # Recebe uma lista com valores ja exponenciados
        if isinstance(x, list):
            for i, (xi, ci) in enumerate(zip(x, self.__coeficients)):
                if not i:
                    acc = ci * xi
                    continue
                acc += ci * xi
            return acc

        # Avaliacao normal
        acc = 0
        for i, ci in enumerate(self.__coeficients):
            acc += pow(x, i, n) * ci
        return acc % n

    def divide(self, a):
        b = self.apply(a)
        poly = self.__coeficients.copy()
        poly[0] += b * (n - 1)
        poly[0] %= n
        qx, _ = polynomial_division(poly, (n - 1) * a)
        return qx
