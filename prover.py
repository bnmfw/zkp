from trusted_setup import TrustedSetup
from poly import Polynomial

class Prover:
    def __init__(self, setup: TrustedSetup, password: int):
        self.__setup: TrustedSetup = setup
        self.__poly: Polynomial = Polynomial(password)
    
    def committedFS(self):
        return self.__poly.apply(self.__setup.getSBS())
    
    def FA(self, a):
        return self.__poly.apply(a)

    def WS(self, a):
        wx: Polynomial = self.__poly.divide(a)
        return wx.apply(self.__setup.getSBS())

    def get_polynomial(self):
        return self.__poly.get_coefficients()
