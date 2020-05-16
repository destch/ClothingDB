from flask import jsonify, request
from . import api
from ..models import *


@api.route('/Brand', methods=['GET', 'POST'])
def get_brands():
    term = request.args.get('term')
    res = Brand.query.filter(Brand.name.like('%{}%'.format(term))).limit(10)
    brands = [r.as_dict() for r in res]
    formatted = {'results': brands}
    return jsonify(formatted)

@api.route('/Subcategory', methods=['GET', 'POST'])
def get_subcat():
    res = Subcategory.query.all()
    subcats = [r.as_dict() for r in res]
    formatted = {'results': subcats}
    return jsonify(formatted)

@api.route('/Style', methods=['GET', 'POST'])
def get_styles():
    term = request.args.get('term')
    res = Style.query.filter(Style.name.like('%{}%'.format(term))).limit(10)
    styles = [r.as_dict() for r in res]
    formatted = {'results': styles}
    return jsonify(formatted)