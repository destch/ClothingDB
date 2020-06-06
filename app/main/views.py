from flask import render_template, request
from . import main
from ..models import *
from werkzeug.utils import secure_filename
import boto3
import random


@main.route('/', methods=['GET', 'POST'])
def index():
    items = Item.query.limit(4).all()
    return render_template('index.html', items=items)

@main.route('/new_item', methods=['GET', 'POST'])
def new_item():
    if request.method == "POST":
        f = request.files['fileInput']
        filename = ""
        if f is not None:
            filename = str(random.randint(1, 1000000000)) + secure_filename(f.filename)
            s3_client = boto3.resource("s3")
            bucket = s3_client.Bucket("cf-simple-s3-origin-db-556603787203")
            bucket.Object(filename).put(Body=f)
        form_inputs = request.form
        print(form_inputs['brandInput'])
        item = Item(thumbnails=[Thumbnail(filename=filename)],
                    brand_id=form_inputs['brandInput'],
                    name=form_inputs['nameInput'],
                    category_id=form_inputs['categoryInput'],
                    subcategory_id=form_inputs['subcatInput'],
                    description=form_inputs['description'],
                    styles=[Style.query.get(form_inputs['styleInput'])])

        db.session.add(item)
        db.session.commit()

    #you should really return the new item's page
    return render_template('new_item.html')


@main.route('/feed', methods=['GET', 'POST'])
def feed():
    page = request.args.get('page', 1, type=int)
    query = Item.query
    pagination = query.order_by(Item.name.desc()).paginate(page, per_page=16, error_out=False)
    items = pagination.items
    return render_template('feed.html', items=items, pagination=pagination)


@main.route('/item/<int:id>', methods=['GET', 'POST'])
def item(id):
    item = Item.query.get(id)
    return render_template('item.html', item=item)


@main.route('test')
def test():
    return render_template('item_test.html')