from datetime import date
from functools import wraps

from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import LoginManager, current_user

import config
from auth import auth_bp
from forms import CommentForm, CreatePostForm
from models import BlogPost, Comment, User, db

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URI

ckeditor = CKEditor(app)
Bootstrap5(app)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

gravatar = Gravatar(
    app,
    size=100,
    rating="g",
    default="retro",
    force_default=False,
)
app.jinja_env.globals["gravatar"] = gravatar

app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def admin_only(func):
    """Restrict access to user id == 1 (first registered user is admin)."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.id == 1:
            return func(*args, **kwargs)
        return abort(403)
    return wrapper


def comment_owner_or_admin(comment: Comment) -> bool:
    return (
        current_user.is_authenticated
        and (current_user.id == 1 or comment.author_id == current_user.id)
    )


@app.route("/")
def get_all_posts():
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("auth.login"))

        new_comment = Comment(
            text=form.comment_text.data,
            author=current_user,
            parent_post=requested_post,
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_id))

    return render_template("post.html", post=requested_post, form=form)


@app.route("/edit-comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    if not current_user.is_authenticated:
        flash("You need to login to edit comments.")
        return redirect(url_for("auth.login"))

    comment = db.get_or_404(Comment, comment_id)

    if not comment_owner_or_admin(comment):
        return abort(403)

    form = CommentForm()

    if form.validate_on_submit():
        comment.text = form.comment_text.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=comment.post_id))

    form.comment_text.data = comment.text
    return render_template("edit-comment.html", form=form, comment=comment)


@app.route("/delete-comment/<int:comment_id>")
def delete_comment(comment_id):
    if not current_user.is_authenticated:
        flash("You need to login to delete comments.")
        return redirect(url_for("auth.login"))

    comment = db.get_or_404(Comment, comment_id)

    if not comment_owner_or_admin(comment):
        return abort(403)

    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for("show_post", post_id=post_id))


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
            author=current_user,
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)

    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body,
    )

    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
