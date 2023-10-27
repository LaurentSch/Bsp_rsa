from src.defender import Defender
from math import gcd


def intercept_signature(target, faulty_sign, sign):
    difference = sign - faulty_sign
    hidden = gcd(difference, target.n)
    other = target.n // hidden
    private_epx = pow(target.d, -1, (hidden-1)*(other-1))
    return private_epx




if __name__ == "__main__":
    attackee = Defender()
    receiver = Defender()
    message = 1234
    fault_encrypted_msg, fault_signature = attackee.send_msg_w_fault(message, receiver)
    not_correct = receiver.is_sender_signature(fault_signature, fault_encrypted_msg, attackee)
    print(not_correct)
    encrypted_msg, signature = attackee.send_msg(message, receiver)
    correct = receiver.is_sender_signature(signature, encrypted_msg, attackee)
    print(correct)
    private_epx = intercept_signature(attackee, fault_signature, signature)
    print(f"Found private exponent? {private_epx == attackee._e}")
