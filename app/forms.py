from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, DateField, BooleanField, SelectField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional
from .models import User, Task, Category, Tag


# Registration form
class RegistrationForm(FlaskForm):

    # Fields, uses validators to check if the fields are not empty
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # Custom validator to check if the username already exists in the database
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another one.')

    # Custom validator to check if the email already exists in the database
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account already exists with this email.')

# Login form
class LoginForm(FlaskForm):

    # Fields, uses validators to check if the fields are not empty
    login = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Task form
class TaskForm(FlaskForm):

    # Fields, uses validators to check if the fields are not empty
    title = StringField('Quest Title', validators=[DataRequired()])
    description = TextAreaField('Quest Description')
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[Optional()])
    quest_type = SelectField('Quest Type', 
                           choices=[
                               ('main_quest', 'Main Quest'),
                               ('side_quest', 'Side Quest'),
                               ('sub_quest', 'Sub-Quest')
                           ],
                           default='side_quest')
    difficulty = SelectField('Difficulty',
                           choices=[
                               ('easy', 'Easy (Commoner)'),
                               ('normal', 'Normal (Adventurer)'),
                               ('hard', 'Hard (Hero)'),
                               ('epic', 'Epic (Legend)')
                           ],
                           default='normal')
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    tags = SelectMultipleField('Tags', coerce=int, validators=[Optional()])
    parent_quest = SelectField('Parent Quest', 
                             coerce=lambda x: int(x) if x and str(x).isdigit() else None,
                             validators=[Optional()])
    priority = SelectField('Priority',
                         choices=[
                             (1, 'High'),
                             (2, 'Medium'),
                             (3, 'Low')
                         ],
                         coerce=int,
                         default=2)
    is_template = BooleanField('Save as Template')
    template_name = StringField('Template Name', validators=[Optional(), Length(max=150)])
    submit = SubmitField('Embark on Quest')

    def validate_parent_quest(self, field):
        if self.quest_type.data == 'sub_quest':
            if field.data is None:
                raise ValidationError('Sub-quests must be associated with a main quest. Please select a parent quest.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=50)])
    color = StringField('Color', default='#4a90e2')
    icon = StringField('Icon', default='fa-tasks')
    submit = SubmitField('Create Category')

class TagForm(FlaskForm):
    name = StringField('Tag Name', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Create Tag')

class QuestChainForm(FlaskForm):
    name = StringField('Chain Name', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Chain Description')
    submit = SubmitField('Create Quest Chain')
