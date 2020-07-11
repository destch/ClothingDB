from flask_admin.contrib.sqla import ModelView
from app import db, admin
from app.models import *


admin.add_view(ModelView(Item, db.session))
admin.add_view(ModelView(ItemMetadata, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Subcategory, db.session))
admin.add_view(ModelView(Material, db.session))
admin.add_view(ModelView(Brand, db.session))
admin.add_view(ModelView(Color, db.session))
admin.add_view(ModelView(ItemEdit, db.session))
admin.add_view(ModelView(Style, db.session))
admin.add_view(ModelView(Thumbnail, db.session))
admin.add_view(ModelView(User, db.session))
