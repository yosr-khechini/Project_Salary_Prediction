import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Employee
from werkzeug.security import generate_password_hash
from datetime import datetime

if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        try:
            # Vérifier/créer l'employé
            emp = Employee.query.filter_by(matricule=15).first()

            if not emp:
                emp = Employee(
                    matricule=15,
                    first_name="Test",
                    last_name="Manager",
                    age=35,
                    position="MANAGER",
                    departement="HR",
                    salary=50000.0,
                    date_joined=datetime.now().date()
                )
                db.session.add(emp)
                db.session.commit()
                print("✅ Employé créé avec matricule 15")
            else:
                print("ℹ️ Employé avec matricule 15 existe déjà")

            # Vérifier/créer l'utilisateur
            existing = User.query.filter_by(username='test1').first()
            if existing:
                print("⚠️ Utilisateur test1 existe déjà")
            else:
                user = User(
                    username='test1',
                    email_adress='test1@manager.tn',
                    password_hash=generate_password_hash('testing1'),
                    matricule=15
                )
                db.session.add(user)
                db.session.commit()
                print("✅ Utilisateur test1 créé avec succès")
                print("   Username: test1")
                print("   Password: testing1")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur: {str(e)}")
            import traceback
            traceback.print_exc()