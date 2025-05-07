from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TimeField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Optional


class TaskForm(FlaskForm):
    name = StringField('Название задачи', validators=[DataRequired()])
    description = TextAreaField('Подробная информация (если необходимо)', validators=[Optional()])
    project = SelectField('Выберите проект (если необходимо)')
    category = SelectField('Выберите категорию важности')
    deadline_time = TimeField('Укажите дедлайн (если необходимо)', validators=[Optional()])
    submit = SubmitField('Добавить')