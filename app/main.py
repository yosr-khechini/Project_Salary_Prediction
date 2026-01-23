from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route("/", methods=["GET", "POST"])
@main.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@main.route("/history", strict_slashes=False)
def history():
    return render_template("history.html")

@main.route("/predict", methods=["GET", "POST"], strict_slashes=False)
@login_required
def predict():
    if request.method == "POST":
        experience = float(request.form["experience"])
        education = request.form["education"]
        base_salary = 30000
        multiplier = {"Bachelor": 1.0, "Master": 1.2, "PhD": 1.5}
        predicted_salary = base_salary + experience * 2000 * multiplier[education]
        return render_template("predict.html", user=current_user, salary=predicted_salary)

    return render_template("predict.html", user=current_user)

@main.route("/test")
def test():
    return "<h1>Test route works!</h1>"

@main.route("/profile")
@login_required
def profile():
    return render_template("profile.html", name=current_user.name)
@main.app_errorhandler(500)
def internal_error(error):
    return "<h1>Something went wrong. Check your terminal for details.</h1>", 500