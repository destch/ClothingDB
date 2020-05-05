from flask import jsonify
from . import api
from ..models import *


@api.route('/Brand', methods=['GET', 'POST'])
def get_brands():
    items = Item.query.limit(4).all()
    return jsonify

