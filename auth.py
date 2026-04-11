from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from forms import LoginForm, RegisterForm
from models import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = db.session.execute(
            db.select(User).where(User.email == form.email.data)
        ).scalar_one_or_none()

        if existing_user:
            flash("You've already signed up with that email. Log in instead.")
            return redirect(url_for("auth.login"))

        hashed_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8,
        )

        new_user = User(
            email=form.email.data,
            password=hashed_password,
            name=form.name.data,
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.execute(
            db.select(User).where(User.email == form.email.data)
        ).scalar_one_or_none()

        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, form.password.data):
            flash("Password incorrect, please try again.")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("get_all_posts"))

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))
