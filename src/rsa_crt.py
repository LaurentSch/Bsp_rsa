import random
import time
from Crypto.Hash import SHA256
from Crypto.Util import number
from src.fast_exponentialion import fast_exponent


# Decorator function to measure execution time
def check_time_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time for {func.__name__}: {execution_time} seconds")
        return result
    return wrapper


def rsa():
    """
    Generates public and private exponents as well as the modulo
    :return: dictionary with modulo, public_exponent and private_exponent
    """
    # Generate two distinct primes p and q
    p = number.getPrime(1512)
    q = number.getPrime(1512)

    # Use p and q to generate N
    n = p*q

    # Find coprime with N, called lambda_n
    lambda_n = (q-1)*(p-1)
    # print(lambda_n)

    e = 65537

    # choose hidden key d
    d = pow(e, -1, lambda_n)

    keys = {
        "modulo": n,
        "public_exponent": e,
        "private_exponent": d,
        "p": p,
        "q": q
    }
    return keys


def encrypt(public_exponent, public_mod, message):
    """
    Encrypt a message with the RSA cryptosystem
    :param public_exponent: your public exponent used for RSA
    :param public_mod: your public modulo used for RSA
    :param message: integer message that needs to be converted with RSA
    :return: RSA encrypted integer
    """
    encrypted_n = fast_exponent(message, public_exponent, public_mod)
    return encrypted_n


@check_time_decorator
def decrypt(private_exponent, public_mod, encrypted_msg):
    """
    Decrypt a message that is encrypted with your public RSA key
    :param private_exponent: your private RSA key
    :param public_mod: your public modulo used for RSA
    :param encrypted_msg: integer message encrypted with your public RSA key
    :return: integer decrypted message
    """
    decrypted_msg = fast_exponent(encrypted_msg, private_exponent, public_mod)
    convert_to_text = decrypted_msg
    return convert_to_text


@check_time_decorator
def decrypt_w_crt(p, q, private_exponent, encrypted_msg):
    """
    Decrypt a message that is encrypted with your public RSA key
    :param private_exponent: your private RSA key
    :param public_mod: your public modulo used for RSA
    :param encrypted_msg: integer message encrypted with your public RSA key
    :return: integer decrypted message
    """
    # print(f"Is pow == by hand? {(private_exponent % (p-1)) == pow(private_exponent, 1, p-1)}")
    # From wikipedia pseudo-code
    # print(f"Value for private exponent: {private_exponent}")
    d_p = fast_exponent(private_exponent, 1, (p-1))
    print(f"Value for d_p: {d_p}")
    d_q = fast_exponent(private_exponent, 1, (q-1))
    print(f"Value for d_q: {d_q}")
    q_inv = fast_exponent(q, -1, p)
    print(f"q_inv is: {q_inv}")

    # Calculate intermediate messages
    m_p = fast_exponent(encrypted_msg, d_p, p)
    print(f"Message m1: {m_p}")
    m_q = fast_exponent(encrypted_msg, d_q, q)
    print(f"Message m2: {m_q}")
    h = (q_inv * (m_p - m_q)) % p
    print(h)
    # Calculate the final decrypted message
    decrypted_message = m_q + h * q

    return decrypted_message


def decrypt_crt_w_fault(p, q, private_exponent, encrypted_msg):
    d_p = fast_exponent(private_exponent, 1, (p-1))
    d_q = fast_exponent(private_exponent, 1, (q-1))
    q_inv = fast_exponent(q, -1, p)

    # Calculate intermediate messages
    m_p = fast_exponent(encrypted_msg, d_p, p)
    m_q = fast_exponent(encrypted_msg, d_q, q)

    # Introduce fault
    fault = random.randint(0, 1)
    if fault == 0:
        m_p = m_p * 10 + 1
    else:
        m_q = m_q * 10 + 1
    print(f"Message m1: {m_p}")
    print(f"Message m2: {m_q}")

    h = (q_inv * (m_p - m_q)) % p
    decrypted_message = m_q + h * q

    return decrypted_message, m_p, m_q


