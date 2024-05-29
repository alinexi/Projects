from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# Generate a new DES key
def generate_des_key():
    return os.urandom(8)  # DES key size is 8 bytes

# Encrypt data using DES
def encrypt_data(key, data):
    iv = os.urandom(8)  # DES block size is 8 bytes
    cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    # Pad data to be a multiple of 8 bytes
    padding_length = 8 - (len(data) % 8)
    padded_data = data + bytes([padding_length] * padding_length)
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data

# Decrypt data using DES
def decrypt_data(key, encrypted_data):
    iv = encrypted_data[:8]
    encrypted_data = encrypted_data[8:]
    cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    # Remove padding
    padding_length = padded_data[-1]
    data = padded_data[:-padding_length]
    return data
