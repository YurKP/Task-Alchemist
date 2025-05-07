from flask import Flask, render_template, abort, request
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import SubmitField, BooleanField, DateField
from flask_wtf.file import FileRequired, FileField

from forms.login import LoginForm
from forms.user import RegisterForm
from forms.task import TaskForm
from forms.project import ProjectForm

from data.users import User
from data.tasks import Task
from data.projects import Project
from data.categories import Category
from data import db_session

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

import datetime
import random

from flask_restful import Api
from api import users_resource
from api import tasks_resource
from api import projects_resource


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
@app.route('/index')
def index():
    if hasattr(current_user, 'id'):
        weekdays = {0: 'понедельник', 1: 'вторник', 2: 'среда', 3: 'четверг', 4: 'пятница', 5: 'суббота',
                    6: 'воскресенье'}
        months = {1: 'янв', 2: 'фев', 3: 'мар', 4: 'апр', 5: 'май', 6: 'июн', 7: 'июл', 8: 'авг', 9: 'сен', 10: 'окт',
                  11: 'ноя', 12: 'дек'}

        time_day = datetime.datetime.now().hour
        greeting = ''

        if 0 <= time_day < 6:
            greeting = 'Здравствуйте!'
        elif 6 <= time_day < 12:
            greeting = 'Доброе утро'
        elif 12 <= time_day < 18:
            greeting = 'Добрый день'
        elif 18 <= time_day <= 23:
            greeting = 'Добрый вечер'

        return render_template('page_after_login.html', title='Профиль',
                               weekday=weekdays[datetime.date.today().weekday()],
                               date=datetime.date.today().day,
                               month=months[datetime.date.today().month],
                               greeting=greeting)
    return render_template('beautiful_page.html')


@app.route('/tasks_today')
def tasks_today():
    # Создаем список, где
    # первый элемент - это список с сегодняшними задачи,
    # второй элемент - это список с просроченными задачами,
    # третий элемент - это список с рутинными задачами, т.е. задачами, которые выполняются каждый день,
    # четвертый элемент - это список с законченными задачами
    # (списки состоят из кортежей с необходимой информацией),
    # и счетчик
    lst = [[], [], [], []]

    for task in current_user.tasks:
        if task.finish_date:
            if ((datetime.date.today() == task.deadline_date) and
                    (datetime.datetime.now().time() <= task.deadline_time)):
                lst[3].append(task)
        else:
            if task.replay_every_day:
                if task.deadline_date == datetime.date.today():
                    lst[2].append(task)

            elif task.replay_every_week:
                if (task.deadline_date == datetime.datetime.now().date()
                        and task.deadline_time >= datetime.datetime.now().time()):
                    lst[2].append(task)

            else:
                if (task.deadline_date == datetime.datetime.now().date()
                        and task.deadline_time >= datetime.datetime.now().time()):
                    lst[0].append(task)
                else:
                    if task.deadline_date < datetime.date.today():
                        lst[1].append(task)
                    elif task.deadline_date == datetime.date.today():
                        if task.deadline_time < datetime.datetime.now().time():
                            lst[1].append(task)

    for i in range(len(lst)):
        # сортируем по категории важности
        lst[i] = sorted(lst[i], key=lambda x: x.ct.id, reverse=True)

    return render_template('tasks.html', title='Задачи на сегодня', lst=lst,
                           len_all_lst=[i for i in range(len(lst))],
                           len_lst=[[i for i in range(len(lst[j]))] for j in range(len(lst))],
                           lst_name=['Актуальные задачи', 'Просроченные задачи', 'Рутинные задачи',
                                     'Законченные задачи'],
                           type_task='today')


