import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Employee

if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        print("\n=== Table Users ===")
        users = User.query.all()
        if users:
            for user in users:
                print(f"ID: {user.id} | Username: {user.username} | Email: {user.email_adress} | Matricule: {user.matricule}")
        else:
            print("Aucun utilisateur trouvé")

        print("\n=== Table Employees ===")
        employees = Employee.query.all()
        if employees:
            for emp in employees:
                print(f"Matricule: {emp.matricule} | Nom: {emp.first_name} {emp.last_name} | Poste: {emp.position} | Département: {emp.departement}")
        else:
            print("Aucun employé trouvé")