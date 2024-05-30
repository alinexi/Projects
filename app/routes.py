# routes.py

from flask import render_template, redirect, url_for, flash, request, session
from app import app, db
from app.models import User, TaxRecord, Invoice, SalaryInvoice, Key, Payment
from app.forms import TaxPercentageForm, SalaryForm, PaymentForm, InvoiceForm
from app.decorators import login_required
from app.des_enc import des_encrypt, des_decrypt
from app.rsa_enc import generate_rsa_key_pair, sign_data, verify_signature
import os
from flask import request

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        user = User.query.filter_by(username=username, password=password, role=role).first()
        if user:
            session['user_id'] = user.id  # Store user ID in session
            flash('Login successful!', 'success')
            if role == 'Sysadmin':
                return redirect(url_for('sysadmin_dashboard'))
            elif role == 'Staff':
                return redirect(url_for('staff_dashboard'))
            elif role == 'User':
                return redirect(url_for('user_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username, password, and role', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/sysadmin_dashboard')
@login_required
def sysadmin_dashboard():
    users = User.query.all()
    return render_template('sysadmin_dashboard.html', users=users)

@app.route('/staff_dashboard', methods=['GET', 'POST'])
@login_required
def staff_dashboard():
    tax_form = TaxPercentageForm()
    invoice_form = InvoiceForm()
    invoice_form.user_id.choices = [(user.id, user.username) for user in User.query.all()]

    if tax_form.validate_on_submit():
        user = User.query.get(tax_form.user_id.data)
        if user:
            user.tax_percentage = tax_form.tax_percentage.data
            db.session.commit()
            flash('Tax percentage updated successfully!', 'success')
            return redirect(url_for('staff_dashboard'))

    if invoice_form.validate_on_submit():
        with open("private.pem", "rb") as prv_file:
            private_key = prv_file.read()
        enc_invoice = des_encrypt(invoice_form.invoice.data.encode(), os.getenv('DES_KEY').encode())
        enc_amount_due = des_encrypt(str(invoice_form.amount_due.data).encode(), os.getenv('DES_KEY').encode())
        signature = sign_data(enc_invoice, private_key)
        amount_signature = sign_data(enc_amount_due, private_key)
        new_invoice = Invoice(
            user_id=invoice_form.user_id.data,
            invoice=enc_invoice,
            signature=signature,
            amount_due=enc_amount_due,
            amount_signature=amount_signature
        )
        db.session.add(new_invoice)
        db.session.commit()
        flash('Invoice added successfully!', 'success')
        return redirect(url_for('staff_dashboard'))

    users = User.query.all()
    return render_template('staff_dashboard.html', tax_form=tax_form, invoice_form=invoice_form, users=users)

@app.route('/user_dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    user_id = session.get('user_id')  # Retrieve user ID from session
    if not user_id:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    invoices = Invoice.query.filter_by(user_id=user_id).all()
    salary_invoices = SalaryInvoice.query.filter_by(user_id=user_id).all()
    payments = Payment.query.filter_by(user_id=user_id).all()

    with open("public.pem", "rb") as prv_file:
        public_key = prv_file.read()

    dec_invoices = []
    for inv in invoices:
        amount_signature_v = verify_signature(inv.amount_due, inv.amount_signature, public_key)
        signature_v = verify_signature(inv.invoice, inv.signature, public_key)
        if amount_signature_v and signature_v:
            inv.invoice = des_decrypt(inv.invoice, os.getenv('DES_KEY').encode()).decode()
            inv.amount_due = des_decrypt(inv.amount_due, os.getenv('DES_KEY').encode()).decode()
            dec_invoices.append(inv)

    dec_salary_invoices = []
    for inv in salary_invoices:
        amount_signature_v = verify_signature(inv.encrypted_amount_due, inv.amount_signature, public_key)
        if amount_signature_v:
            inv.amount_due = des_decrypt(inv.encrypted_amount_due, os.getenv('DES_KEY').encode()).decode()
            dec_salary_invoices.append(inv)

    payment_form = PaymentForm()
    salary_form = SalaryForm()

    tax_amount = None
    if salary_form.validate_on_submit():
        user.salary = salary_form.salary.data
        db.session.commit()
        
        if user.tax_percentage is not None and user.salary is not None:
            tax_amount = user.salary * (user.tax_percentage / 100)
            encrypted_tax_amount = des_encrypt(str(tax_amount).encode(), os.getenv('DES_KEY').encode())
            with open("private.pem", "rb") as prv_file:
                private_key = prv_file.read()
            amount_signature = sign_data(encrypted_tax_amount, private_key)
            new_salary_invoice = SalaryInvoice(
                user_id=user.id,
                amount_due=tax_amount,
                encrypted_amount_due=encrypted_tax_amount,
                amount_signature=amount_signature
            )
            db.session.add(new_salary_invoice)
            db.session.commit()
            flash('Salary and tax invoice updated successfully!', 'success')
        else:
            flash('Tax percentage or salary not set.', 'danger')
        return redirect(url_for('user_dashboard'))

    if payment_form.validate_on_submit():
        invoice_id = request.form['invoice_id']
        # Check if the invoice_id corresponds to a regular invoice or a salary invoice
        invoice = Invoice.query.get(invoice_id) or SalaryInvoice.query.get(invoice_id)
        if invoice and invoice.user_id == user_id:
            # Delete the invoice from the database
            db.session.delete(invoice)
            db.session.commit()

            flash('Payment successful and invoice deleted!', 'success')
            return redirect(url_for('user_dashboard'))

    return render_template('user_dashboard.html', user=user, payment_form=payment_form, salary_form=salary_form, invoices=dec_invoices, salary_invoices=dec_salary_invoices, payments=payments, tax_amount=tax_amount)


@app.route('/add_invoice', methods=['GET', 'POST'])
@login_required
def add_invoice():
    form = InvoiceForm()
    form.user_id.choices = [(user.id, user.username) for user in User.query.all()]
    if form.validate_on_submit():
        with open("private.pem", "rb") as prv_file:
            private_key = prv_file.read()
        enc_invoice = des_encrypt(form.invoice.data.encode(), os.getenv('DES_KEY').encode())
        enc_amount_due = des_encrypt(str(form.amount_due.data).encode(), os.getenv('DES_KEY').encode())
        signature = sign_data(enc_invoice, private_key)
        amount_signature = sign_data(enc_amount_due, private_key)
        new_invoice = Invoice(
            user_id=form.user_id.data,
            invoice=enc_invoice,
            signature=signature,
            amount_due=enc_amount_due,
            amount_signature=amount_signature
        )
        db.session.add(new_invoice)
        db.session.commit()
        flash('Invoice added successfully!', 'success')
        return redirect(url_for('staff_dashboard'))
    return render_template('add_invoice.html', form=form)

@app.route('/edit_invoice/<int:invoice_id>', methods=['GET', 'POST'])
@login_required
def edit_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    form = InvoiceForm(obj=invoice)
    form.user_id.choices = [(user.id, user.username) for user in User.query.all()]
    if form.validate_on_submit():
        invoice.user_id = form.user_id.data
        invoice.encrypted_invoice = form.encrypted_invoice.data.encode()
        invoice.signature = form.signature.data.encode()
        invoice.amount_due = form.amount_due.data
        db.session.commit()
        flash('Invoice updated successfully!', 'success')
        return redirect(url_for('staff_dashboard'))
    return render_template('edit_invoice.html', form=form, invoice_id=invoice_id)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            password=form.password.data,
            role=form.role.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('sysadmin_dashboard'))
    return render_template('add_user.html', form=form)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.password = form.password.data
        user.role = form.role.data
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('sysadmin_dashboard'))
    return render_template('edit_user.html', form=form, user_id=user_id)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('sysadmin_dashboard'))

