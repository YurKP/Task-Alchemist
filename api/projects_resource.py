from flask_restful import abort, Resource
from flask import jsonify

from data import db_session
from data.projects import Project
from api.parser_projects import parser


def abort_if_project_not_found(project_id):
    session = db_session.create_session()
    project = session.query(Project).get(project_id)

    if not project:
        abort(404, message=f"Project {project_id} not found")


class ProjectsResource(Resource):
    def get(self, project_id):
        abort_if_project_not_found(project_id)

        session = db_session.create_session()
        project = session.query(Project).get(project_id)

        return jsonify({'project': project.to_dict(
            only=('id', 'name', 'description', 'founder', 'participants', 'is_finished'))})

    def delete(self, project_id):
        abort_if_project_not_found(project_id)

        session = db_session.create_session()
        project = session.query(Project).get(project_id)

        session.delete(project)
        session.commit()

        return jsonify({'success': 'OK'})


class ProjectsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        projects = session.query(Project).all()

        return jsonify({'tasks': [item.to_dict(
            only=('id', 'name', 'description')) for item in projects]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()

        project = Project(
            name=args['name'],
            description=args['description'],
            founder=args['founder'],
            participants=args['participants'],
            is_finished=args['is_finished']
        )

        session.add(project)
        session.commit()

        return jsonify({'id': project.id})