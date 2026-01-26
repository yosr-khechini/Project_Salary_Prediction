from flask import Blueprint, request, jsonify
from app.models import db, Employee
from datetime import datetime

employees_bp = Blueprint('employees', __name__, url_prefix='/api/employees')

# GET tous les employés
@employees_bp.route('', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    return jsonify([emp.to_dict() for emp in employees]), 200

# GET un employé par matricule
@employees_bp.route('/<int:matricule>', methods=['GET'])
def get_employee(matricule):
    employee = Employee.query.get_or_404(matricule)
    return jsonify(employee.to_dict()), 200

# POST créer un employé
@employees_bp.route('', methods=['POST'])
def create_employee():
    data = request.get_json()

    employee = Employee(
        matricule=data.get('matricule'),
        first_name=data['first_name'],
        last_name=data['last_name'],
        age=data.get('age'),
        position=data.get('position'),
        salary=data.get('salary'),
        departement=data.get('departement'),
        indemnite1=data.get('indemnite1', 0),
        indemnite2=data.get('indemnite2', 0),
        date_joined=datetime.strptime(data['date_joined'], '%Y-%m-%d').date() if data.get('date_joined') else None
    )

    db.session.add(employee)
    db.session.commit()

    return jsonify(employee.to_dict()), 201

# PUT mettre à jour un employé
@employees_bp.route('/<int:matricule>', methods=['PUT'])
def update_employee(matricule):
    employee = Employee.query.get_or_404(matricule)
    data = request.get_json()

    employee.first_name = data.get('first_name', employee.first_name)
    employee.last_name = data.get('last_name', employee.last_name)
    employee.age = data.get('age', employee.age)
    employee.position = data.get('position', employee.position)
    employee.salary = data.get('salary', employee.salary)
    employee.departement = data.get('departement', employee.departement)
    employee.indemnite1 = data.get('indemnite1', employee.indemnite1)
    employee.indemnite2 = data.get('indemnite2', employee.indemnite2)

    db.session.commit()

    return jsonify(employee.to_dict()), 200

# PATCH terminer un employé (date de départ)
@employees_bp.route('/<int:matricule>/terminate', methods=['PATCH'])
def terminate_employee(matricule):
    employee = Employee.query.get_or_404(matricule)
    data = request.get_json()

    employee.date_left = datetime.strptime(data['date_left'], '%Y-%m-%d').date() if data.get('date_left') else datetime.now().date()

    db.session.commit()

    return jsonify(employee.to_dict()), 200

# DELETE supprimer un employé
@employees_bp.route('/<int:matricule>', methods=['DELETE'])
def delete_employee(matricule):
    employee = Employee.query.get_or_404(matricule)
    db.session.delete(employee)
    db.session.commit()

    return jsonify({'message': 'Employé supprimé'}), 200