def calculate_and_update_invoices():
    users = User.query.all()
    for user in users:
        if user.salary is not None and user.tax_percentage is not None:
            tax_amount = user.salary * (user.tax_percentage / 100)
            encrypted_tax_amount = des_encrypt(str(tax_amount).encode(), os.getenv('DES_KEY').encode())
            amount_signature = sign_data(encrypted_tax_amount, private_key)

            new_salary_invoice = SalaryInvoice(
                user_id=user.id,
                amount_due=tax_amount,
                encrypted_amount_due=encrypted_tax_amount,
                amount_signature=amount_signature
            )
            db.session.add(new_salary_invoice)
    db.session.commit()

@app.route('/payment_history')
@login_required
def payment_history():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    if user.role != 'Staff':
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('user_dashboard'))

    query = request.args.get('query')
    if query:
        payments = Payment.query.join(User).filter(
            (User.username.contains(query)) |
            (Payment.payment_details.contains(query))
        ).all()
    else:
        payments = Payment.query.all()
    print(len(payments))
    
    return render_template('payment_history.html', payments=payments)

@app.route('/user_payment_history/<int:user_id>')
@login_required
def user_payment_history(user_id):
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    payments = Payment.query.filter_by(user_id=user_id).all()
    return render_template('user_payment_history.html', user=user, payments=payments)
