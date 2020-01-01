from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField
from wtforms.validators import DataRequired, Email, Length, Optional, URL, regexp as regexp_validator

class BuriedForm(FlaskForm):
	class Meta:
		csrf = False
	action = StringField("action", validators=[DataRequired()])
	job_id = IntegerField("job_id", validators=[DataRequired()])

class ManageForm(FlaskForm):
	class Meta:
		csrf = False
	action = StringField("action", validators=[DataRequired()])
	id = IntegerField("id", validators=[DataRequired()])
	url = StringField("url", validators=[DataRequired(), URL()])

class PreviewForm(FlaskForm):
	class Meta:
		csrf = False
	url = StringField("url", validators=[DataRequired(), URL()])

class SearchForm(FlaskForm):
	class Meta:
		csrf = False
	q = StringField("q", validators=[DataRequired(), Length(min=3, max=64)])

class SubmitForm(FlaskForm):
	class Meta:
		csrf = False
	url = StringField("url", validators=[DataRequired(), URL()])

class ViewForm(FlaskForm):
	class Meta:
		csrf = False
	url = StringField("url", validators=[DataRequired(), URL()])
