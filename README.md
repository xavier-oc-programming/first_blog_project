# Xavier's Blog — Day 69

Flask blog with user authentication, admin-only post management, and per-user comment ownership.

Users can register, log in, and leave rich-text comments on posts. The first registered account becomes the admin and gains exclusive rights to create, edit, and delete posts. Any authenticated user can edit or delete their own comments; the admin can manage all comments.

## Quick start

```bash
git clone https://github.com/xavier-oc-programming/day-69-blog-users.git
cd day-69-blog-users
pip install -r requirements.txt
cp .env.example .env          # then set SECRET_KEY to any random string
python main.py
```

Open http://127.0.0.1:5002 in your browser.

## Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Home — list all posts |
| GET, POST | `/register` | Register a new account |
| GET, POST | `/login` | Log in |
| GET | `/logout` | Log out |
| GET, POST | `/post/<id>` | Read a post and leave a comment |
| GET, POST | `/edit-comment/<id>` | Edit your own comment (or any, if admin) |
| GET | `/delete-comment/<id>` | Delete your own comment (or any, if admin) |
| GET, POST | `/new-post` | Create a post (admin only) |
| GET, POST | `/edit-post/<id>` | Edit a post (admin only) |
| GET | `/delete/<id>` | Delete a post (admin only) |
| GET | `/about` | About page |
| GET | `/contact` | Contact page (form is decorative in Day 69) |

## File structure

```
main.py              Flask app — setup, route handlers
auth.py              /register, /login, /logout routes (Blueprint)
models.py            SQLAlchemy models: User, BlogPost, Comment
forms.py             WTForms: CreatePostForm, RegisterForm, LoginForm, CommentForm
config.py            Constants and environment variable loading
requirements.txt     Pinned dependencies
.env.example         Environment variable template (commit this, not .env)
templates/
  base.html          Shared layout: Bootstrap, navbar, footer
  index.html         Home page — post list
  post.html          Single post + comment form + comments list
  make-post.html     Create / edit post form (admin)
  edit-comment.html  Edit comment form
  login.html         Login form
  register.html      Registration form
  about.html         Static about page
  contact.html       Static contact page
static/
  css/styles.css     Clean Blog theme (StartBootstrap) + custom overrides
  js/scripts.js      Theme JS
  assets/            Favicon + background images
docs/
  COURSE_NOTES.md    Original course exercise description
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask session signing key — any random string works locally |

## Design decisions

- **`auth.py` Blueprint** — login/register/logout are cohesive and separated from content routes, making `main.py` easier to scan.
- **`models.py` separated** — keeps SQLAlchemy boilerplate out of `main.py`; models are importable in `auth.py` and `main.py` without circular imports.
- **`config.py` + `.env`** — one-line edit to change any constant; `SECRET_KEY` is never committed, matching the pattern used in every real Flask project.
- **Admin = first registered user (`id == 1`)** — no separate roles table needed at Day 69; the course convention is explicit and simple.
- **`comment_owner_or_admin()` helper** — avoids duplicating the ownership check between the edit and delete routes.
- **`db.create_all()` inside app context** — safe for development; the SQLite DB is created in `instance/` (gitignored by Flask).
- **Jinja2 `{% extends "base.html" %}`** — replaces the original `{% include %}` pattern; eliminates duplicated `<html>/<head>` boilerplate across ten templates.

## Course context

100 Days of Code: The Complete Python Pro Bootcamp (Udemy — Angela Yu) — Day 69.
Topics: Flask-Login, password hashing with Werkzeug, SQLAlchemy relationships, WTForms, Flask-CKEditor, Flask-Gravatar, Bootstrap-Flask.
