"""
Project: Day 71 — Deploying Web App
Version: day71_blog_step_04
File: forms.py

Description:
This module defines all Flask-WTF form classes used by the blog application,
including registration, login, post creation, and commenting forms. It contains
only form definitions and validation logic and does not include routing or
application configuration.

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
Replaced all hardcoded secrets and configuration values with environment
variables to ensure security and production compatibility.

---------------------------------------------------------------------------
Changes in Step 04
---------------------------------------------------------------------------

This step introduces no functional changes to the form logic. It prepares the
application for production execution by:

• Adding gunicorn to requirements.txt
• Defining a production start command (via Procfile or hosting configuration)
• Verifying the app can be started without relying on app.run()
• Removing reliance on Flask’s built-in development server for deployment

All form definitions remain unchanged.
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
