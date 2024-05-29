from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import base64

def des_encrypt(data, key):
    cipher = DES.new(key, DES.MODE_ECB)
    padded_data = pad(data, DES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_data)

def des_decrypt(encrypted_data, key):
    cipher = DES.new(key, DES.MODE_ECB)
    decoded_encrypted_data = base64.b64decode(encrypted_data)
    decrypted_data = cipher.decrypt(decoded_encrypted_data)
    return unpad(decrypted_data, DES.block_size)
