import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Employee

if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        # 1. Créer l'employé d'abord
        existing_employee = Employee.query.filter_by(matricule='001').first()
        if not existing_employee:
            employee = Employee(
                matricule='001',
                first_name='Test',
                last_name='User',
                position='Admin',
                departement='IT'
            )
            db.session.add(employee)
            db.session.commit()
            print(f"Employé créé : {employee.first_name} {employee.last_name}")

        # 2. Créer l'utilisateur ensuite
        existing_user = User.query.filter_by(username='test1').first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()

        user = User(
            username='test1',
            email_adress='test1@example.com',
            matricule='001'
        )
        user.set_password('password')

        db.session.add(user)
        db.session.commit()

        print(f"Utilisateur créé : {user.username}")
        print(f"Email : {user.email_adress}")
        print("Mot de passe : password")