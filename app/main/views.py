from flask import flash, render_template, request, make_response, redirect, url_for
from . import main
from ..models import *
from werkzeug.utils import secure_filename
import boto3
import random
from sqlalchemy import desc, or_, tuple_
from flask_login import login_user, logout_user, current_user
import uuid
from ..decorators import admin_required
import random
import requests
import json
import urllib.request


@main.route("/", methods=["GET", "POST"])
def index():
    q = Item.query.filter(Item.deleted != 1)
    query = Item.query.filter(Item.deleted != 1)
    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Item.id.desc()).paginate(
        page, per_page=16, error_out=False
    )
    items = pagination.items
    return render_template("index.html", items=items)


@main.route("/new_item", methods=["GET", "POST"])
def new_item():
    if request.method == "POST":

        files = request.form.getlist("filepond")
        thumbnail_list = []
        if files != []:
            for filename in files:
                thumbnail_list.append(Thumbnail(filename=filename))
        form_inputs = request.form

        item = Item(
            # gender = form_inputs["genderInput"],
            thumbnails=[] if files == [] else thumbnail_list,
            brand_id=form_inputs["brandInput"],
            brand_name=Brand.query.get(form_inputs["brandInput"]).name,
            name=form_inputs["nameInput"],
            category_id=None if form_inputs["categoryInput"] == "0" else form_inputs["categoryInput"],
            subcategory_id=None if form_inputs["subcatInput"] == "0" else form_inputs["subcatInput"],
            description=form_inputs["description"],
            season=form_inputs["seasonInput"],
            form_date=form_inputs["releaseInput"],
            fit=form_inputs["fitInput"],
            colors=[] if request.form.getlist('colorInput') == [] else \
                [Color(name=color) for color in request.form.getlist('colorInput')],
            materials=[] if request.form.getlist('materialsInput') == [] else \
                [Material(name=material) for material in request.form.getlist('materialsInput')],
            price=None if request.form.get('priceInput') == '' else \
                request.form.get('priceInput'),
            styles=[] if request.form.getlist('styleInput') == [] else \
                [Style(name=style) for style in request.form.getlist('styleInput')],
        )
        db.session.add(item)
        db.session.commit()
        item_id = Item.query.order_by(desc(Item.id)).first().id
        return redirect(url_for(".item", id=item.id))

    return render_template("new_item.html")


@main.route("/new_seller", methods=["GET", "POST"])
def new_seller():
    if request.method == "POST":
        form_inputs = request.form
        item_id = request.args.get('id')
        listing = Seller(item_id=item_id, site=form_inputs['siteInput'],
                         size=form_inputs['sizeInput'], price=form_inputs['priceInput'], link=form_inputs['urlInput'])
        db.session.add(listing)
        db.session.commit()
        return redirect(url_for(".item", id=item_id))

    return render_template("new_seller.html")


@main.route("/filepond", methods=["POST", "DELETE"])
def filepond():
    if request.method == "DELETE":
        filename = str(request.get_data())
        s3_client = boto3.resource("s3")
        bucket = s3_client.Bucket("cf-simple-s3-origin-db-556603787203")
        bucket.Object(filename).delete()
    elif request.method == "POST":
        f = request.files.get("filepond")
        ext = f.mimetype.split('/')[1].lower()
        filename = str(uuid.uuid4()) + ext
        s3_client = boto3.resource("s3")
        bucket = s3_client.Bucket("cf-simple-s3-origin-db-556603787203")
        bucket.Object(filename).put(Body=f)
        return filename


@main.route("/feed", methods=["GET", "POST"])
def feed():
    query = Item.query.filter(Item.deleted != 1)
    items = query.order_by(Item.id.desc()).limit(16).all()
    looks = Look.query.filter(Look.deleted != 1).order_by(Look.id.desc()).limit(16).all()
    brands = Brand.query.order_by(Brand.id.desc()).limit(16).all()
    return render_template(
        "feed.html",
        items=items, looks=looks, brands=brands)


