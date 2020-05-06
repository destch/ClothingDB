from flask import render_template, request
from . import main
from ..models import *


@main.route('/', methods=['GET', 'POST'])
def index():
    items = Item.query.limit(4).all()
    return render_template('index.html', items=items)

@main.route('/new_item', methods=['GET', 'POST'])
def new_item():
    if request.method == "POST":
        print(request.form)
    return render_template('new_item.html')


@main.route('/feed', methods=['GET', 'POST'])
def feed():
    page = request.args.get('page', 1, type=int)
    query = Item.query
    pagination = query.order_by(Item.name.desc()).paginate(page, per_page=16, error_out=False)
    items = pagination.items
    return render_template('feed.html', items=items, pagination=pagination)
