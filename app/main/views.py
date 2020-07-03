from flask import flash, render_template, request, make_response, redirect, url_for
from . import main
from ..models import *
from werkzeug.utils import secure_filename
import boto3
import random
from sqlalchemy import desc, or_
from flask_login import login_user, logout_user, current_user


@main.route('/', methods=['GET', 'POST'])
def index():
    items = Item.query.order_by(desc(Item.id)).limit(4).all()
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

@main.route('user/<int:id>')
def user(id):
    user = User.query.get(id)
    items = Item.query.limit(4).all()
    wants = user.wants.limit(4).all()
    haves = user.haves.limit(4).all()
    return render_template('user.html', user=user, items=items, wants=wants, haves=haves)

@main.route('brand/<int:id>')
def brand(id):
    brand = Brand.query.get(id)
    page = request.args.get('page', 1, type=int)
    #this needs to take into account the db relationship between the item table and the brand table
    query = Item.query.filter(Item.brand_name == brand)
    #order by date of the item
    pagination = query.order_by(Item.name.desc()).paginate(page, per_page=16, error_out=False)
    items = pagination.items
    return render_template('brand.html', brand=brand, items=items, pagination=pagination)

@main.route('wantlist/<int:id>')
def wantlist(id):
    user = User.query.get(id)
    wants = user.wants.all()
    return render_template('wantlist.html', user=user, wants=wants)

@main.route('collection/<int:id>')
def collection(id):
    user = User.query.get(id)
    haves = user.haves.all()
    return render_template('collection.html', user=user, haves=haves)


#maybe move this into the API
@main.route('add_to_wantlist/<int:id>', methods=['POST'])
def add_to_wantlist(id):
    if current_user.is_authenticated:
        item = Item.query.get(id)
        current_user.wants.append(item)
        db.session.commit()
        flash('Added to Wantlist')
    else:
        pass
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@main.route('add_to_collection/<int:id>', methods=['POST'])
def add_to_collection(id):
    if current_user.is_authenticated:
        item = Item.query.get(id)
        current_user.haves.append(item)
        db.session.commit()
        flash('Added to Collection')
    else:
        pass
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@main.route('remove_from_wantlist/<int:id>', methods=['POST'])
def remove_from_wantlist(id):
    if current_user.is_authenticated:
        item = Item.query.get(id)
        current_user.wants.remove(item)
        db.session.commit()
        flash('Removed from Wantlist')
    else:
        pass
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@main.route('remove_from_collection/<int:id>', methods=['POST'])
def remove_from_collection(id):
    if current_user.is_authenticated:
        item = Item.query.get(id)
        current_user.haves.remove(item)
        db.session.commit()
        flash('Removed from Collection')
    else:
        pass
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 



#also consider moving this into an API route
@main.route('/item_search', methods=['POST'])
def item_search():
    term = request.form['search'] 
    return redirect(url_for('.results', term=term))


@main.route('/results/<term>', methods=["GET", "POST"])
def results(term):
    if request.method == 'POST':
        term = request.form['search']
    multi_term = term.split()
    if len(multi_term) > 1: 
        search_syntax = "%" + "".join([t + "%" for t in multi_term])
    else:
        search_syntax = "%" + term + "%"
    page = request.args.get('page', 1, type=int)
    query = Item.query.filter(or_(Item.name.ilike(search_syntax),
                            Item.brand_name.ilike(search_syntax)))
    pagination = query.paginate(page, per_page=16, error_out=False)
    items = pagination.items
    return render_template('search_results.html', items=items, pagination=pagination, term = term)
