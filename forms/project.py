from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, DateField
from wtforms.validators import DataRequired, Optional


class ProjectForm(FlaskForm):
    name = StringField('Название проекта', validators=[DataRequired()])
    description = TextAreaField('Подробная информация (если необходимо)', validators=[Optional()])
    participants = StringField('Напишите id участников (через запятую и пробел)', validators=[Optional()])
    deadline = DateField('Укажите дедлайн', validators=[Optional()])
    submit = SubmitField('Добавить')