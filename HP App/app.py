
from flask import Flask, render_template, redirect,  url_for, request, Response, current_app, flash, jsonify, make_response
from werkzeug.utils import secure_filename
from PIL import Image
import json, requests
app = Flask(__name__)


from flask import Markup

import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

import random

#################################################################
#DB

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.dialects.sqlite

from sqlalchemy import desc

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)


from datetime import datetime

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer)
    file_name = db.Column(db.String(50))
    file_type = db.Column(db.String(50))
    file_status = db.Column(db.Integer)
    file_base64 = db.Column(db.LargeBinary)

    def __repr__(self):
        return "File('{id}','{file_id}','{file_name}','{file_status}')".format(id= self.id, file_id=self.file_id, file_name=self.file_name, file_status=self.file_status)

import sqlalchemy_jsonfield
import ujson

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.String(50))
    file_data = db.Column( sqlalchemy_jsonfield.JSONField( enforce_string=True, enforce_unicode=False, json=ujson,  ),     )
    
    def __repr__(self):
        return "Result('{id}','{file_id}','{file_data}')".format(id= self.id, file_id=self.file_id, file_data=self.file_data)



#################################################################
#FORMS

from flask_wtf import FlaskForm
from flask_uploads import UploadSet, IMAGES
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FileField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


class NewDocForm(FlaskForm):
	select = SelectField('Document Type', choices=[('MSA', 'Contract - MSA'), ('SOW', 'Contract - SOW'), ('Addendum', 'Contract - Addendum'), ('Invoice', 'Invoice')])
	proceed = SubmitField('Proceed')


class UpdateDocForm(FlaskForm):
	title = StringField('Document Title', validators = [DataRequired()])
	file = FileField('Add file', validators = [ FileRequired(), FileAllowed(['pdf'], 'PDFs only!') ] )
	submit = SubmitField('Submit')




#################################################################

import base64

@app.route('/', methods = ['GET', 'POST'])
def home():
	form = NewDocForm()
	if form.validate_on_submit():
		#flash("Welcome","success")
		select = form.select.data
		return redirect(url_for('docdetails', doctype=str(select)))

	return render_template('newdoc.html', form=form)

@app.route('/docdetails/<string:doctype>', methods = ['GET', 'POST'])
def docdetails(doctype):
	form = UpdateDocForm()

	if form.validate_on_submit():
		file_name = form.title.data
		file_type = doctype
		file = form.file.data
		file_base64 = base64.b64encode(file.read())
		
		file_id = getfileID(file_name, file_type, file_base64)
		print(file_id, file_name, file_type)

		file_object = File(file_id=file_id, file_name=file_name, file_type=file_type, file_status=0, file_base64=file_base64)
		db.session.add(file_object)
		db.session.commit()
		
		flash('file uploaded successfully', 'success')
		return redirect(url_for('files'))

	elif request.method=='POST':
		flash("Please choose PDF type files only", "danger")
		return render_template('docdetails.html', form=form)
		 
	return render_template('docdetails.html', form=form)

@app.route('/files', methods = ['GET', 'POST'])
def files():
	
	files = File.query.all()

	filteronfilestatus = File.query.filter(File.file_status==0).all()

	data = []

	for item in filteronfilestatus:
		data.append(item.file_id)

	data = list(map(str, data))
	#data = ["1","2"]

	return render_template('index.html', data=data, files=files)


def getfileID(file_name, file_type, file_base64):
	
	#API_ENDPOINT = "http://"

	#API_KEY = "XXXXXXXXXXXXXXXXX"
	
	#data = {
	#		'file_name':file_name, 
	#        'file_type':file_type, 
	#        'file_base64':file_base64
	#        } 
	  
	#r = requests.post(url = API_ENDPOINT, data = data) 
	  
	#res = r.text

	#print("response from api", res) 
	
	return random.randint(0,10000) 


if __name__ == '__main__':
	app.run(debug=True)

