from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from app import db


class Employee(db.Model):
    __tablename__ = 'employees'

    matricule = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    position = db.Column(db.String(50))
    salary = db.Column(db.Numeric(10, 2))
    departement = db.Column(db.String(50))
    indemnite1 = db.Column(db.Numeric(10, 2))
    indemnite2 = db.Column(db.Numeric(10, 2))
    date_joined = db.Column(db.Date)
    date_left = db.Column(db.Date)
    def to_dict(self):
        return {
            'matricule': self.matricule,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'position': self.position,
            'salary': float(self.salary) if self.salary else None,
            'departement': self.departement,
            'indemnite1': float(self.indemnite1) if self.indemnite1 else None,
            'indemnite2': float(self.indemnite2) if self.indemnite2 else None,
            'date_joined': self.date_joined.isoformat() if self.date_joined else None,
            'date_left': self.date_left.isoformat() if self.date_left else None
        }

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email_adress = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    #role = db.Column(db.String(20), default='manager')
    matricule = db.Column(db.Integer, db.ForeignKey('employees.matricule'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', backref='user', lazy=True)

    @property
    def is_active(self):
        """Vérifie si l'utilisateur est actif"""
        if self.employee:
            return self.employee.date_left is None
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)