from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import Flask, render_template, redirect,  url_for, request
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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40),unique=True, nullable=False)
    score = db.Column(db.Float, default=0 )
    texts = db.relationship('Text', backref='author', lazy=True)    
    def __repr__(self):
        return "User('{id}','{username}','{score}')".format(id= self.id, username=self.username, score=self.score)
    
class Text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    sentiment = db.Column(db.String(15),nullable=False)
    emotion = db.Column(db.String(100),nullable=False)
    score = db.Column(db.Float,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Text('{id}', '{data}', '{date}', '{sentiment}', '{emotion}', '{score}', '{user_id}')".format(id= self.id, data=self.data, date=self.date, sentiment=self.sentiment,emotion=self.emotion,score=self.score, user_id=self.user_id)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    useful = db.Column(db.String(5), nullable=False)
    suggestion = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Feedback('{id}','{useful}','{suggestion}','{user_id}')".format(id= self.id, useful=self.useful, suggestion=self.suggestion, user_id=self.user_id)
     
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
  


def sentiment_scores(sentence): 
  
    sid_obj = SentimentIntensityAnalyzer() 
   
    sentiment_dict = sid_obj.polarity_scores(sentence) 
      
   
    if sentiment_dict['compound'] >= 0.05 : 
        return ("Positive") 
  
    elif sentiment_dict['compound'] <= - 0.05 : 
        return ("Negative") 
  
    else : 
        return ("Neutral") 


from watson_developer_cloud import ToneAnalyzerV3
tone_analyzer = ToneAnalyzerV3(
   version='2017-09-21',
   iam_apikey='azcAYWvPk1INaDXNa-dGY0AqW6jl8qvqXAAwSqE5DtRQ',
   url='https://gateway-syd.watsonplatform.net/tone-analyzer/api'
)

class LoginForm(FlaskForm):
   username = StringField( validators = [DataRequired(), Length(min=2, max=20)])
   submit = SubmitField('Start')
   def validate_username(self, username):
      user = User.query.filter_by(username=username.data).first()
      if user:
         raise ValidationError('Username is taken, please choose a different one')

class FeedbackForm(FlaskForm):
    useful = SelectField(choices = [(1, 'Yes'), (0, 'No')])
    suggestion = TextAreaField('Suggestions:')
    submit = SubmitField('Submit')




@app.route('/', methods=['GET', 'POST'])
def home():    
    form = LoginForm()
    if form.validate_on_submit():
        user = User(username= form.username.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('question', username=form.username.data))
    
    table_data = User.query.order_by(desc(User.score)).limit(5)

    username = request.args.get('username', None)
    
    rank = 0
        
    if(username):
        all_data = User.query.order_by(desc(User.score)).all()
        rank = 1
        for u in all_data:
            if(u.username== username):
                break
            else:
                rank+=1
        
        print(rank)

        return render_template('table.html', table=table_data, form=form, rank=rank, user=u)

    return render_template('table.html', table=table_data, form=form, rank=rank)

# @app.route('/tester' , methods =['GET', 'POST'])
# def test():
#     return render_template('homee.html')

@app.route('/test' , methods =['GET'])
def text_data():
    username = request.args.get('username', None)
    print(username)
    textdata=request.args.get('data',None)
    print(textdata)
    senti=sentiment_scores(textdata) 
    
    tone_analysis = tone_analyzer.tone({'text': textdata},'application/json').get_result()
    score = 0
    tone_names = []
    
    for tone in tone_analysis['document_tone']['tones']:
        score+=tone['score']
        tone_names.append(tone['tone_name'])

    tones_count = len(tone_analysis['document_tone']['tones'])

    if (tones_count == 0):
        tone_names.append("No tone captured")
        score = round(0, 2)
    else: 
        score = round((score / tones_count)*10, 2)

    user = User.query.filter_by(username = username).first()
    
    if user.score==0:
        user.score = round(score, 2) 
    else:
        user.score  = round((user.score+score)/2, 2)

    tone_names_str = ",".join(tone_names)
    text = Text(data=textdata, emotion=tone_names_str, sentiment=senti, score=score, user_id=user.id)
    
    db.session.add(text)

    db.session.commit()

    return ("<h3>Real Time Analysis</h3> Sentiment: "+ senti + "<br>Tone: "+ tone_names_str+ "<br>Tone Score: "+ str(score) )


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    rank=0
    form = FeedbackForm()
    username = request.args.get('username', None)
    if request.method == 'GET':
        username = request.args.get('username', None)
        user = User.query.filter_by(username = username).first()
        final_data = Text.query.filter_by(user_id=user.id)
        print(final_data)
        return render_template('feedback.html', table=final_data, username=username, form=form)
    
    elif form.validate_on_submit():
        username = request.args.get('username', None)
        user = User.query.filter_by(username = username).first()
        feedback = Feedback(useful=form.useful.data, suggestion=form.suggestion.data, user_id=user.id)
        db.session.add(feedback)
        db.session.commit()
        
        return redirect(url_for('home', username=username))

    return redirect(url_for('home', username=username))

        
question_set_1 = ['How are you feelling today?','How satisfied were you with the event?','What did you like most about the event?','What did you like least about the event?','Are you excited to be part of this event?','What are the key things you are looking forward to at this event?']
question_set_2 = ['Who inspires you? And why?', 'What makes you angry at work?','What has been your proudest professional moment?','']
question_set_3 = ['Describe a time when you resolved a conflict at work?','Describe a time when you had to adapt at work?']

import random

@app.route('/question', methods=['GET', 'POST'])
def question():

    q1 = random.choice(question_set_1)
    if request.method == 'GET':
        username = request.args.get('username', None)
        return render_template('question.html', username=username, quest = q1)
    elif form.validate_on_submit():
        return redirect(url_for('question2', username=form.username.data))
    
@app.route('/question2', methods=['GET', 'POST'])
def question2():
    q2 = random.choice(question_set_2)
    if request.method == 'GET':
        username = request.args.get('username', None)
        return render_template('question2.html', username=username, quest=q2)


@app.route('/question3', methods=['GET', 'POST'])
def question3():
    q3 = random.choice(question_set_3)
    if request.method == 'GET':
        username = request.args.get('username', None)
        return render_template('question3.html', username=username, quest=q3)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')