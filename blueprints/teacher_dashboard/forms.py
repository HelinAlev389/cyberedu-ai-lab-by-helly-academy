from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired


class LessonForm(FlaskForm):
    title = StringField("Заглавие на урока", validators=[DataRequired()])
    topic = SelectField("Тема", choices=[
        ('network', 'Мрежова сигурност'),
        ('log', 'Анализ на логове'),
        ('scenario', 'Сценарий')
    ])
    content = TextAreaField("Съдържание (Markdown или HTML)", validators=[DataRequired()])
    submit = SubmitField("Създай урок")
