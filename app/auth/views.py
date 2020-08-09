from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import (
    LoginForm,
    RegistrationForm,
    ChangePasswordForm,
    PasswordResetRequestForm,
    PasswordResetForm,
    ChangeEmailForm,
)
from werkzeug.utils import secure_filename
import boto3
from mixpanel import Mixpanel
mp = Mixpanel('18e48de5bfb0ffaa3e4f35e6455abad7')

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email").lower()).first()
        if user is not None and user.verify_password(request.form.get("password")):
            login_user(user, request.form.get("remember_me"))
            print('here1')
            next = request.args.get("next")
            print('here2')
            if next is None or not next.startswith("/"):
                print('here3')
                next = url_for("main.index")
            flash("Logged in")
            print('here4')
            mp.track(user.id, 'Logged in')
            return redirect(next)
        flash("Invalid email or password.")
    return render_template("auth/login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        f = form.image.data
        filename = ""
        if f.filename != "":
            user_id = User.query.order_by(User.id.desc()).first().id + 1
            filename = str(user_id) + secure_filename(f.filename)
            s3_client = boto3.resource("s3")
            bucket = s3_client.Bucket("groovespotimages")
            bucket.Object(filename).put(Body=f)
        else:
            filename = "profile-img.png"

        user = User(
            email=form.email.data.lower(),
            username=form.username.data,
            password=form.password.data,
            profile_pic_filename=filename,
        )
        db.session.add(user)
        db.session.commit()
        flash("Thanks for registering!")
        old_id = current_user.id
        login_user(user)
        mp.merge('e4dcb100b38961063280f0ddf0879091',str(old_id), str(current_user.id))
        mp.people_set(current_user.id, {'email': user.email, 'username': user.username})
        mp.track(current_user.id, 'Registered')
        return redirect(url_for("main.index"))
    else:
        for error in form.errors:
            flash(str(error) + ": " + str(form.errors[error][0]))
    return render_template("auth/register.html", form=form)


@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(
                user.email,
                "Reset Your Password",
                "auth/email/reset_password",
                user=user,
                token=token,
            )
        flash(
            "An email with instructions to reset your password has been " "sent to you."
        )
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)
