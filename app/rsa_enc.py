from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


def generate_rsa_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

private_key, public_key = generate_rsa_key_pair()

# Save the keys securely
with open("private.pem", "wb") as prv_file:
    prv_file.write(private_key)

with open("public.pem", "wb") as pub_file:
    pub_file.write(public_key)



def sign_data(data, private_key):
    key = RSA.import_key(private_key)
    h = SHA256.new(data)
    signature = pkcs1_15.new(key).sign(h)
    return signature

# Example usage
data = b"This is a test invoice"
with open("private.pem", "rb") as prv_file:
    private_key = prv_file.read()

signature = sign_data(data, private_key)

def verify_signature(data, signature, public_key):
    key = RSA.import_key(public_key)
    h = SHA256.new(data)
    try:
        pkcs1_15.new(key).verify(h, signature)
        print("The signature is valid.")
        return True
    except (ValueError, TypeError):
        return False

# Example usage
with open("public.pem", "rb") as pub_file:
    public_key = pub_file.read()

verify_signature(data, signature, public_key)

