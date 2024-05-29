from app import db

from app.crypto_utils import encrypt_data, decrypt_data, generate_des_key

from datetime import datetime, timedelta


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    encrypted_password = db.Column(db.LargeBinary, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    encrypted_salary = db.Column(db.LargeBinary, nullable=True)
    encrypted_tax_percentage = db.Column(db.LargeBinary, nullable=True)

    def set_password(self, password, key):
        self.encrypted_password = encrypt_data(key, password.encode())

    def get_password(self, key):
        return decrypt_data(key, self.encrypted_password).decode()

    def set_salary(self, salary, key):
        self.encrypted_salary = encrypt_data(key, str(salary).encode())

    def get_salary(self, key):
        if self.encrypted_salary is None:
            return 0.0  # or some default value
        return float(decrypt_data(key, self.encrypted_salary).decode())

    def set_tax_percentage(self, tax_percentage, key):
        self.encrypted_tax_percentage = encrypt_data(key, str(tax_percentage).encode())

    def get_tax_percentage(self, key):
        if self.encrypted_tax_percentage is None:
            return 0.0  # or some default value
        return float(decrypt_data(key, self.encrypted_tax_percentage).decode())

class TaxRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    encrypted_record = db.Column(db.LargeBinary, nullable=False)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    encrypted_invoice = db.Column(db.LargeBinary, nullable=False)
    signature = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    amount_due = db.Column(db.Float, nullable=False)

class Key(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    des_key = db.Column(db.LargeBinary, nullable=False)
    rsa_private_key = db.Column(db.LargeBinary, nullable=False)
    rsa_public_key = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_details = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref=db.backref('payments', lazy=True))
    invoice = db.relationship('Invoice', backref=db.backref('payments', lazy=True))
    
    
class DESKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def get_current_key():
        des_key = DESKey.query.order_by(DESKey.created_at.desc()).first()
        if des_key and (datetime.utcnow() - des_key.created_at) < timedelta(days=30):
            return des_key.key
        else:
            new_key = DESKey(key=generate_des_key())
            db.session.add(new_key)
            db.session.commit()
            return new_key.key
        



