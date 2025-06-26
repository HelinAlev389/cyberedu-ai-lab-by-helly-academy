from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class LessonForm(FlaskForm):
    title = StringField('Заглавие', validators=[DataRequired()])
    topic = StringField('Тема', validators=[DataRequired()])
    content = TextAreaField('Съдържание', validators=[DataRequired()])

    submit_draft = SubmitField('💾 Запази като чернова')
    submit_publish = SubmitField('📢 Публикувай')
