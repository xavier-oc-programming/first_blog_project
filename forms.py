"""
Project: Day 71 — Deploying Web App
Version: day71_blog_step_05
File: forms.py

Description:
This module defines all Flask-WTF form classes used by the blog application,
including forms for user registration, login, blog post creation and editing,
and comment submission. The forms encapsulate field definitions and validation
logic and remain unchanged in this step.

---------------------------------------------------------------------------
Summary of Previous Steps
---------------------------------------------------------------------------

Step 01 — .gitignore:
Excluded environment files, caches, virtual environments, databases, IDE
metadata, and OS-specific files from version control.

Step 02 — Git version control:
Initialized the project under Git and established a clean baseline for
step-by-step deployment tracking.

Step 03 — Environment variables:
Prepared the application to load secrets securely, ensuring form-related
features such as CSRF protection function correctly in production.

Step 04 — WSGI server configuration:
Ensured the application can be executed by a WSGI server (gunicorn) in a
production environment without reliance on Flask’s development server.

---------------------------------------------------------------------------
Changes in Step 05
---------------------------------------------------------------------------

This step introduces no changes to the form definitions or validation logic.
Its purpose is to confirm that all form classes are correctly tracked in the
remote GitHub repository and are ready for deployment as part of the
application.

---------------------------------------------------------------------------
"""


# WTForms base class and field types.
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField


# Form for creating or editing a blog post.
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# Form for registering a new user account.
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


# Form for logging in an existing user.
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


# Form for submitting a rich-text comment.
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")
