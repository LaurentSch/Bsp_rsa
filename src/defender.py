from Crypto.Hash import SHA256
from Crypto.Util import number
import random
from decimal import Decimal


class Defender:
    """
    Generates encrypts messages and creates signatures using CTR
    """
    # def __init__(self):
    #

    def __init__(self):
        """
        Generates public and private exponents as well as the modulo
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

        e = 65537

        # choose hidden key d
        d = pow(e, -1, lambda_n)

        self._p = p
        self._q = q
        # private exponent
        self._e = d
        # public exponent
        self.d = e
        # modulo
        self.n = n

    def encrypt_w_crt(self, message):
        """
        Encrypt a message with the RSA cryptosystem
        :param private_exponent: your public exponent used for RSA
        :param public_mod: your public modulo used for RSA
        :param message: integer message that needs to be converted with RSA
        :return: RSA encrypted integer
        """
        d_p = self._e % (self._p-1)
        d_q = self._e % (self._q-1)
        q_inv = pow(self._q, -1, self._p)

        # Calculate intermediate messages
        m_p = pow(message, d_p, self._p)
        m_q = pow(message, d_q, self._q)
        h = (q_inv * (m_p - m_q)) % self._p
        # Calculate the final encrypted message
        encrypted_msg = m_q + h * self._q
        return encrypted_msg

    def encrypt_crt_w_fault(self, message):
        """
        Encrypt a message with the RSA cryptosystem
        :param private_exponent: your public exponent used for RSA
        :param public_mod: your public modulo used for RSA
        :param message: integer message that needs to be converted with RSA
        :return: RSA encrypted integer
        """
        d_p = self._e % (self._p-1)
        d_q = self._e % (self._q-1)
        q_inv = pow(self._q, -1, self._p)

        # Calculate intermediate messages
        c_p = pow(message, d_p, self._p)
        c_q = pow(message, d_q, self._q)

        # Introduce fault
        fault = random.randint(0, 1)
        if fault == 0:
            c_p = c_p * 10 + 1
        else:
            c_q = c_q * 10 + 1

        h = (q_inv * (c_p - c_q)) % self._p

        # Calculate the final encrypted message
        encrypted_msg = c_q + h * self._q
        return encrypted_msg

    def encrypt_w_public_key(self, public_exponent, public_modulo, message):
        encrypted_msg = pow(message, public_exponent, public_modulo)
        return encrypted_msg

    def decrypt_w_crt(self, encrypted_msg):
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
        d_p = pow(self._e, 1, (self._p-1))
        d_q = pow(self._e, 1, (self._q-1))
        q_inv = pow(self._q, -1, self._p)

        # Calculate intermediate messages
        m_p = pow(encrypted_msg, d_p, self._p)
        m_q = pow(encrypted_msg, d_q, self._q)
        h = (q_inv * (m_p - m_q)) % self._p
        # Calculate the final decrypted message
        decrypted_message = m_q + h * self._q

        return decrypted_message

    def decrypt_crt_w_fault(self, private_exponent, encrypted_msg):
        d_p = pow(private_exponent, 1, (self._p-1))
        d_q = pow(private_exponent, 1, (self._q-1))
        q_inv = pow(self._q, -1, self._p)

        # Calculate intermediate messages
        m_p = pow(encrypted_msg, d_p, self._p)
        m_q = pow(encrypted_msg, d_q, self._q)

        # Introduce fault
        fault = random.randint(0, 1)
        if fault == 0:
            m_p = m_p * 10 + 1
        else:
            m_q = m_q * 10 + 1

        h = (q_inv * (m_p - m_q)) % self._p
        decrypted_message = m_q + h * self._q

        return decrypted_message

    def is_sender_signature(self, signature, encrypted_message, target):
        message = self.decrypt_w_crt(encrypted_message)
        hashed_msg = int.from_bytes(SHA256.new(str(message).encode()).digest(), byteorder='big')
        decrypted_signature = pow(signature, target.d, target.n)
        if decrypted_signature == hashed_msg:
            return True
        else:
            return False

    def sign_w_crt(self, message):
        """
        Create RSA signature for an integer message

        Hashes the message with sha256 and encrypts it with your private RSA key
        :param private_exponent: your private RSA key
        :param public_mod: your public modulo used for RSA
        :param message: message you want to sign with RSA
        :return: RSA signature for your message
        """
        hashed_msg = int.from_bytes(SHA256.new(str(message).encode()).digest(), byteorder='big')
        signature = self.encrypt_w_crt(hashed_msg)
        return signature

    def sign_crt_w_fault(self, message):
        """
        Create RSA signature for an integer message

        Hashes the message with sha256 and encrypts it with your private RSA key
        :param private_exponent: your private RSA key
        :param public_mod: your public modulo used for RSA
        :param message: message you want to sign with RSA
        :return: RSA signature for your message
        """
        hashed_msg = int.from_bytes(SHA256.new(str(message).encode()).digest(), byteorder='big')
        signature = self.encrypt_crt_w_fault(hashed_msg)
        return signature

    def verify_w_crt(self, signature, message, target):
        """
        Checks if message signature encryption can be decrypted with public key of the sender.
        If false, the sender of the message is not the person they claim they are.

        :param public_exponent: the senders public exponent used for RSA
        :param public_mod: the senders public modulo used for RSA
        :param signature: encrypted hash of the message attached to it
        :param message: decrypted message (integer) you received
        :return: True if the decrypted signature matches the hash of the message
        """
        decrypted_sign = self.decrypt_w_crt(signature)
        hashed_msg = int.from_bytes(SHA256.new(str(message).encode()).digest(), byteorder='big')
        if decrypted_sign == hashed_msg:
            return True
        else:
            return False

    def send_msg(self, message, target):
        encrypted_msg = self.encrypt_w_public_key(target.d, target.n, message)
        signature = self.sign_w_crt(message)
        return encrypted_msg, signature

    def send_msg_w_fault(self, message, target):
        encrypted_msg = self.encrypt_w_public_key(target.d, target.n, message)
        signature = self.sign_crt_w_fault(message)
        return encrypted_msg, signature

if __name__ == "__main__":
    a = Defender()
    msg = a.encrypt_w_crt(1234)
    print(f"The final output is {a.decrypt_w_crt(msg)}")
