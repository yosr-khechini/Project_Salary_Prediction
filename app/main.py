from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
import html
from .models import Employee

# Blueprint principal
main = Blueprint('main', __name__)

def _sanitize_input(value: str) -> str:
    """Sanitize user input to prevent XSS attacks"""
    if not value:
        return ''
    return html.escape(value.strip())

# --- Home ---
@main.route('/')
@login_required
def index():
    return render_template('index.html')

@main.route("/home", methods=["GET"])
@login_required
def home():
    return render_template("home.html", user=current_user)

# --- History ---
@main.route("/history", methods=["GET"], strict_slashes=False)
@login_required
def history():
    return render_template("history.html", user=current_user)

# --- Predict ---
@main.route("/predict", methods=["GET", "POST"], strict_slashes=False)
@login_required
def predict():
    salary = None
    if request.method == "POST":
        try:
            experience_raw = _sanitize_input(request.form.get("experience", "0"))
            experience = float(experience_raw)
        except (TypeError, ValueError):
            flash("Expérience invalide.", "error")
            experience = 0.0

        experience = max(0.0, min(experience, 50.0))  # Limite à 50 ans d'expérience

        education = _sanitize_input(request.form.get("education", "Bachelor")).strip()
        allowed_educations = {"Bachelor", "Master", "PhD"}
        if education not in allowed_educations:
            flash("Niveau d'éducation invalide, utilisation de 'Bachelor'.", "warning")
            education = "Bachelor"

        base_salary = 30000.0
        multiplier = {"Bachelor": 1.0, "Master": 1.2, "PhD": 1.5}
        salary = round(base_salary + experience * 2000.0 * multiplier[education], 2)

    return render_template("prediction.html", user=current_user, salary=salary)

# --- Profile ---
@main.route("/profile", methods=["GET"])
@login_required
def profile():
    employee = Employee.query.filter_by(matricule=current_user.matricule).first()
    if not employee:
        flash("Aucun employé trouvé pour cet utilisateur.", "error")
        return render_template('error.html', message="Employee not found"), 404

    return render_template(
        "profile.html",
        username=current_user.username,
        email=current_user.email_adress,
        first_name=employee.first_name,
        last_name=employee.last_name,
        position=employee.position,
        departement=employee.departement,
        salary=employee.salary  # Correction: 'salary' au lieu de 'salaire'
    )

# --- Error handler ---
@main.app_errorhandler(500)
def handle_500(err):
    return render_template('error.html', message=str(err)), 500