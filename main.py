"""
Project: Blog From Day 69
File: main.py
Description:
This module defines the Flask application for the blog project, including
configuration, database models, authentication, and HTTP routes. It wires up
extensions (SQLAlchemy, Flask-Login, Bootstrap5, CKEditor, and Gravatar),
declares the User, BlogPost, and Comment tables with their relationships, and
implements the full set of routes for registration, login/logout, post CRUD,
comment creation/editing/deletion, and static pages. The routing layer renders
Jinja templates and enforces admin-only and comment-owner permissions.
"""

# Standard library imports for dates and decorators.
from datetime import date
from functools import wraps

# Third-party imports for Flask, extensions, and utilities.
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# SQLAlchemy core and ORM helpers for models and relationships.
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Local form classes used by the route handlers.
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm


# Create the Flask application and configure its secret key.
app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"

# Initialize UI and editor extensions.
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure session-based login management.
login_manager = LoginManager()
login_manager.init_app(app)

# Configure Gravatar so comments display user avatars.
gravatar = Gravatar(
    app,
    size=100,
    rating="g",
    default="retro",
    force_default=False
)

# Make the gravatar helper available inside Jinja templates.
app.jinja_env.globals["gravatar"] = gravatar


# Base class for SQLAlchemy models.
class Base(DeclarativeBase):
    pass


# Configure and initialize the database connection.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Blog post model with author and comment relationships.
class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)

    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="posts")

    comments = relationship("Comment", back_populates="parent_post")


# User model for authentication and authored content.
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")


# Comment model tied to both a user and a blog post.
class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="comments")

    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("blog_posts.id"), nullable=False)
    parent_post = relationship("BlogPost", back_populates="comments")


# Register the user loader callback for Flask-Login.
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Ensure the database tables exist on startup.
with app.app_context():
    db.create_all()


# Decorator to enforce admin-only access.
def admin_only(func):
    """
    Project: Blog From Day 69
    File: main.py
    Description:
    Guard for admin-only routes that allows access only to the first registered
    user (id == 1). Any other user, or unauthenticated requests, receive a 403
    Forbidden response to prevent unauthorized post management.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.id == 1:
            return func(*args, **kwargs)
        return abort(403)

    return wrapper


# Helper to verify the current user owns a comment or is admin.
def comment_owner_or_admin(comment: Comment) -> bool:
    return (
        current_user.is_authenticated
        and (current_user.id == 1 or comment.author_id == current_user.id)
    )


# Registration route: create a new user account.
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = db.session.execute(
            db.select(User).where(User.email == form.email.data)
        ).scalar_one_or_none()

        if existing_user:
            flash("You've already signed up with that email. Log in instead.")
            return redirect(url_for("login"))

        hashed_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )

        new_user = User(
            email=form.email.data,
            password=hashed_password,
            name=form.name.data
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=form)


# Login route: authenticate existing users.
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.execute(
            db.select(User).where(User.email == form.email.data)
        ).scalar_one_or_none()

        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for("login"))

        if not check_password_hash(user.password, form.password.data):
            flash("Password incorrect, please try again.")
            return redirect(url_for("login"))

        login_user(user)
        return redirect(url_for("get_all_posts"))

    return render_template("login.html", form=form)


# Logout route: clear the user session.
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))


# Home route: list all blog posts.
@app.route("/")
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# Post detail route: display a post and handle new comments.
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=form.comment_text.data,
            author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_id))

    return render_template("post.html", post=requested_post, form=form)


# Comment edit route: allow owners/admin to update comment text.
@app.route("/edit-comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    if not current_user.is_authenticated:
        flash("You need to login to edit comments.")
        return redirect(url_for("login"))

    comment = db.get_or_404(Comment, comment_id)

    if not comment_owner_or_admin(comment):
        return abort(403)

    form = CommentForm()

    if form.validate_on_submit():
        comment.text = form.comment_text.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=comment.post_id))

    # Pre-fill the editor on GET
    form.comment_text.data = comment.text
    return render_template("edit-comment.html", form=form, comment=comment)


# Comment delete route: allow owners/admin to remove a comment.
@app.route("/delete-comment/<int:comment_id>")
def delete_comment(comment_id):
    if not current_user.is_authenticated:
        flash("You need to login to delete comments.")
        return redirect(url_for("login"))

    comment = db.get_or_404(Comment, comment_id)

    if not comment_owner_or_admin(comment):
        return abort(403)

    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for("show_post", post_id=post_id))


# New post route: admin-only post creation.
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            date=date.today().strftime("%B %d, %Y"),
            author=current_user
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form)


# Edit post route: admin-only updates to existing posts.
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)

    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )

    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True)


# Delete post route: admin-only removal of posts.
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


# Static about page.
@app.route("/about")
def about():
    return render_template("about.html")


# Static contact page.
@app.route("/contact")
def contact():
    return render_template("contact.html")


# Development entry point.
if __name__ == "__main__":
    app.run(debug=True, port=5002)
