from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit
from app import app, db
from app.models import User
from app.forms import LoginForm

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


@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template("index.html", title="Home", posts=test_posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Redirect to index if already logged in
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    # Otherwise create, validate, and submit the form
    form = LoginForm()
    if form.validate_on_submit():
        user: User = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )

        # If user does not exist or wrong password, flash message
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))

        # Login user with flask-login login_user function
        login_user(user, remember=form.remember_me.data)

        # Return to original page or index
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)

    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
