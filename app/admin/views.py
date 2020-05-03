from flask_admin.contrib.sqla import ModelView
from app import db, admin
from app.models import * 


admin.add_view(ModelView(Items, db.session))
admin.add_view(ModelView(ItemMetadata, db.session))
admin.add_view(ModelView(Categories, db.session))
admin.add_view(ModelView(Subcategories, db.session))
admin.add_view(ModelView(Brands, db.session))
admin.add_view(ModelView(Colors, db.session))
admin.add_view(ModelView(ItemEdits, db.session))
admin.add_view(ModelView(Styles, db.session))
admin.add_view(ModelView(Thumbnails, db.session))
admin.add_view(ModelView(Users, db.session))