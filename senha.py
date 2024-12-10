import kzg
from bib.polynomial import evaluate_polynomial
import hashlib

stored_polynomial = None
stored_commitment = None
setup_g1, setup_g2 = kzg.trusted_setup()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    global stored_polynomial, stored_commitment

    print(f"Registrando usuário: {username}")

    hashed_password = hash_password(password)
    print(f"Hash da senha (registro): {hashed_password}")

    data = hashed_password.encode()  
    _, polynomial = kzg.encode_as_polynomial(data)
    commitment = kzg.commit(polynomial, setup_g1)

    stored_polynomial = polynomial
    stored_commitment = commitment

    print(len(polynomial))

    print(f"Polinômio armazenado no registro: {polynomial}")
    print(f"Compromisso armazenado: {commitment}")

def login_user(username, password):
    global stored_polynomial, stored_commitment

    print(f"Realizando login para o usuário: {username}")

    if stored_commitment is None or stored_polynomial is None:
        print("Erro: Nenhum usuário registrado!")
        return False

    hashed_password = hash_password(password)
    print(f"Hash da senha (login): {hashed_password}")

    x_p = 1
    y_p = evaluate_polynomial(stored_polynomial, x_p)
    print(f"Polinômio usado no login: {stored_polynomial}")
    print(f"Ponto calculado no login: (x_p={x_p}, y_p={y_p})")

    try:
        proof = kzg.proof(stored_polynomial, (x_p, y_p), setup_g1)
        print(f"Prova gerada no login: {proof}")
    except AssertionError as e:
        print(f"Erro ao gerar a prova: {e}")
        return False

    is_valid = kzg.verify(stored_commitment, proof, (x_p, y_p), setup_g2)

    if is_valid:
        print(f"Login para o usuário {username} bem-sucedido!")
        return True
    else:
        print(f"Falha no login para o usuário {username}: prova inválida.")
        return False

if __name__ == '__main__':
    register_user("usuario1", "senhasegura")

    # Tenta logar
    login_user("usuario1", "senhasegura")  # Sucesso
    # login_user("usuario1", "senhaerrada")   # Falha