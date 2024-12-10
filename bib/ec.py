"""
Este modulo contem parte o arcabouco necessario para aritimetica com Curvas Elipticas
"""

from __future__ import annotations

from collections import namedtuple
from copy import deepcopy

import bib.bls12381 as bls12381
from bib.fields import FieldExtBase, Fq, Fq6, Fq12

# Struct for elliptic curve parameters
EC = namedtuple("EC", "q a b gx gy g2x g2y n h x k sqrt_n3 sqrt_n3m1o2")

default_ec = EC(*bls12381.parameters())


class AffinePoint:
    """
    Elliptic curve point, can represent any curve, and use Fq or Fq2
    coordinates.
    """

    def __init__(self, x, y, infinity: bool, ec=default_ec):
        if (
            (not isinstance(x, Fq) and not isinstance(x, FieldExtBase))
            or (not isinstance(y, Fq) and not isinstance(y, FieldExtBase))
            or type(x) != type(y)
        ):
            raise Exception("x,y should be field elements")
        self.FE = type(x)
        self.x = x
        self.y = y
        self.infinity = infinity
        self.ec = ec

    def is_on_curve(self) -> bool:
        """
        Check that y^2 = x^3 + ax + b.
        """
        if self.infinity:
            return True
        left = self.y * self.y
        right = self.x * self.x * self.x + self.ec.a * self.x + self.ec.b

        return left == right

    def __add__(self, other: AffinePoint) -> AffinePoint:
        if other == 0:
            return self
        if not isinstance(other, AffinePoint):
            raise Exception("Incorrect object")

        return add_points(self, other, self.ec, self.FE)

    def __radd__(self, other: AffinePoint) -> AffinePoint:
        return self.__add__(other)

    def __sub__(self, other: AffinePoint) -> AffinePoint:
        return self.__add__(other.negate())

    def __rsub__(self, other: AffinePoint) -> AffinePoint:
        return self.negate().__add__(other)

    def __str__(self) -> str:
        return (
            "AffinePoint(x="
            + self.x.__str__()
            + ", y="
            + self.y.__str__()
            + ", i="
            + str(self.infinity)
            + ")\n"
        )

    def __repr__(self) -> str:
        return (
            "AffinePoint(x="
            + self.x.__repr__()
            + ", y="
            + self.y.__repr__()
            + ", i="
            + str(self.infinity)
            + ")\n"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, AffinePoint):
            return False
        return (
            self.x == other.x and self.y == other.y and self.infinity == other.infinity
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __mul__(self, c) -> AffinePoint:
        if not isinstance(c, Fq) and not isinstance(c, int):
            raise ValueError("Error, must be int or Fq")
        return scalar_mult_jacobian(c, self.to_jacobian(), self.ec).to_affine()

    def negate(self) -> AffinePoint:
        return AffinePoint(self.x, -self.y, self.infinity, self.ec)

    def __rmul__(self, c: Fq) -> AffinePoint:
        return self.__mul__(c)

    def to_jacobian(self) -> JacobianPoint:
        return JacobianPoint(
            self.x, self.y, self.FE.one(self.ec.q), self.infinity, self.ec
        )

    def __deepcopy__(self, memo) -> AffinePoint:
        return AffinePoint(
            deepcopy(self.x, memo), deepcopy(self.y, memo), self.infinity, self.ec
        )


class JacobianPoint:
    """
    Elliptic curve point, can represent any curve, and use Fq or Fq2
    coordinates. Uses Jacobian coordinates so that point addition
    does not require slow inversion.
    """

    def __init__(self, x, y, z, infinity: bool, ec=default_ec):

        if (
            not isinstance(x, Fq)
            and not isinstance(x, FieldExtBase)
            or (not isinstance(y, Fq) and not isinstance(y, FieldExtBase))
            or (not isinstance(z, Fq) and not isinstance(z, FieldExtBase))
        ):
            raise Exception("x,y should be field elements")
        self.FE = type(x)
        self.x = x
        self.y = y
        self.z = z
        self.infinity = infinity
        self.ec = ec

    def is_on_curve(self) -> bool:
        if self.infinity:
            return True
        return self.to_affine().is_on_curve()

    def negate(self) -> JacobianPoint:
        return self.to_affine().negate().to_jacobian()

    def to_affine(self) -> AffinePoint:
        if self.infinity:
            return AffinePoint(
                Fq.zero(self.ec.q), Fq.zero(self.ec.q), self.infinity, self.ec
            )
        new_x = self.x / (self.z**2)
        new_y = self.y / (self.z**3)
        return AffinePoint(new_x, new_y, self.infinity, self.ec)

    def check_valid(self) -> None:
        assert self.is_on_curve()

    def __add__(self, other: JacobianPoint) -> JacobianPoint:
        if other == 0:
            return self
        if not isinstance(other, JacobianPoint):
            raise ValueError("Incorrect object")

        return add_points_jacobian(self, other, self.ec, self.FE)

    def __radd__(self, other: JacobianPoint) -> JacobianPoint:
        return self.__add__(other)

    def __eq__(self, other) -> bool:
        if not isinstance(other, JacobianPoint):
            return False
        return self.to_affine() == other.to_affine()

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __mul__(self, c) -> JacobianPoint:
        if not isinstance(c, int) and not isinstance(c, Fq):
            raise ValueError("Error, must be int or Fq")
        return scalar_mult_jacobian(c, self, self.ec)

    def __rmul__(self, c) -> JacobianPoint:
        return self.__mul__(c)

    def __neg__(self) -> JacobianPoint:
        return self.to_affine().negate().to_jacobian()

    def __str__(self) -> str:
        return (
            "JacobianPoint(x="
            + self.x.__str__()
            + ", y="
            + self.y.__str__()
            + "z="
            + self.z.__str__()
            + ", i="
            + str(self.infinity)
            + ")\n"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __deepcopy__(self, memo) -> JacobianPoint:
        return JacobianPoint(
            deepcopy(self.x, memo),
            deepcopy(self.y, memo),
            deepcopy(self.z, memo),
            self.infinity,
            self.ec,
        )

    def __hash__(self) -> int:
        return int.from_bytes(bytes(self), "big")


def double_point(p1: AffinePoint, ec=default_ec, FE=Fq) -> AffinePoint:
    """
    Basic elliptic curve point doubling
    """
    x, y = p1.x, p1.y
    left = Fq(ec.q, 3) * x * x
    left = left + ec.a
    s = left / (Fq(ec.q, 2) * y)
    new_x = s * s - x - x
    new_y = s * (x - new_x) - y
    return AffinePoint(new_x, new_y, False, ec)


def add_points(p1: AffinePoint, p2: AffinePoint, ec=default_ec, FE=Fq) -> AffinePoint:
    """
    Basic elliptic curve point addition.
    """
    assert p1.is_on_curve()
    assert p2.is_on_curve()
    if p1.infinity:
        return p2
    if p2.infinity:
        return p1
    if p1 == p2:
        return double_point(p1, ec, FE)
    if p1.x == p2.x:
        return AffinePoint(FE.zero(ec.q), FE.zero(ec.q), True, ec)

    x1, y1 = p1.x, p1.y
    x2, y2 = p2.x, p2.y
    s = (y2 - y1) / (x2 - x1)
    new_x = s * s - x1 - x2
    new_y = s * (x1 - new_x) - y1
    return AffinePoint(new_x, new_y, False, ec)


def double_point_jacobian(p1: JacobianPoint, ec=default_ec, FE=Fq) -> JacobianPoint:
    """
    Jacobian elliptic curve point doubling, see
    http://www.hyperelliptic.org/EFD/oldefd/jacobian.html
    """
    X, Y, Z = p1.x, p1.y, p1.z
    if Y == FE.zero(ec.q) or p1.infinity:
        return JacobianPoint(FE.one(ec.q), FE.one(ec.q), FE.zero(ec.q), True, ec)

    # S = 4*X*Y^2
    S = Fq(ec.q, 4) * X * Y * Y

    Z_sq = Z * Z
    Z_4th = Z_sq * Z_sq
    Y_sq = Y * Y
    Y_4th = Y_sq * Y_sq

    # M = 3*X^2 + a*Z^4
    M = Fq(ec.q, 3) * X * X
    M += ec.a * Z_4th

    # X' = M^2 - 2*S
    X_p = M * M - Fq(ec.q, 2) * S
    # Y' = M*(S - X') - 8*Y^4
    Y_p = M * (S - X_p) - Fq(ec.q, 8) * Y_4th
    # Z' = 2*Y*Z
    Z_p = Fq(ec.q, 2) * Y * Z
    return JacobianPoint(X_p, Y_p, Z_p, False, ec)


def add_points_jacobian(
    p1: JacobianPoint, p2: JacobianPoint, ec=default_ec, FE=Fq
) -> JacobianPoint:
    """
    Jacobian elliptic curve point addition, see
    http://www.hyperelliptic.org/EFD/oldefd/jacobian.html
    """
    if p1.infinity:
        return p2
    if p2.infinity:
        return p1
    # U1 = X1*Z2^2
    U1 = p1.x * (p2.z**2)
    # U2 = X2*Z1^2
    U2 = p2.x * (p1.z**2)
    # S1 = Y1*Z2^3
    S1 = p1.y * (p2.z**3)
    # S2 = Y2*Z1^3
    S2 = p2.y * (p1.z**3)
    if U1 == U2:
        if S1 != S2:
            return JacobianPoint(FE.one(ec.q), FE.one(ec.q), FE.zero(ec.q), True, ec)
        else:
            return double_point_jacobian(p1, ec, FE)

    # H = U2 - U1
    H = U2 - U1
    # R = S2 - S1
    R = S2 - S1
    H_sq = H * H
    H_cu = H * H_sq
    # X3 = R^2 - H^3 - 2*U1*H^2
    X3 = R * R - H_cu - Fq(ec.q, 2) * U1 * H_sq
    # Y3 = R*(U1*H^2 - X3) - S1*H^3
    Y3 = R * (U1 * H_sq - X3) - S1 * H_cu
    # Z3 = H*Z1*Z2
    Z3 = H * p1.z * p2.z
    return JacobianPoint(X3, Y3, Z3, False, ec)


def scalar_mult(c, p1: AffinePoint, ec=default_ec, FE=Fq) -> AffinePoint:
    """
    Double and add, see
    https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication
    """
    if p1.infinity or c % ec.q == 0:
        return AffinePoint(FE.zero(ec.q), FE.zero(ec.q), ec)
    result = AffinePoint(FE.zero(ec.q), FE.zero(ec.q), True, ec)
    addend = p1
    while c > 0:
        if c & 1:
            result += addend

        # double point
        addend += addend
        c = c >> 1

    return result


def scalar_mult_jacobian(c, p1: JacobianPoint, ec=default_ec, FE=Fq) -> JacobianPoint:
    """
    Double and add, see
    https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication
    """
    if isinstance(c, FE):
        c = c.value
    if p1.infinity or c % ec.q == 0:
        return JacobianPoint(FE.one(ec.q), FE.one(ec.q), FE.zero(ec.q), True, ec)

    result = JacobianPoint(FE.one(ec.q), FE.one(ec.q), FE.zero(ec.q), True, ec)
    addend = p1
    while c > 0:
        if c & 1:
            result += addend
        # double point
        addend += addend
        c = c >> 1
    return result


def untwist(point: AffinePoint, ec=default_ec) -> AffinePoint:
    """
    Given a point on G2 on the twisted curve, this converts its
    coordinates back from Fq2 to Fq12. See Craig Costello book, look
    up twists.
    """
    f = Fq12.one(ec.q)
    wsq = Fq12(ec.q, f.root, Fq6.zero(ec.q))
    wcu = Fq12(ec.q, Fq6.zero(ec.q), f.root)
    return AffinePoint(point.x / wsq, point.y / wcu, False, ec)


"""
Copyright 2020 Chia Network Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
