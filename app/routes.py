from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.models import User, TaxRecord, Invoice
from app.forms import TaxRecordForm, UserForm

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

@app.route('/delete_user/<int=user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('sysadmin_dashboard'))

@app.route('/staff_dashboard', methods=['GET', 'POST'])
def staff_dashboard():
    form = TaxRecordForm()
    if form.validate_on_submit():
        # Process form data and save to database
        tax_record = TaxRecord(
            user_id=form.user_id.data,
            encrypted_record=form.encrypted_record.data
        )
        db.session.add(tax_record)
        db.session.commit()
        flash('Tax record updated successfully!', 'success')
        return redirect(url_for('staff_dashboard'))
    return render_template('staff_dashboard.html', form=form)

@app.route('/user_dashboard')
def user_dashboard():
    user_id = request.args.get('user_id')
    invoices = Invoice.query.filter_by(user_id=user_id).all()
    return render_template('user_dashboard.html', invoices=invoices)

@app.route('/logout')
def logout():
    return redirect(url_for('login'))
