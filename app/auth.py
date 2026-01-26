from flask import Blueprint, request, redirect, url_for, flash, render_template, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user
from urllib.parse import urlparse, urljoin
import html
from app import db
from app.models import User, Employee

auth = Blueprint('auth', __name__)

def _is_safe_next_url(target: str) -> bool:
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target or ''))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def _is_valid_email(email: str) -> bool:
    return bool(email) and '@' in email and '.' in email.split('@')[-1]

def _is_valid_username(username: str) -> bool:
    return bool(username) and 3 <= len(username) <= 64

def _is_strong_password(password: str) -> bool:
    return bool(password) and len(password) >= 8

def _sanitize_input(value: str) -> str:
    """Sanitize user input to prevent XSS attacks"""
    if not value:
        return ''
    return html.escape(value.strip())


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        print(f"Tentative de connexion : username={username}")  # Debug

        user = User.query.filter_by(username=username).first()

        print(f"Utilisateur trouvé : {user}")  # Debug

        if user:
            print(f"Hash stocké : {user.password_hash}")  # Debug
            print(f"Vérification : {user.check_password(password)}")  # Debug

        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for('main.home'))
        else:
            flash('Identifiants invalides')

    return render_template('login.html')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    # Sanitize all inputs
    matricule_raw = _sanitize_input(request.form.get('matricule') or '')
    username = _sanitize_input(request.form.get('username') or '')
    email = _sanitize_input(request.form.get('email') or '').lower()
    password = request.form.get('password') or ''

    if not all([matricule_raw, username, email, password]):
        flash('Tous les champs sont requis.')
        return render_template('signup.html'), 400

    if not _is_valid_username(username):
        flash('Nom utilisateur invalide (3-64 caractères).')
        return render_template('signup.html'), 400

    if not _is_valid_email(email):
        flash('Email invalide.')
        return render_template('signup.html'), 400

    if not _is_strong_password(password):
        flash('Le mot de passe doit contenir au moins 8 caractères.')
        return render_template('signup.html'), 400

    # Validate matricule
    try:
        matricule_int = int(matricule_raw)
    except ValueError:
        flash('Le matricule doit être un nombre.')
        return render_template('signup.html'), 400

    # Check if employee exists
    emp = Employee.query.filter_by(matricule=matricule_int).first()
    if not emp:
        flash("Matricule introuvable. Seuls les employés enregistrés peuvent créer un compte.")
        return render_template('signup.html'), 403

    # Check if employee is terminated
    if emp.date_left:
        flash("Accès refusé. Cet employé n'est plus actif.")
        return render_template('signup.html'), 403

    # Check department and position (case-insensitive)
    dept = (emp.departement or '').strip().upper()
    pos = (emp.position or '').strip().upper()

    if dept != 'HR' or pos != 'MANAGER':
        flash('Accès réservé aux HR Managers uniquement.')
        return render_template('signup.html'), 403

    # Check if user already exists
    exists = User.query.filter(
        or_(User.username == username, User.email_adress == email)
    ).first()
    if exists:
        flash('Nom utilisateur ou email déjà utilisé.')
        return render_template('signup.html'), 409

    try:
        user = User(
            username=username,
            email_adress=email,
            password_hash=generate_password_hash(password),
            #role='manager',
            matricule=emp.matricule
        )
        db.session.add(user)
        db.session.commit()
        flash('Compte créé avec succès. Vous pouvez maintenant vous connecter.')
        return redirect(url_for('auth.login'))
    except IntegrityError:
        db.session.rollback()
        flash('Erreur : contrainte dunicité violée.')
        return render_template('signup.html'), 409
    except Exception:
        db.session.rollback()
        current_app.logger.exception('Erreur interne pendant le signup')
        flash('Erreur interne du serveur.')
        return render_template('signup.html'), 500