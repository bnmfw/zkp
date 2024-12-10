from ec import JacobianPoint, AffinePoint, EC
import bls12381

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

setup = TrustedSetup(4407697174071727152978788492618288547108724430693899596767139174863299291018)