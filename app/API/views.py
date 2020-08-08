from flask import jsonify, request, render_template, redirect, Response
from . import api
from ..models import *
from flask_login import current_user


@api.route("/Brand", methods=["GET", "POST"])
def get_brands():
    term = request.args.get("term")
    res = Brand.query.filter(Brand.name.ilike("%{}%".format(term))).limit(10)
    brands = [r.as_dict() for r in res]
    formatted = {"results": brands}
    return jsonify(formatted)


@api.route("/ItemSearch", methods=["GET", "POST"])
def get_items():
    term = request.args.get("term")
    res = Item.query.filter(Item.name.ilike("%{}%".format(term))).limit(10)
    items = [r.as_dict() for r in res]
    formatted = {"results": items}
    return jsonify(formatted)


@api.route("/Subcategory", methods=["GET", "POST"])
def get_subcat():
    res = Subcategory.query.all()
    subcats = [r.as_dict() for r in res]
    formatted = {"results": subcats}
    return jsonify(formatted)



@api.route("/Style", methods=["GET", "POST"])
def get_styles():
    term = request.args.get("term")
    res = Style.query.filter(Style.name.like("%{}%".format(term))).limit(10)
    styles = [r.as_dict() for r in res]
    formatted = {"results": styles}
    return jsonify(formatted)


# need to add authentication here
@api.route("/delete", methods=["POST"])
def delete_item():
    if current_user.is_administrator():
        id = request.form.get("itemId")
        print(id)
        item = Item.query.get(id)
        item.deleted = 1
        db.session.add(item)
        db.session.commit()
        return Response(status=200)
    else:
        return Response(status=404)