@app.route('/tasks_week')
def tasks_week():
    # Создаем список, где
    # первый элемент - это список с сегодняшними задачи,
    # второй элемент - это список с просроченными задачами,
    # третий элемент - это список с рутинными задачами, т.е. задачами, которые выполняются каждый день,
    # четвертый элемент - это список с законченными задачами
    # (списки состоят из кортежей с необходимой информацией),
    # и счетчик
    lst = [[], [], [], []]

    for task in current_user.tasks:
        if task.finish_date:

            if datetime.date.today() < task.deadline_date < datetime.date.today() + datetime.timedelta(weeks=1):
                lst[3].append(task)

            elif datetime.date.today() == task.deadline_date:
                if datetime.datetime.now().time() <= task.deadline_time:
                    lst[3].append(task)

            elif datetime.date.today() + datetime.timedelta(weeks=1) == task.deadline_date:
                if datetime.datetime.now().time() >= task.deadline_time:
                    lst[3].append(task)

        else:

            if task.replay_every_day:
                lst[2].append(task)

            elif task.replay_every_week:
                lst[2].append(task)

            else:

                if task.deadline_date < datetime.date.today():
                    lst[1].append(task)

                elif datetime.date.today() < task.deadline_date < datetime.date.today() + datetime.timedelta(weeks=1):
                    lst[0].append(task)

                elif datetime.date.today() == task.deadline_date:
                    if datetime.datetime.now().time() <= task.deadline_time:
                        lst[0].append(task)
                    else:
                        lst[1].append(task)

                elif datetime.date.today() + datetime.timedelta(weeks=1) == task.deadline_date:
                    if datetime.datetime.now().time() >= task.deadline_time:
                        lst[0].append(task)

    for i in range(len(lst)):
        lst[i] = sorted(lst[i], key=lambda x: x.ct.id, reverse=True)

    return render_template('tasks.html', title='Задачи на неделю', lst=lst,
                           len_all_lst=[i for i in range(len(lst))],
                           len_lst=[[i for i in range(len(lst[j]))] for j in range(len(lst))],
                           lst_name=['Актуальные задачи', 'Просроченные задачи', 'Рутинные задачи',
                                     'Законченные задачи'],
                           type_task='week')


@app.route('/tasks_all')
def tasks_all():
    # Создаем список, где
    # первый элемент - это список с сегодняшними задачи,
    # второй элемент - это список с просроченными задачами,
    # третий элемент - это список с рутинными задачами, т.е. задачами, которые выполняются каждый день,
    # четвертый элемент - это список с законченными задачами
    # (списки состоят из кортежей с необходимой информацией)
    lst = [[], [], [], []]

    for task in current_user.tasks:
        if task.finish_date:

            if task.replay_every_day or task.replay_every_week:
                lst[3].append(task)

            elif task.deadline_date == datetime.date.today():
                if task.deadline_time >= datetime.datetime.now().time():
                    lst[3].append(task)

            elif task.deadline_date > datetime.date.today():
                lst[3].append(task)

        else:

            if task.replay_every_day:
                lst[2].append(task)

            elif task.replay_every_week:
                lst[2].append(task)

            else:
                if task.deadline_date < datetime.date.today():
                    lst[1].append(task)

                elif task.deadline_date == datetime.date.today():
                    if task.deadline_time >= datetime.datetime.now().time():
                        lst[0].append(task)
                    else:
                        lst[1].append(task)

                else:
                    lst[0].append(task)

    for i in range(len(lst)):
        lst[i] = sorted(lst[i], key=lambda x: x.ct.id, reverse=True)

    return render_template('tasks.html', title='Все задачи', lst=lst,
                           len_all_lst=[i for i in range(len(lst))],
                           len_lst=[[i for i in range(len(lst[j]))] for j in range(len(lst))],
                           lst_name=['Актуальные задачи', 'Просроченные задачи', 'Рутинные задачи',
                                     'Законченные задачи'],
                           type_task='all')


@app.route('/projects')
def projects():
    db_sess = db_session.create_session()

    # Создаем список, где
    # первый элемент - это список с актуальными проектами
    # второй элемент - это список с просроченными проектами
    lst = [[], [], []]

    lst_projects = (db_sess.query(Project).
                    filter((Project.participants.like(f'%{current_user.id}%')) | (Project.founder == current_user.id)).
                    all())

    for project in lst_projects:
        if not project.is_finished:
            if project.deadline >= datetime.date.today():
                lst[0].append(project)
            else:
                lst[1].append(project)
        else:
            if project.deadline >= datetime.date.today():
                lst[2].append(project)

    return render_template('projects.html', title='Проекты',
                           len_all_lst=[i for i in range(len(lst))],
                           len_lst=[[i for i in range(len(lst[j]))] for j in range(len(lst))],
                           lst_name=['Актуальные проекты', 'Просроченные проекты', 'Законченные проекты'],
                           flags=[True if i.founder == current_user.id else False for i in lst_projects],
                           lst=lst)


