from flask import Blueprint


api = Blueprint('API', __name__)

from . import views