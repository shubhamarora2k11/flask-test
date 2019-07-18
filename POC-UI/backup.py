

from flask import Flask, render_template, redirect,  url_for, request, Response
from werkzeug.utils import secure_filename


app = Flask(__name__)

import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.dialects.sqlite
import future_fstrings
from sqlalchemy import desc

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

from datetime import datetime

class Details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, unique=True, nullable=False)
    ass_id = db.Column(db.Integer, unique=True, nullable=False)
    ass_gstin = db.Column(db.String(30),  nullable=False) 
    ass_name = db.Column(db.String(30),  nullable=False)
    state = db.Column(db.String(20),  nullable=False)
    sac = db.Column(db.String(20),  nullable=False)
    h_gstin = db.Column(db.String(30),  nullable=False) 
    taxable_value = db.Column(db.Float,  nullable=False) 
    rate = db.Column(db.Float,  nullable=False) 
    igst = db.Column(db.Float,  nullable=False) 
    typ =  db.Column(db.String(5),  nullable=False)
    email = db.Column(db.String(40),  nullable=False)
    email_sent_status = db.Column(db.Integer,  nullable=False, default = 0)
    tax_in_received = db.Column(db.Integer,  nullable=False, default= 0)
    in_date =  db.Column(db.DateTime, nullable=False )
    in_no = db.Column(db.String(20), nullable =False)
    re_date =  db.Column(db.DateTime)
    re_remarks = db.Column(db.String(100))
    email_ack_status = db.Column(db.Integer,  nullable=False, default = 0)
    doc_status = db.Column(db.Integer,  nullable=False, default = 0)

    def __repr__(self):
        return "Details('{id}','{username}','{score}')".format(id= self.id, username=self.ass_name, score=self.taxable_value)


import pandas as pd

data = pd.read_excel('Sheet.xlsx', sheet_name='Sheet1')
data['doc_status'] = 0
data['doc_status'][2] = 1

print(data.head())

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      
   return render_template('acknowledgement.html')

@app.route('/')
def hello_world(data=data):
    return render_template('index.html', data=data)


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/download')
def download(data=data.to_csv()):
	return Response(
        data,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=myplot.csv"})

if __name__ == '__main__':
    app.run(debug=True)