@app.route('/tasks/projects/<int:id>')
def tasks_project(id):
    db_sess = db_session.create_session()

    tasks = (db_sess.query(Task).
             filter(Task.project == id).
             all())

    return render_template('tasks_project.html', lst=tasks, title='Задачи проекта',
                           user_id=current_user.id)


@app.route('/change_status_project/<int:id>')
def change_status_project(id):
    db_sess = db_session.create_session()

    project = (db_sess.query(Project).
               filter(Project.id == id).
               first())

    if project.is_finished:
        project.is_finished = 0
    else:
        project.is_finished = 1

    db_sess.commit()

    return redirect('/projects')


@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    form = ProjectForm()

    if form.validate_on_submit():

        db_sess = db_session.create_session()
        ids = [i.id for i in db_sess.query(User).all()]

        if form.participants.data:
            try:
                for i in form.participants.data.split(', '):
                    if int(i) not in ids:
                        return render_template('add_project.html', title='Добавление проекта',
                                                form=form,
                                                message="Участники не найдены")
            except Exception:
                return render_template('add_project.html', title='Добавление проекта',
                                       form=form,
                                       message="Участники не найдены")

        if not form.deadline.data:
            return render_template('add_project.html', title='Добавление проекта',
                                   form=form,
                                   message="Не указана дата дедлайна")

        project = Project(
            name=form.name.data,
            description=form.description.data,
            founder=current_user.id,
            participants=form.participants.data,
            is_finished=0,
            deadline=form.deadline.data
        )

        db_sess.add(project)
        db_sess.commit()

        return redirect('/projects')

    return render_template('add_project.html',
                           title='Добавление проекта', form=form)


@app.route('/edit_project/<int:id>', methods=['GET', 'POST'])
def edit_project(id):
    form = ProjectForm()

    if request.method == "GET":
        db_sess = db_session.create_session()

        project = db_sess.query(Project).filter(Project.id == id).first()

        if project:
            form.name.data = project.name
            form.description.data = project.description
            form.participants.data = project.participants
            form.deadline.data = project.deadline
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        project = db_sess.query(Project).filter(Project.id == id).first()

        if project:

            ids = [i.id for i in db_sess.query(User).all()]

            if form.participants.data:
                try:
                    for i in form.participants.data.split(', '):
                        if int(i) not in ids:
                            return render_template('add_project.html', title='Добавление проекта',
                                                   form=form,
                                                   message="Участники не найдены")
                except Exception:
                    return render_template('add_project.html', title='Добавление проекта',
                                           form=form,
                                           message="Участники не найдены")

            if not form.deadline.data:
                return render_template('add_project.html', title='Добавление проекта',
                                       form=form,
                                       message="Не указана дата дедлайна")

            project.name = form.name.data
            project.description = form.description.data
            project.participants = form.participants.data
            project.deadline = form.deadline.data

            db_sess.commit()
            return redirect('/projects')
        else:
            abort(404)

    return render_template('add_project.html', title='Редактирование проекта', form=form)


@app.route('/delete_project/<int:id>')
def delete_project(id):
    db_sess = db_session.create_session()

    project = db_sess.query(Project).filter(Project.id == id).first()

    if project:
        db_sess.delete(project)
        db_sess.commit()
    else:
        abort(404)

    return redirect('/projects')


@app.route('/detail_task/<int:id>')
def detail_task(id):
    db_sess = db_session.create_session()

    if 'tasks_today' in request.referrer.split('/'):
        name_page = '/tasks_today'
    elif 'tasks_week' in request.referrer.split('/'):
        name_page = '/tasks_week'
    elif 'tasks_all' in request.referrer.split('/'):
        name_page = '/tasks_all'
    else:
        name_page = '/information'

    return render_template('detail_task.html', title='Задача',
                           lst=db_sess.query(Task).filter(Task.id == id).first(),
                           name_page=name_page)


@app.route('/change_status_task/<int:id>')
def change_status_task(id):
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == id).first()

    if task:
        if task.finish_date:
            task.finish_date = None
        else:
            task.finish_date = datetime.date.today()
        db_sess.commit()
    else:
        abort(404)

    if 'tasks_today' in request.referrer.split('/'):
        name_page = '/tasks_today'
    elif 'tasks_week' in request.referrer.split('/'):
        name_page = '/tasks_week'
    else:
        name_page = '/tasks_all'

    return redirect(f'/switch{name_page}')


@app.route('/delete_task/<int:id>')
def delete_task(id):
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == id).first()

    if task:
        db_sess.delete(task)
        db_sess.commit()
    else:
        abort(404)

    if 'tasks_today' in request.referrer.split('/'):
        name_page = '/tasks_today'
    elif 'tasks_week' in request.referrer.split('/'):
        name_page = '/tasks_week'
    else:
        name_page = '/tasks_all'

    return redirect(f'/switch{name_page}')


@app.route('/add_task/<string:type_task>', methods=['GET', 'POST'])
def add_task(type_task):
    db_sess = db_session.create_session()

    # flag_form - вид формы, (1 - форма добавление задачи на СЕГОДНЯ, 0 - форма добавления задачи на НЕДЕЛЮ,
    # -1 - форма добавления задачи на ЛЮБУЮ дату)

    flag_form = -1

    if type_task == 'today':
        TaskForm.replay = BooleanField('Повторять каждый день?')
        flag_form = 1

    elif type_task == 'week':
        TaskForm.replay = BooleanField('Повторять каждую неделю?')
        TaskForm.date = DateField('Напишите  дату дедлайна')
        flag_form = 0

    if flag_form == -1:
        TaskForm.date = DateField('Напишите  дату дедлайна')

    form = TaskForm()

    # добавление выбора для выпадающих полей (проект, категория)
    form.project.choices = [('Нет', 'Нет')] + [(item.name, item.name) for item in
                                               db_sess.query(Project).all()
                                               if str(current_user.id) in item.participants or
                                               current_user.id == item.founder]
    form.category.choices = [(item.name, item.name) for item in
                             db_sess.query(Category).all()]

    if form.validate_on_submit():

        if flag_form == 0 or flag_form == -1:
            if not form.date.data:
                return render_template('add_task.html', title='Добавление задачи', form=form,
                                       flag_form=flag_form, message='Не указана дата дедлайна')

        # проверка даты для формы добавления задачи на неделю
        if flag_form == 0:
            if not (datetime.date.today() <= form.date.data <= datetime.date.today() + datetime.timedelta(weeks=1)):
                return render_template('add_task.html', title='Добавление задачи', form=form,
                                       flag_form=flag_form, message='Дата дедлайна выходит за границы недели')

        # либо получение id проекта, либо ничего
        if form.project.data == 'Нет':
            form.project.data = None
        else:
            form.project.data = db_sess.query(Project).filter(Project.name == form.project.data).first().id

        # установка 23:59:59 на время дедлайна в случае ее отсутствия
        if not form.deadline_time.data:
            form.deadline_time.data = datetime.time(23, 59, 59)

        # id категории
        form.category.data = db_sess.query(Category).filter(Category.name == form.category.data).first().id

        date, replay_every_day, replay_every_week = datetime.date.today(), 0, 0

        if flag_form == 0:

            if form.replay.data:
                replay_every_week = 1
            date = form.date.data

        elif flag_form == 1:

            if form.replay.data:
                replay_every_day = 1

        else:
            date = form.date.data

        task = Task(
            name=form.name.data,
            description=form.description.data,
            founder=current_user.id,
            project=form.project.data,
            category=form.category.data,
            deadline_date=datetime.date(date.year, date.month, date.day),
            deadline_time=datetime.time(form.deadline_time.data.hour, form.deadline_time.data.minute,
                                        form.deadline_time.data.second),
            replay_every_day=replay_every_day,
            replay_every_week=replay_every_week
        )

        db_sess.add(task)
        db_sess.commit()

        return redirect(f'/switch/tasks_{type_task}')

    return render_template('add_task.html', title='Добавление задачи', form=form,
                           flag_form=flag_form)


@app.route('/edit_task/<int:id>/<string:type_task>', methods=['GET', 'POST'])
def edit_task_today(id, type_task):
    db_sess = db_session.create_session()

    # flag_form - вид формы, (1 - форма добавление задачи на СЕГОДНЯ, 0 - форма добавления задачи на НЕДЕЛЮ,
    # -1 - форма добавления задачи на ЛЮБУЮ дату)

    flag_form = -1

    if type_task == 'today':
        TaskForm.replay = BooleanField('Повторять каждый день?')
        flag_form = 1

    elif type_task == 'week':
        TaskForm.replay = BooleanField('Повторять каждую неделю?')
        TaskForm.date = DateField('Напишите  дату дедлайна')
        flag_form = 0

    if flag_form == -1:
        TaskForm.date = DateField('Напишите  дату дедлайна')

    form = TaskForm()
    form.project.choices = [('Нет', 'Нет')] + [(item.name, item.name) for item in
                                               db_sess.query(Project).all()
                                               if str(current_user.id) in item.participants]
    form.category.choices = [(item.name, item.name) for item in
                             db_sess.query(Category).all()]

    if request.method == "GET":
        task = db_sess.query(Task).filter(Task.id == id).first()

        if task:
            form.name.data = task.name
            form.description.data = task.description
            form.project.data = task.project
            form.category.data = task.category
            form.deadline_time.data = task.deadline_time

            if flag_form == 1:
                if task.replay_every_day:
                    form.replay.data = True
                else:
                    form.replay.data = False
            elif flag_form == 0:
                if task.replay_every_week:
                    form.replay.data = True
                else:
                    form.replay.data = False
                form.date.data = task.deadline_date
            elif flag_form == -1:
                form.date.data = task.deadline_date

        else:
            abort(404)

    if form.validate_on_submit():

        task = db_sess.query(Task).filter(Task.id == id).first()

        if task:

            if flag_form == 0 or flag_form == -1:
                if not form.date.data:
                    return render_template('add_task.html', title='Редактирование задачи', form=form,
                                           flag_form=flag_form, message='Не указана дата дедлайна')

            # проверка даты для формы добавления задачи на неделю
            if flag_form == 0:
                if not (datetime.date.today() <= form.date.data <= datetime.date.today() + datetime.timedelta(weeks=1)):
                    return render_template('add_task.html', title='Рекатирование задачи', form=form,
                                           flag_form=flag_form, message='Дата дедлайна выходит за границы недели')

            # либо получение id проекта, либо ничего
            if form.project.data == 'Нет':
                form.project.data = None
            else:
                form.project.data = db_sess.query(Project).filter(Project.name == form.project.data).first().id

            # установка 23:59:59 на время дедлайна в случае ее отсутствия
            if not form.deadline_time.data:
                form.deadline_time.data = datetime.time(23, 59, 59)

            # id категории
            form.category.data = db_sess.query(Category).filter(Category.name == form.category.data).first().id

            date, replay_every_day, replay_every_week = datetime.date.today(), 0, 0

            if flag_form == 0:

                if form.replay.data:
                    if not task.replay_every_day:
                        replay_every_week = 1
                    else:
                        return render_template('add_task.html', title='Редактирование задачи',
                                               form=form,
                                               flag_form=flag_form, message='Задача повторяется каждый день')
                date = form.date.data

            elif flag_form == 1:

                if form.replay.data:
                    replay_every_day = 1

            else:
                date = form.date.data

            task.name = form.name.data
            task.description = form.description.data
            task.project = form.project.data
            task.category = form.category.data
            task.deadline_date = datetime.date(date.year, date.month, date.day)
            task.deadline_time = datetime.time(form.deadline_time.data.hour, form.deadline_time.data.minute,
                                               form.deadline_time.data.second)
            task.replay_every_day = replay_every_day
            task.replay_every_week = replay_every_week

            db_sess.commit()

            return redirect(f'/switch/tasks_{type_task}')

        else:
            abort(404)

    return render_template('add_task.html', title='Редактирование задачи', form=form,
                           flag_form=flag_form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()

    if form.validate_on_submit():

        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   form=form,
                                   message="Пароли не совпадают")

        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')

    return render_template('register.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")

        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route('/switch/<string:name_page>')
def switch(name_page):
    db_sess = db_session.create_session()

    date = datetime.date.today()
    time = datetime.datetime.now().time()

    tasks_every_day = db_sess.query(Task).filter(Task.founder == current_user.id,
                                                 Task.replay_every_day == 1).all()
    tasks_every_week = db_sess.query(Task).filter(Task.founder == current_user.id,
                                                  Task.replay_every_week == 1).all()

    for task in tasks_every_day:
        if task.deadline_date < date:
            task.finish_date = None
            task.deadline_date = datetime.date.today()
        elif task.deadline_date == date and task.deadline_time < time:
            task.finish_date = None
            task.deadline_date = datetime.date.today() + datetime.timedelta(days=1)

    for task in tasks_every_week:
        while (task.deadline_date < date) or (task.deadline_date == date and task.deadline_time < time):
            task.finish_date = None
            task.deadline_date = task.deadline_date + datetime.timedelta(weeks=1)

    db_sess.commit()

    return redirect(f'/{name_page}')


class LoadPhotoForm(FlaskForm):
    photo = FileField('Загрузить картинку', validators=[FileRequired()])
    submit = SubmitField('Загрузить')

    photo_file = 'static/img/профиль.png'


@app.route('/information', methods=['GET', 'POST'])
def information():
    db_sess = db_session.create_session()

    number_of_completed_tasks = len(db_sess.query(Task).filter(Task.founder == current_user.id,
                                                               Task.finish_date == datetime.date.today()).all())
    number_of_overdue_tasks = 0

    for item in db_sess.query(Task).filter(Task.founder == current_user.id,
                                        Task.finish_date == None).all():
        if item.deadline_date < datetime.date.today():
            number_of_overdue_tasks += 1
        elif item.deadline_date == datetime.date.today():
            if item.deadline_time < datetime.datetime.now().time():
                number_of_overdue_tasks += 1

    numbers_tasks = number_of_completed_tasks + number_of_overdue_tasks

    if numbers_tasks != 0:
        per1, per2 = number_of_completed_tasks / numbers_tasks, number_of_overdue_tasks / numbers_tasks
    else:
        per1, per2 = 0, 0

    load_photo = LoadPhotoForm(meta={'csrf': False})

    if load_photo.validate_on_submit():
        f = load_photo.photo.data

        f.save(f'static/img/{f.filename}')
        LoadPhotoForm.photo_file = f'static/img/{f.filename}'

        return redirect('/information')

    return render_template('information.html', title='Данные',
                           id=current_user.id, name=current_user.name, surname=current_user.surname,
                           number_of_completed_tasks=number_of_completed_tasks, percentage1=per1,
                           percentage2=per2, count1=number_of_completed_tasks,
                           count2=number_of_overdue_tasks, photo=LoadPhotoForm.photo_file,
                           form=load_photo)


@app.route('/random_task')
def random_task():
    db_sess = db_session.create_session()

    tasks = db_sess.query(Task).filter(Task.founder == current_user.id,
                                       Task.finish_date == None).all()

    if tasks:
        random.shuffle(tasks)
        return redirect(f'/detail_task/{tasks[0].id}')
    return redirect('/information')


if __name__ == '__main__':
    db_session.global_init("db/interesting.db")

    api.add_resource(users_resource.UsersListResource, '/api/v2/users')
    api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')

    api.add_resource(tasks_resource.TasksListResource, '/api/v2/tasks')
    api.add_resource(tasks_resource.TasksResource, '/api/v2/tasks/<int:task_id>')

    api.add_resource(projects_resource.ProjectsListResource, '/api/v2/projects')
    api.add_resource(projects_resource.ProjectsResource, '/api/v2/projects/<int:project_id>')

    app.run(port=8080, host='127.0.0.1')