@main.route("/feed/filter/", methods=["GET", "POST"])
def filtered_feed():
    brand_id = request.args.get("brandInput")
    category_id = request.args.get("categoryInput")
    subcat_id = request.args.get("subcatInput")

    params = {
        "brand_id": brand_id,
        "category_id": category_id,
        "subcategory_id": subcat_id,
    }
    brand = None
    category = None
    subcat = None

    query = Item.query
    if brand_id:
        query.filter(Item.brand_id == brand_id)
        brand = Brand.query.get(brand_id).name
    if category_id:
        query.filter(Item.category_id == category_id)
        category = Category.query.get(category_id).name
    if subcat_id:
        query.filter(Item.subcategory_id == subcat_id)
        subcat = Subcategory.query.get(subcat_id).name
    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Item.id.desc()).paginate(
        page, per_page=16, error_out=False
    )
    items = pagination.items
    return render_template(
        "feed.html",
        pagination=pagination,
        items=items,
        params=params,
        brand=brand,
        category=category,
        subcat=subcat,
    )


@main.route("/item/<int:id>", methods=["GET", "POST"])
def item(id):
    item = Item.query.get(id)
    comments = item.comments.all()
    listings = item.sellers.all()
    if request.method == "POST":
        comment_text = request.form["text"]
        author = current_user.id
        comment = Comment(body=comment_text, disabled=False, author_id=author, item_id=id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('main.item', id=id))

    return render_template("item.html", item=item, comments=comments, listings=listings)


@main.route("user/<int:id>")
def user(id):
    user = User.query.get(id)
    items = Item.query.limit(4).all()
    wants = user.wants.limit(4).all()
    haves = user.haves.limit(4).all()
    return render_template(
        "user.html", user=user, items=items, wants=wants, haves=haves
    )


@main.route("brand/<int:id>")
def brand(id):
    brand = Brand.query.get(id)
    # brand = Item.query.filter(Item.id == id).first().brand_name
    page = request.args.get("page", 1, type=int)
    # this needs to take into account the db relationship between the item table and the brand table
    query = Item.query.filter(Item.deleted != 1)
    query = query.filter(Item.brand_id == id)
    # order by date of the item
    pagination = query.order_by(Item.name.desc()).paginate(
        page, per_page=16, error_out=False
    )
    items = pagination.items
    return render_template(
        "brand.html", brand=brand, items=items, pagination=pagination
    )


@main.route("wantlist/<int:id>")
def wantlist(id):
    user = User.query.get(id)
    wants = user.wants.all()
    return render_template("wantlist.html", user=user, wants=wants)


@main.route("brand/<int:id>/newcollection", methods=["GET", "POST"])
def newCollection(id):
    if request.method == "POST":
        # get brand objcect
        brand = Brand.query.get(id)
        # images
        files = request.form.getlist("filepond")
        thumbnail_list = []
        if files != []:
            for filename in files:
                thumbnail_list.append(Thumbnail(filename=filename))
        formInputs = request.form
        collection = Collection(
            brand_name=brand.name,
            name=formInputs['nameInput'],
            brand_id=id,
            about=formInputs['descriptionInput'],
            designer=formInputs['designerInput'],
            year=formInputs['yearInput'],
            season=formInputs['seasonInput'],
            styles=[] if request.form.getlist('styleInput') == [] else \
                [Style(name=style) for style in request.form.getlist('styleInput')],
            thumbnails=thumbnail_list
        )
        db.session.add(collection)
        db.session.commit()
        return redirect(url_for(".brand", id=id))
    return render_template("new_collection.html")


@main.route("collection/<int:id>", methods=["GET", "POST"])
def collection(id):
    collection_obj = Collection.query.get(id)
    looks = collection_obj.looks.all()
    return render_template("collection.html", collection_obj=collection_obj, looks=looks)


@main.route("look/<int:id>", methods=["GET", "POST"])
def look(id):
    look_obj = Look.query.get(id)
    return render_template("look.html", look=look_obj)


