import json
from app import db
from sqlalchemy.ext import mutable
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager


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


# item
class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    deleted = db.Column(db.Integer, default=0)
    name = db.Column(db.String)
    description = db.Column(db.Text)
    date_released = db.Column(db.DateTime())
    form_date = db.Column(db.String)
    price = db.Column(db.Float)
    brand_name = db.Column(db.String)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    subcategory_id = db.Column(db.Integer, db.ForeignKey("subcategories.id"))
    season = db.Column(db.String)
    fit = db.Column(db.String)
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
    filename = db.Column(db.String)

    def __repr__(self):
        return "<Filename %r>" % self.filename


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    profile_pic_filename = db.Column(db.String)
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
    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser
