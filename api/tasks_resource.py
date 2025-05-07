from flask_restful import abort, Resource
from flask import jsonify

from data import db_session
from data.tasks import Task
from api.parser_tasks import parser


def abort_if_tasks_not_found(task_id):
    session = db_session.create_session()
    task = session.query(Task).get(task_id)

    if not task:
        abort(404, message=f"Task {task_id} not found")


class TasksResource(Resource):
    def get(self, task_id):
        abort_if_tasks_not_found(task_id)

        session = db_session.create_session()
        task = session.query(Task).get(task_id)

        return jsonify({'task': task.to_dict(
            only=('id', 'name', 'description', 'founder', 'project', 'category',
                  'replay_every_day', 'replay_every_week'))})

    def delete(self, task_id):
        abort_if_tasks_not_found(task_id)

        session = db_session.create_session()
        task = session.query(Task).get(task_id)

        session.delete(task)
        session.commit()

        return jsonify({'success': 'OK'})


class TasksListResource(Resource):
    def get(self):
        session = db_session.create_session()
        tasks = session.query(Task).all()

        return jsonify({'tasks': [item.to_dict(
            only=('id', 'name', 'description')) for item in tasks]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()

        task = Task(
            name=args['name'],
            description=args['description'],
            founder=args['founder'],
            project=args['project'],
            category=args['category'],
            replay_every_day=args['replay_every_day'],
            replay_every_week=args['replay_every_week']
        )

        session.add(task)
        session.commit()

        return jsonify({'id': task.id})