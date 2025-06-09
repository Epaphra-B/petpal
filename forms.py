from flask_wtf import FlaskForm
from wtforms import FileField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from wtforms import StringField, PasswordField, SubmitField, FileField
from flask_wtf.file import FileAllowed

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PetForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    species = StringField('Species', validators=[DataRequired()])
    breed = StringField('Breed', validators=[DataRequired()])
    age = StringField('Age')
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Save')

class HealthRecordForm(FlaskForm):
    type = StringField('Type', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    details = StringField('Details')
    weight = StringField('Weight')
    submit = SubmitField('Save')

class ReminderForm(FlaskForm):
    task = StringField('Task', validators=[DataRequired()])
    due_date = StringField('Due Date', validators=[DataRequired()])
    recurring = StringField('Recurring', validators=[DataRequired()])
    submit = SubmitField('Save')

class TaskForm(FlaskForm):
    description = StringField('Task', validators=[DataRequired()])
    submit = SubmitField('Add Task')