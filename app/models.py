import json
from app import db
from sqlalchemy.ext import mutable
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# json
class JsonEncodedDict(db.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = db.Text

    @staticmethod
    def process_bind_param(value, dialect):
        if value is None:
            return '{}'
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
materials = db.Table('materials',
                     db.Column('material_id', db.Integer, db.ForeignKey('Materials.id'), primary_key=True),
                     db.Column('item_id', db.Integer, db.ForeignKey('Items.id'), primary_key=True)
                     )

colors = db.Table('colors',
                  db.Column('color_id', db.Integer, db.ForeignKey('Colors.id'), primary_key=True),
                  db.Column('item_id', db.Integer, db.ForeignKey('Items.id'), primary_key=True)
                  )

styles = db.Table('styles',
                  db.Column('style_id', db.Integer, db.ForeignKey('Styles.id'), primary_key=True),
                  db.Column('item_id', db.Integer, db.ForeignKey('Items.id'), primary_key=True)
                  )


# item
class Items(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, required=True)
    description = db.Column(db.Text)
    date_released = db.Column(db.Timestamp)
    price = db.Column(db.Float)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
                            nullable=False)
    materials = db.relationship('Materials', secondary=materials, lazy='subquery',
                                backref=db.backref('items', lazy=True))
    colors = db.relationship('Colors', secondary=colors, lazy='subquery',
                             backref=db.backref('items', lazy=True))

    styles = db.relationship('Styles', secondary=styles, lazy='subquery',
                             backref=db.backref('items', lazy=True))
    thumbnails = db.relationship('Thumbnails', backref='item', lazy='dynamic')
    metadata_id = db.Column(db.Integer, db.ForeignKey('item_metadata.id'))
    edits = db.relationship('ItemEdit', backref='item', lazy='dynamic')


class ItemMetadata(db.Model):
    __tablename__ = 'item_metadata'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.relationship('Items', backref='item_metadata', lazy='dynamic')
    date_submitted = db.Column(db.Timestamp)
    submitter = db.Column(db.Integer, db.ForeignKey('user.id'))
    field_edited = db.Column(db.String, required=True)


class Categories(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, required=True)
    items = db.relationsip('Items', backref='category', lazy='dynamic')


class Subcategories(db.Model):
    __tablename__ = 'subcategories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, required=True)
    items = db.relationsip('Items', backref='subcategory', lazy='dynamic')


class Brands(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, required=True)
    items = db.relationsip('Items', backref='brand', lazy='dynamic')


class Materials(db.Model):
    __tablename__ = 'materials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, required=True)


class Colors(db.Model):
    __tablename__ = 'colors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, required=True)


class ItemEdits(db.Model):
    __tablename__ = 'item_edits'
    id = db.Column(db.Integer, db.ForeignKey())

class Styles(db.Model):
    __tablename__ = 'styles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, required=True)


class Thumbnails(db.Model):
    __tablename__ = 'thumbnails'
    id = db.Column(db.Integer, db.ForeignKey('item.id'))
    filename = db.Column(db.String, required=True)

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    profile_pic_filename = db.Column(db.String)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

