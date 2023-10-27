from src.defender import Defender, encrypt_w_public_key, decrypt_w_public_key
from math import gcd


def intercept_signature(target, faulty_sign, sign):
    difference = sign - faulty_sign
    hidden = gcd(difference, target.n)
    print(f"Is p? {hidden == target._p}")
    print(f"Is q? {hidden == target._q}")
    other = target.n // hidden
    try:
        private_epx = pow(target.d, -1, (hidden-1)*(other-1))
        return private_epx
    except Exception as e:
        print("Fault was either twice in p or twice in q")
        return 0


def signature_transaction(target, receiver):
    message = 1234
    # Send message with public key of receiver and sign with private exponent
    fault_encrypted_msg, fault_signature = target.send_msg_w_fault(message, receiver)
    not_correct = receiver.is_sender_signature(fault_signature, fault_encrypted_msg, target)
    print(f"Is the signature correct: {not_correct}")

    fault_encrypted_msg2, fault_signature2 = target.send_msg_w_fault(message, receiver)

    encrypted_msg, signature = target.send_msg(message, receiver)
    correct = receiver.is_sender_signature(signature, encrypted_msg, target)
    print(f"Is the signature correct: {correct}")
    return fault_signature, fault_signature2, signature


def intercept_signature_test():
    target = Defender()
    receiver = Defender()
    fault_signature, fault_signature2, signature = signature_transaction(target, receiver)

    private_epx = intercept_signature(target, fault_signature, signature)
    print(f"Found private exponent with one faulty signature? {private_epx == target._e}")

    private_epx2 = intercept_signature(target, fault_signature, fault_signature2)
    if private_epx2 != 0:
        print(f"Found private exponent with 2 faulty signatures? {private_epx2 == target._e}")


def message_transaction(target, sender):
    message = 1234
    encrypted_msg, signature = sender.send_msg(message, target)
    decrypted_msg_w_fault = target.decrypt_crt_w_fault(encrypted_msg)
    print(f"Sender of message has been verified: {target.verify(signature, decrypted_msg_w_fault, sender)}")
    decrypted_msg = target.decrypt_w_crt(encrypted_msg)
    print(f"Sender of message has been verified: {target.verify(signature, decrypted_msg, sender)}")
    return decrypted_msg_w_fault, decrypted_msg


def intercepted_decrypted_message_test():
    target = Defender()
    sender = Defender()
    msg1, msg2 = message_transaction(target, sender)
    private_exponent = intercept_signature(target, msg1, msg2)
    print(f"Target private exponent has been found: {private_exponent == target._e}")


if __name__ == "__main__":
    print("--- Attack on faulty signature interception ---")
    intercept_signature_test()
    print("\n--- Attack on faulty decryption output message ---")
    intercepted_decrypted_message_test()
