from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo


class RegistrationForm(FlaskForm):
    first_name = StringField('Име', validators=[DataRequired(), Length(1, 80)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(1, 80)])
    username = StringField('Потребителско име', validators=[DataRequired(), Length(4, 80)])
    password = PasswordField('Парола', validators=[DataRequired(), Length(6, 200)])
    email = StringField('Имейл', validators=[DataRequired(), Length(5, 120)])

    confirm_password = PasswordField(
        'Потвърди парола',
        validators=[DataRequired(), EqualTo('password', message='Паролите не съвпадат.')]
    )

    role = SelectField('Роля', choices=[
        ('student', 'Студент'),
        ('teacher', 'Преподавател'),
        ('admin', 'Администратор')],
                       validators=[DataRequired()]
                       )
    submit = SubmitField('Регистрация')


class LoginForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    password = PasswordField('Парола', validators=[DataRequired()])
    otp = StringField('Код за 2FA')
    remember_me = BooleanField('Запомни ме')
    submit = SubmitField('Вход')


class ForgotPasswordForm(FlaskForm):
    username = StringField('Имейл или потребителско име', validators=[DataRequired()])
    submit = SubmitField('Изпрати линк')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Нова парола', validators=[DataRequired(), Length(6)])
    confirm = PasswordField('Потвърди паролата', validators=[EqualTo('password')])
    submit = SubmitField('Запази')
