from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class TopicForm(FlaskForm):
    topic = SelectField("Тема", choices=[
        ('cpp', 'C++'),
        ('python', 'Python'),
        ('linux', 'Linux'),
        ('network', 'Мрежи'),
        ('web', 'Web сигурност'),
        ('forensics', 'Компютърна криминалистика'),
        ('ai', 'Изкуствен интелект'),
        ('siem', 'SIEM системи'),
        ('cyberethics', 'Кибер етика')
    ])

    submit = SubmitField('Запази тема')


class DifficultyForm(FlaskForm):
    difficulty = SelectField(
        'Ниво на сложност',
        choices=[
            ('beginner', 'Начално'),
            ('intermediate', 'Средно'),
            ('advanced', 'Напреднало')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Запази ниво')


class ControlPointForm(FlaskForm):
    checkpoint = IntegerField(
        'Процент за преминаване на контролен въпрос',
        validators=[
            DataRequired(),
            NumberRange(min=0, max=100, message="Въведи число между 0 и 100")
        ]
    )
    submit = SubmitField('Запази праг')


