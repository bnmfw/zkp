from prover import Prover
from verifier import Verifier
from trusted_setup import setup

senha = b'\xff'*460
senha2 = b'\xf0'*460

p = Prover(setup, senha)
p2 = Prover(setup, senha2)
v = Verifier(setup)

v.setCommitment(p.committedFS())

v.setB(p2.FA(v.getA()))
print(v.verify(p2.WS(v.getA())))

v.setB(p.FA(v.getA()))
print(v.verify(p.WS(v.getA())))