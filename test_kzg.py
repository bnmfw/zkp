import kzg
from polynomial import evaluate_polynomial

if __name__=='__main__':
    print("run kzg proof test:")
    # run trusted setup and store public setup bs
    setup_g1, s_g2 = kzg.trusted_setup()
    # print(setup_g1)

    # encode data as polynomial P(x)
    data=b'\xff'*460 # pick some random data
    bs, poly = kzg.encode_as_polynomial(data)

    # create kzg commitment to P(x) using public trusted_setup curve bs
    C = kzg.commit(poly, setup_g1)

    # choose some b on P(x) to prove
    b = (1, evaluate_polynomial(poly,1))
    # print(b)
    assert bs[1][0] == b[0], "xs should be equal"
    assert bs[1][1] == b[1], "ys should be equal"

    # create kzg proof
    pi = kzg.proof(poly, b, setup_g1)
    print(pi)

    # verifier can verify proof that some (x,y) b is on P(x)
    # with only commitment C, proof pi, the b in question
    # and public trusted_setup curve bs
    assert kzg.verify(C,pi,b,s_g2), "test fail: valid proof rejected"

    # evidence that proof only passes with the correct b
    wrong_b=(b[1], b[0])
    assert not kzg.verify(C,pi,wrong_b,s_g2), "test fail: uncaught invalid proof"
    
    print("SUCCESS!")