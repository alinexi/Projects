from flask import render_template, redirect, url_for, flash, request, session
from app import app, db
from app.models import User, Invoice, Payment,DESKey
from app.forms import TaxRecordForm, UserForm, PaymentForm, InvoiceForm, SalaryForm, TaxPercentageForm
from app.decorators import login_required

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        current_key = DESKey.get_current_key()
        if not current_key:
            flash('DES key generation error. Please contact admin.', 'danger')
            return redirect(url_for('login'))
        user = User.query.filter_by(username=username, role=role).first()
        if user and user.get_password(current_key) == password:
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


@app.route('/sysadmin_dashboard', methods=['GET', 'POST'])
@login_required
def sysadmin_dashboard():
    current_key = DESKey.get_current_key()
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        role = form.role.data
        new_user = User(username=username, role=role)
        new_user.set_password(password, current_key)
        db.session.add(new_user)
        db.session.commit()
        flash(f'User {username} created successfully!', 'success')
        return redirect(url_for('sysadmin_dashboard'))
    
    users = User.query.all()
    for user in users:
        user.salary = user.get_salary(current_key)
        user.tax_percentage = user.get_tax_percentage(current_key)
    
    return render_template('sysadmin_dashboard.html', users=users, form=form)

@app.route('/staff_dashboard', methods=['GET', 'POST'])
@login_required
def staff_dashboard():
    current_key = DESKey.get_current_key()
    tax_form = TaxPercentageForm()
    if tax_form.validate_on_submit():
        user_id = tax_form.user_id.data
        tax_percentage = tax_form.tax_percentage.data
        user = User.query.get(user_id)
        if user:
            user.set_tax_percentage(tax_percentage, current_key)
            db.session.commit()
            calculate_and_update_invoices()  # Update invoices after setting tax percentage
            flash('Tax percentage updated successfully', 'success')
        else:
            flash('User not found', 'danger')
        return redirect(url_for('staff_dashboard'))

    users = User.query.all()
    for user in users:
        user.salary = user.get_salary(current_key)
        user.tax_percentage = user.get_tax_percentage(current_key)

    return render_template('staff_dashboard.html', users=users, tax_form=tax_form)

def calculate_and_update_invoices():
    current_key = DESKey.get_current_key()
    users = User.query.all()
    for user in users:
        salary = user.get_salary(current_key)
        tax_percentage = user.get_tax_percentage(current_key)
        if salary is not None and tax_percentage is not None:
            # Perform calculation and update invoice logic here
            pass


@app.route('/user_dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    user_id = session.get('user_id')  # Retrieve user ID from session
    if not user_id:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    current_key = DESKey.get_current_key()
    user.salary = user.get_salary(current_key)
    user.tax_percentage = user.get_tax_percentage(current_key)
    invoices = Invoice.query.filter_by(user_id=user_id).all()
    payments = Payment.query.filter_by(user_id=user_id).all()
    payment_form = PaymentForm()
    salary_form = SalaryForm()
    if salary_form.validate_on_submit():
        salary = salary_form.salary.data
        user.set_salary(salary, current_key)
        db.session.commit()
        flash('Salary updated successfully', 'success')
        return redirect(url_for('user_dashboard'))

    #user.salary = user.get_salary(current_key)
    #return render_template('user_dashboard.html', user=user, salary_form=salary_form)

    if payment_form.validate_on_submit():
        payment_amount = payment_form.amount.data
        if payment_amount <= 0:
            flash('Payment amount must be greater than zero. Please enter a valid amount.', 'danger')
        else:
            invoice_id = request.form['invoice_id']
            invoice = Invoice.query.get(invoice_id)
            if invoice and invoice.user_id == user_id:
                invoice.amount_due -= payment_amount
                new_payment = Payment(
                    invoice_id=invoice_id,
                    user_id=user_id,
                    amount=payment_amount,
                    payment_details=payment_form.payment_details.data
                )
                db.session.add(new_payment)
                db.session.commit()
                flash('Payment successful!', 'success')
                return redirect(url_for('user_dashboard'))
    return render_template('user_dashboard.html', user=user, payment_form=payment_form, salary_form=salary_form, invoices=invoices, payments=payments)


@app.route('/add_invoice', methods=['GET', 'POST'])
@login_required
def add_invoice():
    form = InvoiceForm()
    if form.validate_on_submit():
        new_invoice = Invoice(
            user_id=form.user_id.data,
            encrypted_invoice=form.encrypted_invoice.data.encode(),
            signature=form.signature.data.encode(),
            amount_due=form.amount_due.data
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
            existing_invoice = Invoice.query.filter_by(user_id=user.id).first()
            if existing_invoice:
                existing_invoice.amount_due = tax_amount
            else:
                new_invoice = Invoice(
                    user_id=user.id,
                    encrypted_invoice=b'',  # You can replace this with actual encrypted data
                    signature=b'',  # You can replace this with actual signature
                    amount_due=tax_amount
                )
                db.session.add(new_invoice)
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