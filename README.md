# Xavier's Blog — Day 71

Flask blog with user authentication, admin post management, rich-text comments, and production deployment to Render.

Users register an account, log in, and leave rich-text comments on any blog post. The first registered account (`id == 1`) becomes the permanent admin and gains exclusive rights to create, edit, and delete posts. Any authenticated user can edit or delete their own comments; the admin can manage all comments sitewide. Gravatar avatars appear automatically next to every comment.

This project covers two contexts: a local development build running against SQLite with Flask's built-in server, and a production deployment to Render backed by PostgreSQL and served by Gunicorn. Both run the same `main.py` — the only difference is which environment variables are set.

External services used: **Render** hosts the web service and provides a managed PostgreSQL database. No API keys are required locally — SQLite is used as a zero-configuration fallback.

---

## Table of Contents

0. [Prerequisites](#0-prerequisites)
1. [Quick start](#1-quick-start)
2. [Builds comparison](#2-builds-comparison)
3. [Usage](#3-usage)
4. [Data flow](#4-data-flow)
5. [Features](#5-features)
6. [Route map](#6-route-map)
7. [Architecture](#7-architecture)
8. [Module reference](#8-module-reference)
9. [Configuration reference](#9-configuration-reference)
10. [Data schema](#10-data-schema)
11. [Environment variables](#11-environment-variables)
12. [Deploy to Render](#12-deploy-to-render)
13. [Design decisions](#13-design-decisions)
14. [Course context](#14-course-context)
15. [Dependencies](#15-dependencies)

---

## 0. Prerequisites

- A [GitHub account](https://github.com) with this project pushed to a repository
- A [Render account](https://render.com) (free tier works) for production deployment
- Python 3.10+ installed locally

---

## 1. Quick start

```bash
git clone https://github.com/xavier-oc-programming/day-71-blog-deploy.git
cd day-71-blog-deploy
pip install -r requirements.txt
cp .env.example .env          # then set FLASK_KEY to any random string
python main.py
```

Open http://127.0.0.1:5002 in your browser.

The first account you register becomes the admin.

---

## 2. Builds comparison

| | Local (dev) | Render (production) |
|---|---|---|
| Server | Flask built-in (`debug=False`) | Gunicorn (`gunicorn main:app`) |
| Database | SQLite (`instance/posts.db`) | PostgreSQL (Render managed) |
| Config | `.env` file | Environment variables on Render |
| `DB_URI` set? | No — SQLite fallback | Yes — PostgreSQL connection string |
| Entry point | `python main.py` | `gunicorn main:app` (from `Procfile`) |

---

## 3. Usage

**Register and log in**

```
GET  /register  →  fill out name, email, password  →  logged in automatically
GET  /login     →  email + password  →  redirected to home
```

**Browse and comment**

```
GET  /                →  list of all blog posts
GET  /post/<id>       →  read post, leave a comment (login required to comment)
```

**Admin actions** (first registered account only)

```
GET  /new-post        →  create a post
GET  /edit-post/<id>  →  edit a post
GET  /delete/<id>     →  delete a post
```

**Comment management**

```
GET  /edit-comment/<id>    →  edit your own comment (or any, if admin)
GET  /delete-comment/<id>  →  delete your own comment (or any, if admin)
```

---

## 4. Data flow

```
Browser request
      │
      ▼
Flask route (main.py)
      │
      ├── Auth check (Flask-Login / admin_only decorator)
      │
      ├── Form validation (Flask-WTF / WTForms)
      │
      ├── DB query (SQLAlchemy → SQLite locally / PostgreSQL on Render)
      │
      └── Template render (Jinja2 → HTML response)
                │
                └── Gravatar URL injected for comment avatars
```

---

## 5. Features

**Both builds**
- User registration with hashed passwords (Werkzeug `pbkdf2:sha256`)
- Session-based login / logout (Flask-Login)
- Rich-text post and comment creation (CKEditor)
- Gravatar avatars on all comments
- Flash messages for auth feedback
- Responsive layout (Bootstrap 5 / Clean Blog theme)

**Admin-only (first registered user)**
- Create, edit, and delete blog posts
- Edit or delete any comment sitewide

---

## 6. Route map

```
/                          GET          Home — all posts
/register                  GET POST     Register new account
/login                     GET POST     Log in
/logout                    GET          Log out
/post/<id>                 GET POST     Read post + submit comment
/edit-comment/<id>         GET POST     Edit comment (owner or admin)
/delete-comment/<id>       GET          Delete comment (owner or admin)
/new-post                  GET POST     Create post (admin only)
/edit-post/<id>            GET POST     Edit post (admin only)
/delete/<id>               GET          Delete post (admin only)
/about                     GET          About page
/contact                   GET          Contact page
```

---

## 7. Architecture

```
main.py                  Flask app — config, models, all routes
forms.py                 WTForms form classes
Procfile                 Gunicorn start command for Render
requirements.txt         Pinned dependencies
.env.example             Environment variable template (committed)
.env                     Real secrets — never committed
templates/
  base.html              Shared layout: Bootstrap, navbar, footer
  index.html             Home — post list
  post.html              Single post + comment form + comments
  make-post.html         Create / edit post (admin)
  edit-comment.html      Edit comment form
  login.html             Login form
  register.html          Registration form
  about.html             Static about page
  contact.html           Static contact page
static/
  css/styles.css         Clean Blog theme + custom overrides
  js/scripts.js          Theme JS
  assets/                Favicon + background images
instance/
  posts.db               SQLite database (local dev only, gitignored)
```

---

## 8. Module reference

### `main.py`

| Function / decorator | Returns | Description |
|---|---|---|
| `load_user(user_id)` | `User \| None` | Flask-Login user loader callback |
| `admin_only(func)` | decorator | Aborts with 403 if current user is not `id == 1` |
| `comment_owner_or_admin(comment)` | `bool` | Returns True if current user owns the comment or is admin |
| `register()` | response | Creates a new user, hashes password, logs in automatically |
| `login()` | response | Authenticates user by email + password |
| `logout()` | redirect | Clears session, redirects to home |
| `get_all_posts()` | response | Queries all posts, renders home page |
| `show_post(post_id)` | response | Renders a single post; handles new comment submission |
| `edit_comment(comment_id)` | response | Pre-fills comment editor; saves updated text on POST |
| `delete_comment(comment_id)` | redirect | Deletes comment, redirects to parent post |
| `add_new_post()` | response | Admin: creates a new blog post |
| `edit_post(post_id)` | response | Admin: updates an existing post |
| `delete_post(post_id)` | redirect | Admin: deletes a post |
| `about()` | response | Renders static about page |
| `contact()` | response | Renders static contact page |

### `forms.py`

| Class | Fields | Description |
|---|---|---|
| `CreatePostForm` | title, subtitle, img_url, body | Admin post creation / editing |
| `RegisterForm` | email, password, name | New user registration |
| `LoginForm` | email, password | User login |
| `CommentForm` | comment_text | Rich-text comment submission and editing |

---

## 9. Configuration reference

| Constant / setting | Default | Description |
|---|---|---|
| `SECRET_KEY` / `FLASK_KEY` | *(required)* | Flask session signing key |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///posts.db` | DB connection — overridden by `DB_URI` env var on Render |
| `app.run(port=...)` | `5002` | Local dev port |
| Gravatar `size` | `100` | Avatar pixel size |
| Gravatar `rating` | `g` | Maximum content rating |
| Gravatar `default` | `retro` | Fallback avatar style |
| Password hash method | `pbkdf2:sha256` | Werkzeug hashing algorithm |
| Password `salt_length` | `8` | Werkzeug salt length |

---

## 10. Data schema

### `users`

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary key |
| `email` | String(100) | Unique, not null |
| `password` | String(200) | Not null (hashed) |
| `name` | String(100) | Not null |

### `blog_posts`

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary key |
| `title` | String(250) | Unique, not null |
| `subtitle` | String(250) | Not null |
| `date` | String(250) | Not null |
| `body` | Text | Not null |
| `img_url` | String(250) | Not null |
| `author_id` | Integer | Foreign key → `users.id` |

### `comments`

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary key |
| `text` | Text | Not null |
| `author_id` | Integer | Foreign key → `users.id` |
| `post_id` | Integer | Foreign key → `blog_posts.id` |

**Relationships**
- `User` → `BlogPost`: one-to-many (`author` / `posts`)
- `User` → `Comment`: one-to-many (`author` / `comments`)
- `BlogPost` → `Comment`: one-to-many (`parent_post` / `comments`)

---

## 11. Environment variables

| Variable | Required | Description |
|---|---|---|
| `FLASK_KEY` | Yes | Flask session signing key — any random string |
| `DB_URI` | Production only | PostgreSQL connection string — falls back to SQLite locally |

Copy `.env.example` to `.env` and fill in the values. Never commit `.env`.

---

## 12. Deploy to Render

1. **Push your code to GitHub** and connect the repo to [render.com](https://render.com).

2. **Create a PostgreSQL database** on Render (New → PostgreSQL). Copy the **Internal Database URL** for the next step.

3. **Create a Web Service** on Render (New → Web Service), connect your GitHub repo, and set:

   | Setting | Value |
   |---|---|
   | Runtime | Python |
   | Build command | `pip install -r requirements.txt` |
   | Start command | `gunicorn main:app` |

4. **Set environment variables** under the Web Service → Environment tab:

   | Variable | Value |
   |---|---|
   | `FLASK_KEY` | Any random secret string |
   | `DB_URI` | Internal Database URL from your Render PostgreSQL |

5. Click **Deploy** — Render builds and starts the app automatically. Any future `git push` triggers a re-deploy.

---

## 13. Design decisions

- **Admin = first registered user (`id == 1`)** — no separate roles table needed at Day 71; the course convention is explicit and simple.
- **`admin_only` decorator** — keeps the access check out of route body; a single `@admin_only` line is harder to forget than an inline `if` block.
- **`comment_owner_or_admin()` helper** — avoids duplicating the ownership check between the edit and delete routes.
- **`DB_URI` env var with SQLite fallback** — the same `main.py` runs locally (SQLite, zero setup) and in production (PostgreSQL, full concurrency) with no code changes.
- **`Procfile` with `gunicorn main:app`** — Render detects it automatically; no build configuration needed beyond environment variables.
- **`db.create_all()` inside app context on startup** — safe for development; on Render with PostgreSQL, tables are created on first deploy and left untouched on subsequent ones.
- **`load_dotenv()` at the top of `main.py`** — environment variables from `.env` are available before any app configuration runs, including `SECRET_KEY` and `DB_URI`.
- **Gravatar injected into `jinja_env.globals`** — makes `gravatar(email)` callable from any template without passing it explicitly in every `render_template()` call.
- **`Jinja2 {% extends "base.html" %}`** — replaces the original `{% include %}` pattern; eliminates duplicated `<html>/<head>` boilerplate across nine templates.

---

## 14. Course context

100 Days of Code: The Complete Python Pro Bootcamp (Udemy — Angela Yu) — Day 71.
Topics: Flask deployment, Gunicorn, environment variables, PostgreSQL on Render, `.gitignore` for production, Git version control for deployment.

---

## 15. Dependencies

| Module | Used in | Purpose |
|---|---|---|
| `Flask` | `main.py` | Web framework — routing, request handling, templating |
| `Flask-Login` | `main.py` | Session management and `current_user` proxy |
| `Flask-SQLAlchemy` | `main.py` | ORM — database models and queries |
| `Flask-WTF` | `forms.py` | CSRF-protected form handling |
| `Flask-CKEditor` | `main.py`, `forms.py` | Rich-text editor for posts and comments |
| `Flask-Gravatar` | `main.py` | Gravatar avatar URLs from email addresses |
| `Bootstrap-Flask` | `main.py` | Bootstrap 5 Jinja2 helpers |
| `Werkzeug` | `main.py` | Password hashing (`generate_password_hash` / `check_password_hash`) |
| `SQLAlchemy` | `main.py` | Core ORM types (`Integer`, `String`, `Text`, `ForeignKey`, etc.) |
| `WTForms` | `forms.py` | Form field types and validators |
| `gunicorn` | `Procfile` | Production WSGI server |
| `psycopg2-binary` | runtime | PostgreSQL adapter for SQLAlchemy |
| `python-dotenv` | `main.py` | Loads `.env` file into environment variables |
| `email-validator` | `forms.py` | Validates email fields in WTForms |
