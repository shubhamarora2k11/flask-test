# -*- coding: utf-8 -*-
"""
Created on Fri May 31 14:51:06 2019

@author: kpmg
"""

from flask import Flask, render_template
app = Flask(__name__)


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
        

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/home')
def json():
    return render_template('home.html')

def record():
    with sr.Microphone() as source:
        print("Speak Anything")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
    except:
        print("Sorry, please speak again!")

    return text


@app.route('/background_process_test')
def background_process_test():
    print ("Hello")
    with sr.Microphone() as source:
        print("Speak Anything")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        print("You said: {}".format(text))
        sentiment = sentiment_scores(text)
        print(sentiment)
        tone_analysis = tone_analyzer.tone({'text': text},'application/json').get_result()
        print(tone_analysis)
        if ( len(tone_analysis['document_tone']['tones'])>0):
            print("Below are the emotions captured:")
        for tone in tone_analysis['document_tone']['tones']:    
            print(tone['tone_name'])
            
    except:
        print("Sorry, please speak again!")

    return render_template('home2.html', data = "data")

if __name__ == '__main__':
    app.run(debug=True)