from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.Float, nullable=True)
    tax_percentage = db.Column(db.Float, nullable=True)

class TaxRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    encrypted_record = db.Column(db.LargeBinary, nullable=False)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invoice = db.Column(db.LargeBinary, nullable=False)
    signature = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    amount_due = db.Column(db.LargeBinary, nullable=False)
    amount_signature = db.Column(db.LargeBinary, nullable=False)

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
