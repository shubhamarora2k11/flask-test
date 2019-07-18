

from flask import Flask, render_template, redirect,  url_for, request, Response, current_app, flash
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)

import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.dialects.sqlite

from sqlalchemy import desc

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

from flask_mail import Mail, Message

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'dip.outsystems@gmail.com'
app.config['MAIL_PASSWORD'] = 'dipPassword1'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


mail = Mail(app)

def send_mail(to, subject, template):
    try:
        msg = Message(subject, sender = 'noreply@gmail.com', recipients = [to], html=template)
        #msg.body = template
        mail.send(msg)
    except Exception as e:
        print('Cannot send mail')
        print(e)
        return -1
    return 1

app.config['MAIL_DEFAULT_SENDER'] = 'noreply@kpmg.com'

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    try:
        mail.send(msg)
    except:
        return -1
    return 1

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
    h_add = db.Column(db.String(30)) 
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
    doc = db.Column(db.String(50))
    doc_status = db.Column(db.Integer,  nullable=False, default = 0)

    def __repr__(self):
        return "Details('{id}','{username}','{score}')".format(id= self.id, username=self.ass_name, score=self.taxable_value)




from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FileField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


class UpdateForm(FlaskForm):
    orderid = StringField('Order ID', render_kw={'readonly': True})
    picture = FileField('Update Picture', validators=[FileAllowed(['jpg','png'])])
    
    submit = SubmitField('Update')

class ViewForm(FlaskForm):
    orderid = StringField('Order ID', render_kw={'readonly': True})
    ass_id = StringField('Associate ID', render_kw={'readonly': True})
    ass_name = StringField('Associate Name', render_kw={'readonly': True})
    ass_gstin = StringField('Associate GSTIN', render_kw={'readonly': True})
    ass_email = StringField('Email', render_kw={'readonly': True})   
    state = StringField('State', render_kw={'readonly': True})
    sac = StringField('SAC', render_kw={'readonly': True})
    h_gstin = StringField('Herbalife GSTIN', render_kw={'readonly': True})
    h_add =  StringField('Herbalife Bill To address', render_kw={'readonly': True})
    taxable_value = StringField('Taxable Value', render_kw={'readonly': True})
    rate = StringField('Rate', render_kw={'readonly': True})
    igst = StringField('IGST', render_kw={'readonly': True})
    typ = StringField('Type', render_kw={'readonly': True})
    email_sent_status = StringField('Email Status', render_kw={'readonly': True})
    tax_in_received = StringField('tax_in_received', render_kw={'readonly': True})
    in_date = StringField('In-voice date', render_kw={'readonly': True})
    in_no = StringField('In-voice number', render_kw={'readonly': True})
    re_date = StringField('Receipt Date', render_kw={'readonly': True})
    re_remarks = StringField('Remarks', render_kw={'readonly': True})
    doc_status = StringField('Doc Status', render_kw={'readonly': True})
    doc_link = StringField('Doc Link', render_kw={'readonly': True})
    email_ack_status = StringField('Email acknowledgement Status', render_kw={'readonly': True})

    submit = SubmitField('Close')


import secrets

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/user_uploads', picture_fn)
    
    #output_size = (125,125)
    i = Image.open(form_picture)
    #i.thumbnail(output_size)
    i.save(picture_path)
    #form_picture.save(picture_path)
    return picture_fn 


app.config['SECURITY_PASSWORD_SALT'] = 'shubham'

from itsdangerous import URLSafeTimedSerializer
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email



@app.route('/', methods = ['GET', 'POST'])
def hello_world():
    form = UpdateForm()

    table_data = Details.query.all()

    if form.validate_on_submit():
        orderid = form.orderid.data
        print('oid', orderid)
        if form.picture.data and orderid!='':
            picture_file = save_picture(form.picture.data)
            print("pic",picture_file)
            temp_order =  Details.query.filter(Details.order_id==orderid).first()
            temp_order.doc_status=1
            temp_order.doc=picture_file
            db.session.commit()
            print(temp_order)
            token = generate_confirmation_token(temp_order.email)
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            print(temp_order.email, token, confirm_url, html, subject)
            
            mail_status = send_mail(temp_order.email, subject, html)
            temp_order.email_sent_status = mail_status
            db.session.commit()
            print(mail_status)
            if mail_status == -1:
                flash("Mail could not be sent. Please try after sometime","danger")
                return redirect(url_for('hello_world'))
            
            flash("Mail has been sent. Please acknowledge the same","success") 
            return redirect(url_for('hello_world'))
    
    return render_template('index.html', data=table_data, form=form)


@app.route('/document/<string:doc_string>')
def doc_link(doc_string):
    return redirect(url_for('static', filename='user_uploads/'+doc_string))

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
        print('email', email)
    except Exception as e:
        flash(e, 'danger')
        print(e)
    
    
    order =  Details.query.filter(Details.email==email).first()
    if order:
        if order.email_ack_status:
            flash('Email already acknowledged. Please check', 'danger')
            pass
        else:
            order.email_ack_status = 1
            db.session.commit()
            flash('You have acknowledged the email. Thanks!', 'success')
        return redirect(url_for('hello_world'))

    else:
        flash("Link has expired","danger")
        return redirect(url_for('hello_world'))   

@app.route('/view/<int:orderid>', methods = ['GET', 'POST'])
def view(orderid):
    form2 = ViewForm()

    order_data =  Details.query.filter(Details.order_id==orderid).first()

    form2.orderid.data = orderid
    form2.ass_id.data = order_data.ass_id
    form2.ass_name.data = order_data.ass_name
    form2.ass_gstin.data =  order_data.ass_gstin
    form2.ass_email.data = order_data.email
    form2.state.data = order_data.state
    form2.sac.data = order_data.sac
    form2.h_gstin.data = order_data.h_gstin
    form2.h_add.data = order_data.h_add
    form2.taxable_value.data = order_data.taxable_value
    form2.rate.data = order_data.rate
    form2.igst.data = order_data.igst
    form2.typ.data = order_data.typ
    form2.email_sent_status.data = order_data.email_sent_status
    form2.tax_in_received.data = order_data.tax_in_received
    form2.in_date.data = order_data.in_date
    form2.in_no.data = order_data.in_no
    form2.re_date.data = order_data.re_date
    form2.re_remarks.data = order_data.re_remarks
    form2.email_ack_status.data = order_data.email_ack_status
    form2.doc_link.data = 'http://localhost:5000/document/'+order_data.doc
    
    
    return render_template('view.html', form2=form2)


@app.route('/home')
def home():
    return render_template('home.html')

import sqlite3
import pandas as pd


@app.route('/download')
def download():
    dat = sqlite3.connect('site.db')
    query = dat.execute("SELECT * From Details")
    cols = [column[0] for column in query.description]
    results= pd.DataFrame.from_records(data = query.fetchall(), columns = cols)

    data=results.to_csv()
    return Response(
        data,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=mydata.csv"})

if __name__ == '__main__':
    app.run(debug=True)

