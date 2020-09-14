from flask import jsonify, request, render_template, redirect, Response
from . import api
from ..models import *
from flask_login import current_user
import requests
from elasticsearch import Elasticsearch
es = Elasticsearch(["http://elastic:daniel97@34.198.0.244:9200"])

@api.route("/LoadItems", methods=["GET", "POST"])
def load_items():
    query = Item.query.filter(Item.deleted != 1)
    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Item.id.desc()).paginate(
        page, per_page=16, error_out=False
    )
    items = pagination.items
    formatted = {"results": [item.as_dict() for item in items]}
    return jsonify(formatted)

@api.route("/Brand", methods=["GET", "POST"])
def get_brands():
    term = request.args.get("term")
    res = Brand.query.filter(Brand.name.ilike("%{}%".format(term))).limit(10)
    print(res)
    brands = [r.as_dict() for r in res]
    print(brands)
    formatted = {"results": brands}
    return jsonify(formatted)

@api.route("/Elasticsearch", methods=["GET", "POST"])
def elasticsearch():
    term = request.args.get("term")
    res = es.search(index="clothdb", body={"query": {"multi_match": {"query": term, "type": "cross_fields", "fields": ["name", "brand_name"]}}})
    res = res['hits']['hits']
    item_ids = [r['_source']["id"] for r in res]
    items = [x.as_dict() for x in Item.query.filter(Item.id.in_(item_ids)).all()]
    formatted = {"items": items}
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

