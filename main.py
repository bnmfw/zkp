from prover import Prover
from verifier import Verifier
from trusted_setup import setup
import hashlib

stored_provers = {}
stored_commitments = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    global stored_provers, stored_commitments

    if username in stored_provers:
        print(f"Usuário {username} já está registrado!")
        return

    hashed_password = hash_password(password)

    prover = Prover(setup, hashed_password.encode())
    C = prover.committedFS()  
    stored_provers[username] = prover
    stored_commitments[username] = C


def login_user(username, password):
    global stored_provers, stored_commitments

    if username not in stored_provers:
        return False


    commitment = stored_commitments[username]
    verifier = Verifier(setup)
    verifier.setCommitment(commitment)

    hashed_password = hash_password(password)
    login_prover = Prover(setup, hashed_password.encode())

    a = verifier.getA()
    b = login_prover.FA(a)
    verifier.setB(b)

    proof = login_prover.WS(a)

    if verifier.verify(proof):
        return True
    else:
        return False

if __name__ == '__main__':
    register_user("usuario1", "senhasegura")
    register_user("usuario2", "senhasegura2")

    print(login_user("usuario1", "senhasegura2"))  # False
    print(login_user("usuario2", "senhasegura2"))  # True
    print(login_user("usuario1", "senhasegura"))   # True