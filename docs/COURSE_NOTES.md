# Day 69 — Blog Capstone Project Pt. 4: Adding Users

## Course exercise description

100 Days of Code: The Complete Python Pro Bootcamp (Udemy — Angela Yu), Day 69.

This project extends the blog capstone across three previous days by adding a full user authentication layer, relational database associations, and a per-user comment system.

### Requirements implemented

**Requirement 1 — Register new users**
- `/register` route renders a WTForm with email, password, and name fields.
- Duplicate email registration is blocked (flash + redirect to login).
- Passwords are hashed with `werkzeug.security.generate_password_hash` (pbkdf2:sha256, salt_length=8).
- Successful registration logs the user in immediately via Flask-Login.

**Requirement 2 — Log in registered users**
- `/login` route validates credentials against the hashed password in the database.
- Bad email and bad password produce separate flash messages.
- Successful login redirects to the home page.

**Requirement 3 — Protect routes with authentication**
- Custom `@admin_only` decorator restricts post creation, editing, and deletion to the user with `id == 1` (the first registered user).
- Non-admin requests are met with HTTP 403.

**Requirement 4 — Relational databases for users and posts**
- `User` ↔ `BlogPost` one-to-many relationship: each post has a `ForeignKey("users.id")` and an `author` relationship back to `User`.
- SQLAlchemy 2.x `mapped_column` / `Mapped` style annotations used throughout.

**Requirement 5 — Allow any user to add comments**
- `Comment` model added with `ForeignKey` to both `users` and `blog_posts`.
- `CommentForm` uses `CKEditorField` for rich-text input.
- Gravatar avatars displayed next to each comment.

**Step 6 (beyond course) — Comment ownership**
- Comment owners and the admin (id == 1) can edit/delete their own comments.
- `comment_owner_or_admin()` helper enforces this check server-side.
- UI links shown conditionally in `post.html`.

### Sensitive data note

`main.py` in the `source` branch has the original `SECRET_KEY` redacted to `*****`.
The real secret key must be set in a `.env` file (see `.env.example`).
