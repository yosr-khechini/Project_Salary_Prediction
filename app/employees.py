from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
import html
from app import db
from app.models import Employee

employees = Blueprint('employees', __name__, url_prefix='/employees')

def _sanitize_input(value: str) -> str:
    """Sanitize user input to prevent XSS attacks"""
    if not value:
        return ''
    return html.escape(value.strip())

# --- List Employees ---
@employees.route("/")
@login_required
def list_employees():
    search = _sanitize_input(request.args.get('search', ''))
    departement = _sanitize_input(request.args.get('departement', ''))
    status = _sanitize_input(request.args.get('status', ''))
    year = request.args.get('year', type=int)

    query = Employee.query

    if search:
        query = query.filter(
            (Employee.first_name.ilike(f'%{search}%')) |
            (Employee.last_name.ilike(f'%{search}%')) |
            (Employee.matricule.ilike(f'%{search}%'))
        )

    if departement:
        query = query.filter(db.func.upper(Employee.departement) == departement.upper())

    if status == 'active':
        query = query.filter(Employee.date_left.is_(None))
    elif status == 'terminated':
        query = query.filter(Employee.date_left.isnot(None))

    if year:
        query = query.filter(db.extract('year', Employee.date_joined) == year)

    all_employees = query.all()

    # Get distinct departments (uppercase)
    departments = db.session.query(
        db.func.upper(Employee.departement)
    ).distinct().filter(
        Employee.departement.isnot(None)
    ).order_by(db.func.upper(Employee.departement)).all()
    departments = [dept[0] for dept in departments if dept[0]]

    # Get distinct years from date_joined
    years = db.session.query(
        db.extract('year', Employee.date_joined).label('year')
    ).distinct().filter(
        Employee.date_joined.isnot(None)
    ).order_by(db.text('year DESC')).all()
    years = [int(year[0]) for year in years]

    return render_template("employees.html",
                         employees=all_employees,
                         departments=departments,
                         years=years)

# --- Add Employee ---
@employees.route("/add", methods=["GET", "POST"])
@login_required
def add_employee():
    if request.method == "POST":
        try:
            first_name = _sanitize_input(request.form.get("first_name", ""))
            last_name = _sanitize_input(request.form.get("last_name", ""))

            if not first_name or not last_name:
                raise ValueError("First name and last name are required")

            age_raw = _sanitize_input(request.form.get("age", ""))
            age = int(age_raw) if age_raw else None
            if age and (age < 18 or age > 100):
                raise ValueError("Age must be between 18 and 100")

            matricule_raw = _sanitize_input(request.form.get("matricule", ""))
            matricule = float(matricule_raw) if matricule_raw else None
            if matricule and matricule < 0:
                raise ValueError("matricule cannot be negative")

            salary_raw = _sanitize_input(request.form.get("salary", ""))
            salary = float(salary_raw) if salary_raw else None
            if salary and salary < 0:
                raise ValueError("Salary cannot be negative")

            indemnite1_raw = _sanitize_input(request.form.get("indemnite1", ""))
            indemnite1 = float(indemnite1_raw) if indemnite1_raw else None
            if indemnite1 and indemnite1 < 0:
                raise ValueError("Indemnite cannot be negative")

            indemnite2_raw = _sanitize_input(request.form.get("indemnite2", ""))
            indemnite2 = float(indemnite2_raw) if indemnite2_raw else None
            if indemnite2 and indemnite2 < 0:
                raise ValueError("Indemnite cannot be negative")

            date_joined_raw = _sanitize_input(request.form.get("date_joined", ""))
            date_joined = datetime.strptime(date_joined_raw, "%Y-%m-%d").date() if date_joined_raw else None

            departement_input = _sanitize_input(request.form.get("departement", ""))
            departement = departement_input.upper() if departement_input else None

            emp = Employee(
                first_name=first_name,
                last_name=last_name,
                age=age,
                position=_sanitize_input(request.form.get("position", "")) or None,
                departement=departement,
                salary=salary,
                indemnite1=indemnite1,
                indemnite2=indemnite2,
                date_joined=date_joined,
                matricule=matricule
            )

            db.session.add(emp)
            db.session.commit()
            flash("Employee added successfully", "success")
            return redirect(url_for("employees.list_employees"))

        except ValueError as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding employee: {str(e)}", "error")

    return render_template("add_employee.html")

