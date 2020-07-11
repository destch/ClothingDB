from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class NewItem(FlaskForm):
    image = StringField(
        "Country",
        validators=[DataRequired(), Length(max=40)],
        render_kw={"placeholder": "country"},
    )
