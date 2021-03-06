from datetime import datetime
from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user, current_user
from . import auth
from . forms import LoginForm, RegistrationForm, EmailForm, PasswordResetForm
from email_token import generate_confirmation_token, confirm_token
from send_user_email import send_email

from .. models import User
from app import db

@auth.route('/register', methods=['POST', 'GET'])
def register_user():
    """
    Handles user registration at /register
    """
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        new_user = User(email=registration_form.email.data, username=registration_form.username.data,
                    first_name=registration_form.first_name.data, last_name=registration_form.last_name.data,
                    profile_pic=registration_form.profile_pic.data,
                    password=registration_form.password.data)
        db.session.add(new_user)
        db.session.commit()
        # Generate token to send user an email asking them to confirm their email
        token = generate_confirmation_token(registration_form.email.data)
        confirmation_url = url_for("auth.confirm_email", token=token, _external=True)
        html = render_template("auth/activate.html", confirmation_url=confirmation_url)
        subject = "Please confirm your email"
        send_email(new_user.email, subject, html)
        login_user(new_user)
        flash('A confirmation email has been sent to {}. Please confirm your email.'.format(new_user.email), 'info')
        return redirect(url_for('auth.unconfirmed'))

    return render_template('auth/register.html', registration_form=registration_form, title="Register")

@auth.route("/confirm/<token>")
@login_required
def confirm_email(token):
    """
    Handles user confirmation email processes
    """
    try:
        email = confirm_token(token)
    except:
        flash("The confirmation link is invalid or has expired", "danger")
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirm_email:
        flash('Your account has already been confirm. Please login.', 'success')
        return redirect(url_for("auth.user_login"))
    else:
        user.confirm_email=True
        user.confirm_on = datetime.utcnow()
        db.session.commit()
        flash('{}, you have successfully confirm your account. Thank you'.format(user.first_name), 'success')
    return redirect(url_for('campground.list_all_campgrounds'))

@auth.route("/unconfirm")
@login_required
def unconfirmed():
    """
    Handles the unconfirm route /unconfirm if the user is unconfirm
    """
    if current_user.confirm_email:
        return redirect(url_for('home.home_page'))

    return render_template('auth/unconfirm.html')


@auth.route('/login', methods=['POST', 'GET'])
def user_login():
    """
    Handles user login at /account/login
    """
    login_form = LoginForm()
    if login_form.validate_on_submit():
        register_user = User.query.filter_by(email=login_form.email.data).first()
        if register_user is not None and register_user.verify_password(login_form.password.data):
            login_user(register_user)
            return redirect(url_for('home.home_page'))

        else:
            flash("Invalid Credentials. Please provide valid credential to login.", 'danger')
            return redirect(url_for('auth.user_login'))

    return render_template('auth/login.html', login_form=login_form, title="Login")

@auth.route('/resend')
@login_required
def resend_confirmation():
    """
    Handles the resending of user confirmation link if the user didn't
    receive the initial confirmation link at route /account/resend
    """
    token = generate_confirmation_token(current_user.confirm_email)
    confirmation_url = url_for("auth.confirm_email", token=token, _external=True)
    html = render_template("auth/activate.html", confirmation_url=confirmation_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash('A comfirmation email has been sent to {}'.format(current_user.email), 'success')
    return redirect(url_for('auth.unconfirmed'))

@auth.route("/reset", methods=["GET", "POST"])
def reset():
    """
    Handles the reset of a user password by rendering a template that
    gets the user email at /account/reset
	"""
    email_form = EmailForm()
    user = None
    if email_form.validate_on_submit():
        try:
            user = User.query.filter_by(email=email_form.user_email.data).first_or_404()
        except:
            # render the form, the email entered isn't registered
            return render_template('auth/email_reset_form.html', email_form=email_form)
        if user.confirm_email:
            token = generate_confirmation_token(user.email)
            password_reset_url = url_for("auth.reset_with_token", token=token, _external=True)
            html = render_template("auth/reset_link.html", password_reset_url=password_reset_url)
            subject = "Password Change Requested"
            send_email(user.email, subject, html)
            flash('We sent an email to {} with a link to change your password. Please check your inbox for the email.'.format(user.email), "info")
            return redirect(url_for('auth.user_login'))
        else:
            flash("You will need to confirm your account before resetting password", 'success' )
            return redirect(url_for("auth.resend_confirmation"))
    return render_template('auth/email_reset_form.html', email_form=email_form)


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_with_token(token):
	"""
	Handles the reset of a user password with the token that was sent
	to the user at /reset-password/<token>
	"""
	password_form = PasswordResetForm()
	try:
		email = confirm_token(token)
	except:
		return redirect(url_for('auth.login'))
	if password_form.validate_on_submit():
		user = User.query.filter_by(email=email).first_or_404()
		user.password = password_form.password.data
		db.session.add(user)
		db.session.commit()
		flash("You have successfully change your password.", "success")
		return redirect(url_for('auth.user_login'))
	return render_template("auth/password_change_form.html", password_form=password_form, token=token)


@auth.route('/logout')
def user_logout():
    """
    Handles logout for current login users
    """
    flash(current_user.username + ', you have succesfully logout', 'success')
    logout_user()
    return redirect(url_for('auth.user_login'))