# --- Edit Employee ---
@employees.route("/edit/<int:matricule>", methods=["GET", "POST"])
@login_required
def edit_employee(matricule):
    employee = Employee.query.get_or_404(matricule)

    if employee.date_left:
        flash("Cannot edit terminated employee", "error")
        return redirect(url_for("employees.list_employees"))

    if request.method == "POST":
        try:
            first_name = _sanitize_input(request.form.get("first_name", ""))
            last_name = _sanitize_input(request.form.get("last_name", ""))

            if not first_name or not last_name:
                raise ValueError("First name and last name are required")

            employee.first_name = first_name
            employee.last_name = last_name

            age_raw = _sanitize_input(request.form.get("age", ""))
            age = int(age_raw) if age_raw else None
            if age and (age < 18 or age > 100):
                raise ValueError("Age must be between 18 and 100")
            employee.age = age

            employee.position = _sanitize_input(request.form.get("position", "")) or None

            departement_input = _sanitize_input(request.form.get("departement", ""))
            employee.departement = departement_input.upper() if departement_input else None

            salary_raw = _sanitize_input(request.form.get("salary", ""))
            salary = float(salary_raw) if salary_raw else None
            if salary and salary < 0:
                raise ValueError("Salary cannot be negative")
            employee.salary = salary

            salary_raw = _sanitize_input(request.form.get("salary", ""))
            salary = float(salary_raw) if salary_raw else None
            if salary and salary < 0:
                raise ValueError("Salary cannot be negative")
            employee.salary = salary

            indemnite1_raw = _sanitize_input(request.form.get("indemnite1", ""))
            indemnite1 = float(indemnite1_raw) if salary_raw else None
            if indemnite1 and indemnite1 < 0:
                raise ValueError("indemnite cannot be negative")
            employee.indemnite1 = indemnite1

            indemnite2_raw = _sanitize_input(request.form.get("indemnite2", ""))
            indemnite2= float(indemnite2_raw) if salary_raw else None
            if indemnite2 and indemnite2 < 0:
                raise ValueError("indemnite cannot be negative")
            employee.indemnite2= indemnite2

            date_joined_raw = _sanitize_input(request.form.get("date_joined", ""))
            employee.date_joined = datetime.strptime(date_joined_raw, "%Y-%m-%d").date() if date_joined_raw else None

            db.session.commit()
            flash("Employee updated successfully", "success")
            return redirect(url_for("employees.list_employees"))

        except ValueError as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating employee: {str(e)}", "error")

    return render_template("edit_employee.html", employee=employee)

# --- Terminate Employee ---
@employees.route("/terminate/<int:matricule>", methods=["GET", "POST"])
@login_required
def terminate_employee(matricule):
    employee = Employee.query.get_or_404(matricule)

    if employee.date_left:
        flash("Employee is already terminated", "warning")
        return redirect(url_for("employees.list_employees"))

    if request.method == "POST":
        try:
            date_left_raw = _sanitize_input(request.form.get("date_left", ""))
            if not date_left_raw:
                raise ValueError("Termination date is required")

            date_left = datetime.strptime(date_left_raw, "%Y-%m-%d").date()

            if employee.date_joined and date_left < employee.date_joined:
                raise ValueError("Termination date cannot be before hire date")

            employee.date_left = date_left
            db.session.commit()
            flash("Employee terminated successfully", "success")
            return redirect(url_for("employees.list_employees"))

        except ValueError as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Error terminating employee: {str(e)}", "error")

    return render_template("terminate_employee.html", employee=employee)