@main.route("collection/<int:id>/newlook", methods=["GET", "POST"])
def newCollectionLook(id):
    if request.method == "POST":
        # get collection object that the look corresponds to
        collection = Collection.query.get(id)
        # images
        files = request.form.getlist("filepond")
        thumbnail_list = []
        if files != []:
            for filename in files:
                thumbnail_list.append(Thumbnail(filename=filename))
        formInputs = request.form
        look = Look(
            name=formInputs['nameInput'],
            description=formInputs['descriptionInput'],
            collection_id=id,
            styles=[] if request.form.getlist('styleInput') == [] else \
                [Style(name=style) for style in request.form.getlist('styleInput')],
            thumbnails=thumbnail_list
        )
        db.session.add(look)
        db.session.commit()
        return redirect(url_for(".collection", id=id))
    return render_template("new_collection_look.html")


# maybe move this into the API
@main.route("add_to_wantlist/<int:id>", methods=["POST"])
def add_to_wantlist(id):
    if current_user.is_authenticated:
        item = Item.query.get(id)
        current_user.wants.append(item)
        db.session.commit()
        flash("Added to Wantlist")
    else:
        pass
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@main.route("add_to_collection/<int:id>", methods=["POST"])
def add_to_collection(id):
    if current_user.is_authenticated:
        item = Item.query.get(id)
        current_user.haves.append(item)
        db.session.commit()
        flash("Added to Collection")
    else:
        pass
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@main.route("remove_from_wantlist/<int:id>", methods=["POST"])
def remove_from_wantlist(id):
    if current_user.is_authenticated:
        item = Item.query.get(id)
        current_user.wants.remove(item)
        db.session.commit()
        flash("Removed from Wantlist")
    else:
        pass
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@main.route("remove_from_collection/<int:id>", methods=["POST"])
def remove_from_collection(id):
    if current_user.is_authenticated:
        item = Item.query.get(id)
        current_user.haves.remove(item)
        db.session.commit()
        flash("Removed from Collection")
    else:
        pass
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


@admin_required
@main.route("delete/<int:id>", methods=["POST"])
def delete(id):
    item = Item.query.get(id)
    item.deleted = 1
    db.session.add(item)
    db.session.commit()
    flash("Item deleted")
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


# also consider moving this into an API route
@main.route("/item_search", methods=["POST"])
def item_search():
    term = request.form["search"]

    return redirect(url_for(".results", term=term))


@main.route("/results/<term>", methods=["GET", "POST"])
def results(term):
    if request.method == "POST":
        term = request.form["search"]
    multi_term = term.split()
    if len(multi_term) > 1:
        search_syntax = "%" + "".join([t + "%" for t in multi_term])
    else:
        search_syntax = "%" + term + "%"
    page = request.args.get("page", 1, type=int)
    query = Item.query.filter(Item.deleted != 1)
    query = query.filter(
        or_(Item.name.ilike(search_syntax), Item.brand_name.ilike(search_syntax))
    )
    num_results = len(query.all())
    pagination = query.paginate(page, per_page=16, error_out=False)
    items = pagination.items
    return render_template(
        "search_results.html", items=items, pagination=pagination, term=term, num_results=num_results
    )


@main.route("/social", methods=["GET", "POST"])
def social():
    page = request.args.get("page", 1, type=int)
    query = Item.query
    pagination = query.order_by(Item.id.desc()).paginate(
        page, per_page=16, error_out=False
    )
    items = pagination.items
    return render_template("social.html", items=items)


