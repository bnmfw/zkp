from bib.ec import JacobianPoint, AffinePoint, EC
import bib.bls12381 as bls12381
from secrets import randbelow

def rand_int(prime):
	return __randrange(1, prime-1)

def __randrange(lower, upper):
	return randbelow(upper-lower)+lower

class TrustedSetup:
    def __init__(self, s: int, power: int = 16):
        ec1 = EC(*bls12381.parameters())
        ec2 = EC(*bls12381.parameters_twist()) 
        self.__G1: JacobianPoint = AffinePoint(ec1.gx, ec1.gy, False, ec1).to_jacobian()
        self.__G2: JacobianPoint = AffinePoint(ec2.g2x, ec2.g2y, False, ec2).to_jacobian()
        self.__encripted_s: list[JacobianPoint] = [s**i % bls12381.n * self.__G1 for i in range(power)]
        self.__s_G2: JacobianPoint = self.__G2 * s

    def getG1(self): return self.__G1

    def getG2(self): return self.__G2

    def getSBS(self): return self.__encripted_s

    def getSG2(self): return self.__s_G2
	
def rand_int(prime):
	return __randrange(1, prime-1)

def __randrange(lower, upper):
	return randbelow(upper-lower)+lower
setup = TrustedSetup(rand_int(bls12381.n))