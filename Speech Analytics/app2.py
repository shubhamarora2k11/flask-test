
from flask import Flask, render_template, redirect,  url_for
app = Flask(__name__)
import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
  
def sentiment_scores(sentence): 
  
    sid_obj = SentimentIntensityAnalyzer() 
   
    sentiment_dict = sid_obj.polarity_scores(sentence) 
      
    print("Sentence Overall Rated As", end = " ") 
   
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

import speech_recognition as sr


r = sr.Recognizer()
        
from flask_wtf import FlaskForm
from wtforms import SubmitField

class PostForm(FlaskForm):
    submit = SubmitField('')

@app.route('/')
def hello_world():
    return 'Hello, World!'



	
import json
@app.route('/tester' , methods =['GET', 'POST'])
def test():
    return render_template('homee.html')

@app.route('/home' , methods =['GET', 'POST'])
def home():
    form = PostForm()
    if form.validate_on_submit():
        with sr.Microphone() as source:
            print("Speak Anything")
            audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print("You spoke: ", text)
            sentiment = sentiment_scores(text)
            print(sentiment)
            data = { "text":text, "sentiment": sentiment, "tone":[]}
            tone_analysis = tone_analyzer.tone({'text': text},'application/json').get_result()
            print("Emotions:")
            for tone in tone_analysis['document_tone']['tones']:    
                data['tone'].append(tone['tone_name'])
            
            print(data['tone'])
            return render_template('home.html', data=json.dumps(data), form=form)
    
        except:
            print("Sorry, please try again!")
            return render_template('home.html', data="321l", form=form)
        
    return render_template('home.html', data="123", form=form)


if __name__ == '__main__':
    app.run(debug=True)