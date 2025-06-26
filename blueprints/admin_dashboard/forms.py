from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional


class CreateUserForm(FlaskForm):
    username = StringField("Потребителско име", validators=[DataRequired()])
    email = StringField("Имейл", validators=[DataRequired(), Email()])
    first_name = StringField("Име", validators=[Optional()])
    last_name = StringField("Фамилия", validators=[Optional()])
    password = PasswordField("Парола", validators=[DataRequired(), Length(min=6)])
    role = SelectField("Роля", choices=[('student', 'Студент'), ('teacher', 'Преподавател'), ('admin', 'Администратор')])
    submit = SubmitField("Създай")


class EditUserForm(FlaskForm):
    username = StringField("Потребителско име", validators=[DataRequired()])
    email = StringField("Имейл", validators=[DataRequired(), Email()])
    first_name = StringField("Име", validators=[Optional()])
    last_name = StringField("Фамилия", validators=[Optional()])
    ROLES = [('student', 'Студент'), ('teacher', 'Преподавател'), ('admin', 'Администратор')]
    role = SelectField("Роля", choices=ROLES)
    submit = SubmitField("Обнови")
