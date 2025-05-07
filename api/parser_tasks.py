from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('description', required=True)
parser.add_argument('founder', required=True, type=int)
parser.add_argument('project', required=True, type=int)
parser.add_argument('category', required=True, type=int)
parser.add_argument('replay_every_day', required=True, type=int)
parser.add_argument('replay_every_week', required=True, type=int)