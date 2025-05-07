from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('description', required=True)
parser.add_argument('founder', required=True, type=int)
parser.add_argument('participants', required=True)
parser.add_argument('is_finished', required=True, type=int)