import random

from Crypto.Util import number
from Crypto.Hash import SHA256
from math import gcd


def rsa():
    """
    Generates public and private keys
    :return: dictionary with modulo, public_exponent and private_exponent
    """
    # Generate two distinct primes p and q
    p = number.getPrime(512)
    q = number.getPrime(512)

    # Use p and q to generate N
    n = p*q

    # Find coprime with N, called lambda_n
    lambda_n = (q-1)*(p-1)
    # print(lambda_n)

    e = find_e(lambda_n)

    # choose hidden key d
    d = pow(e, -1, lambda_n)

    keys = {
        "modulo": n,
        "public_exponent": e,
        "private_exponent": d
    }
    return keys


# Find a new valid e
def find_e(lambda_n):
    count = 0
    while True:
        count += 1
        e = random.randrange(2, lambda_n)
        if gcd(e, lambda_n) == 1:
            print(f"E found after {count} iterations")
            return e


# Take 65537 as e, since it's commonly chosen and works well
def lazy_e():
    return 65537


def encrypt(public_exponent, public_mod, message):
    converted_msg = message
    encrypted_mgs = pow(converted_msg, public_exponent, public_mod)
    return encrypted_mgs


def decrypt(private_exponent, public_mod, encrypted_msg):
    decrypted_msg = pow(encrypted_msg, private_exponent, public_mod)
    convert_to_text = decrypted_msg
    return convert_to_text


def sign(private_exponent, public_mod, message):
    hashed_msg = int.from_bytes(SHA256.new(str(message).encode()).digest(), byteorder='big')
    signature = encrypt(private_exponent, public_mod, hashed_msg)
    return signature


def verify(public_exponent, public_mod, signature, message):
    decrypted_sign = decrypt(public_exponent, public_mod, signature)
    hashed_msg = int.from_bytes(SHA256.new(str(message).encode()).digest(), byteorder='big')
    if decrypted_sign == hashed_msg:
        return True
    else:
        return False


# prime = number.getPrime(512)
# print(prime)
# print(prime.bit_length())

keys = rsa()
message = 22
encrypted_msg = encrypt(keys.get("public_exponent"), keys.get("modulo"), message)
print(encrypted_msg)
decrypted_message = decrypt(keys.get("private_exponent"), keys.get("modulo"), encrypted_msg)
print(decrypted_message)

# other way around
decrypted_message1 = decrypt(keys.get("private_exponent"), keys.get("modulo"), decrypted_message)
print(decrypted_message1)
encrypted_msg1 = encrypt(keys.get("public_exponent"), keys.get("modulo"), decrypted_message1)
print(encrypted_msg1)

message2 = 2992142
signature = sign(keys.get("private_exponent"), keys.get("modulo"), message2)
print(signature)

print(verify(keys.get("public_exponent"), keys.get("modulo"), signature, message2))


