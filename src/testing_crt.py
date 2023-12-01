import random
from sympy import mod_inverse
from Crypto.Util import number


def generate_large_prime(bits):
    # Helper function to generate a large prime number
    return number.getPrime(bits)



def rsa_keygen(bits):
    # Generate RSA key pair
    p = generate_large_prime(bits)
    q = generate_large_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537  # A common choice for the public exponent
    d = mod_inverse(e, phi)
    return (n, e), (n, d), (p, q)


def encrypt(message, public_key):
    n, e = public_key
    return pow(message, e, n)


def decrypt(ciphertext, private_key, p, q):
    n, d = private_key
    m_p = pow(ciphertext, d % (p - 1), p)
    print(f"mp = {m_p}")
    m_q = pow(ciphertext, d % (q - 1), q)
    print(f"mq = {m_q}")
    q_inv = mod_inverse(q, p)
    h = (q_inv * (m_p - m_q)) % p
    return m_q + h * q


# Example usage:
bits = 512  # Adjust the key size as needed
public_key, private_key, pq = rsa_keygen(bits)
message = 12345  # Replace with your message
ciphertext = encrypt(message, public_key)
decrypted_message = decrypt(ciphertext, private_key, pq[0], pq[1])  # Replace p and q with the actual values

print(f"Original Message: {message}")
print(f"Decrypted Message: {decrypted_message}")
