from app import db
from app.models import User, Invoice

def query_db():
    users = User.query.all()
    invoices = Invoice.query.all()

    print("Users:")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Role: {user.role}")

    print("\nInvoices:")
    for invoice in invoices:
        print(f"ID: {invoice.id}, User ID: {invoice.user_id}, Amount Due: {invoice.amount_due}, Created At: {invoice.created_at}")

if __name__ == "__main__":
    query_db()
