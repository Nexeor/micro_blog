from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit
from datetime import datetime, timezone

from app import app, db
from app.models import User
from app.forms import LoginForm, RegistrationForm, EditProfileForm

test_user = {"username": "Tim"}
test_posts = [
    {
        "author": {"username": "Tim"},
        "post_id": 1,
        "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
        "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto",
    },
    {
        "author": {"username": "Tim"},
        "post_id": 2,
        "title": "qui est esse",
        "body": "est rerum tempore vitae\nsequi sint nihil reprehenderit dolor beatae ea dolores neque\nfugiat blanditiis voluptate porro vel nihil molestiae ut reiciendis\nqui aperiam non debitis possimus qui neque nisi nulla",
    },
    {
        "author": {"username": "Tim"},
        "post_id": 3,
        "title": "ea molestias quasi exercitationem repellat qui ipsa sit aut",
        "body": "et iusto sed quo iure\nvoluptatem occaecati omnis eligendi aut ad\nvoluptatem doloribus vel accusantium quis pariatur\nmolestiae porro eius odio et labore et velit aut",
    },
]


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template("index.html", title="Home", posts=test_posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Use flask-login to check if user is authenticated
    # Redirect to index if already logged in
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    # Otherwise create, validate, and submit the form
    form = LoginForm()
    if form.validate_on_submit():
        user: User = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )

        # If user does not exist or wrong password, flash message and redirect to login
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))

        # Login user with flask-login
        login_user(user, remember=form.remember_me.data)

        # If request provided next page, go there
        # Otherwise, redirect to index
        # Also check that for relative URL to protect against foreign next
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)

    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registed user!")
        # Login user with flask-login
        login_user(user, remember=False)
        return redirect(url_for("index"))
    return render_template("register.html", title="Register", form=form)


@app.route("/user/<username>")
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [{"author": user, "body": "dummy 1"}, {"author": user, "body": "dummy 2"}]
    return render_template("user.html", user=user, posts=posts)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    # Submit: Overwrite username/about_me and commit
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    # If GET, display the username/about_me fetched from db
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title="Edit profile", form=form)
