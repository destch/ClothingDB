from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    SelectField,
    SubmitField,
    MultipleFileField,
)


class NewItem(FlaskForm):
    image = StringField(
        "Country",
        validators=[DataRequired(), Length(max=40)],
        render_kw={"placeholder": "country"},
    )
