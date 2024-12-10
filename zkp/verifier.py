from zkp.trusted_setup import TrustedSetup
from bib.pairing import tate_pairing
from bib.bls12381 import MINUS1
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

    def verify(self, ws):
        s_minus_a = self.__setup.getSG2() + MINUS1 * self.__a * self.__setup.getG2()
        fs_minus_b = self.__commit + MINUS1 * self.__b * self.__setup.getG1()
        return tate_pairing(ws, s_minus_a) == tate_pairing(
            fs_minus_b, self.__setup.getG2()
        )
