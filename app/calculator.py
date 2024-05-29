from app import db
from app.models import User, Invoice, DESKey
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

def calculate_and_update_invoices():
    users = User.query.all()
    current_key = DESKey.get_current_key()
    des_cipher = DES.new(current_key.key, DES.MODE_ECB)

    for user in users:
        if user.salary is not None and user.tax_percentage is not None:
            tax_amount = user.salary * (user.tax_percentage / 100)
            encrypted_invoice = des_cipher.encrypt(pad(str(tax_amount).encode(), DES.block_size))
            signature = generate_signature(str(tax_amount))  # Assuming you have a function to generate the signature

            existing_invoice = Invoice.query.filter_by(user_id=user.id).first()
            if existing_invoice:
                existing_invoice.amount_due = tax_amount
                existing_invoice.encrypted_invoice = encrypted_invoice
                existing_invoice.signature = signature
            else:
                new_invoice = Invoice(
                    user_id=user.id,
                    encrypted_invoice=encrypted_invoice,
                    signature=signature,
                    amount_due=tax_amount
                )
                db.session.add(new_invoice)

    db.session.commit()

def pad(data, block_size):
    """Pads data to be a multiple of block_size."""
    padding_len = block_size - len(data) % block_size
    padding = bytes([padding_len] * padding_len)
    return data + padding

def unpad(data):
    """Removes padding from data."""
    padding_len = data[-1]
    return data[:-padding_len]

def generate_signature(data):
    """Generates a signature for the given data."""
    # Add your RSA signature generation logic here
    pass