@main.route("/item/edit/<int:id>", methods=["GET", "POST"])
def item_edit(id):
    item = Item.query.get(id)
    if request.method == "POST":
        files = request.form.getlist("filepond")
        thumbnail_list = []
        if files != []:
            for filename in files:
                thumbnail_list.append(Thumbnail(filename=filename))
        form_inputs = request.form
        item.gender = form_inputs["genderInput"]
        item.thumbnails = item.thumbnails.all() + [] if files == [] else thumbnail_list
        item.brand_id = form_inputs["brandInput"]
        item.brand_name = Brand.query.get(form_inputs["brandInput"]).name
        item.name = form_inputs["nameInput"]
        item.category_id = None if form_inputs["categoryInput"] == "" else form_inputs["categoryInput"]
        item.subcategory_id = None if form_inputs["subcatInput"] == "" else form_inputs["subcatInput"]
        item.description = form_inputs["description"]
        item.season = form_inputs["seasonInput"]
        item.form_date = form_inputs["releaseInput"]
        item.fit = form_inputs["fitInput"]
        item.colors = [] if request.form.getlist('colorInput') == [] else \
            [Color(name=color) for color in request.form.getlist('colorInput')]
        item.materials = [] if request.form.getlist('materialsInput') == [] else \
            [Material(name=material) for material in request.form.getlist('materialsInput')]
        item.price = None if request.form.get('priceInput') == "None" or "" else float(request.form.get('priceInput'))
        # first try and get the style id by looking up the input, if doesnt exist then create a new style object
        item.styles = [] if request.form.getlist('styleInput') == [] else \
            [Style(name=style) for style in request.form.getlist('styleInput')]

        db.session.add(item)
        db.session.commit()
        return redirect(url_for(".item", id=item.id))
    brand = Brand.query.get(item.brand_id)
    category = Category.query.get(item.category_id)
    subcategory = Subcategory.query.get(item.subcategory_id)
    return render_template("item_edit.html", item=item, brand=brand, category=category, subcategory=subcategory)


@main.route("/user/edit/<int:id>", methods=["GET", "POST"])
def user_edit(id):
    user = User.query.get(id)
    if request.method == "POST":
        files = request.form.getlist("filepond")
        thumbnail_list = []
        if files != []:
            for filename in files:
                user.profile_pic_filename = filename
        form_inputs = request.form
        user.name = form_inputs["nameInput"]
        user.about_me = form_inputs["aboutInput"]
        db.session.add(user)
        db.session.commit()
        return redirect(url_for(".user", id=user.id))
    return render_template("user_edit.html", user=user)


@main.route("/brand/edit/<int:id>", methods=["GET", "POST"])
def brand_edit(id):
    brand = Brand.query.get(id)
    if request.method == "POST":
        files = request.form.getlist("filepond")
        thumbnail_list = []
        if files != []:
            for filename in files:
                brand.thumbnail_filename = filename
        form_inputs = request.form
        brand.about = form_inputs["aboutInput"]
        db.session.add(brand)
        db.session.commit()
        return redirect(url_for(".brand", id=brand.id))
    return render_template("brand_edit.html", brand=brand)


@main.route("/new_brand", methods=["GET", "POST"])
def new_brand():
    if request.method == "POST":
        form_inputs = request.form
        brand = Brand(name=form_inputs["nameInput"],
                      about=form_inputs["aboutInput"])
        files = request.form.getlist("filepond")
        thumbnail_list = []
        if files != []:
            for filename in files:
                brand.thumbnail_filename = filename

        db.session.add(brand)
        db.session.commit()
        brand_id = (Brand.query.order_by(desc(Brand.id)).first().id,)
        flash('Brand Submitted')
        return render_template("new_brand.html")
    return render_template("new_brand.html")


def upload_image_from_src(url):
    filename = str(uuid.uuid4()) + ".jpg"
    s3_client = boto3.resource("s3")
    bucket = s3_client.Bucket("cf-simple-s3-origin-db-556603787203")
    with urllib.request.urlopen(url) as f:
        bucket.upload_fileobj(f, filename)
    return filename


@main.route("/shopify", methods=["GET", "POST"])
def shopify():
    if request.method == "POST":
        url = request.form["url"] + 'products.json'
        r = requests.get(url)
        d = json.loads(r.content)
        products = d["products"]
        objs = []
        for i in range(len(products) - 20):
            print(str(i) + ' out of ' + str(len(products)))
            product = products[i]
            objs.append(Item(name=product["title"],
                             brand_name=product["vendor"],
                             description=product["body_html"],
                             thumbnails=[Thumbnail(filename=upload_image_from_src(img["src"])) for img in
                                         product["images"]]))

        db.session.add_all(objs)
        db.session.commit()

    return render_template("shopify.html")
