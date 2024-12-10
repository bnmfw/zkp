from trusted_setup import TrustedSetup
from pairing import tate_pairing
from bls12381 import n
from random import randint


class Verifier:
    def __init__(self, setup: TrustedSetup):
        self.__setup = setup
        self.__a = randint(1, 15)

    def getA(self):
        return self.__a

    def setB(self, b):
        self.__b = b

    def setCommitment(self, commit):
        self.__commit = commit

    def verify(self, proof):
        s_minus_x = (n - self.__a) * self.__setup.getG2() + self.__setup.getSG2()
        result = tate_pairing(proof, s_minus_x)
        c_minus_y = (n - self.__b) * self.__setup.getG1() + self.__commit
        return result == tate_pairing(c_minus_y, self.__setup.getG2())
