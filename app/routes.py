from flask import render_template, redirect, url_for, flash, request, session
from app import app, db
from app.models import User, Invoice, Payment
from app.forms import TaxRecordForm, UserForm, PaymentForm

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
            if role == 'Sysadmin':
                return redirect(url_for('sysadmin_dashboard'))
            elif role == 'Staff':
                return redirect(url_for('staff_dashboard'))
            elif role == 'User':
                return redirect(url_for('user_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username, password, and role', 'danger')
    return render_template('login.html')

@app.route('/sysadmin_dashboard')
def sysadmin_dashboard():
    users = User.query.all()
    return render_template('sysadmin_dashboard.html', users=users)

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

@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    user_id = session.get('user_id')  # Retrieve user ID from session
    if not user_id:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    
    invoices = Invoice.query.filter_by(user_id=user_id).all()
    form = PaymentForm()
    if form.validate_on_submit():
        new_payment = Payment(
            invoice_id=request.form['invoice_id'],
            user_id=user_id,
            amount=form.amount.data,
            payment_details=form.payment_details.data
        )
        db.session.add(new_payment)
        db.session.commit()
        flash('Payment successful!', 'success')
        return redirect(url_for('user_dashboard'))
    return render_template('user_dashboard.html', form=form, invoices=invoices)

   
@app.route('/staff_dashboard', methods=['GET', 'POST'])
def staff_dashboard():
    form = TaxRecordForm()
    if form.validate_on_submit():
        full_name = form.full_name.data
        tax_id = form.tax_id.data
        address = form.address.data
        city = form.city.data
        state = form.state.data
        postal_code = form.postal_code.data
        annual_income = form.annual_income.data
        income_sources = form.income_sources.data
        deductions = form.deductions.data
        deduction_details = form.deduction_details.data
        tax_rate = form.tax_rate.data
        calculated_tax = form.calculated_tax.data
        # Here you can add logic to save the data to the database
        flash('Tax record updated successfully!', 'success')
        return redirect(url_for('staff_dashboard'))
    return render_template('staff_dashboard.html', form=form)


@app.route('/logout')
def logout():
    return redirect(url_for('login'))