def sign_w_crt(private_exponent, public_mod, message):
    """
    Create RSA signature for an integer message

    Hashes the message with sha256 and encrypts it with your private RSA key
    :param private_exponent: your private RSA key
    :param public_mod: your public modulo used for RSA
    :param message: message you want to sign with RSA
    :return: RSA signature for your message
    """
    hashed_msg = int.from_bytes(SHA256.new(str(message).encode()).digest(), byteorder='big')
    signature = encrypt(private_exponent, public_mod, hashed_msg)
    return hashed_msg, signature


def verify_w_crt(p, q, public_exponent, public_mod, signature, message):
    """
    Checks if message signature encryption can be decrypted with public key of the sender.
    If false, the sender of the message is not the person they claim they are.

    :param public_exponent: the senders public exponent used for RSA
    :param public_mod: the senders public modulo used for RSA
    :param signature: encrypted hash of the message attached to it
    :param message: decrypted message (integer) you received
    :return: True if the decrypted signature matches the hash of the message
    """
    decrypted_sign = decrypt_w_crt(p, q, public_exponent, public_mod, signature)
    hashed_msg = int.from_bytes(SHA256.new(str(message).encode()).digest(), byteorder='big')
    if decrypted_sign == hashed_msg:
        return True
    else:
        return False


def verify_crt_w_fault(p, q, private_exponent, signature, message):
    decrypted_sign, m_p, m_q = decrypt_crt_w_fault(p, q, private_exponent, signature)
    hashed_msg = int.from_bytes(SHA256.new(str(message).encode()).digest(), byteorder='big')
    return decrypted_sign, m_p, m_q


def attack_w_signature(public_exponent, private_exponent, public_mod, p, q):
    message = 1337
    hash_s, sign = sign_w_crt(public_exponent, public_mod, message)
    decrypted_sign, m_p, m_q = verify_crt_w_fault(p, q, private_exponent, sign, message)
    print(f"m_p: {m_p}")
    print(f"m_q: {m_q}")
    is_zero_p = pow((pow(hash_s, public_exponent) - m_p), 1, p)
    print(f"Is this zero? {is_zero_p}")
    is_zero_q = pow((pow(hash_s, public_exponent) - m_q), 1, q)
    print(f"Is this zero? {is_zero_q}")



def testing_stuff():
    """
    Just a test function.
    """
    # prime = number.getPrime(512)
    # print(prime)
    # print(prime.bit_length())

    keys = rsa()
    message = 22
    p = keys.get("p")
    q = keys.get("q")
    # encrypted_msg = encrypt_w_crt(keys.get("public_exponent"), keys.get("modulo"), message)
    # print(f"This is the encrypted message {encrypted_msg}")
    # decrypted_message = decrypt_w_crt(p, q, keys.get("private_exponent"), keys.get("modulo"), encrypted_msg)
    # print(f"This is the decrypted message {decrypted_message}")
    #
    # message2 = 2992142
    # signature = sign_w_crt(p, q, keys.get("private_exponent"), keys.get("modulo"), message2)
    # print(signature)
    #
    # print(verify_w_crt(p, q, keys.get("public_exponent"), keys.get("modulo"), signature, message2))

    message3 = 17
    encrypted_msg = encrypt(keys.get("public_exponent"), keys.get("modulo"), message3)
    # print(f"Encrypted Message = {encrypted_msg}")
    # print("decrypt_w_crt result = ", decrypt_w_crt(p, q, keys.get("private_exponent"), encrypted_msg))
    # print("decrypt result = ", decrypt(keys.get("private_exponent"), encrypted_msg))
    print("decrypt_crt_w_fault result = ", decrypt_crt_w_fault(p, q, keys.get("private_exponent"), encrypted_msg))
    attack_w_signature(keys.get("public_exponent"), keys.get("private_exponent"), keys.get("modulo"), p, q)

if __name__ == "__main__":
    testing_stuff()
