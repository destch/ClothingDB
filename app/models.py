import json
from app import db
from sqlalchemy.ext import mutable
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from flask import request
from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)



class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# json
class JsonEncodedDict(db.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""

    impl = db.Text

    @staticmethod
    def process_bind_param(value, dialect):
        if value is None:
            return "{}"
        else:
            return json.dumps(value)

    @staticmethod
    def process_result_value(value, dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)


mutable.MutableDict.associate_with(JsonEncodedDict)

# area for defining many to one helpers
material_registrations = db.Table(
    "material_registrations",
    db.Column("material_id", db.Integer, db.ForeignKey("materials.id")),
    db.Column("item_id", db.Integer, db.ForeignKey("items.id")),
)

color_registrations = db.Table(
    "color_registrations",
    db.Column("color_id", db.Integer, db.ForeignKey("colors.id")),
    db.Column("item_id", db.Integer, db.ForeignKey("items.id")),
)

style_registrations = db.Table(
    "style_registrations",
    db.Column("style_id", db.Integer, db.ForeignKey("styles.id")),
    db.Column("item_id", db.Integer, db.ForeignKey("items.id")),
)
want_registrations = db.Table(
    "want_registrations",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("item_id", db.Integer, db.ForeignKey("items.id")),
)
have_registrations = db.Table(
    "have_registrations",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("item_id", db.Integer, db.ForeignKey("items.id")),
)

item_registrations = db.Table(
    "item_registrations",
    db.Column("look_id", db.Integer, db.ForeignKey("looks.id")),
    db.Column("item_id", db.Integer, db.ForeignKey("items.id")),
)



# item
class Item(SearchableMixin, db.Model):
    __tablename__ = "items"
    __searchable__ = ['name', 'brand_name', 'description']
    id = db.Column(db.Integer, primary_key=True)
    deleted = db.Column(db.Integer, default=0)
    name = db.Column(db.String)
    description = db.Column(db.Text)
    date_released = db.Column(db.DateTime())
    form_date = db.Column(db.String)
    price = db.Column(db.String)
    brand_name = db.Column(db.String)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    subcategory_id = db.Column(db.Integer, db.ForeignKey("subcategories.id"))
    season = db.Column(db.String)
    fit = db.Column(db.String)
    comments = db.relationship("Comment", backref="items", lazy="dynamic")
    sellers = db.relationship("Seller", backref="items", lazy="dynamic")
    materials = db.relationship(
        "Material",
        secondary=material_registrations,
        backref=db.backref("items", lazy="dynamic"),
        lazy="dynamic",
    )
    colors = db.relationship(
        "Color",
        secondary=color_registrations,
        backref=db.backref("items", lazy="dynamic"),
        lazy="dynamic",
    )
    styles = db.relationship(
        "Style",
        secondary=style_registrations,
        backref=db.backref("items", lazy="dynamic"),
        lazy="dynamic",
    )

    thumbnails = db.relationship("Thumbnail", backref="items", lazy="dynamic")
    metadata_id = db.Column(db.Integer, db.ForeignKey("item_metadata.id"))
    edits = db.relationship("ItemEdit", backref="items", lazy="dynamic")
    gender = db.Column(db.String)


    def __repr__(self):
        return "<Item %r>" % self.name

    def as_dict(self):
        return {'id': self.id, "brand": self.brand_name, "name": self.name, "thumbnails": [res.filename for res in self.thumbnails.all()]}


class ItemMetadata(db.Model):
    __tablename__ = "item_metadata"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.relationship("Item", backref="item_metadata", lazy="dynamic")
    date_submitted = db.Column(db.DateTime())
    submitter = db.Column(db.Integer, db.ForeignKey("users.id"))
    field_edited = db.Column(db.String)

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    items = db.relationship("Item", backref="categories", lazy="dynamic")

    def __repr__(self):
        return "<Category %r>" % self.name


class Subcategory(db.Model):
    __tablename__ = "subcategories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    items = db.relationship("Item", backref="subcategories", lazy="dynamic")

    def __repr__(self):
        return "<Subcategory %r>" % self.name


class Brand(db.Model):
    __tablename__ = "brands"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    items = db.relationship("Item", backref="brands", lazy="dynamic")
    thumbnail_filename = db.Column(db.String)
    about = db.Column(db.Text)

    def __repr__(self):
        return "<Brand %r>" % self.name

    def as_dict(self):
        return {"id": self.id, "text": self.name}


class Material(db.Model):
    __tablename__ = "materials"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return "<Material %r>" % self.name


class Color(db.Model):
    __tablename__ = "colors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return "<Color %r>" % self.name


class ItemEdit(db.Model):
    __tablename__ = "item_edits"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    data_edited = db.Column(db.String)
    time_edited = db.Column(db.DateTime(), default=datetime.utcnow())
    reason = db.Column(db.Text)
    editing_user = db.Column(db.Integer, db.ForeignKey("users.id"))


class Style(db.Model):
    __tablename__ = "styles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return "<Style %r>" % self.name

    def as_dict(self):
        return {"id": self.id, "text": self.name}


class Thumbnail(db.Model):
    __tablename__ = "thumbnails"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    look_id = db.Column(db.Integer, db.ForeignKey("looks.id"))
    filename = db.Column(db.String)

    def __repr__(self):
        return "<Filename %r>" % self.filename


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    profile_pic_filename = db.Column(db.String)
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    edits = db.relationship("ItemEdit", backref="user_edits", lazy="dynamic")
    wants = db.relationship(
        "Item",
        secondary=want_registrations,
        backref=db.backref("user_wants", lazy="dynamic"),
        lazy="dynamic",
    )
    haves = db.relationship(
        "Item",
        secondary=have_registrations,
        backref=db.backref("user_haves", lazy="dynamic"),
        lazy="dynamic",
    )


    def __init__(self, **kwargs):
            super(User, self).__init__(**kwargs)
            if self.role is None:
                if self.email == 'daniel.chavez9797@gmail.com':
                    self.role = Role.query.filter_by(name='Administrator').first()
                if self.role is None:
                    self.role = Role.query.filter_by(default=True).first()



    def can(self, perm):
            return self.role is not None and self.role.has_permission(perm)


    def is_administrator(self):
        return self.email == "daniel.chavez9797@gmail.com"

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User %r>" % self.username


class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        self.id = request.remote_addr
    
    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser




class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name



class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    look_id = db.Column(db.Integer, db.ForeignKey("looks.id"))
    collection_id = db.Column(db.Integer, db.ForeignKey("collections.id"))

class Collection(db.Model):
    __tablename__ = "collections"
    id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"))
    name = db.Column(db.String)
    year = db.Column(db.String)
    season = db.Column(db.String)
    season_collection = db.Column(db.String)
    gender = db.Column(db.String)
    about = db.Column(db.Text)
    comments = db.relationship("Comment", backref="collections", lazy="dynamic")
    #video_links = 

class Look(db.Model):
    __tablename__ = "looks"
    id = db.Column(db.Integer, primary_key=True)
    deleted = db.Column(db.Integer, default=0)
    name = db.Column(db.String)
    collection_id = db.Column(db.Integer, db.ForeignKey("collections.id"))
    description = db.Column(db.Text)
    date = db.Column(db.DateTime())
    form_date = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    subcategory_id = db.Column(db.Integer, db.ForeignKey("subcategories.id"))
    season = db.Column(db.String)
    comments = db.relationship("Comment", backref="looks", lazy="dynamic")
    thumbnails = db.relationship("Thumbnail", backref="looks", lazy="dynamic")
    items = db.relationship(
        "Item",
        secondary=item_registrations,
        backref=db.backref("look_items", lazy="dynamic"),
        lazy="dynamic",
    )

    def __repr__(self):
        return "<Look %r>" % self.name

class Seller(db.Model):
    __tablename__ = "sellers"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    site = db.Column(db.String)
    size = db.Column(db.String)
    price = db.Column(db.String)
    link = db.Column(db.String)
