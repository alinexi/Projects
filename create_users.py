# create_users.py
from app import app, db
from app.models import User

def create_users():
    with app.app_context():
        # Create Sysadmin user
        sysadmin = User(username='sysadmin', password='123', role='Sysadmin')
        
        # Create Staff user
        staff = User(username='staff', password='123', role='Staff')
        
        # Create regular User
        user = User(username='user', password='123', role='User')

        # Add users to the session and commit to the database
        db.session.add(sysadmin)
        db.session.add(staff)
        db.session.add(user)
        db.session.commit()

        print("Users created successfully!")

if __name__ == '__main__':
    create_users()
